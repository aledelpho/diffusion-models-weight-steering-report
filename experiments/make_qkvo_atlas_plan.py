# -*- coding: utf-8 -*-
"""
experiments/make_qkvo_atlas_plan.py
===================================
Generates data/qkvo_atlas_plan.csv for the QKVO Atlas (RUNBOOK_qkvo_atlas_plan_1.md §7.5).
  - Row 1: determinism_check (S1_photo baseline seed 42)
  - Rows 2..433: 432 renders grouped by preset:
    18 presets x 8 prompts (S1_photo .. S8_charcoal) x 3 seeds (42, 777, 1337)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROMPT_JSON = DATA_DIR / "stage9_prompts.json"
PRESET_COUNTS_CSV = DATA_DIR / "qkvo_preset_layer_counts.csv"
OUT_PLAN_CSV = DATA_DIR / "qkvo_atlas_plan.csv"

SEEDS = [42, 777, 1337]

# Sampler settings from standard atlas pipeline
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

    if len(prompts) != 8:
        raise RuntimeError(f"Expected 8 prompts (S1-S8), got {len(prompts)}")

    with open(PRESET_COUNTS_CSV, encoding="utf-8") as f:
        preset_rows = list(csv.DictReader(f))

    if len(preset_rows) != 18:
        raise RuntimeError(f"Expected 18 presets in {PRESET_COUNTS_CSV}, got {len(preset_rows)}")

    s1 = next(p for p in prompts if p["prompt_id"] == "S1_photo")

    plan_rows = []
    row_idx = 1

    # 1. Row 1: Determinism check row (runs FIRST)
    plan_rows.append({
        "row_index": row_idx,
        "type": "determinism_check",
        "condition": "baseline",
        "draw": 0,
        "preset_file": "",
        "prompt_id": s1["prompt_id"],
        "prompt_sha1": s1["prompt_sha1"],
        "seed": 42,
        "sampler": SAMPLER,
        "scheduler": SCHEDULER,
        "steps": STEPS,
        "cfg": CFG,
        "denoise": DENOISE,
        "width": WIDTH,
        "height": HEIGHT,
        "expected_filename": f"{s1['prompt_id']}_baseline_seed42_00001_.png",
        "prompt_text": s1["text"],
    })
    row_idx += 1

    # 2. 432 perturbed renders grouped by preset
    for p_row in preset_rows:
        preset_name = p_row["preset"]
        preset_file = f"{preset_name}.json"
        is_ctrl = "normscales" in preset_name
        row_type = "control" if is_ctrl else "perturbed"

        # Condition string: strip Arthemy_QKVO_ prefix
        cond_str = preset_name.replace("Arthemy_QKVO_", "")

        for p in prompts:
            pid = p["prompt_id"]
            psha = p["prompt_sha1"]
            ptext = p["text"]
            for seed in SEEDS:
                plan_rows.append({
                    "row_index": row_idx,
                    "type": row_type,
                    "condition": cond_str,
                    "draw": 0,
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

    fieldnames = [
        "row_index", "type", "condition", "draw", "preset_file",
        "prompt_id", "prompt_sha1", "seed",
        "sampler", "scheduler", "steps", "cfg", "denoise", "width", "height",
        "expected_filename", "prompt_text"
    ]

    with open(OUT_PLAN_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(plan_rows)

    print(f"Wrote {OUT_PLAN_CSV} with {len(plan_rows)} rows:")
    print(f"  - 1 determinism_check row")
    print(f"  - {len(plan_rows) - 1} condition rows (18 presets x 8 prompts x 3 seeds)")


if __name__ == "__main__":
    main()
