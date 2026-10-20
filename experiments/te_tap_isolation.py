"""C79 — 12-tap isolation on Qwen3-VL-4B: early/mid taps (0..8 = L02..L26) vs late taps (9..11 = L29..L35)
(docs/prereg_te_tap_isolation.md). Written 2026-10-17, before any C79 render.

  python te_tap_isolation.py --plan              # data/te_tap_isolation_plan.csv (4 gate + 72 main = 76 rows)
  python te_tap_isolation.py --encoder           # 0-render audit: per-tap push norms (C67/C68) + txtfusion adapter weights
  python te_tap_isolation.py --queue --block gate
  python te_tap_isolation.py --gate              # all 4 gates must print max abs diff 0 and GATE PASS
  python te_tap_isolation.py --queue --block main
  python te_tap_isolation.py --count             # expected 76 missing 0 []
  python te_tap_isolation.py --selftest
"""
import argparse, csv, json, sys, urllib.request
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_pilot as TP
import te_conditioning as T
import te_regions as RG

DATA = HERE.parent / "data"
PLAN = DATA / "te_tap_isolation_plan.csv"
ENC_BY_TAP = DATA / "te_tap_isolation_encoder_by_tap.csv"
ENC_SUMMARY = DATA / "te_tap_isolation_encoder_summary.csv"
TXTFUSION_CSV = DATA / "te_tap_isolation_txtfusion_weights.csv"
FOLDER = "benchmark_te_tap_isolation"

CHARS = ["D1_dwarf_paladin", "E2_elf_rogue", "O4_halforc_fighter"]
SEEDS = ["2645751", "3316624", "3605551", "4123105"]
LAYERS = [6, 14]
DOSE = 1.00
NOISE_SEED = 7
SET = {
    "sampler": "euler_ancestral",
    "scheduler": "simple",
    "steps": "9",
    "cfg": "1.0",
    "denoise": "1.0",
    "width": "1024",
    "height": "1280",
}

TAP_CONDS = {
    6: {
        "taps_local": "2,3",
        "taps_early_mid": "0,1,2,3,4,5,6,7,8",
        "taps_late": "9,10,11",
    },
    14: {
        "taps_local": "4,5",
        "taps_early_mid": "0,1,2,3,4,5,6,7,8",
        "taps_late": "9,10,11",
    },
}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def gj(layer, d):
    return json.dumps({f"layers.{layer}.mlp.{m}_proj.weight": d for m in ("gate", "up", "down")})


def texts():
    t = {}
    for r in rd(DATA / "te_characters_plan.csv"):
        if r["char"] in CHARS and r["char"] not in t:
            t[r["char"]] = r["prompt_text"]
    assert len(t) == 3, list(t)
    return t


def make_plan():
    tx = texts()
    rows = []

    def add(block, ch, seed, layer, d, cond_tag, variant, taps_str):
        cond = f"L{layer:02d}_mlp_p{d:.2f}_{cond_tag}"
        prefix = f"{ch}_{cond}_krea2_seed{seed}"
        rows.append({
            "row": len(rows),
            "block": block,
            "char": ch,
            "seed": seed,
            "layer": layer,
            "dose": f"{d:.2f}",
            "cond_tag": cond_tag,
            "variant": variant,
            "taps": taps_str,
            "noise_seed": NOISE_SEED,
            "te_granular_json": gj(layer, d),
            "cond": cond,
            "prompt_text": tx[ch],
            "output_prefix": prefix,
            "expected_filename": f"{prefix}_00001_.png",
            **SET,
        })

    # 4 Gate rows on D1_dwarf_paladin, seed 2645751
    add("gate", CHARS[0], SEEDS[0], 6, DOSE, "gate_zero", "zero", "")
    add("gate", CHARS[0], SEEDS[0], 6, DOSE, "gate_real", "real", "")
    add("gate", CHARS[0], SEEDS[0], 6, DOSE, "gate_all12", "taps", "0,1,2,3,4,5,6,7,8,9,10,11")
    add("gate", CHARS[0], SEEDS[0], 28, DOSE, "gate_late_L28", "taps", "9,10,11")

    # 72 Main rows: 2 layers x 3 tap conditions x 3 characters x 4 seeds
    for layer in LAYERS:
        for cond_tag, taps_str in TAP_CONDS[layer].items():
            for ch in CHARS:
                for s in SEEDS:
                    add("main", ch, s, layer, DOSE, cond_tag, "taps", taps_str)

    assert len(rows) == 76, len(rows)
    with open(PLAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print("plan rows:", len(rows), dict(Counter(r["block"] for r in rows)))


def workflow(r):
    wf = TP.workflow({**r, "te_granular_json": "", "vectors_override": ""})  # plain CLIP on node 40
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    wf["51"] = {
        "class_type": "ArthemyKrea2CLIPTuner",
        "inputs": {
            "clip": ["37", 1],
            "mode": "Real Value",
            "vectors_override": "",
            "granular_json": r["te_granular_json"],
            "Embedding": 0.0,
            "Layer_1": 0.0,
            "Layer_2": 0.0,
            "Layer_3": 0.0,
            "Layer_4": 0.0,
            "Layer_5": 0.0,
            "Layer_6": 0.0,
            "Layer_7": 0.0,
        },
    }
    wf["94"] = {"class_type": "CLIPTextEncode", "inputs": {"clip": ["51", 0], "text": r["prompt_text"]}}
    wf["93"] = {
        "class_type": "Krea2ConditioningPush",
        "inputs": {
            "conditioning": ["40", 0],
            "conditioning_edit": ["94", 0],
            "variant": r["variant"],
            "noise_seed": int(r["noise_seed"]),
            "taps": r["taps"],
        },
    }
    wf["42"]["inputs"]["positive"] = ["93", 0]
    return wf


def queue(block=None, first=None):
    rows = rd(PLAN)
    if block:
        rows = [r for r in rows if r["block"] == block]
    if block == "main":
        rows = sorted(rows, key=lambda r: (r["char"], int(r["layer"]), int(r["row"])))
    if first:
        rows = rows[:first]
    n = 0
    for r in rows:
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(
            f"{c47.COMFY}/prompt",
            data=json.dumps({"prompt": workflow(r)}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def _im(p):
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def gate():
    g = [r for r in rd(PLAN) if r["block"] == "gate"]
    ch, s = g[0]["char"], g[0]["seed"]
    ref_base = _im(c47.IMG_ROOT / "benchmark_portraits" / "phase_c" / f"{ch}_baseline_krea2_seed{s}_00001_.png")
    ref_l06 = _im(c47.IMG_ROOT / "benchmark_te_characters" / f"{ch}_L06_mlp_p1.00_krea2_seed{s}_00001_.png")
    ref_l28 = _im(c47.IMG_ROOT / "benchmark_te_characters" / f"{ch}_L28_mlp_p1.00_krea2_seed{s}_00001_.png")
    refs = [
        ("gate_zero vs phase_c baseline", g[0], ref_base),
        ("gate_real_L06 vs C74 L06_mlp_p1.00", g[1], ref_l06),
        ("gate_all12_L06 vs C74 L06_mlp_p1.00", g[2], ref_l06),
        ("gate_late_L28 (taps 9,10,11) vs C74 L28_mlp_p1.00", g[3], ref_l28),
    ]
    ok = True
    for label, row, ref in refs:
        p = c47.IMG_ROOT / FOLDER / row["expected_filename"]
        if not p.exists():
            print(label, "MISSING", p)
            ok = False
            continue
        d = int(np.abs(_im(p) - ref).max())
        print(f"{label}: max abs diff {d}")
        if d != 0:
            ok = False
    print("GATE", "PASS" if ok else "FAIL - stop")


def count():
    rows = rd(PLAN)
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:3])


def encoder_audit():
    """Zero-render audit of per-tap perturbation energy and Krea-2 txtfusion adapter weights."""
    from safetensors import safe_open

    # 1. Inspect txtfusion weights in krea2_turbo_bf16.safetensors
    krea_path = Path(r"D:\StabilityMatrix-win-x64\Data\Models\DiffusionModels\krea2_turbo_bf16.safetensors")
    tf_rows = []
    if krea_path.exists():
        import torch
        with safe_open(str(krea_path), framework="pt", device="cpu") as f:
            for k in sorted(f.keys()):
                if "txt" in k:
                    t = f.get_tensor(k).float()
                    row = {
                        "key": k,
                        "shape": str(list(t.shape)),
                        "fro_norm": round(float(t.norm().item()), 6),
                        "mean_abs": round(float(t.abs().mean().item()), 6),
                    }
                    # If shape has a dimension of 12 * 2560 = 30720 or 12, break down by the 12 taps!
                    if t.shape == (1, 12) or t.shape == (12,):
                        vals = t.flatten().tolist()
                        for j, v in enumerate(vals):
                            row[f"tap_{j:02d}_L{T.TAPS[j]:02d}"] = round(float(v), 6)
                    elif t.ndim == 2 and t.shape[1] == 12 * 2560:
                        blocks = t.reshape(t.shape[0], 12, 2560)
                        norms = blocks.norm(dim=(0, 2)).tolist()
                        for j, v in enumerate(norms):
                            row[f"tap_{j:02d}_L{T.TAPS[j]:02d}"] = round(float(v), 6)
                    tf_rows.append(row)
        if tf_rows:
            fields = []
            for r in tf_rows:
                for k in r:
                    if k not in fields:
                        fields.append(k)
            with open(TXTFUSION_CSV, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=fields)
                w.writeheader()
                w.writerows(tf_rows)
            print("wrote", TXTFUSION_CSV, len(tf_rows), "rows")

    # 2. Compute per-tap push norms for L06, L14, L28 across the 3 characters (D1, E2, O4)
    import te_layer0_encoder as L0E
    import te_punct_encoder as TPE

    tx = texts()
    edits = [
        ("L06_mlp_p1.00", 6, 1.00),
        ("L14_mlp_p1.00", 14, 1.00),
        ("L28_mlp_p1.00", 28, 1.00),
    ]
    base_clip = L0E.gate()
    patched_clips = {ename: L0E.apply_te_edit(base_clip, json.loads(gj(layer, dose))) for ename, layer, dose in edits}

    by_tap_rows = []
    summary_rows = []
    for ch in CHARS:
        B_raw, _, ids = TPE.encode_taps(base_clip, tx[ch])
        B = B_raw.astype(np.float32)  # (seq, 12, 2560)
        b_norms = np.linalg.norm(B, axis=(0, 2))  # (12,)
        for ename, layer, dose in edits:
            E_raw, _, _ = TPE.encode_taps(patched_clips[ename], tx[ch])
            E = E_raw.astype(np.float32)
            P = E - B
            p_norms = np.linalg.norm(P, axis=(0, 2))
            rel_norms = p_norms / (b_norms + 1e-12)
            total_p2 = float(np.sum(p_norms ** 2)) + 1e-12
            for j, l_idx in enumerate(T.TAPS):
                cos_b = float(np.sum(E[:, j, :] * B[:, j, :]) / (np.linalg.norm(E[:, j, :]) * b_norms[j] + 1e-12))
                by_tap_rows.append({
                    "char": ch,
                    "edit": ename,
                    "layer": layer,
                    "tap_idx": j,
                    "tap_layer": l_idx,
                    "base_fro": round(float(b_norms[j]), 4),
                    "push_fro": round(float(p_norms[j]), 4),
                    "rel_fro": round(float(rel_norms[j]), 6),
                    "energy_share": round(float((p_norms[j] ** 2) / total_p2), 6),
                    "cos_with_base": round(cos_b, 6),
                })
            loc_idx = [2, 3] if layer == 6 else ([4, 5] if layer == 14 else [9, 10])
            em_idx = list(range(9))
            lt_idx = [9, 10, 11]
            summary_rows.append({
                "char": ch,
                "edit": ename,
                "layer": layer,
                "total_push_fro": round(float(np.sqrt(total_p2)), 4),
                "local_push_fro": round(float(np.linalg.norm(P[:, loc_idx, :])), 4),
                "early_mid_0to8_push_fro": round(float(np.linalg.norm(P[:, em_idx, :])), 4),
                "late_9to11_push_fro": round(float(np.linalg.norm(P[:, lt_idx, :])), 4),
                "local_energy_share": round(float(np.sum(p_norms[loc_idx] ** 2) / total_p2), 6),
                "early_mid_0to8_energy_share": round(float(np.sum(p_norms[em_idx] ** 2) / total_p2), 6),
                "late_9to11_energy_share": round(float(np.sum(p_norms[lt_idx] ** 2) / total_p2), 6),
                "mean_rel_fro_early_mid_reached": round(
                    float(np.mean([rel_norms[j] for j in em_idx if T.TAPS[j] >= layer]))
                    if any(T.TAPS[j] >= layer for j in em_idx) else 0.0,
                    6,
                ),
                "mean_rel_fro_late_9to11": round(float(np.mean(rel_norms[lt_idx])), 6),
            })

    with open(ENC_BY_TAP, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(by_tap_rows[0]))
        w.writeheader()
        w.writerows(by_tap_rows)
    with open(ENC_SUMMARY, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary_rows[0]))
        w.writeheader()
        w.writerows(summary_rows)
    print("wrote", ENC_BY_TAP, len(by_tap_rows), "rows; and", ENC_SUMMARY, len(summary_rows), "rows")


def selftest():
    # Verify exact partition identity: D_early_mid + D_late == P
    rng = np.random.default_rng(42)
    P = rng.standard_normal((18, 12, 2560)).astype(np.float32)
    em = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    lt = [9, 10, 11]
    D_em = np.zeros_like(P); D_em[:, em, :] = P[:, em, :]
    D_lt = np.zeros_like(P); D_lt[:, lt, :] = P[:, lt, :]
    assert np.array_equal(D_em + D_lt, P)
    assert float(np.linalg.norm(D_em[:, lt, :])) == 0.0
    assert float(np.linalg.norm(D_lt[:, em, :])) == 0.0
    print("selftest ok")


VQA_TRAITS = {
    "D1_dwarf_paladin": [
        ("d_dwarf", "a female mountain dwarf"),
        ("d_copper", "copper-colored hair"),
        ("d_braids", "thick braided hair pinned back"),
        ("d_gorget", "a polished steel gorget at the neck"),
        ("d_navy", "a navy blue gambeson"),
        ("d_brass", "a high brass collar"),
    ],
    "E2_elf_rogue": [
        ("e_ears", "pointed elf ears"),
        ("e_smirk", "a smug lopsided smirk"),
        ("e_undercut", "an asymmetrical undercut hairstyle"),
        ("e_black", "raven black hair"),
        ("e_amber", "amber eyes"),
        ("e_cowl", "a dark forest green hooded leather cowl"),
        ("e_buckles", "brass buckles"),
        ("e_tunic", "a high-collared charcoal tunic"),
        ("e_feather", "a single dangling feather earring"),
    ],
    "O4_halforc_fighter": [
        ("o_orc", "a female half-orc with non-human features"),
        ("o_undercut", "shorn faded sides of the head"),
        ("o_knot", "hair tied in a tight black warrior knot"),
        ("o_greyeyes", "pale grey eyes"),
        ("o_scale", "a bronze scale-mail collar"),
        ("o_jack", "a burgundy quilted jack"),
    ],
}


def analyze():
    """Compute DINOv2-large, CSD-ViT-L, VQAScore trait retention, and contact sheets for all 72 C79 main renders."""
    from PIL import Image, ImageDraw
    import metric_validation as MV

    rows = [r for r in rd(PLAN) if r["block"] == "main"]
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    if miss:
        raise RuntimeError(f"Missing {len(miss)} C79 main renders: {miss[:5]}")

    m = MV.Models(vqa=True)
    cache = {}

    def eval_img(path, ch):
        key = str(path)
        if key not in cache:
            im = Image.open(path).convert("RGB")
            arr = np.asarray(im, dtype=np.float32)
            csd_v = m.csd_vec(im)
            dino_v = m.dino_vec(im)
            gen = m.genre(im)
            top_genre = max(gen.items(), key=lambda kv: kv[1])[0]
            t_phrases = [p for _, p in VQA_TRAITS[ch]]
            vqa_sc = m.vqa_scores(path, t_phrases)
            cache[key] = {
                "arr": arr,
                "csd": csd_v,
                "dino": dino_v,
                "top_genre": top_genre,
                "comic_prob": float(gen["comic"]),
                "vqa_mean": float(np.mean(vqa_sc)),
                "vqa_by_id": dict(zip([tid for tid, _ in VQA_TRAITS[ch]], vqa_sc)),
            }
        return cache[key]

    metrics_rows = []
    by_cell = {}
    for idx, r in enumerate(rows):
        ch, s, layer, ctag = r["char"], r["seed"], int(r["layer"]), r["cond_tag"]
        p_cond = c47.IMG_ROOT / FOLDER / r["expected_filename"]
        p_base = c47.IMG_ROOT / "benchmark_portraits" / "phase_c" / f"{ch}_baseline_krea2_seed{s}_00001_.png"
        p_real = c47.IMG_ROOT / "benchmark_te_characters" / f"{ch}_L{layer:02d}_mlp_p1.00_krea2_seed{s}_00001_.png"

        eb = eval_img(p_base, ch)
        ec = eval_img(p_cond, ch)
        rms_base = float(np.sqrt(np.mean((ec["arr"] - eb["arr"]) ** 2)))
        dino_dist_base = 1.0 - MV.cos(ec["dino"], eb["dino"])
        csd_dist_base = 1.0 - MV.cos(ec["csd"], eb["csd"])
        vqa_loss_vs_base = eb["vqa_mean"] - ec["vqa_mean"]

        has_real = p_real.exists()
        if has_real:
            er = eval_img(p_real, ch)
            rms_real = round(float(np.sqrt(np.mean((ec["arr"] - er["arr"]) ** 2))), 4)
            dino_dist_real = round(1.0 - MV.cos(ec["dino"], er["dino"]), 6)
            csd_dist_real = round(1.0 - MV.cos(ec["csd"], er["csd"]), 6)
        else:
            rms_real = ""
            dino_dist_real = ""
            csd_dist_real = ""

        mrow = {
            "char": ch,
            "seed": s,
            "layer": layer,
            "cond_tag": ctag,
            "taps": r["taps"],
            "pixel_rms_to_base": round(rms_base, 4),
            "dinov2_dist_to_base": round(dino_dist_base, 6),
            "csd_dist_to_base": round(csd_dist_base, 6),
            "vqa_trait_mean": round(ec["vqa_mean"], 6),
            "vqa_base_mean": round(eb["vqa_mean"], 6),
            "vqa_loss_vs_base": round(vqa_loss_vs_base, 6),
            "clip_top_genre": ec["top_genre"],
            "clip_comic_prob": round(ec["comic_prob"], 5),
            "pixel_rms_to_real": rms_real,
            "dinov2_dist_to_real": dino_dist_real,
            "csd_dist_to_real": csd_dist_real,
        }
        metrics_rows.append(mrow)
        by_cell.setdefault((ch, s, layer), {})[ctag] = mrow
        if (idx + 1) % 12 == 0:
            print(f"analyzed {idx + 1}/{len(rows)}")

    out_metrics = DATA / "te_tap_isolation_metrics.csv"
    with open(out_metrics, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(metrics_rows[0]))
        w.writeheader()
        w.writerows(metrics_rows)

    cell_rows = []
    for (ch, s, layer), d in sorted(by_cell.items()):
        em, lt, loc = d["taps_early_mid"], d["taps_late"], d["taps_local"]
        has_r = em["dinov2_dist_to_real"] != ""
        cell_rows.append({
            "char": ch,
            "seed": s,
            "layer": layer,
            "dinov2_base_local": loc["dinov2_dist_to_base"],
            "dinov2_base_early_mid": em["dinov2_dist_to_base"],
            "dinov2_base_late": lt["dinov2_dist_to_base"],
            "delta_early_late_dinov2": round(em["dinov2_dist_to_base"] - lt["dinov2_dist_to_base"], 6),
            "csd_base_local": loc["csd_dist_to_base"],
            "csd_base_early_mid": em["csd_dist_to_base"],
            "csd_base_late": lt["csd_dist_to_base"],
            "delta_early_late_csd": round(em["csd_dist_to_base"] - lt["csd_dist_to_base"], 6),
            "vqa_loss_local": loc["vqa_loss_vs_base"],
            "vqa_loss_early_mid": em["vqa_loss_vs_base"],
            "vqa_loss_late": lt["vqa_loss_vs_base"],
            "delta_early_late_vqa_loss": round(em["vqa_loss_vs_base"] - lt["vqa_loss_vs_base"], 6),
            "pi_early_late_dinov2": round(lt["dinov2_dist_to_real"] - em["dinov2_dist_to_real"], 6) if has_r else "",
            "pi_early_late_csd": round(lt["csd_dist_to_real"] - em["csd_dist_to_real"], 6) if has_r else "",
            "local_over_early_mid_dinov2": round(loc["dinov2_dist_to_base"] / (em["dinov2_dist_to_base"] + 1e-12), 4),
        })

    out_cells = DATA / "te_tap_isolation_cells.csv"
    with open(out_cells, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cell_rows[0]))
        w.writeheader()
        w.writerows(cell_rows)

    # Build contact sheets per (layer, char)
    sheets_dir = c47.IMG_ROOT / FOLDER / "sheets"
    sheets_dir.mkdir(parents=True, exist_ok=True)
    tw, th = 256, 320
    for layer in LAYERS:
        for ch in CHARS:
            canvas = Image.new("RGB", (tw * 5, th * len(SEEDS)), (26, 26, 25))
            draw = ImageDraw.Draw(canvas)
            for si, s in enumerate(SEEDS):
                p_base = c47.IMG_ROOT / "benchmark_portraits" / "phase_c" / f"{ch}_baseline_krea2_seed{s}_00001_.png"
                p_real = c47.IMG_ROOT / "benchmark_te_characters" / f"{ch}_L{layer:02d}_mlp_p1.00_krea2_seed{s}_00001_.png"
                cols = [
                    ("baseline", p_base),
                    ("full_12taps", p_real if p_real.exists() else None),
                    ("taps_local", c47.IMG_ROOT / FOLDER / f"{ch}_L{layer:02d}_mlp_p1.00_taps_local_krea2_seed{s}_00001_.png"),
                    ("taps_early_mid(0..8)", c47.IMG_ROOT / FOLDER / f"{ch}_L{layer:02d}_mlp_p1.00_taps_early_mid_krea2_seed{s}_00001_.png"),
                    ("taps_late(9..11)", c47.IMG_ROOT / FOLDER / f"{ch}_L{layer:02d}_mlp_p1.00_taps_late_krea2_seed{s}_00001_.png"),
                ]
                for ci, (lbl, p) in enumerate(cols):
                    if p is not None and p.exists():
                        im = Image.open(p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
                        canvas.paste(im, (ci * tw, si * th))
                    draw.rectangle([ci * tw, si * th, ci * tw + 210, si * th + 20], fill=(0, 0, 0))
                    draw.text((ci * tw + 5, si * th + 3), f"{lbl} s={s}", fill=(255, 255, 255))
            sheet_path = sheets_dir / f"sheet_L{layer:02d}_{ch}.jpg"
            canvas.save(sheet_path, quality=90)
    print("wrote", out_metrics, out_cells, "and 6 contact sheets in", sheets_dir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--encoder", action="store_true")
    ap.add_argument("--queue", action="store_true")
    ap.add_argument("--block", default=None)
    ap.add_argument("--first", type=int, default=None)
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.plan:
        make_plan()
    if a.encoder:
        encoder_audit()
    if a.queue:
        queue(a.block, a.first)
    if a.gate:
        gate()
    if a.count:
        count()
    if a.analyze:
        analyze()
    if a.selftest:
        selftest()
