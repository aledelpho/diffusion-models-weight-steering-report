#!/usr/bin/env python3
"""QKVO Atlas, re-read on texture axes using verified baselines from benchmark_atlas_phase1.

benchmark_qkvo_atlas carries 433 renders: 432 perturbed cells across 18 conditions (Q, K, V, O
sub-matrices of attention in Block 1 and Block 6, plus normscales controls) and 1 determinism check.
Baselines are verified from benchmark_atlas_phase1--renders (same 8 style prompts and 3 seeds),
confirmed bit-for-bit identical via PNG metadata and zero-metric difference on the determinism check.

Four readings:
  1. Coherence behaviour across the 8 style families;
  2. Dose/ladder check (all conditions tested at dose 0.200, no multi-dose ladder);
  3. Scale signatures by sub-matrix (Wq/Wk vs Wv/Wo on Block 1 and Block 6);
  4. Line-preserving movers (coherence >= 0.98) vs collapses.

Reads data/retro_texture_axes.csv. Writes data/retro_qkvo_atlas_cells.csv and data/retro_qkvo_atlas_summary.csv.
"""
import csv, math, os, re, statistics

SRC = "data/retro_texture_axes.csv"
BENCH_Q = "benchmark_qkvo_atlas--renders"
BENCH_A = "benchmark_atlas_phase1--renders"
OUT_CELLS = "data/retro_qkvo_atlas_cells.csv"
OUT_SUMM = "data/retro_qkvo_atlas_summary.csv"
BANDS = [f"band{i}" for i in range(5)]
LABEL = ["1-2px", "2-4px", "4-8px", "8-16px", "16-32px"]
PAT_Q = re.compile(r"^(S\d_[a-z]+)_(?:Arthemy_QKVO_)?(.+)_seed(\d+)_00001_\.png$")
PAT_A = re.compile(r"^(S\d_[a-z]+)_(?:Arthemy_Atlas_)?(.+)_seed(\d+)_00001_\.png$")


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    q_rows = [r for r in rows if r["bench"] == BENCH_Q]
    a_rows = [r for r in rows if r["bench"] == BENCH_A]

    q_rec = {}
    unparsed_q = []
    det_checks = []
    for r in q_rows:
        if r["file"].startswith("determinism_check"):
            det_checks.append(r["file"])
            continue
        m = PAT_Q.match(r["file"])
        if not m:
            unparsed_q.append(r["file"])
            continue
        style, cond, seed = m.group(1), m.group(2), m.group(3)
        q_rec[(style, cond, seed)] = r

    a_base = {}
    for r in a_rows:
        m = PAT_A.match(r["file"])
        if m and m.group(2) == "baseline":
            a_base[(m.group(1), m.group(3))] = r

    print(f"Parsed QKVO: {len(q_rec)} perturbed + {len(det_checks)} determinism check = {len(q_rows)} files")
    print(f"Verified Atlas baselines: {len(a_base)} available across {len(set(k[0] for k in a_base))} styles")
    if unparsed_q:
        print(f"ERROR: {len(unparsed_q)} files failed to parse: {unparsed_q[:5]}")
        raise ValueError("Unparsed files in qkvo_atlas")

    assert len(q_rec) == 432 and len(det_checks) == 1 and len(q_rows) == 433
    assert len(a_base) == 24

    styles = sorted(list(set(k[0] for k in q_rec)))
    conds = sorted(list(set(k[1] for k in q_rec)))

    cells = []
    for (style, cond, seed), r in sorted(q_rec.items()):
        b = a_base.get((style, seed))
        if not b:
            raise KeyError(f"Missing atlas baseline for {style} seed {seed}")
        b_ratios = [float(r[f]) / float(b[f]) for f in BANDS]
        co = float(r["coherence"]) / float(b["coherence"])
        ct = float(r["variance"]) / float(b["variance"])
        ch = float(r["chroma"]) / float(b["chroma"])
        d = math.sqrt(sum(math.log(max(v, 1e-6)) ** 2 for v in b_ratios) / 5)
        cells.append(dict(
            style=style, condition=cond, seed=seed,
            coherence_ratio=f"{co:.5f}",
            **{f"band{i}_ratio": f"{b_ratios[i]:.4f}" for i in range(5)},
            peak_band=max(range(5), key=lambda i: b_ratios[i]),
            contrast_ratio=f"{ct:.5f}",
            chroma_ratio=f"{ch:.5f}",
            displacement=f"{d:.5f}"
        ))

    with open(OUT_CELLS, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cells[0].keys()))
        w.writeheader()
        for c in cells:
            w.writerow(c)
    print(f"Wrote {len(cells)} cells to {OUT_CELLS}\n")

    # 1 -- Coherence behaviour style by style
    print("  READING 1 -- Coherence ratio behaviour across 8 styles (QKVO sub-matrices):")
    print("  %-16s %6s %10s %10s %9s %11s" % ("style", "cells", "mean", "sd", "pct<0.9", "pct>=0.98"))
    for s in styles:
        sc = [c for c in cells if c["style"] == s]
        co_vals = [float(c["coherence_ratio"]) for c in sc]
        lo = sum(1 for x in co_vals if x < 0.90)
        hi = sum(1 for x in co_vals if x >= 0.98)
        print("  %-16s %6d %10.4f %10.4f %8.1f%% %10.1f%%" % (
            s, len(co_vals), statistics.fmean(co_vals), statistics.pstdev(co_vals),
            100 * lo / len(co_vals), 100 * hi / len(co_vals)
        ))

    # 2 -- Aggregation by condition
    summary_rows = []
    print("\n  READING 2 & 3 -- Sub-matrix scale signatures (n=24 per condition, pooled over 8 styles and 3 seeds):")
    hdr = "%-22s %9s %8s %10s %8s %9s %8s %6s %6s %6s %6s %6s %7s" % (
        "condition", "coherence", "pct<0.9", "pct>=0.98", "displ", "contrast", "chroma", "b0", "b1", "b2", "b3", "b4", "peak"
    )
    print("  " + hdr)
    for cname in conds:
        sc = [c for c in cells if c["condition"] == cname]
        co_vals = [float(c["coherence_ratio"]) for c in sc]
        co_mean = statistics.fmean(co_vals)
        co_sd = statistics.pstdev(co_vals)
        lo = sum(1 for x in co_vals if x < 0.90)
        hi = sum(1 for x in co_vals if x >= 0.98)
        d_mean = statistics.fmean(float(c["displacement"]) for c in sc)
        ct_mean = statistics.fmean(float(c["contrast_ratio"]) for c in sc)
        ch_mean = statistics.fmean(float(c["chroma_ratio"]) for c in sc)
        b_means = [statistics.fmean(float(c[f"band{i}_ratio"]) for c in sc) for i in range(5)]
        peak = max(range(5), key=lambda i: b_means[i])

        row_dict = dict(
            condition=cname,
            n=len(sc),
            coherence_ratio=f"{co_mean:.5f}",
            coherence_sd=f"{co_sd:.5f}",
            pct_below_0_90=round(100 * lo / len(co_vals), 1),
            pct_above_0_98=round(100 * hi / len(co_vals), 1),
            displacement=f"{d_mean:.5f}",
            contrast_ratio=f"{ct_mean:.5f}",
            chroma_ratio=f"{ch_mean:.5f}",
            **{f"band{i}_ratio": f"{b_means[i]:.4f}" for i in range(5)},
            peak_band=peak,
            peak_label=LABEL[peak]
        )
        summary_rows.append(row_dict)
        print("  %-22s %9.4f %7.1f%% %9.1f%% %8.4f %9.4f %8.4f %6.3f %6.3f %6.3f %6.3f %6.3f   %s" % (
            cname, co_mean, 100 * lo / len(co_vals), 100 * hi / len(co_vals),
            d_mean, ct_mean, ch_mean, b_means[0], b_means[1], b_means[2], b_means[3], b_means[4], LABEL[peak]
        ))

    with open(OUT_SUMM, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary_rows[0].keys()))
        w.writeheader()
        for r in summary_rows:
            w.writerow(r)
    print(f"\nWrote summary of {len(summary_rows)} conditions to {OUT_SUMM}\n")

    # 4 -- Line-preserving movers vs collapses
    print("  READING 4 -- Line-preserving movers (coherence >= 0.98):")
    movers = sorted([r for r in summary_rows if float(r["coherence_ratio"]) >= 0.98],
                    key=lambda r: -float(r["displacement"]))
    for m in movers:
        print(f"    {m['condition']:<22}: displacement={m['displacement']}, coherence={m['coherence_ratio']}, pct>=0.98={m['pct_above_0_98']}%")

    print("\n  Conditions with coherence < 0.98:")
    losers = sorted([r for r in summary_rows if float(r["coherence_ratio"]) < 0.98],
                    key=lambda r: float(r["coherence_ratio"]))
    for l in losers:
        print(f"    {l['condition']:<22}: displacement={l['displacement']}, coherence={l['coherence_ratio']}, pct<0.90={l['pct_below_0_90']}%")


if __name__ == "__main__":
    main()
