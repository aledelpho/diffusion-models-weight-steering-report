# -*- coding: utf-8 -*-
"""
experiments/make_atlas_phase1_plan.py
====================================
Generates the Phase 1 render plan for the Perturbation Atlas (Block J, J4).
Governed by:
  - docs/RUNBOOK_2026-09-25e.md (Block J, J4)
  - docs/prereg_perturbation_atlas.md (§5 Phase 1)
  - docs/prereg_perturbation_atlas_amendment_04.md (§3 13 conditions, 81 renders)
  - docs/prereg_mountain_reachability_amendment_01.md (§6 Environment determinism check)

Structure:
  - Row 1: Determinism check (S1 baseline seed 42, compared byte-for-byte with committed render)
  - Rows 2-4: 3 baselines (seeds 42, 777, 1337)
  - Rows 5-82: 78 perturbed renders (13 conditions x 2 draws x 3 noise seeds)
  - Sampler columns included explicitly on all rows:
    sampler, scheduler, steps, cfg, denoise, width, height.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

PROMPT_JSON = DATA_DIR / "stage9_prompts.json"
CALIB_CSV = DATA_DIR / "perturbation_atlas_calibration.csv"
OUT_PLAN_CSV = DATA_DIR / "perturbation_atlas_phase1_plan.csv"

REFERENCE_BASELINE_FILE = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage9\renders\S1_photo_baseline_seed42_00001_.png"
REFERENCE_BASELINE_SHA256 = "08d0193a58aee459c41905029ef04fa795af9ff71cd20ff14fc2ba278e404637"

SEEDS = [42, 777, 1337]

# Sampler settings verified from reference render metadata
SAMPLER = "euler_ancestral"
SCHEDULER = "simple"
STEPS = 9
CFG = 1.0
DENOISE = 1.0
WIDTH = 1024
HEIGHT = 1280


def main():
    with open(PROMPT_JSON, encoding="utf-8") as f:
        prompts = json.load(f)

    # Find S1_photo
    s1 = next(p for p in prompts if p["prompt_id"] == "S1_photo")
    prompt_id = s1["prompt_id"]
    prompt_sha1 = s1["prompt_sha1"]
    prompt_text = s1["text"]

    # Load 26 atlas presets in order
    with open(CALIB_CSV, encoding="utf-8") as f:
        calib_rows = list(csv.DictReader(f))

    if len(calib_rows) != 26:
        raise RuntimeError(f"Expected 26 calibrated presets, got {len(calib_rows)}")

    plan_rows = []
    row_idx = 1

    # 0. Determinism check row (runs FIRST)
    plan_rows.append({
        "row_index": row_idx,
        "type": "determinism_check",
        "condition": "baseline",
        "draw": 0,
        "seed": 42,
        "sampler": SAMPLER,
        "scheduler": SCHEDULER,
        "steps": STEPS,
        "cfg": CFG,
        "denoise": DENOISE,
        "width": WIDTH,
        "height": HEIGHT,
        "preset_file": "",
        "prompt_id": prompt_id,
        "prompt_sha1": prompt_sha1,
        "expected_filename": f"{prompt_id}_baseline_seed42_00001_.png",
        "prompt_text": prompt_text,
    })
    row_idx += 1

    # 1. Three Baselines (seeds 42, 777, 1337)
    for seed in SEEDS:
        plan_rows.append({
            "row_index": row_idx,
            "type": "baseline",
            "condition": "baseline",
            "draw": 0,
            "seed": seed,
            "sampler": SAMPLER,
            "scheduler": SCHEDULER,
            "steps": STEPS,
            "cfg": CFG,
            "denoise": DENOISE,
            "width": WIDTH,
            "height": HEIGHT,
            "preset_file": "",
            "prompt_id": prompt_id,
            "prompt_sha1": prompt_sha1,
            "expected_filename": f"{prompt_id}_baseline_seed{seed}_00001_.png",
            "prompt_text": prompt_text,
        })
        row_idx += 1

    # 2. 78 Perturbation renders (26 presets x 3 seeds)
    for c_row in calib_rows:
        preset_name = c_row["preset"]
        region = c_row["region"]
        draw = int(c_row["draw"])
        preset_file = f"{preset_name}.json"

        for seed in SEEDS:
            plan_rows.append({
                "row_index": row_idx,
                "type": "perturbation",
                "condition": region,
                "draw": draw,
                "seed": seed,
                "sampler": SAMPLER,
                "scheduler": SCHEDULER,
                "steps": STEPS,
                "cfg": CFG,
                "denoise": DENOISE,
                "width": WIDTH,
                "height": HEIGHT,
                "preset_file": preset_file,
                "prompt_id": prompt_id,
                "prompt_sha1": prompt_sha1,
                "expected_filename": f"{prompt_id}_{preset_name}_seed{seed}_00001_.png",
                "prompt_text": prompt_text,
            })
            row_idx += 1

    fieldnames = [
        "row_index", "type", "condition", "draw", "seed",
        "sampler", "scheduler", "steps", "cfg", "denoise", "width", "height",
        "preset_file", "prompt_id", "prompt_sha1",
        "expected_filename", "prompt_text"
    ]

    with open(OUT_PLAN_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(plan_rows)

    print(f"Generated {OUT_PLAN_CSV} successfully:")
    print(f"  Total rows: {len(plan_rows)} (1 determinism_check + 3 baselines + 78 perturbations)")
    print(f"  Prompt: {prompt_id} (SHA1: {prompt_sha1})")
    print(f"  Seeds: {SEEDS}")
    print(f"  Sampler: {SAMPLER}, Scheduler: {SCHEDULER}, Steps: {STEPS}, CFG: {CFG}, Denoise: {DENOISE}, Dim: {WIDTH}x{HEIGHT}")
    print(f"\nEnvironment Determinism Check reference:")
    print(f"  File:   {REFERENCE_BASELINE_FILE}")
    print(f"  SHA256: {REFERENCE_BASELINE_SHA256}")


if __name__ == "__main__":
    main()
