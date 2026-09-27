#!/usr/bin/env python3
"""Does the edit's signature survive an augmented image?

Pre-registration: docs/prereg_signature_robustness.md (commit 0b3a8c2), deposited before any
augmented image existed. Augmentation is image processing on copies -- no render is generated.

Stage 1 (--make AUG): write augmented copies of the P02 candidates and the P02 baselines.
Stage 2 (--extract AUG): extract the 23 traits from them, then delete the copies.
Stage 3 (--score): the forced choice, per condition, with the exact 720-permutation null.
"""
import argparse, collections, csv, glob, itertools, math, os, shutil, subprocess, sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

RENDERS = os.path.expanduser("~/mnt/benchmark_mappa--renders")
WORK = os.path.expanduser("~/mnt/outputs/aug")
FEAT = "data/style_features_mappa.csv"
AUGFEAT = "data/style_features_mappa_aug.csv"
DISP = "data/sign_decomposition_cells.csv"
OUT = "data/signature_robustness.csv"
BLOCKS = [f"Block_{i}" for i in range(1, 7)]
DOSES = ["0.050", "0.200"]
SIGNS = ["pos", "neg"]
SEEDS = ["42", "777", "1337"]
AUGS = ["identity", "hflip", "rot90", "hue", "desat", "noise", "jpeg"]
NON = {"file", "width_px", "height_px"}

SUBSETS = {
    "colour": ["color_top4_cluster_share", "color_cluster_entropy_norm", "color_n_effective",
               "colorfulness_hs"],
    "texture": ["glcm_contrast", "glcm_homogeneity", "glcm_energy", "glcm_correlation",
                "lbp_entropy", "lbp_uniform_share", "fft_radial_slope", "fft_high_freq_share"],
    "stroke": ["stroke_width_median_px", "stroke_width_std_px", "stroke_width_cv", "edge_density",
               "contour_mean_length_px", "contour_n_components", "crosshatch_entropy_mean",
               "crosshatch_entropy_p90"],
    "tone": ["luminance_hist_n_peaks", "shadow_edge_transition_width_px",
             "shadow_edge_transition_width_std"],
}


def apply_aug(im, aug):
    if aug == "identity":
        return im, "png"
    if aug == "hflip":
        return im.transpose(Image.FLIP_LEFT_RIGHT), "png"
    if aug == "rot90":
        return im.transpose(Image.ROTATE_90), "png"
    if aug == "hue":
        h, s, v = im.convert("HSV").split()
        a = np.asarray(h, dtype=np.int16)
        return Image.merge("HSV", (Image.fromarray(((a + 42) % 256).astype(np.uint8)), s, v)
                           ).convert("RGB"), "png"
    if aug == "desat":
        return ImageEnhance.Color(im).enhance(0.5), "png"
    if aug == "noise":
        rng = np.random.default_rng(0)
        a = np.asarray(im, dtype=np.float32)
        return Image.fromarray(np.clip(a + rng.normal(0, 8, a.shape), 0, 255).astype(np.uint8)), "png"
    if aug == "jpeg":
        return im, "jpeg"
    raise SystemExit(f"unknown augmentation {aug}")


def candidates():
    out = {f"P02_baseline_krea2_seed{s}_00001_.png" for s in SEEDS}
    for b, d, sg, s in itertools.product(BLOCKS, DOSES, SIGNS, SEEDS):
        out.add(f"P02_{b}{sg}_{d}_krea2_seed{s}_00001_.png")
    return sorted(out)


def make(aug):
    d = os.path.join(WORK, aug)
    os.makedirs(d, exist_ok=True)
    n = 0
    for f in candidates():
        src = os.path.join(RENDERS, f)
        if not os.path.exists(src):
            print(f"  missing {f}"); continue
        im = Image.open(src).convert("RGB")
        out, fmt = apply_aug(im, aug)
        if fmt == "jpeg":
            out.save(os.path.join(d, f.replace(".png", ".jpg")), quality=40)
        else:
            out.save(os.path.join(d, f))
        n += 1
    print(f"{aug}: wrote {n} copies to {d}")


def extract(aug):
    d = os.path.join(WORK, aug)
    paths = sorted(glob.glob(os.path.join(d, "*.png")) + glob.glob(os.path.join(d, "*.jpg")))
    tmp = f"/tmp/aug_{aug}.csv"
    subprocess.run([sys.executable, "experiments/style_features.py", "--out", tmp] + paths,
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    rows = list(csv.DictReader(open(tmp, encoding="utf-8")))
    for r in rows:
        r["aug"] = aug
    new = not os.path.exists(AUGFEAT)
    with open(AUGFEAT, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["aug"] + list(rows[0].keys())[:-1])
        if new:
            w.writeheader()
        for r in rows:
            w.writerow(r)
    shutil.rmtree(d, ignore_errors=True)
    print(f"{aug}: extracted {len(rows)}, copies deleted")


def parse(f):
    n = f.rsplit("_00001_", 1)[0]
    p, rest = n.split("_", 1)
    seed = rest.rsplit("_seed", 1)[1]
    rest = rest.rsplit("_krea2_seed", 1)[0]
    if rest == "baseline":
        return p, "baseline", "", "", seed
    dose = rest.rsplit("_", 1)[1]
    reg = rest.rsplit("_", 1)[0]
    return p, reg[:-3], reg[-3:], dose, seed


def foils():
    g = collections.defaultdict(list)
    for r in csv.DictReader(open(DISP, encoding="utf-8")):
        g[(r["region"], r["dose"])].append(
            (float(r["norm_plus"]) ** 2 + float(r["norm_minus"]) ** 2) / 2)
    nm = {k: float(np.mean(v)) ** 0.5 for k, v in g.items()}
    return {(b, d): min((abs(nm[(b, d)] - nm[(o, d)]), o) for o in BLOCKS if o != b)[1]
            for d in DOSES for b in BLOCKS}


def score():
    base = list(csv.DictReader(open(FEAT, encoding="utf-8")))
    traits = [c for c in base[0] if c not in NON]
    V = {}
    for r in base:
        try:
            V[parse(r["file"])] = np.array([float(r[t]) for t in traits])
        except ValueError:
            pass
    # fixed metric and P01 centring, from the UNTOUCHED baselines (pitfall 33)
    p01 = np.mean([V[("P01", "baseline", "", "", s)] for s in SEEDS], axis=0)
    resid = []
    for p in ("P01", "P02", "A01"):
        bs = [V[(p, "baseline", "", "", s)] for s in SEEDS if (p, "baseline", "", "", s) in V]
        if bs:
            m = np.mean(bs, axis=0); resid += [b - m for b in bs]
    scale = np.std(np.array(resid), axis=0, ddof=1); scale[scale == 0] = 1.0

    A = collections.defaultdict(dict)
    for r in csv.DictReader(open(AUGFEAT, encoding="utf-8")):
        try:
            A[r["aug"]][parse(os.path.basename(r["file"]))] = np.array([float(r[t]) for t in traits])
        except ValueError:
            pass
    F = foils()
    idx = {t: i for i, t in enumerate(traits)}
    rows = []
    for aug in AUGS:
        T = A.get(aug)
        if not T:
            print(f"  {aug}: no features, skipped"); continue
        bm = np.mean([T[("P02", "baseline", "", "", s)] for s in SEEDS
                      if ("P02", "baseline", "", "", s) in T], axis=0)
        for b, d, sg, s in itertools.product(BLOCKS, DOSES, SIGNS, SEEDS):
            ref = (V[("P01", b, sg, d, s)] - p01) / scale
            kt, kf = ("P02", b, sg, d, s), ("P02", F[(b, d)], sg, d, s)
            if kt not in T or kf not in T:
                continue
            tgt, fl = (T[kt] - bm) / scale, (T[kf] - bm) / scale
            row = dict(aug=aug, block=b, dose=d, sign=sg, seed=s, foil=F[(b, d)])
            for name, sub in [("all", traits)] + list(SUBSETS.items()):
                j = [idx[t] for t in sub if t in idx]
                c = lambda x, y: float(x[j] @ y[j] / (np.linalg.norm(x[j]) * np.linalg.norm(y[j])))
                row[f"hit_{name}"] = int(c(ref, tgt) > c(ref, fl))
            rows.append(row)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)} decisions to {OUT}\n")

    # exact permutation null over the 720 relabellings of the P02 blocks
    def perm_p(aug, key):
        sub = [r for r in rows if r["aug"] == aug]
        obs = np.mean([r[key] for r in sub])
        byk = {(r["block"], r["dose"], r["sign"], r["seed"]): r for r in sub}
        T = A[aug]
        bm = np.mean([T[("P02", "baseline", "", "", s)] for s in SEEDS], axis=0)
        j = [idx[t] for t in (traits if key == "hit_all" else SUBSETS[key[4:]]) if t in idx]
        c = lambda x, y: float(x[j] @ y[j] / (np.linalg.norm(x[j]) * np.linalg.norm(y[j])))
        null = []
        for pm in itertools.permutations(BLOCKS):
            a = dict(zip(BLOCKS, pm)); h = n = 0
            for (b, d, sg, s) in byk:
                if a[b] == F[(b, d)]:
                    continue
                kt, kf = ("P02", a[b], sg, d, s), ("P02", F[(b, d)], sg, d, s)
                if kt not in T or kf not in T:
                    continue
                ref = (V[("P01", b, sg, d, s)] - p01) / scale
                h += int(c(ref, (T[kt] - bm) / scale) > c(ref, (T[kf] - bm) / scale)); n += 1
            null.append(h / n if n else np.nan)
        null = np.array(null)
        return obs, float(np.nanmean(null)), float(np.nanstd(null)), float((null >= obs).mean())

    print("=" * 78)
    print(f"{'condition':11s} {'all 23':>9s} {'perm p':>8s} | {'colour':>8s} {'texture':>8s} "
          f"{'stroke':>8s} {'tone':>8s}")
    res = {}
    for aug in AUGS:
        sub = [r for r in rows if r["aug"] == aug]
        if not sub:
            continue
        obs, mu, sd, p = perm_p(aug, "hit_all")
        res[aug] = obs
        line = f"{aug:11s} {obs:9.4f} {p:8.4f} |"
        for name in ("colour", "texture", "stroke", "tone"):
            line += f" {np.mean([r['hit_'+name] for r in sub]):8.4f}"
        print(line + f"   (null {mu:.3f}±{sd:.3f})")
    print("=" * 78)
    real = [a for a in AUGS if a != "identity" and a in res]
    print(f"\nA1  all six > 0.50: {all(res[a] > 0.50 for a in real)}   "
          f"four or more > 0.60: {sum(1 for a in real if res[a] > 0.60)}/6  -> "
          f"{'CONFIRMED' if all(res[a]>0.50 for a in real) and sum(1 for a in real if res[a]>0.60)>=4 else ('FALSIFIED' if sum(1 for a in real if res[a]<=0.50)>=2 else 'GREY')}")
    rank = sorted(real, key=lambda a: res[a])
    print(f"A2  ranking worst to best: {rank}")
    print(f"    noise and jpeg in the bottom two: {set(rank[:2]) == {'noise','jpeg'}} -> "
          f"{'CONFIRMED' if set(rank[:2])=={'noise','jpeg'} else ('FALSIFIED' if ('noise' in rank[-2:] or 'jpeg' in rank[-2:]) else 'GREY')}")
    g = lambda a, k: np.mean([r["hit_" + k] for r in rows if r["aug"] == a])
    h1, h2 = g("hue", "colour"), g("hue", "texture")
    n1, n2 = g("noise", "texture"), g("noise", "colour")
    print(f"A3  under hue:   colour {h1:.3f} vs texture {h2:.3f}  -> colour below: {h1 < h2}")
    print(f"    under noise: texture {n1:.3f} vs colour {n2:.3f}  -> texture below: {n1 < n2}")
    print(f"    crossover -> {'CONFIRMED' if (h1<h2 and n1<n2) else 'FALSIFIED'}")
    print("A4  Block_6 per condition:")
    ok = 0
    for aug in real:
        v = np.mean([r["hit_all"] for r in rows if r["aug"] == aug and r["block"] == "Block_6"])
        ok += v >= 0.80
        print(f"      {aug:9s} {v:.3f}")
    print(f"    >=0.80 in {ok}/6 -> {'CONFIRMED' if ok >= 5 else ('FALSIFIED' if ok <= 3 else 'GREY')}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--make"); ap.add_argument("--extract"); ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.make: make(a.make)
    if a.extract: extract(a.extract)
    if a.score: score()
