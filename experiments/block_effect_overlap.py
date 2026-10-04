"""Where-vs-which-way overlap between single-block effects.

For each prompt (fixed seed), every block arm gives a difference image
D_b = render_b - baseline in CIELAB at 64x80. For every pair of arms (a, b)
on the same prompt we record two numbers:

  where  = Spearman correlation of |D_a| and |D_b| over the 64x80 grid
           (do the two arms change the same regions?)
  signed = Pearson correlation of D_a and D_b over grid x 3 channels
           (do they push those regions the same way?)

Alessandro's intuition ("groups of blocks that move the same things in
different directions") reads as: high `where`, low or negative `signed`.
This is an aid to looking, not a verdict; it was written after he described
the intuition and after the renders were opened.

Usage: python experiments/block_effect_overlap.py
A second signed number, signed_resid, removes first the mean change over all
56 arms on that prompt (the common mode), because before removal even the two
arms of one block correlate positively.

Writes data/block_effect_overlap_pairs.csv (one row per prompt x pair)
and data/block_effect_overlap_mean.csv (mean over prompts, styles bench only).
"""
import csv, glob, os, re
import numpy as np
from PIL import Image

ROOT = r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"
if not os.path.isdir(ROOT):  # Cowork mount
    ROOT = os.path.expanduser("~/mnt")
    BENCH = {"styles": os.path.join(ROOT, "benchmark_single_blocks_styles", "renders"),
             "v3": os.path.join(ROOT, "benchmark_single_blocks_v3", "renders"),
             "v4": os.path.join(ROOT, "benchmark_single_blocks_v4", "renders")}
else:
    BENCH = {k: os.path.join(ROOT, f"benchmark_single_blocks_{k}", "renders") for k in ("styles", "v3", "v4")}
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data")
PAT = re.compile(r"^(.+?)_(blk\d\d)_(pos|neg)_d([\d.]+)_krea2_seed(\d+)_")
BASE = re.compile(r"^(.+?)_baseline_krea2_seed(\d+)_")


def lab(path):
    im = Image.open(path).convert("RGB").resize((64, 80), Image.BOX)
    a = np.asarray(im, dtype=np.float64) / 255.0
    a = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = a @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def rank(x):
    r = np.empty_like(x); r[np.argsort(x)] = np.arange(len(x)); return r


def main():
    rows = []
    for bench, d in BENCH.items():
        files = [os.path.basename(f) for f in glob.glob(os.path.join(d, "*.png"))]
        base = {}
        arms = {}
        for f in files:
            m = BASE.match(f)
            if m:
                base[(m[1], m[2])] = f; continue
            m = PAT.match(f)
            if m:
                arms.setdefault((m[1], m[5]), []).append((f"{m[2]}_{m[3]}", m[4], f))
        for key, lst in sorted(arms.items()):
            if key not in base: continue
            B = lab(os.path.join(d, base[key]))
            D = {}
            for arm, dose, f in lst:
                D[arm] = (dose, lab(os.path.join(d, f)) - B)
            names = sorted(D)
            # common mode: the part of the change every arm on this prompt shares
            # (pos and neg of the same block correlate at about +0.25 before this)
            C = np.mean([D[n][1] for n in names], axis=0)
            mag = {n: np.linalg.norm(D[n][1], axis=-1).ravel() for n in names}
            rk = {n: rank(mag[n]) for n in names}
            for i, a in enumerate(names):
                for b in names[i + 1:]:
                    where = np.corrcoef(rk[a], rk[b])[0, 1]
                    signed = np.corrcoef(D[a][1].ravel(), D[b][1].ravel())[0, 1]
                    resid = np.corrcoef((D[a][1] - C).ravel(), (D[b][1] - C).ravel())[0, 1]
                    rows.append([bench, key[0], key[1], a, D[a][0], b, D[b][0],
                                 round(where, 4), round(signed, 4), round(resid, 4),
                                 round(float(mag[a].mean()), 3), round(float(mag[b].mean()), 3)])
    hdr = ["bench", "prompt", "seed", "arm_a", "dose_a", "arm_b", "dose_b", "where", "signed", "signed_resid", "dE_a", "dE_b"]
    with open(os.path.join(OUT, "block_effect_overlap_pairs.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(hdr); w.writerows(rows)
    # mean over the 12 styles prompts (one seed, one dose per arm)
    acc = {}
    for r in rows:
        if r[0] != "styles": continue
        acc.setdefault((r[3], r[5]), []).append((r[7], r[8], r[9]))
    with open(os.path.join(OUT, "block_effect_overlap_mean.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["arm_a", "arm_b", "n_prompts", "where_mean", "signed_mean", "signed_sd", "resid_mean", "resid_sd"])
        for (a, b), v in sorted(acc.items()):
            v = np.array(v)
            w.writerow([a, b, len(v), round(v[:, 0].mean(), 4), round(v[:, 1].mean(), 4), round(v[:, 1].std(ddof=1), 4), round(v[:, 2].mean(), 4), round(v[:, 2].std(ddof=1), 4)])
    print(len(rows), "pairs")


if __name__ == "__main__":
    main()
