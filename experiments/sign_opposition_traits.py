#!/usr/bin/env python3
"""Observer prediction O1 / O1' -- sign opposition in the extracted traits.

Pre-registration: docs/observer_prediction_sign_opposition.md (commit 4706b78),
deposited before this script was run.

Corpus: data/style_features_qkvo.csv, 433 rows. Baseline per (scene, seed) is the
normscales_all control, whose displacement is exactly zero everywhere.
"""
import csv, re, collections
import numpy as np

rows = list(csv.DictReader(open("data/style_features_qkvo.csv")))
NON = {"file", "width_px", "height_px"}
traits = [c for c in rows[0] if c not in NON]

def parse(f):
    m = re.match(r"^(S\d+_\w+?)_Arthemy_QKVO_(.+?)_(pos|neg)_seed(\d+)_", f)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3), m.group(4)

tab = {}
for r in rows:
    k = parse(r["file"])
    if k is None:
        print("unparsed:", r["file"]); continue
    scene, cell, sign, seed = k
    tab[(scene, cell, sign, seed)] = {t: float(r[t]) for t in traits if r[t] not in ("", "nan")}

scenes = sorted({k[0] for k in tab})
cells = sorted({k[1] for k in tab})
seeds = sorted({k[3] for k in tab})
live = [c for c in cells if c != "normscales_all"]
print(f"traits {len(traits)}  scenes {len(scenes)}  cells {cells}  seeds {seeds}")

# --- seed-to-seed noise per trait, from the baseline (normscales) only: pitfall 33,
#     one standardisation taken from the controls, never from the treated cells.
noise = {}
for t in traits:
    devs = []
    for sc in scenes:
        v = [tab[(sc, "normscales_all", sg, sd)].get(t) for sg in ("pos", "neg") for sd in seeds
             if (sc, "normscales_all", sg, sd) in tab]
        v = [x for x in v if x is not None]
        if len(v) > 1:
            devs.append(np.std(v, ddof=1))
    noise[t] = float(np.mean(devs)) if devs else 0.0

def base(sc, sd, t):
    vals = [tab[(sc, "normscales_all", sg, sd)].get(t) for sg in ("pos", "neg")
            if (sc, "normscales_all", sg, sd) in tab]
    vals = [v for v in vals if v is not None]
    return float(np.mean(vals)) if vals else None

per_pair = []
for cell in live:
    for sc in scenes:
        for sd in seeds:
            kp, km = (sc, cell, "pos", sd), (sc, cell, "neg", sd)
            if kp not in tab or km not in tab:
                continue
            anyopp = 0; nopp = 0; nlive = 0; nopp_all = 0; nall = 0
            for t in traits:
                b = base(sc, sd, t)
                if b is None or t not in tab[kp] or t not in tab[km]:
                    continue
                dp = tab[kp][t] - b; dm = tab[km][t] - b
                if dp == 0 or dm == 0:
                    continue
                nall += 1
                if (dp > 0) != (dm > 0):
                    nopp_all += 1
                    anyopp = 1
                thr = noise[t]
                if abs(dp) > thr and abs(dm) > thr and thr > 0:
                    nlive += 1
                    if (dp > 0) != (dm > 0):
                        nopp += 1
            per_pair.append(dict(cell=cell, scene=sc, seed=sd, any_opposed=anyopp,
                                 n_all=nall, n_opposed_all=nopp_all,
                                 n_abovenoise=nlive, n_opposed_abovenoise=nopp))

n = len(per_pair)
print(f"\npairs analysed: {n}")
print("=" * 70)
print("O1  (his, as stated): fraction of pairs with AT LEAST ONE opposed trait")
frac = sum(p["any_opposed"] for p in per_pair) / n
print(f"    observed {frac*100:.1f}%   threshold 80%   -> {'CONFIRMED' if frac>0.80 else 'FALSIFIED'}")
print("    per cell (majority of its 24 pairs):")
for cell in live:
    sub = [p for p in per_pair if p["cell"] == cell]
    f2 = sum(p["any_opposed"] for p in sub) / len(sub)
    print(f"      {cell:16s} {f2*100:5.1f}%  ({len(sub)} pairs)")

print("=" * 70)
print("O1' (informative): fraction of ABOVE-NOISE traits that oppose  (chance 0.50)")
tot_l = sum(p["n_abovenoise"] for p in per_pair); tot_o = sum(p["n_opposed_abovenoise"] for p in per_pair)
print(f"    pooled {tot_o}/{tot_l} = {tot_o/tot_l:.4f}")
print(f"    all traits, no noise gate: {sum(p['n_opposed_all'] for p in per_pair)}/{sum(p['n_all'] for p in per_pair)} = "
      f"{sum(p['n_opposed_all'] for p in per_pair)/sum(p['n_all'] for p in per_pair):.4f}")
print("    per cell:")
for cell in live:
    sub = [p for p in per_pair if p["cell"] == cell]
    l = sum(p["n_abovenoise"] for p in sub); o = sum(p["n_opposed_abovenoise"] for p in sub)
    mean_live = l / len(sub)
    print(f"      {cell:16s} {o}/{l} = {o/l if l else float('nan'):.4f}   traits above noise per pair {mean_live:.1f}/{len(traits)}")

print("=" * 70)
print("per-trait opposition rate (above-noise pairs only), sorted")
per_t = []
for t in traits:
    l = o = 0
    for cell in live:
        for sc in scenes:
            for sd in seeds:
                kp, km = (sc, cell, "pos", sd), (sc, cell, "neg", sd)
                if kp not in tab or km not in tab: continue
                b = base(sc, sd, t)
                if b is None or t not in tab[kp] or t not in tab[km]: continue
                dp = tab[kp][t] - b; dm = tab[km][t] - b
                thr = noise[t]
                if thr > 0 and abs(dp) > thr and abs(dm) > thr:
                    l += 1
                    if (dp > 0) != (dm > 0): o += 1
    if l: per_t.append((o / l, o, l, t))
for r_, o, l, t in sorted(per_t, reverse=True):
    print(f"    {r_:.3f}  {o:4d}/{l:4d}  {t}")
