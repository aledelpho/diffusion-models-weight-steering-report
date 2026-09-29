# -*- coding: utf-8 -*-
"""
experiments/wo_depth_noise_diagnostic.py — POST HOC, not pre-registered.

The composition test of prereg_wo_depth.md compares the union's displacement with the SUM of six
slice displacements. If a slice's displacement is partly a seed-specific chaotic kick rather than a
reproducible direction, summing six of them sums six kicks, and rho < 1, cos < 1 follow even if the
reproducible parts compose perfectly. The pre-registration did not anticipate this. Three checks:

  1. reproducibility: mean pairwise cos of the SAME condition's displacement across the 3 seeds;
  2. the ceiling: the union's own reproducibility is an upper bound on how well anything, the sum of
     parts included, can agree with it at cos;
  3. seed-averaged composition: the same rho and cos on displacements averaged over the three seeds,
     which shrinks the seed-specific part by about sqrt(3).

Writes data/wo_depth_noise_diagnostic.csv. No render.
"""
import itertools, statistics, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))
import groove_or_hole as G
import analyze_wo_depth as A

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
cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
seeds = sorted({k[3] for k in D})
rows = []
for d in sorted({k[1] for k in D}):
    for p in ("P01", "P02"):
        rep = {g: statistics.fmean(cos(D[(g, d, p, a)], D[(g, d, p, b)])
                                   for a, b in itertools.combinations(seeds, 2))
               for g in A.GROUPS + ["union"]}
        Ub = sum(D[("union", d, p, s)] for s in seeds) / 3
        Sb = sum(sum(D[(g, d, p, s)] for g in A.GROUPS) for s in seeds) / 3
        rows.append({"dose": f"{d:+.3f}", "prompt": p,
                     "status": "confirmatory-dose" if abs(d) == A.CONFIRMATORY else "exploratory-dose",
                     "repro_union": rep["union"],
                     "repro_slices_mean": statistics.fmean(rep[g] for g in A.GROUPS),
                     **{f"repro_{g}": rep[g] for g in A.GROUPS},
                     "rho_seedavg": float(np.linalg.norm(Ub) / np.linalg.norm(Sb)),
                     "cos_seedavg": cos(Ub, Sb)})
G.write_csv(ROOT / "data" / "wo_depth_noise_diagnostic.csv", rows)
print(f"{'dose':>7} {'p':3} | riproducibilita' fra semi: unione  fette(media)  [b1..b6]        | composizione su media dei semi: rho   cos")
for x in rows:
    sl = " ".join(f"{x['repro_'+g]:+.2f}" for g in A.GROUPS)
    print(f"{x['dose']:>7} {x['prompt']} |   {x['repro_union']:+.3f}   {x['repro_slices_mean']:+.3f}   [{sl}] |   {x['rho_seedavg']:.3f}  {x['cos_seedavg']:.3f}")
