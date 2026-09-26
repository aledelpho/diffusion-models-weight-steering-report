# -*- coding: utf-8 -*-
"""
experiments/region_draw_consistency.py
======================================
POST-HOC, DESCRIPTIVE. Asked after the pre-registered region contrast of
docs/prereg_style_capacity.md section 5 (Q1) came back null, to see what the aggregate hides.

For each of the 12 live regions: the distance between its two independent draws, the region's own
displacement magnitude, the ratio of the two, and the cosine between the draws. Then the rank
correlation between the draw-to-draw distance and the magnitude, which is what decides whether any
apparent structure is structure or just size.

No p-value beyond the pre-registered one. Writes data/region_draw_consistency.csv.
"""
from __future__ import annotations
import csv, math, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import style_capacity_multiprompt as M

DATA = Path(__file__).resolve().parent.parent / "data"

def spear(x, y):
    def rk(v):
        o = np.argsort(v); r = np.empty(len(v)); r[o] = np.arange(len(v)); return r
    x, y = rk(np.asarray(x)), rk(np.asarray(y)); x = x - x.mean(); y = y - y.mean()
    return float((x * y).sum() / math.sqrt((x ** 2).sum() * (y ** 2).sum()))

def main():
    presets, prompts, seeds, cells, D = M.load(M.FEATURES_23)
    P, Q, S, F = len(presets), len(prompts), len(seeds), len(M.FEATURES_23)
    X = (D / M.scale(D, Q, S)).reshape(P, Q, S, F)
    region = [p[0] for p in presets]
    C = X.mean(axis=2)
    rows = []
    for r in sorted(set(region)):
        idx = [i for i in range(P) if region[i] == r]
        if len(idx) != 2:
            continue
        a, b = idx
        d = float(np.mean([np.linalg.norm(C[a, q] - C[b, q]) for q in range(Q)]))
        mag = float(np.mean([np.linalg.norm(C[i, q]) for i in idx for q in range(Q)]))
        cos = float(np.mean([C[a, q] @ C[b, q] /
                             (np.linalg.norm(C[a, q]) * np.linalg.norm(C[b, q])) for q in range(Q)]))
        rows.append(dict(region=r, draw_distance=round(d, 4), delta_norm=round(mag, 4),
                         distance_over_norm=round(d / mag, 4), cosine_between_draws=round(cos, 4)))
    d = [x["draw_distance"] for x in rows]; m = [x["delta_norm"] for x in rows]
    ra = [x["distance_over_norm"] for x in rows]; cs = [x["cosine_between_draws"] for x in rows]
    summ = dict(region="__summary__", draw_distance="",
                delta_norm=f"spearman(dist,norm)={spear(d,m):+.3f}",
                distance_over_norm=f"spearman(ratio,norm)={spear(ra,m):+.3f} mean={np.mean(ra):.3f}",
                cosine_between_draws=f"mean={np.mean(cs):+.3f} spearman(cos,norm)={spear(cs,m):+.3f}")
    with (DATA / "region_draw_consistency.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        w.writerows(rows); w.writerow(summ)
    for x in rows + [summ]:
        print("  ", x)

if __name__ == "__main__":
    main()
