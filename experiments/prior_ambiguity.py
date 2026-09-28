#!/usr/bin/env python3
"""How much work does "undeclared" actually leave the model to do?

Arm C of benchmark_leaf_collapse tested four subjects chosen for having a STRONG colour prior, to
see whether the achromatic collapse generalises. It never fired, and that was read as
"leaf-specific". Looking at the contact sheets says otherwise: for those four subjects the
undeclared row and the prototypical-declared row are the same picture.

So this measures it. For each subject, the circular hue distance between the UNDECLARED baseline
and the PROTOTYPICAL-DECLARED baseline, pooled over the three seeds. Small means the prior is
unambiguous -- not naming the colour is the same as naming it, there is no inference left to fail,
and the mechanism proposed in what_broke_in_the_leaf.md section 2 predicts nothing to break.

The leaf is measured the same way, from the Stage 2b corpus (LN against LG).

Writes data/prior_ambiguity.csv. No render.
"""
import csv, math, os, statistics
import numpy as np
from PIL import Image
from scipy import ndimage

H = os.path.expanduser("~/mnt")
R = f"{H}/benchmark_leaf_collapse/renders"
RC = f"{H}/benchmark_colour_binding--renders"
OUT = "data/prior_ambiguity.csv"
SEEDS = ["42", "777", "1337"]
SUBJECTS = [("MU", "mushroom"), ("TO", "tomato"), ("PC", "pinecone"), ("BA", "banana")]


def hue(path):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    mx, mn = a.max(2), a.min(2)
    d = mx - mn
    sat = np.where(mx > 1e-5, d / np.maximum(mx, 1e-5), 0.0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    h = np.zeros_like(mx)
    m = (mx == r) & (d > 1e-5); h[m] = (60 * ((g[m] - b[m]) / d[m]) + 360) % 360
    m = (mx == g) & (d > 1e-5); h[m] = (60 * ((b[m] - r[m]) / d[m]) + 120) % 360
    m = (mx == b) & (d > 1e-5); h[m] = (60 * ((r[m] - g[m]) / d[m]) + 240) % 360
    small = np.asarray(Image.fromarray((mx * 255).astype(np.uint8)).resize(
        (mx.shape[1] // 8, mx.shape[0] // 8), Image.BOX), dtype=np.float32) / 255.0
    ring = np.concatenate([small[:5].ravel(), small[-5:].ravel(),
                           small[:, :5].ravel(), small[:, -5:].ravel()])
    k = ndimage.binary_opening(np.abs(small - float(np.median(ring))) > 0.06, np.ones((3, 3)))
    lab, n = ndimage.label(k)
    if n:
        k = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
    fg = np.asarray(Image.fromarray((k * 255).astype(np.uint8)).resize(
        (mx.shape[1], mx.shape[0]), Image.NEAREST)) > 127
    hh, ss = h[fg], sat[fg]
    rad = np.deg2rad(hh)
    return math.degrees(math.atan2((ss * np.sin(rad)).sum(), (ss * np.cos(rad)).sum())) % 360


def circ(a, b):
    d = abs(a - b) % 360.0
    return d if d <= 180 else 360 - d


def main():
    rows = []
    for code, name in SUBJECTS:
        v = [circ(hue(f"{R}/{code}N_baseline_krea2_seed{s}_00001_.png"),
                  hue(f"{R}/{code}P_baseline_krea2_seed{s}_00001_.png")) for s in SEEDS]
        rows.append(dict(subject=name, corpus="benchmark_leaf_collapse",
                         mean_deg=f"{statistics.fmean(v):.1f}",
                         per_seed="; ".join(f"{x:.0f}" for x in v),
                         prior="unambiguous" if statistics.fmean(v) < 20 else "ambiguous"))
    v = [circ(hue(f"{RC}/LN_baseline_krea2_seed{s}_00001_.png"),
              hue(f"{RC}/LG_baseline_krea2_seed{s}_00001_.png")) for s in SEEDS]
    rows.append(dict(subject="leaf", corpus="stage 2b", mean_deg=f"{statistics.fmean(v):.1f}",
                     per_seed="; ".join(f"{x:.0f}" for x in v),
                     prior="unambiguous" if statistics.fmean(v) < 20 else "ambiguous"))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    for r in rows:
        print("  %-9s undeclared vs prototypical-declared: %5s deg  (%s)  -> %s"
              % (r["subject"], r["mean_deg"], r["per_seed"], r["prior"]))


if __name__ == "__main__":
    main()
