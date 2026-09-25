# -*- coding: utf-8 -*-
"""
experiments/make_atlas_phase2_plan.py
====================================
Generates the Phase 2 render plan for the remaining 7 style prompts
(S2_watercolor through S8_charcoal) for the Perturbation Atlas (Block J, J6).

Optimal queuing order (per user directive):
  - Grouped by preset: load a preset once, run all 7 prompts x 3 seeds (21 images),
    then proceed to the next preset.
  - Baselines run first as a single group (no preset loaded).

Structure:
  - 21 baselines (7 prompts x 3 seeds)
  - 546 perturbed renders (26 presets x 7 prompts x 3 seeds)
  - Total: 567 renders
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

PROMPT_JSON = DATA_DIR / "stage9_prompts.json"
CALIB_CSV = DATA_DIR / "perturbation_atlas_calibration.csv"
OUT_PLAN_CSV = DATA_DIR / "perturbation_atlas_phase2_plan.csv"

SEEDS = [42, 777, 1337]

# Sampler settings identical across all runs
SAMPLER = "euler_ancestral"
SCHEDULER = "simple"
STEPS = 9
CFG = 1.0
DENOISE = 1.0
WIDTH = 1024
HEIGHT = 1280


def main():
    with open(PROMPT_JSON, encoding="utf-8") as f:
        all_prompts = json.load(f)

    # Remaining 7 prompts: S2 through S8
    prompts = [p for p in all_prompts if p["prompt_id"] != "S1_photo"]
    if len(prompts) != 7:
        raise RuntimeError(f"Expected 7 prompts (S2-S8), got {len(prompts)}")

    with open(CALIB_CSV, encoding="utf-8") as f:
        calib_rows = list(csv.DictReader(f))

    if len(calib_rows) != 26:
        raise RuntimeError(f"Expected 26 calibrated presets, got {len(calib_rows)}")

    plan_rows = []
    row_idx = 1

    # 1. Baselines first: all 7 prompts x 3 seeds (21 renders)
    for p in prompts:
        pid = p["prompt_id"]
        psha = p["prompt_sha1"]
        ptext = p["text"]
        for seed in SEEDS:
            plan_rows.append({
                "row_index": row_idx,
                "type": "baseline",
                "condition": "baseline",
                "draw": 0,
                "preset_file": "",
                "prompt_id": pid,
                "prompt_sha1": psha,
                "seed": seed,
                "sampler": SAMPLER,
                "scheduler": SCHEDULER,
                "steps": STEPS,
                "cfg": CFG,
                "denoise": DENOISE,
                "width": WIDTH,
                "height": HEIGHT,
                "expected_filename": f"{pid}_baseline_seed{seed}_00001_.png",
                "prompt_text": ptext,
            })
            row_idx += 1

    # 2. Perturbed renders grouped by preset:
    # For each preset, run all 7 prompts x 3 seeds (21 renders per preset)
    for c_row in calib_rows:
        preset_name = c_row["preset"]
        region = c_row["region"]
        draw = int(c_row["draw"])
        preset_file = f"{preset_name}.json"

        for p in prompts:
            pid = p["prompt_id"]
            psha = p["prompt_sha1"]
            ptext = p["text"]
            for seed in SEEDS:
                plan_rows.append({
                    "row_index": row_idx,
                    "type": "perturbation",
                    "condition": region,
                    "draw": draw,
                    "preset_file": preset_file,
                    "prompt_id": pid,
                    "prompt_sha1": psha,
                    "seed": seed,
                    "sampler": SAMPLER,
                    "scheduler": SCHEDULER,
                    "steps": STEPS,
                    "cfg": CFG,
                    "denoise": DENOISE,
                    "width": WIDTH,
                    "height": HEIGHT,
                    "expected_filename": f"{pid}_{preset_name}_seed{seed}_00001_.png",
                    "prompt_text": ptext,
                })
                row_idx += 1

    expected_total = 7 * 3 + 26 * 7 * 3  # 21 + 546 = 567
    if len(plan_rows) != expected_total:
        raise RuntimeError(f"Expected {expected_total} rows, got {len(plan_rows)}")

    fieldnames = [
        "row_index", "type", "condition", "draw", "preset_file",
        "prompt_id", "prompt_sha1", "seed",
        "sampler", "scheduler", "steps", "cfg", "denoise", "width", "height",
        "expected_filename", "prompt_text"
    ]

    with open(OUT_PLAN_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(plan_rows)

    print(f"Generated {OUT_PLAN_CSV} successfully:")
    print(f"  Total render rows: {len(plan_rows)} (21 baselines + 546 perturbations)")
    print(f"  Prompts ({len(prompts)}): {[p['prompt_id'] for p in prompts]}")
    print(f"  Seeds ({len(SEEDS)}): {SEEDS}")
    print(f"  Presets ({len(calib_rows)}): 21 images per preset grouping")


if __name__ == "__main__":
    main()
