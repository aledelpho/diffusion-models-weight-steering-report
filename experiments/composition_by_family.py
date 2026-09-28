#!/usr/bin/env python3
"""Does `Block_4` compose better than `Block_6` on an axis that was not used to say so?

block4_vs_block6_synthesis.md section 2(a) reports that Block_6's sub-blocks are 2.6x less
predictable from their parts than Block_4's, measured on contrast and grain -- the same statistics
the masks were designed with. That is suggestive and circular in equal measure.

Structure coherence was invented afterwards, for a different question (whether an edit keeps the
drawn line), and never entered the mask design. If the two-mechanisms reading is right, the same
separation must appear there too. This tests it.

Predictions compose multiplicatively, the same rule the mask bench used: a condition's coherence
ratio is predicted by the product of its members' single-block ratios, with each member's sign
flipped for the negative arm. Six comparisons per family -- four mask/anti conditions and the group
against its own members, both arms.

Exact two-sided Mann-Whitney on the absolute deviations, 6 against 6.
Writes data/composition_by_family.csv. No render, no new measurement.
"""
import csv, itertools, statistics

SRC = "data/texture_anisotropy.csv"
OUT = "data/composition_by_family.csv"
SPEC = {"B4_mask": {15: +1, 18: -1}, "B4_anti": {15: +1, 18: +1},
        "B6_mask": {27: +1, 26: -1}, "B6_anti": {27: +1, 26: +1}}
GROUP = {"Block_4": [15, 16, 17, 18, 19], "Block_6": [24, 25, 26, 27]}


def mw_exact(a, b):
    allv = sorted(a + b)
    rk, i = {}, 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j+1] == allv[i]:
            j += 1
        for k in range(i, j+1):
            rk[allv[k]] = (i + j) / 2 + 1
        i = j + 1
    obs = sum(rk[v] for v in a)
    n, k = len(allv), len(a)
    ranks = [rk[v] for v in allv]
    mean = k * (n + 1) / 2
    cnt = tot = 0
    for c in itertools.combinations(range(n), k):
        tot += 1
        if abs(sum(ranks[i] for i in c) - mean) >= abs(obs - mean) - 1e-9:
            cnt += 1
    return cnt / tot


def main():
    coh = {(x["condition"], x["arm"]): float(x["coherence_ratio"])
           for x in csv.DictReader(open(SRC, encoding="utf-8"))}
    rows = []
    for c, spec in SPEC.items():
        for arm in ("pos", "neg"):
            pred = 1.0
            for i, s in spec.items():
                sg = ("pos" if s > 0 else "neg") if arm == "pos" else ("neg" if s > 0 else "pos")
                pred *= coh[(f"blk{i:02d}", sg)]
            rows.append(dict(family=c[:2], condition=c, arm=arm, kind="mask",
                             predicted=f"{pred:.4f}", observed=f"{coh[(c, arm)]:.4f}",
                             deviation=f"{coh[(c, arm)] - pred:+.4f}"))
    for g, mem in GROUP.items():
        for arm in ("pos", "neg"):
            pred = 1.0
            for i in mem:
                pred *= coh[(f"blk{i:02d}", arm)]
            fam = "B4" if g == "Block_4" else "B6"
            rows.append(dict(family=fam, condition=g, arm=arm, kind="group",
                             predicted=f"{pred:.4f}", observed=f"{coh[(g, arm)]:.4f}",
                             deviation=f"{coh[(g, arm)] - pred:+.4f}"))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    a = [abs(float(r["deviation"])) for r in rows if r["family"] == "B4"]
    b = [abs(float(r["deviation"])) for r in rows if r["family"] == "B6"]
    for r in rows:
        print("  %-11s %-4s %-6s pred %s  obs %s  %s"
              % (r["condition"], r["arm"], r["kind"], r["predicted"], r["observed"],
                 r["deviation"]))
    print(f"\n  Block_4 family: mean |deviation| {statistics.fmean(a):.4f}  max {max(a):.4f}  n={len(a)}")
    print(f"  Block_6 family: mean |deviation| {statistics.fmean(b):.4f}  max {max(b):.4f}  n={len(b)}")
    print(f"  exact two-sided Mann-Whitney p = {mw_exact(a, b):.5f}")
    print(f"  ratio of means {statistics.fmean(b)/statistics.fmean(a):.2f}x  -> {OUT}")


if __name__ == "__main__":
    main()
