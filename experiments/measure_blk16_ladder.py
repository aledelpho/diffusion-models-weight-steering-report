#!/usr/bin/env python3
"""Scores benchmark_blk16_ladder against the predictions frozen in
docs/RENDERS_2026-09-28_leaf_collapse_and_blk16.md section 6.

Estimators identical to the ones the predictions were made with:
  style_shift -- norm of (ln contrast, ln grain, ln chroma, hue shift / 90), as in
                 experiments/style_damage_frontier.py
  coherence   -- structure-tensor (l1-l2)/(l1+l2) over 9x9, ratio to baseline, as in
                 experiments/texture_anisotropy.py
Baselines are benchmark_mappa, the same ones every other bench uses.

K3 re-renders a cell that already exists in benchmark_profondita from a different plan file: it is
a determinism and provenance check on the whole chain, not on blk16. Read it first.

Writes data/blk16_ladder_cells.csv and data/blk16_ladder_verdict.csv. No render.
"""
import csv, math, os, statistics
import numpy as np
from PIL import Image

H = os.path.expanduser("~/mnt")
REN = f"{H}/benchmark_blk16_ladder/renders"
BASE = f"{H}/benchmark_mappa--renders"
OUT = "data/blk16_ladder_cells.csv"
OUT_V = "data/blk16_ladder_verdict.csv"
P = ["P01", "P02"]
S = ["42", "777", "1337"]
DOSES = ["0.020", "0.035", "0.050", "0.080", "0.120", "0.200"]


def box(a, k=9):
    c = np.cumsum(np.cumsum(np.pad(a, ((1, 0), (1, 0))), 0), 1)
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def feats(path):
    im = Image.open(path)
    a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    g = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
    lp = (4*g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:])**2
    mx, mn = a.max(2), a.min(2)
    d = mx - mn
    sat = np.where(mx > 1e-5, d / np.maximum(mx, 1e-5), 0.0)
    r, gg, b = a[..., 0], a[..., 1], a[..., 2]
    hue = np.zeros_like(mx)
    m = (mx == r) & (d > 1e-5); hue[m] = (60 * ((gg[m] - b[m]) / d[m]) + 360) % 360
    m = (mx == gg) & (d > 1e-5); hue[m] = (60 * ((b[m] - r[m]) / d[m]) + 120) % 360
    m = (mx == b) & (d > 1e-5); hue[m] = (60 * ((r[m] - gg[m]) / d[m]) + 240) % 360
    ang = float(np.rad2deg(np.arctan2((sat*np.sin(np.deg2rad(hue))).sum(),
                                      (sat*np.cos(np.deg2rad(hue))).sum())) % 360)
    gy, gx = np.gradient(g)
    jxx, jyy, jxy = box(gx*gx), box(gy*gy), box(gx*gy)
    tr = jxx + jyy
    root = np.sqrt(np.maximum((jxx - jyy)**2 + 4*jxy**2, 0))
    coh = float(np.mean(np.where(tr > 1e-8, root / np.maximum(tr, 1e-8), 0.0)))
    return float(lp.mean()), float(g.var()), float(sat.mean()), ang, coh


def circ(a, b):
    d = abs(a - b) % 360.0
    return d if d <= 180 else 360 - d


def main():
    cache = {}
    def base(p, s):
        if (p, s) not in cache:
            cache[(p, s)] = feats(f"{BASE}/{p}_baseline_krea2_seed{s}_00001_.png")
        return cache[(p, s)]
    rows = []
    for dose in DOSES:
        for arm in ("pos", "neg"):
            for p in P:
                for s in S:
                    f = f"{REN}/{p}_blk16{arm}_{dose}_krea2_seed{s}_00001_.png"
                    if not os.path.exists(f):
                        print(f"  MISSING {os.path.basename(f)}"); continue
                    hb, vb, cb, ab, kb = base(p, s)
                    h, v, c, ang, k = feats(f)
                    contrast, chroma = v / vb, c / cb
                    grain = (h / v) / (hb / vb)
                    dh = circ(ang, ab)
                    style = math.sqrt(math.log(contrast)**2 + math.log(grain)**2 +
                                      math.log(chroma)**2 + (dh / 90.0)**2)
                    rows.append(dict(dose=dose, arm=arm, prompt=p, seed=s,
                                     contrast=f"{contrast:.5f}", grain=f"{grain:.5f}",
                                     chroma=f"{chroma:.5f}", hue_shift_deg=f"{dh:.2f}",
                                     style_shift=f"{style:.5f}",
                                     coherence_ratio=f"{k/kb:.5f}"))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    print(f"wrote {len(rows)} cells to {OUT}")

    def agg(dose, arm, field):
        v = [float(r[field]) for r in rows if r["dose"] == dose and r["arm"] == arm]
        return statistics.fmean(v), min(v), len(v)

    print("\n  dose    arm   style   coherence  (cells above 1)")
    for dose in DOSES:
        for arm in ("pos", "neg"):
            st, _, n = agg(dose, arm, "style_shift")
            co, _, _ = agg(dose, arm, "coherence_ratio")
            above = sum(1 for r in rows if r["dose"] == dose and r["arm"] == arm
                        and float(r["coherence_ratio"]) > 1)
            print(f"  {dose}  {arm}  {st:7.4f}  {co:8.4f}   {above}/{n}")

    v = []
    def add(i, q, obs, verdict):
        v.append(dict(id=i, quantity=q, observed=obs, verdict=verdict))

    st200 = agg("0.200", "pos", "style_shift")[0]
    co200 = agg("0.200", "pos", "coherence_ratio")[0]
    add("K3", "blk16 pos 0.200 reproduces its measured point (style 0.447 +-0.08, coherence 1.040 +-0.03)",
        f"style {st200:.4f}, coherence {co200:.4f}",
        "CONFIRMED" if abs(st200 - 0.447) <= 0.08 and abs(co200 - 1.040) <= 0.03
        else "FALSIFIED -- nothing else in this bench is readable")

    cos = [agg(d, "pos", "coherence_ratio")[0] for d in DOSES]
    bad = [d for d, c in zip(DOSES, cos) if c < 0.95 and float(d) <= 0.120]
    add("K1", "coherence at or above baseline across the positive ladder",
        ", ".join(f"{d}:{c:.3f}" for d, c in zip(DOSES, cos)),
        "CONFIRMED" if all(c >= 0.98 for c in cos)
        else ("FALSIFIED at " + ",".join(bad) if bad else "GREY"))

    sts = [agg(d, "pos", "style_shift")[0] for d in DOSES]
    inv = [(DOSES[i], sts[i] - sts[i+1]) for i in range(len(sts)-1) if sts[i] > sts[i+1]]
    worst = max((x[1] for x in inv), default=0.0)
    add("K2", "style grows monotonically with dose, positive arm",
        ", ".join(f"{d}:{x:.3f}" for d, x in zip(DOSES, sts)),
        "CONFIRMED" if not inv else ("FALSIFIED" if worst > 0.03 else "GREY -- inversion %.3f" % worst))

    con = agg("0.200", "neg", "coherence_ratio")[0]
    add("K4", "negative arm buys style by losing line (coherence < 0.98 at 0.200)",
        f"{con:.4f}", "CONFIRMED" if con < 0.98 else ("FALSIFIED" if con >= 1.00 else "GREY"))

    with open(OUT_V, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "quantity", "observed", "verdict"]); w.writeheader()
        for r in v: w.writerow(r)
    print()
    for r in v:
        print(f"  {r['id']}  {r['quantity']}\n        {r['observed']}  ->  {r['verdict']}")


if __name__ == "__main__":
    main()
