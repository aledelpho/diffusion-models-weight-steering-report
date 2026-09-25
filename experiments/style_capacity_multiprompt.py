# -*- coding: utf-8 -*-
"""
experiments/style_capacity_multiprompt.py
=========================================
Capacity of the tuner on the eight-prompt atlas corpus.

Governed by docs/prereg_style_capacity.md and its amendment 01, both committed before any
feature of this corpus was extracted. The single-prompt script experiments/style_capacity.py is
left untouched as the record of what was frozen first; it stops itself on a multi-prompt plan.

Frozen here:
  - Delta is paired by (prompt, seed) against the baseline of the same prompt and seed.
  - Scale = pooled within-(preset, prompt) sd of Delta across seeds, over all 208 cells.
  - Null = permutation WITHIN each prompt of that prompt's 78 vectors among its 26 presets,
    10000 draws, random.Random(1337); tau = 95th percentile of the MAXIMUM pairwise distance.
  - K_common (PRIMARY) = components of the consensus graph, two presets joined when they are
    indistinguishable in at least 5 of the 8 prompts. K_median and K_pooled are secondary.
  - Q1 region contrast, Q2 Spearman, and a secondary leave-one-prompt-out identification.
No new render. Nothing here changes an existing claim.
"""

from __future__ import annotations

import csv
import math
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PLANS = ["perturbation_atlas_phase1_plan.csv", "perturbation_atlas_phase2_plan.csv"]
FEATS = DATA / "style_features_atlas_phase1.csv"

FEATURES_23 = [
    "stroke_width_median_px", "stroke_width_std_px", "stroke_width_cv", "edge_density",
    "contour_mean_length_px", "contour_n_components", "crosshatch_entropy_mean",
    "crosshatch_entropy_p90", "color_top4_cluster_share", "color_cluster_entropy_norm",
    "color_n_effective", "colorfulness_hs", "luminance_hist_n_peaks",
    "shadow_edge_transition_width_px", "shadow_edge_transition_width_std", "glcm_contrast",
    "glcm_homogeneity", "glcm_energy", "glcm_correlation", "lbp_entropy",
    "lbp_uniform_share", "fft_radial_slope", "fft_high_freq_share",
]
COLOUR = ["color_top4_cluster_share", "color_cluster_entropy_norm", "color_n_effective", "colorfulness_hs"]
FEATURES_19 = [f for f in FEATURES_23 if f not in COLOUR]

N_PERM = 10000
N_PERM_ID = 1000
SEED = 1337
MAJORITY = 5          # of 8 prompts, frozen in amendment 01 section 3


def die(msg):
    sys.exit(f"ABORT (pre-registration): {msg}")


def load(cols):
    if not FEATS.exists():
        die(f"{FEATS.name} does not exist. Extract it with experiments/style_features.py first.")
    feats = {os.path.basename(r["file"]): r for r in csv.DictReader(FEATS.open(encoding="utf-8"))}
    base, pert = defaultdict(dict), defaultdict(dict)
    seen_missing = []
    for pl in PLANS:
        path = DATA / pl
        if not path.exists():
            die(f"missing plan {pl}")
        for r in csv.DictReader(path.open(encoding="utf-8")):
            if r["type"] == "determinism_check":
                continue
            fn = os.path.basename(r["expected_filename"])
            row = feats.get(fn)
            if row is None:
                seen_missing.append(fn)
                continue
            v = np.array([float(row[c]) for c in cols])
            if r["type"] == "baseline":
                base[r["prompt_id"]][r["seed"]] = v
            else:
                pert[(r["condition"], r["draw"])][(r["prompt_id"], r["seed"])] = v
    if seen_missing:
        die(f"{len(seen_missing)} planned images have no features, e.g. {seen_missing[:3]}")

    prompts = sorted(base)
    seeds = sorted({s for d in base.values() for s in d})
    presets = sorted(pert)
    cells = [(q, s) for q in prompts for s in seeds]
    for p in presets:
        miss = [c for c in cells if c not in pert[p]]
        if miss:
            die(f"preset {p} is missing {len(miss)} (prompt, seed) cells")
    D = np.stack([[pert[p][(q, s)] - base[q][s] for (q, s) in cells] for p in presets])
    return presets, prompts, seeds, cells, D          # D: (P, Q*S, F)


def scale(D, nQ, nS):
    P, _, F = D.shape
    X = D.reshape(P, nQ, nS, F)
    sd = np.sqrt(np.mean(X.var(axis=2, ddof=1).reshape(-1, F), axis=0))
    return np.where(sd > 0, sd, 1.0)


def pdist(C, metric):
    n = C.shape[0]
    ia, ib = np.triu_indices(n, k=1)
    if metric == "euclidean":
        return np.linalg.norm(C[ia] - C[ib], axis=1), ia, ib
    nr = np.linalg.norm(C, axis=1, keepdims=True)
    U = C / np.where(nr > 0, nr, 1.0)
    return 1.0 - np.sum(U[ia] * U[ib], axis=1), ia, ib


def components(n, ia, ib, dis):
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for k in range(len(ia)):
        if not dis[k]:
            a, b = find(int(ia[k])), find(int(ib[k]))
            if a != b:
                par[a] = b
    roots, lab = {}, []
    for i in range(n):
        lab.append(roots.setdefault(find(i), len(roots)))
    return lab, len(roots)


def spearman(x, y):
    def rank(v):
        o = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), float)
        r[o] = np.arange(len(v), dtype=float)
        s = np.asarray(v, float)[o]
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and s[j + 1] == s[i]:
                j += 1
            if j > i:
                r[o[i:j + 1]] = r[o[i:j + 1]].mean()
            i = j + 1
        return r
    rx, ry = rank(x) - rank(x).mean(), rank(y) - rank(y).mean()
    den = math.sqrt(float((rx ** 2).sum() * (ry ** 2).sum()))
    return float((rx * ry).sum() / den) if den else float("nan")


def tau_per_prompt(Xq, metric, rng):
    """Xq: (P, S, F) for one prompt. Permute its P*S vectors among the P presets."""
    P, S, F = Xq.shape
    flat = Xq.reshape(P * S, F)
    order = list(range(P * S))
    mx = np.empty(N_PERM)
    for t in range(N_PERM):
        rng.shuffle(order)
        C = flat[np.asarray(order)].reshape(P, S, F).mean(axis=1)
        d, _, _ = pdist(C, metric)
        mx[t] = d.max()
    return float(np.percentile(mx, 95))


def tau_pooled(X, metric, rng):
    """X: (P, Q, S, F). Permute within each prompt, then pool across prompts."""
    P, Q, S, F = X.shape
    orders = [list(range(P * S)) for _ in range(Q)]
    mx = np.empty(N_PERM)
    for t in range(N_PERM):
        acc = np.zeros((P, F))
        for q in range(Q):
            rng.shuffle(orders[q])
            acc += X[:, q].reshape(P * S, F)[np.asarray(orders[q])].reshape(P, S, F).mean(axis=1)
        d, _, _ = pdist(acc / Q, metric)
        mx[t] = d.max()
    return float(np.percentile(mx, 95))


def lopo_identify(X, presets, prompts):
    """Nearest centroid by cosine, one whole prompt held out per fold. P classes.

    labels[i, q, k] is the class of row i in cell (prompt q, seed k); under the null it is a
    permutation drawn independently per cell. inv[q, k, c] is the row carrying class c there.
    """
    P, Q, S, F = X.shape
    Kidx = np.arange(S)[None, :, None]

    def run(inv):
        correct = 0
        per = np.zeros(P)
        for q in range(Q):
            tr = np.array([j for j in range(Q) if j != q])
            Jidx = tr[:, None, None]
            vals = X[inv[tr], Jidx, Kidx]                 # (Q-1, S, P, F)
            cen = vals.mean(axis=(0, 1))                  # (P, F)
            nr = np.linalg.norm(cen, axis=1, keepdims=True)
            cn = cen / np.where(nr > 0, nr, 1.0)
            Xq = X[:, q]                                  # (P, S, F)
            nx = np.linalg.norm(Xq, axis=2, keepdims=True)
            Un = Xq / np.where(nx > 0, nx, 1.0)
            pred = np.argmax(Un @ cn.T, axis=2)           # (P, S)
            true = np.empty((P, S), int)
            for k in range(S):
                true[inv[q, k], k] = np.arange(P)
            hit = pred == true
            correct += int(hit.sum())
            for c in range(P):
                per[c] += int(hit[true == c].sum())
        return correct / (P * Q * S), per / (Q * S)

    inv = np.repeat(np.arange(P)[None, None, :], Q, axis=0).repeat(S, axis=1)   # (Q, S, P)
    acc, per = run(inv)
    rng = random.Random(SEED)
    ge = 0
    for _ in range(N_PERM_ID):
        pinv = np.empty_like(inv)
        for q in range(Q):
            for k in range(S):
                pm = list(range(P))
                rng.shuffle(pm)
                pinv[q, k] = np.asarray(pm)
        a, _ = run(pinv)
        if a >= acc:
            ge += 1
    return acc, (1 + ge) / (1 + N_PERM_ID), per


def main():
    tests, pairs, graph = [], [], []
    for cols, rep in ((FEATURES_23, "features_23"), (FEATURES_19, "features_19_texture")):
        presets, prompts, seeds, cells, D = load(cols)
        P, Q, S, F = len(presets), len(prompts), len(seeds), len(cols)
        sd = scale(D, Q, S)
        X = (D / sd).reshape(P, Q, S, F)
        region = np.array([p[0] for p in presets])
        print(f"  [{rep}] {P} presets x {Q} prompts x {S} seeds, {F} features")

        for metric in ("euclidean", "cosine"):
            per_prompt_dis, Kq, Rq, rhoq, taus = [], [], [], [], []
            for q in range(Q):
                Cq = X[:, q].mean(axis=1)
                d, ia, ib = pdist(Cq, metric)
                tau = tau_per_prompt(X[:, q], metric, random.Random(SEED))
                dis = d > tau
                _, k = components(P, ia, ib, dis)
                per_prompt_dis.append(dis)
                Kq.append(k)
                taus.append(tau)
                same = region[ia] == region[ib]
                Rq.append(float(d[~same].mean() - d[same].mean()))
                dist = np.array([d[(ia == i) | (ib == i)].mean() for i in range(P)])
                rhoq.append(spearman(dist, np.linalg.norm(Cq, axis=1)))
                for kk in range(len(d)):
                    pairs.append(dict(representation=rep, geometry=metric, prompt=prompts[q],
                                      preset_a=f"{presets[ia[kk]][0]}_d{presets[ia[kk]][1]}",
                                      preset_b=f"{presets[ib[kk]][0]}_d{presets[ib[kk]][1]}",
                                      same_region=int(region[ia[kk]] == region[ib[kk]]),
                                      distance=round(float(d[kk]), 6), above_tau=int(dis[kk])))

            M = np.vstack(per_prompt_dis)                       # (Q, 325)
            n_dis = M.sum(axis=0)
            consensus = n_dis >= MAJORITY
            d0, ia, ib = pdist(X[:, 0].mean(axis=1), metric)     # indices only
            lab_c, K_common = components(P, ia, ib, consensus)

            Cp = X.mean(axis=(1, 2))
            dp, _, _ = pdist(Cp, metric)
            taup = tau_pooled(X, metric, random.Random(SEED))
            _, K_pooled = components(P, ia, ib, dp > taup)

            # Q1 null: relabel regions over presets, one relabelling for all prompts
            same0 = region[ia] == region[ib]
            R_obs = float(np.mean(Rq))
            rng = random.Random(SEED)
            order = list(range(P))
            ge = 0
            all_d = np.stack([pdist(X[:, q].mean(axis=1), metric)[0] for q in range(Q)])
            for _ in range(N_PERM):
                rng.shuffle(order)
                rg = region[np.asarray(order)]
                sm = rg[ia] == rg[ib]
                r = float(np.mean([all_d[q][~sm].mean() - all_d[q][sm].mean() for q in range(Q)]))
                if r >= R_obs:
                    ge += 1
            pR = (1 + ge) / (1 + N_PERM)

            tests.append(dict(representation=rep, geometry=metric, n_presets=P, n_prompts=Q,
                              K_common=K_common, K_median=float(np.median(Kq)),
                              K_pooled=K_pooled, K_per_prompt=" ".join(map(str, Kq)),
                              tau_mean=float(np.mean(taus)), tau_pooled=taup,
                              pairs_above_tau_median=float(np.median(M.sum(axis=1))),
                              consensus_pairs_distinguishable=int(consensus.sum()),
                              region_contrast_R=R_obs, region_perm_p=pR,
                              spearman_median=float(np.median(rhoq))))
            for i in range(P):
                graph.append(dict(representation=rep, geometry=metric,
                                  preset=f"{presets[i][0]}_d{presets[i][1]}",
                                  region=presets[i][0], draw=presets[i][1],
                                  component_consensus=lab_c[i],
                                  delta_norm=round(float(np.linalg.norm(Cp[i])), 6)))

        if rep == "features_23":
            acc, p_id, per = lopo_identify(X, presets, prompts)
            tests.append(dict(representation=rep, geometry="lopo_identification", n_presets=P,
                              n_prompts=Q, K_common="", K_median="", K_pooled="",
                              K_per_prompt="", tau_mean="", tau_pooled="",
                              pairs_above_tau_median="", consensus_pairs_distinguishable="",
                              region_contrast_R="", region_perm_p="", spearman_median="",
                              lopo_accuracy=acc, lopo_chance=1.0 / P, lopo_perm_p=p_id,
                              lopo_min_recall=float(per.min()), lopo_max_recall=float(per.max())))
            for i in range(P):
                graph.append(dict(representation=rep, geometry="lopo_identification",
                                  preset=f"{presets[i][0]}_d{presets[i][1]}",
                                  region=presets[i][0], draw=presets[i][1],
                                  component_consensus="", delta_norm=round(float(per[i]), 6)))

    keys = sorted({k for t in tests for k in t})
    order_k = ["representation", "geometry", "n_presets", "n_prompts", "K_common", "K_median",
               "K_pooled", "K_per_prompt", "consensus_pairs_distinguishable", "tau_mean",
               "tau_pooled", "pairs_above_tau_median", "region_contrast_R", "region_perm_p",
               "spearman_median"] + [k for k in keys if k.startswith("lopo")]
    order_k += [k for k in keys if k not in order_k]
    for name, rows, ks in (("style_capacity_tests.csv", tests, order_k),
                           ("style_capacity_pairs.csv", pairs, list(pairs[0].keys())),
                           ("style_capacity_graph.csv", graph, list(graph[0].keys()))):
        with (DATA / name).open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=ks)
            w.writeheader()
            for r in rows:
                w.writerow({k: (round(r[k], 6) if isinstance(r.get(k), float) else r.get(k, "")) for k in ks})
    for t in tests:
        print("  ", {k: v for k, v in t.items() if v != ""})


if __name__ == "__main__":
    main()
