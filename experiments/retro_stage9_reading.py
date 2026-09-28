#!/usr/bin/env python3
"""Stage 9 (Style Direction & Amplitude Ladder), re-read on texture axes.

benchmark_stage9 carries 300 renders:
  - Part 1 (Style variants, S1_photo .. S8_charcoal):
    40 baselines (8 styles x 5 seeds) + 240 perturbed cells (8 styles x 6 conditions x 5 seeds).
    Conditions: preset_pos (1x and 2x), blockshuf_neg (1x and 2x), rand_pos (1x and 2x).
  - Part 2 (Chaos Edges V2, I06, I07, I20, I24):
    20 renders (4 prompts x 5 seeds). PNG metadata verification reveals their prompt texts differ
    fundamentally from stage7a (e.g. I06 in stage9 is an elf ranger with teal rim light, while I06 in
    stage7a is a human knight in steel armor). Following project protocol (pitfall 69 avoidance),
    their baseline ratio columns are strictly left empty.

Four readings:
  1. Coherence behaviour across 8 style families;
  2. Dose ladder check: 1x (dose 1.0) vs 2x (dose 2.0) across preset, blockshuf, and rand_pos;
  3. Scale signatures: band energy ratios b0..b4, peak band, shape;
  4. Line-preserving movers (coherence >= 0.98) vs collapses.

Reads data/retro_texture_axes.csv. Writes data/retro_stage9_cells.csv and data/retro_stage9_summary.csv.
"""
import csv, math, os, re, statistics

SRC = "data/retro_texture_axes.csv"
BENCH = "benchmark_stage9/renders"
OUT_CELLS = "data/retro_stage9_cells.csv"
OUT_SUMM = "data/retro_stage9_summary.csv"
BANDS = [f"band{i}" for i in range(5)]
LABEL = ["1-2px", "2-4px", "4-8px", "8-16px", "16-32px"]

PAT_S = re.compile(r"^(S\d)_([a-z]+)_(.+)_seed(\d+)_00001_\.png$")
PAT_I = re.compile(r"^(I\d+)_(.+)_seed(\d+)_00001_\.png$")


def main():
    rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["bench"] == BENCH]

    s_rec = {}
    i_rec = {}
    unparsed = []

    for r in rows:
        f = r["file"]
        m_s = PAT_S.match(f)
        if m_s:
            style_num, style_name, cond, seed = m_s.group(1), m_s.group(2), m_s.group(3), m_s.group(4)
            style = f"{style_num}_{style_name}"
            s_rec[(style, cond, seed)] = r
            continue
        m_i = PAT_I.match(f)
        if m_i:
            p, cond, seed = m_i.group(1), m_i.group(2), m_i.group(3)
            i_rec[(p, cond, seed)] = r
            continue
        unparsed.append(f)

    if unparsed:
        print(f"ERROR: {len(unparsed)} files failed to parse: {unparsed}")
        raise ValueError("Unparsed files in stage9")

    baselines = {k: v for k, v in s_rec.items() if k[1] == "baseline"}
    s_perturbed = {k: v for k, v in s_rec.items() if k[1] != "baseline"}

    print(f"Parsed stage9: {len(s_perturbed)} S-perturbed + {len(baselines)} S-baselines + {len(i_rec)} I-unbaselined = {len(rows)} total files")
    assert len(s_perturbed) == 240 and len(baselines) == 40 and len(i_rec) == 20 and len(rows) == 300

    styles = sorted(list(set(k[0] for k in s_rec)))
    conds = sorted(list(set(k[1] for k in s_perturbed)))

    cells = []
    # Join S-perturbed with matching baseline (same style, same seed)
    for (style, cond, seed), r in sorted(s_perturbed.items()):
        b = baselines.get((style, "baseline", seed))
        if not b:
            raise KeyError(f"Missing baseline for style={style}, seed={seed}")
        b_ratios = [float(r[f]) / float(b[f]) for f in BANDS]
        co = float(r["coherence"]) / float(b["coherence"])
        ct = float(r["variance"]) / float(b["variance"])
        ch = float(r["chroma"]) / float(b["chroma"])
        d = math.sqrt(sum(math.log(max(v, 1e-6)) ** 2 for v in b_ratios) / 5)
        cells.append(dict(
            family="style_variant", prompt_or_style=style, condition=cond, seed=seed,
            has_baseline="true",
            coherence_ratio=f"{co:.5f}",
            **{f"band{i}_ratio": f"{b_ratios[i]:.4f}" for i in range(5)},
            peak_band=max(range(5), key=lambda i: b_ratios[i]),
            contrast_ratio=f"{ct:.5f}",
            chroma_ratio=f"{ch:.5f}",
            displacement=f"{d:.5f}"
        ))

    # Add un-baselined I-files with empty ratio columns
    for (p, cond, seed), r in sorted(i_rec.items()):
        cells.append(dict(
            family="chaos_v2", prompt_or_style=p, condition=cond, seed=seed,
            has_baseline="false",
            coherence_ratio="",
            band0_ratio="", band1_ratio="", band2_ratio="", band3_ratio="", band4_ratio="",
            peak_band="", contrast_ratio="", chroma_ratio="", displacement=""
        ))

    with open(OUT_CELLS, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cells[0].keys()))
        w.writeheader()
        for c in cells:
            w.writerow(c)
    print(f"Wrote {len(cells)} total cells (240 baselined + 20 unbaselined) to {OUT_CELLS}\n")

    # 1 -- Coherence behaviour by style
    print("  READING 1 -- Coherence ratio by Style family (n=30 per style):")
    print("  %-16s %6s %10s %10s %9s %11s" % ("style", "cells", "mean", "sd", "pct<0.9", "pct>=0.98"))
    for s in styles:
        sc = [c for c in cells if c["prompt_or_style"] == s and c["has_baseline"] == "true"]
        co_vals = [float(c["coherence_ratio"]) for c in sc]
        lo = sum(1 for x in co_vals if x < 0.90)
        hi = sum(1 for x in co_vals if x >= 0.98)
        print("  %-16s %6d %10.4f %10.4f %8.1f%% %10.1f%%" % (
            s, len(co_vals), statistics.fmean(co_vals), statistics.pstdev(co_vals),
            100 * lo / len(co_vals), 100 * hi / len(co_vals)
        ))

    # Aggregated conditions across styles
    summary_rows = []
    print("\n  READING 2 & 3 -- Condition summaries & scale signatures (n=40 per condition, pooled over 8 styles and 5 seeds):")
    hdr = "%-18s %9s %8s %10s %8s %9s %8s %6s %6s %6s %6s %6s %7s" % (
        "condition", "coherence", "pct<0.9", "pct>=0.98", "displ", "contrast", "chroma", "b0", "b1", "b2", "b3", "b4", "peak"
    )
    print("  " + hdr)
    for cname in conds:
        sc = [c for c in cells if c["condition"] == cname and c["has_baseline"] == "true"]
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
        print("  %-18s %9.4f %7.1f%% %9.1f%% %8.4f %9.4f %8.4f %6.3f %6.3f %6.3f %6.3f %6.3f   %s" % (
            cname, co_mean, 100 * lo / len(co_vals), 100 * hi / len(co_vals),
            d_mean, ct_mean, ch_mean, b_means[0], b_means[1], b_means[2], b_means[3], b_means[4], LABEL[peak]
        ))

    with open(OUT_SUMM, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary_rows[0].keys()))
        w.writeheader()
        for r in summary_rows:
            w.writerow(r)
    print(f"\nWrote summary of {len(summary_rows)} conditions to {OUT_SUMM}\n")

    # 2 -- Dose ladder check (1x vs 2x)
    print("  READING 2 -- Dose ladder rate check: 1x (dose 1.0) vs 2x (dose 2.0):")
    delta_log_dose = math.log(2.0 / 1.0)
    for pair_name, c1, c2 in [
        ("preset_pos", "preset_pos_1x", "preset_pos_2x"),
        ("blockshuf_neg", "blockshuf_neg_1x", "blockshuf_neg_2x"),
        ("rand_pos", "rand_pos_1x", "rand_pos_2x")
    ]:
        r1 = next(r for r in summary_rows if r["condition"] == c1)
        r2 = next(r for r in summary_rows if r["condition"] == c2)
        co1, co2 = float(r1["coherence_ratio"]), float(r2["coherence_ratio"])
        d1, d2 = float(r1["displacement"]), float(r2["displacement"])
        rate = (co2 - co1) / delta_log_dose
        print(f"    {pair_name:<14}: 1x coh={co1:.4f} (pct<0.9={r1['pct_below_0_90']}%) -> 2x coh={co2:.4f} (pct<0.9={r2['pct_below_0_90']}%)")
        print(f"                   delta_coh={co2-co1:+.4f}, rate d(coh)/d(log_dose)={rate:+.4f}, disp={d1:.4f} -> {d2:.4f}")

    # 4 -- Line-preserving movers vs collapses
    print("\n  READING 4 -- Line-preserving movers (coherence >= 0.98):")
    movers = sorted([r for r in summary_rows if float(r["coherence_ratio"]) >= 0.98],
                    key=lambda r: -float(r["displacement"]))
    for m in movers:
        print(f"    {m['condition']:<18}: displacement={m['displacement']}, coherence={m['coherence_ratio']}, pct>=0.98={m['pct_above_0_98']}%")

    print("\n  Collapse conditions (sorted by lowest coherence):")
    losers = sorted(summary_rows, key=lambda r: float(r["coherence_ratio"]))
    for l in losers:
        if float(l["coherence_ratio"]) < 0.98:
            print(f"    {l['condition']:<18}: displacement={l['displacement']}, coherence={l['coherence_ratio']}, pct<0.90={l['pct_below_0_90']}%")


if __name__ == "__main__":
    main()
