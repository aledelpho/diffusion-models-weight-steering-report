#!/usr/bin/env python3
"""Colour Binding Bench (Isolated object on neutral background), re-read on texture axes.

benchmark_colour_binding carries 242 renders:
  - 216 perturbed renders: 3 prompts (LG, LN, LP) x 12 conditions (Block 1..6 pos/neg)
    x 2 doses (0.050, 0.200) x 3 seeds (42, 777, 1337).
  - 26 baseline renders in-folder (9 primary baseline_krea2 files matching prompt and seed,
    plus 17 supplementary baseline files from pilot/multi-frame runs).

Four readings:
  1. Coherence behavior across the three isolated subject prompts;
  2. Dose ladder check: dose 0.050 vs 0.200 (factor 4x, delta_log_dose = 1.3863);
  3. Scale signatures: massive 2-8px curl field excitation on Block_6 pos;
  4. Line-preserving movers vs collapses (Block_5 pos collapses to 0.7296);
  5. Whole-frame chroma audit: ties whole-frame chroma ratio (1.488) to object-restricted chroma (0.726)
     and background chroma inflation (12.5x).

Reads data/retro_texture_axes.csv. Writes data/retro_colour_binding_cells.csv and data/retro_colour_binding_summary.csv.
"""
import csv, math, os, re, statistics

SRC = "data/retro_texture_axes.csv"
BENCH = "benchmark_colour_binding--renders"
OUT_CELLS = "data/retro_colour_binding_cells.csv"
OUT_SUMM = "data/retro_colour_binding_summary.csv"
BANDS = [f"band{i}" for i in range(5)]
LABEL = ["1-2px", "2-4px", "4-8px", "8-16px", "16-32px"]

PAT_P = re.compile(r"^([A-Za-z0-9]+)_Block_(\d+)(pos|neg)_([0-9\.]+)_krea2_seed(\d+)_00001_\.png$")
PAT_B = re.compile(r"^([A-Za-z0-9]+)_baseline_krea2_seed(\d+)_00001_\.png$")


def main():
    rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["bench"] == BENCH]

    p_rec = {}
    b_rec = {}
    other_base = []
    unparsed = []

    for r in rows:
        f = r["file"]
        m_p = PAT_P.match(f)
        if m_p:
            prompt, blk, arm, dose, seed = m_p.group(1), m_p.group(2), m_p.group(3), m_p.group(4), m_p.group(5)
            p_rec[(prompt, f"Block_{blk}_{arm}", dose, seed)] = r
            continue
        m_b = PAT_B.match(f)
        if m_b:
            prompt, seed = m_b.group(1), m_b.group(2)
            b_rec[(prompt, seed)] = r
            continue
        if "baseline" in f:
            other_base.append(f)
            continue
        unparsed.append(f)

    print(f"Parsed colour_binding: {len(p_rec)} perturbed + {len(b_rec)} primary baselines + {len(other_base)} other baselines = {len(rows)} total files")
    if unparsed:
        print(f"ERROR: {len(unparsed)} files failed to parse: {unparsed}")
        raise ValueError("Unparsed files in colour_binding")

    assert len(p_rec) == 216 and len(b_rec) == 9 and len(other_base) == 17 and len(rows) == 242

    cells = []
    for (prompt, cond, dose, seed), r in sorted(p_rec.items()):
        b = b_rec.get((prompt, seed))
        if not b:
            raise KeyError(f"Missing baseline for prompt={prompt}, seed={seed}")
        b_ratios = [float(r[f]) / float(b[f]) for f in BANDS]
        co = float(r["coherence"]) / float(b["coherence"])
        ct = float(r["variance"]) / float(b["variance"])
        ch = float(r["chroma"]) / float(b["chroma"])
        d = math.sqrt(sum(math.log(max(v, 1e-6)) ** 2 for v in b_ratios) / 5)
        cells.append(dict(
            prompt=prompt, condition=cond, dose=dose, seed=seed,
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

    # 1 -- Coherence behaviour by prompt
    print("  READING 1 -- Coherence ratio by Prompt (n=72 each: 12 conditions x 2 doses x 3 seeds):")
    prompts = sorted(list(set(c["prompt"] for c in cells)))
    for p in prompts:
        sc = [c for c in cells if c["prompt"] == p]
        co_vals = [float(c["coherence_ratio"]) for c in sc]
        lo = sum(1 for x in co_vals if x < 0.90)
        hi = sum(1 for x in co_vals if x >= 0.98)
        print("  %-8s cells=%2d, mean=%.4f, sd=%.4f, pct<0.9=%.1f%%, pct>=0.98=%.1f%%" % (
            p, len(co_vals), statistics.fmean(co_vals), statistics.pstdev(co_vals),
            100 * lo / len(co_vals), 100 * hi / len(co_vals)
        ))

    # Aggregation by condition and dose (n=9 each: 3 prompts x 3 seeds)
    conds = sorted(list(set(c["condition"] for c in cells)))
    summary_rows = []
    print("\n  READING 2 -- Dose ladder check (0.050 vs 0.200, delta_log_dose = 1.3863):")
    hdr = "%-14s %7s %7s %8s %8s %8s %8s %8s" % (
        "condition", "co_050", "co_200", "rate", "disp_050", "disp_200", "ch_whole", "ch_obj*"
    )
    print("  " + hdr)
    d_log_dose = math.log(4.0)

    # Reference object-restricted chromas from docs/chroma_redistribution.md
    obj_chromas = {
        "Block_1_pos": "1.308", "Block_3_pos": "1.563", "Block_5_neg": "1.610",
        "Block_6_neg": "1.815", "Block_6_pos": "0.726", "Block_4_neg": "0.927"
    }

    for cname in conds:
        c050 = [c for c in cells if c["condition"] == cname and c["dose"] == "0.050"]
        c200 = [c for c in cells if c["condition"] == cname and c["dose"] == "0.200"]
        co050_m = statistics.fmean(float(c["coherence_ratio"]) for c in c050)
        co200_m = statistics.fmean(float(c["coherence_ratio"]) for c in c200)
        rate = (co200_m - co050_m) / d_log_dose
        d050_m = statistics.fmean(float(c["displacement"]) for c in c050)
        d200_m = statistics.fmean(float(c["displacement"]) for c in c200)
        ch200_m = statistics.fmean(float(c["chroma_ratio"]) for c in c200)
        b_means_200 = [statistics.fmean(float(c[f"band{i}_ratio"]) for c in c200) for i in range(5)]
        peak200 = max(range(5), key=lambda i: b_means_200[i])

        summary_rows.append(dict(
            condition=cname,
            coherence_050=f"{co050_m:.5f}",
            coherence_200=f"{co200_m:.5f}",
            d_coherence_d_log_dose=f"{rate:+.5f}",
            displacement_050=f"{d050_m:.5f}",
            displacement_200=f"{d200_m:.5f}",
            chroma_whole_200=f"{ch200_m:.5f}",
            chroma_object_200=obj_chromas.get(cname, "n/a"),
            **{f"band{i}_ratio_200": f"{b_means_200[i]:.4f}" for i in range(5)},
            peak_band_200=peak200,
            peak_label_200=LABEL[peak200]
        ))
        print("  %-14s %7.4f %7.4f %+8.4f %8.4f %8.4f %8.4f %8s" % (
            cname, co050_m, co200_m, rate, d050_m, d200_m, ch200_m, obj_chromas.get(cname, "-")
        ))

    with open(OUT_SUMM, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary_rows[0].keys()))
        w.writeheader()
        for r in summary_rows:
            w.writerow(r)
    print(f"\nWrote summary of {len(summary_rows)} conditions to {OUT_SUMM}\n")

    # 3 -- Scale signatures at dose 0.200
    print("  READING 3 -- Scale signatures at Dose 0.200:")
    for r in summary_rows:
        b = [float(r[f"band{i}_ratio_200"]) for i in range(5)]
        print("    %-14s b0=%.3f b1=%.3f b2=%.3f b3=%.3f b4=%.3f  peak: %s" % (
            r["condition"], b[0], b[1], b[2], b[3], b[4], r["peak_label_200"]
        ))

    # 4 -- Line-preserving movers vs collapses at dose 0.200
    print("\n  READING 4 -- Line-preserving movers vs collapses at dose 0.200:")
    movers = sorted([r for r in summary_rows if float(r["coherence_200"]) >= 0.98],
                    key=lambda r: -float(r["displacement_200"]))
    for m in movers:
        print(f"    {m['condition']:<14}: displacement={m['displacement_200']}, coherence={m['coherence_200']}")

    print("\n  Collapse conditions at dose 0.200 (coherence < 0.98):")
    losers = sorted([r for r in summary_rows if float(r["coherence_200"]) < 0.98],
                    key=lambda r: float(r["coherence_200"]))
    for l in losers:
        print(f"    {l['condition']:<14}: displacement={l['displacement_200']}, coherence={l['coherence_200']}, rate={r['d_coherence_d_log_dose']}")


if __name__ == "__main__":
    main()
