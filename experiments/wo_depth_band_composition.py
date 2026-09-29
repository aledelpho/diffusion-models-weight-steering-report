# -*- coding: utf-8 -*-
"""
experiments/wo_depth_band_composition.py — POST HOC, not pre-registered.

The pre-registered composition test lives in 23-feature z space. On a single scalar — the band-0
(1-2 px) energy ratio — composition has a natural form: if the six slices act independently on
fine-grain energy, the union's ratio should be the PRODUCT of the six slice ratios, i.e. the sum of
their logs. Per render (same prompt, same seed), then seed-averaged.
Writes data/wo_depth_band_composition.csv. No render.
"""
import math, statistics, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))
import groove_or_hole as G
import analyze_wo_depth as A

prof = G.read_csv(A.OUT_PROFILE)
v = {(x["group"], float(x["dose"]), x["prompt"], x["seed"]): float(x["band0_ratio"]) for x in prof}
seeds = sorted({k[3] for k in v})
rows = []
for d in sorted({k[1] for k in v}):
    for p in ("P01", "P02"):
        pred = [sum(math.log(v[(g, d, p, s)]) for g in A.GROUPS) for s in seeds]
        obs = [math.log(v[("union", d, p, s)]) for s in seeds]
        # per-seed obs/pred of logs is ill-conditioned where the predicted log is near 0 (at +-0.100
        # it divides by ~0.02 and swings from -6.8 to 3.0): the ratio of the seed-mean logs is used
        mp, mo = statistics.fmean(pred), statistics.fmean(obs)
        rows.append({"dose": f"{d:+.3f}", "prompt": p,
                     "status": "confirmatory-dose" if abs(d) == A.CONFIRMATORY else "exploratory-dose",
                     "pred_union_band0": math.exp(statistics.fmean(pred)),
                     "obs_union_band0": math.exp(statistics.fmean(obs)),
                     "log_ratio_obs_over_pred": mo / mp,
                     "abs_gap_pct": 100 * abs(math.exp(mo) - math.exp(mp)) / math.exp(mp)})
G.write_csv(ROOT / "data" / "wo_depth_band_composition.csv", rows)
print(" dose   p   | prodotto delle 6 fette | unione osservata | ln oss / ln prev | scarto")
for x in rows:
    print(f"{x['dose']} {x['prompt']} |        {x['pred_union_band0']:.3f}          |      {x['obs_union_band0']:.3f}       |      {x['log_ratio_obs_over_pred']:.2f}        | {x['abs_gap_pct']:.1f}%")
