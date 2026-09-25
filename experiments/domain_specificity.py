# -*- coding: utf-8 -*-
"""
experiments/domain_specificity.py
=================================
Does the calibrated preset lose more of its direction than a norm-matched random edit when
the style-domain boundary is crossed, while losing less inside a domain?

Governed by docs/prereg_domain_specificity.md (2026-09-25), whose section 0 states that the
pattern was seen before the test was written: the p-value here is not a discovery p-value.

Constraints carried from the pre-registration:
  - Families B (16 comics prompts) and C (8 style prompts) only; A1 and A2 excluded because
    they carry a different suite_git_sha.
  - Standardisation from the baselines of THESE 24 prompts only; the 48-prompt
    standardisation is carried as a sign cross-check.
  - Null: the preset/rand label is exchangeable within each prompt (sign-flip over 24
    prompts), 20000 draws, random.Random(1337). The prompt is the unit.
  - Holm over the two arm contrasts. No new render.
"""

from __future__ import annotations

import csv
import itertools
import math
import random
from pathlib import Path

import numpy as np

import family_coherence as fc

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

FAM_B = fc.FAM_B
FAM_C = fc.FAM_C
PROMPTS = FAM_B + FAM_C
DOMAIN = {p: ("B" if p in FAM_B else "C") for p in PROMPTS}
ARMS = ["preset_pos", "rand_pos", "blockshuf_neg"]
N_PERM = 20000
PERM_SEED = 1337


def z_rows(rows, base_prompts):
    base = np.array([r["vec"] for r in rows
                     if r["arm"] == "baseline" and r["prompt"] in base_prompts], dtype=float)
    mu, sd = base.mean(axis=0), base.std(axis=0, ddof=1)
    sd = np.where(sd > 0, sd, 1.0)
    out = {}
    for r in rows:
        out[(r["prompt"], r["arm"], r["seed"])] = (np.array(r["vec"], dtype=float) - mu) / sd
    return out, base.shape[0]


def deltas(z, cols, prompts, arms):
    idx = [fc.FEATURES_23.index(c) for c in cols]
    d = {}
    for p in prompts:
        for a in arms:
            if all((p, a, s) in z and (p, "baseline", s) in z for s in fc.SEEDS_5):
                d[(p, a)] = np.mean([z[(p, a, s)][idx] - z[(p, "baseline", s)][idx]
                                     for s in fc.SEEDS_5], axis=0)
    return d


def split_half_rel(z, cols, prompts, arm):
    idx = [fc.FEATURES_23.index(c) for c in cols]
    vals = []
    for p in prompts:
        if not all((p, arm, s) in z for s in fc.SEEDS_5):
            continue
        for half in itertools.combinations(fc.SEEDS_5, 2):
            other = [s for s in fc.SEEDS_5 if s not in half]
            v1 = np.mean([z[(p, arm, s)][idx] - z[(p, "baseline", s)][idx] for s in half], axis=0)
            v2 = np.mean([z[(p, arm, s)][idx] - z[(p, "baseline", s)][idx] for s in other], axis=0)
            vals.append(fc.cosine(v1, v2))
    return float(np.mean(vals)) if vals else float("nan")


def cosmat(A, B):
    n = len(A)
    M = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            M[i, j] = fc.cosine(A[i], B[j])
    return M


def summarise(M, dom, ia, ib):
    """W_B, W_C, W, X, D from a cosine matrix over the ordered prompt list."""
    same = dom[ia] == dom[ib]
    both_b = same & (dom[ia] == "B")
    both_c = same & (dom[ia] == "C")
    c = M[ia, ib]
    wB = float(c[both_b].mean())
    wC = float(c[both_c].mean())
    w = float(c[same].mean())
    x = float(c[~same].mean())
    return wB, wC, w, x, w - x, int(both_b.sum()), int(both_c.sum()), int((~same).sum())


def run_block(z, cols, prompts, tag_rep, tag_std, pairs_sink):
    d = deltas(z, cols, prompts, ARMS)
    keep = [p for p in prompts if all((p, a) in d for a in ARMS)]
    n = len(keep)
    dom = np.array([DOMAIN[p] for p in keep])
    ia, ib = np.triu_indices(n, k=1)
    V = {a: [d[(p, a)] for p in keep] for a in ARMS}
    M = {a: cosmat(V[a], V[a]) for a in ARMS}

    rows = []
    for a in ARMS:
        wB, wC, w, x, D, nB, nC, nX = summarise(M[a], dom, ia, ib)
        rows.append(dict(arm=a, W_B=wB, W_C=wC, W=w, X=x, D=D,
                         n_pairs_BB=nB, n_pairs_CC=nC, n_pairs_BC=nX))
        if tag_rep == "features_23" and tag_std == "std_24_prompts":
            for k in range(len(ia)):
                i, j = int(ia[k]), int(ib[k])
                pairs_sink.append(dict(arm=a, prompt_a=keep[i], prompt_b=keep[j],
                                       domain_a=dom[i], domain_b=dom[j],
                                       same_domain=int(dom[i] == dom[j]),
                                       cosine=round(float(M[a][i, j]), 6)))

    # cross-arm cosine blocks, needed by the within-prompt label-swap null
    def contrast(arm_test):
        blocks = {(0, 0): cosmat(V[arm_test], V[arm_test]),
                  (0, 1): cosmat(V[arm_test], V["rand_pos"]),
                  (1, 0): cosmat(V["rand_pos"], V[arm_test]),
                  (1, 1): cosmat(V["rand_pos"], V["rand_pos"])}
        S = np.stack([blocks[(0, 0)], blocks[(0, 1)], blocks[(1, 0)], blocks[(1, 1)]])

        def delta_for(f):
            selA = f[ia] * 2 + f[ib]
            selB = (1 - f[ia]) * 2 + (1 - f[ib])
            cA = S[selA, ia, ib]
            cB = S[selB, ia, ib]
            same = dom[ia] == dom[ib]
            dA = cA[same].mean() - cA[~same].mean()
            dB = cB[same].mean() - cB[~same].mean()
            return float(dA - dB)

        obs = delta_for(np.zeros(n, dtype=int))
        rng = random.Random(PERM_SEED)
        ge = 0
        for _ in range(N_PERM):
            f = np.array([rng.randint(0, 1) for _ in range(n)], dtype=int)
            if delta_for(f) >= obs:
                ge += 1
        return obs, (1 + ge) / (1 + N_PERM)

    d_preset, p_preset = contrast("preset_pos")
    d_block, p_block = contrast("blockshuf_neg")
    holm = fc.holm([p_preset, p_block])

    rel = {a: {fam: split_half_rel(z, cols, [p for p in keep if DOMAIN[p] == fam], a)
               for fam in ("B", "C")} for a in ARMS}

    for r in rows:
        r.update(representation=tag_rep, standardisation=tag_std, n_prompts=n,
                 rel_B=rel[r["arm"]]["B"], rel_C=rel[r["arm"]]["C"])
    by = {r["arm"]: r for r in rows}
    rows[0].update(delta_vs_rand=d_preset, perm_p=p_preset, holm_p=holm[0])
    by["blockshuf_neg"].update(delta_vs_rand=d_block, perm_p=p_block, holm_p=holm[1])
    return rows, by, d_preset, p_preset, holm[0], d_block, holm[1], rel


def verdict(by, d_preset, holm_preset, d_block, holm_block, rel, signs_agree):
    pp, rp = by["preset_pos"], by["rand_pos"]
    if d_preset <= 0:
        return "refuted_no_extra_loss"
    if pp["X"] >= rp["X"] or pp["W"] <= rp["W"]:
        return "refuted_no_crossover"
    if rel["preset_pos"]["C"] < 0.50:
        return "inconclusive_instrument"
    if not signs_agree:
        return "inconclusive_representation"
    if holm_preset >= 0.05:
        return "not_significant"
    if d_block >= 0.5 * d_preset and holm_block < 0.05:
        return "holds_provisionally_not_specific_to_calibration"
    return "holds_provisionally"


def main():
    runs = fc.load_runs()
    rows_all = [r for r in fc.load_rows(runs) if r["prompt"] in PROMPTS]
    z24, n24 = z_rows(rows_all, set(PROMPTS))
    rows48 = fc.load_rows(runs)
    z48, n48 = z_rows(rows48, set(fc.FAMILY_OF))
    z48 = {k: v for k, v in z48.items() if k[0] in PROMPTS}
    print(f"  baseline rows: {n24} (24 prompts), {n48} (48 prompts)")

    pairs, out = [], []
    blocks = {}
    for z, tag_std in ((z24, "std_24_prompts"), (z48, "std_48_prompts")):
        for cols, tag_rep in ((fc.FEATURES_23, "features_23"), (fc.FEATURES_19, "features_19_texture")):
            r, by, dp, pp_, hp, db, hb, rel = run_block(z, cols, PROMPTS, tag_rep, tag_std, pairs)
            blocks[(tag_std, tag_rep)] = (r, by, dp, hp, db, hb, rel)
            out += r

    signs = [v[2] > 0 for v in blocks.values()]
    signs_agree = all(signs) or not any(signs)
    r, by, dp, hp, db, hb, rel = blocks[("std_24_prompts", "features_23")]
    v = verdict(by, dp, hp, db, hb, rel, signs_agree)
    print(f"  Delta(preset vs rand) = {dp:.6f}   Holm p = {hp:.6g}")
    print(f"  Delta(blockshuf vs rand) = {db:.6f}   Holm p = {hb:.6g}")
    print(f"  sign agreement across the 4 blocks: {signs_agree}  ({signs})")
    print(f"  VERDICT: {v}")
    for rr in out:
        rr["verdict_primary"] = v if (rr["standardisation"] == "std_24_prompts"
                                      and rr["representation"] == "features_23") else "cross_check"

    keys = ["standardisation", "representation", "arm", "n_prompts", "W_B", "W_C", "W", "X", "D",
            "delta_vs_rand", "perm_p", "holm_p", "rel_B", "rel_C",
            "n_pairs_BB", "n_pairs_CC", "n_pairs_BC", "verdict_primary"]
    with (DATA / "domain_specificity_tests.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for rr in out:
            w.writerow({k: (round(rr[k], 6) if isinstance(rr.get(k), float) else rr.get(k, "")) for k in keys})
    with (DATA / "domain_specificity_pairs.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pairs[0].keys()))
        w.writeheader(); w.writerows(pairs)
    print(f"  wrote {len(out)} test rows, {len(pairs)} pair rows")


if __name__ == "__main__":
    main()
