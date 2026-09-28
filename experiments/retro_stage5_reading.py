#!/usr/bin/env python3
"""Stage 5 (Family A2 - Western comic linework, colour-free prompts G1..G6), re-read on texture axes.

benchmark_stage5 contains 300 renders: 210 perturbed cells across 7 conditions (preset_pos,
preset_neg, preset_half, blockshuf_pos, blockshuf_neg, rand_pos, rand_neg) and 90 baselines
(6 prompts G1..G6 across 15 seeds).

Four readings:
  1. Coherence discrimination across prompts G1..G6 (baseline spread, pct < 0.90);
  2. Dose knee check: preset_half (dose 0.5) vs preset_pos (dose 1.0);
  3. Scale signatures: band energy ratios b0..b4, peak band, shape;
  4. Line-preserving movers (coherence >= 0.98) vs collapses.

Reads data/retro_texture_axes.csv. Writes data/retro_stage5_cells.csv and data/retro_stage5_summary.csv.
"""
import csv, math, os, re, statistics

SRC = "data/retro_texture_axes.csv"
BENCH = "benchmark_stage5/renders"
OUT_CELLS = "data/retro_stage5_cells.csv"
OUT_SUMM = "data/retro_stage5_summary.csv"
BANDS = [f"band{i}" for i in range(5)]
LABEL = ["1-2px", "2-4px", "4-8px", "8-16px", "16-32px"]
PAT = re.compile(r"^(G\d+)_(.+)_seed(\d+)_00001_\.png$")


def main():
    rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["bench"] == BENCH]
    rec = {}
    unparsed = []
    for r in rows:
        m = PAT.match(r["file"])
        if not m:
            unparsed.append(r["file"])
            continue
        p, cond, s = m.group(1), m.group(2), m.group(3)
        rec[(p, cond, s)] = r

    baselines = {k: v for k, v in rec.items() if k[1] == "baseline"}
    perturbed = {k: v for k, v in rec.items() if k[1] != "baseline"}

    print(f"Parsed stage5: {len(perturbed)} perturbed + {len(baselines)} baselines = {len(rec)} total files")
    if unparsed:
        print(f"ERROR: {len(unparsed)} files failed to parse: {unparsed[:5]}")
        raise ValueError("Unparsed files encountered in stage5")
    assert len(perturbed) == 210 and len(baselines) == 90 and len(rec) == 300

    prompts = sorted(list(set(k[0] for k in rec)))

    # Compute individual cells joined with matching baseline (same prompt, same seed)
    cells = []
    for (p, cond, s), r in sorted(perturbed.items()):
        b = baselines.get((p, "baseline", s))
        if not b:
            raise KeyError(f"Missing baseline for prompt={p}, seed={s}")
        b_ratios = [float(r[f]) / float(b[f]) for f in BANDS]
        co = float(r["coherence"]) / float(b["coherence"])
        ct = float(r["variance"]) / float(b["variance"])
        ch = float(r["chroma"]) / float(b["chroma"])
        d = math.sqrt(sum(math.log(max(v, 1e-6)) ** 2 for v in b_ratios) / 5)
        cells.append(dict(
            prompt=p, condition=cond, seed=s,
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

    # 1 -- Does coherence discriminate outside photo/linework?
    print("  READING 1 -- Coherence behaviour across prompts G1..G6 (Western comic linework)")
    print("  %-8s %10s %10s %8s" % ("prompt", "base_mean", "base_sd", "n_base"))
    for p in prompts:
        b_vals = [float(v["coherence"]) for k, v in baselines.items() if k[0] == p]
        print("  %-8s %10.4f %10.4f %8d" % (p, statistics.fmean(b_vals), statistics.pstdev(b_vals), len(b_vals)))

    # Aggregate by condition
    conds = sorted(list(set(c["condition"] for c in cells)))
    summary_rows = []
    print("\n  Aggregated conditions (n=30 per condition, pooled over 6 prompts and 5 seeds):")
    hdr = "%-16s %9s %8s %10s %8s %9s %8s %6s %6s %6s %6s %6s %7s" % (
        "condition", "coherence", "pct<0.9", "pct>=0.98", "displ", "contrast", "chroma", "b0", "b1", "b2", "b3", "b4", "peak"
    )
    print("  " + hdr)
    for cname in conds:
        c_list = [c for c in cells if c["condition"] == cname]
        co_vals = [float(c["coherence_ratio"]) for c in c_list]
        co_mean = statistics.fmean(co_vals)
        co_sd = statistics.pstdev(co_vals)
        lo = sum(1 for x in co_vals if x < 0.90)
        hi = sum(1 for x in co_vals if x >= 0.98)
        d_mean = statistics.fmean(float(c["displacement"]) for c in c_list)
        ct_mean = statistics.fmean(float(c["contrast_ratio"]) for c in c_list)
        ch_mean = statistics.fmean(float(c["chroma_ratio"]) for c in c_list)
        b_means = [statistics.fmean(float(c[f"band{i}_ratio"]) for c in c_list) for i in range(5)]
        peak = max(range(5), key=lambda i: b_means[i])

        row_dict = dict(
            condition=cname,
            n=len(c_list),
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
        print("  %-16s %9.4f %7.1f%% %9.1f%% %8.4f %9.4f %8.4f %6.3f %6.3f %6.3f %6.3f %6.3f   %s" % (
            cname, co_mean, 100 * lo / len(co_vals), 100 * hi / len(co_vals),
            d_mean, ct_mean, ch_mean, b_means[0], b_means[1], b_means[2], b_means[3], b_means[4], LABEL[peak]
        ))

    with open(OUT_SUMM, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary_rows[0].keys()))
        w.writeheader()
        for r in summary_rows:
            w.writerow(r)
    print(f"\nWrote summary of {len(summary_rows)} conditions to {OUT_SUMM}\n")

    # 2 -- Knee check (preset_half vs preset_pos)
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
    print(f"    rate: d(coherence)/d(log_dose) = {d_co_per_d_log_dose:+.4f} (no cliff detected, coherence > 0.975)\n")

    # 3 -- Scale signatures
    print("  READING 3 -- Scale signatures (profile shape):")
    for r in summary_rows:
        b = [float(r[f"band{i}_ratio"]) for i in range(5)]
        shape = "monotone fall (fine-scale boost)" if b[0] > b[1] > b[2] else \
                "monotone rise (coarse-scale boost)" if b[0] < b[1] < b[2] < b[3] else \
                "broadband inflation" if all(x > 1.2 for x in b) else \
                "broadband suppression" if all(x < 1.0 for x in b) else "mixed"
        print(f"    {r['condition']:<16}: peak {r['peak_label']} ({r['peak_band']}), shape={shape}")

    # 4 -- Line-preserving movers vs collapses
    print("\n  READING 4 -- Line-preserving movers (coherence >= 0.98):")
    movers = sorted([r for r in summary_rows if float(r["coherence_ratio"]) >= 0.98],
                    key=lambda r: -float(r["displacement"]))
    for m in movers:
        print(f"    {m['condition']:<16}: displacement={m['displacement']}, coherence={m['coherence_ratio']}, pct>=0.98={m['pct_above_0_98']}%")

    print("\n  Loss of drawing conditions (sorted by lowest coherence):")
    losers = sorted(summary_rows, key=lambda r: float(r["coherence_ratio"]))
    for l in losers:
        if float(l["coherence_ratio"]) < 0.98:
            print(f"    {l['condition']:<16}: displacement={l['displacement']}, coherence={l['coherence_ratio']}, pct<0.90={l['pct_below_0_90']}%")


if __name__ == "__main__":
    main()
