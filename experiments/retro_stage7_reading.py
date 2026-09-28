#!/usr/bin/env python3
"""Stage 7 (Western comic linework, 16 confirmation prompts I01..I24), re-read on texture axes.

benchmark_stage7 carries 480 renders (16 prompts x 6 conditions x 5 seeds) and 0 baselines in its
own folder. Its baselines live in benchmark_stage7a/renders (120 renders, 24 prompts x 5 seeds),
verified bit-for-bit on prompt text, KSampler settings (euler_ancestral, simple, 9 steps, cfg 1.0),
and dimensions (1024x1280).

Six conditions: preset_pos, preset_neg, blockshuf_pos, blockshuf_neg, rand_pos, rand_neg.

Four readings:
  1. Baseline coherence across 16 Western comic prompts I01..I24;
  2. Dose ladder check (single dose 1.0x across all conditions);
  3. Scale signatures: band energy ratios b0..b4, peak band, shape (replicated from Stage 5);
  4. Line-preserving movers (coherence >= 0.98) vs collapses.

Reads data/retro_texture_axes.csv. Writes data/retro_stage7_cells.csv and data/retro_stage7_summary.csv.
"""
import csv, math, os, re, statistics

SRC = "data/retro_texture_axes.csv"
BENCH_7 = "benchmark_stage7/renders"
BENCH_7A = "benchmark_stage7a/renders"
OUT_CELLS = "data/retro_stage7_cells.csv"
OUT_SUMM = "data/retro_stage7_summary.csv"
BANDS = [f"band{i}" for i in range(5)]
LABEL = ["1-2px", "2-4px", "4-8px", "8-16px", "16-32px"]

PAT_7 = re.compile(r"^(I\d+)_(.+)_seed(\d+)_00001_\.png$")
PAT_7A = re.compile(r"^(I\d+)_baseline_seed(\d+)_00001_\.png$")


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    r_7 = [r for r in rows if r["bench"] == BENCH_7]
    r_7a = [r for r in rows if r["bench"] == BENCH_7A]

    rec_7 = {}
    unparsed_7 = []
    for r in r_7:
        m = PAT_7.match(r["file"])
        if not m:
            unparsed_7.append(r["file"])
            continue
        p, cond, seed = m.group(1), m.group(2), m.group(3)
        rec_7[(p, cond, seed)] = r

    rec_7a = {}
    unparsed_7a = []
    for r in r_7a:
        m = PAT_7A.match(r["file"])
        if not m:
            unparsed_7a.append(r["file"])
            continue
        p, seed = m.group(1), m.group(2)
        rec_7a[(p, seed)] = r

    print(f"Parsed stage7: {len(rec_7)} perturbed renders (unparsed: {len(unparsed_7)})")
    print(f"Parsed stage7a: {len(rec_7a)} baseline renders (unparsed: {len(unparsed_7a)})")
    if unparsed_7 or unparsed_7a:
        raise ValueError("Unparsed files in stage7 or stage7a")

    assert len(rec_7) == 480 and len(rec_7a) == 120

    prompts = sorted(list(set(k[0] for k in rec_7)))
    conds = sorted(list(set(k[1] for k in rec_7)))
    seeds = sorted(list(set(k[2] for k in rec_7)))

    print(f"Structure: {len(prompts)} prompts * {len(conds)} conditions * {len(seeds)} seeds = {len(rec_7)}")
    assert len(prompts) == 16 and len(conds) == 6 and len(seeds) == 5

    cells = []
    for (p, cond, seed), r in sorted(rec_7.items()):
        b = rec_7a.get((p, seed))
        if not b:
            raise KeyError(f"Missing stage7a baseline for prompt={p}, seed={seed}")
        b_ratios = [float(r[f]) / float(b[f]) for f in BANDS]
        co = float(r["coherence"]) / float(b["coherence"])
        ct = float(r["variance"]) / float(b["variance"])
        ch = float(r["chroma"]) / float(b["chroma"])
        d = math.sqrt(sum(math.log(max(v, 1e-6)) ** 2 for v in b_ratios) / 5)
        cells.append(dict(
            prompt=p, condition=cond, seed=seed,
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

    # 1 -- Baseline coherence across 16 prompts
    print("  READING 1 -- Baseline coherence across 16 prompts (I01..I24, n=5 seeds each):")
    print("  %-8s %10s %10s" % ("prompt", "base_mean", "base_sd"))
    b_means = []
    for p in prompts:
        b_vals = [float(rec_7a[(p, s)]["coherence"]) for s in seeds]
        b_means.append(statistics.fmean(b_vals))
        print("  %-8s %10.4f %10.4f" % (p, statistics.fmean(b_vals), statistics.pstdev(b_vals)))
    print(f"  Overall: mean={statistics.fmean(b_means):.4f}, sd={statistics.pstdev(b_means):.4f}\n")

    # Aggregated by condition (n=80 each: 16 prompts * 5 seeds)
    summary_rows = []
    print("  READING 2 & 3 -- Condition summaries & scale signatures (n=80 each, 16 prompts * 5 seeds):")
    hdr = "%-16s %9s %8s %10s %8s %9s %8s %6s %6s %6s %6s %6s %7s" % (
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
        band_means = [statistics.fmean(float(c[f"band{i}_ratio"]) for c in sc) for i in range(5)]
        peak = max(range(5), key=lambda i: band_means[i])

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
            **{f"band{i}_ratio": f"{band_means[i]:.4f}" for i in range(5)},
            peak_band=peak,
            peak_label=LABEL[peak]
        )
        summary_rows.append(row_dict)
        print("  %-16s %9.4f %7.1f%% %9.1f%% %8.4f %9.4f %8.4f %6.3f %6.3f %6.3f %6.3f %6.3f   %s" % (
            cname, co_mean, 100 * lo / len(co_vals), 100 * hi / len(co_vals),
            d_mean, ct_mean, ch_mean, band_means[0], band_means[1], band_means[2], band_means[3], band_means[4], LABEL[peak]
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
        print(f"    {m['condition']:<16}: displacement={m['displacement']}, coherence={m['coherence_ratio']}, pct>=0.98={m['pct_above_0_98']}%")

    print("\n  Conditions with coherence < 0.98:")
    losers = sorted(summary_rows, key=lambda r: float(r["coherence_ratio"]))
    for l in losers:
        if float(l["coherence_ratio"]) < 0.98:
            print(f"    {l['condition']:<16}: displacement={l['displacement']}, coherence={l['coherence_ratio']}, pct<0.90={l['pct_below_0_90']}%")


if __name__ == "__main__":
    main()
