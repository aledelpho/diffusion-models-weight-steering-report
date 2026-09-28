#!/usr/bin/env python3
"""Does the universal table reproduce the numbers already published from it?

data/retro_texture_axes.csv was computed with scipy filters (uniform_filter, convolve1d) for
speed, while the documents of 2026-09-28 used a hand-rolled cumsum box filter
(texture_anisotropy.py) and np.convolve with mode="same" (mask_damage_taxonomy.py). Those differ
at the frame edges. If the difference is not negligible the retro table cannot be compared with
anything already published from those scripts, and every re-reading built on it inherits the
mismatch silently.

So this recomputes, from the retro table only, the two quantities those documents report on
benchmark_rectified_masks, and prints the largest disagreement. No render, no new measurement.
"""
import csv, os, statistics

RETRO = "data/retro_texture_axes.csv"
ANISO = "data/texture_anisotropy.csv"
TAXO = "data/mask_damage_taxonomy.csv"
MASKS = "benchmark_rectified_masks/renders"
BASE = "benchmark_mappa--renders"
P = ["P01", "P02"]
S = ["42", "777", "1337"]
CONDS = ["B4_mask", "B4_anti", "B6_mask", "B6_anti", "B4B6_mask", "B4B6_anti"]


def main():
    t = {}
    for r in csv.DictReader(open(RETRO, encoding="utf-8")):
        t[(r["bench"], r["file"])] = r
    worst_c, worst_b = (0.0, ""), (0.0, "")
    rows = []
    aniso = {(x["condition"], x["arm"]): float(x["coherence_ratio"])
             for x in csv.DictReader(open(ANISO, encoding="utf-8"))}
    taxo = {}
    for x in csv.DictReader(open(TAXO, encoding="utf-8")):
        if x.get("condition") in CONDS and x.get("arm") in ("pos", "neg") and x.get("band2_ratio"):
            taxo[(x["condition"], x["arm"])] = float(x["band2_ratio"])

    for c in CONDS:
        for arm in ("pos", "neg"):
            co, b2 = [], []
            for p in P:
                for s in S:
                    x = t[(MASKS, f"{p}_{c}_{arm}_seed{s}_00001_.png")]
                    b = t[(BASE, f"{p}_baseline_krea2_seed{s}_00001_.png")]
                    co.append(float(x["coherence"]) / float(b["coherence"]))
                    b2.append(float(x["band2"]) / float(b["band2"]))
            mc, mb = statistics.fmean(co), statistics.fmean(b2)
            dc = abs(mc - aniso[(c, arm)])
            db = abs(mb - taxo[(c, arm)])
            worst_c = max(worst_c, (dc, f"{c} {arm}"))
            worst_b = max(worst_b, (db, f"{c} {arm}"))
            rows.append((c, arm, mc, aniso[(c, arm)], dc, mb, taxo[(c, arm)], db))

    print("  %-11s %-4s | coherence retro / published / diff | band2 retro / published / diff"
          % ("condition", "arm"))
    for c, arm, mc, pc, dc, mb, pb, db in rows:
        print("  %-11s %-4s |  %.4f   %.4f   %+.4f  |  %.4f   %.4f   %+.4f"
              % (c, arm, mc, pc, dc, mb, pb, db))
    print(f"\n  largest coherence disagreement  {worst_c[0]:.5f}  ({worst_c[1]})")
    print(f"  largest band-2 disagreement     {worst_b[0]:.5f}  ({worst_b[1]})")
    ok = worst_c[0] < 0.005 and worst_b[0] < 0.01
    print("\n  " + ("COMPARABLE -- the retro table can be read against the published documents"
                    if ok else
                    "NOT COMPARABLE -- the retro table must not be compared with those documents"))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
