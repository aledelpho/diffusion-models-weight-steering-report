# -*- coding: utf-8 -*-
"""
experiments/palette_coherence.py
================================
Statistical evaluation of colour palette position (Track A) and palette recurrence (Track B).
Frozen in docs/prereg_palette_position.md and docs/prereg_palette_position_amendment_01.md.

Inputs:
  - data/palette_instrument_check.csv
  - data/palette_position.csv
  - data/palette_swatches.json
  - data/stage9_images.csv

Outputs:
  - data/palette_recurrence.csv (Track B metrics per arm and prompt)
  - data/palette_tests.csv (Contrasts, permutation tests, Holm correction, verdicts, N-sensitivity)
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import os
import statistics
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from skimage.color import deltaE_ciede2000

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

STYLE_PROMPTS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
ARMS = [
    "preset_pos_1x", "preset_pos_2x",
    "blockshuf_neg_1x", "blockshuf_neg_2x",
    "rand_pos_1x", "rand_pos_2x"
]
CONDITIONS = ["baseline"] + ARMS
SEEDS = [42, 777, 1337, 9999, 4242145]

CONTRASTS = [
    ("preset_pos_1x", "rand_pos_1x"),
    ("preset_pos_2x", "rand_pos_2x"),
    ("blockshuf_neg_1x", "rand_pos_1x"),
    ("blockshuf_neg_2x", "rand_pos_2x"),
]

TRACK_A_COLS = [
    "delta_mean_L", "delta_mean_a", "delta_mean_b",
    "delta_std_L", "delta_std_a", "delta_std_b",
    "delta_corr_La", "delta_corr_Lb", "delta_corr_ab"
]


def cosine(a: list[float], b: list[float]) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if not na or not nb:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def emd_ciede2000(w1: list[float], lab1: list[list[float]], w2: list[float], lab2: list[list[float]]) -> float:
    n1, n2 = len(w1), len(w2)
    l1_arr = np.array(lab1, dtype=np.float64)
    l2_arr = np.array(lab2, dtype=np.float64)

    C = np.zeros((n1, n2), dtype=np.float64)
    for i in range(n1):
        for j in range(n2):
            C[i, j] = deltaE_ciede2000(l1_arr[i].reshape(1, 1, 3), l2_arr[j].reshape(1, 1, 3))[0, 0]

    c_flat = C.flatten()
    A_eq1 = np.zeros((n1, n1 * n2))
    for i in range(n1):
        A_eq1[i, i * n2:(i + 1) * n2] = 1.0

    A_eq2 = np.zeros((n2, n1 * n2))
    for j in range(n2):
        for i in range(n1):
            A_eq2[j, i * n2 + j] = 1.0

    A_eq = np.vstack([A_eq1, A_eq2])
    b_eq = np.concatenate([w1, w2])

    res = linprog(c_flat, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if not res.success:
        raise RuntimeError(f"linprog EMD failed: {res.message}")
    return float(res.fun)


def sign_flip(diffs: list[float]) -> tuple[float, float]:
    """Exact two-tailed sign-flip permutation p-value and floor."""
    n = len(diffs)
    if n > 20:
        raise SystemExit(f"{n} pairs is too many to enumerate exactly")
    obs = abs(statistics.fmean(diffs))
    hits = sum(
        1 for s in itertools.product((1, -1), repeat=n)
        if abs(statistics.fmean(a * d for a, d in zip(s, diffs))) >= obs - 1e-12
    )
    return hits / 2 ** n, 2 / 2 ** n


def holm(ps: list[float]) -> list[float]:
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out = [0.0] * len(ps)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, ps[i] * (len(ps) - rank)))
        out[i] = running
    return out


def load_file_map() -> dict[tuple[str, str, int], str]:
    stage9_csv = DATA / "stage9_images.csv"
    if not stage9_csv.exists():
        sys.exit(f"stage9_images.csv missing: {stage9_csv}")
    with stage9_csv.open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    fmap = {}
    for r in rows:
        p = (r.get("prompt_id") or "").split("_")[0]
        arm = r.get("cond_name") or r.get("arm")
        seed = int(r["seed"])
        fn = os.path.basename(r.get("image_path") or "")
        if p in STYLE_PROMPTS and arm in CONDITIONS:
            fmap[(arm, p, seed)] = fn
    return fmap


def load_instrument_thresholds() -> tuple[float, float, float]:
    """Loads p95 floor, detection threshold (+30 deg D_pal), and delta norm p95."""
    check_csv = DATA / "palette_instrument_check.csv"
    if not check_csv.exists():
        sys.exit(f"palette_instrument_check.csv missing: {check_csv}")

    d_pal_floor_p95 = None
    detection_thresh_d_pal = None
    delta_floor_p95 = None

    with check_csv.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    for r in rows:
        cid = r.get("check_id") or ""
        if cid == "check_3_floor_D_pal_stats":
            # Details: Floor D_pal over 80 within-prompt baseline pairs: p95=5.373563
            details = r.get("details") or ""
            if "p95=" in details:
                d_pal_floor_p95 = float(details.split("p95=")[1].strip())
        elif cid == "check_3_floor_delta_norm_stats":
            details = r.get("details") or ""
            if "p95=" in details:
                delta_floor_p95 = float(details.split("p95=")[1].strip())
        elif cid == "check_4_positive_control_30deg":
            detection_thresh_d_pal = float(r["D_pal"])

    if d_pal_floor_p95 is None or detection_thresh_d_pal is None:
        sys.exit("Failed to extract p95 and detection threshold from palette_instrument_check.csv")

    return d_pal_floor_p95, detection_thresh_d_pal, delta_floor_p95 or 4.023


def compute_track_b_recurrence(swatches: dict, fmap: dict, n_tag: str) -> tuple[dict, dict, dict]:
    """Computes W(A,P), B(P), and R(A,P) for all arms and prompts."""
    # 1. Within-arm pairwise EMD across seeds: W(A, P)
    W = {}
    for a in ARMS:
        for p in STYLE_PROMPTS:
            d_list = []
            for s1, s2 in itertools.combinations(SEEDS, 2):
                fn1 = fmap[(a, p, s1)]
                fn2 = fmap[(a, p, s2)]
                d = emd_ciede2000(
                    swatches[fn1]["weights"], swatches[fn1]["lab"],
                    swatches[fn2]["weights"], swatches[fn2]["lab"]
                )
                d_list.append(d)
            W[(a, p)] = statistics.fmean(d_list)

    # 2. Between-arms pairwise EMD at identical seed: B(P)
    B = {}
    for p in STYLE_PROMPTS:
        b_list = []
        for s in SEEDS:
            for a1, a2 in itertools.combinations(ARMS, 2):
                fn1 = fmap[(a1, p, s)]
                fn2 = fmap[(a2, p, s)]
                d = emd_ciede2000(
                    swatches[fn1]["weights"], swatches[fn1]["lab"],
                    swatches[fn2]["weights"], swatches[fn2]["lab"]
                )
                b_list.append(d)
        B[p] = statistics.fmean(b_list)

    # 3. Recurrence index R(A, P) = B(P) - W(A, P)
    R = {}
    for a in ARMS:
        for p in STYLE_PROMPTS:
            R[(a, p)] = B[p] - W[(a, p)]

    return W, B, R


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate palette position and recurrence.")
    ap.add_argument("--out-rec", default=str(DATA / "palette_recurrence.csv"),
                    help="Target path for recurrence CSV")
    ap.add_argument("--out-tests", default=str(DATA / "palette_tests.csv"),
                    help="Target path for statistical tests CSV")
    args = ap.parse_args()

    # Load inputs
    fmap = load_file_map()
    floor_p95, det_thresh, delta_p95 = load_instrument_thresholds()

    swatches_path = DATA / "palette_swatches.json"
    if not swatches_path.exists():
        sys.exit(f"palette_swatches.json missing: {swatches_path}")
    with swatches_path.open(encoding="utf-8") as fh:
        swatches_data = json.load(fh)

    pos_csv = DATA / "palette_position.csv"
    if not pos_csv.exists():
        sys.exit(f"palette_position.csv missing: {pos_csv}")
    with pos_csv.open(encoding="utf-8") as fh:
        pos_rows = list(csv.DictReader(fh))

    # =========================================================================
    # STEP 1: Displacements vs Detection Threshold (+30 deg = 7.204) and p95 floor (5.374)
    # =========================================================================
    print("=== Step 1: Arm Displacements vs Detection Threshold (§5 Amendment 01) ===")
    sw15 = swatches_data["n15"]
    arm_disps_raw: dict[str, list[float]] = {a: [] for a in ARMS}
    cell_disps: dict[tuple[str, str, int], float] = {}

    for a in ARMS:
        for p in STYLE_PROMPTS:
            for s in SEEDS:
                fn_edit = fmap[(a, p, s)]
                fn_base = fmap[("baseline", p, s)]
                d = emd_ciede2000(
                    sw15[fn_edit]["weights"], sw15[fn_edit]["lab"],
                    sw15[fn_base]["weights"], sw15[fn_base]["lab"]
                )
                arm_disps_raw[a].append(d)
                cell_disps[(a, p, s)] = d

    arm_mean_disp: dict[str, float] = {}
    arm_disp_status: dict[str, str] = {}

    print(f"Floor p95 = {floor_p95:.4f}, Detection Threshold (+30 deg) = {det_thresh:.4f}\n")
    for a in ARMS:
        m = statistics.fmean(arm_disps_raw[a])
        arm_mean_disp[a] = m
        ratio_floor = m / floor_p95
        ratio_thresh = m / det_thresh
        if m < det_thresh:
            status = "uninterpretable"
        else:
            status = "interpretable"
        arm_disp_status[a] = status
        print(f"  {a:18s}: mean D_pal = {m:6.3f} (vs floor p95: {ratio_floor:5.2f}x, vs +30deg: {ratio_thresh:5.2f}x) -> {status.upper()}")

    # =========================================================================
    # STEP 2: Track B Recurrence (N=15 Primary, plus N=8 and N=24 Sensitivity)
    # =========================================================================
    print("\n=== Step 2: Track B Recurrence Analysis (N=15, 8, 24) ===")
    rec_n15_W, rec_n15_B, rec_n15_R = compute_track_b_recurrence(swatches_data["n15"], fmap, "n15")
    rec_n8_W, rec_n8_B, rec_n8_R = compute_track_b_recurrence(swatches_data["n8"], fmap, "n8")
    rec_n24_W, rec_n24_B, rec_n24_R = compute_track_b_recurrence(swatches_data["n24"], fmap, "n24")

    # Build data/palette_recurrence.csv for primary N=15
    rec_csv_rows = []
    for a in ARMS:
        for p in STYLE_PROMPTS:
            p_disp = statistics.fmean(cell_disps[(a, p, s)] for s in SEEDS)
            rec_csv_rows.append({
                "arm": a,
                "prompt": p,
                "N": 15,
                "W_within_arm": round(rec_n15_W[(a, p)], 6),
                "B_between_arms": round(rec_n15_B[p], 6),
                "R_recurrence": round(rec_n15_R[(a, p)], 6),
                "mean_D_pal_displacement": round(p_disp, 6),
                "disp_vs_floor_p95": round(p_disp / floor_p95, 4),
                "disp_vs_threshold_30deg": round(p_disp / det_thresh, 4),
                "arm_interpretability": arm_disp_status[a],
            })

    out_rec_path = Path(args.out_rec)
    out_rec_path.parent.mkdir(parents=True, exist_ok=True)
    with out_rec_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rec_csv_rows[0].keys()))
        w.writeheader()
        w.writerows(rec_csv_rows)
    print(f"wrote {out_rec_path} ({len(rec_csv_rows)} rows for N=15 primary)")

    # =========================================================================
    # STEP 3: Track A 9D Position Vector Coherence & Contrasts
    # =========================================================================
    print("\n=== Step 3: Track A 9D Coherence Analysis ===")
    delta_9d = {}
    for r in pos_rows:
        a = r["arm"]
        p = r["prompt"]
        s = int(r["seed"])
        delta_9d[(a, p, s)] = [float(r[col]) for col in TRACK_A_COLS]

    # Per-prompt within-prompt cosine across seeds
    track_a_within_p = {a: {} for a in ARMS}
    track_a_within_mean = {}
    for a in ARMS:
        for p in STYLE_PROMPTS:
            p_vecs = [delta_9d[(a, p, s)] for s in SEEDS]
            cos_pairs = [cosine(v1, v2) for v1, v2 in itertools.combinations(p_vecs, 2)]
            track_a_within_p[a][p] = statistics.fmean(cos_pairs)
        track_a_within_mean[a] = statistics.fmean(track_a_within_p[a].values())

    # Per-prompt cross-prompt mean cosine
    mean_vecs_p = {
        a: {
            p: [statistics.fmean(delta_9d[(a, p, s)][j] for s in SEEDS) for j in range(9)]
            for p in STYLE_PROMPTS
        }
        for a in ARMS
    }

    track_a_cross_p = {a: {} for a in ARMS}
    track_a_cross_mean = {}
    for a in ARMS:
        for p in STYLE_PROMPTS:
            other_cos = [cosine(mean_vecs_p[a][p], mean_vecs_p[a][p2]) for p2 in STYLE_PROMPTS if p2 != p]
            track_a_cross_p[a][p] = statistics.fmean(other_cos)
        all_cross_pairs = [
            cosine(mean_vecs_p[a][p1], mean_vecs_p[a][p2])
            for p1, p2 in itertools.combinations(STYLE_PROMPTS, 2)
        ]
        track_a_cross_mean[a] = statistics.fmean(all_cross_pairs)

    # Track A Norms
    track_a_mean_norm = {}
    for a in ARMS:
        norms = [float(r["delta_norm"]) for r in pos_rows if r["arm"] == a]
        track_a_mean_norm[a] = statistics.fmean(norms)

    for a in ARMS:
        print(f"  {a:18s}: ||Delta||={track_a_mean_norm[a]:.3f} ({track_a_mean_norm[a]/delta_p95:.2f}x null p95), "
              f"within_cos={track_a_within_mean[a]:+.3f}, cross_cos={track_a_cross_mean[a]:+.3f}")

    # =========================================================================
    # STEP 4: Formal Hypothesis Testing & Verdict Compilation
    # =========================================================================
    tests_rows = []

    # --- TRACK A TESTS (Primary Contrast: preset minus scramble on cross-prompt & within-prompt) ---
    track_a_raw_p = []
    track_a_tests_temp = []

    for a, ctrl in CONTRASTS:
        diffs_cross = [track_a_cross_p[a][p] - track_a_cross_p[ctrl][p] for p in STYLE_PROMPTS]
        diffs_within = [track_a_within_p[a][p] - track_a_within_p[ctrl][p] for p in STYLE_PROMPTS]

        pv_cross, p_floor = sign_flip(diffs_cross)
        pv_within, _ = sign_flip(diffs_within)

        track_a_raw_p.append(pv_cross)

        # Interpretability gate from Amendment 01 §5
        arm_interp = arm_disp_status[a]

        track_a_tests_temp.append({
            "track": "Track A (9D CIELAB position)",
            "contrast": f"{a} minus {ctrl}",
            "arm": a,
            "control": ctrl,
            "metric_tested": "cross_prompt_coherence",
            "N": "all_pixels",
            "mean_displacement_arm": round(arm_mean_disp[a], 4),
            "displacement_status": arm_interp,
            "mean_diff": round(statistics.fmean(diffs_cross), 4),
            "prompts_in_favour": sum(1 for d in diffs_cross if d > 0),
            "n_prompts": len(STYLE_PROMPTS),
            "p_sign_flip": round(pv_cross, 6),
            "p_floor": round(p_floor, 6),
            "within_prompt_diff": round(statistics.fmean(diffs_within), 4),
            "within_prompt_p": round(pv_within, 6),
        })

    track_a_holm = holm(track_a_raw_p)
    for t, h in zip(track_a_tests_temp, track_a_holm):
        t["p_holm"] = round(h, 6)
        if t["displacement_status"] == "uninterpretable":
            t["verdict"] = "uninterpretable"
            t["details"] = (
                f"Arm displacement ({t['mean_displacement_arm']:.3f}) falls below detection threshold (+30 deg = {det_thresh:.3f}); "
                f"test is uninterpretable per Amendment 01 §5"
            )
        else:
            if h < 0.05 and t["mean_diff"] > 0:
                t["verdict"] = "separates"
                t["details"] = "Separates from scramble beyond permutation null at Holm p < 0.05"
            else:
                t["verdict"] = "does_not_separate"
                t["details"] = "Does not separate from scramble control"
        tests_rows.append(t)

    # --- TRACK B TESTS (Primary N=15, plus Sensitivity N=8, N=24) ---
    track_b_runs = [
        (15, rec_n15_R, "primary"),
        (8, rec_n8_R, "sensitivity_N8"),
        (24, rec_n24_R, "sensitivity_N24"),
    ]

    for N_val, R_dict, run_mode in track_b_runs:
        raw_p_b = []
        tests_b_temp = []
        for a, ctrl in CONTRASTS:
            diffs_R = [R_dict[(a, p)] - R_dict[(ctrl, p)] for p in STYLE_PROMPTS]
            pv, p_floor = sign_flip(diffs_R)
            raw_p_b.append(pv)
            arm_interp = arm_disp_status[a]

            tests_b_temp.append({
                "track": f"Track B (swatch recurrence N={N_val})",
                "contrast": f"{a} minus {ctrl}",
                "arm": a,
                "control": ctrl,
                "metric_tested": f"R_recurrence_N{N_val}",
                "N": str(N_val),
                "mean_displacement_arm": round(arm_mean_disp[a], 4),
                "displacement_status": arm_interp,
                "mean_diff": round(statistics.fmean(diffs_R), 4),
                "prompts_in_favour": sum(1 for d in diffs_R if d > 0),
                "n_prompts": len(STYLE_PROMPTS),
                "p_sign_flip": round(pv, 6),
                "p_floor": round(p_floor, 6),
                "within_prompt_diff": "",
                "within_prompt_p": "",
            })

        holm_b = holm(raw_p_b)
        for t, h in zip(tests_b_temp, holm_b):
            t["p_holm"] = round(h, 6)
            if t["displacement_status"] == "uninterpretable":
                t["verdict"] = "uninterpretable"
                t["details"] = (
                    f"Arm displacement ({t['mean_displacement_arm']:.3f}) below detection threshold (+30 deg = {det_thresh:.3f}); "
                    f"test is uninterpretable per Amendment 01 §5"
                )
            else:
                if h < 0.05 and t["mean_diff"] > 0:
                    t["verdict"] = "separates"
                    t["details"] = "Separates from scramble beyond permutation null at Holm p < 0.05"
                else:
                    t["verdict"] = "does_not_separate"
                    t["details"] = "Does not separate from scramble control"
            tests_rows.append(t)

    # Save data/palette_tests.csv
    out_tests_path = Path(args.out_tests)
    out_tests_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "track", "contrast", "arm", "control", "metric_tested", "N",
        "mean_displacement_arm", "displacement_status", "mean_diff",
        "prompts_in_favour", "n_prompts", "p_sign_flip", "p_floor",
        "within_prompt_diff", "within_prompt_p",
        "p_holm", "verdict", "details"
    ]
    with out_tests_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(tests_rows)
    print(f"wrote {out_tests_path} ({len(tests_rows)} contrast tests and sensitivity rows)")

    print("\n=== SUMMARY OF TESTS ===")
    for t in tests_rows:
        print(f"[{t['track']:30s}] {t['contrast']:32s} diff={t['mean_diff']:+.4f} ({t['prompts_in_favour']}/{t['n_prompts']} favour) "
              f"pHolm={t['p_holm']:.5f} -> {t['verdict'].upper()}")


if __name__ == "__main__":
    main()
