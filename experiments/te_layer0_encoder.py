"""C77 encoder-side diagnostic — what happens to the 12 taps of Qwen3-VL-4B when Layer 0 Attention is zeroed,
Layer 0 MLP is zeroed, or the whole Layer 0 block is zeroed?
Tests the unchecked candidate mechanism in docs/te_layer0_result.md ("early layers of Qwen-family models build a few
very large activations that later layers rely on (Sun et al. 2024, 'Massive activations'); without them the
conditioning may arrive at the wrong scale" vs "token identity preservation" via Logit Lens).

Usage:
  python te_layer0_encoder.py --gate   # verifies ArthemyKrea2CLIPTuner matches C67 CHK_active_L02_mlp_p1.00.npz
  python te_layer0_encoder.py --run    # writes data/te_layer0_encoder_by_tap.csv, data/te_layer0_encoder_summary.csv, and contact sheet
"""
import argparse, csv, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
COMFY_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI")
sys.path.insert(0, str(COMFY_ROOT))
sys.path.insert(0, str(COMFY_ROOT / "custom_nodes" / "Arthemy_Krea2_Tuner"))

import blk23_colorful as c47
import te_conditioning as TC
import te_layer0 as TL0
import te_layer0_block as TL0B
import te_punct_encoder as TPE
from Arthemy_Krea2_Tuner import ArthemyKrea2CLIPTuner

DATA = HERE.parent / "data"
OUT_TAP = DATA / "te_layer0_encoder_by_tap.csv"
OUT_SUM = DATA / "te_layer0_encoder_summary.csv"
TAPS = TC.TAPS  # [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]


def apply_te_edit(base_clip, granular_dict):
    if not granular_dict:
        return base_clip
    tuner = ArthemyKrea2CLIPTuner()
    patched_clip, _ = tuner.tune_clip(
        clip=base_clip,
        mode="Real Value",
        vectors_override="",
        granular_json=json.dumps(granular_dict),
    )
    return patched_clip


def gate():
    base_clip = TPE.gate()
    # Verify active edit CHK_active_L02_mlp_p1.00 against C67 .npz
    row = next(r for r in TC.rd(DATA / "te_pilot_plan.csv") if r["cond"] == "CHK_active_L02_mlp_p1.00")
    gj = json.loads(row["te_granular_json"])
    patched = apply_te_edit(base_clip, gj)
    c_edit, _, ids = TPE.encode_taps(patched, row["prompt_text"])
    b_ref = np.load(TC.out_path("elf", "P1_elfbrawler", "baseline"))["cond"].astype(np.float32)
    d = c_edit - b_ref
    nb = np.linalg.norm(b_ref, axis=-1) + 1e-6
    rel = np.linalg.norm(d, axis=-1) / nb
    ref_diff = np.load(TC.out_path("elf", "P1_elfbrawler", "CHK_active_L02_mlp_p1.00"))
    max_rel_err = float(np.abs(rel - ref_diff["rel"]).max())
    print(f"CHK_active_L02_mlp_p1.00 vs C67 diff .npz: max_rel_err={max_rel_err:.6f} (limit {2 * TC.FP16_FLOOR:.6f})")
    ok = max_rel_err <= 2 * TC.FP16_FLOOR
    print("TUNER GATE", "PASS" if ok else "FAIL - stop")
    if not ok:
        sys.exit(1)
    return base_clip


def load_vocab_embedding():
    import torch
    from safetensors import safe_open
    with safe_open(str(TC.TE_WEIGHTS), framework="pt") as f:
        name = next(k for k in f.keys() if k.endswith("embed_tokens.weight") and "visual" not in k)
        E = f.get_tensor(name).float().cuda()
    return E


def build_contact_sheet(out_paths):
    from PIL import Image, ImageDraw, ImageFont
    chars = ["P1_elfbrawler", "D1_dwarf_paladin", "R6_dragonborn_cleric", "D1W_dwarf_paladin_watercolor"]
    conds = [
        ("L00_attn_m1.00 (Attention x 0)", "L00_attn_m1.00"),
        ("L00_mlp_m1.00 (MLP x 0)", "L00_mlp_m1.00"),
        ("L00_block_m1.00 (Whole Block x 0)", "L00_block_m1.00"),
    ]
    cell_w, cell_h = 320, 400
    pad_top, pad_left = 44, 220
    W = pad_left + len(conds) * cell_w
    H = pad_top + len(chars) * cell_h
    canvas = Image.new("RGB", (W, H), (18, 20, 28))
    draw = ImageDraw.Draw(canvas)

    for j, (label, _) in enumerate(conds):
        draw.text((pad_left + j * cell_w + 12, 14), label, fill=(235, 240, 250))

    for i, ch in enumerate(chars):
        draw.text((12, pad_top + i * cell_h + cell_h // 2 - 10), ch, fill=(235, 240, 250))
        for j, (_, cond) in enumerate(conds):
            if cond == "L00_block_m1.00":
                p = c47.IMG_ROOT / "benchmark_te_layer0_block" / f"{ch}_{cond}_krea2_seed1618033_00001_.png"
            elif ch == "P1_elfbrawler":
                p = c47.IMG_ROOT / "benchmark_te_pilot" / f"{ch}_{cond}_krea2_seed1618033_00001_.png"
            else:
                p = c47.IMG_ROOT / "benchmark_te_layer0" / f"{ch}_{cond}_krea2_seed1618033_00001_.png"
            assert p.exists(), f"Missing image: {p}"
            im = Image.open(p).convert("RGB").resize((cell_w - 8, cell_h - 8), Image.Resampling.LANCZOS)
            canvas.paste(im, (pad_left + j * cell_w + 4, pad_top + i * cell_h + 4))

    for op in out_paths:
        op.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(op, quality=92)
        print("Saved contact sheet:", op)


def run():
    import torch
    base_clip = gate()
    inv = TC.vocab()
    E_emb = load_vocab_embedding()

    tx = {}
    for r in TC.rd(DATA / "te_characters_plan.csv"):
        tx.setdefault(r["char"], r["prompt_text"])
    pilot = [r for r in TC.rd(DATA / "te_pilot_plan.csv") if r["cond"] == "L00_mlp_m1.00"][0]
    tx["P1_elfbrawler"] = pilot["prompt_text"]
    chars = ["P1_elfbrawler", "D1_dwarf_paladin", "R6_dragonborn_cleric", "D1W_dwarf_paladin_watercolor"]

    cond_defs = {
        "baseline": {},
        "L00_attn_m1.00": TL0.EDITS["L00_attn_m1.00"],
        "L00_mlp_m1.00": TL0.EDITS["L00_mlp_m1.00"],
        "L00_block_m1.00": TL0B.EDIT_L00_BLOCK,
    }

    patched_clips = {k: apply_te_edit(base_clip, gj) for k, gj in cond_defs.items()}

    tap_rows = []
    for ch in chars:
        text = tx[ch]
        c_base, _, ids_base = TPE.encode_taps(patched_clips["baseline"], text)
        pieces = [inv.get(int(i), "") for i in ids_base]
        end = next((p for p, s in enumerate(pieces) if s.startswith("<|im_end")), len(pieces))
        ids_content = ids_base[:end]
        mag_base = np.abs(c_base[:end]).mean(axis=0)  # (12, 2560)

        for cond_name, p_clip in patched_clips.items():
            c, _, ids = TPE.encode_taps(p_clip, text)
            assert np.array_equal(ids[:end], ids_content)
            # Logit lens top-5 token indices at every position and tap
            with torch.no_grad():
                c_gpu = torch.from_numpy(c[:end].astype(np.float32)).cuda()
                logits = c_gpu @ E_emb.T  # (end, 12, vocab_size)
                top5 = logits.topk(5, dim=-1).indices.cpu().numpy()  # (end, 12, 5)

            for t_idx, layer in enumerate(TAPS):
                Xt = c[:end, t_idx, :]   # (end, 2560)
                Bt = c_base[:end, t_idx, :]
                # 1. Token L2 norm
                norms = np.linalg.norm(Xt, axis=-1)
                base_norms = np.linalg.norm(Bt, axis=-1)
                norm_ratio = float(norms.mean() / (base_norms.mean() + 1e-6))

                # 2. Massive channels (the 2 largest channels of baseline at this tap, e.g. channels 0 and 4/11)
                big2_idx = np.argsort(-mag_base[t_idx])[:2]
                ch_mag = np.abs(Xt).mean(axis=0)
                big2_amp = float(ch_mag[big2_idx].mean())
                med_amp = float(np.median(ch_mag))
                big2_over_med = big2_amp / (med_amp + 1e-6)

                # 3. Cosine with baseline token at the same position
                cos_base = float(((Xt * Bt).sum(axis=-1) / (norms * base_norms + 1e-6)).mean())

                # 4. Pairwise cosine across different token positions (measures token collapse / uniformity)
                Y = Xt / (norms[:, None] + 1e-12)
                Cmat = Y @ Y.T
                iu, ju = np.triu_indices(end, k=1)
                inter_tok_cos_raw = float(Cmat[iu, ju].mean())

                # 5. Logit-lens self-token retention: how often is position p's own input token in top-1 or top-5?
                self_top1 = float(np.mean([ids_content[p] == top5[p, t_idx, 0] for p in range(end)]))
                self_top5 = float(np.mean([ids_content[p] in top5[p, t_idx, :5] for p in range(end)]))

                tap_rows.append({
                    "char": ch,
                    "cond": cond_name,
                    "tap_idx": t_idx,
                    "tap_layer": layer,
                    "mean_l2_norm": round(float(norms.mean()), 2),
                    "norm_ratio_vs_base": round(norm_ratio, 4),
                    "big2_channels": f"{big2_idx[0]} {big2_idx[1]}",
                    "big2_mean_abs": round(big2_amp, 2),
                    "median_ch_abs": round(med_amp, 4),
                    "big2_over_median": round(big2_over_med, 2),
                    "cos_with_base": round(cos_base, 4),
                    "inter_token_cos_raw": round(inter_tok_cos_raw, 4),
                    "logitlens_self_top1": round(self_top1, 4),
                    "logitlens_self_top5": round(self_top5, 4),
                })

    with open(OUT_TAP, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(tap_rows[0]))
        w.writeheader()
        w.writerows(tap_rows)

    # Summary averaged over the 4 prompts for each (cond, tap_layer) and overall across all 12 taps / final tap 35
    sum_rows = []
    for cond_name in cond_defs:
        for t_idx, layer in enumerate(TAPS):
            sub = [r for r in tap_rows if r["cond"] == cond_name and r["tap_layer"] == layer]
            sum_rows.append({
                "cond": cond_name,
                "tap_layer": layer,
                "mean_l2_norm": round(float(np.mean([r["mean_l2_norm"] for r in sub])), 2),
                "norm_ratio_vs_base": round(float(np.mean([r["norm_ratio_vs_base"] for r in sub])), 4),
                "big2_mean_abs": round(float(np.mean([r["big2_mean_abs"] for r in sub])), 2),
                "big2_over_median": round(float(np.mean([r["big2_over_median"] for r in sub])), 2),
                "cos_with_base": round(float(np.mean([r["cos_with_base"] for r in sub])), 4),
                "inter_token_cos_raw": round(float(np.mean([r["inter_token_cos_raw"] for r in sub])), 4),
                "logitlens_self_top1": round(float(np.mean([r["logitlens_self_top1"] for r in sub])), 4),
                "logitlens_self_top5": round(float(np.mean([r["logitlens_self_top5"] for r in sub])), 4),
            })

    with open(OUT_SUM, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sum_rows[0]))
        w.writeheader()
        w.writerows(sum_rows)

    print(f"Wrote {len(tap_rows)} rows to {OUT_TAP.name} and {len(sum_rows)} rows to {OUT_SUM.name}")
    for cond_name in cond_defs:
        sub_all = [r for r in sum_rows if r["cond"] == cond_name]
        t0 = sub_all[0]
        t11 = sub_all[-1]
        print(f"[{cond_name}]")
        print(f"  Tap 0 (L02): norm={t0['mean_l2_norm']} ({t0['norm_ratio_vs_base']}x), big2/med={t0['big2_over_median']}, inter_tok_cos={t0['inter_token_cos_raw']}, self_top1={t0['logitlens_self_top1']}, self_top5={t0['logitlens_self_top5']}")
        print(f"  Tap 11 (L35): norm={t11['mean_l2_norm']} ({t11['norm_ratio_vs_base']}x), big2/med={t11['big2_over_median']}, inter_tok_cos={t11['inter_token_cos_raw']}, self_top1={t11['logitlens_self_top1']}, self_top5={t11['logitlens_self_top5']}")
        print(f"  Mean all 12 taps: norm_ratio={np.mean([r['norm_ratio_vs_base'] for r in sub_all]):.3f}, big2/med={np.mean([r['big2_over_median'] for r in sub_all]):.1f}, self_top1={np.mean([r['logitlens_self_top1'] for r in sub_all]):.3f}, self_top5={np.mean([r['logitlens_self_top5'] for r in sub_all]):.3f}")

    sheet_paths = [
        HERE.parent / "docs" / "te_layer0_contact_sheet.jpg",
        Path(r"C:\Users\aless\.gemini\antigravity\brain\094fcef7-1a15-436f-85ab-9f44f39ff9f5\te_layer0_contact_sheet.jpg"),
    ]
    build_contact_sheet(sheet_paths)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("gate", "run"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.gate:
        gate()
    if a.run:
        run()
