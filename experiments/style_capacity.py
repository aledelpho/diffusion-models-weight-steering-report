# -*- coding: utf-8 -*-
"""
experiments/style_capacity.py
=============================
How many mutually distinguishable styles does the tuner produce at one displacement?

Governed by docs/prereg_style_capacity.md, written and committed 2026-09-25 while the Phase 1
render queue stood at 52 %. THIS SCRIPT WAS WRITTEN BEFORE ITS DATA EXISTED. It is committed
unrun on purpose: nothing in it can have been tuned to a number.

Constraints carried from the pre-registration:
  - K = connected components of the graph whose edges join pairs that are NOT distinguishable.
    Conservative by construction: everything we cannot tell apart is merged.
  - tau = 95th percentile of the null distribution of the MAXIMUM pairwise distance, over
    10000 permutations of the 78 displacement vectors across the 26 presets, random.Random(1337).
    The max-statistic carries the family of 325 pairs; no Holm is applied on top.
  - Two geometries, both primary: Euclidean (how much) and cosine (what).
  - Scale = pooled within-preset standard deviation of the displacement across seeds.
  - The quantity is named capacity on ONE SCENE. Phase 1 renders a single prompt.
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
PLAN = DATA / "perturbation_atlas_phase1_plan.csv"
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
SEED = 1337


def die(msg):
    sys.exit(f"ABORT (pre-registration): {msg}")


def load():
    if not PLAN.exists():
        die(f"missing {PLAN.name}")
    if not FEATS.exists():
        die(
            f"{FEATS.name} does not exist yet. Phase 1 has not been measured.\n"
            f"  Produce it with:\n"
            f"    python experiments/style_features.py --dir <phase1 renders> "
            f"--out data/style_features_atlas_phase1.csv\n"
            f"  This script does not render and does not extract. It only analyses."
        )
    plan = list(csv.DictReader(PLAN.open(encoding="utf-8")))
    feats = {os.path.basename(r["file"]): r for r in csv.DictReader(FEATS.open(encoding="utf-8"))}

    # GUARD, added 2026-09-25 before any data existed, after finding that the loader below
    # keys baselines by seed alone. With more than one prompt in the plan that key collides and
    # every displacement would be silently anchored to whichever prompt was read last. This is a
    # loud stop, not a statistic: nothing computed below changes.
    prompts = sorted({r.get("prompt_id", "") for r in plan})
    if len(prompts) != 1:
        die(
            f"the plan carries {len(prompts)} prompts ({prompts}). "
            "docs/prereg_style_capacity.md is written for the single-prompt Phase 1 and names its "
            "quantity 'capacity on one scene'. A multi-prompt corpus needs prompt-paired baselines, "
            "a null permuted within prompt, and leave-one-prompt-out identification: that is an "
            "amendment to the pre-registration, to be written before this script is run."
        )
    return plan, feats


def build(plan, feats, cols):
    """Delta(preset, seed) = x(preset, seed) - x(baseline, same seed), then scaled."""
    base, pert = {}, defaultdict(dict)
    missing = []
    for r in plan:
        if r["type"] == "determinism_check":
            continue
        fn = os.path.basename(r["expected_filename"])
        row = feats.get(fn)
        if row is None:
            missing.append(fn)
            continue
        v = np.array([float(row[c]) for c in cols])
        if r["type"] == "baseline":
            base[r["seed"]] = v
        else:
            pert[(r["condition"], r["draw"])][r["seed"]] = v
    seeds = sorted(base)
    if len(seeds) != 3:
        die(f"expected 3 baselines, found {len(seeds)}")
    presets, deltas, dropped = [], [], []
    for key in sorted(pert):
        got = pert[key]
        if set(got) != set(seeds):
            dropped.append((key, sorted(got)))
            continue
        presets.append(key)
        deltas.append(np.array([got[s] - base[s] for s in seeds]))   # (3, n_features)
    if not presets:
        die("no preset has all three seeds")
    D = np.stack(deltas)                                             # (P, 3, F)
    sd = np.sqrt(np.mean(D.var(axis=1, ddof=1), axis=0))             # pooled within-preset sd
    sd = np.where(sd > 0, sd, 1.0)
    return presets, D / sd, missing, dropped


def pdist_centroids(C, metric):
    n = C.shape[0]
    ia, ib = np.triu_indices(n, k=1)
    if metric == "euclidean":
        return np.linalg.norm(C[ia] - C[ib], axis=1), ia, ib
    nrm = np.linalg.norm(C, axis=1, keepdims=True)
    nrm = np.where(nrm > 0, nrm, 1.0)
    U = C / nrm
    return 1.0 - np.sum(U[ia] * U[ib], axis=1), ia, ib


def tau_maxstat(D, metric, rng):
    """Null: the 3*P displacement vectors are exchangeable across presets."""
    P = D.shape[0]
    flat = D.reshape(P * 3, D.shape[2])
    order = list(range(P * 3))
    mx = np.empty(N_PERM)
    for t in range(N_PERM):
        rng.shuffle(order)
        C = flat[np.asarray(order)].reshape(P, 3, -1).mean(axis=1)
        d, _, _ = pdist_centroids(C, metric)
        mx[t] = d.max()
    return float(np.percentile(mx, 95)), mx


def components(n, ia, ib, distinguishable):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for k in range(len(ia)):
        if not distinguishable[k]:                    # edge = indistinguishable
            a, b = find(int(ia[k])), find(int(ib[k]))
            if a != b:
                parent[a] = b
    roots = {}
    lab = []
    for i in range(n):
        r = find(i)
        lab.append(roots.setdefault(r, len(roots)))
    return lab, len(roots)


def spearman(x, y):
    def rank(v):
        o = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), float)
        r[o] = np.arange(len(v), dtype=float)
        # average ties
        s = np.array(v, float)[o]
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and s[j + 1] == s[i]:
                j += 1
            if j > i:
                r[o[i:j + 1]] = np.mean(r[o[i:j + 1]])
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    rx -= rx.mean(); ry -= ry.mean()
    den = math.sqrt(float((rx ** 2).sum() * (ry ** 2).sum()))
    return float((rx * ry).sum() / den) if den else float("nan")


def region_contrast(d, ia, ib, presets, rng):
    """Q1: between-region distance minus within-region (draw 1 vs draw 2 of one region)."""
    region = np.array([p[0] for p in presets])
    same = region[ia] == region[ib]
    if same.sum() == 0:
        return float("nan"), float("nan"), 0
    obs = float(d[~same].mean() - d[same].mean())
    n = len(presets)
    order = list(range(n))
    pos = {(int(a), int(b)): k for k, (a, b) in enumerate(zip(ia, ib))}
    ge = 0
    for _ in range(N_PERM):
        rng.shuffle(order)
        idx = []
        for k in range(0, n - 1, 2):
            a, b = sorted((order[k], order[k + 1]))
            idx.append(pos[(a, b)])
        m = np.zeros(len(d), bool)
        m[idx] = True
        if float(d[~m].mean() - d[m].mean()) >= obs:
            ge += 1
    return obs, (1 + ge) / (1 + N_PERM), int(same.sum())


def main():
    plan, feats = load()
    tests, pairs, graph = [], [], []
    for cols, rep in ((FEATURES_23, "features_23"), (FEATURES_19, "features_19_texture")):
        presets, D, missing, dropped = build(plan, feats, cols)
        if missing:
            print(f"  images in the plan with no features: {len(missing)}")
        if dropped:
            print(f"  presets dropped for an incomplete seed set: {dropped}")
        C = D.mean(axis=1)
        mag = np.linalg.norm(C, axis=1)
        for metric in ("euclidean", "cosine"):
            d, ia, ib = pdist_centroids(C, metric)
            tau, null = tau_maxstat(D, metric, random.Random(SEED))
            dis = d > tau
            lab, K = components(len(presets), ia, ib, dis)
            R, pR, n_within = region_contrast(d, ia, ib, presets, random.Random(SEED))
            distinct = np.array([d[(ia == i) | (ib == i)].mean() for i in range(len(presets))])
            rho = spearman(distinct, mag)
            tests.append(dict(representation=rep, geometry=metric, n_presets=len(presets),
                              n_pairs=len(d), tau=tau, observed_max=float(d.max()),
                              n_pairs_above_tau=int(dis.sum()), K=K,
                              region_contrast_R=R, region_perm_p=pR, n_within_region_pairs=n_within,
                              spearman_distinctiveness_vs_magnitude=rho,
                              null_max_mean=float(null.mean())))
            for k in range(len(d)):
                pairs.append(dict(representation=rep, geometry=metric,
                                  preset_a=f"{presets[ia[k]][0]}_draw{presets[ia[k]][1]}",
                                  preset_b=f"{presets[ib[k]][0]}_draw{presets[ib[k]][1]}",
                                  same_region=int(presets[ia[k]][0] == presets[ib[k]][0]),
                                  distance=round(float(d[k]), 6), above_tau=int(dis[k])))
            for i, p in enumerate(presets):
                graph.append(dict(representation=rep, geometry=metric,
                                  preset=f"{p[0]}_draw{p[1]}", region=p[0], draw=p[1],
                                  component=lab[i], distinctiveness=round(float(distinct[i]), 6),
                                  delta_norm=round(float(mag[i]), 6)))

    for name, rows in (("style_capacity_tests.csv", tests),
                       ("style_capacity_pairs.csv", pairs),
                       ("style_capacity_graph.csv", graph)):
        with (DATA / name).open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
    for t in tests:
        print("  ", t)
    print("\n  K is CAPACITY ON ONE SCENE. Phase 1 renders a single prompt (S1_photo).")


if __name__ == "__main__":
    main()
