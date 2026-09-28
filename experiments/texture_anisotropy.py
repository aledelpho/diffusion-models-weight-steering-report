#!/usr/bin/env python3
"""Is the added texture speckle, or strands?

Alessandro: "maybe you don't feel it as full of grain only because the patches of colour are
looser." The isotropic Laplacian this project calls `grain` cannot tell dots from filaments -- it
sums squared second differences and throws the orientation away. Two images with the same grain
number can be one stippled and one covered in fibrous scribble, and only the second reads as a
structural defect.

Measured with the structure tensor of the luminance gradient, smoothed over 9x9:
    coherence = (l1 - l2) / (l1 + l2),  averaged over the frame.
Near 0 -- gradients point every way: speckle, or flat. Near 1 -- gradients agree locally: strands,
hatching, filaments. Reported as a ratio against the same prompt/seed baseline.

All conditions at dose 0.200: 6 groups, 28 single blocks, 12 mask conditions. 2 prompts x 3 seeds.
Writes data/texture_anisotropy.csv. No render.
"""
import csv, os, statistics
import numpy as np
from PIL import Image

H = os.path.expanduser("~/mnt")
BASE = f"{H}/benchmark_mappa--renders"
OUT = "data/texture_anisotropy.csv"
P = ["P01", "P02"]
S = ["42", "777", "1337"]


def jobs():
    out = [("group", f"Block_{g}", arm,
            f"{BASE}/{{p}}_Block_{g}{arm}_0.200_krea2_seed{{s}}_00001_.png")
           for g in range(1, 7) for arm in ("pos", "neg")]
    out += [("subblock", f"blk{b:02d}", arm,
             f"{H}/benchmark_profondita{'' if arm == 'pos' else '_neg'}/renders/"
             f"{{p}}_blk{b:02d}{arm}_0.200_krea2_seed{{s}}_00001_.png")
            for b in range(28) for arm in ("pos", "neg")]
    out += [("mask", c, arm,
             f"{H}/benchmark_rectified_masks/renders/{{p}}_{c}_{arm}_seed{{s}}_00001_.png")
            for c in ("B4_mask", "B4_anti", "B6_mask", "B6_anti", "B4B6_mask", "B4B6_anti")
            for arm in ("pos", "neg")]
    return out


def box(a, k=9):
    c = np.cumsum(np.cumsum(np.pad(a, ((1, 0), (1, 0))), 0), 1)
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def coherence(path):
    g = np.asarray(Image.open(path).convert("L"), dtype=np.float32) / 255.0
    gy, gx = np.gradient(g)
    jxx, jyy, jxy = box(gx * gx), box(gy * gy), box(gx * gy)
    tr = jxx + jyy
    root = np.sqrt(np.maximum((jxx - jyy)**2 + 4 * jxy**2, 0))
    return float(np.mean(np.where(tr > 1e-8, root / np.maximum(tr, 1e-8), 0.0)))


def main():
    cache = {}
    rows = []
    for (fam, cond, arm, tpl) in jobs():
        vals = []
        for p in P:
            for s in S:
                f = tpl.format(p=p, s=s)
                if not os.path.exists(f):
                    continue
                if (p, s) not in cache:
                    cache[(p, s)] = coherence(f"{BASE}/{p}_baseline_krea2_seed{s}_00001_.png")
                vals.append(coherence(f) / cache[(p, s)])
        if vals:
            rows.append(dict(family=fam, condition=cond, arm=arm, n=len(vals),
                             coherence_ratio=f"{statistics.fmean(vals):.5f}",
                             min=f"{min(vals):.5f}", max=f"{max(vals):.5f}",
                             cells_above_1=sum(1 for v in vals if v > 1)))
    rows.sort(key=lambda r: -float(r["coherence_ratio"]))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    print(f"{len(rows)} conditions -> {OUT}")
    for r in rows[:8] + rows[-4:]:
        print("  %-9s %-11s %-4s  coherence x%s  (%s cells of %d above 1)"
              % (r["family"], r["condition"], r["arm"], r["coherence_ratio"],
                 r["cells_above_1"], r["n"]))


if __name__ == "__main__":
    main()
