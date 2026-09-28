#!/usr/bin/env python3
"""Latent space benches: benchmark_latenti_b6 (18 renders) & benchmark_pavimento_rumore (32 renders).

Reads data/retro_texture_axes.csv.
Writes:
  - data/retro_latenti_b6_cells.csv
  - data/retro_latenti_b6_summary.csv
  - data/retro_pavimento_rumore_summary.csv
"""
import csv, math, os, re, statistics

SRC = "data/retro_texture_axes.csv"
BENCH_L = "benchmark_latenti_b6/renders"
BENCH_P = "benchmark_pavimento_rumore/renders"
OUT_L_CELLS = "data/retro_latenti_b6_cells.csv"
OUT_L_SUMM = "data/retro_latenti_b6_summary.csv"
OUT_P_SUMM = "data/retro_pavimento_rumore_summary.csv"

BANDS = [f"band{i}" for i in range(5)]
LABEL = ["1-2px", "2-4px", "4-8px", "8-16px", "16-32px"]

PAT_L = re.compile(r"^(P\d+)_(.+)_lat_0\.200_krea2_seed(\d+)_00001_\.png$")
PAT_B = re.compile(r"^(P\d+)_baseline_lat_krea2_seed(\d+)_00001_\.png$")


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    r_l = [r for r in rows if r["bench"] == BENCH_L]
    r_p = [r for r in rows if r["bench"] == BENCH_P]

    # Part 1: benchmark_latenti_b6
    rec_p = {}
    rec_b = {}
    unparsed_l = []
    for r in r_l:
        f = r["file"]
        m_p = PAT_L.match(f)
        if m_p:
            prompt, cond, seed = m_p.group(1), m_p.group(2), m_p.group(3)
            rec_p[(prompt, cond, seed)] = r
            continue
        m_b = PAT_B.match(f)
        if m_b:
            prompt, seed = m_b.group(1), m_b.group(2)
            rec_b[(prompt, seed)] = r
            continue
        unparsed_l.append(f)

    print(f"Parsed latenti_b6: {len(rec_p)} perturbed + {len(rec_b)} baselines = {len(r_l)} total files")
    if unparsed_l:
        raise ValueError("Unparsed files in latenti_b6")
    assert len(rec_p) == 12 and len(rec_b) == 6 and len(r_l) == 18

    cells_l = []
    for (p, cond, seed), r in sorted(rec_p.items()):
        b = rec_b.get((p, seed))
        if not b:
            raise KeyError(f"Missing baseline for prompt={p}, seed={seed}")
        b_ratios = [float(r[f]) / float(b[f]) for f in BANDS]
        co = float(r["coherence"]) / float(b["coherence"])
        ct = float(r["variance"]) / float(b["variance"])
        ch = float(r["chroma"]) / float(b["chroma"])
        d = math.sqrt(sum(math.log(max(v, 1e-6)) ** 2 for v in b_ratios) / 5)
        cells_l.append(dict(
            prompt=p, condition=cond, dose="0.200", seed=seed,
            coherence_ratio=f"{co:.5f}",
            **{f"band{i}_ratio": f"{b_ratios[i]:.4f}" for i in range(5)},
            peak_band=max(range(5), key=lambda i: b_ratios[i]),
            contrast_ratio=f"{ct:.5f}",
            chroma_ratio=f"{ch:.5f}",
            displacement=f"{d:.5f}"
        ))

    with open(OUT_L_CELLS, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cells_l[0].keys()))
        w.writeheader()
        for c in cells_l:
            w.writerow(c)
    print(f"Wrote {len(cells_l)} cells to {OUT_L_CELLS}\n")

    summary_l = []
    print("  LATENT B6 -- Condition summaries (n=6 each: 2 prompts * 3 seeds):")
    hdr = "%-12s %9s %8s %10s %8s %9s %8s %6s %6s %6s %6s %6s %7s" % (
        "condition", "coherence", "pct<0.9", "pct>=0.98", "displ", "contrast", "chroma", "b0", "b1", "b2", "b3", "b4", "peak"
    )
    print("  " + hdr)
    for cname in ["B6pos", "B6neg"]:
        sc = [c for c in cells_l if c["condition"] == cname]
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

        summary_l.append(dict(
            condition=cname,
            dose="0.200",
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
        ))
        print("  %-12s %9.4f %7.1f%% %9.1f%% %8.4f %9.4f %8.4f %6.3f %6.3f %6.3f %6.3f %6.3f   %s" % (
            cname, co_mean, 100 * lo / len(co_vals), 100 * hi / len(co_vals),
            d_mean, ct_mean, ch_mean, band_means[0], band_means[1], band_means[2], band_means[3], band_means[4], LABEL[peak]
        ))

    with open(OUT_L_SUMM, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary_l[0].keys()))
        w.writeheader()
        for r in summary_l:
            w.writerow(r)
    print(f"\nWrote summary of {len(summary_l)} conditions to {OUT_L_SUMM}\n")

    # Part 2: benchmark_pavimento_rumore (Noise Floor)
    rec_pr = {}
    unparsed_p = []
    for r in r_p:
        m = PAT_B.match(r["file"])
        if m:
            p, s = m.group(1), m.group(2)
            rec_pr[(p, s)] = r
        else:
            unparsed_p.append(r["file"])

    print(f"Parsed pavimento_rumore: {len(rec_pr)} baseline renders (unparsed: {len(unparsed_p)})")
    assert len(rec_pr) == 32

    summary_p = []
    print("\n  PAVIMENTO RUMORE (Baseline Inter-Seed Noise Floor across 16 seeds):")
    print("  %-6s %6s %10s %8s %8s %10s %8s %8s %10s %8s %8s" % (
        "prompt", "seeds", "coh_mean", "coh_sd", "coh_CV", "var_mean", "var_sd", "var_CV", "ch_mean", "ch_sd", "ch_CV"
    ))
    for p in ["P01", "P02"]:
        cohs = [float(v["coherence"]) for k, v in rec_pr.items() if k[0] == p]
        vars_ = [float(v["variance"]) for k, v in rec_pr.items() if k[0] == p]
        chs = [float(v["chroma"]) for k, v in rec_pr.items() if k[0] == p]
        c_mean, c_sd = statistics.fmean(cohs), statistics.pstdev(cohs)
        v_mean, v_sd = statistics.fmean(vars_), statistics.pstdev(vars_)
        ch_mean, ch_sd = statistics.fmean(chs), statistics.pstdev(chs)

        summary_p.append(dict(
            prompt=p, seeds=len(cohs),
            coherence_mean=f"{c_mean:.5f}", coherence_sd=f"{c_sd:.5f}", coherence_cv_pct=f"{c_sd/c_mean*100:.2f}%",
            variance_mean=f"{v_mean:.5f}", variance_sd=f"{v_sd:.5f}", variance_cv_pct=f"{v_sd/v_mean*100:.2f}%",
            chroma_mean=f"{ch_mean:.5f}", chroma_sd=f"{ch_sd:.5f}", chroma_cv_pct=f"{ch_sd/ch_mean*100:.2f}%"
        ))
        print("  %-6s %6d %10.4f %8.4f %7.2f%% %10.4f %8.4f %7.2f%% %10.4f %8.4f %7.2f%%" % (
            p, len(cohs), c_mean, c_sd, c_sd / c_mean * 100,
            v_mean, v_sd, v_sd / v_mean * 100,
            ch_mean, ch_sd, ch_sd / ch_mean * 100
        ))

    with open(OUT_P_SUMM, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary_p[0].keys()))
        w.writeheader()
        for r in summary_p:
            w.writerow(r)
    print(f"\nWrote noise floor summary to {OUT_P_SUMM}\n")


if __name__ == "__main__":
    main()
