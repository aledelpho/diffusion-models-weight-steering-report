# -*- coding: utf-8 -*-
"""
experiments/score_observer_predictions.py
========================================
Scores the observer statements frozen in docs/observer_predictions_atlas_phase1.md
against the atlas corpus. The four compound criteria are exactly as frozen there; the
per-clause columns are reported so that a compound failure can be attributed to the clause
that failed rather than to the statement as a whole.
"""
import csv,os,numpy as np,collections
R=os.path.expanduser("~/mnt/diffusion-models-weight-steering-report/data")
F=["stroke_width_median_px","stroke_width_std_px","stroke_width_cv","edge_density",
"contour_mean_length_px","contour_n_components","crosshatch_entropy_mean","crosshatch_entropy_p90",
"color_top4_cluster_share","color_cluster_entropy_norm","color_n_effective","colorfulness_hs",
"luminance_hist_n_peaks","shadow_edge_transition_width_px","shadow_edge_transition_width_std",
"glcm_contrast","glcm_homogeneity","glcm_energy","glcm_correlation","lbp_entropy",
"lbp_uniform_share","fft_radial_slope","fft_high_freq_share"]
feats={os.path.basename(r["file"]):r for r in csv.DictReader(open(os.path.join(R,"style_features_atlas_phase1.csv"),encoding="utf-8"))}
base=collections.defaultdict(dict); pert=collections.defaultdict(dict)
for pl in ["perturbation_atlas_phase1_plan.csv","perturbation_atlas_phase2_plan.csv"]:
    for r in csv.DictReader(open(os.path.join(R,pl),encoding="utf-8")):
        if r["type"]=="determinism_check": continue
        row=feats[os.path.basename(r["expected_filename"])]
        v=np.array([float(row[c]) for c in F])
        (base if r["type"]=="baseline" else pert)[(r["condition"],r.get("draw","")) if r["type"]!="baseline" else r["prompt_id"]][(r["prompt_id"],r["seed"]) if r["type"]!="baseline" else r["seed"]]=v
prompts=sorted(base); seeds=sorted(base[prompts[0]]); presets=sorted(pert)
i={c:F.index(c) for c in ["edge_density","lbp_entropy","colorfulness_hs","glcm_contrast","fft_high_freq_share"]}
def cos(a,b):
    na,nb=np.linalg.norm(a),np.linalg.norm(b)
    return float(a@b/(na*nb)) if na and nb else float("nan")
A=("early_attn","2"); B=("late_mlp","2"); C=("model_only","2"); D=("late_attn","1")
def sd_scale():
    X=np.stack([[ [pert[p][(q,s)]-base[q][s] for s in seeds] for q in prompts] for p in presets])
    return np.sqrt(np.mean(X.var(axis=2,ddof=1).reshape(-1,len(F)),axis=0))
sd=np.where(sd_scale()>0,sd_scale(),1.0)
out=[]
for q in prompts:
    bm=np.stack([base[q][s] for s in seeds]); bmu=bm.mean(0); bsd=bm.std(0,ddof=1)
    dl={p:np.mean([pert[p][(q,s)]-base[q][s] for s in seeds],axis=0) for p in presets}
    dz={p:dl[p]/sd for p in presets}
    nrm={p:float(np.linalg.norm(dz[p])) for p in presets}
    rank=lambda p,key: 1+sorted(presets,key=lambda x:-key(x)).index(p)
    def gate(p):
        a=abs(dl[p][i["edge_density"]])>3*max(bsd[i["edge_density"]],1e-12)
        b=abs(dl[p][i["lbp_entropy"]])>3*max(bsd[i["lbp_entropy"]],1e-12)
        return bool(a or b)
    med=np.median([cos(dz[x],dz[y]) for a_,x in enumerate(presets) for y in presets[a_+1:]])
    res={
     "A_out_of_range":gate(A), "A_norm_upper_half": rank(A,lambda p:nrm[p])<=13,
     "B_out_of_range":gate(B), "B_cos_below_median": cos(dz[A],dz[B])<med,
     "C_colorfulness_up": bool(dl[C][i["colorfulness_hs"]]>0), "C_contrast_up": bool(dl[C][i["glcm_contrast"]]>0),
     "C_colorfulness_top5": rank(C,lambda p:dl[p][i["colorfulness_hs"]])<=5,
     "D_hf_up": bool(dl[D][i["fft_high_freq_share"]]>0), "D_hf_top8": rank(D,lambda p:dl[p][i["fft_high_freq_share"]])<=8,
     "D_closer_to_B_than_A": cos(dz[D],dz[B])>cos(dz[D],dz[A]),
    }
    hits={"A":res["A_out_of_range"] and res["A_norm_upper_half"],
          "B":res["B_out_of_range"] and res["B_cos_below_median"],
          "C":res["C_colorfulness_up"] and res["C_contrast_up"] and res["C_colorfulness_top5"],
          "D":res["D_hf_up"] and res["D_hf_top8"] and res["D_closer_to_B_than_A"]}
    out.append((q,hits,res))
print(f"{'prompt':16s} A B C D   dettagli")
tot=collections.Counter()
for q,h,res in out:
    print(f"{q:16s} {'H' if h['A'] else '.'} {'H' if h['B'] else '.'} {'H' if h['C'] else '.'} {'H' if h['D'] else '.'}   "
          + " ".join(f"{k}={int(v)}" for k,v in res.items()))
    for k,v in h.items():
        if v: tot[k]+=1
print()
print("colpi su S1_photo (i 4):", {k:int(v) for k,v in out[0][1].items()})
print("colpi sui 7 prompt mai visti, per predizione:", {k:tot[k]-int(out[0][1][k]) for k in "ABCD"}, " su 7 ciascuna")

with open(os.path.join(R,"observer_prediction_scores.csv"),"w",newline="",encoding="utf-8") as fh:
    keys=["prompt","seen_by_observer","hit_A","hit_B","hit_C","hit_D"]+list(out[0][2].keys())
    w=csv.DictWriter(fh,fieldnames=keys); w.writeheader()
    for q,h,res in out:
        row={"prompt":q,"seen_by_observer":int(q=="S1_photo")}
        row.update({f"hit_{k}":int(v) for k,v in h.items()})
        row.update({k:int(v) for k,v in res.items()})
        w.writerow(row)
print("scritto data/observer_prediction_scores.csv")
