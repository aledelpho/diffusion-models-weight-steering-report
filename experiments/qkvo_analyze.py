# -*- coding: utf-8 -*-
"""
experiments/qkvo_analyze.py
===========================
Governed by docs/RUNBOOK_qkvo_atlas_plan.md sections 3 and 4, frozen and committed before the
first of these 432 renders existed.

PRIMARY: G = A_proj - A_band, where
  A_proj = mean cosine between the SAME projection in the two bands        (4 pairs)
  A_band = mean cosine between DIFFERENT projections in the same band      (2 x 6 = 12 pairs)
averaged over the 8 prompts. Null: the 8 cells' (projection, band) labels are exchangeable; all
8! = 40320 relabellings enumerated exactly; two-sided. Floor 1/40320 = 2.48e-05.

  G < 0 beyond the null -> PROXIMITY: components at one depth act alike.
  G > 0 beyond the null -> FUNCTION: a projection keeps its identity across depth.
  inside the null       -> neither; report it and do not reach for a third reading.

SECONDARY, also frozen: cos(+,-) per cell (the rectification map, predicted to deviate more in the
late band); and the four projections ranked by mean distance to the other three within each band
(AnyStyle predicts wq separates).

NEGATIVE CONTROL: normscales +/- . If it is distinguishable from the baseline, the pipeline is
broken and nothing else is read.

Baselines are reused from the atlas corpus: the determinism check returned zero pixel difference
and the same SHA256 as 2026-09-25.
"""
from __future__ import annotations
import csv, itertools, math, os, re, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
F23 = ["stroke_width_median_px","stroke_width_std_px","stroke_width_cv","edge_density",
"contour_mean_length_px","contour_n_components","crosshatch_entropy_mean","crosshatch_entropy_p90",
"color_top4_cluster_share","color_cluster_entropy_norm","color_n_effective","colorfulness_hs",
"luminance_hist_n_peaks","shadow_edge_transition_width_px","shadow_edge_transition_width_std",
"glcm_contrast","glcm_homogeneity","glcm_energy","glcm_correlation","lbp_entropy",
"lbp_uniform_share","fft_radial_slope","fft_high_freq_share"]
PROJ = ["wq","wk","wv","wo"]; BANDS = ["b1","b6"]; SEEDS = ["42","777","1337"]
SCENES = ["S1_photo","S2_watercolor","S3_lowpoly","S4_claymation","S5_ukiyoe","S6_pixel","S7_glass","S8_charcoal"]

def load(path, key=lambda f: f):
    out = {}
    for r in csv.DictReader(Path(path).open(encoding="utf-8")):
        out[os.path.basename(r["file"])] = np.array([float(r[c]) for c in F23])
    return out

def main():
    qk = load(DATA / "style_features_qkvo.csv")
    at = load(DATA / "style_features_atlas_phase1.csv")
    base = {}
    for sc in SCENES:
        for s in SEEDS:
            fn = f"{sc}_baseline_seed{s}_00001_.png"
            if fn not in at:
                sys.exit(f"ABORT: baseline {fn} not in the atlas feature file")
            base[(sc, s)] = at[fn]

    cells, missing = {}, []
    for p in PROJ:
        for b in BANDS:
            for sg in ("pos", "neg"):
                for sc in SCENES:
                    for s in SEEDS:
                        fn = f"{sc}_Arthemy_QKVO_{p}_{b}_{sg}_seed{s}_00001_.png"
                        if fn in qk: cells[(p, b, sg, sc, s)] = qk[fn] - base[(sc, s)]
                        else: missing.append(fn)
    ctrl = {}
    for sg in ("pos", "neg"):
        for sc in SCENES:
            for s in SEEDS:
                fn = f"{sc}_Arthemy_QKVO_normscales_all_{sg}_seed{s}_00001_.png"
                if fn in qk: ctrl[(sg, sc, s)] = qk[fn] - base[(sc, s)]
                else: missing.append(fn)
    if missing: sys.exit(f"ABORT: {len(missing)} cells missing, e.g. {missing[:3]}")
    print(f"  {len(cells)} perturbed cells, {len(ctrl)} control cells, baselines reused from the atlas")

    # scale: pooled within-(preset, prompt) sd of Delta across seeds
    groups = []
    for p in PROJ:
        for b in BANDS:
            for sg in ("pos","neg"):
                for sc in SCENES:
                    groups.append(np.stack([cells[(p,b,sg,sc,s)] for s in SEEDS]))
    for sg in ("pos","neg"):
        for sc in SCENES:
            groups.append(np.stack([ctrl[(sg,sc,s)] for s in SEEDS]))
    sd = np.sqrt(np.mean(np.stack([g.var(axis=0, ddof=1) for g in groups]), axis=0))
    sd = np.where(sd > 0, sd, 1.0)

    def D(p,b,sg,sc): return np.mean([cells[(p,b,sg,sc,s)] for s in SEEDS], axis=0)/sd
    def Dc(sg,sc):    return np.mean([ctrl[(sg,sc,s)] for s in SEEDS], axis=0)/sd
    def cos(a,b):
        na,nb=np.linalg.norm(a),np.linalg.norm(b)
        return float(a@b/(na*nb)) if na>0 and nb>0 else float("nan")

    # --- NEGATIVE CONTROL
    mags=[float(np.linalg.norm(Dc(sg,sc))) for sg in ("pos","neg") for sc in SCENES]
    exact_zero = all(not np.any(np.stack([ctrl[(sg,sc,s)] for s in SEEDS])) for sg in ("pos","neg") for sc in SCENES)
    print(f"\n  NEGATIVE CONTROL normscales: |Delta| mean {np.mean(mags):.4f}, max {max(mags):.4f}, "
          f"exactly zero everywhere: {exact_zero}")
    live_mag = np.mean([float(np.linalg.norm(D(p,b,'pos',sc))) for p in PROJ for b in BANDS for sc in SCENES])
    print(f"  live cells |Delta| mean {live_mag:.4f}  -> control/live ratio {np.mean(mags)/live_mag:.4f}")

    # --- PRIMARY
    labels=[(p,b) for p in PROJ for b in BANDS]
    ia,ib=np.triu_indices(8,1)
    Cq=[]
    for sc in SCENES:
        V=[D(p,b,'pos',sc) for (p,b) in labels]
        M=np.zeros((8,8))
        for i in range(8):
            for j in range(8): M[i,j]=cos(V[i],V[j])
        Cq.append(M)
    Cq=np.stack(Cq)
    def G_of(perm):
        lab=[labels[perm[i]] for i in range(8)]
        sp=np.array([lab[i][0]==lab[j][0] and lab[i][1]!=lab[j][1] for i,j in zip(ia,ib)])
        sb=np.array([lab[i][1]==lab[j][1] and lab[i][0]!=lab[j][0] for i,j in zip(ia,ib)])
        c=Cq[:,ia,ib]
        ap=float(c[:,sp].mean()); ab=float(c[:,sb].mean())
        return ap-ab, ap, ab, int(sp.sum()), int(sb.sum())
    G,Ap,Ab,np_,nb_=G_of(list(range(8)))
    print(f"\n  A_proj = {Ap:+.4f} over {np_} pairs   A_band = {Ab:+.4f} over {nb_} pairs")
    print(f"  G = {G:+.4f}")
    null=np.array([G_of(list(pm))[0] for pm in itertools.permutations(range(8))])
    p2=float((np.abs(null)>=abs(G)).mean())
    print(f"  null over {len(null)} permutations: mean {null.mean():+.4f} sd {null.std():.4f} "
          f"p2.5 {np.percentile(null,2.5):+.4f} p97.5 {np.percentile(null,97.5):+.4f}")
    print(f"  p (two-sided, exact) = {p2:.6f}")
    verdict = ("function_component_carries_identity" if G>0 and p2<0.05 else
               "proximity_depth_dominates" if G<0 and p2<0.05 else "neither_inside_the_null")
    print(f"  VERDICT: {verdict}")

    # --- SECONDARY
    print("\n  antisymmetry cos(+,-) per cell:")
    anti={}
    for (p,b) in labels:
        v=float(np.mean([cos(D(p,b,'pos',sc), D(p,b,'neg',sc)) for sc in SCENES])); anti[(p,b)]=v
        print(f"    {p}_{b}: {v:+.4f}")
    print(f"    mean b1 {np.mean([anti[(p,'b1')] for p in PROJ]):+.4f}   "
          f"mean b6 {np.mean([anti[(p,'b6')] for p in PROJ]):+.4f}")
    print("\n  distinctiveness within band (mean distance to the other three):")
    rows=[]
    for b in BANDS:
        d={}
        for p in PROJ:
            d[p]=float(np.mean([np.linalg.norm(D(p,b,'pos',sc)-D(q,b,'pos',sc))
                                for q in PROJ if q!=p for sc in SCENES]))
        order=sorted(PROJ,key=lambda x:-d[x])
        print(f"    {b}: "+"  ".join(f"{p}={d[p]:.2f}" for p in order))
        rows.append((b,order[0],d))
    with (DATA/"qkvo_tests.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.writer(fh)
        w.writerow(["quantity","value","note"])
        w.writerow(["A_proj",round(Ap,6),f"{np_} pairs, same projection across bands"])
        w.writerow(["A_band",round(Ab,6),f"{nb_} pairs, different projections same band"])
        w.writerow(["G",round(G,6),"A_proj - A_band, primary"])
        w.writerow(["p_two_sided_exact",p2,f"{len(null)} permutations enumerated"])
        w.writerow(["null_mean",round(float(null.mean()),6),""]); w.writerow(["null_sd",round(float(null.std()),6),""])
        w.writerow(["verdict",verdict,"docs/RUNBOOK_qkvo_atlas_plan.md section 4"])
        w.writerow(["control_delta_norm_mean",round(float(np.mean(mags)),6),"normscales negative control"])
        w.writerow(["control_exactly_zero",exact_zero,""])
        w.writerow(["live_delta_norm_mean",round(float(live_mag),6),""])
        for (p,b),v in anti.items(): w.writerow([f"antisymmetry_{p}_{b}",round(v,6),"cos(+,-)"])
        for b,top,d in rows:
            for p in PROJ: w.writerow([f"distinctiveness_{p}_{b}",round(d[p],6),f"most distinct in {b}: {top}"])
    print("\n  wrote data/qkvo_tests.csv")

if __name__=="__main__":
    main()
