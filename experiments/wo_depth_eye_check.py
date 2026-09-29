# -*- coding: utf-8 -*-
"""
experiments/wo_depth_eye_check.py — scores Alessandro's notes against the measures fixed in
docs/wo_depth_eye_mapping.md (deposited 75a1268 before this ran). Exploratory. No render.
E12/E13 reuse S4's statistic, whose values the analyst had already printed: not blind for him.
Writes data/wo_depth_eye_check.csv.
"""
import itertools, math, statistics, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))
import groove_or_hole as G
import analyze_wo_depth as A
from retro_texture_axes import measure

plan = G.read_csv(A.PLAN)
meas = {r["file"]: r for r in G.read_csv(A.CACHE)}
bor = A.borrowed()
borname = {k: v.name for k, v in bor.items()}
cell = {}
for r in plan:
    if r["arm"] == "push":
        g, d = A.parse(r["condition"])
        cell[(g, d, r["prompt_id"], r["seed"])] = r["expected_filename"]
seeds = sorted({k[3] for k in cell}); prompts = ("P01", "P02")
F = lambda fn, c: float(meas[fn][c])

def hue_dist(h, t=55.0):
    d = abs(h - t) % 360
    return min(d, 360 - d)

_colour = {}
def colour(fn, path):
    if fn not in _colour:
        _, _, _, sat, hue = measure(str(path))
        _colour[fn] = (sat, hue)
    return _colour[fn]

def feat_claim(eid, g, d, col, sign):
    out = []
    for p in prompts:
        for s in seeds:
            fn, bf = cell[(g, d, p, s)], borname[(p, s)]
            out.append((p, s, (F(fn, col) - F(bf, col)) * sign > 0, F(fn, col) / F(bf, col)))
    return out

def colour_claim(eid, g, d, kind, sign):
    out = []
    for p in prompts:
        for s in seeds:
            fn = cell[(g, d, p, s)]
            sat, hue = colour(fn, A.rp(fn))
            bsat, bhue = colour(borname[(p, s)], bor[(p, s)])
            if kind == "sat":
                out.append((p, s, (sat - bsat) * sign > 0, sat / bsat))
            else:
                out.append((p, s, hue_dist(hue) < hue_dist(bhue), ((hue - bhue + 180) % 360) - 180))
    return out

cloud, feats, mu, sd = G.load_cloud()
Z = lambda fn: np.array(G.z_of([F(fn, c) for c in feats], mu, sd))
def dz(g, d, p, s): return Z(cell[(g, d, p, s)]) - Z(borname[(p, s)])
def cos(a, b): return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

claims = [
    ("E1", "b1 -0.350 linee piu' spesse", lambda: feat_claim("E1", "b1", -0.35, "stroke_width_median_px", +1)),
    ("E2", "b1 -0.350 colori meno accentuati", lambda: feat_claim("E2", "b1", -0.35, "colorfulness_hs", -1)),
    ("E3", "b1 +0.350 linee piu' sottili", lambda: feat_claim("E3", "b1", 0.35, "stroke_width_median_px", -1)),
    ("E4", "b1 +0.350 colori piu' vibranti", lambda: feat_claim("E4", "b1", 0.35, "colorfulness_hs", +1)),
    ("E5", "b1 +0.350 tinte piatte", lambda: feat_claim("E5", "b1", 0.35, "color_n_effective", -1)),
    ("E6", "b3 -0.350 tratti spessi", lambda: feat_claim("E6", "b3", -0.35, "stroke_width_median_px", +1)),
    ("E7", "b3 -0.350 colori piatti", lambda: feat_claim("E7", "b3", -0.35, "color_n_effective", -1)),
    ("E8", "b3 +0.350 colori piu' accesi", lambda: feat_claim("E8", "b3", 0.35, "colorfulness_hs", +1)),
    ("E9", "b6 -0.350 piu' grigio", lambda: colour_claim("E9", "b6", -0.35, "sat", -1)),
    ("E10", "b6 -0.350 piu' giallino", lambda: colour_claim("E10", "b6", -0.35, "hue", 0)),
    ("E11", "b6 +0.350 colori si saturano", lambda: colour_claim("E11", "b6", 0.35, "sat", +1)),
    ("E12", "b2 piu' positivo simile al piu' negativo",
     lambda: [(p, s, cos(dz("b2", .35, p, s), dz("b2", -.35, p, s)) > 0, cos(dz("b2", .35, p, s), dz("b2", -.35, p, s)))
              for p in prompts for s in seeds]),
]
rows = []
def sign_p(k, n): return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
print(f"{'':4} {'affermazione':38} {'accordo':>7}  p(1 coda)  per prompt   valori (rapporto o scarto, per cella)")
for eid, text, fn in claims:
    res = fn()
    k = sum(r[2] for r in res)
    pp = {p: sum(r[2] for r in res if r[0] == p) for p in prompts}
    vals = " ".join(f"{r[3]:.3f}" if isinstance(r[3], float) else str(r[3]) for r in res)
    print(f"{eid:4} {text:38} {k}/6      {sign_p(k,6):.3f}     P01 {pp['P01']}/3 P02 {pp['P02']}/3   {vals}")
    for r in res:
        rows.append({"claim": eid, "text": text, "prompt": r[0], "seed": r[1], "agrees": r[2], "value": r[3]})

# E13 — clear (b1,b3,b6) vs unclear (b2,b4): seed-mean cos(+,-) at +-0.350
print("\nE13 — cos(Δ+, Δ−) medio sui semi a ±0.350 (piu' negativo = due poli opposti)")
sm = {}
for p in prompts:
    for g in A.GROUPS:
        a = sum(dz(g, .35, p, s) for s in seeds) / 3; b = sum(dz(g, -.35, p, s) for s in seeds) / 3
        sm[(g, p)] = cos(a, b)
    print(f"  {p}: " + "  ".join(f"{g} {sm[(g,p)]:+.2f}" for g in A.GROUPS))
    clear = [sm[(g, p)] for g in ("b1", "b3", "b6")]; unclear = [sm[(g, p)] for g in ("b2", "b4")]
    ok = max(clear) < min(unclear)
    print(f"      'chiare' b1,b3,b6 tutte sotto le 'non chiare' b2,b4: {ok}  (media chiare {statistics.fmean(clear):+.2f}, non chiare {statistics.fmean(unclear):+.2f})")
    rows.append({"claim": "E13", "text": "clear below unclear", "prompt": p, "seed": "mean", "agrees": ok,
                 "value": statistics.fmean(clear) - statistics.fmean(unclear)})
G.write_csv(ROOT / "data" / "wo_depth_eye_check.csv", rows)
