# -*- coding: utf-8 -*-
"""
experiments/shared_axis_diagnostics.py
======================================
Post-hoc diagnostics on the shared axis analysis (RUNBOOK_2026-09-25.md Block B5).
Does not modify or overwrite data/shared_axis.csv or experiments/shared_axis.py.

Evaluates:
  - D1: Angles (cosines) between axis definitions (u_stage7, u_stage9_all, u_loo).
  - D2: Observed share vs uniform random unit vector baseline in 23D (1000 draws, seed=1337).
  - D3: Null split-half behavior under matched cell counts (80 cells, 40 cells, disjoint pairs).

Output:
  - data/shared_axis_diagnostics.csv (with explicit post-hoc diagnostic flags).
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
        sys.exit(f"Input file missing: {path}")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    feats = [c for c in rows[0] if c not in NOT_FEATURES]
    return feats, rows


def cosine(a: list[float], b: list[float]) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if not na or not nb:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def compute_share(diff_dict: dict[tuple[str, str], list[float]], u: list[float]) -> float:
    shares = []
    for v in diff_dict.values():
        nv = math.sqrt(sum(x * x for x in v))
        dot = sum(x * y for x, y in zip(v, u))
        shares.append(abs(dot) / nv if nv > 0 else 0.0)
    return statistics.fmean(shares)


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


def main() -> None:
    ap = argparse.ArgumentParser(description="Shared axis diagnostics (D1, D2, D3).")
    ap.add_argument("--out", default=str(DATA / "shared_axis_diagnostics.csv"),
                    help="Target path for diagnostics CSV")
    ap.add_argument("--seed", type=int, default=RANDOM_SEED,
                    help="Random seed")
    args = ap.parse_args()

    s7_path = DATA / "style_features_stage7.csv"
    s9_path = DATA / "style_features_stage9.csv"

    feats7, rows7 = load_dataset(s7_path)
    feats9, rows9 = load_dataset(s9_path)
    if feats7 != feats9:
        sys.exit("Feature mismatch between stage7 and stage9")
    feats = feats7
    n_feats = len(feats)

    # 1. Stage 7 base and axis
    b7 = [r for r in rows7 if r["condition"] == BASELINE]
    mu7 = [statistics.fmean(float(r[f]) for r in b7) for f in feats]
    sd7 = [statistics.stdev(float(r[f]) for r in b7) for f in feats]
    def z7(r): return [(float(r[f]) - mu7[i]) / sd7[i] for i, f in enumerate(feats)]
    b7_map = {(r["prompt_dir"], r["seed"]): z7(r) for r in b7}

    diffs7 = []
    for r in rows7:
        if r["condition"] in STAGE7_ARMS:
            k = (r["prompt_dir"], r["seed"])
            if k in b7_map:
                diffs7.append([x - y for x, y in zip(z7(r), b7_map[k])])
    raw7 = [statistics.fmean(d[i] for d in diffs7) for i in range(n_feats)]
    norm7 = math.sqrt(sum(x * x for x in raw7))
    u_stage7 = [x / norm7 for x in raw7]

    # 2. Stage 9 base and arms
    rows9_style = [r for r in rows9 if r["prompt_dir"] in STYLE_PROMPTS]
    b9 = [r for r in rows9_style if r["condition"] == BASELINE]
    mu9 = [statistics.fmean(float(r[f]) for r in b9) for f in feats]
    sd9 = [statistics.stdev(float(r[f]) for r in b9) for f in feats]
    def z9(r): return [(float(r[f]) - mu9[i]) / sd9[i] for i, f in enumerate(feats)]
    b9_map = {(r["prompt_dir"], r["seed"]): z9(r) for r in b9}

    diffs9: dict[str, dict[tuple[str, str], list[float]]] = {}
    diffs9_all: list[list[float]] = []
    for arm in STAGE9_ARMS:
        d_arm = {}
        for r in rows9_style:
            if r["condition"] == arm:
                k = (r["prompt_dir"], r["seed"])
                if k in b9_map:
                    v = [x - y for x, y in zip(z9(r), b9_map[k])]
                    d_arm[k] = v
                    diffs9_all.append(v)
        diffs9[arm] = d_arm

    raw9_all = [statistics.fmean(d[i] for d in diffs9_all) for i in range(n_feats)]
    norm9_all = math.sqrt(sum(x * x for x in raw9_all))
    u_stage9_all = [x / norm9_all for x in raw9_all]

    u_loo: dict[str, list[float]] = {}
    for arm in STAGE9_ARMS:
        other_diffs: list[list[float]] = []
        for other_arm in STAGE9_ARMS:
            if other_arm != arm:
                other_diffs.extend(diffs9[other_arm].values())
        raw_loo = [statistics.fmean(d[i] for d in other_diffs) for i in range(n_feats)]
        norm_loo = math.sqrt(sum(x * x for x in raw_loo))
        u_loo[arm] = [x / norm_loo for x in raw_loo]

    rows_out: list[dict] = []

    # ----------------------------------------------------
    # B5.2: D1 — Angles between axes
    # ----------------------------------------------------
    print("=== D1: Angles Between Axis Definitions ===")
    cos_s7_s9all = cosine(u_stage7, u_stage9_all)
    print(f"cos(u_stage7, u_stage9_all_arms) = {cos_s7_s9all:.6f}")
    rows_out.append({
        "diagnostic_id": "D1_axis_angle",
        "item": "u_stage7_vs_u_stage9_all_arms",
        "axis_definition": "cross_definition",
        "value": f"{cos_s7_s9all:.6f}",
        "reference_mean": "",
        "reference_p95": "",
        "percentile_in_reference": "",
        "note": "cosine between primary stage7 axis and pooled stage9 axis",
        "is_post_hoc_diagnostic": "yes"
    })

    print("cos(u_stage7, u_loo[arm]):")
    for arm in STAGE9_ARMS:
        c = cosine(u_stage7, u_loo[arm])
        print(f"  {arm:18s}: {c:.6f}")
        rows_out.append({
            "diagnostic_id": "D1_axis_angle",
            "item": f"u_stage7_vs_u_loo_{arm}",
            "axis_definition": "cross_definition",
            "value": f"{c:.6f}",
            "reference_mean": "",
            "reference_p95": "",
            "percentile_in_reference": "",
            "note": f"cosine between stage7 axis and LOO axis for {arm}",
            "is_post_hoc_diagnostic": "yes"
        })

    print("cos(u_loo[i], u_loo[j]):")
    for a1, a2 in itertools.combinations(STAGE9_ARMS, 2):
        c = cosine(u_loo[a1], u_loo[a2])
        print(f"  {a1:18s} vs {a2:18s}: {c:.6f}")
        rows_out.append({
            "diagnostic_id": "D1_axis_angle",
            "item": f"u_loo_{a1}_vs_u_loo_{a2}",
            "axis_definition": "within_stage9_loo",
            "value": f"{c:.6f}",
            "reference_mean": "",
            "reference_p95": "",
            "percentile_in_reference": "",
            "note": f"pairwise cosine between LOO axes of {a1} and {a2}",
            "is_post_hoc_diagnostic": "yes"
        })

    # ----------------------------------------------------
    # B5.3: D2 — Random-direction baseline for share
    # ----------------------------------------------------
    print("\n=== D2: Random-Direction Baseline for Share ===")
    rng = random.Random(args.seed)
    random_vectors: list[list[float]] = []
    for _ in range(1000):
        g = [rng.gauss(0, 1) for _ in range(n_feats)]
        ng = math.sqrt(sum(x * x for x in g))
        random_vectors.append([x / ng for x in g])

    d2_header = f"{'arm':18s} {'share_s7':10s} {'pct_s7':8s} {'share_loo':10s} {'pct_loo':8s} {'rand_mean':10s} {'rand_p95':10s}"
    print(d2_header)

    for arm in STAGE9_ARMS:
        d_arm = diffs9[arm]
        s_s7 = compute_share(d_arm, u_stage7)
        s_loo = compute_share(d_arm, u_loo[arm])

        # 1000 random direction shares for this arm
        rand_shares = [compute_share(d_arm, u_rnd) for u_rnd in random_vectors]
        rand_mean = statistics.fmean(rand_shares)
        rand_p95 = float(statistics.quantiles(rand_shares, n=100)[94])

        pct_s7 = sum(1 for x in rand_shares if x <= s_s7) / len(rand_shares) * 100.0
        pct_loo = sum(1 for x in rand_shares if x <= s_loo) / len(rand_shares) * 100.0

        row_str = f"{arm:18s} {s_s7:10.4f} {pct_s7:7.1f}%  {s_loo:10.4f} {pct_loo:7.1f}%  {rand_mean:10.4f} {rand_p95:10.4f}"
        print(row_str)

        rows_out.append({
            "diagnostic_id": "D2_share_vs_random",
            "item": arm,
            "axis_definition": "stage7",
            "value": f"{s_s7:.6f}",
            "reference_mean": f"{rand_mean:.6f}",
            "reference_p95": f"{rand_p95:.6f}",
            "percentile_in_reference": f"{pct_s7:.1f}",
            "note": "observed share falls below random-direction p95" if pct_s7 < 95.0 else "observed share above random-direction p95",
            "is_post_hoc_diagnostic": "yes"
        })
        rows_out.append({
            "diagnostic_id": "D2_share_vs_random",
            "item": arm,
            "axis_definition": "leave_one_out",
            "value": f"{s_loo:.6f}",
            "reference_mean": f"{rand_mean:.6f}",
            "reference_p95": f"{rand_p95:.6f}",
            "percentile_in_reference": f"{pct_loo:.1f}",
            "note": "observed share falls below random-direction p95" if pct_loo < 95.0 else "observed share above random-direction p95",
            "is_post_hoc_diagnostic": "yes"
        })

    # ----------------------------------------------------
    # B5.4: D3 — Null with matched cell count
    # ----------------------------------------------------
    print("\n=== D3: Null with Matched Cell Count ===")
    all_comb = list(itertools.combinations(STYLE_PROMPTS, 4))
    distinct_splits = [
        (c, tuple(p for p in STYLE_PROMPTS if p not in c))
        for c in all_comb if "S1" in c
    ]

    # Config 1: 80 cells (all baseline pairs C(5,2)=10 per prompt x 8 prompts)
    base_pairs_80 = []
    for p in STYLE_PROMPTS:
        seeds = sorted(s for (pp, s) in b9_map if pp == p)
        for s1, s2 in itertools.combinations(seeds, 2):
            delta = [x - y for x, y in zip(b9_map[(p, s1)], b9_map[(p, s2)])]
            base_pairs_80.append((p, s1, s2, delta))

    rng_null = random.Random(args.seed)
    null_80 = []
    for _ in range(200):
        signed_map = {}
        for p, s1, s2, delta in base_pairs_80:
            sign = rng_null.choice([-1, 1])
            signed_map[(p, f"{s1}-{s2}")] = [sign * x for x in delta]
        null_80.append(split_half_s(signed_map, distinct_splits, n_feats))
    m80 = statistics.fmean(null_80)
    p95_80 = float(statistics.quantiles(null_80, n=100)[94])

    # Config 2: 40 cells sampled (5 pairs per prompt x 8 prompts)
    rng_null = random.Random(args.seed)
    null_40 = []
    for _ in range(200):
        signed_map = {}
        for p in STYLE_PROMPTS:
            seeds = sorted(s for (pp, s) in b9_map if pp == p)
            all_pairs = list(itertools.combinations(seeds, 2))
            chosen = rng_null.sample(all_pairs, 5)
            for s1, s2 in chosen:
                delta = [x - y for x, y in zip(b9_map[(p, s1)], b9_map[(p, s2)])]
                sign = rng_null.choice([-1, 1])
                signed_map[(p, f"{s1}-{s2}")] = [sign * x for x in delta]
        null_40.append(split_half_s(signed_map, distinct_splits, n_feats))
    m40 = statistics.fmean(null_40)
    p95_40 = float(statistics.quantiles(null_40, n=100)[94])

    # Config 3: 16 cells strictly disjoint pairs (2 disjoint pairs per prompt x 8 prompts)
    rng_null = random.Random(args.seed)
    null_disjoint = []
    for _ in range(200):
        signed_map = {}
        for p in STYLE_PROMPTS:
            seeds = list(sorted(s for (pp, s) in b9_map if pp == p))
            rng_null.shuffle(seeds)
            for s1, s2 in [(seeds[0], seeds[1]), (seeds[2], seeds[3])]:
                delta = [x - y for x, y in zip(b9_map[(p, s1)], b9_map[(p, s2)])]
                sign = rng_null.choice([-1, 1])
                signed_map[(p, f"{s1}-{s2}")] = [sign * x for x in delta]
        null_disjoint.append(split_half_s(signed_map, distinct_splits, n_feats))
    m_disj = statistics.fmean(null_disjoint)
    p95_disj = float(statistics.quantiles(null_disjoint, n=100)[94])

    print(f"80-cell null (all pairs)            : mean = {m80:.4f}, p95 = {p95_80:.4f}")
    print(f"40-cell null (5 pairs/prompt)       : mean = {m40:.4f}, p95 = {p95_40:.4f}")
    print(f"16-cell disjoint null (2 pairs/prm) : mean = {m_disj:.4f}, p95 = {p95_disj:.4f}")

    rows_out.append({
        "diagnostic_id": "D3_null_cell_count",
        "item": "null_80_cells_all_pairs",
        "axis_definition": "unstripped_null",
        "value": f"{m80:.6f}",
        "reference_mean": f"{m80:.6f}",
        "reference_p95": f"{p95_80:.6f}",
        "percentile_in_reference": "",
        "note": "80 baseline pairs across 8 style prompts (C(5,2)=10 per prompt)",
        "is_post_hoc_diagnostic": "yes"
    })
    rows_out.append({
        "diagnostic_id": "D3_null_cell_count",
        "item": "null_40_cells_sampled",
        "axis_definition": "unstripped_null",
        "value": f"{m40:.6f}",
        "reference_mean": f"{m40:.6f}",
        "reference_p95": f"{p95_40:.6f}",
        "percentile_in_reference": "",
        "note": "40 baseline pairs sampled (5 per prompt across 8 style prompts)",
        "is_post_hoc_diagnostic": "yes"
    })
    rows_out.append({
        "diagnostic_id": "D3_null_cell_count",
        "item": "null_16_cells_strictly_disjoint",
        "axis_definition": "unstripped_null",
        "value": f"{m_disj:.6f}",
        "reference_mean": f"{m_disj:.6f}",
        "reference_p95": f"{p95_disj:.6f}",
        "percentile_in_reference": "",
        "note": "16 strictly disjoint baseline pairs (each baseline used at most once per draw)",
        "is_post_hoc_diagnostic": "yes"
    })

    # Write data/shared_axis_diagnostics.csv
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "diagnostic_id", "item", "axis_definition", "value",
        "reference_mean", "reference_p95", "percentile_in_reference",
        "note", "is_post_hoc_diagnostic"
    ]
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)
    print(f"\nwrote {out_path} ({len(rows_out)} rows)")


if __name__ == "__main__":
    main()
