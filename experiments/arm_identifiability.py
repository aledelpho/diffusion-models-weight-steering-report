# -*- coding: utf-8 -*-
"""
experiments/arm_identifiability.py
===================================
Tests whether an edit leaves a recognisable signature in style feature space,
predicting the arm on prompts never seen during fitting (leave-one-prompt-out).

Governed by docs/prereg_arm_identifiability.md (2026-09-25).

Constraints:
  - Leave one whole prompt out per fold (16 folds on stage 7, 8 folds on stage 9).
    Random cross-validation is strictly forbidden.
  - Null hypothesis: label permutation within each (prompt, seed) group across
    1000 repetitions with fixed seed random.Random(1337). No binomial test.
  - Two classifiers: Nearest Centroid (Cosine) [primary], Multinomial Logistic Regression (L2, C=1.0) [secondary].
  - Checks for bias/fragility (§9):
      * carried_by_one_arm: single arm recall > 3x mean of others.
      * fragile: single fold contribution > 40% of correct predictions above chance.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from sklearn.linear_model import LogisticRegression
except ImportError:
    sys.exit("scikit-learn is required to run experiments/arm_identifiability.py")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

NOT_FEATURES = {
    "file", "width_px", "height_px", "condition", "prompt_dir", "prompt_id",
    "prompt_sha1", "seed", "rel_path", "source_manifest", "source_csv",
    "paper_hex", "ink_hex", "sw1_hex", "sw2_hex", "sw3_hex", "sw4_hex", "sw5_hex", "sw6_hex"
}

SEEDS_5 = [42, 777, 1337, 9999, 4242145]

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


def cosine_similarity(a: List[float], b: List[float]) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def holm_stepdown(ps: List[float]) -> List[float]:
    """Holm step-down procedure across a list of p-values."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out = [0.0] * len(ps)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, ps[i] * (len(ps) - rank)))
        out[i] = running
    return out


def evaluate_nearest_centroid(
    deltas: List[Dict[str, Any]],
    prompts: List[str],
    arms: List[str]
) -> Tuple[float, List[Tuple[str, str, str]], Dict[str, int], Dict[str, int]]:
    """
    Leave-one-prompt-out Nearest Centroid with Cosine similarity.
    Returns: (accuracy, predictions_tuples, fold_correct_dict, fold_total_dict)
    """
    preds: List[Tuple[str, str, str]] = []  # (prompt, true_arm, pred_arm)
    fold_correct: Dict[str, int] = {}
    fold_total: Dict[str, int] = {}

    for held_out in prompts:
        train_deltas = [d for d in deltas if d["prompt"] != held_out]
        test_deltas = [d for d in deltas if d["prompt"] == held_out]

        # Fit centroids
        centroids: Dict[str, List[float]] = {}
        for a in arms:
            a_vecs = [d["delta"] for d in train_deltas if d["arm"] == a]
            c = [statistics.fmean(v[i] for v in a_vecs) for i in range(len(a_vecs[0]))]
            centroids[a] = c

        f_corr = 0
        for td in test_deltas:
            true_a = td["arm"]
            vec = td["delta"]
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
    arms: List[str]
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

        X_train = [d["delta"] for d in train_deltas]
        y_train = [arm_to_idx[d["arm"]] for d in train_deltas]
        X_test = [d["delta"] for d in test_deltas]
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
    prompts: List[str],
    arms: List[str],
    fold_correct: Dict[str, int],
    fold_total: Dict[str, int]
) -> Dict[str, Any]:
    """
    Computes confusion matrix, per-arm recalls, and checks the two §9 criteria:
      1. carried_by_one_arm: single arm recall > 3x mean of others.
      2. fragile: single fold contribution > 40% of correct predictions above chance.
    """
    conf = Counter()
    for _, t, p in preds:
        conf[(t, p)] += 1

    recalls: Dict[str, float] = {}
    supports: Dict[str, int] = {}
    for a in arms:
        supp = sum(conf[(a, pred_a)] for pred_a in arms)
        corr = conf[(a, a)]
        recalls[a] = corr / supp if supp else 0.0
        supports[a] = supp

    # Check carried_by_one_arm
    max_arm_ratio = 0.0
    carried_arm_name = ""
    is_carried_by_one_arm = False
    for a in arms:
        rec = recalls[a]
        others = [recalls[other] for other in arms if other != a]
        mean_oth = statistics.fmean(others) if others else 0.0
        if mean_oth > 0:
            ratio = rec / mean_oth
            if ratio > max_arm_ratio:
                max_arm_ratio = ratio
                carried_arm_name = a
            if ratio > 3.0:
                is_carried_by_one_arm = True

    # Check fragile
    chance = 1.0 / len(arms)
    total_n = len(preds)
    total_correct = sum(1 for _, t, p in preds if t == p)
    total_gain = total_correct - (total_n * chance)
    max_fold_share = 0.0
    fragile_fold_name = ""
    is_fragile = False

    if total_gain > 0:
        for p in prompts:
            f_gain = fold_correct[p] - (fold_total[p] * chance)
            share = f_gain / total_gain
            if share > max_fold_share:
                max_fold_share = share
                fragile_fold_name = p
            if share > 0.40:
                is_fragile = True

    return {
        "conf": conf,
        "recalls": recalls,
        "supports": supports,
        "max_arm_ratio": max_arm_ratio,
        "carried_arm_name": carried_arm_name,
        "is_carried_by_one_arm": is_carried_by_one_arm,
        "max_fold_share": max_fold_share,
        "fragile_fold_name": fragile_fold_name,
        "is_fragile": is_fragile,
    }


def run_permutation_null(
    deltas: List[Dict[str, Any]],
    prompts: List[str],
    arms: List[str],
    eval_func: Any,
    observed_acc: float,
    n_perms: int = 1000,
    seed: int = 1337
) -> Tuple[float, float, float, float]:
    """
    Runs 1000 permutations shuffling arm labels within each (prompt, seed) group.
    Returns: (null_mean, null_p95, p_perm, p_floor)
    """
    rng = random.Random(seed)
    grouped: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}
    for d in deltas:
        grouped.setdefault((d["prompt"], d["seed"]), []).append(d)

    null_accs: List[float] = []
    hits = 0

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
                    "delta": c["delta"],
                })

        p_acc, _, _, _ = eval_func(perm_deltas, prompts, arms)
        null_accs.append(p_acc)
        if p_acc >= observed_acc - 1e-12:
            hits += 1

    null_mean = statistics.fmean(null_accs)
    null_p95 = float(statistics.quantiles(null_accs, n=100)[94])
    p_perm = hits / n_perms
    p_floor = 1.0 / n_perms

    return null_mean, null_p95, p_perm, p_floor


def load_and_standardise(
    csv_path: Path,
    target_prompts: List[str],
    baseline_prompts: List[str],
    target_arms: List[str]
) -> Tuple[List[str], List[Dict[str, Any]], Dict[str, Dict[str, float]]]:
    """
    Loads features, standardises once using the mean and std dev of that corpus's baselines,
    and constructs displacement vectors Delta = z(edited) - z(baseline) for identical (prompt, seed).
    """
    with csv_path.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    feat_cols = [c for c in rows[0].keys() if c not in NOT_FEATURES]

    # Baseline rows
    baselines = [
        r for r in rows
        if (r.get("condition") or r.get("cond_name") or r.get("arm")) == "baseline"
        and (r.get("prompt_dir") or r.get("prompt_id")) in baseline_prompts
    ]
    if not baselines:
        sys.exit(f"No baselines found in {csv_path} for prompts {baseline_prompts}")

    mu = {c: statistics.fmean(float(r[c]) for r in baselines) for c in feat_cols}
    sd = {c: statistics.stdev(float(r[c]) for r in baselines) for c in feat_cols}
    for c, s in sd.items():
        if s == 0:
            sys.exit(f"Feature {c} has zero standard deviation across baselines in {csv_path}")

    def z(r_dict: Dict[str, str]) -> List[float]:
        return [(float(r_dict[c]) - mu[c]) / sd[c] for c in feat_cols]

    base_map = {(r.get("prompt_dir") or r.get("prompt_id"), int(r["seed"])): z(r) for r in baselines}

    deltas: List[Dict[str, Any]] = []
    for r in rows:
        arm = r.get("condition") or r.get("cond_name") or r.get("arm")
        if arm not in target_arms:
            continue
        p = r.get("prompt_dir") or r.get("prompt_id")
        if p not in target_prompts:
            continue
        seed = int(r["seed"])
        if seed not in SEEDS_5:
            continue

        base_z = base_map.get((p, seed))
        if base_z is None:
            sys.exit(f"Missing paired baseline for ({p}, {seed}) in {csv_path}")

        edit_z = z(r)
        delta_vec = [edit_z[i] - base_z[i] for i in range(len(feat_cols))]

        deltas.append({
            "prompt": p,
            "seed": seed,
            "arm": arm,
            "delta": delta_vec,
        })

    # Global centroids per arm for descriptive features table
    centroids: Dict[str, Dict[str, float]] = {}
    for arm in target_arms:
        arm_vecs = [d["delta"] for d in deltas if d["arm"] == arm]
        if arm_vecs:
            centroids[arm] = {
                feat_cols[i]: statistics.fmean(v[i] for v in arm_vecs)
                for i in range(len(feat_cols))
            }

    return feat_cols, deltas, centroids


def main() -> None:
    ap = argparse.ArgumentParser(description="Arm identifiability experiment.")
    ap.add_argument("--perms", type=int, default=1000,
                    help="Number of permutations for null distribution (default: 1000)")
    ap.add_argument("--seed", type=int, default=1337,
                    help="Random seed for permutations (default: 1337)")
    ap.add_argument("--out", default=str(DATA / "arm_identifiability.csv"))
    ap.add_argument("--out-confusion", default=str(DATA / "arm_identifiability_confusion.csv"))
    ap.add_argument("--out-tests", default=str(DATA / "arm_identifiability_tests.csv"))
    ap.add_argument("--out-features", default=str(DATA / "arm_identifiability_features.csv"))
    args = ap.parse_args()

    print(f"=== ARM IDENTIFIABILITY ANALYSIS (docs/prereg_arm_identifiability.md) ===")
    print(f"Permutations: {args.perms} (seed={args.seed})")

    # 1. Load Stage 7
    s7_csv = DATA / "style_features_stage7.csv"
    if not s7_csv.exists():
        sys.exit(f"Stage 7 features missing: {s7_csv}")
    feats_s7, deltas_s7_6, centroids_s7 = load_and_standardise(
        csv_path=s7_csv,
        target_prompts=STAGE7_TEST_PROMPTS,
        baseline_prompts=[f"I{i:02d}" for i in range(1, 25)],  # All 24 stage-7 baselines
        target_arms=STAGE7_ARMS_6,
    )
    deltas_s7_2 = [d for d in deltas_s7_6 if d["arm"] in STAGE7_ARMS_2]
    print(f"Loaded Stage 7: {len(deltas_s7_6)} cells (6-class), {len(deltas_s7_2)} cells (2-class)")

    # 2. Load Stage 9
    s9_csv = DATA / "style_features_stage9.csv"
    if not s9_csv.exists():
        sys.exit(f"Stage 9 features missing: {s9_csv}")
    feats_s9, deltas_s9_6, centroids_s9 = load_and_standardise(
        csv_path=s9_csv,
        target_prompts=STAGE9_STYLE_PROMPTS,
        baseline_prompts=STAGE9_STYLE_PROMPTS,  # 8 style baselines
        target_arms=STAGE9_ARMS_6,
    )
    deltas_s9_2 = [d for d in deltas_s9_6 if d["arm"] in STAGE9_ARMS_2]
    print(f"Loaded Stage 9: {len(deltas_s9_6)} cells (6-class), {len(deltas_s9_2)} cells (2-class)")

    # Test suite configurations
    # (corpus, classifier_name, eval_func, contrast_name, arms, deltas, prompts)
    configs = [
        # Stage 7 Nearest Centroid
        ("stage7", "nearest_centroid", evaluate_nearest_centroid, "6_class", STAGE7_ARMS_6, deltas_s7_6, STAGE7_TEST_PROMPTS),
        ("stage7", "nearest_centroid", evaluate_nearest_centroid, "2_class", STAGE7_ARMS_2, deltas_s7_2, STAGE7_TEST_PROMPTS),
        # Stage 7 Logistic Regression
        ("stage7", "logistic_regression", evaluate_logistic_regression, "6_class", STAGE7_ARMS_6, deltas_s7_6, STAGE7_TEST_PROMPTS),
        ("stage7", "logistic_regression", evaluate_logistic_regression, "2_class", STAGE7_ARMS_2, deltas_s7_2, STAGE7_TEST_PROMPTS),
        # Stage 9 Nearest Centroid
        ("stage9", "nearest_centroid", evaluate_nearest_centroid, "6_class", STAGE9_ARMS_6, deltas_s9_6, STAGE9_STYLE_PROMPTS),
        ("stage9", "nearest_centroid", evaluate_nearest_centroid, "2_class", STAGE9_ARMS_2, deltas_s9_2, STAGE9_STYLE_PROMPTS),
        # Stage 9 Logistic Regression
        ("stage9", "logistic_regression", evaluate_logistic_regression, "6_class", STAGE9_ARMS_6, deltas_s9_6, STAGE9_STYLE_PROMPTS),
        ("stage9", "logistic_regression", evaluate_logistic_regression, "2_class", STAGE9_ARMS_2, deltas_s9_2, STAGE9_STYLE_PROMPTS),
    ]

    all_fold_rows: List[Dict[str, Any]] = []
    all_confusion_rows: List[Dict[str, Any]] = []
    test_results: List[Dict[str, Any]] = []

    print("\nExecuting Leave-One-Prompt-Out and 1000 Permutations per configuration...")

    for corpus, clf_name, eval_func, contrast, arms, data_subset, prompt_list in configs:
        chance = 1.0 / len(arms)
        n_cells = len(data_subset)
        n_prompts = len(prompt_list)

        # 1. Observed LOOCV
        obs_acc, preds, fold_corr, fold_tot = eval_func(data_subset, prompt_list, arms)
        diag = compute_diagnostics_and_confusion(preds, prompt_list, arms, fold_corr, fold_tot)

        # Record fold detail rows
        for p in prompt_list:
            f_corr = fold_corr[p]
            f_tot = fold_tot[p]
            f_acc = f_corr / f_tot if f_tot else 0.0
            # per-arm recall in this fold
            for a in arms:
                arm_test_cells = [x for x in preds if x[0] == p and x[1] == a]
                a_supp = len(arm_test_cells)
                a_corr = sum(1 for x in arm_test_cells if x[2] == a)
                a_rec = a_corr / a_supp if a_supp else 0.0
                all_fold_rows.append({
                    "corpus": corpus,
                    "classifier": clf_name,
                    "contrast": contrast,
                    "fold_prompt": p,
                    "arm": a,
                    "support": a_supp,
                    "correct": a_corr,
                    "recall": round(a_rec, 4),
                    "fold_accuracy": round(f_acc, 4),
                })

        # Record confusion matrix rows
        for true_a in arms:
            for pred_a in arms:
                cnt = diag["conf"][(true_a, pred_a)]
                supp = diag["supports"][true_a]
                share = cnt / supp if supp else 0.0
                all_confusion_rows.append({
                    "corpus": corpus,
                    "classifier": clf_name,
                    "contrast": contrast,
                    "true_arm": true_a,
                    "pred_arm": pred_a,
                    "count": cnt,
                    "support": supp,
                    "share_within_true": round(share, 4),
                })

        # 2. Permutation Null
        print(f"Running {args.perms} permutations for {corpus} | {clf_name} | {contrast} ...")
        null_mean, null_p95, p_perm, p_fl = run_permutation_null(
            deltas=data_subset,
            prompts=prompt_list,
            arms=arms,
            eval_func=eval_func,
            observed_acc=obs_acc,
            n_perms=args.perms,
            seed=args.seed
        )

        test_results.append({
            "corpus": corpus,
            "classifier": clf_name,
            "contrast": contrast,
            "n_classes": len(arms),
            "n_prompts": n_prompts,
            "n_cells": n_cells,
            "observed_accuracy": obs_acc,
            "chance_accuracy": chance,
            "null_mean": null_mean,
            "null_p95": null_p95,
            "p_perm": p_perm,
            "p_floor": p_fl,
            "max_arm_ratio": diag["max_arm_ratio"],
            "carried_arm_name": diag["carried_arm_name"],
            "is_carried_by_one_arm": diag["is_carried_by_one_arm"],
            "max_fold_share": diag["max_fold_share"],
            "fragile_fold_name": diag["fragile_fold_name"],
            "is_fragile": diag["is_fragile"],
        })

    # 3. Holm correction across contrasts within each (corpus, classifier)
    # Group tests by (corpus, classifier)
    grouped_tests: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for tr in test_results:
        grouped_tests.setdefault((tr["corpus"], tr["classifier"]), []).append(tr)

    for (corp, clf), rows in grouped_tests.items():
        ps = [r["p_perm"] for r in rows]
        h_ps = holm_stepdown(ps)
        for i, r in enumerate(rows):
            r["p_holm"] = h_ps[i]

            # Determine verdict (§7 & §9)
            if r["is_carried_by_one_arm"]:
                r["verdict"] = "carried_by_one_arm"
                r["details"] = f"Recall of {r['carried_arm_name']} exceeds mean of others by {r['max_arm_ratio']:.2f}x (> 3x); no claim promoted (§9)"
            elif r["is_fragile"]:
                r["verdict"] = "fragile"
                r["details"] = f"Fold {r['fragile_fold_name']} contributes {r['max_fold_share']*100:.1f}% (> 40%) of correct above chance; no claim promoted (§9)"
            elif r["observed_accuracy"] > r["null_p95"] and r["p_holm"] <= 0.05:
                r["verdict"] = "identifiable"
                r["details"] = f"Accuracy {r['observed_accuracy']:.4f} exceeds null p95 {r['null_p95']:.4f} at p_holm={r['p_holm']:.4f}; arm signature is decodable (§7)"
            else:
                r["verdict"] = "not_identifiable"
                r["details"] = f"Accuracy {r['observed_accuracy']:.4f} does not clear null threshold (p95={r['null_p95']:.4f}, p_holm={r['p_holm']:.4f}); no decodable signature in feature space"

    # Write data/arm_identifiability.csv
    out_csv = Path(args.out)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        fieldnames = [
            "corpus", "classifier", "contrast", "fold_prompt", "arm",
            "support", "correct", "recall", "fold_accuracy"
        ]
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_fold_rows)
    print(f"wrote {out_csv} ({len(all_fold_rows)} rows)")

    # Write data/arm_identifiability_confusion.csv
    out_conf = Path(args.out_confusion)
    with out_conf.open("w", newline="", encoding="utf-8") as fh:
        fieldnames = [
            "corpus", "classifier", "contrast", "true_arm", "pred_arm",
            "count", "support", "share_within_true"
        ]
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_confusion_rows)
    print(f"wrote {out_conf} ({len(all_confusion_rows)} rows)")

    # Write data/arm_identifiability_tests.csv
    out_tests = Path(args.out_tests)
    with out_tests.open("w", newline="", encoding="utf-8") as fh:
        fieldnames = [
            "corpus", "classifier", "contrast", "n_classes", "n_prompts", "n_cells",
            "observed_accuracy", "chance_accuracy", "null_mean", "null_p95",
            "p_perm", "p_floor", "p_holm", "max_arm_ratio", "is_carried_by_one_arm",
            "max_fold_share", "is_fragile", "verdict", "details"
        ]
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for r in test_results:
            w.writerow({
                "corpus": r["corpus"],
                "classifier": r["classifier"],
                "contrast": r["contrast"],
                "n_classes": r["n_classes"],
                "n_prompts": r["n_prompts"],
                "n_cells": r["n_cells"],
                "observed_accuracy": round(r["observed_accuracy"], 4),
                "chance_accuracy": round(r["chance_accuracy"], 4),
                "null_mean": round(r["null_mean"], 4),
                "null_p95": round(r["null_p95"], 4),
                "p_perm": round(r["p_perm"], 4),
                "p_floor": round(r["p_floor"], 4),
                "p_holm": round(r["p_holm"], 4),
                "max_arm_ratio": round(r["max_arm_ratio"], 2),
                "is_carried_by_one_arm": r["is_carried_by_one_arm"],
                "max_fold_share": round(r["max_fold_share"], 4),
                "is_fragile": r["is_fragile"],
                "verdict": r["verdict"],
                "details": r["details"],
            })
    print(f"wrote {out_tests} ({len(test_results)} rows)")

    # Write data/arm_identifiability_features.csv (written only if §7 returns identifiable)
    any_identifiable = any(r["verdict"] == "identifiable" for r in test_results)
    if any_identifiable:
        out_feats = Path(args.out_features)
        feature_rows: List[Dict[str, Any]] = []

        # Stage 7 descriptive centroid separation
        for feat in feats_s7:
            row = {"corpus": "stage7", "feature": feat}
            vals = [centroids_s7[a][feat] for a in STAGE7_ARMS_6]
            for a in STAGE7_ARMS_6:
                row[f"centroid_{a}"] = round(centroids_s7[a][feat], 4)
            row["min_centroid"] = round(min(vals), 4)
            row["max_centroid"] = round(max(vals), 4)
            row["spread_between_centroids"] = round(max(vals) - min(vals), 4)
            feature_rows.append(row)

        # Stage 9 descriptive centroid separation
        for feat in feats_s9:
            row = {"corpus": "stage9", "feature": feat}
            vals = [centroids_s9[a][feat] for a in STAGE9_ARMS_6]
            for a in STAGE9_ARMS_6:
                row[f"centroid_{a}"] = round(centroids_s9[a][feat], 4)
            row["min_centroid"] = round(min(vals), 4)
            row["max_centroid"] = round(max(vals), 4)
            row["spread_between_centroids"] = round(max(vals) - min(vals), 4)
            feature_rows.append(row)

        all_keys = []
        for r in feature_rows:
            for k in r.keys():
                if k not in all_keys:
                    all_keys.append(k)

        with out_feats.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=all_keys)
            w.writeheader()
            w.writerows(feature_rows)
        print(f"wrote {out_feats} ({len(feature_rows)} rows) [§7 identifiable]")
    else:
        print(f"Skipping {args.out_features} (identifiable not returned)")

    print("\n=== SUMMARY OF TESTS ===")
    for r in test_results:
        print(f"{r['corpus']:7s} | {r['classifier']:19s} | {r['contrast']:7s} | "
              f"Acc={r['observed_accuracy']:.4f} (chance={r['chance_accuracy']:.4f}, null_p95={r['null_p95']:.4f}) | "
              f"p_perm={r['p_perm']:.4f}, p_holm={r['p_holm']:.4f} | "
              f"carried={r['is_carried_by_one_arm']} (max_ratio={r['max_arm_ratio']:.2f}), "
              f"fragile={r['is_fragile']} (max_share={r['max_fold_share']*100:.1f}%) | "
              f"verdict={r['verdict']}")


if __name__ == "__main__":
    main()
