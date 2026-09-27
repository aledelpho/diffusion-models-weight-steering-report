# -*- coding: utf-8 -*-
"""
experiments/evaluate_colour_object_sweep.py
==========================================
Evaluates Stage 2 block sweep renders with 3 arms (LP, LG, LN)
against frozen pre-registered criteria.
Governed by:
  - docs/prereg_colour_object_dissociation.md
  - docs/RENDERS_2026-09-27_colour_object_pilot.md (§3, §4)
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RENDERS_DIR = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_colour_binding\renders")
MEAS_CSV = DATA_DIR / "colour_object_sweep_measurements.csv"
VERDICT_CSV = DATA_DIR / "colour_object_sweep_verdict.csv"

SEEDS = [42, 777, 1337]
BLOCKS = ["Block_1", "Block_2", "Block_3", "Block_4", "Block_5", "Block_6"]
SIGNS = ["pos", "neg"]
PROMPTS = ["LP", "LG", "LN"]
DEFAULT_DOSE = 0.200

GREEN_HUE_MIN = 65.0
GREEN_HUE_MAX = 120.0
AUTUMN_HUE_MIN = 20.0
AUTUMN_HUE_MAX = 55.0


def circular_diff(deg_a: float, deg_b: float) -> float:
    """Returns signed shortest angular distance from b to a in [-180, 180]."""
    diff = (deg_a - deg_b + 180.0) % 360.0 - 180.0
    return diff


def rgb_to_hsv_np(arr: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rgb = arr.astype(np.float32) / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin

    hue = np.zeros_like(cmax)
    mask_r = (cmax == r) & (delta > 1e-5)
    hue[mask_r] = (60.0 * ((g[mask_r] - b[mask_r]) / delta[mask_r]) + 360.0) % 360.0
    mask_g = (cmax == g) & (delta > 1e-5)
    hue[mask_g] = (60.0 * ((b[mask_g] - r[mask_g]) / delta[mask_g]) + 120.0) % 360.0
    mask_b = (cmax == b) & (delta > 1e-5)
    hue[mask_b] = (60.0 * ((r[mask_b] - g[mask_b]) / delta[mask_b]) + 240.0) % 360.0

    sat = np.zeros_like(cmax)
    mask_cmax = cmax > 1e-5
    sat[mask_cmax] = delta[mask_cmax] / cmax[mask_cmax]

    val = cmax
    return hue, sat, val


def analyze_image(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing render file: {path}")

    img = Image.open(path).convert("RGB")
    arr = np.array(img)
    hue, sat, val = rgb_to_hsv_np(arr)

    fg_mask = (sat > 0.15) & (val > 0.08) & (val < 0.98)
    fg_pixel_count = int(np.sum(fg_mask))
    total_pixels = arr.shape[0] * arr.shape[1]
    fg_share = fg_pixel_count / total_pixels

    if fg_pixel_count < 1000:
        h, w = arr.shape[:2]
        center_mask = np.zeros((h, w), dtype=bool)
        center_mask[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4] = True
        fg_mask = center_mask & (sat > 0.10)
        fg_pixel_count = int(np.sum(fg_mask))

    fg_hues = hue[fg_mask]

    rads = np.deg2rad(fg_hues)
    sin_mean = np.mean(np.sin(rads))
    cos_mean = np.mean(np.cos(rads))
    mean_hue_deg = float(np.rad2deg(np.arctan2(sin_mean, cos_mean)) % 360.0)
    median_hue_deg = float(np.median(fg_hues)) if len(fg_hues) > 0 else 0.0
    mean_sat = float(np.mean(sat[fg_mask])) if len(fg_hues) > 0 else 0.0

    object_intact = (fg_share >= 0.030) and (mean_sat >= 0.15)

    return {
        "file": path.name,
        "fg_pixels": fg_pixel_count,
        "fg_share": fg_share,
        "mean_hue_deg": round(mean_hue_deg, 2),
        "median_hue_deg": round(median_hue_deg, 2),
        "mean_sat": round(mean_sat, 4),
        "object_intact": object_intact,
    }


def run_evaluation(dose: float = DEFAULT_DOSE):
    print(f"Evaluating Stage 2 Sweep Renders at dose {dose:.3f} (3 Arms: LP, LG, LN)...")

    meas_rows = []

    # 1. Measure Baselines
    baselines: dict[tuple[str, int], dict] = {}
    for pid in PROMPTS:
        for seed in SEEDS:
            fn = f"{pid}_baseline_krea2_seed{seed}_00001_.png"
            p = RENDERS_DIR / fn
            if not p.exists():
                fn = f"{pid}_baseline_seed{seed}_00001_.png"
                p = RENDERS_DIR / fn
            m = analyze_image(p)
            m.update({"type": "baseline", "prompt_id": pid, "block": "none", "sign": "none", "seed": seed})
            baselines[(pid, seed)] = m
            meas_rows.append(m)

    # 2. Measure Perturbed Renders
    perturbed: dict[tuple[str, str, str, int], dict] = {}
    for blk in BLOCKS:
        for sgn in SIGNS:
            for pid in PROMPTS:
                for seed in SEEDS:
                    fn = f"{pid}_{blk}{sgn}_{dose:.3f}_krea2_seed{seed}_00001_.png"
                    p = RENDERS_DIR / fn
                    m = analyze_image(p)
                    m.update({"type": "perturbed", "prompt_id": pid, "block": blk, "sign": sgn, "seed": seed})
                    perturbed[(blk, sgn, pid, seed)] = m
                    meas_rows.append(m)

    # Write measurements CSV
    fieldnames = [
        "type", "prompt_id", "block", "sign", "seed",
        "mean_hue_deg", "median_hue_deg", "mean_sat", "fg_share", "object_intact", "file"
    ]
    MEAS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(MEAS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(meas_rows)
    print(f"Wrote {MEAS_CSV} ({len(meas_rows)} rows)")

    # 3. Classify Each of the 12 Block Treatments
    verdict_rows = []
    print("\n=== CLASSIFICATION MATRIX ACROSS 12 BLOCK CONDITIONS (3 ARMS) ===")

    reversion_blocks = []
    collapse_blocks = []

    for blk in BLOCKS:
        for sgn in SIGNS:
            cond_label = f"{blk}_{sgn}"

            lp_intact_count = sum(1 for s in SEEDS if perturbed[(blk, sgn, "LP", s)]["object_intact"])
            lg_intact_count = sum(1 for s in SEEDS if perturbed[(blk, sgn, "LG", s)]["object_intact"])
            ln_intact_count = sum(1 for s in SEEDS if perturbed[(blk, sgn, "LN", s)]["object_intact"])

            # Check collapse (>= 2 seeds collapsed on any prompt)
            if lp_intact_count <= 1 or lg_intact_count <= 1 or ln_intact_count <= 1:
                classification = "object_collapse"
                collapse_blocks.append(cond_label)
                lp_shifts = [circular_diff(perturbed[(blk, sgn, "LP", s)]["mean_hue_deg"], baselines[("LP", s)]["mean_hue_deg"]) for s in SEEDS]
                lg_shifts = [circular_diff(perturbed[(blk, sgn, "LG", s)]["mean_hue_deg"], baselines[("LG", s)]["mean_hue_deg"]) for s in SEEDS]
                ln_shifts = [circular_diff(perturbed[(blk, sgn, "LN", s)]["mean_hue_deg"], baselines[("LN", s)]["mean_hue_deg"]) for s in SEEDS]
                verdict_rows.append({
                    "condition": cond_label,
                    "block": blk,
                    "sign": sgn,
                    "dose": dose,
                    "lp_intact": f"{lp_intact_count}/3",
                    "lg_intact": f"{lg_intact_count}/3",
                    "ln_intact": f"{ln_intact_count}/3",
                    "lp_mean_shift_deg": round(float(np.mean(lp_shifts)), 1),
                    "lg_mean_shift_deg": round(float(np.mean(lg_shifts)), 1),
                    "ln_mean_shift_deg": round(float(np.mean(ln_shifts)), 1),
                    "classification": classification,
                    "notes": "Object area or chromatic structure collapsed on at least one arm"
                })
                print(f"  {cond_label:14s} | LP: {lp_intact_count}/3, LG: {lg_intact_count}/3, LN: {ln_intact_count}/3 | CLASSIFICATION: {classification}")
                continue

            # All 3 arms intact across >= 2 seeds
            lp_hues = [perturbed[(blk, sgn, "LP", s)]["mean_hue_deg"] for s in SEEDS]
            lg_hues = [perturbed[(blk, sgn, "LG", s)]["mean_hue_deg"] for s in SEEDS]
            ln_hues = [perturbed[(blk, sgn, "LN", s)]["mean_hue_deg"] for s in SEEDS]

            lp_shifts = [circular_diff(perturbed[(blk, sgn, "LP", s)]["mean_hue_deg"], baselines[("LP", s)]["mean_hue_deg"]) for s in SEEDS]
            lg_shifts = [circular_diff(perturbed[(blk, sgn, "LG", s)]["mean_hue_deg"], baselines[("LG", s)]["mean_hue_deg"]) for s in SEEDS]
            ln_shifts = [circular_diff(perturbed[(blk, sgn, "LN", s)]["mean_hue_deg"], baselines[("LN", s)]["mean_hue_deg"]) for s in SEEDS]

            # Criterion B: Reversion check
            # LG stays green: within [65, 120] and |shift| < 25 on >= 2 seeds
            lg_stays_green_count = sum(1 for h, sh in zip(lg_hues, lg_shifts) if (GREEN_HUE_MIN <= h <= GREEN_HUE_MAX) and abs(sh) < 25.0)
            lg_stays_green = lg_stays_green_count >= 2

            # LP shifts toward green or natural prior
            lp_moves_green_count = sum(1 for h in lp_hues if (65.0 <= h <= 165.0) or (abs(circular_diff(h, 88.0)) < 50.0))
            lp_moves_autumn_count = sum(1 for h in lp_hues if (AUTUMN_HUE_MIN <= h <= AUTUMN_HUE_MAX))

            if lg_stays_green and (lp_moves_green_count >= 2):
                classification = "semantic_reversion"
                reversion_blocks.append(cond_label)
                notes = "Binding decoupled: LP shifted green (canonical concept) while LG stayed green"
            elif lg_stays_green and (lp_moves_autumn_count >= 2):
                classification = "default_prior_reversion"
                reversion_blocks.append(cond_label)
                notes = "Binding decoupled: LP shifted autumnal (natural unconstrained prior) while LG stayed green"
            else:
                # Criterion C: Generic rotation
                diff_pg = [abs(p_sh - g_sh) for p_sh, g_sh in zip(lp_shifts, lg_shifts)]
                diff_pn = [abs(p_sh - n_sh) for p_sh, n_sh in zip(lp_shifts, ln_shifts)]

                if sum(1 for dg, dn in zip(diff_pg, diff_pn) if dg < 30.0 and dn < 30.0) >= 2 and abs(np.mean(lp_shifts)) > 15.0:
                    classification = "generic_rotation"
                    notes = "Global chromatic rotation across all three arms"
                elif all(abs(sh) < 20.0 for sh in lp_shifts + lg_shifts + ln_shifts):
                    classification = "unperturbed_binding"
                    notes = "Binding unaffected: all three arms remained stable"
                else:
                    classification = "partial_chromatic_shift"
                    notes = "Asymmetric shift without full reversion"

            verdict_rows.append({
                "condition": cond_label,
                "block": blk,
                "sign": sgn,
                "dose": dose,
                "lp_intact": f"{lp_intact_count}/3",
                "lg_intact": f"{lg_intact_count}/3",
                "ln_intact": f"{ln_intact_count}/3",
                "lp_mean_shift_deg": round(float(np.mean(lp_shifts)), 1),
                "lg_mean_shift_deg": round(float(np.mean(lg_shifts)), 1),
                "ln_mean_shift_deg": round(float(np.mean(ln_shifts)), 1),
                "classification": classification,
                "notes": notes
            })
            print(f"  {cond_label:14s} | LP: {np.mean(lp_shifts):+6.1f}°, LG: {np.mean(lg_shifts):+6.1f}°, LN: {np.mean(ln_shifts):+6.1f}° | {classification}")

    # Write Verdict CSV
    v_fields = [
        "condition", "block", "sign", "dose", "lp_intact", "lg_intact", "ln_intact",
        "lp_mean_shift_deg", "lg_mean_shift_deg", "ln_mean_shift_deg", "classification", "notes"
    ]
    with open(VERDICT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=v_fields)
        w.writeheader()
        w.writerows(verdict_rows)
    print(f"\nWrote {VERDICT_CSV}")

    # Also save dose-specific copy
    dose_v_csv = DATA_DIR / f"colour_object_sweep_verdict_{dose:.3f}.csv"
    with open(dose_v_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=v_fields)
        w.writeheader()
        w.writerows(verdict_rows)
    print(f"Wrote {dose_v_csv}")

    # Dissociation verdict
    print("\n=== FINAL DISSOCIATION VERDICT ===")
    if reversion_blocks and collapse_blocks:
        print(f"DECISIVE FINDING (DISSOCIATION OBSERVED):")
        print(f"  Reversion blocks: {reversion_blocks}")
        print(f"  Collapse blocks:  {collapse_blocks}")
    elif reversion_blocks:
        print(f"SELECTIVE REVERSION OBSERVED in: {reversion_blocks}")
    else:
        print(f"NEGATIVE FINDING: No block produced selective colour/object dissociation at dose {dose:.3f}.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate colour object sweep")
    parser.add_argument("--dose", type=float, default=DEFAULT_DOSE, help="Steering dose to evaluate (default: 0.200)")
    args = parser.parse_args()
    run_evaluation(dose=args.dose)


if __name__ == "__main__":
    main()
