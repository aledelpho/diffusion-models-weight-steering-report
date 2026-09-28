#!/usr/bin/env python3
"""Does the collapse take the colour off the leaf, or out of the whole frame?

Two readings of the same event, and they are not the same claim:
  - the object failed to be given a colour  -> only the foreground loses chroma;
  - the edit suppressed colour generation   -> the background's residual tint goes too.

Measured on arm A of benchmark_leaf_collapse: chroma inside the value-based foreground and chroma
outside it, each as a ratio to the same seed's own unperturbed baseline. The background is a plain
light grey by construction, so its chroma is small -- but it is not zero, and a ratio against the
same background in the same baseline is a fair test.

Writes data/leaf_collapse_scope.csv. No render.
"""
import csv, itertools, os, statistics
import numpy as np
from PIL import Image
from scipy import ndimage

REN = os.path.expanduser("~/mnt/benchmark_leaf_collapse/renders")
CELLS = "data/leaf_collapse_cells.csv"
OUT = "data/leaf_collapse_scope.csv"


def parts(path):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    mx, mn = a.max(2), a.min(2)
    sat = np.where(mx > 1e-5, (mx - mn) / np.maximum(mx, 1e-5), 0.0)
    small = np.asarray(Image.fromarray((mx * 255).astype(np.uint8)).resize(
        (mx.shape[1] // 8, mx.shape[0] // 8), Image.BOX), dtype=np.float32) / 255.0
    ring = np.concatenate([small[:5].ravel(), small[-5:].ravel(),
                           small[:, :5].ravel(), small[:, -5:].ravel()])
    m = ndimage.binary_opening(np.abs(small - float(np.median(ring))) > 0.06, np.ones((3, 3)))
    lab, n = ndimage.label(m)
    if n:
        m = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
    fg = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize(
        (mx.shape[1], mx.shape[0]), Image.NEAREST)) > 127
    # the background is everything outside the object, eroded a little so the object's own
    # antialiased rim does not leak into it
    bg = ~ndimage.binary_dilation(fg, np.ones((9, 9)))
    return float(sat[fg].mean()) if fg.any() else 0.0, float(sat[bg].mean()) if bg.any() else 0.0


def mw_exact(a, b):
    allv = sorted(a + b)
    rk = {}
    i = 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j+1] == allv[i]:
            j += 1
        for k in range(i, j+1):
            rk[allv[k]] = (i + j) / 2 + 1
        i = j + 1
    obs = sum(rk[v] for v in a)
    n, k = len(allv), len(a)
    ranks = [rk[v] for v in allv]
    mean = k * (n + 1) / 2
    cnt = tot = 0
    for c in itertools.combinations(range(n), k):
        s = sum(ranks[i] for i in c)
        tot += 1
        if abs(s - mean) >= abs(obs - mean) - 1e-9:
            cnt += 1
    return cnt / tot


def main():
    cells = [x for x in csv.DictReader(open(CELLS, encoding="utf-8")) if x["arm"] == "A_seeds"]
    rows = []
    for c in cells:
        s = c["seed"]
        bfg, bbg = parts(f"{REN}/LN_baseline_krea2_seed{s}_00001_.png")
        pfg, pbg = parts(f"{REN}/LN_B4neg_0.200_krea2_seed{s}_00001_.png")
        rows.append(dict(seed=s, hit=int(c["hit"]),
                         leaf_chroma_baseline=f"{bfg:.4f}", leaf_chroma_perturbed=f"{pfg:.4f}",
                         leaf_ratio=f"{pfg/bfg:.4f}" if bfg else "",
                         bg_chroma_baseline=f"{bbg:.4f}", bg_chroma_perturbed=f"{pbg:.4f}",
                         bg_ratio=f"{pbg/bbg:.4f}" if bbg else ""))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    hit = [r for r in rows if r["hit"]]
    no = [r for r in rows if not r["hit"]]
    print(f"wrote {len(rows)} rows to {OUT}\n")
    for field, label in (("leaf_ratio", "leaf"), ("bg_ratio", "background")):
        a = [float(r[field]) for r in hit]
        b = [float(r[field]) for r in no]
        p = mw_exact(a, b)
        print(f"  {label:11s} chroma ratio -- collapsed seeds {statistics.fmean(a):.4f} "
              f"(min {min(a):.4f}), others {statistics.fmean(b):.4f}, exact p = {p:.5f}")
    print("\n  background absolute chroma, collapsed seeds: "
          + ", ".join(f"{float(r['bg_chroma_perturbed']):.4f}" for r in hit))
    print("  baselines of the same seeds:                  "
          + ", ".join(f"{float(r['bg_chroma_baseline']):.4f}" for r in hit))


if __name__ == "__main__":
    main()
