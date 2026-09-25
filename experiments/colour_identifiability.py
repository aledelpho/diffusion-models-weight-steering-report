# -*- coding: utf-8 -*-
"""
experiments/colour_identifiability.py
=====================================
Evaluates whether colour carries an independent fingerprint of the arm.
Governed by docs/prereg_colour_identifiability.md (2026-09-25).

Classifiers, folds, and permutation machinery are inherited unchanged
from Block H (experiments/arm_identifiability.py).

Features evaluated:
  - T: 19 texture features (style features excluding 4 colour features)
  - C1: 4 global colour features
  - C2: 13 features (C1 + 9 CIELAB moment deltas)
  - C3: 25 features (C2 + 12 regional features at 3 bands)
  - C3_5b: 33 features (C2 + 20 regional features at 5 bands, sensitivity)
  - T + C3: 44 features (T + C3)

Pre-fit additions to §5 (decided on matrix dimensions alone, before seeing accuracies):
  - Control term T + C3-perm: 25 colour features permuted within each (prompt, seed)
    group across 1000 draws (seed 1337) to separate true information from model capacity.
    Rule: colour adds information only if Acc(T+C3) > p95(Acc(T+C3-perm)).
    Otherwise: 'capacità e non informazione'.
  - Ceiling guard: if Acc(T) > 0.95 on a contrast (e.g. 2-class), marked 'ceiling_uninformative'.
    The decisive test is evaluated on the 6-class contrast.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import random
import statistics
import sys
import warnings
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

try:
    from joblib import Parallel, delayed
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

warnings.filterwarnings("ignore", category=ConvergenceWarning)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

NOT_FEATURES = {
    "file", "width_px", "height_px", "condition", "prompt_dir", "prompt_id",
    "prompt_sha1", "seed", "rel_path", "source_manifest", "source_csv",
    "paper_hex", "ink_hex", "sw1_hex", "sw2_hex", "sw3_hex", "sw4_hex", "sw5_hex", "sw6_hex",
    "corpus", "arm", "prompt"
}

COLOUR_4 = {
    "color_n_effective",
    "color_top4_cluster_share",
    "color_cluster_entropy_norm",
    "colorfulness_hs",
}

CIELAB_9 = [
    "delta_mean_L", "delta_mean_a", "delta_mean_b",
    "delta_std_L", "delta_std_a", "delta_std_b",
    "delta_corr_La", "delta_corr_Lb", "delta_corr_ab",
]

STAGE7_TEST_PROMPTS = [
    "I01", "I02", "I05", "I06", "I07", "I09", "I10", "I11",
    "I12", "I16", "I17", "I18", "I20", "I21", "I23", "I24"
]
STAGE7_ARMS_6 = [
    "preset_pos", "preset_neg",
    "blockshuf_pos", "blockshuf_neg",
    "rand_pos", "rand_neg"
]
STAGE7_ARMS_2 = ["preset_pos", "rand_pos"]

STAGE9_STYLE_PROMPTS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
STAGE9_ARMS_6 = [
    "preset_pos_1x", "preset_pos_2x",
    "blockshuf_neg_1x", "blockshuf_neg_2x",
    "rand_pos_1x", "rand_pos_2x"
]
STAGE9_ARMS_2 = ["preset_pos_1x", "rand_pos_1x"]

SEEDS = [42, 777, 1337, 9999, 4242145]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors."""
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def evaluate_nearest_centroid(
    deltas: List[Dict[str, Any]],
    prompts: List[str],
    arms: List[str],
    vec_key: str = "delta"
) -> Tuple[float, List[Tuple[str, str, str]], Dict[str, int], Dict[str, int]]:
    """
    Leave-one-prompt-out Nearest Centroid by Cosine distance.
    Returns: (accuracy, predictions_tuples, fold_correct_dict, fold_total_dict)
    """
    preds: List[Tuple[str, str, str]] = []
    fold_correct: Dict[str, int] = {}
    fold_total: Dict[str, int] = {}

    for held_out in prompts:
        train_deltas = [d for d in deltas if d["prompt"] != held_out]
        test_deltas = [d for d in deltas if d["prompt"] == held_out]

        centroids: Dict[str, List[float]] = {}
        for a in arms:
            arm_vecs = [d[vec_key] for d in train_deltas if d["arm"] == a]
            dim = len(arm_vecs[0])
            c = [statistics.fmean(v[i] for v in arm_vecs) for i in range(dim)]
            centroids[a] = c

        f_corr = 0
        for td in test_deltas:
            true_a = td["arm"]
            vec = td[vec_key]
            best_a = max(arms, key=lambda a: cosine_similarity(vec, centroids[a]))
            preds.append((held_out, true_a, best_a))
            if best_a == true_a:
                f_corr += 1

        fold_correct[held_out] = f_corr
        fold_total[held_out] = len(test_deltas)

    total_correct = sum(1 for _, t, p in preds if t == p)
    acc = total_correct / len(preds)
    return acc, preds, fold_correct, fold_total


def evaluate_logistic_regression(
    deltas: List[Dict[str, Any]],
    prompts: List[str],
    arms: List[str],
    vec_key: str = "delta"
) -> Tuple[float, List[Tuple[str, str, str]], Dict[str, int], Dict[str, int]]:
    """
    Leave-one-prompt-out Multinomial Logistic Regression (L2, C=1.0, max_iter=2000).
    Returns: (accuracy, predictions_tuples, fold_correct_dict, fold_total_dict)
    """
    arm_to_idx = {a: i for i, a in enumerate(arms)}
    idx_to_arm = {i: a for i, a in enumerate(arms)}
    preds: List[Tuple[str, str, str]] = []
    fold_correct: Dict[str, int] = {}
    fold_total: Dict[str, int] = {}

    for held_out in prompts:
        train_deltas = [d for d in deltas if d["prompt"] != held_out]
        test_deltas = [d for d in deltas if d["prompt"] == held_out]

        X_train = [d[vec_key] for d in train_deltas]
        y_train = [arm_to_idx[d["arm"]] for d in train_deltas]
        X_test = [d[vec_key] for d in test_deltas]
        y_test = [arm_to_idx[d["arm"]] for d in test_deltas]

        clf = LogisticRegression(
            penalty="l2",
            C=1.0,
            max_iter=2000,
            random_state=1337,
            solver="lbfgs"
        )
        clf.fit(X_train, y_train)
        pred_indices = clf.predict(X_test)

        f_corr = 0
        for true_idx, pred_idx in zip(y_test, pred_indices):
            t_a = idx_to_arm[true_idx]
            p_a = idx_to_arm[pred_idx]
            preds.append((held_out, t_a, p_a))
            if t_a == p_a:
                f_corr += 1

        fold_correct[held_out] = f_corr
        fold_total[held_out] = len(test_deltas)

    total_correct = sum(1 for _, t, p in preds if t == p)
    acc = total_correct / len(preds)
    return acc, preds, fold_correct, fold_total


def compute_diagnostics_and_confusion(
    preds: List[Tuple[str, str, str]],
    fold_correct: Dict[str, int],
    fold_total: Dict[str, int],
    arms: List[str]
) -> Dict[str, Any]:
    """Computes confusion matrix, per-arm recalls, and checks §7 guards."""
    n_classes = len(arms)
    chance = 1.0 / n_classes

    # Confusion matrix
    conf: Dict[Tuple[str, str], int] = Counter((t, p) for _, t, p in preds)

    # Recalls
    recalls: Dict[str, float] = {}
    supports: Dict[str, int] = {}
    for a in arms:
        supp = sum(conf.get((a, pred_a), 0) for pred_a in arms)
        corr = conf.get((a, a), 0)
        recalls[a] = corr / supp if supp > 0 else 0.0
        supports[a] = supp

    # Guard 1: carried by one arm (recall > 3x mean of others)
    is_carried_by_one_arm = False
    carried_arm_name = ""
    max_arm_ratio = 0.0

    for a in arms:
        other_recalls = [recalls[oa] for oa in arms if oa != a]
        mean_others = statistics.fmean(other_recalls) if other_recalls else 0.0
        if mean_others > 0:
            ratio = recalls[a] / mean_others
        else:
            ratio = 999.0 if recalls[a] > 0 else 1.0

        if ratio > max_arm_ratio:
            max_arm_ratio = ratio

        if ratio > 3.0:
            is_carried_by_one_arm = True
            carried_arm_name = a

    # Guard 2: fragile fold (> 40% of above-chance correct predictions)
    total_correct = sum(1 for _, t, p in preds if t == p)
    total_cells = len(preds)
    expected_chance_correct = total_cells * chance
    above_chance_total = total_correct - expected_chance_correct

    is_fragile = False
    fragile_fold_name = ""
    max_fold_share = 0.0

    if above_chance_total > 0:
        for p, corr in fold_correct.items():
            tot = fold_total[p]
            f_chance = tot * chance
            f_above = max(0.0, corr - f_chance)
            share = f_above / above_chance_total
            if share > max_fold_share:
                max_fold_share = share
            if share > 0.40:
                is_fragile = True
                fragile_fold_name = p
    else:
        max_fold_share = 0.0

    return {
        "confusion": conf,
        "recalls": recalls,
        "supports": supports,
        "max_arm_ratio": max_arm_ratio,
        "carried_arm_name": carried_arm_name,
        "is_carried_by_one_arm": is_carried_by_one_arm,
        "max_fold_share": max_fold_share,
        "fragile_fold_name": fragile_fold_name,
        "is_fragile": is_fragile,
    }


def _eval_one_perm(
    cells_list: List[Dict[str, Any]],
    prompts: List[str],
    arms: List[str],
    eval_func: Any,
    vec_key: str
) -> float:
    acc, _, _, _ = eval_func(cells_list, prompts, arms, vec_key=vec_key)
    return acc


def run_permutation_null(
    deltas: List[Dict[str, Any]],
    prompts: List[str],
    arms: List[str],
    eval_func: Any,
    observed_acc: float,
    vec_key: str = "delta",
    n_perms: int = 1000,
    seed: int = 1337,
    n_jobs: int = 16
) -> Tuple[float, float, float, float]:
    """
    Runs 1000 permutations shuffling arm labels within each (prompt, seed) group.
    Returns: (null_mean, null_p95, p_perm, p_floor)
    """
    rng = random.Random(seed)
    grouped: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}
    for d in deltas:
        grouped.setdefault((d["prompt"], d["seed"]), []).append(d)

    # Pre-generate permutation datasets deterministically
    all_perm_datasets: List[List[Dict[str, Any]]] = []
    for _ in range(n_perms):
        perm_deltas: List[Dict[str, Any]] = []
        for (p, s), cells in grouped.items():
            shuffled_labels = [c["arm"] for c in cells]
            rng.shuffle(shuffled_labels)
            for c, shuf_label in zip(cells, shuffled_labels):
                perm_deltas.append({
                    "prompt": p,
                    "seed": s,
                    "arm": shuf_label,
                    vec_key: c[vec_key],
                })
        all_perm_datasets.append(perm_deltas)

    # Evaluate sequentially for Nearest Centroid (already ~1 ms/draw) or parallel for Logistic Regression
    if HAS_JOBLIB and eval_func == evaluate_logistic_regression and n_jobs > 1:
        null_accs = Parallel(n_jobs=n_jobs)(
            delayed(_eval_one_perm)(ds, prompts, arms, eval_func, vec_key) for ds in all_perm_datasets
        )
    else:
        null_accs = [
            _eval_one_perm(ds, prompts, arms, eval_func, vec_key) for ds in all_perm_datasets
        ]

    hits = sum(1 for p_acc in null_accs if p_acc >= observed_acc - 1e-12)

    null_mean = statistics.fmean(null_accs)
    null_p95 = float(statistics.quantiles(null_accs, n=100)[94])
    p_perm = hits / n_perms
    p_floor = 1.0 / n_perms

    return null_mean, null_p95, p_perm, p_floor


def run_capacity_control_null(
    deltas: List[Dict[str, Any]],
    prompts: List[str],
    arms: List[str],
    eval_func: Any,
    n_perms: int = 1000,
    seed: int = 1337,
    n_jobs: int = 16
) -> Tuple[float, float]:
    """
    Control term: T + C3-permuted.
    Keeps true T intact with true arm labels; permutes only C3 within each (prompt, seed) group.
    Returns: (perm_mean, perm_p95)
    """
    rng = random.Random(seed)
    grouped: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}
    for d in deltas:
        grouped.setdefault((d["prompt"], d["seed"]), []).append(d)

    all_perm_datasets: List[List[Dict[str, Any]]] = []
    for _ in range(n_perms):
        shuf_dataset: List[Dict[str, Any]] = []
        for (p, s), cells in grouped.items():
            c3_vecs = [c["C3"] for c in cells]
            rng.shuffle(c3_vecs)
            for c, shuf_c3 in zip(cells, c3_vecs):
                combined = c["T"] + shuf_c3
                shuf_dataset.append({
                    "prompt": p,
                    "seed": s,
                    "arm": c["arm"],
                    "vec": combined,
                })
        all_perm_datasets.append(shuf_dataset)

    if HAS_JOBLIB and eval_func == evaluate_logistic_regression and n_jobs > 1:
        perm_accs = Parallel(n_jobs=n_jobs)(
            delayed(_eval_one_perm)(ds, prompts, arms, eval_func, "vec") for ds in all_perm_datasets
        )
    else:
        perm_accs = [
            _eval_one_perm(ds, prompts, arms, eval_func, "vec") for ds in all_perm_datasets
        ]

    perm_mean = statistics.fmean(perm_accs)
    perm_p95 = float(statistics.quantiles(perm_accs, n=100)[94])
    return perm_mean, perm_p95


def assemble_dataset(
    corpus: str,
    prompts: List[str],
    arms: List[str]
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Loads style, palette position, and regional colour features and computes Delta."""
    # 1. Style features
    style_csv = DATA / f"style_features_{corpus}.csv"
    with style_csv.open(encoding="utf-8-sig") as fh:
        style_rows = list(csv.DictReader(fh))

    all_style_cols = [c for c in style_rows[0].keys() if c not in NOT_FEATURES]
    t_cols = [c for c in all_style_cols if c not in COLOUR_4]
    c1_cols = [c for c in all_style_cols if c in COLOUR_4]

    # Standardise style on baseline
    base_style = [r for r in style_rows if r["condition"] == "baseline"]
    mu_style = {c: statistics.fmean(float(r[c]) for r in base_style) for c in all_style_cols}
    sd_style = {c: statistics.stdev(float(r[c]) for r in base_style) for c in all_style_cols}
    base_style_map = {(r["prompt_dir"], int(r["seed"])): r for r in base_style}

    # 2. Regional colour features
    with (DATA / "colour_features_regional.csv").open(encoding="utf-8-sig") as fh:
        reg_rows = [r for r in csv.DictReader(fh) if r["corpus"] == corpus]

    reg3_cols = [c for c in reg_rows[0].keys() if c.startswith("band3_")]
    reg5_cols = [c for c in reg_rows[0].keys() if c.startswith("band5_")]
    all_reg_cols = reg3_cols + reg5_cols

    base_reg = [r for r in reg_rows if r["arm"] == "baseline"]
    mu_reg = {c: statistics.fmean(float(r[c]) for r in base_reg) for c in all_reg_cols}
    sd_reg = {c: statistics.stdev(float(r[c]) for r in base_reg) for c in all_reg_cols}
    base_reg_map = {(r["prompt"], int(r["seed"])): r for r in base_reg}

    # 3. Palette position moments (Track A)
    pos_csv = DATA / ("palette_position_stage7.csv" if corpus == "stage7" else "palette_position.csv")
    with pos_csv.open(encoding="utf-8-sig") as fh:
        pos_rows = list(csv.DictReader(fh))
    pos_delta_map = {(r["arm"], r["prompt"], int(r["seed"])): [float(r[c]) for c in CIELAB_9] for r in pos_rows}

    dataset: List[Dict[str, Any]] = []

    for p in prompts:
        for s in SEEDS:
            b_st = base_style_map[(p, s)]
            b_rg = base_reg_map[(p, s)]

            for a in arms:
                m_st = [r for r in style_rows if r["prompt_dir"] == p and int(r["seed"]) == s and r["condition"] == a][0]
                m_rg = [r for r in reg_rows if r["prompt"] == p and int(r["seed"]) == s and r["arm"] == a][0]
                d_pos = pos_delta_map[(a, p, s)]

                # Standardised Deltas
                dT = [(float(m_st[c]) - float(b_st[c])) / sd_style[c] for c in t_cols]
                dC1 = [(float(m_st[c]) - float(b_st[c])) / sd_style[c] for c in c1_cols]
                dC2 = dC1 + d_pos
                dC3_reg3 = [(float(m_rg[c]) - float(b_rg[c])) / sd_reg[c] for c in reg3_cols]
                dC3_reg5 = [(float(m_rg[c]) - float(b_rg[c])) / sd_reg[c] for c in reg5_cols]

                dC3 = dC2 + dC3_reg3
                dC3_5b = dC2 + dC3_reg5
                dT_plus_C3 = dT + dC3

                dataset.append({
                    "corpus": corpus,
                    "prompt": p,
                    "seed": s,
                    "arm": a,
                    "T": dT,
                    "C1": dC1,
                    "C2": dC2,
                    "C3": dC3,
                    "C3_5b": dC3_5b,
                    "T_plus_C3": dT_plus_C3,
                })

    dims = {
        "T": len(t_cols),
        "C1": len(c1_cols),
        "C2": len(dC2),
        "C3": len(dC3),
        "C3_5b": len(dC3_5b),
        "T_plus_C3": len(dT_plus_C3)
    }
    return dataset, dims


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate colour identifiability.")
    ap.add_argument("--perms", type=int, default=1000, help="Number of permutations for null")
    ap.add_argument("--seed", type=int, default=1337, help="Random seed")
    ap.add_argument("--n-jobs", type=int, default=20, help="Number of CPU workers for parallel fits")
    ap.add_argument("--out-tests", default=str(DATA / "colour_identifiability_tests.csv"))
    ap.add_argument("--out-predictions", default=str(DATA / "colour_identifiability.csv"))
    ap.add_argument("--out-confusion", default=str(DATA / "colour_identifiability_confusion.csv"))
    args = ap.parse_args()

    print("=== BLOCK I: COLOUR IDENTIFIABILITY ===")
    print("Loading datasets and assembling standardized feature spaces...")

    dataset_s7, dims_s7 = assemble_dataset("stage7", STAGE7_TEST_PROMPTS, STAGE7_ARMS_6)
    dataset_s9, dims_s9 = assemble_dataset("stage9", STAGE9_STYLE_PROMPTS, STAGE9_ARMS_6)

    print(f"Stage 7: {len(dataset_s7)} cells across 16 prompts. Dims: {dims_s7}")
    print(f"Stage 9: {len(dataset_s9)} cells across 8 prompts. Dims: {dims_s9}")

    trace_note = (
        "Aggiunta pre-fit al §5 decisa su dimensioni matrice (T=19 vs T+C3=44) prima di vedere accuratezze: "
        "introdotto controllo T + C3-permutato (25 feat C3 permutate entro (prompt, seed), 1000 draw, seed 1337) "
        "per scorporare capacità da informazione. Regola pre-fissata: se Acc(T) > 0.95 il test è ceiling_uninformative; "
        "su 6 classi, guadagno valido solo se T+C3 > p95(T+C3-perm), altrimenti capacità e non informazione."
    )

    all_predictions_rows: List[Dict[str, Any]] = []
    all_confusion_rows: List[Dict[str, Any]] = []
    test_results: List[Dict[str, Any]] = []

    # Corpora specifications
    corpora_specs = [
        ("stage7", dataset_s7, STAGE7_TEST_PROMPTS, STAGE7_ARMS_6, STAGE7_ARMS_2, dims_s7),
        ("stage9", dataset_s9, STAGE9_STYLE_PROMPTS, STAGE9_ARMS_6, STAGE9_ARMS_2, dims_s9),
    ]

    classifiers = [
        ("nearest_centroid", evaluate_nearest_centroid),
        ("logistic_regression", evaluate_logistic_regression),
    ]

    for corpus, dataset, prompts, arms_6, arms_2, dims in corpora_specs:
        print(f"\n--- Running evaluations for {corpus.upper()} ---")

        for clf_name, eval_func in classifiers:
            print(f"\nClassifier: {clf_name}")

            # Run capacity control on 6-class and 2-class
            print("  Evaluating capacity control (T vs T+C3 vs T+C3-perm)...")
            cap_stats: Dict[str, Any] = {}
            for contrast, arm_subset in [("6_class", arms_6), ("2_class", arms_2)]:
                sub_data = [d for d in dataset if d["arm"] in arm_subset]

                # Acc(T)
                acc_t, _, _, _ = eval_func(sub_data, prompts, arm_subset, vec_key="T")
                # Acc(T+C3)
                acc_tc3, _, _, _ = eval_func(sub_data, prompts, arm_subset, vec_key="T_plus_C3")

                # Acc(T+C3-perm)
                print(f"    Running {args.perms} draws for T+C3-perm on {contrast}...")
                perm_mean, perm_p95 = run_capacity_control_null(
                    sub_data, prompts, arm_subset, eval_func, n_perms=args.perms, seed=args.seed, n_jobs=args.n_jobs
                )

                # Reading rule per §6 and pre-fit capacity rule
                if acc_t > 0.95:
                    info_verdict = "ceiling_uninformative"
                elif acc_tc3 <= acc_t:
                    info_verdict = "capacità e non informazione"  # colour adds no gain to texture
                elif acc_tc3 > perm_p95 + 1e-12:
                    info_verdict = "colour carries an independent fingerprint"
                else:
                    info_verdict = "capacità e non informazione"

                cap_stats[contrast] = {
                    "acc_t": acc_t,
                    "acc_tc3": acc_tc3,
                    "perm_mean": perm_mean,
                    "perm_p95": perm_p95,
                    "info_verdict": info_verdict
                }
                print(f"    [{corpus} {clf_name} {contrast}] Acc(T)={acc_t:.4f}, Acc(T+C3)={acc_tc3:.4f}, "
                      f"T+C3-perm(p95)={perm_p95:.4f} -> {info_verdict}")

            # Feature sets to test individually against perm null
            # Pre-registered order: C2 (primary 2-class), C2 6-class, C3 2-class, C1 2-class
            fsets = ["C2", "C3", "C1", "T", "T_plus_C3", "C3_5b"]

            for fset in fsets:
                for contrast, arm_subset in [("2_class", arms_2), ("6_class", arms_6)]:
                    sub_data = [d for d in dataset if d["arm"] in arm_subset]
                    chance = 1.0 / len(arm_subset)

                    acc, preds, fold_corr, fold_tot = eval_func(sub_data, prompts, arm_subset, vec_key=fset)
                    diag = compute_diagnostics_and_confusion(preds, fold_corr, fold_tot, arm_subset)

                    # Predictions records
                    for held_out in prompts:
                        f_acc = fold_corr[held_out] / fold_tot[held_out] if fold_tot[held_out] > 0 else 0.0
                        for a in arm_subset:
                            # per-fold per-arm recall
                            arm_preds = [p for p in preds if p[0] == held_out and p[1] == a]
                            supp = len(arm_preds)
                            corr = sum(1 for p in arm_preds if p[1] == p[2])
                            rec = corr / supp if supp > 0 else 0.0
                            all_predictions_rows.append({
                                "corpus": corpus,
                                "classifier": clf_name,
                                "contrast": contrast,
                                "feature_set": fset,
                                "fold_prompt": held_out,
                                "arm": a,
                                "support": supp,
                                "correct": corr,
                                "recall": round(rec, 4),
                                "fold_accuracy": round(f_acc, 4),
                            })

                    # Confusion matrix records
                    for ta in arm_subset:
                        for pa in arm_subset:
                            cnt = diag["confusion"].get((ta, pa), 0)
                            supp = diag["supports"][ta]
                            share = cnt / supp if supp > 0 else 0.0
                            all_confusion_rows.append({
                                "corpus": corpus,
                                "classifier": clf_name,
                                "contrast": contrast,
                                "feature_set": fset,
                                "true_arm": ta,
                                "pred_arm": pa,
                                "count": cnt,
                                "support": supp,
                                "share_within_true": round(share, 4),
                            })

                    # Permutation null (1000 draws)
                    null_mean, null_p95, p_perm, p_floor = run_permutation_null(
                        sub_data, prompts, arm_subset, eval_func, acc, vec_key=fset, n_perms=args.perms, seed=args.seed, n_jobs=args.n_jobs
                    )

                    cs = cap_stats[contrast]

                    test_results.append({
                        "corpus": corpus,
                        "classifier": clf_name,
                        "contrast": contrast,
                        "feature_set": fset,
                        "n_features": dims[fset],
                        "n_classes": len(arm_subset),
                        "n_prompts": len(prompts),
                        "n_cells": len(sub_data),
                        "observed_accuracy": round(acc, 4),
                        "chance_accuracy": round(chance, 4),
                        "null_mean": round(null_mean, 4),
                        "null_p95": round(null_p95, 4),
                        "p_perm": round(p_perm, 4),
                        "p_floor": round(p_floor, 4),
                        "p_holm": "",  # updated below for Holm tests
                        "max_arm_ratio": round(diag["max_arm_ratio"], 2),
                        "is_carried_by_one_arm": diag["is_carried_by_one_arm"],
                        "max_fold_share": round(diag["max_fold_share"], 4),
                        "is_fragile": diag["is_fragile"],
                        "verdict": "",  # updated below
                        "t_acc": round(cs["acc_t"], 4),
                        "t_plus_c3_acc": round(cs["acc_tc3"], 4),
                        "t_plus_c3_perm_mean": round(cs["perm_mean"], 4),
                        "t_plus_c3_perm_p95": round(cs["perm_p95"], 4),
                        "colour_information_verdict": cs["info_verdict"],
                        "details": trace_note
                    })

    # Apply Holm correction on Stage 7 pre-specified tests
    # §5 defines:
    #   Primary: C2, 2_class, nearest_centroid, stage7
    #   Secondaries:
    #     1. C2, 6_class, nearest_centroid, stage7
    #     2. C3, 2_class, nearest_centroid, stage7
    #     3. C1, 2_class, nearest_centroid, stage7
    holm_keys = [
        ("stage7", "nearest_centroid", "2_class", "C2"),
        ("stage7", "nearest_centroid", "6_class", "C2"),
        ("stage7", "nearest_centroid", "2_class", "C3"),
        ("stage7", "nearest_centroid", "2_class", "C1"),
    ]

    holm_rows = [r for r in test_results if (r["corpus"], r["classifier"], r["contrast"], r["feature_set"]) in holm_keys]
    # Sort by p_perm ascending
    sorted_holm = sorted(holm_rows, key=lambda r: (r["p_perm"], -r["observed_accuracy"]))

    m = len(sorted_holm)
    running_p = 0.0
    for k, r in enumerate(sorted_holm):
        mult = m - k
        p_raw = r["p_perm"]
        adj_p = min(1.0, p_raw * mult)
        running_p = max(running_p, adj_p)
        r["p_holm"] = round(running_p, 4)

    # Assign verdicts
    for r in test_results:
        p_eval = r["p_holm"] if (r["corpus"], r["classifier"], r["contrast"], r["feature_set"]) in holm_keys else r["p_perm"]
        is_sig = (p_eval < 0.05) and (r["observed_accuracy"] > r["null_p95"])

        if r["is_carried_by_one_arm"]:
            r["verdict"] = "carried_by_one_arm"
        elif r["is_fragile"]:
            r["verdict"] = "fragile"
        elif is_sig:
            r["verdict"] = "identifiable"
        else:
            r["verdict"] = "not_significant"

    # Write output files
    # 1. Tests CSV
    out_tests = Path(args.out_tests)
    out_tests.parent.mkdir(parents=True, exist_ok=True)
    fieldnames_tests = list(test_results[0].keys())
    with out_tests.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames_tests)
        w.writeheader()
        w.writerows(test_results)
    print(f"\nwrote {out_tests} ({len(test_results)} rows)")

    # 2. Predictions CSV
    out_preds = Path(args.out_predictions)
    with out_preds.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(all_predictions_rows[0].keys()))
        w.writeheader()
        w.writerows(all_predictions_rows)
    print(f"wrote {out_preds} ({len(all_predictions_rows)} rows)")

    # 3. Confusion CSV
    out_conf = Path(args.out_confusion)
    with out_conf.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(all_confusion_rows[0].keys()))
        w.writeheader()
        w.writerows(all_confusion_rows)
    print(f"wrote {out_conf} ({len(all_confusion_rows)} rows)")

    print("\n=== EXECUTION COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
