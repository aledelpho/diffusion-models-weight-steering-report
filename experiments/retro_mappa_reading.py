#!/usr/bin/env python3
"""The map, re-read on the two axes. No render, no image read -- everything from the retro table.

benchmark_mappa is the dose sweep: six block groups, two arms, six doses, two prompts, three
seeds. benchmark_profondita/_neg is the same thing at sub-block granularity, 28 blocks at 0.200.
Both were read, for weeks, with statistics that sum over scale and cannot tell a move from a
collapse.

Three questions the old statistics could not put:
  1. does an edit's damage accumulate smoothly with dose, or is there a knee?
  2. at what SCALE does each group act -- which is the quantity the observer's taxonomy showed the
     grain ratio had been hiding;
  3. which conditions raise the drawing rather than costing it.

Reads data/retro_texture_axes.csv. Writes data/retro_mappa_cells.csv, data/retro_mappa_dose.csv.
"""
import csv, math, os, statistics

SRC = "data/retro_texture_axes.csv"
B = "benchmark_mappa--renders"
POS, NEG = "benchmark_profondita/renders", "benchmark_profondita_neg/renders"
OUT, OUT_D = "data/retro_mappa_cells.csv", "data/retro_mappa_dose.csv"
P, S = ["P01", "P02"], ["42", "777", "1337"]
DOSES = ["0.020", "0.035", "0.050", "0.080", "0.120", "0.200"]
BANDS = [f"band{i}" for i in range(5)]
LABEL = ["1-2px", "2-4px", "4-8px", "8-16px", "16-32px"]


def main():
    t = {(r["bench"], r["file"]): r for r in csv.DictReader(open(SRC, encoding="utf-8"))}

    def cells(bench, tpl):
        out = []
        for p in P:
            for s in S:
                k = (bench, tpl.format(p=p, s=s))
                b = (B, f"{p}_baseline_krea2_seed{s}_00001_.png")
                if k in t and b in t:
                    out.append((t[k], t[b]))
        return out

    def agg(pairs):
        if not pairs:
            return None
        co = statistics.fmean(float(x["coherence"]) / float(b["coherence"]) for x, b in pairs)
        bd = [statistics.fmean(float(x[f]) / float(b[f]) for x, b in pairs) for f in BANDS]
        ct = statistics.fmean(float(x["variance"]) / float(b["variance"]) for x, b in pairs)
        ch = statistics.fmean(float(x["chroma"]) / float(b["chroma"]) for x, b in pairs)
        d = math.sqrt(sum(math.log(max(v, 1e-6)) ** 2 for v in bd) / 5)
        return co, bd, ct, ch, d, len(pairs)

    rows = []
    for g in range(1, 7):
        for arm in ("pos", "neg"):
            for dose in DOSES:
                a = agg(cells(B, "{p}_Block_%d%s_%s_krea2_seed{s}_00001_.png" % (g, arm, dose)))
                if a:
                    co, bd, ct, ch, d, n = a
                    rows.append(dict(family="group", condition=f"Block_{g}", arm=arm, dose=dose,
                                     n=n, coherence_ratio=f"{co:.5f}",
                                     **{f"{f}_ratio": f"{bd[i]:.4f}" for i, f in enumerate(BANDS)},
                                     peak_band=max(range(5), key=lambda i: bd[i]),
                                     contrast_ratio=f"{ct:.4f}", chroma_ratio=f"{ch:.4f}",
                                     displacement=f"{d:.5f}"))
    for blk in range(28):
        for arm, bench in (("pos", POS), ("neg", NEG)):
            a = agg(cells(bench, "{p}_blk%02d%s_0.200_krea2_seed{s}_00001_.png" % (blk, arm)))
            if a:
                co, bd, ct, ch, d, n = a
                rows.append(dict(family="subblock", condition=f"blk{blk:02d}", arm=arm,
                                 dose="0.200", n=n, coherence_ratio=f"{co:.5f}",
                                 **{f"{f}_ratio": f"{bd[i]:.4f}" for i, f in enumerate(BANDS)},
                                 peak_band=max(range(5), key=lambda i: bd[i]),
                                 contrast_ratio=f"{ct:.4f}", chroma_ratio=f"{ch:.4f}",
                                 displacement=f"{d:.5f}"))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    print(f"wrote {len(rows)} conditions to {OUT}\n")

    print("  1 -- COHERENCE ALONG THE DOSE LADDER (does the drawing go smoothly, or at a knee?)")
    print("  %-9s %-4s " % ("group", "arm") + " ".join(f"{d:>7}" for d in DOSES))
    dose_rows = []
    for g in range(1, 7):
        for arm in ("pos", "neg"):
            v = [next((float(r["coherence_ratio"]) for r in rows
                       if r["condition"] == f"Block_{g}" and r["arm"] == arm and r["dose"] == d),
                      float("nan")) for d in DOSES]
            print("  %-9s %-4s " % (f"Block_{g}", arm) + " ".join(f"{x:7.3f}" for x in v))
            dose_rows.append(dict(condition=f"Block_{g}", arm=arm,
                                  **{f"d{d}": f"{x:.4f}" for d, x in zip(DOSES, v)},
                                  drop_0020_to_0200=f"{v[0]-v[-1]:+.4f}"))
    with open(OUT_D, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(dose_rows[0].keys())); w.writeheader()
        for r in dose_rows: w.writerow(r)

    print("\n  2 -- AT WHAT SCALE DOES EACH GROUP ACT (band ratios at dose 0.200)")
    print("  %-9s %-4s " % ("group", "arm") + " ".join(f"{l:>8}" for l in LABEL) + "   peak")
    for g in range(1, 7):
        for arm in ("pos", "neg"):
            r = next((x for x in rows if x["condition"] == f"Block_{g}"
                      and x["arm"] == arm and x["dose"] == "0.200"), None)
            if r:
                print("  %-9s %-4s " % (f"Block_{g}", arm)
                      + " ".join(f"{float(r[f'{f}_ratio']):8.3f}" for f in BANDS)
                      + f"   {LABEL[int(r['peak_band'])]}")

    print("\n  3 -- SUB-BLOCKS THAT RAISE THE DRAWING (coherence > 1, sorted by displacement)")
    up = sorted([r for r in rows if r["family"] == "subblock"
                 and float(r["coherence_ratio"]) > 1.0],
                key=lambda r: -float(r["displacement"]))
    for r in up[:8]:
        print("  %-9s %-4s  displacement %s  coherence %s  peak %s"
              % (r["condition"], r["arm"], r["displacement"], r["coherence_ratio"],
                 LABEL[int(r["peak_band"])]))
    print(f"  {len(up)} of 56 single-block conditions raise it at all")


if __name__ == "__main__":
    main()
