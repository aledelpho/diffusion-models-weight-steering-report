# -*- coding: utf-8 -*-
"""
experiments/shared_axis.py
==========================
Pre-registered analysis of the axis every edit shares, estimated out of sample.
Frozen in docs/prereg_shared_axis.md (2026-09-24).

Reads:
  - data/style_features_stage7.csv
  - data/style_features_stage9.csv

Writes:
  - data/shared_axis.csv
  - data/shared_axis_loadings.csv

Seed:
  RandomState is seeded at 1337 for the 200 Monte Carlo draws of the sign-randomised null.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

NOT_FEATURES = {
    "file", "width_px", "height_px", "condition", "prompt_dir",
    "prompt_sha1", "seed", "rel_path", "source_manifest"
}
BASELINE = "baseline"
RANDOM_SEED = 1337
N_NULL_DRAWS = 200
NULL_SPLIT_HALF_THRESHOLD = 0.40

STAGE7_ARMS = [
    "preset_pos", "preset_neg",
    "blockshuf_pos", "blockshuf_neg",
    "rand_pos", "rand_neg"
]

STAGE9_ARMS = [
    "preset_pos_1x", "preset_pos_2x",
    "blockshuf_neg_1x", "blockshuf_neg_2x",
    "rand_pos_1x", "rand_pos_2x"
]

STYLE_PROMPTS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]


def load_dataset(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        sys.exit(f"Required input file missing: {path}")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        sys.exit(f"Input file is empty: {path}")
    feats = [c for c in rows[0] if c not in NOT_FEATURES]
    return feats, rows


def cosine(a: list[float], b: list[float]) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if not na or not nb:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def strip_vector(v: list[float], u: list[float]) -> list[float]:
    dot = sum(x * y for x, y in zip(v, u))
    return [x - dot * y for x, y in zip(v, u)]


def split_half_s(vec_map: dict[tuple[str, str], list[float]],
                 splits: list[tuple[tuple[str, ...], tuple[str, ...]]],
                 n_feats: int) -> float:
    cos_vals: list[float] = []
    for h1, h2 in splits:
        v1 = [vec_map[k] for k in vec_map if k[0] in h1]
        v2 = [vec_map[k] for k in vec_map if k[0] in h2]
        if not v1 or not v2:
            continue
        m1 = [statistics.fmean(v[i] for v in v1) for i in range(n_feats)]
        m2 = [statistics.fmean(v[i] for v in v2) for i in range(n_feats)]
        cos_vals.append(cosine(m1, m2))
    return statistics.fmean(cos_vals) if cos_vals else 0.0


def evaluate_arm(diffs: dict[tuple[str, str], list[float]],
                 u: list[float],
                 splits: list[tuple[tuple[str, ...], tuple[str, ...]]],
                 signed_null_draws: list[dict[tuple[str, str], list[float]]],
                 n_feats: int) -> dict:
    s_val = split_half_s(diffs, splits, n_feats)
    diffs_stripped = {k: strip_vector(v, u) for k, v in diffs.items()}
    s_strip_val = split_half_s(diffs_stripped, splits, n_feats)

    shares = []
    for v in diffs.values():
        nv = math.sqrt(sum(x * x for x in v))
        dot = sum(x * y for x, y in zip(v, u))
        shares.append(abs(dot) / nv if nv > 0 else 0.0)
    share_val = statistics.fmean(shares)

    # Calculate stripped null distributions against this specific axis u
    null_stripped_s = []
    for null_map in signed_null_draws:
        stripped_map = {k: strip_vector(v, u) for k, v in null_map.items()}
        null_stripped_s.append(split_half_s(stripped_map, splits, n_feats))

    null_mean_s = statistics.fmean(null_stripped_s)
    null_p95_s = float(statistics.quantiles(null_stripped_s, n=100)[94])

    if s_strip_val > null_p95_s:
        verdict = "keeps a direction of its own"
    elif s_val > null_p95_s and s_strip_val <= null_p95_s:
        verdict = "its consistency was the shared axis"
    else:
        verdict = "no cross-scene direction either way"

    return {
        "share": share_val,
        "S": s_val,
        "S_strip": s_strip_val,
        "null_mean_stripped": null_mean_s,
        "null_p95_stripped": null_p95_s,
        "verdict": verdict,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Estimate and evaluate the shared edit axis.")
    ap.add_argument("--out", default=str(DATA / "shared_axis.csv"),
                    help="Target path for shared_axis.csv")
    ap.add_argument("--out-loadings", default=str(DATA / "shared_axis_loadings.csv"),
                    help="Target path for shared_axis_loadings.csv")
    ap.add_argument("--seed", type=int, default=RANDOM_SEED,
                    help="Random seed for Monte Carlo null draws")
    args = ap.parse_args()

    s7_path = DATA / "style_features_stage7.csv"
    s9_path = DATA / "style_features_stage9.csv"

    feats7, rows7 = load_dataset(s7_path)
    feats9, rows9 = load_dataset(s9_path)

    # 1. Feature check
    if feats7 != feats9:
        diff_7_only = set(feats7) - set(feats9)
        diff_9_only = set(feats9) - set(feats7)
        sys.exit(f"Feature set mismatch between stage7 and stage9:\n"
                 f"  In stage7 only: {diff_7_only}\n"
                 f"  In stage9 only: {diff_9_only}")
    feats = feats7
    n_feats = len(feats)
    if n_feats != 23:
        sys.exit(f"Expected exactly 23 style features, found {n_feats}: {feats}")

    # Standardise stage 7 once on its baselines
    b7 = [r for r in rows7 if r["condition"] == BASELINE]
    if not b7:
        sys.exit("No baseline rows found in stage 7 features")
    mu7 = [statistics.fmean(float(r[f]) for r in b7) for f in feats]
    sd7 = [statistics.stdev(float(r[f]) for r in b7) for f in feats]
    if any(s == 0 for s in sd7):
        sys.exit("Stage 7 has zero standard deviation in at least one feature")

    def z7(r: dict[str, str]) -> list[float]:
        return [(float(r[f]) - mu7[i]) / sd7[i] for i, f in enumerate(feats)]

    b7_map = {(r["prompt_dir"], r["seed"]): z7(r) for r in b7}

    diffs7: list[list[float]] = []
    for r in rows7:
        if r["condition"] in STAGE7_ARMS:
            k = (r["prompt_dir"], r["seed"])
            if k in b7_map:
                diffs7.append([x - y for x, y in zip(z7(r), b7_map[k])])

    if not diffs7:
        sys.exit("No paired differences found in stage 7")

    # Primary axis u: mean of stage 7 differences, unit-normalised
    u_raw7 = [statistics.fmean(d[i] for d in diffs7) for i in range(n_feats)]
    norm7 = math.sqrt(sum(x * x for x in u_raw7))
    if norm7 == 0:
        sys.exit("Stage 7 axis norm is 0")
    u_stage7 = [x / norm7 for x in u_raw7]

    # Standardise stage 9 once on style prompt baselines
    rows9_style = [r for r in rows9 if r["prompt_dir"] in STYLE_PROMPTS]
    b9 = [r for r in rows9_style if r["condition"] == BASELINE]
    if not b9:
        sys.exit("No baseline rows found for style prompts in stage 9")
    mu9 = [statistics.fmean(float(r[f]) for r in b9) for f in feats]
    sd9 = [statistics.stdev(float(r[f]) for r in b9) for f in feats]
    if any(s == 0 for s in sd9):
        sys.exit("Stage 9 has zero standard deviation in at least one feature")

    def z9(r: dict[str, str]) -> list[float]:
        return [(float(r[f]) - mu9[i]) / sd9[i] for i, f in enumerate(feats)]

    b9_map = {(r["prompt_dir"], r["seed"]): z9(r) for r in b9}

    diffs9: dict[str, dict[tuple[str, str], list[float]]] = {}
    for arm in STAGE9_ARMS:
        d_arm: dict[tuple[str, str], list[float]] = {}
        for r in rows9_style:
            if r["condition"] == arm:
                k = (r["prompt_dir"], r["seed"])
                if k in b9_map:
                    d_arm[k] = [x - y for x, y in zip(z9(r), b9_map[k])]
        if not d_arm:
            sys.exit(f"No paired differences for arm {arm} in stage 9")
        diffs9[arm] = d_arm

    # Secondary axis: leave-one-out for each stage-9 arm
    u_loo: dict[str, list[float]] = {}
    for arm in STAGE9_ARMS:
        other_diffs: list[list[float]] = []
        for other_arm in STAGE9_ARMS:
            if other_arm != arm:
                other_diffs.extend(diffs9[other_arm].values())
        raw_loo = [statistics.fmean(d[i] for d in other_diffs) for i in range(n_feats)]
        norm_loo = math.sqrt(sum(x * x for x in raw_loo))
        if norm_loo == 0:
            sys.exit(f"Leave-one-out axis norm is 0 for {arm}")
        u_loo[arm] = [x / norm_loo for x in raw_loo]

    # Overall stage 9 mean axis (average across all LOO axes / all arms) for loadings inspection
    all_diffs9: list[list[float]] = []
    for d_arm in diffs9.values():
        all_diffs9.extend(d_arm.values())
    raw_s9_all = [statistics.fmean(d[i] for d in all_diffs9) for i in range(n_feats)]
    norm_s9_all = math.sqrt(sum(x * x for x in raw_s9_all))
    u_stage9_all = [x / norm_s9_all for x in raw_s9_all]

    # Generate 35 distinct 4-against-4 split-half partitions of STYLE_PROMPTS
    all_combinations = list(itertools.combinations(STYLE_PROMPTS, 4))
    distinct_splits: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
        (c, tuple(p for p in STYLE_PROMPTS if p not in c))
        for c in all_combinations if "S1" in c
    ]
    if len(distinct_splits) != 35:
        sys.exit(f"Expected 35 distinct split-half partitions, got {len(distinct_splits)}")

    # Generate baseline pair differences for the null
    base_pairs: list[tuple[str, str, str, list[float]]] = []
    for p in STYLE_PROMPTS:
        seeds = sorted(s for (pp, s) in b9_map if pp == p)
        for s1, s2 in itertools.combinations(seeds, 2):
            delta = [x - y for x, y in zip(b9_map[(p, s1)], b9_map[(p, s2)])]
            base_pairs.append((p, s1, s2, delta))

    # 2. Monte Carlo sign-randomised null (200 draws)
    rng = random.Random(args.seed)
    signed_null_draws: list[dict[tuple[str, str], list[float]]] = []
    for _ in range(N_NULL_DRAWS):
        signed_map: dict[tuple[str, str], list[float]] = {}
        for p, s1, s2, delta in base_pairs:
            sign = rng.choice([-1, 1])
            signed_map[(p, f"{s1}-{s2}")] = [sign * x for x in delta]
        signed_null_draws.append(signed_map)

    # Check unstripped null split-half
    null_unstripped_s = [
        split_half_s(m, distinct_splits, n_feats) for m in signed_null_draws
    ]
    null_mean_unstripped = statistics.fmean(null_unstripped_s)
    null_p95_unstripped = float(statistics.quantiles(null_unstripped_s, n=100)[94])

    print(f"Null split-half check: mean = {null_mean_unstripped:.4f}, p95 = {null_p95_unstripped:.4f}")
    if null_mean_unstripped > NULL_SPLIT_HALF_THRESHOLD:
        sys.exit(
            f"FATAL: Null split-half mean ({null_mean_unstripped:.4f}) is above {NULL_SPLIT_HALF_THRESHOLD}. "
            f"Sign randomisation is not working correctly. Stopping as required by prereg §3."
        )

    # Evaluate arms across both definitions
    eval_stage7: dict[str, dict] = {}
    eval_loo: dict[str, dict] = {}

    for arm in STAGE9_ARMS:
        eval_stage7[arm] = evaluate_arm(
            diffs9[arm], u_stage7, distinct_splits, signed_null_draws, n_feats
        )
        eval_loo[arm] = evaluate_arm(
            diffs9[arm], u_loo[arm], distinct_splits, signed_null_draws, n_feats
        )

    # 4. Check agreement between definitions and set undecided if they disagree
    results_rows: list[dict] = []
    for arm in STAGE9_ARMS:
        res7 = eval_stage7[arm]
        res_loo = eval_loo[arm]

        v7 = res7["verdict"]
        v_loo = res_loo["verdict"]

        # If definitions disagree on the arm, report undecided
        consensus_v7 = v7 if v7 == v_loo else "undecided"
        consensus_v_loo = v_loo if v7 == v_loo else "undecided"

        n_cells = len(diffs9[arm])
        n_prompts = len({k[0] for k in diffs9[arm]})

        results_rows.append({
            "arm": arm,
            "axis_definition": "stage7",
            "share": f"{res7['share']:.6f}",
            "S": f"{res7['S']:.6f}",
            "S_strip": f"{res7['S_strip']:.6f}",
            "null_mean": f"{null_mean_unstripped:.6f}",
            "null_p95": f"{null_p95_unstripped:.6f}",
            "null_mean_stripped": f"{res7['null_mean_stripped']:.6f}",
            "null_p95_stripped": f"{res7['null_p95_stripped']:.6f}",
            "verdict": consensus_v7,
            "n_cells": n_cells,
            "n_prompts": n_prompts,
        })
        results_rows.append({
            "arm": arm,
            "axis_definition": "leave_one_out",
            "share": f"{res_loo['share']:.6f}",
            "S": f"{res_loo['S']:.6f}",
            "S_strip": f"{res_loo['S_strip']:.6f}",
            "null_mean": f"{null_mean_unstripped:.6f}",
            "null_p95": f"{null_p95_unstripped:.6f}",
            "null_mean_stripped": f"{res_loo['null_mean_stripped']:.6f}",
            "null_p95_stripped": f"{res_loo['null_p95_stripped']:.6f}",
            "verdict": consensus_v_loo,
            "n_cells": n_cells,
            "n_prompts": n_prompts,
        })

    # Write data/shared_axis.csv
    out_csv = Path(args.out)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "arm", "axis_definition", "share", "S", "S_strip",
        "null_mean", "null_p95", "null_mean_stripped", "null_p95_stripped",
        "verdict", "n_cells", "n_prompts"
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results_rows)
    print(f"wrote {out_csv} ({len(results_rows)} rows)")

    # Write data/shared_axis_loadings.csv
    # Compute mean loading across leave-one-out axes
    loadings_rows: list[dict] = []
    for i, feat in enumerate(feats):
        l7 = u_stage7[i]
        l_loo_mean = statistics.fmean(u_loo[arm][i] for arm in STAGE9_ARMS)
        l_s9 = u_stage9_all[i]
        loadings_rows.append({
            "feature": feat,
            "loading_stage7": f"{l7:.6f}",
            "loading_leave_one_out": f"{l_loo_mean:.6f}",
            "loading_stage9_pooled": f"{l_s9:.6f}",
        })

    out_loadings = Path(args.out_loadings)
    out_loadings.parent.mkdir(parents=True, exist_ok=True)
    loadings_fields = ["feature", "loading_stage7", "loading_leave_one_out", "loading_stage9_pooled"]
    with out_loadings.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=loadings_fields)
        writer.writeheader()
        writer.writerows(loadings_rows)
    print(f"wrote {out_loadings} ({len(loadings_rows)} features)")


if __name__ == "__main__":
    main()
