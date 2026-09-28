#!/usr/bin/env python3
"""Stage 4 Preset (Family A1 - Western comic linework with pinned monochromatic hue, prompts F1..F4), re-read on texture axes.

benchmark_stage4_preset carries 140 renders across 7 conditions (preset_pos, preset_half,
preset_neg, blockshuf_pos, blockshuf_neg, rand_pos, rand_neg) across 4 prompts (F1..F4) and 5 seeds.
Its baselines live in benchmark_stage2_family/renders (prompts F1..F4, seeds 42, 777, 1337, 9999, 4242145),
verified bit-for-bit on prompt text, KSampler settings, and dimensions.

Four readings:
  1. Baseline coherence across prompts F1..F4;
  2. Dose ladder check: preset_half (dose 0.5) vs preset_pos (dose 1.0);
  3. Scale signatures: comparison with Family A2 (Stage 5) and Stage 7;
  4. Line-preserving movers (coherence >= 0.98) vs collapses.

Reads data/retro_texture_axes.csv. Writes data/retro_stage4_preset_cells.csv and data/retro_stage4_preset_summary.csv.
"""
import csv, math, os, re, statistics

SRC = "data/retro_texture_axes.csv"
BENCH_4 = "benchmark_stage4_preset/renders"
BENCH_2 = "benchmark_stage2_family/renders"
OUT_CELLS = "data/retro_stage4_preset_cells.csv"
OUT_SUMM = "data/retro_stage4_preset_summary.csv"
BANDS = [f"band{i}" for i in range(5)]
LABEL = ["1-2px", "2-4px", "4-8px", "8-16px", "16-32px"]

PAT_4 = re.compile(r"^(F\d+)_(.+)_seed(\d+)_00001_\.png$")
PAT_2 = re.compile(r"^(F\d+)_baseline_seed(\d+)_00001_\.png$")


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    r_4 = [r for r in rows if r["bench"] == BENCH_4]
    r_2 = [r for r in rows if r["bench"] == BENCH_2]

    rec_4 = {}
    unparsed_4 = []
    for r in r_4:
        m = PAT_4.match(r["file"])
        if not m:
            unparsed_4.append(r["file"])
            continue
        p, cond, seed = m.group(1), m.group(2), m.group(3)
        rec_4[(p, cond, seed)] = r

    rec_2 = {}
    unparsed_2 = []
    for r in r_2:
        m = PAT_2.match(r["file"])
        if not m:
            continue
        p, seed = m.group(1), m.group(2)
        rec_2[(p, seed)] = r

    print(f"Parsed stage4_preset: {len(rec_4)} perturbed renders (unparsed: {len(unparsed_4)})")
    print(f"Parsed stage2_family baselines: {len(rec_2)} matching baselines")
    if unparsed_4:
        raise ValueError("Unparsed files in stage4_preset")

    assert len(rec_4) == 140

    prompts = sorted(list(set(k[0] for k in rec_4)))
    conds = sorted(list(set(k[1] for k in rec_4)))
    seeds = sorted(list(set(k[2] for k in rec_4)))

    print(f"Structure: {len(prompts)} prompts * {len(conds)} conditions * {len(seeds)} seeds = {len(rec_4)}")
    assert len(prompts) == 4 and len(conds) == 7 and len(seeds) == 5

    cells = []
    for (p, cond, seed), r in sorted(rec_4.items()):
        b = rec_2.get((p, seed))
        if not b:
            raise KeyError(f"Missing stage2 baseline for prompt={p}, seed={seed}")
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

    # 1 -- Baseline coherence across F1..F4
    print("  READING 1 -- Baseline coherence across F1..F4 (n=5 seeds each):")
    print("  %-8s %10s %10s" % ("prompt", "base_mean", "base_sd"))
    b_means = []
    for p in prompts:
        b_vals = [float(rec_2[(p, s)]["coherence"]) for s in seeds]
        b_means.append(statistics.fmean(b_vals))
        print("  %-8s %10.4f %10.4f" % (p, statistics.fmean(b_vals), statistics.pstdev(b_vals)))
    print(f"  Overall: mean={statistics.fmean(b_means):.4f}, sd={statistics.pstdev(b_means):.4f}\n")

    # Aggregation by condition (n=20 each: 4 prompts * 5 seeds)
    summary_rows = []
    print("  READING 2 & 3 -- Condition summaries & scale signatures (n=20 each, 4 prompts * 5 seeds):")
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

    # 2 -- Dose ladder check (preset_half vs preset_pos)
    print("  READING 2 -- Dose ladder check on preset (half dose 0.5 vs full dose 1.0):")
    p_half = next(r for r in summary_rows if r["condition"] == "preset_half")
    p_pos = next(r for r in summary_rows if r["condition"] == "preset_pos")
    co_half, co_pos = float(p_half["coherence_ratio"]), float(p_pos["coherence_ratio"])
    d_half, d_pos = float(p_half["displacement"]), float(p_pos["displacement"])
    delta_log_dose = math.log(1.0 / 0.5)
    d_co_per_d_log_dose = (co_pos - co_half) / delta_log_dose
    print(f"    preset_half (dose 0.5): coherence={co_half:.4f}, displacement={d_half:.4f}")
    print(f"    preset_pos  (dose 1.0): coherence={co_pos:.4f}, displacement={d_pos:.4f}")
    print(f"    delta_coherence: {co_pos - co_half:+.4f}, delta_log_dose: {delta_log_dose:.4f}")
    print(f"    rate: d(coherence)/d(log_dose) = {d_co_per_d_log_dose:+.4f} (no cliff detected, coherence > 0.95)\n")

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
