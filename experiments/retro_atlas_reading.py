#!/usr/bin/env python3
"""The atlas, re-read on the two axes added on 2026-09-28. No render.

benchmark_atlas_phase1 carries 649 renders over EIGHT style families -- photo, watercolour,
lowpoly, claymation, ukiyo-e, pixel, glass, charcoal -- each with its own baseline. That makes it
the corpus register item C20 was going to spend renders on: structure coherence was validated only
on comic linework, which is the case where an orientation statistic should work best, and this
answers whether it says anything on seven other styles for free.

Two readings:
  1. does coherence behave, style by style -- is its spread on the untouched renders small enough
     for a ratio against it to mean anything, and does the ratio separate conditions within a style;
  2. which atlas conditions move the image a lot while losing the drawing -- the failure the old
     statistics could not see, now checkable across 8 styles instead of 1.

Reads data/retro_texture_axes.csv (absolute values, every render in the project).
Writes data/retro_atlas_cells.csv and data/retro_atlas_summary.csv.
"""
import csv, math, os, re, statistics

SRC = "data/retro_texture_axes.csv"
BENCH = "benchmark_atlas_phase1--renders"
OUT = "data/retro_atlas_cells.csv"
OUT_S = "data/retro_atlas_summary.csv"
PAT = re.compile(r"^(S\d_[a-z]+)_(?:Arthemy_Atlas_)?(.+?)_seed(\d+)_00001_\.png$")


def main():
    rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["bench"] == BENCH]
    rec = {}
    for r in rows:
        m = PAT.match(r["file"])
        if not m or r["file"].startswith("determinism_check"):
            continue
        style, cond, seed = m.group(1), m.group(2), m.group(3)
        rec[(style, cond, seed)] = r
    styles = sorted({k[0] for k in rec})
    base = {(s, sd): rec[(s, "baseline", sd)] for s in styles
            for sd in {k[2] for k in rec if k[0] == s} if (s, "baseline", sd) in rec}

    cells = []
    for (style, cond, seed), r in sorted(rec.items()):
        if cond == "baseline" or (style, seed) not in base:
            continue
        b = base[(style, seed)]
        bands = [float(r[f"band{i}"]) / float(b[f"band{i}"]) for i in range(5)]
        cells.append(dict(
            style=style, condition=cond, seed=seed,
            coherence_ratio=f"{float(r['coherence'])/float(b['coherence']):.5f}",
            **{f"band{i}_ratio": f"{bands[i]:.4f}" for i in range(5)},
            peak_band=max(range(5), key=lambda i: bands[i]),
            contrast_ratio=f"{float(r['variance'])/float(b['variance']):.5f}",
            chroma_ratio=f"{float(r['chroma'])/float(b['chroma']):.5f}",
            displacement=f"{math.sqrt(sum(math.log(max(x, 1e-6))**2 for x in bands)/5):.5f}"))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cells[0].keys())); w.writeheader()
        for c in cells: w.writerow(c)
    print(f"wrote {len(cells)} perturbed cells over {len(styles)} styles to {OUT}\n")

    # 1 -- does coherence behave outside comic linework?
    print("  READING 1 -- is the coherence ratio usable, style by style?")
    print("  %-14s %8s %9s %9s %9s %7s" %
          ("style", "baseline", "cells", "mean", "spread", "below 0.9"))
    summ = []
    for s in styles:
        bs = [float(base[(s, sd)]["coherence"]) for sd in {k[2] for k in rec if k[0] == s}
              if (s, sd) in base]
        cs = [float(c["coherence_ratio"]) for c in cells if c["style"] == s]
        lo = sum(1 for x in cs if x < 0.90)
        print("  %-14s %8.4f %9d %9.4f %9.4f %6d%%" %
              (s, statistics.fmean(bs), len(cs), statistics.fmean(cs),
               statistics.pstdev(cs), round(100*lo/len(cs))))
        summ.append(dict(style=s, baseline_coherence=f"{statistics.fmean(bs):.4f}",
                         baseline_spread=f"{statistics.pstdev(bs):.4f}", cells=len(cs),
                         coherence_ratio_mean=f"{statistics.fmean(cs):.4f}",
                         coherence_ratio_sd=f"{statistics.pstdev(cs):.4f}",
                         pct_below_0_90=round(100*lo/len(cs))))
    with open(OUT_S, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summ[0].keys())); w.writeheader()
        for r in summ: w.writerow(r)

    # 2 -- conditions that move a lot and lose the drawing
    print("\n  READING 2 -- big movers that lost the line (pooled over seeds, by condition)")
    agg = {}
    for c in cells:
        agg.setdefault((c["style"], c["condition"]), []).append(c)
    scored = []
    for k, g in agg.items():
        scored.append((statistics.fmean(float(x["displacement"]) for x in g),
                       statistics.fmean(float(x["coherence_ratio"]) for x in g), k, len(g)))
    scored.sort(key=lambda t: t[1])
    print("  %-14s %-26s %8s %10s" % ("style", "condition", "displ.", "coherence"))
    for d, co, k, n in scored[:10]:
        print("  %-14s %-26s %8.4f %10.4f" % (k[0], k[1][:26], d, co))
    print("\n  and the ones that move most while KEEPING the line (coherence >= 0.98):")
    keep = sorted([t for t in scored if t[1] >= 0.98], key=lambda t: -t[0])
    for d, co, k, n in keep[:8]:
        print("  %-14s %-26s %8.4f %10.4f" % (k[0], k[1][:26], d, co))
    print(f"\n  {len(keep)} of {len(scored)} condition-style pairs keep the line at 0.98 or above")


if __name__ == "__main__":
    main()
