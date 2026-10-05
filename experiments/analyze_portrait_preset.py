"""Score C52 phase C (docs/prereg_portrait_preset.md). Written 2026-10-05, after the preset was frozen
(commit 4da5117) and BEFORE any phase C render.

  python analyze_portrait_preset.py --features   # 23 style features per image          (any machine with the images)
  python analyze_portrait_preset.py --faces      # ArcFace embeddings + BRISQUE, CLIP-IQA (GPU PC: insightface, piq)
  python analyze_portrait_preset.py --test       # the pre-registered rules
  python analyze_portrait_preset.py --selftest   # the rules on synthetic data (no images needed)

Outputs:
  data/portrait_preset_style_features.csv   char, cond, seed, 23 features
  data/portrait_preset_faces.csv            char, cond, seed, detected, det_score, brisque, clipiqa, emb (512 floats)
  data/portrait_preset_measures.csv         every W, S, ID value used by a rule
  data/portrait_preset_tests.csv            G_S, H1, H2, H3 with their numbers and verdicts

Implementation choices fixed here, before the data (the pre-registration leaves them implicit):
  * features are standardised by the SD (ddof=1) over the 28 phase C baselines;
  * W_held: cosine of dF between two different held-out characters at the same seed, all 3 pairs x 4 seeds;
    W_cal the same over the 4 calibration characters (6 pairs x 4 seeds); medians are reported and used;
  * S: cosine of dF between two seeds of one character, 6 seed pairs x 7 characters, median used by G_S;
  * ID_seed(c): MEAN cosine over the 6 pairs of baselines of c; ID_edit(c, s): cosine baseline vs preset;
  * H3 "median of ID_edit over them": the median over all (character, seed) ID_edit values of the eligible
    held-out characters;
  * ArcFace: insightface FaceAnalysis(name="buffalo_l"), det_size (640, 640), largest face by box area,
    normed_embedding; a character is eligible for H3 only if a face is found in all 8 of its images.
"""
import argparse, csv, itertools, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from portraits import CALIBRATION, HELD_OUT, SEEDS_C, FOLDER_C, IMG_ROOT

DATA = os.path.join(HERE, "..", "data")
FEAT = os.path.join(DATA, "portrait_preset_style_features.csv")
FACES = os.path.join(DATA, "portrait_preset_faces.csv")
CAL, HELD = list(CALIBRATION), list(HELD_OUT)
CHARS = CAL + HELD
CONDS = ["baseline", "preset"]


def path(ch, cond, seed):
    return os.path.join(str(IMG_ROOT), FOLDER_C, f"{ch}_{cond}_krea2_seed{seed}_00001_.png")


# ---------------------------------------------------------------- measurement
def features():
    from style_features import extract_all_features
    done = set()
    if os.path.exists(FEAT):
        done = {(r["char"], r["cond"], r["seed"]) for r in csv.DictReader(open(FEAT))}
    new = not os.path.exists(FEAT)
    with open(FEAT, "a", newline="") as fh:
        w = None
        for ch in CHARS:
            for seed in SEEDS_C:
                for cond in CONDS:
                    if (ch, cond, seed) in done:
                        continue
                    f = extract_all_features(path(ch, cond, seed))
                    row = {"char": ch, "cond": cond, "seed": seed,
                           **{k: v for k, v in f.items() if k not in ("file", "width_px", "height_px")}}
                    if w is None:
                        w = csv.DictWriter(fh, fieldnames=list(row))
                        if new:
                            w.writeheader()
                    w.writerow(row); fh.flush()
    print("features ok")


def faces():
    import torch, piq
    from PIL import Image
    from insightface.app import FaceAnalysis
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    app = FaceAnalysis(name="buffalo_l", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
    app.prepare(ctx_id=0 if dev == "cuda" else -1, det_size=(640, 640))
    ciqa = piq.CLIPIQA(data_range=1.).to(dev)
    out = []
    for ch in CHARS:
        for seed in SEEDS_C:
            for cond in CONDS:
                p = path(ch, cond, seed)
                im = Image.open(p).convert("RGB")
                bgr = np.asarray(im)[:, :, ::-1].copy()
                fs = app.get(bgr)
                if fs:
                    f = max(fs, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
                    emb, det, sc = f.normed_embedding, 1, float(f.det_score)
                else:
                    emb, det, sc = np.zeros(512), 0, 0.0
                x = torch.from_numpy(np.asarray(im.resize((512, 640), Image.BICUBIC), dtype=np.float32) / 255.).permute(2, 0, 1)[None].to(dev)
                out.append({"char": ch, "cond": cond, "seed": seed, "detected": det, "det_score": round(sc, 4),
                            "brisque": round(float(piq.brisque(x, data_range=1.)), 4),
                            "clipiqa": round(float(ciqa(x).mean()), 5),
                            "emb": " ".join(f"{v:.6f}" for v in emb)})
                print(ch, cond, seed, "face" if det else "NO FACE")
    with open(FACES, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print("faces ok:", sum(r["detected"] for r in out), "of", len(out), "with a face")


# ---------------------------------------------------------------- rules
cos = lambda x, y: float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))


def rules(F, E, det):
    """F[(ch, cond, seed)] -> 23-vector; E[(ch, cond, seed)] -> 512 unit vector; det[(ch, cond, seed)] -> 0/1."""
    B = np.array([F[(c, "baseline", s)] for c in CHARS for s in SEEDS_C])
    sd = B.std(axis=0, ddof=1); sd[sd == 0] = 1
    dF = {(c, s): (F[(c, "preset", s)] - F[(c, "baseline", s)]) / sd for c in CHARS for s in SEEDS_C}
    meas = []
    W_held = [cos(dF[(a, s)], dF[(b, s)]) for s in SEEDS_C for a, b in itertools.combinations(HELD, 2)]
    W_cal = [cos(dF[(a, s)], dF[(b, s)]) for s in SEEDS_C for a, b in itertools.combinations(CAL, 2)]
    S = {c: [cos(dF[(c, s)], dF[(c, t)]) for s, t in itertools.combinations(SEEDS_C, 2)] for c in CHARS}
    for v in W_held: meas.append(("W_held", "", v))
    for v in W_cal: meas.append(("W_cal", "", v))
    for c in CHARS:
        for v in S[c]: meas.append(("S", c, v))
    mS = float(np.median([v for c in CHARS for v in S[c]]))
    mWh, mWc = float(np.median(W_held)), float(np.median(W_cal))
    gate = mS >= 0.50
    if not gate:
        h1 = h2 = "uninformative"
    else:
        h1 = "supported" if mWh >= 0.40 else "refuted" if mWh < 0.25 else "inconclusive"
        h2 = "supported" if mWh >= mWc - 0.15 else "refuted" if mWh < mWc - 0.30 else "inconclusive"
    # identity
    idrows, eligible = {}, []
    for c in CHARS:
        ok = all(det[(c, k, s)] for k in CONDS for s in SEEDS_C)
        if not ok:
            idrows[c] = {"eligible": 0}
            continue
        ide = [cos(E[(c, "baseline", s)], E[(c, "preset", s)]) for s in SEEDS_C]
        ids = float(np.mean([cos(E[(c, "baseline", s)], E[(c, "baseline", t)]) for s, t in itertools.combinations(SEEDS_C, 2)]))
        idrows[c] = {"eligible": 1, "ID_edit": ide, "ID_edit_median": float(np.median(ide)), "ID_seed": ids}
        for s, v in zip(SEEDS_C, ide): meas.append(("ID_edit", f"{c}|{s}", v))
        meas.append(("ID_seed", c, ids))
        if c in HELD:
            eligible.append(c)
    if not eligible:
        h3, h3_med = "untestable", float("nan")
    else:
        above = [idrows[c]["ID_edit_median"] > idrows[c]["ID_seed"] for c in eligible]
        h3_med = float(np.median([v for c in eligible for v in idrows[c]["ID_edit"]]))
        if all(above) and h3_med >= 0.50:
            h3 = "supported"
        elif sum(not a for a in above) >= len(eligible) / 2:
            h3 = "refuted"
        else:
            h3 = "inconclusive"
    tests = [("G_S median S (>= 0.50 to inform H1-H2)", round(mS, 4), "pass" if gate else "fail"),
             ("H1 median W_held (>= 0.40 / < 0.25)", round(mWh, 4), h1),
             ("H2 median W_held vs median W_cal (>= W_cal-0.15 / < W_cal-0.30)", f"{mWh:.4f} vs {mWc:.4f}", h2),
             ("H3 eligible held-out characters", " ".join(eligible) or "none", ""),
             ("H3 median ID_edit over eligible (>= 0.50) and per-character ID_edit > ID_seed", round(h3_med, 4) if eligible else "", h3)]
    for c in CHARS:
        r = idrows[c]
        tests.append((f"identity {c}", "not eligible (face not found in all 8)" if not r["eligible"]
                      else f"ID_edit median {r['ID_edit_median']:.4f} vs ID_seed {r['ID_seed']:.4f}", "held out" if c in HELD else "calibration"))
    return tests, meas


def load():
    rows = list(csv.DictReader(open(FEAT)))
    keys = [k for k in rows[0] if k not in ("char", "cond", "seed")]
    assert len(keys) == 23, len(keys)
    F = {(r["char"], r["cond"], r["seed"]): np.array([float(r[k]) for k in keys]) for r in rows}
    fr = list(csv.DictReader(open(FACES)))
    E = {(r["char"], r["cond"], r["seed"]): np.array([float(x) for x in r["emb"].split()]) for r in fr}
    det = {(r["char"], r["cond"], r["seed"]): int(r["detected"]) for r in fr}
    assert len(F) == len(E) == 56, (len(F), len(E))
    return F, E, det


def write(tests, meas):
    with open(os.path.join(DATA, "portrait_preset_tests.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["test", "value", "verdict"]); w.writerows(tests)
    with open(os.path.join(DATA, "portrait_preset_measures.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["quantity", "unit", "value"]); w.writerows([(a, b, round(v, 5)) for a, b, v in meas])
    for t in tests:
        print(" | ".join(str(x) for x in t))


def selftest():
    rng = np.random.default_rng(0)
    def synth(coherent: bool, same_face: bool, hide_r6: bool):
        F, E, det = {}, {}, {}
        look = rng.normal(size=23)
        for c in CHARS:
            face = rng.normal(size=512)
            for s in SEEDS_C:
                base = rng.normal(size=23) * 3
                F[(c, "baseline", s)] = base
                F[(c, "preset", s)] = base + (look if coherent else rng.normal(size=23)) + rng.normal(size=23) * 0.2
                fb = face + rng.normal(size=512) * 0.6
                fp = fb + rng.normal(size=512) * (0.2 if same_face else 3.0)
                E[(c, "baseline", s)] = fb / np.linalg.norm(fb); E[(c, "preset", s)] = fp / np.linalg.norm(fp)
                for k in CONDS:
                    det[(c, k, s)] = 0 if (hide_r6 and c == "R6_dragonborn_cleric") else 1
        return F, E, det
    t, _ = rules(*synth(True, True, True));   v = {x[0][:2]: x[2] for x in t}
    assert v["G_"] == "pass" and v["H1"] == "supported" and v["H2"] == "supported" and t[4][2] == "supported", t
    assert "R6_dragonborn_cleric" not in t[3][1]
    t, _ = rules(*synth(False, True, False)); v = {x[0][:2]: x[2] for x in t}
    assert v["G_"] == "fail" and v["H1"] == "uninformative", t
    t, _ = rules(*synth(True, False, False))
    assert t[4][2] == "refuted", t
    F, E, det = synth(True, True, False)
    for k in det:
        if k[0] in HELD: det[k] = 0
    t, _ = rules(F, E, det)
    assert t[4][2] == "untestable", t
    print("selftest: coherent+same face -> supported; incoherent -> uninformative; face swapped -> refuted; "
          "no face -> untestable; R6 excluded when undetected. OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for f in ("features", "faces", "test", "selftest"):
        ap.add_argument(f"--{f}", action="store_true")
    a = ap.parse_args()
    if a.features: features()
    if a.faces: faces()
    if a.test: write(*rules(*load()))
    if a.selftest: selftest()
