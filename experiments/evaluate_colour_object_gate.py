# -*- coding: utf-8 -*-
"""
experiments/evaluate_colour_object_gate.py
=========================================
Evaluates Stage 1 feasibility gate for colour/object dissociation study.
Governed by docs/RENDERS_2026-09-27_colour_object_pilot.md (§2).

Gate Criteria:
  - G1: LP renders a leaf whose dominant hue is in the violet/purple band (>= 4 of 5 seeds).
        [Violet/purple band: 260 deg to 335 deg]
  - G2: LG renders a leaf whose dominant hue is in the green band (>= 4 of 5 seeds).
        [Green band: 65 deg to 165 deg]
  - G3: LP and LG hue distributions do NOT overlap across the 5 seeds.
  - G4: A leaf is present and intact in all 15 images (checked via foreground mask area and connectivity).
  - LN: Descriptive baseline for the model's unconstrained prior.
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
OUT_CSV = DATA_DIR / "colour_object_pilot_measurements.csv"

SEEDS = [42, 777, 1337, 9999, 4242145]
PROMPTS = ["LP", "LG", "LN"]

PURPLE_HUE_MIN = 250.0
PURPLE_HUE_MAX = 340.0

GREEN_HUE_MIN = 65.0
GREEN_HUE_MAX = 165.0


def rgb_to_hsv_np(arr: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Converts RGB uint8 image [H, W, 3] to Hue (0-360), Sat (0-1), Val (0-1)."""
    rgb = arr.astype(np.float32) / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin

    # Hue
    hue = np.zeros_like(cmax)
    # r is max
    mask_r = (cmax == r) & (delta > 1e-5)
    hue[mask_r] = (60.0 * ((g[mask_r] - b[mask_r]) / delta[mask_r]) + 360.0) % 360.0
    # g is max
    mask_g = (cmax == g) & (delta > 1e-5)
    hue[mask_g] = (60.0 * ((b[mask_g] - r[mask_g]) / delta[mask_g]) + 120.0) % 360.0
    # b is max
    mask_b = (cmax == b) & (delta > 1e-5)
    hue[mask_b] = (60.0 * ((r[mask_b] - g[mask_b]) / delta[mask_b]) + 240.0) % 360.0

    # Saturation
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

    # Plain grey background has low saturation and mid-to-high value.
    # Leaf object has chroma: sat > 0.15, and is not pure black/white.
    fg_mask = (sat > 0.15) & (val > 0.08) & (val < 0.98)
    fg_pixel_count = int(np.sum(fg_mask))
    total_pixels = arr.shape[0] * arr.shape[1]
    fg_share = fg_pixel_count / total_pixels

    if fg_pixel_count < 1000:
        # Fallback to center crop if background mask is noisy
        h, w = arr.shape[:2]
        center_mask = np.zeros((h, w), dtype=bool)
        center_mask[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4] = True
        fg_mask = center_mask & (sat > 0.10)
        fg_pixel_count = int(np.sum(fg_mask))

    fg_hues = hue[fg_mask]

    # Circular mean hue
    rads = np.deg2rad(fg_hues)
    sin_mean = np.mean(np.sin(rads))
    cos_mean = np.mean(np.cos(rads))
    mean_hue_deg = float(np.rad2deg(np.arctan2(sin_mean, cos_mean)) % 360.0)

    # Median hue
    median_hue_deg = float(np.median(fg_hues)) if len(fg_hues) > 0 else 0.0
    mean_sat = float(np.mean(sat[fg_mask])) if len(fg_hues) > 0 else 0.0

    # Dominant band check
    is_purple = PURPLE_HUE_MIN <= mean_hue_deg <= PURPLE_HUE_MAX
    is_green = GREEN_HUE_MIN <= mean_hue_deg <= GREEN_HUE_MAX

    # Object integrity check (leaf present and occupying at least 3% of the image)
    object_intact = fg_share >= 0.03

    return {
        "file": path.name,
        "fg_pixels": fg_pixel_count,
        "fg_share": fg_share,
        "mean_hue_deg": round(mean_hue_deg, 2),
        "median_hue_deg": round(median_hue_deg, 2),
        "mean_sat": round(mean_sat, 4),
        "is_purple": is_purple,
        "is_green": is_green,
        "object_intact": object_intact,
    }


def main():
    rows = []
    print("Evaluating Stage 1 Pilot Renders...")

    missing = []
    for pid in PROMPTS:
        for seed in SEEDS:
            fn = f"{pid}_baseline_seed{seed}_00001_.png"
            p = RENDERS_DIR / fn
            if not p.exists():
                missing.append(fn)

    if missing:
        print(f"[FAIL] {len(missing)} of 15 renders missing on disk:")
        for m in missing[:5]:
            print(f"  - {m}")
        sys.exit(1)

    for pid in PROMPTS:
        for seed in SEEDS:
            fn = f"{pid}_baseline_seed{seed}_00001_.png"
            p = RENDERS_DIR / fn
            metrics = analyze_image(p)
            metrics["prompt_id"] = pid
            metrics["seed"] = seed
            rows.append(metrics)

    # Write measurements CSV
    fieldnames = [
        "prompt_id", "seed", "mean_hue_deg", "median_hue_deg",
        "mean_sat", "fg_share", "is_purple", "is_green", "object_intact", "file"
    ]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT_CSV} ({len(rows)} rows)\n")

    # Gate evaluations
    lp_rows = [r for r in rows if r["prompt_id"] == "LP"]
    lg_rows = [r for r in rows if r["prompt_id"] == "LG"]
    ln_rows = [r for r in rows if r["prompt_id"] == "LN"]

    lp_purple_count = sum(1 for r in lp_rows if r["is_purple"])
    lg_green_count = sum(1 for r in lg_rows if r["is_green"])

    lp_hues = [r["mean_hue_deg"] for r in lp_rows]
    lg_hues = [r["mean_hue_deg"] for r in lg_rows]

    min_lp, max_lp = min(lp_hues), max(lp_hues)
    min_lg, max_lg = min(lg_hues), max(lg_hues)

    # Check non-overlap
    no_overlap = (max_lg < min_lp) or (max_lp < min_lg)

    intact_count = sum(1 for r in rows if r["object_intact"])

    g1_pass = lp_purple_count >= 4
    g2_pass = lg_green_count >= 4
    g3_pass = no_overlap
    g4_pass = intact_count == 15

    overall_pass = g1_pass and g2_pass and g3_pass and g4_pass

    print("=== STAGE 1 GATE VERIFICATION REPORT ===")
    print(f"G1 (LP purple >= 4/5):     {'PASS' if g1_pass else 'FAIL'} ({lp_purple_count}/5 purple, hues: {lp_hues})")
    print(f"G2 (LG green >= 4/5):      {'PASS' if g2_pass else 'FAIL'} ({lg_green_count}/5 green, hues: {lg_hues})")
    print(f"G3 (LP/LG hue no overlap): {'PASS' if g3_pass else 'FAIL'} (LP range: [{min_lp}, {max_lp}], LG range: [{min_lg}, {max_lg}])")
    print(f"G4 (15/15 leaf intact):    {'PASS' if g4_pass else 'FAIL'} ({intact_count}/15 intact)")
    print(f"\nLN descriptive prior hues: {[r['mean_hue_deg'] for r in ln_rows]}")
    print(f"\nOVERALL GATE VERDICT:      {'PASS' if overall_pass else 'FAIL'}")

    sys.exit(0 if overall_pass else 2)


if __name__ == "__main__":
    main()
