# -*- coding: utf-8 -*-
"""
experiments/style_axis_tradeoff.py
==================================
Does an edit push a scene further into its own style, or out of it, and does the sign differ
between scenes within one preset?

Governed by docs/prereg_style_axis_tradeoff.md, committed before this file was written.

Frozen there:
  - u_s = z(baseline of s) - mean over the eight scenes, in the same scaled space as Delta.
  - PRIMARY is the split-seed version: the axis from one seed, the displacement from the other
    two, averaged over the three choices, so that axis and displacement share no image. The
    naive all-three-seeds version is a cross-check; a disagreement in sign is inconclusive.
  - Null: all 8! = 40320 permutations of the axes among the scenes, enumerated exactly.
    Floor 1/40320 = 2.48e-05.
  - M = mean matched cosine (two-sided). T = mean over presets of min(k, 8-k), k = scenes with
    positive cosine. Only T outside the null supports a trade-off.
No new render.
"""

from __future__ import annotations

import csv
import itertools
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style_capacity_multiprompt as M  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def cos_rows(A, B):
    na = np.linalg.norm(A, axis=-1, keepdims=True)
    nb = np.linalg.norm(B, axis=-1, keepdims=True)
    A = A / np.where(na > 0, na, 1.0)
    B = B / np.where(nb > 0, nb, 1.0)
    return A @ B.T


def build():
    feats = {os.path.basename(r["file"]): r
             for r in csv.DictReader((DATA / "style_features_atlas_phase1.csv").open(encoding="utf-8"))}
    base, pert = {}, {}
    for pl in M.PLANS:
        for r in csv.DictReader((DATA / pl).open(encoding="utf-8")):
            if r["type"] == "determinism_check":
                continue
            v = np.array([float(feats[os.path.basename(r["expected_filename"])][c])
                          for c in M.FEATURES_23])
            if r["type"] == "baseline":
                base[(r["prompt_id"], r["seed"])] = v
            else:
                pert[((r["condition"], r["draw"]), r["prompt_id"], r["seed"])] = v
    prompts = sorted({k[0] for k in base})
    seeds = sorted({k[1] for k in base})
    presets = sorted({k[0] for k in pert})
    D = np.stack([[[pert[(p, q, s)] - base[(q, s)] for s in seeds] for q in prompts] for p in presets])
    live = [i for i in range(len(presets)) if np.any(D[i])]
    dropped = [presets[i] for i in range(len(presets)) if i not in live]
    presets = [presets[i] for i in live]
    D = D[live]
    B = np.stack([[base[(q, s)] for s in seeds] for q in prompts])          # (Q,S,F)
    sd = np.sqrt(np.mean(D.var(axis=2, ddof=1).reshape(-1, len(M.FEATURES_23)), axis=0))
    sd = np.where(sd > 0, sd, 1.0)
    return presets, prompts, seeds, D / sd, B / sd, dropped


def cmatrix(D, B, split):
    """C[p, s, s'] = cos(Delta(p,s), u_s'). split=True -> axis and displacement on disjoint seeds."""
    P, Q, S, F = D.shape
    if not split:
        u = B.mean(axis=1)
        u = u - u.mean(axis=0, keepdims=True)
        d = D.mean(axis=2)
        return np.stack([cos_rows(d[p], u) for p in range(P)])
    acc = np.zeros((P, Q, Q))
    for a in range(S):
        rest = [k for k in range(S) if k != a]
        u = B[:, a, :]
        u = u - u.mean(axis=0, keepdims=True)
        d = D[:, :, rest, :].mean(axis=2)
        acc += np.stack([cos_rows(d[p], u) for p in range(P)])
    return acc / S


def stats(C, perm):
    v = C[:, np.arange(C.shape[1]), perm]          # (P, Q)
    k = (v > 0).sum(axis=1)
    return float(v.mean()), float(np.minimum(k, C.shape[1] - k).mean())


def main():
    presets, prompts, seeds, D, B, dropped = build()
    P, Q = len(presets), len(prompts)
    print(f"  {P} presets x {Q} scenes x {len(seeds)} seeds   (excluded as inert: {dropped})")

    out_rows, tests = [], []
    res = {}
    for split, tag in ((True, "split_seed_primary"), (False, "naive_cross_check")):
        C = cmatrix(D, B, split)
        ident = np.arange(Q)
        M_obs, T_obs = stats(C, ident)
        Ms, Ts = [], []
        for perm in itertools.permutations(range(Q)):
            m, t = stats(C, np.asarray(perm))
            Ms.append(m); Ts.append(t)
        Ms, Ts = np.asarray(Ms), np.asarray(Ts)
        n = len(Ms)
        pM = float((np.abs(Ms) >= abs(M_obs)).sum()) / n
        pT_hi = float((Ts >= T_obs).sum()) / n
        pT_lo = float((Ts <= T_obs).sum()) / n
        per_scene = C[:, ident, ident].mean(axis=0)
        res[tag] = dict(M=M_obs, T=T_obs, pM=pM, pT=2 * min(pT_hi, pT_lo),
                        null_M_mean=float(Ms.mean()), null_T_mean=float(Ts.mean()),
                        null_M_p2_5=float(np.percentile(Ms, 2.5)),
                        null_M_p97_5=float(np.percentile(Ms, 97.5)),
                        null_T_p2_5=float(np.percentile(Ts, 2.5)),
                        null_T_p97_5=float(np.percentile(Ts, 97.5)),
                        per_scene={prompts[s]: float(per_scene[s]) for s in range(Q)},
                        n_perm=n)
        if split:
            for p in range(P):
                for s in range(Q):
                    out_rows.append(dict(preset=f"{presets[p][0]}_d{presets[p][1]}",
                                         region=presets[p][0], draw=presets[p][1],
                                         scene=prompts[s],
                                         cos_split_seed=round(float(C[p, s, s]), 6)))
    Cn = cmatrix(D, B, False)
    for r in out_rows:
        p = [f"{x[0]}_d{x[1]}" for x in presets].index(r["preset"])
        s = prompts.index(r["scene"])
        r["cos_naive"] = round(float(Cn[p, s, s]), 6)
        r["sign_split"] = int(np.sign(r["cos_split_seed"]))

    a, b = res["split_seed_primary"], res["naive_cross_check"]
    agree = np.sign(a["M"]) == np.sign(b["M"])
    if not agree:
        verdict = "inconclusive_split_and_naive_disagree_in_sign"
    elif a["pT"] < 0.05:
        verdict = "trade_off"
    elif a["pM"] < 0.05 and a["M"] < 0:
        verdict = "contractive_not_selective"
    elif a["pM"] < 0.05 and a["M"] > 0:
        verdict = "selective_gain_requires_replication"
    else:
        verdict = "no_signal"

    for tag, r in res.items():
        tests.append(dict(version=tag, M=r["M"], p_M_exact=r["pM"], T=r["T"], p_T_exact=r["pT"],
                          null_M_mean=r["null_M_mean"], null_M_ci=f"[{r['null_M_p2_5']:.4f}, {r['null_M_p97_5']:.4f}]",
                          null_T_mean=r["null_T_mean"], null_T_ci=f"[{r['null_T_p2_5']:.3f}, {r['null_T_p97_5']:.3f}]",
                          n_permutations=r["n_perm"], n_presets=P, n_scenes=Q,
                          verdict=verdict if tag == "split_seed_primary" else "cross_check",
                          **{f"scene_{k}": round(v, 6) for k, v in r["per_scene"].items()}))

    with (DATA / "style_axis_projection.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys())); w.writeheader(); w.writerows(out_rows)
    with (DATA / "style_axis_tests.csv").open("w", newline="", encoding="utf-8") as fh:
        keys = list(tests[0].keys())
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader()
        for t in tests:
            w.writerow({k: (round(t[k], 6) if isinstance(t[k], float) else t[k]) for k in keys})
    for t in tests:
        print("  ", {k: v for k, v in t.items() if not k.startswith("scene_")})
    print("  per scena (primaria):", {k: round(v, 4) for k, v in res["split_seed_primary"]["per_scene"].items()})
    print("  VERDETTO:", verdict)


if __name__ == "__main__":
    main()
