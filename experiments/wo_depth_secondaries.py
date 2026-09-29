# -*- coding: utf-8 -*-
"""
experiments/wo_depth_secondaries.py — S1..S4 of prereg_wo_depth.md, from data/wo_depth_profile.csv
and the z-displacements. S1-S4 are pre-registered at +-0.100; the same numbers at +-0.200/+-0.350
are printed alongside and are exploratory. Writes data/wo_depth_secondaries.csv. No render.
"""
import statistics, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))
import groove_or_hole as G
import analyze_wo_depth as A

prof = G.read_csv(A.OUT_PROFILE)
plan = G.read_csv(A.PLAN)
meas = {r["file"]: r for r in G.read_csv(A.CACHE)}
cloud, feats, mu, sd = G.load_cloud()
bor = {k: v.name for k, v in A.borrowed().items()}
Z = lambda fn: np.array(G.z_of([float(meas[fn][c]) for c in feats], mu, sd))
D = {}
for r in plan:
    if r["arm"] == "push":
        g, d = A.parse(r["condition"])
        D[(g, d, r["prompt_id"], r["seed"])] = Z(r["expected_filename"]) - Z(bor[(r["prompt_id"], r["seed"])])
seeds = sorted({k[3] for k in D})
m = lambda g, d, p, k: statistics.fmean(float(x[k]) for x in prof
                                         if x["group"] == g and float(x["dose"]) == d and x["prompt"] == p)
rows = []
for mag in (0.100, 0.200, 0.350):
    st = "confirmatory" if mag == 0.100 else "exploratory"
    for p in ("P01", "P02"):
        for sgn in (+1, -1):
            d = round(sgn * mag, 3)
            b0 = {g: m(g, d, p, "band0_ratio") for g in A.GROUPS}
            dz = {g: m(g, d, p, "dz_over_N") for g in A.GROUPS}
            dev = {g: abs(b0[g] - 1) for g in A.GROUPS}
            seq = [b0[g] for g in A.GROUPS]
            diffs = [seq[i + 1] - seq[i] for i in range(5)]
            inv = sum(1 for i in range(4) if diffs[i] * diffs[i + 1] < 0)
            rows.append({"status": st, "dose": f"{d:+.3f}", "prompt": p,
                         **{f"band0_{g}": b0[g] for g in A.GROUPS},
                         **{f"dzN_{g}": dz[g] for g in A.GROUPS},
                         "band0_union": m("union", d, p, "band0_ratio"),
                         "S2_largest_band0_dev": max(dev, key=dev.get),
                         "S3_adjacent_inversions": inv})
        # S4 antisymmetry, per group: cos(mean_seed dpos, mean_seed dneg)
        for g in A.GROUPS + ["union"]:
            a = sum(D[(g, mag, p, s)] for s in seeds) / 3
            b = sum(D[(g, -mag, p, s)] for s in seeds) / 3
            rows.append({"status": st, "dose": f"+-{mag:.3f}", "prompt": p, "S4_group": g,
                         "S4_cos_pos_neg": float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))})
G.write_csv(ROOT / "data" / "wo_depth_secondaries.csv", rows)

print("S1/S2/S3 — band 0 (1-2 px) ratio per group, seed mean; largest deviation; adjacent inversions")
for x in rows:
    if "S2_largest_band0_dev" in x:
        b = " ".join(f"{x['band0_'+g]:.3f}" for g in A.GROUPS)
        dz = " ".join(f"{x['dzN_'+g]:.2f}" for g in A.GROUPS)
        print(f"  [{x['status'][:4]}] {x['dose']} {x['prompt']}  b0: {b} | union {x['band0_union']:.3f} "
              f"| max={x['S2_largest_band0_dev']} inv={x['S3_adjacent_inversions']} | |dz|/N: {dz}")
print("\nS4 — cos(+d, -d) per group, seed-averaged (-1 = one axis, 0 = unrelated edits)")
for mag in ("+-0.100", "+-0.200", "+-0.350"):
    for p in ("P01", "P02"):
        xs = [x for x in rows if x.get("S4_group") and x["dose"] == mag and x["prompt"] == p]
        print(f"  {mag} {p}: " + "  ".join(f"{x['S4_group']} {x['S4_cos_pos_neg']:+.2f}" for x in xs))
