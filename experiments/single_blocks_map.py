# -*- coding: utf-8 -*-
"""Descriptive map of docs/prereg_single_blocks_identifiability.md: per block and sign, the features
whose change has the SAME sign on all three prompts (largest mean |dz| first), band-0 and band-4
ratios, saturation ratio. Writes data/single_blocks_map.csv. Description, not a test. No render."""
import statistics, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent; DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "experiments"))
import groove_or_hole as G
import analyze_single_blocks as S
plan = G.read_csv(S.PLAN); meas = {r["file"]: r for r in G.read_csv(S.CACHE)}
cloud, feats, mu, sd = G.load_cloud()
base = {r["prompt_id"]: meas[r["expected_filename"]] for r in plan if r["arm"] == "baseline"}
cell = {(int(r["block_idx"]), r["sign"], r["prompt_id"]): meas[r["expected_filename"]] for r in plan if r["arm"] == "perturbation"}
zc = lambda row, c: (float(row[c]) - mu[feats.index(c)]) / sd[feats.index(c)]
short = {"stroke_width_median_px": "tratto", "stroke_width_std_px": "var.tratto", "stroke_width_cv": "cv.tratto",
         "edge_density": "densità bordi", "contour_mean_length_px": "lungh.contorni", "contour_n_components": "n.contorni",
         "crosshatch_entropy_mean": "tratteggio", "crosshatch_entropy_p90": "tratteggio p90", "color_top4_cluster_share": "4 colori dominanti",
         "color_cluster_entropy_norm": "entropia colore", "color_n_effective": "n.colori", "colorfulness_hs": "colorfulness",
         "luminance_hist_n_peaks": "picchi luminanza", "shadow_edge_transition_width_px": "morbidezza ombre",
         "shadow_edge_transition_width_std": "var.ombre", "glcm_contrast": "contrasto locale", "glcm_homogeneity": "omogeneità",
         "glcm_energy": "uniformità", "glcm_correlation": "correlazione", "lbp_entropy": "entropia micro-texture",
         "lbp_uniform_share": "texture uniforme", "fft_radial_slope": "pendenza spettro", "fft_high_freq_share": "alte frequenze"}
rows = []
for b in S.BLOCKS:
    line = []
    for sign in ("neg", "pos"):
        cons = []
        for c in feats:
            d = [zc(cell[(b, sign, p)], c) - zc(base[p], c) for p in S.PROMPTS]
            if all(x > 0 for x in d) or all(x < 0 for x in d):
                cons.append((statistics.fmean(d), c))
        cons.sort(key=lambda t: -abs(t[0]))
        r = lambda k: statistics.fmean(float(cell[(b, sign, p)][k]) / float(base[p][k]) for p in S.PROMPTS)
        top = ", ".join(f"{short.get(c,c)} {'↑' if v>0 else '↓'}{abs(v):.1f}" for v, c in cons[:3]) or "—"
        rows.append({"block": b, "sign": sign, "n_consistent_features": len(cons), "top3": top,
                     "band0": r("band0"), "band4": r("band4"), "sat": r("sat")})
        line.append(f"{sign}: [{len(cons):2}] {top:58} b0 {r('band0'):.2f} b4 {r('band4'):.2f} sat {r('sat'):.2f}")
    print(f"{b:02d} " + "\n   ".join(line))
G.write_csv(DATA / "single_blocks_map.csv", rows)
