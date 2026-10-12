"""C65 — do text-encoder edits move different characters the same way? (docs/prereg_te_characters.md)
Written 2026-10-11, before any render. Renders authorised by Alessandro.

  python te_characters.py --plan            # data/te_characters_plan.csv (the 20 edits are chosen by rule from C64 phase 1)
  python te_characters.py --queue --first 2 # the two reproduction renders only (characters, word order)
  python te_characters.py --repro           # must print REPRO PASS max abs diff 0 twice
  python te_characters.py --queue           # everything else
  python te_characters.py --count           # expected N missing 0
  python te_characters.py --features        # data/te_characters_style_features.csv (23 style statistics)
  python te_characters.py --faces           # data/te_characters_faces.csv (ArcFace buffalo_l, BRISQUE, CLIP-IQA; GPU PC)
  python te_characters.py --page            # eye page + data/te_characters_eye_key.csv (key committed before labels)
  python te_characters.py --night [--shutdown]  # wait for ComfyUI's queue to empty, then count, repro, page, log; then power off
  python te_characters.py --test            # the decision rules (Claude runs it)
  python te_characters.py --selftest        # the rules on synthetic data

Characters, prompt frame and baselines are those of C52 (experiments/portraits.py, benchmark_portraits/phase_c):
seven Western-comics portraits, seeds 2645751 and 3316624. The baselines are reused, after one render through
this script's workflow reproduces one of them pixel for pixel.

Part B (word order): the same 20 edits on P1_elfbrawler in the five word orders of the DiT test
(benchmark_prompt_order, seeds 3141592 and 1234567), with that test's baselines reused after one reproduction.

Part C (style family): the first calibration character (D1) rewritten as a realistic watercolour, same edits, same
two seeds; its baselines are rendered here.
"""
import argparse, csv, itertools, json, os, sys, urllib.request
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import portraits as P
import te_pilot as TP

DATA = HERE.parent / "data"
PLAN = DATA / "te_characters_plan.csv"
FEAT = DATA / "te_characters_style_features.csv"
FACES = DATA / "te_characters_faces.csv"
KEY = DATA / "te_characters_eye_key.csv"
LABELS = DATA / "te_characters_eye_alessandro.csv"
RESULT = DATA / "te_characters_tests.csv"
ORDER_FOLDER = "benchmark_prompt_order"
ORDERS = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
ORDER_SEEDS = ["3141592", "1234567"]
ORDER_FEAT = DATA / "te_order_style_features.csv"
ORDER_RESULT = DATA / "te_order_tests.csv"
LOG = HERE.parent / "docs" / "RENDERS_2026-10-11_te_characters.md"
WC = "D1W_dwarf_paladin_watercolor"     # part C
WC_OF = "D1_dwarf_paladin"
WC_HEAD = "Realistic watercolor painting, close-up portrait, frontal view."
WC_RESULT = DATA / "te_watercolor_tests.csv"
FOLDER = "benchmark_te_characters"
BASE_FOLDER = P.FOLDER_C
CHARS = list(P.CALIBRATION) + list(P.HELD_OUT)
SEEDS = P.SEEDS_C[:2]          # 2645751, 3316624
ID_SEEDS = P.SEEDS_C           # all four phase C baselines, for ID_seed
PARTS = {"attn": TP.ATTN, "mlp": TP.MLP}


def select_edits():
    """The rule, fixed in the pre-registration: C64 phase-1 layer edits (attention or MLP, dose +-1.00) that Alessandro
    judged a medium or strong change, with the overall style changed, and the surface as the original or cleaner."""
    out = []
    for r in csv.DictReader(open(DATA / "te_pilot_phase1_joined.csv", encoding="utf-8")):
        if (r["phase"] == "main" and r["part"] in PARTS and r["entita"] in ("media", "forte")
                and r["stile"] == "cambiato" and r["dmg"] in ("pulito", "come")):
            out.append((int(r["unit"][1:]), r["part"], 1.0 if r["sign"] == "+" else -1.0, r["cond"]))
    return sorted(out)


def order_prompts():
    out = {}
    for r in csv.DictReader(open(DATA / "prompt_order_experiment_plan_seed2.csv", encoding="utf-8-sig")):
        out.setdefault(r["prompt_id"], r["prompt"])
    assert set(out) == set(ORDERS), list(out)
    return out


def order_path(v, cond, seed):
    if cond == "baseline":
        return c47.IMG_ROOT / ORDER_FOLDER / f"{v}_baseline_krea2_seed{seed}_00001_.png"
    return c47.IMG_ROOT / FOLDER / f"{v}_{cond}_krea2_seed{seed}_00001_.png"


def path(ch, cond, seed):
    if cond == "baseline" and ch != WC:
        return c47.IMG_ROOT / BASE_FOLDER / f"{ch}_baseline_krea2_seed{seed}_00001_.png"
    return c47.IMG_ROOT / FOLDER / f"{ch}_{cond}_krea2_seed{seed}_00001_.png"


def make_plan():
    edits = select_edits()
    rows = []
    OP = order_prompts()
    def add(ch, seed, cond, te_json, phase, unit="", part="", dose=0.0):
        prefix = f"{ch}_{cond}_krea2_seed{seed}"
        text = (OP[ch] if ch in OP else f"{WC_HEAD}\n{P.CALIBRATION[WC_OF]} {P.TAIL}" if ch == WC
                else P.text({**P.CALIBRATION, **P.HELD_OUT}[ch]))
        rows.append({"row": len(rows), "phase": phase, "char": ch, "seed": seed, "cond": cond, "unit": unit, "part": part,
                     "dose": dose, "te_granular_json": te_json, "vectors_override": "",
                     "prompt_text": text, "output_prefix": prefix,
                     "expected_filename": f"{prefix}_00001_.png", **P.SETTINGS})
    add(CHARS[0], SEEDS[0], "REPRO_baseline", "", "check")
    add(ORDERS[0], ORDER_SEEDS[0], "REPRO_baseline", "", "check")
    for ch in CHARS:
        add(ch, SEEDS[0], "CHK_null_L35_both_p1.00", TP.gj_te(35, TP.ATTN + TP.MLP, 1.0), "check", "L35", "both", 1.0)
    for L, part, d, cond in edits:
        for ch in CHARS:
            for seed in SEEDS:
                add(ch, seed, cond, TP.gj_te(L, PARTS[part], d), "main", f"L{L:02d}", part, d)
    for seed in SEEDS:
        add(WC, seed, "baseline", "", "watercolor")
    for L, part, d, cond in edits:
        for seed in SEEDS:
            add(WC, seed, cond, TP.gj_te(L, PARTS[part], d), "watercolor", f"L{L:02d}", part, d)
    for L, part, d, cond in edits:
        for v in ORDERS:
            for seed in ORDER_SEEDS:
                add(v, seed, cond, TP.gj_te(L, PARTS[part], d), "order", f"L{L:02d}", part, d)
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("edits:", len(edits), [e[3] for e in edits])
    print("plan rows:", len(rows))


def plan():
    return list(csv.DictReader(open(PLAN, encoding="utf-8")))


def workflow(r):
    wf = TP.workflow(r)
    wf["61"]["inputs"]["filename_prefix"] = f"{FOLDER}/{r['output_prefix']}"
    return wf


def queue(first):
    n = 0
    for r in plan()[: first or None]:
        if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists():
            continue
        req = urllib.request.Request(f"{c47.COMFY}/prompt", data=json.dumps({"prompt": workflow(r)}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
        n += 1
    print("queued", n)


def _im(p):
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def _base(r):
    return order_path(r["char"], "baseline", r["seed"]) if r["char"] in ORDERS else path(r["char"], "baseline", r["seed"])


def repro():
    ok = True
    for r in plan()[:2]:
        d = int(np.abs(_im(c47.IMG_ROOT / FOLDER / r["expected_filename"]) - _im(_base(r))).max())
        ok &= d == 0
        print("REPRO", r["char"], "PASS" if d == 0 else "FAIL - stop", "max abs diff", d)
    nulls = [r for r in plan() if r["cond"].startswith("CHK_null")]
    have = [r for r in nulls if (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    if have:
        dn = [int(np.abs(_im(c47.IMG_ROOT / FOLDER / r["expected_filename"]) - _im(path(r["char"], "baseline", r["seed"]))).max()) for r in have]
        print("null L35 (reported):", len(have), "renders, max abs diff", dn)
    return ok


def count():
    rows = plan()
    miss = [r["expected_filename"] for r in rows if not (c47.IMG_ROOT / FOLDER / r["expected_filename"]).exists()]
    base_miss = [str(path(c, "baseline", s)) for c in CHARS for s in ID_SEEDS if not path(c, "baseline", s).exists()]
    base_miss += [str(order_path(v, "baseline", s)) for v in ORDERS for s in ORDER_SEEDS if not order_path(v, "baseline", s).exists()]
    print("expected", len(rows), "missing", len(miss), miss[:5], "| reused baselines missing", len(base_miss))
    return len(miss) == 0


def main_conds():
    seen = []
    for r in plan():
        if r["phase"] == "main" and r["cond"] not in seen:
            seen.append(r["cond"])
    return seen


# ---------------------------------------------------------------- measurement
def features():
    _features(FEAT, [(c, "baseline", s) for c in CHARS + [WC] for s in SEEDS] + [(c, k, s) for k in main_conds() for c in CHARS + [WC] for s in SEEDS], path)
    _features(ORDER_FEAT, [(v, "baseline", s) for v in ORDERS for s in ORDER_SEEDS] +
              [(v, k, s) for k in main_conds() for v in ORDERS for s in ORDER_SEEDS], order_path)


def _features(out, items, pathf):
    from style_features import extract_all_features
    done = set()
    if out.exists():
        done = {(r["char"], r["cond"], r["seed"]) for r in csv.DictReader(open(out))}
    new = not out.exists()
    with open(out, "a", newline="") as fh:
        w = None
        for ch, cond, seed in items:
            if (ch, cond, seed) in done:
                continue
            f = extract_all_features(str(pathf(ch, cond, seed)))
            row = {"char": ch, "cond": cond, "seed": seed, **{k: v for k, v in f.items() if k not in ("file", "width_px", "height_px")}}
            if w is None:
                w = csv.DictWriter(fh, fieldnames=list(row))
                if new:
                    w.writeheader()
            w.writerow(row); fh.flush()
    print("features ok", out.name)


def faces():
    import torch, piq
    from PIL import Image
    from insightface.app import FaceAnalysis
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    app = FaceAnalysis(name="buffalo_l", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
    app.prepare(ctx_id=0 if dev == "cuda" else -1, det_size=(640, 640))
    ciqa = piq.CLIPIQA(data_range=1.).to(dev)
    items = [(c, "baseline", s) for c in CHARS for s in ID_SEEDS] + [(c, k, s) for k in main_conds() for c in CHARS for s in SEEDS]
    out = []
    for ch, cond, seed in items:
        im = Image.open(path(ch, cond, seed)).convert("RGB")
        fs = app.get(np.asarray(im)[:, :, ::-1].copy())
        if fs:
            f = max(fs, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
            emb, det, sc = f.normed_embedding, 1, float(f.det_score)
        else:
            emb, det, sc = np.zeros(512), 0, 0.0
        x = torch.from_numpy(np.asarray(im.resize((512, 640), Image.BICUBIC), dtype=np.float32) / 255.).permute(2, 0, 1)[None].to(dev)
        out.append({"char": ch, "cond": cond, "seed": seed, "detected": det, "det_score": round(sc, 4),
                    "brisque": round(float(piq.brisque(x, data_range=1.)), 4), "clipiqa": round(float(ciqa(x).mean()), 5),
                    "emb": " ".join(f"{v:.6f}" for v in emb)})
    with open(FACES, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print("faces ok:", sum(r["detected"] for r in out), "of", len(out), "with a face")


# ---------------------------------------------------------------- rules (fixed in the pre-registration)
cos = lambda x, y: float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-12))


def rules(F, E, det, conds, chars=CHARS, seeds=SEEDS, id_seeds=ID_SEEDS):
    B = np.array([F[(c, "baseline", s)] for c in chars for s in seeds])
    sd = B.std(axis=0, ddof=1); sd[sd == 0] = 1
    per = []
    for k in conds:
        dF = {(c, s): (F[(c, k, s)] - F[(c, "baseline", s)]) / sd for c in chars for s in seeds}
        S = [cos(dF[(c, seeds[0])], dF[(c, seeds[1])]) for c in chars]
        W = [cos(dF[(a, s)], dF[(b, s)]) for s in seeds for a, b in itertools.combinations(chars, 2)]
        mS, mW = float(np.median(S)), float(np.median(W))
        verdict = "uninformative" if mS < 0.50 else ("coherent" if mW >= 0.40 else "incoherent" if mW < 0.25 else "unclear")
        # identity, reported: characters with a face in all their images
        idrow = []
        for c in chars:
            imgs = [(c, "baseline", s) for s in id_seeds] + [(c, k, s) for s in seeds]
            if not all(det.get(x, 0) for x in imgs):
                continue
            id_seed = np.mean([float(E[(c, "baseline", a)] @ E[(c, "baseline", b)]) for a, b in itertools.combinations(id_seeds, 2)])
            id_edit = np.median([float(E[(c, "baseline", s)] @ E[(c, k, s)]) for s in seeds])
            idrow.append(id_edit > id_seed)
        per.append({"cond": k, "median_S": round(mS, 3), "median_W": round(mW, 3), "verdict": verdict,
                    "id_eligible": len(idrow), "id_kept": int(sum(idrow))})
    n = len(per)
    inf = [p for p in per if p["verdict"] != "uninformative"]
    coh = sum(p["verdict"] == "coherent" for p in per)
    if len(inf) < n / 2:
        overall = "uninformative (more than half the edits disagree with themselves across seeds)"
    else:
        overall = "supported" if coh >= np.ceil(2 * n / 3) else "refuted" if coh <= np.floor(n / 3) else "inconclusive"
    return per, {"n_edits": n, "informative": len(inf), "coherent": coh,
                 "incoherent": sum(p["verdict"] == "incoherent" for p in per), "H1": overall}


def load():
    F = {(r["char"], r["cond"], r["seed"]): np.array([float(v) for k, v in r.items() if k not in ("char", "cond", "seed")])
         for r in csv.DictReader(open(FEAT))}
    E, det = {}, {}
    for r in csv.DictReader(open(FACES)):
        key = (r["char"], r["cond"], r["seed"])
        E[key] = np.array([float(v) for v in r["emb"].split()]); det[key] = int(r["detected"])
    return F, E, det


def test():
    F, E, det = load()
    per, tot = rules(F, E, det, main_conds())
    with open(RESULT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(per[0])); w.writeheader(); w.writerows(per)
    for p in per:
        print(p)
    print("H1", tot)
    Fo = {(r["char"], r["cond"], r["seed"]): np.array([float(v) for k, v in r.items() if k not in ("char", "cond", "seed")])
          for r in csv.DictReader(open(ORDER_FEAT))}
    dit = list(csv.DictReader(open(DATA / "prompt_order_feature_consistency.csv")))
    perB, totB = order_rules(Fo, main_conds(), dit)
    with open(ORDER_RESULT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(perB[0])); w.writeheader(); w.writerows(perB)
    for p in perB:
        print(p)
    print("H2", totB)
    perC, totC = watercolor_rules(F, main_conds())
    with open(WC_RESULT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(perC[0])); w.writeheader(); w.writerows(perC)
    for p in perC:
        print(p)
    print("H3", totC)
    for k, v in predictions(per, Fo, main_conds(), list(csv.DictReader(open(FACES)))).items():
        print(k, v)


def selftest():
    rng = np.random.default_rng(0)
    chars, seeds, ids = [f"c{i}" for i in range(7)], ["s1", "s2"], ["s1", "s2", "s3", "s4"]
    F, E, det = {}, {}, {}
    for c in chars:
        for s in ids:
            F[(c, "baseline", s)] = rng.normal(size=23); E[(c, "baseline", s)] = (v := rng.normal(size=512)) / np.linalg.norm(v); det[(c, "baseline", s)] = 1
    shared = rng.normal(size=23) * 3
    for k, kind in (("same", "shared"), ("random", "random")):
        for c in chars:
            for s in seeds:
                F[(c, k, s)] = F[(c, "baseline", s)] + (shared + rng.normal(size=23) * 0.3 if kind == "shared" else rng.normal(size=23) * 3)
                E[(c, k, s)] = E[(c, "baseline", s)]; det[(c, k, s)] = 1
    per, tot = rules(F, E, det, ["same", "random"], chars, seeds, ids)
    assert per[0]["verdict"] == "coherent" and per[1]["verdict"] in ("incoherent", "uninformative"), per
    assert per[0]["id_kept"] == 7, per
    print("selftest ok", per, tot)
    # part B: an edit whose change ignores the order versus one that follows it
    orders, oseeds = ["o1", "o2", "o3", "o4", "o5"], ["s1", "s2"]
    Fo = {}
    for o in orders:
        for s in oseeds:
            Fo[(o, "baseline", s)] = rng.normal(size=23)
    stable, perord = rng.normal(size=23) * 3, {o: rng.normal(size=23) * 3 for o in orders}
    for o in orders:
        for s in oseeds:
            Fo[(o, "stable", s)] = Fo[(o, "baseline", s)] + stable + rng.normal(size=23) * 0.3
            Fo[(o, "orderdep", s)] = Fo[(o, "baseline", s)] + perord[o] + rng.normal(size=23) * 0.3
    dit = [{"arm": f"a{i}", "size": "3", "cos_order": "0.8", "cos_seed": "0.75"} for i in range(10)] + [{"arm": "REORDER_ONLY", "size": "1.1"}]
    perB, totB = order_rules(Fo, ["stable", "orderdep"], dit, orders, oseeds)
    assert perB[0]["cos_order"] > 0.9 and perB[1]["cos_order"] < 0.5 and perB[1]["cos_seed"] > 0.9, perB
    assert participation_ratio([np.eye(5)[i] for i in range(5)]) > participation_ratio([np.ones(5) * i for i in range(5)])
    print("selftest B ok", perB, totB)
    # part C: watercolour change unrelated to the comic one, while comic characters agree
    for s in seeds:
        F[("w", "baseline", s)] = rng.normal(size=23)
        F[("w", "same", s)] = F[("w", "baseline", s)] + rng.normal(size=23) * 3
    perC, totC = watercolor_rules(F, ["same"] * 6, chars, seeds, "w", "c0")
    assert perC[0]["cos_across_character"] > 0.9 and perC[0]["cos_across_style"] < 0.6, perC
    print("selftest C ok", perC[0], totC)


# ---------------------------------------------------------------- part B and the predictions (fixed in the pre-registration)
def order_rules(F, conds, dit, orders=ORDERS, seeds=ORDER_SEEDS):
    """F[(v, cond, seed)] -> 23-vector (cond 'baseline' for the reused baselines). dit: rows of
    data/prompt_order_feature_consistency.csv (the DiT arms). Same definitions as prompt_order_feature_consistency.py."""
    B = np.array([F[(v, "baseline", s)] for v in orders for s in seeds])
    sd = B.std(axis=0, ddof=1); sd[sd == 0] = 1
    reorder = float(np.mean([np.abs((F[(a, "baseline", s)] - F[(b, "baseline", s)]) / sd).mean()
                             for s in seeds for a, b in itertools.combinations(orders, 2)]))
    per = []
    for k in conds:
        dF = {(v, s): (F[(v, k, s)] - F[(v, "baseline", s)]) / sd for v in orders for s in seeds}
        co = float(np.mean([cos(dF[(a, s)], dF[(b, s)]) for s in seeds for a, b in itertools.combinations(orders, 2)]))
        cs = float(np.mean([cos(dF[(v, seeds[0])], dF[(v, seeds[1])]) for v in orders]))
        size = float(np.mean([np.abs(x).mean() for x in dF.values()]))
        per.append({"cond": k, "size": round(size, 3), "cos_order": round(co, 3), "cos_seed": round(cs, 3),
                    "d": round(co - cs, 3), "above_reorder": int(size > reorder)})
    te = [p["d"] for p in per if p["above_reorder"]]
    dit_rows = [r for r in dit if r["arm"] != "REORDER_ONLY"]
    dit_reorder = float(next(r["size"] for r in dit if r["arm"] == "REORDER_ONLY"))
    dd = [float(r["cos_order"]) - float(r["cos_seed"]) for r in dit_rows if float(r["size"]) > dit_reorder]
    out = {"reorder_size_te": round(reorder, 3), "n_te": len(te), "n_dit": len(dd),
           "median_d_te": round(float(np.median(te)), 3) if te else None, "median_d_dit": round(float(np.median(dd)), 3),
           "median_cos_order_te": round(float(np.median([p["cos_order"] for p in per if p["above_reorder"]])), 3) if te else None,
           "median_cos_order_dit": round(float(np.median([float(r["cos_order"]) for r in dit_rows if float(r["size"]) > dit_reorder])), 3)}
    if len(te) < 5:
        out["H2"] = "uninformative (fewer than 5 edits larger than the reordering itself)"
    else:
        from scipy.stats import mannwhitneyu
        pv = float(mannwhitneyu(te, dd, alternative="less").pvalue)
        out["p_mwu"] = round(pv, 4)
        out["H2"] = ("supported" if out["median_d_te"] <= out["median_d_dit"] - 0.10 and pv < 0.05
                     else "refuted" if out["median_d_te"] >= out["median_d_dit"] else "inconclusive")
    return per, out


def watercolor_rules(F, conds, chars=CHARS, seeds=SEEDS, wc=WC, of=WC_OF):
    """Per edit: cos between the change on the watercolour D1 and on the comic D1 (same seed), against the change on
    the comic D1 and on each other comic character (same seed). Scale: SD of the comic baselines, for both families."""
    B = np.array([F[(c, "baseline", s)] for c in chars for s in seeds])
    sd = B.std(axis=0, ddof=1); sd[sd == 0] = 1
    dF = lambda c, k, s: (F[(c, k, s)] - F[(c, "baseline", s)]) / sd
    per = []
    for k in conds:
        x_style = float(np.mean([cos(dF(wc, k, s), dF(of, k, s)) for s in seeds]))
        x_char = float(np.mean([cos(dF(c, k, s), dF(of, k, s)) for s in seeds for c in chars if c != of]))
        per.append({"cond": k, "cos_across_style": round(x_style, 3), "cos_across_character": round(x_char, 3),
                    "size_watercolor": round(float(np.mean([np.abs(dF(wc, k, s)).mean() for s in seeds])), 3),
                    "size_comic_D1": round(float(np.mean([np.abs(dF(of, k, s)).mean() for s in seeds])), 3)})
    a, b = np.median([p["cos_across_style"] for p in per]), np.median([p["cos_across_character"] for p in per])
    from scipy.stats import wilcoxon
    diffs = [p["cos_across_style"] - p["cos_across_character"] for p in per]
    pv = float(wilcoxon(diffs, alternative="less").pvalue) if any(diffs) else 1.0
    H3 = "supported" if a <= b - 0.10 and pv < 0.05 else "refuted" if a >= b else "inconclusive"
    return per, {"median_cos_across_style": round(float(a), 3), "median_cos_across_character": round(float(b), 3),
                 "p_wilcoxon": round(pv, 4), "H3": H3}


def participation_ratio(V):
    V = np.asarray(V, float); V = V - V.mean(axis=0)
    ev = np.clip(np.linalg.eigvalsh(V @ V.T), 0, None)
    return float(ev.sum() ** 2 / (ev ** 2).sum()) if ev.sum() > 0 else 0.0


def predictions(per_char, Fo, conds, faces_rows):
    """Alessandro's three predictions (2026-10-11), each read as holds / fails; none decides H1 or H2."""
    out = {}
    W = [p["median_W"] for p in per_char if p["verdict"] != "uninformative"]
    mw = float(np.median(W)) if W else float("nan")
    out["P1_coherence_like_dit"] = f"median W {mw:.3f} vs C52 0.51 -> " + ("holds" if 0.41 <= mw <= 0.61 else "fails")
    # P2: quality less degraded than the C52 DiT preset, same characters and seeds
    q = {(r["char"], r["cond"], r["seed"]): (float(r["brisque"]), float(r["clipiqa"])) for r in faces_rows}
    qc = {(r["char"], r["cond"], r["seed"]): (float(r["brisque"]), float(r["clipiqa"]))
          for r in csv.DictReader(open(DATA / "portrait_preset_faces.csv"))}
    te_b = np.median([np.median([q[(c, k, s)][0] - q[(c, "baseline", s)][0] for c in CHARS for s in SEEDS]) for k in conds])
    te_c = np.median([np.median([q[(c, k, s)][1] - q[(c, "baseline", s)][1] for c in CHARS for s in SEEDS]) for k in conds])
    dit_b = np.median([qc[(c, "preset", s)][0] - qc[(c, "baseline", s)][0] for c in CHARS for s in SEEDS])
    dit_c = np.median([qc[(c, "preset", s)][1] - qc[(c, "baseline", s)][1] for c in CHARS for s in SEEDS])
    out["P2_quality_less_degraded"] = (f"dBRISQUE te {te_b:+.2f} vs preset {dit_b:+.2f}; dCLIP-IQA te {te_c:+.4f} vs preset {dit_c:+.4f} -> "
                                       + ("holds" if te_b < dit_b and te_c > dit_c else "fails"))
    # P3: a wider spread of styles than the DiT single blocks, same prompt (V1) and seeds, 20 largest DiT arms
    rows = list(csv.DictReader(open(DATA / "prompt_order_style_features.csv")))
    feats = [k for k in rows[0] if k not in ("file", "width_px", "height_px")]
    import re
    BASE = re.compile(r"^V1_Original_baseline_krea2_seed(\d+)_"); ARM = re.compile(r"^V1_Original_(blk\d\d_(?:pos|neg))_d[\d.]+_krea2_seed(\d+)_")
    Bd, Ad = {}, {}
    for r in rows:
        v = np.array([float(r[k]) for k in feats])
        m = BASE.match(r["file"])
        if m: Bd[m[1]] = v; continue
        m = ARM.match(r["file"])
        if m: Ad[(m[1], m[2])] = v
    sd = np.array([Fo[(o, "baseline", s)] for o in ORDERS for s in ORDER_SEEDS]).std(axis=0, ddof=1); sd[sd == 0] = 1
    arms = sorted({a for a, _ in Ad})
    dit = {a: np.mean([(Ad[(a, s)] - Bd[s]) / sd for s in ORDER_SEEDS], axis=0) for a in arms if all((a, s) in Ad for s in ORDER_SEEDS)}
    top = sorted(dit, key=lambda a: -np.abs(dit[a]).mean())[:len(conds)]
    te = [np.mean([(Fo[("V1_Original", k, s)] - Fo[("V1_Original", "baseline", s)]) / sd for s in ORDER_SEEDS], axis=0) for k in conds]
    pr_te, pr_dit = participation_ratio(te), participation_ratio([dit[a] for a in top])
    out["P3_wider_style_spread"] = f"participation ratio te {pr_te:.2f} vs DiT top-{len(top)} {pr_dit:.2f} -> " + ("holds" if pr_te > pr_dit else "fails")
    return out


def night(shutdown):
    """For an unattended run: wait until ComfyUI's queue has been empty for three checks a minute apart, then run
    --count, --repro and --page, write the log for Claude, and (with --shutdown) power the PC off after 5 minutes.
    The shutdown can be cancelled from a terminal with `shutdown /a`. Nothing else is run."""
    import io, time, contextlib, subprocess, datetime
    empty = 0
    while empty < 3:
        try:
            with urllib.request.urlopen(f"{c47.COMFY}/queue", timeout=10) as resp:
                q = json.loads(resp.read())
            empty = empty + 1 if not q.get("queue_running") and not q.get("queue_pending") else 0
        except Exception as e:
            print("queue check failed:", e); empty = 0
        time.sleep(60)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print("night run finished", datetime.datetime.now().isoformat(timespec="seconds"))
        for name, fn in (("--count", count), ("--repro", repro), ("--page", page)):
            print(f"\n$ python te_characters.py {name}")
            try:
                fn()
            except Exception as e:
                print("ERROR", type(e).__name__, e)
    LOG.write_text("# C65 renders — unattended night run\n\n```\n" + buf.getvalue() + "```\n", encoding="utf-8")
    print(buf.getvalue()); print("log ->", LOG)
    if shutdown:
        subprocess.run(["shutdown", "/s", "/t", "300", "/c", "C65 finished: power off in 5 minutes (cancel: shutdown /a)"])
        print("shutdown scheduled in 5 minutes")


# ---------------------------------------------------------------- eye page: one sheet per edit x seed
def page():
    """Sheet = the 7 characters, baseline row above, edit row below; anonymous id, shuffled (rng 66), 6 repeats.
    Questions: do the seven change in the same direction (yes / partly / no); which direction (free); for each
    character, left to right, follows / changes another way / nearly unchanged; how the exceptions change (free);
    surface against the originals (cleaner / as / slight / medium / strong). Key written before any label."""
    from PIL import Image
    rng = np.random.default_rng(66)
    out = c47.IMG_ROOT / FOLDER / "eye_test"; out.mkdir(parents=True, exist_ok=True)
    sheets = [(k, s) for k in main_conds() for s in SEEDS]
    ids = rng.permutation(np.arange(100, 999))[: len(sheets)]
    items = [{"id": f"x{i}", "cond": k, "seed": s} for (k, s), i in zip(sheets, ids)]
    W, H = 300, 375
    for x in items:
        dst = out / f"{x['id']}.jpg"
        if dst.exists():
            continue
        canvas = Image.new("RGB", (W * 7, H * 2), "white")
        for j, ch in enumerate(CHARS):
            canvas.paste(Image.open(path(ch, "baseline", x["seed"])).convert("RGB").resize((W, H), Image.LANCZOS), (j * W, 0))
            canvas.paste(Image.open(path(ch, x["cond"], x["seed"])).convert("RGB").resize((W, H), Image.LANCZOS), (j * W, H))
        canvas.save(dst, quality=90)
    show = [x["id"] for x in items]; rng.shuffle(show)
    rep = list(rng.choice(show, 6, replace=False))
    for x in rep:
        show.insert(int(rng.integers(len(show) // 3, len(show) + 1)), x)
    with open(KEY, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["item", "cond", "seed", "repeated"])
        for x in items:
            w.writerow([x["id"], x["cond"], x["seed"], int(x["id"] in rep)])
    slots = [f"{s}#{k}" for k, s in enumerate(show)]
    (out / "eye_test.html").write_text(EYE.replace("__SLOTS__", json.dumps(slots)), encoding="utf-8")
    print(len(items), "sheets,", len(slots), "showings ->", out / "eye_test.html")


EYE = r"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>C65: stessi cambi su personaggi diversi?</title>
<style>body{margin:0;background:#1d1d1f;color:#eee;font:14px system-ui,sans-serif}#wrap{display:flex;flex-direction:column;height:100vh}
#view{flex:1;overflow:auto;background:#000;text-align:center;min-height:0}#view img{max-width:100%;max-height:100%}#view.zoom img{max-width:none;max-height:none}
#side{background:#2a2a2d;padding:6px 12px;max-height:46vh;overflow:auto}.r{display:flex;align-items:center;gap:6px;padding:2px 6px;border-radius:6px;border:2px solid transparent;flex-wrap:wrap}
.r>span{min-width:330px}.r.cur{border-color:#ffcc55;background:#3a3524}.r.chg>span{color:#ffd27a}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:0 18px}
button{font:13px system-ui;padding:2px 8px;border-radius:6px;border:1px solid #555;background:#333;color:#ddd}
button.on{background:#2f4f3a;border-color:#6a8;color:#fff}button.on.diverso{background:#7a4a1e;border-color:#c85}button.on.invariato{background:#444b5a;border-color:#89a}
textarea{flex:1;min-width:300px;background:#222;color:#eee;border:1px solid #555;border-radius:6px;font:13px system-ui}
kbd{font:12px ui-monospace,monospace;background:#444;border:1px solid #666;border-radius:4px;padding:0 4px}#n{color:#aaa}.g{color:#9ab;font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin:6px 0 1px}</style></head><body><div id="wrap">
<div id="view"><img id="im"></div><div id="side"><div id="n"></div>
<small>Riga sopra: i 7 originali. Riga sotto: la stessa modifica su ciascuno. <kbd>↑</kbd><kbd>↓</kbd> voce · <kbd>←</kbd><kbd>→</kbd> valore · <kbd>Invio</kbd> avanti · <kbd>⌫</kbd> indietro · <kbd>z</kbd> zoom. Nei campi di testo <kbd>→</kbd> per scrivere, <kbd>Esc</kbd> per uscire.</small>
<div id="rows"></div><button id="exp">Scarica le risposte</button></div></div>
<script>
const S=__SLOTS__,K="te_characters_eye_v1";let A={};try{A=JSON.parse(localStorage.getItem(K)||"{}")}catch(e){}
let i=0;try{i=Math.min(+localStorage.getItem(K+"_i")||0,S.length-1)}catch(e){}const $=q=>document.querySelector(q);
const CH=["1 · nana paladina","2 · elfo ladro","3 · mezzorca guerriera","4 · gnomo mago","5 · halfling druido","6 · dragonide chierica","7 · tiefling bardo"];
const R=[{k:"stessa",g:"Insieme",lab:"i 7 personaggi cambiano nella stessa direzione?",o:[["si","sì"],["parte","in parte"],["no","no"]],d:""},
 {k:"direzione",lab:"la direzione comune (stile, colori, forme…)",txt:1}];
CH.forEach((c,j)=>R.push({k:"c"+(j+1),g:j===0?"Personaggio per personaggio, da sinistra":"",lab:c,o:[["segue","segue la direzione"],["diverso","cambia in un altro modo"],["invariato","quasi invariato"]],d:"segue"}));
R.push({k:"eccezioni",g:"Eccezioni",lab:"come cambiano le eccezioni (es. «4: diventa acquerello»)",txt:1});
R.push({k:"dmg",g:"",lab:"superficie rispetto agli originali",o:[["pulito","più pulita"],["come","come"],["lieve","peggio: lieve"],["medio","medio"],["forte","forte"]],d:"come"});
R.push({k:"note",lab:"altro (libero)",txt:1});
let c=0;let gp="";$("#rows").innerHTML=R.map((r,j)=>(r.g?`<div class="g">${r.g}</div>`:"")+(r.txt?`<div class="r" id="r${j}"><span>${r.lab}</span><textarea rows="1" data-j="${j}"></textarea></div>`:
 `<div class="r" id="r${j}"><span>${r.lab}</span>`+r.o.map(([v,l])=>`<button class="${v}" data-j="${j}" data-v="${v}">${l}</button>`).join("")+`</div>`)).join("");
function cur(){return A[S[i]]||(A[S[i]]={})}
function save(){try{localStorage.setItem(K,JSON.stringify(A));localStorage.setItem(K+"_i",i)}catch(e){}}
function show(){const a=A[S[i]]||{};$("#im").src=S[i].split("#")[0]+".jpg";
 $("#n").textContent=`foglio ${i+1} di ${S.length} · completati ${S.filter(s=>A[s]&&A[s].stessa).length}`;
 R.forEach((r,j)=>{const el=$("#r"+j);el.classList.toggle("cur",j===c);if(r.txt){const t=el.querySelector("textarea");if(document.activeElement!==t)t.value=a[r.k]||"";return}
  const v=a[r.k]||r.d;el.classList.toggle("chg",!!r.d&&v!==r.d);el.querySelectorAll("button").forEach(b=>b.classList.toggle("on",v===b.dataset.v))});save()}
function step(d){const r=R[c];if(r.txt){if(d>0)$("#r"+c+" textarea").focus();return}const vs=r.o.map(x=>x[0]);let k=vs.indexOf(cur()[r.k]||r.d);
 k=k<0?(d>0?0:vs.length-1):Math.max(0,Math.min(vs.length-1,k+d));cur()[r.k]=vs[k];show()}
function move(d){c=Math.max(0,Math.min(R.length-1,c+d));show();$("#r"+c).scrollIntoView({block:"nearest"})}
document.querySelectorAll("button[data-j]").forEach(b=>b.onclick=()=>{c=+b.dataset.j;cur()[R[c].k]=b.dataset.v;show()});
document.querySelectorAll("textarea").forEach(t=>{t.onfocus=()=>{c=+t.dataset.j;show()};t.oninput=()=>{cur()[R[+t.dataset.j].k]=t.value;save()}});
addEventListener("keydown",e=>{if(e.target.tagName==="TEXTAREA"){if(["Escape","ArrowUp","ArrowDown"].includes(e.key)){e.preventDefault();e.target.blur();
  if(e.key!=="Escape")move(e.key==="ArrowDown"?1:-1)}return}
 if(e.key==="ArrowDown"){e.preventDefault();move(1)}else if(e.key==="ArrowUp"){e.preventDefault();move(-1)}
 else if(e.key==="ArrowRight"){e.preventDefault();step(1)}else if(e.key==="ArrowLeft"){e.preventDefault();step(-1)}
 else if(e.key==="Enter"){e.preventDefault();if(i<S.length-1){i++;c=0;show();$("#side").scrollTop=0}}else if(e.key==="Backspace"){e.preventDefault();if(i>0){i--;c=0;show();$("#side").scrollTop=0}}
 else if(e.key.toLowerCase()==="z")$("#view").classList.toggle("zoom")});
const q=v=>'"'+String(v||"").replace(/"/g,'""').replace(/\n/g," ")+'"';
$("#exp").onclick=()=>{let t="slot,stessa,direzione,"+CH.map((_,j)=>"c"+(j+1)).join(",")+",eccezioni,dmg,note\n";S.forEach(s=>{const a=A[s]||{};const done=!!a.stessa;
 t+=[s,a.stessa||"",q(a.direzione),...CH.map((_,j)=>done?(a["c"+(j+1)]||"segue"):""),q(a.eccezioni),done?(a.dmg||"come"):"",q(a.note)].join(",")+"\n"});
 const u=URL.createObjectURL(new Blob([t],{type:"text/csv"}));const l=document.createElement("a");l.href=u;l.download="te_characters_eye_alessandro.csv";l.click()};
show();
</script></body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("plan", "queue", "repro", "count", "features", "faces", "page", "test", "selftest", "night", "shutdown"):
        ap.add_argument(f"--{x}", action="store_true")
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: c47.IMG_ROOT = Path(a.img_root)
    if a.plan: make_plan()
    if a.queue: queue(a.first)
    if a.repro: repro()
    if a.count: count()
    if a.features: features()
    if a.faces: faces()
    if a.page: page()
    if a.test: test()
    if a.selftest: selftest()
    if a.night: night(a.shutdown)
