#!/usr/bin/env python3
"""Scores benchmark_leaf_collapse against the predictions frozen in
docs/RENDERS_2026-09-28_leaf_collapse_and_blk16.md section 3.

Foreground, chroma and hue exactly as experiments/colour_chroma_audit.py: value-based, 8x
low-passed, largest connected component. Blind to colour so it can see an object that lost its
colour, and low-passed so grain cannot manufacture foreground.

A HIT is chroma ratio < 0.20 against the cell's own baseline AND IoU >= 0.70 with it.

L2 needs a different rule, because an unperturbed render has no baseline of its own: an arm-A
baseline counts as collapsed when its foreground chroma is below 0.20x the MEDIAN of the twenty
arm-A baselines. The IoU clause is dropped there -- an unperturbed render is an intact object by
construction.

Writes data/leaf_collapse_cells.csv and data/leaf_collapse_verdict.csv. No render.
"""
import csv, math, os, statistics
import numpy as np
from PIL import Image
from scipy import ndimage

REN = os.path.expanduser("~/mnt/benchmark_leaf_collapse/renders")
PLAN = "data/leaf_collapse_plan.csv"
OUT = "data/leaf_collapse_cells.csv"
OUT_V = "data/leaf_collapse_verdict.csv"
HIT_CHROMA, HIT_IOU = 0.20, 0.70
CORPUS_RATE = 1 / 108


def load(path):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    mx, mn = a.max(2), a.min(2)
    d = mx - mn
    sat = np.where(mx > 1e-5, d / np.maximum(mx, 1e-5), 0.0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hue = np.zeros_like(mx)
    m = (mx == r) & (d > 1e-5); hue[m] = (60 * ((g[m] - b[m]) / d[m]) + 360) % 360
    m = (mx == g) & (d > 1e-5); hue[m] = (60 * ((b[m] - r[m]) / d[m]) + 120) % 360
    m = (mx == b) & (d > 1e-5); hue[m] = (60 * ((r[m] - g[m]) / d[m]) + 240) % 360
    small = np.asarray(Image.fromarray((mx * 255).astype(np.uint8)).resize(
        (mx.shape[1] // 8, mx.shape[0] // 8), Image.BOX), dtype=np.float32) / 255.0
    ring = np.concatenate([small[:5].ravel(), small[-5:].ravel(),
                           small[:, :5].ravel(), small[:, -5:].ravel()])
    msk = ndimage.binary_opening(np.abs(small - float(np.median(ring))) > 0.06, np.ones((3, 3)))
    lab, n = ndimage.label(msk)
    if n:
        msk = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
    fg = np.asarray(Image.fromarray((msk * 255).astype(np.uint8)).resize(
        (mx.shape[1], mx.shape[0]), Image.NEAREST)) > 127
    if not fg.any():
        return fg, 0.0, 0.0, 0.0
    s = sat[fg]
    rad = np.deg2rad(hue[fg])
    h = (float(np.rad2deg(np.arctan2((s * np.sin(rad)).sum(), (s * np.cos(rad)).sum())) % 360)
         if s.sum() > 1e-6 else 0.0)
    return fg, float(fg.mean()), float(s.mean()), h


def circ(a, b):
    d = abs(a - b) % 360.0
    return d if d <= 180 else 360 - d


def main():
    plan = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    base = {}
    for row in plan:
        if row["treatment"] == "none":
            base[(row["prompt_id"], row["seed"])] = load(f"{REN}/{row['expected_filename']}")
    rows = []
    for row in plan:
        if row["treatment"] == "none":
            continue
        fg, sh, ch, hu = load(f"{REN}/{row['expected_filename']}")
        bfg, bsh, bch, bhu = base[(row["prompt_id"], row["seed"])]
        inter, union = float((fg & bfg).sum()), float((fg | bfg).sum())
        iou = inter / union if union else 0.0
        cr = ch / bch if bch else 0.0
        rows.append(dict(arm=row["arm"], prompt_id=row["prompt_id"], seed=row["seed"],
                         fg_share=f"{sh:.5f}", iou=f"{iou:.5f}",
                         chroma=f"{ch:.4f}", baseline_chroma=f"{bch:.4f}",
                         chroma_ratio=f"{cr:.4f}", hue_deg=f"{hu:.2f}",
                         hue_shift_deg=f"{circ(hu, bhu):.2f}",
                         hit=int(cr < HIT_CHROMA and iou >= HIT_IOU)))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    print(f"wrote {len(rows)} perturbed cells to {OUT}")

    v = []
    def add(i, q, obs, verdict):
        v.append(dict(id=i, quantity=q, observed=obs, verdict=verdict))

    # L2 first: the control that can kill the rest.
    bch = {k: b[2] for k, b in base.items() if k[0] == "LN" and int(k[1]) >= 2001}
    med = statistics.median(bch.values())
    coll = [k for k, c in bch.items() if c < 0.20 * med]
    add("L2", "arm A baselines collapsing on their own (median chroma %.4f)" % med,
        f"{len(coll)}/{len(bch)}", "CONFIRMED -- the edit is the cause" if not coll
        else "FALSIFIED -- STOP, L1/L3/L4 unreadable: " + ", ".join(k[1] for k in coll))

    a = [r for r in rows if r["arm"] == "A_seeds"]
    k = sum(r["hit"] for r in a)
    p = sum(math.comb(len(a), i) * CORPUS_RATE**i * (1-CORPUS_RATE)**(len(a)-i)
            for i in range(k, len(a)+1))
    add("L1", "arm A hits (>=2 reproducible, 0 one-off)", f"{k}/{len(a)}, binomial p={p:.4f}",
        "CONFIRMED" if k >= 2 else ("FALSIFIED -- one-off" if k == 0 else "GREY -- exactly 1"))

    b_ = [r for r in rows if r["arm"] == "B_wording"]
    nb = len({r["prompt_id"] for r in b_ if r["hit"]})
    add("L3", "arm B wordings with at least one hit (>=2 preset-driven)",
        f"{nb}/5 wordings, {sum(r['hit'] for r in b_)}/{len(b_)} cells",
        "CONFIRMED" if nb >= 2 else ("FALSIFIED -- wording-specific" if nb == 0 else "GREY"))

    c_ = [r for r in rows if r["arm"] == "C_subject"]
    subj = {r["prompt_id"][:2] for r in c_ if r["hit"]}
    add("L4", "arm C subjects with at least one hit (>=2 subject-general)",
        f"{len(subj)}/4 subjects, {sum(r['hit'] for r in c_)}/{len(c_)} cells",
        "CONFIRMED" if len(subj) >= 2 else ("FALSIFIED -- leaf-specific" if not subj else "GREY"))

    # L5: prototypical < unusual < undeclared, hue undefined cells dropped.
    ok = 0; detail = []
    for code in ("MU", "TO", "PC", "BA"):
        m = {}
        for tag in ("P", "U", "N"):
            vals = [float(r["hue_shift_deg"]) for r in c_
                    if r["prompt_id"] == code + tag and float(r["chroma_ratio"]) >= 0.20]
            m[tag] = statistics.fmean(vals) if vals else float("nan")
        good = m["P"] < m["U"] < m["N"]
        ok += good
        detail.append(f"{code} {m['P']:.1f}/{m['U']:.1f}/{m['N']:.1f}{'*' if good else ''}")
    add("L5", "arm C: prototypical < unusual < undeclared (P/U/N mean hue shift)",
        f"{ok}/4 subjects: " + ", ".join(detail),
        "CONFIRMED" if ok >= 3 else "FALSIFIED")

    with open(OUT_V, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "quantity", "observed", "verdict"]); w.writeheader()
        for r in v: w.writerow(r)
    for r in v:
        print(f"  {r['id']}  {r['quantity']}\n        {r['observed']}  ->  {r['verdict']}")


if __name__ == "__main__":
    main()
