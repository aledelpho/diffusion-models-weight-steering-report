# -*- coding: utf-8 -*-
"""
experiments/measure_palette.py
==============================
Measures colour palette position (Track A) and palette recurrence (Track B).
Frozen in docs/prereg_palette_position.md (2026-09-25).

Input:
  - data/stage9_images.csv (prompts S1..S8, 5 seeds, baseline + 6 arms = 280 renders).

Outputs:
  - data/palette_instrument_check.csv (mandatory §5 checks, run and written first)
  - data/palette_position.csv (Track A 9D position vectors and Delta per cell)
  - data/palette_swatches_n15.json (Track B palettes for N=15, 8, 24)
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.optimize import linprog
from skimage.color import deltaE_ciede2000, rgb2lab

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

ROOTS = [
    Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"),
    Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output"),
    Path(r"c:\Users\aless\Desktop\comfyui-pilot"),
]

STYLE_PROMPTS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
STAGE9_ARMS = [
    "preset_pos_1x", "preset_pos_2x",
    "blockshuf_neg_1x", "blockshuf_neg_2x",
    "rand_pos_1x", "rand_pos_2x"
]
CONDITIONS = ["baseline"] + STAGE9_ARMS
SEEDS = [42, 777, 1337, 9999, 4242145]


def find_on_disk(rel_path: str, bench_folder: str = "benchmark_stage9") -> Path | None:
    fn = os.path.basename(rel_path.replace("\\", "/"))
    bench_candidates = [bench_folder, "benchmark_stage7a", "benchmark_stage7", "benchmark_stage9"]
    for r in ROOTS:
        c1 = r / rel_path
        if c1.is_file():
            return c1
        for bf in bench_candidates:
            c2 = r / bf / rel_path
            if c2.is_file():
                return c2
            c3 = r / bf / "renders" / fn
            if c3.is_file():
                return c3
            d = r / bf
            if d.is_dir():
                matches = list(d.glob(f"**/{fn}"))
                if matches:
                    return matches[0]
    return None


def extract_track_a(im: Image.Image) -> list[float]:
    """Track A: 9D colour position vector over all pixels in CIELAB."""
    arr = np.array(im, dtype=np.float32) / 255.0
    lab = rgb2lab(arr)
    L = lab[:, :, 0].flatten()
    a = lab[:, :, 1].flatten()
    b = lab[:, :, 2].flatten()

    mL, ma, mb = float(np.mean(L)), float(np.mean(a)), float(np.mean(b))
    sL, sa, sb = float(np.std(L, ddof=1)), float(np.std(a, ddof=1)), float(np.std(b, ddof=1))

    rLa = float(np.corrcoef(L, a)[0, 1]) if sL > 0 and sa > 0 else 0.0
    rLb = float(np.corrcoef(L, b)[0, 1]) if sL > 0 and sb > 0 else 0.0
    rab = float(np.corrcoef(a, b)[0, 1]) if sa > 0 and sb > 0 else 0.0

    return [mL, ma, mb, sL, sa, sb, rLa, rLb, rab]


def quantize_palette(im: Image.Image, n: int = 15) -> tuple[list[int], list[float], list[list[float]]]:
    """Track B: Median cut quantization, CIEDE2000 Lab coordinates, and pixel weights."""
    q = im.quantize(colors=n, method=Image.Quantize.MEDIANCUT, kmeans=0, dither=Image.Dither.NONE)
    palette_raw = q.getpalette()[:n * 3]
    rgb_swatches = np.array([palette_raw[i * 3:(i + 1) * 3] for i in range(n)], dtype=np.float32) / 255.0
    lab_swatches = rgb2lab(rgb_swatches.reshape(1, n, 3))[0].tolist()

    counts = np.bincount(np.array(q).flatten(), minlength=n)[:n]
    total = counts.sum()
    weights = (counts.astype(np.float64) / total).tolist() if total > 0 else [1.0 / n] * n

    return palette_raw, weights, lab_swatches


def emd_ciede2000(w1: list[float], lab1: list[list[float]], w2: list[float], lab2: list[list[float]]) -> float:
    """Exact Earth Mover's Distance under CIEDE2000 ground metric via HiGHS linear program."""
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


def run_instrument_check(baseline_renders: dict[tuple[str, int], dict], out_path: Path) -> dict:
    """Executes the mandatory instrument checks from §5 as amended by Amendment 01."""
    print("=== Running Mandatory Instrument Checks (§5 - Amendment 01) ===")
    prompts = sorted(list({p for (p, s) in baseline_renders}))
    print(f"Baselines provided: {len(baseline_renders)} renders across {len(prompts)} prompts: {prompts[:6]}...")

    # Pre-extract Track A and Track B for all baseline renders
    print(f"Pre-extracting features for {len(baseline_renders)} baseline renders...")
    base_data = {}
    for (p, s), info in sorted(baseline_renders.items()):
        im = Image.open(info["path"]).convert("RGB")
        v = extract_track_a(im)
        pal, w, lab = quantize_palette(im, 15)
        base_data[(p, s)] = {
            "im": im,
            "v": v,
            "pal": pal,
            "w": w,
            "lab": lab,
            "file": info["file"],
        }

    # Check 1: Determinism (run twice on first prompt seed 42)
    p0 = prompts[0]
    p0_42_im = base_data[(p0, 42)]["im"]
    pal_a, w_a, lab_a = quantize_palette(p0_42_im, 15)
    pal_b, w_b, lab_b = quantize_palette(p0_42_im, 15)
    det_pass = (pal_a == pal_b) and (w_a == w_b) and (lab_a == lab_b)
    if not det_pass:
        sys.exit("FATAL: Check 1 (Determinism) failed! Palettes differ on identical run.")

    # Check 2: Zero on identity
    v42_a = extract_track_a(p0_42_im)
    v42_b = extract_track_a(p0_42_im)
    d_pal_id = emd_ciede2000(w_a, lab_a, w_b, lab_b)
    id_pass = (d_pal_id == 0.0) and (v42_a == v42_b)
    if not id_pass:
        sys.exit(f"FATAL: Check 2 (Zero on identity) failed: D_pal={d_pal_id}, v_equal={v42_a == v42_b}")

    print("Check 1 (Determinism)      : PASS (palettes and weights byte-identical)")
    print(f"Check 2 (Zero on identity) : PASS (D_pal = {d_pal_id:.6f}, 9D vectors equal)")

    # §2. §5.3 Replaced: Noise floor distribution across all within-prompt baseline pairs
    pair_rows = []
    floor_d_pal_list = []
    floor_delta_list = []

    expected_pairs = len(prompts) * 10
    print(f"Computing noise floor over {expected_pairs} within-prompt baseline pairs...")
    for p in prompts:
        seeds_p = sorted(SEEDS)
        for i in range(len(seeds_p)):
            for j in range(i + 1, len(seeds_p)):
                s1, s2 = seeds_p[i], seeds_p[j]
                b1 = base_data[(p, s1)]
                b2 = base_data[(p, s2)]
                d_pal = emd_ciede2000(b1["w"], b1["lab"], b2["w"], b2["lab"])
                delta_vec = [x - y for x, y in zip(b1["v"], b2["v"])]
                delta_norm = math.sqrt(sum(x * x for x in delta_vec))

                floor_d_pal_list.append(d_pal)
                floor_delta_list.append(delta_norm)

                pair_rows.append({
                    "record_type": "floor_pair",
                    "check_id": "check_3_floor_distribution",
                    "prompt": p,
                    "seed_pair": f"{s1}_vs_{s2}",
                    "angle_deg": "",
                    "metric_name": "within_prompt_baseline_pair",
                    "D_pal": f"{d_pal:.6f}",
                    "delta_norm": f"{delta_norm:.6f}",
                    "delta_a": "",
                    "delta_b": "",
                    "ratio_to_p95": "",
                    "status": "RECORDED",
                    "details": f"Baseline pair for prompt {p}"
                })

    assert len(floor_d_pal_list) == expected_pairs, f"Expected {expected_pairs} baseline pairs, got {len(floor_d_pal_list)}"

    d_pal_mean = float(np.mean(floor_d_pal_list))
    d_pal_sd = float(np.std(floor_d_pal_list, ddof=1))
    d_pal_median = float(np.median(floor_d_pal_list))
    d_pal_p95 = float(np.percentile(floor_d_pal_list, 95))
    d_pal_max = float(np.max(floor_d_pal_list))

    delta_mean = float(np.mean(floor_delta_list))
    delta_sd = float(np.std(floor_delta_list, ddof=1))
    delta_median = float(np.median(floor_delta_list))
    delta_p95 = float(np.percentile(floor_delta_list, 95))
    delta_max = float(np.max(floor_delta_list))

    print(f"Check 3 (Floor D_pal)      : mean={d_pal_mean:.4f}, sd={d_pal_sd:.4f}, median={d_pal_median:.4f}, p95={d_pal_p95:.4f}, max={d_pal_max:.4f}")
    print(f"Check 3 (Floor ||Delta||)  : mean={delta_mean:.4f}, sd={delta_sd:.4f}, median={delta_median:.4f}, p95={delta_p95:.4f}, max={delta_max:.4f}")

    # §3. §5.4 Replaced: Positive control sensitivity curve (+10, +30, +90, +180 deg) on at least 8 baselines
    ctrl_prompts = prompts[:8]
    print(f"Computing positive control sensitivity curve on {len(ctrl_prompts)} baselines ({ctrl_prompts[0]}..{ctrl_prompts[-1]}, seed 42)...")
    angles = [10, 30, 90, 180]
    curve_data = {a: {"d_pal": [], "delta_a": [], "delta_b": []} for a in angles}

    for p in ctrl_prompts:
        b = base_data[(p, 42)]
        im_orig = b["im"]
        v_orig = b["v"]
        w_orig, lab_orig = b["w"], b["lab"]

        hsv = cv2.cvtColor(np.array(im_orig), cv2.COLOR_RGB2HSV)

        for theta in angles:
            hsv_rot = hsv.copy()
            # 1 unit in OpenCV HSV hue = 2 degrees
            hue_shift = int(round(theta / 2.0))
            hsv_rot[:, :, 0] = (hsv_rot[:, :, 0].astype(int) + hue_shift) % 180
            im_rot = Image.fromarray(cv2.cvtColor(hsv_rot, cv2.COLOR_HSV2RGB))
            v_rot = extract_track_a(im_rot)
            _, w_rot, lab_rot = quantize_palette(im_rot, 15)

            d_pal_rot = emd_ciede2000(w_orig, lab_orig, w_rot, lab_rot)
            da = abs(v_rot[1] - v_orig[1])
            db = abs(v_rot[2] - v_orig[2])

            curve_data[theta]["d_pal"].append(d_pal_rot)
            curve_data[theta]["delta_a"].append(da)
            curve_data[theta]["delta_b"].append(db)

    curve_summary = []
    detection_threshold = None

    for theta in angles:
        mean_d = float(np.mean(curve_data[theta]["d_pal"]))
        mean_da = float(np.mean(curve_data[theta]["delta_a"]))
        mean_db = float(np.mean(curve_data[theta]["delta_b"]))
        ratio = mean_d / d_pal_p95 if d_pal_p95 > 0 else 0.0

        if detection_threshold is None and mean_d > d_pal_p95:
            detection_threshold = theta

        status_angle = "CLEARS_P95" if mean_d > d_pal_p95 else "BELOW_P95"
        curve_summary.append({
            "theta": theta,
            "mean_d_pal": mean_d,
            "mean_delta_a": mean_da,
            "mean_delta_b": mean_db,
            "ratio_to_p95": ratio,
            "status": status_angle,
        })
        print(f"Check 4 (Pos Control +{theta:3d} deg): D_pal={mean_d:.4f}, |da|={mean_da:.4f}, |db|={mean_db:.4f}, ratio_to_p95={ratio:.2f}x ({status_angle})")

    det_thresh_str = f"+{detection_threshold} deg" if detection_threshold is not None else "NONE (>180 deg)"
    print(f"Detection Threshold (min angle > p95) : {det_thresh_str}")

    # Check requirement: +180 deg rotation must exceed p95 by at least 1.5x
    mean_180 = [c for c in curve_summary if c["theta"] == 180][0]
    ratio_180 = mean_180["ratio_to_p95"]
    instrument_pass = (ratio_180 >= 1.5)

    verdict_str = "PASS" if instrument_pass else "FAIL_INSTRUMENT_INSUFFICIENT"
    print(f"Instrument Check Verdict: {verdict_str} (ratio_180 = {ratio_180:.3f} >= 1.5: {instrument_pass})")

    # Assemble all CSV rows
    csv_rows = []
    # Check 1
    csv_rows.append({
        "record_type": "check_summary",
        "check_id": "check_1_determinism",
        "prompt": p0,
        "seed_pair": "42_vs_42",
        "angle_deg": "",
        "metric_name": "quantization_determinism",
        "D_pal": "0.0",
        "delta_norm": "0.0",
        "delta_a": "0.0",
        "delta_b": "0.0",
        "ratio_to_p95": "",
        "status": "PASS",
        "details": f"Two runs on {p0} seed 42 yielded byte-identical palettes and weights"
    })
    # Check 2
    csv_rows.append({
        "record_type": "check_summary",
        "check_id": "check_2_zero_on_identity",
        "prompt": p0,
        "seed_pair": "42_vs_42",
        "angle_deg": "",
        "metric_name": "zero_on_identity",
        "D_pal": f"{d_pal_id:.6f}",
        "delta_norm": "0.0",
        "delta_a": "0.0",
        "delta_b": "0.0",
        "ratio_to_p95": "",
        "status": "PASS",
        "details": "D_pal == 0.0 and identical 9D vectors on identical render"
    })
    # Check 3 Distribution summaries
    csv_rows.append({
        "record_type": "floor_summary",
        "check_id": "check_3_floor_D_pal_stats",
        "prompt": f"ALL_{len(prompts)}_PROMPTS",
        "seed_pair": f"{len(floor_d_pal_list)}_PAIRS",
        "angle_deg": "",
        "metric_name": "D_pal_distribution",
        "D_pal": f"mean={d_pal_mean:.6f};sd={d_pal_sd:.6f};median={d_pal_median:.6f};p95={d_pal_p95:.6f};max={d_pal_max:.6f}",
        "delta_norm": "",
        "delta_a": "",
        "delta_b": "",
        "ratio_to_p95": "1.000000",
        "status": "RECORDED",
        "details": f"Floor D_pal over {len(floor_d_pal_list)} within-prompt baseline pairs: p95={d_pal_p95:.6f}"
    })
    csv_rows.append({
        "record_type": "floor_summary",
        "check_id": "check_3_floor_delta_norm_stats",
        "prompt": f"ALL_{len(prompts)}_PROMPTS",
        "seed_pair": f"{len(floor_d_pal_list)}_PAIRS",
        "angle_deg": "",
        "metric_name": "delta_norm_distribution",
        "D_pal": "",
        "delta_norm": f"mean={delta_mean:.6f};sd={delta_sd:.6f};median={delta_median:.6f};p95={delta_p95:.6f};max={delta_max:.6f}",
        "delta_a": "",
        "delta_b": "",
        "ratio_to_p95": "",
        "status": "RECORDED",
        "details": f"Floor raw 9D delta norm over {len(floor_d_pal_list)} within-prompt baseline pairs: p95={delta_p95:.6f}"
    })
    # Check 4 Sensitivity curve summaries
    for c in curve_summary:
        csv_rows.append({
            "record_type": "sensitivity_curve",
            "check_id": f"check_4_positive_control_{c['theta']}deg",
            "prompt": f"{len(ctrl_prompts)}_BASELINES_{ctrl_prompts[0]}_{ctrl_prompts[-1]}",
            "seed_pair": "seed42_rotated",
            "angle_deg": str(c["theta"]),
            "metric_name": "hue_rotation_sensitivity",
            "D_pal": f"{c['mean_d_pal']:.6f}",
            "delta_norm": "",
            "delta_a": f"{c['mean_delta_a']:.6f}",
            "delta_b": f"{c['mean_delta_b']:.6f}",
            "ratio_to_p95": f"{c['ratio_to_p95']:.6f}",
            "status": c["status"],
            "details": f"Hue +{c['theta']} deg mean D_pal={c['mean_d_pal']:.4f}, ratio to p95={c['ratio_to_p95']:.2f}x"
        })
    # Detection threshold & final verdict
    csv_rows.append({
        "record_type": "threshold_verdict",
        "check_id": "detection_threshold",
        "prompt": "ALL",
        "seed_pair": "",
        "angle_deg": str(detection_threshold) if detection_threshold is not None else "",
        "metric_name": "smallest_angle_clearing_p95",
        "D_pal": "",
        "delta_norm": "",
        "delta_a": "",
        "delta_b": "",
        "ratio_to_p95": "",
        "status": "RECORDED",
        "details": f"Smallest angle that clears floor p95: {det_thresh_str}"
    })
    csv_rows.append({
        "record_type": "final_verdict",
        "check_id": "instrument_check_verdict",
        "prompt": "ALL",
        "seed_pair": "",
        "angle_deg": "180",
        "metric_name": "ratio_180deg_to_p95_ge_1.5",
        "D_pal": f"{mean_180['mean_d_pal']:.6f}",
        "delta_norm": "",
        "delta_a": "",
        "delta_b": "",
        "ratio_to_p95": f"{ratio_180:.6f}",
        "status": verdict_str,
        "details": f"PASS requires ratio_180 >= 1.5; observed {ratio_180:.3f}"
    })

    # Include all 80 pairs
    csv_rows.extend(pair_rows)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "record_type", "check_id", "prompt", "seed_pair", "angle_deg",
        "metric_name", "D_pal", "delta_norm", "delta_a", "delta_b",
        "ratio_to_p95", "status", "details"
    ]
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_rows)
    print(f"wrote {out_path} ({len(csv_rows)} rows: summaries, curve, and {len(floor_d_pal_list)} baseline pairs)")

    return {
        "d_pal_p95": d_pal_p95,
        "delta_p95": delta_p95,
        "floor_d_pal": d_pal_p95,
        "floor_delta_vec": delta_p95,
        "d_pal_mean": d_pal_mean,
        "d_pal_sd": d_pal_sd,
        "d_pal_median": d_pal_median,
        "d_pal_max": d_pal_max,
        "curve_summary": curve_summary,
        "detection_threshold": detection_threshold,
        "ratio_180": ratio_180,
        "instrument_pass": instrument_pass,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Measure colour palette position and recurrence.")
    ap.add_argument("--stage", type=int, choices=[7, 9], default=9, help="Stage to analyze (7 or 9)")
    ap.add_argument("--check-only", action="store_true", help="Run only the §5 instrument checks and stop")
    ap.add_argument("--out-check", default=None,
                    help="Target path for instrument check CSV")
    ap.add_argument("--out-pos", default=str(DATA / "palette_position.csv"),
                    help="Target path for Track A position CSV")
    ap.add_argument("--out-palettes", default=str(DATA / "palette_swatches.json"),
                    help="Target path for Track B swatches JSON")
    args = ap.parse_args()

    if args.stage == 7:
        stage7_csv = DATA / "stage7a_images.csv"
        if not stage7_csv.exists():
            sys.exit(f"stage7a_images.csv missing: {stage7_csv}")
        with stage7_csv.open(encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))

        out_check_path = Path(args.out_check) if args.out_check else DATA / "palette_instrument_check_stage7.csv"

        baseline_renders = {}
        missing = []
        for r in rows:
            if (r.get("cond_name") or r.get("arm")) != "baseline":
                continue
            p = r.get("prompt_id") or ""
            seed = int(r["seed"])
            rel = r.get("image_path") or ""
            fn = os.path.basename(rel)
            p_disk = find_on_disk(rel, "benchmark_stage7a")
            if not p_disk:
                missing.append(fn)
                continue
            baseline_renders[(p, seed)] = {
                "arm": "baseline",
                "prompt": p,
                "seed": seed,
                "file": fn,
                "path": p_disk,
            }
        if missing:
            sys.exit(f"FATAL: Missing {len(missing)} stage 7 baseline renders: {missing[:5]}")
        if len(baseline_renders) != 120:
            sys.exit(f"FATAL: Expected 120 stage 7 baseline renders, got {len(baseline_renders)}")

        check_results = run_instrument_check(baseline_renders, out_check_path)
        if args.check_only:
            sys.exit(0)

        # Stage 7 Track A: load 480 edited renders from stage7b_images.csv
        stage7b_csv = DATA / "stage7b_images.csv"
        if not stage7b_csv.exists():
            sys.exit(f"stage7b_images.csv missing: {stage7b_csv}")
        with stage7b_csv.open(encoding="utf-8-sig") as fh:
            rows_7b = list(csv.DictReader(fh))

        stage7_arms = ["preset_pos", "preset_neg", "blockshuf_pos", "blockshuf_neg", "rand_pos", "rand_neg"]
        stage7_prompts = [
            "I01", "I02", "I05", "I06", "I07", "I09", "I10", "I11",
            "I12", "I16", "I17", "I18", "I20", "I21", "I23", "I24"
        ]

        renders_7 = {}
        # Include baselines in renders_7
        for k, b_info in baseline_renders.items():
            renders_7[("baseline", b_info["prompt"], b_info["seed"])] = b_info

        missing_7 = []
        for r in rows_7b:
            p = r.get("prompt_id") or ""
            if p not in stage7_prompts:
                continue
            arm = r.get("cond_name") or r.get("arm")
            if arm not in stage7_arms:
                continue
            seed = int(r["seed"])
            rel = r.get("image_path") or ""
            fn = os.path.basename(rel)
            p_disk = find_on_disk(rel, "benchmark_stage7")
            if not p_disk:
                missing_7.append(fn)
                continue
            renders_7[(arm, p, seed)] = {
                "arm": arm,
                "prompt": p,
                "seed": seed,
                "file": fn,
                "path": p_disk,
            }

        if missing_7:
            sys.exit(f"FATAL: Missing {len(missing_7)} stage 7 edited renders: {missing_7[:5]}")

        expected_total = 120 + 480  # 120 baselines + 480 edited
        if len(renders_7) != expected_total:
            sys.exit(f"FATAL: Expected {expected_total} stage 7 renders, found {len(renders_7)}")

        print(f"\nExtracting Track A CIELAB positions for {len(renders_7)} stage 7 renders...")
        track_a_cols = ["mean_L", "mean_a", "mean_b", "std_L", "std_a", "std_b", "corr_La", "corr_Lb", "corr_ab"]

        for i, (key, info) in enumerate(sorted(renders_7.items())):
            im = Image.open(info["path"]).convert("RGB")
            info["v9"] = extract_track_a(im)
            if (i + 1) % 100 == 0:
                print(f"  [{i+1}/{len(renders_7)}] renders extracted...")

        # Standardise on stage-7 baselines only
        baselines_info_7 = [info for (arm, p, s), info in renders_7.items() if arm == "baseline"]
        mu_7 = [statistics.fmean(b["v9"][j] for b in baselines_info_7) for j in range(9)]
        sd_7 = [statistics.stdev(b["v9"][j] for b in baselines_info_7) for j in range(9)]
        for j, s in enumerate(sd_7):
            if s == 0:
                sys.exit(f"Stage 7 Track A feature {track_a_cols[j]} has 0 standard deviation across baselines")

        def z_A7(v: list[float]) -> list[float]:
            return [(v[j] - mu_7[j]) / sd_7[j] for j in range(9)]

        for info in renders_7.values():
            info["z9"] = z_A7(info["v9"])

        delta_rows_7 = []
        base_map_7 = {(info["prompt"], info["seed"]): info for info in baselines_info_7}

        for (arm, p, s), info in sorted(renders_7.items()):
            if arm == "baseline":
                continue
            base_pair = base_map_7[(p, s)]
            delta_vec = [x - y for x, y in zip(info["z9"], base_pair["z9"])]
            delta_norm = math.sqrt(sum(x * x for x in delta_vec))

            r_dict = {
                "file": info["file"],
                "arm": arm,
                "prompt": p,
                "seed": s,
                "delta_norm": round(delta_norm, 6),
            }
            for j, col in enumerate(track_a_cols):
                r_dict[f"delta_{col}"] = round(delta_vec[j], 6)
            delta_rows_7.append(r_dict)

        out_pos_7 = Path(args.out_pos) if args.out_pos != str(DATA / "palette_position.csv") else DATA / "palette_position_stage7.csv"
        out_pos_7.parent.mkdir(parents=True, exist_ok=True)
        with out_pos_7.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(delta_rows_7[0].keys()))
            w.writeheader()
            w.writerows(delta_rows_7)
        print(f"wrote {out_pos_7} ({len(delta_rows_7)} cells)")
        sys.exit(0)

    # Locate the 280 renders in stage9_images.csv
    out_check_path = Path(args.out_check) if args.out_check else DATA / "palette_instrument_check.csv"
    stage9_csv = DATA / "stage9_images.csv"
    if not stage9_csv.exists():
        sys.exit(f"stage9_images.csv missing: {stage9_csv}")

    with stage9_csv.open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    renders: dict[tuple[str, str, int], dict] = {}
    missing: list[str] = []

    for r in rows:
        raw_p = r.get("prompt_id") or ""
        p = raw_p.split("_")[0]
        if p not in STYLE_PROMPTS:
            continue
        arm = r.get("cond_name") or r.get("arm")
        if arm not in CONDITIONS:
            continue
        seed = int(r["seed"])

        rel = r.get("image_path") or ""
        fn = os.path.basename(rel)
        p_disk = find_on_disk(rel, "benchmark_stage9")
        if not p_disk:
            missing.append(fn)
            continue
        renders[(arm, p, seed)] = {
            "arm": arm,
            "prompt": p,
            "seed": seed,
            "file": fn,
            "path": p_disk,
        }

    if missing:
        sys.exit(f"FATAL: Missing {len(missing)} stage 9 renders on disk: {missing[:5]}")

    if len(renders) != 280:
        sys.exit(f"FATAL: Expected 280 stage 9 renders, found {len(renders)}")

    # 1. Run mandatory §5 instrument checks first (as amended by Amendment 01)
    baseline_renders = {
        (info["prompt"], info["seed"]): info
        for (arm, p, s), info in renders.items()
        if arm == "baseline"
    }
    check_results = run_instrument_check(baseline_renders, out_check_path)

    if args.check_only:
        sys.exit(0)

    # 2. Extract full Track A and Track B for all 280 renders
    print(f"\nExtracting Track A and Track B for all {len(renders)} renders...")
    pos_raw_rows = []
    palettes_n15: dict[str, dict] = {}
    palettes_n8: dict[str, dict] = {}
    palettes_n24: dict[str, dict] = {}

    track_a_cols = ["mean_L", "mean_a", "mean_b", "std_L", "std_a", "std_b", "corr_La", "corr_Lb", "corr_ab"]

    for i, (key, info) in enumerate(sorted(renders.items())):
        im = Image.open(info["path"]).convert("RGB")
        v9 = extract_track_a(im)
        info["v9"] = v9

        # Quantize N=15 (primary)
        pal15, w15, lab15 = quantize_palette(im, 15)
        palettes_n15[info["file"]] = {"weights": w15, "lab": lab15, "palette_rgb": pal15}

        # Quantize N=8 (sensitivity)
        pal8, w8, lab8 = quantize_palette(im, 8)
        palettes_n8[info["file"]] = {"weights": w8, "lab": lab8, "palette_rgb": pal8}

        # Quantize N=24 (sensitivity)
        pal24, w24, lab24 = quantize_palette(im, 24)
        palettes_n24[info["file"]] = {"weights": w24, "lab": lab24, "palette_rgb": pal24}

        row_dict = {
            "file": info["file"],
            "arm": info["arm"],
            "prompt": info["prompt"],
            "seed": info["seed"],
        }
        for idx, col in enumerate(track_a_cols):
            row_dict[col] = round(v9[idx], 6)
        pos_raw_rows.append(row_dict)

        if (i + 1) % 40 == 0:
            print(f"  [{i+1}/{len(renders)}] renders extracted...")

    # Standardise Track A on stage-9 baselines only
    baselines_info = [info for (arm, p, s), info in renders.items() if arm == "baseline"]
    mu_9 = [statistics.fmean(b["v9"][j] for b in baselines_info) for j in range(9)]
    sd_9 = [statistics.stdev(b["v9"][j] for b in baselines_info) for j in range(9)]
    for j, s in enumerate(sd_9):
        if s == 0:
            sys.exit(f"Track A feature {track_a_cols[j]} has 0 standard deviation across baselines")

    def z_A(v: list[float]) -> list[float]:
        return [(v[j] - mu_9[j]) / sd_9[j] for j in range(9)]

    for info in renders.values():
        info["z9"] = z_A(info["v9"])

    # Compute paired Delta for all edited cells
    delta_rows = []
    base_map = {(info["prompt"], info["seed"]): info for info in baselines_info}
    floor_vec = check_results["floor_delta_vec"]

    for (arm, p, s), info in sorted(renders.items()):
        if arm == "baseline":
            continue
        base_pair = base_map[(p, s)]
        delta_vec = [x - y for x, y in zip(info["z9"], base_pair["z9"])]
        delta_norm = math.sqrt(sum(x * x for x in delta_vec))

        r_dict = {
            "file": info["file"],
            "arm": arm,
            "prompt": p,
            "seed": s,
            "delta_norm": round(delta_norm, 6),
        }
        for j, col in enumerate(track_a_cols):
            r_dict[f"delta_{col}"] = round(delta_vec[j], 6)
        delta_rows.append(r_dict)

    # Write data/palette_position.csv
    out_pos = Path(args.out_pos)
    out_pos.parent.mkdir(parents=True, exist_ok=True)
    with out_pos.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(delta_rows[0].keys()))
        w.writeheader()
        w.writerows(delta_rows)
    print(f"wrote {out_pos} ({len(delta_rows)} cells)")

    # Save palettes JSON for Track B analysis
    out_pal = Path(args.out_palettes)
    pal_data = {
        "n15": palettes_n15,
        "n8": palettes_n8,
        "n24": palettes_n24,
    }
    with out_pal.open("w", encoding="utf-8") as fh:
        json.dump(pal_data, fh)
    print(f"wrote {out_pal} (palettes for N=15, 8, 24)")


if __name__ == "__main__":
    main()
