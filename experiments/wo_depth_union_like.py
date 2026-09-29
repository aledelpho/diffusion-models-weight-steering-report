# -*- coding: utf-8 -*-
"""
experiments/wo_depth_union_like.py — POST HOC. Operationalises Alessandro's answer to §8 of
prereg_wo_depth.md ("mi sembra l'unione di tutte insieme") as the one question it poses to the data:
is the union's displacement closer in direction to the SUM of the six slices than to ANY single
slice? Per cell (prompt, seed, dose), and on seed-averaged displacements.
Writes data/wo_depth_union_like.csv. No render.
"""
import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))
import groove_or_hole as G
import analyze_wo_depth as A

plan = G.read_csv(A.PLAN); meas = {r["file"]: r for r in G.read_csv(A.CACHE)}
cloud, feats, mu, sd = G.load_cloud(); bor = {k: v.name for k, v in A.borrowed().items()}
Z = lambda fn: np.array(G.z_of([float(meas[fn][c]) for c in feats], mu, sd))
D = {}
for r in plan:
    if r["arm"] == "push":
        g, d = A.parse(r["condition"])
        D[(g, d, r["prompt_id"], r["seed"])] = Z(r["expected_filename"]) - Z(bor[(r["prompt_id"], r["seed"])])
cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
seeds = sorted({k[3] for k in D}); rows = []
print(" dose    p  | celle in cui la somma batte ogni singola fetta | su media dei semi: cos(U,Σ) vs miglior fetta")
for d in sorted({k[1] for k in D}):
    for p in ("P01", "P02"):
        wins = 0
        for s in seeds:
            U = D[("union", d, p, s)]; S = sum(D[(g, d, p, s)] for g in A.GROUPS)
            best = max(A.GROUPS, key=lambda g: cos(U, D[(g, d, p, s)]))
            w = cos(U, S) > cos(U, D[(best, d, p, s)]); wins += w
            rows.append({"dose": f"{d:+.3f}", "prompt": p, "seed": s, "cos_U_sum": cos(U, S),
                         "best_slice": best, "cos_U_best_slice": cos(U, D[(best, d, p, s)]), "sum_wins": w})
        Ub = sum(D[("union", d, p, s)] for s in seeds) / 3
        Sb = sum(sum(D[(g, d, p, s)] for g in A.GROUPS) for s in seeds) / 3
        bb = max(A.GROUPS, key=lambda g: cos(Ub, sum(D[(g, d, p, s)] for s in seeds)))
        cb = cos(Ub, sum(D[(bb, d, p, s)] for s in seeds))
        print(f"{d:+.3f} {p} |                 {wins}/3                          |   {cos(Ub,Sb):.3f}  vs  {bb} {cb:.3f}")
G.write_csv(ROOT / "data" / "wo_depth_union_like.csv", rows)
tot = sum(r["sum_wins"] for r in rows)
print(f"\ntotale: la somma batte la miglior fetta singola in {tot}/{len(rows)} celle")
