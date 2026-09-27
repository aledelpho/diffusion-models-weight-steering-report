# -*- coding: utf-8 -*-
"""
experiments/make_colour_object_pilot_plan.py
===========================================
Generates the Stage 1 pilot render plan for colour/object dissociation study.
Governed by:
  - docs/RENDERS_2026-09-27_colour_object_pilot.md
  - docs/assessment_colour_object_dissociation.md

Structure:
  - 15 renders: 3 prompts x 5 seeds
  - Prompts: LP (purple), LG (green), LN (neutral)
  - Seeds: 42, 777, 1337, 9999, 4242145
  - Output folder: benchmark_colour_binding/renders
  - Baseline mode: tuner absent or zero gains
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_PLAN_CSV = DATA_DIR / "colour_object_pilot_plan.csv"

PROMPTS = [
    {
        "prompt_id": "LP",
        "label": "uncommon_binding_purple",
        "text": "a single purple leaf centred on a plain light grey background, macro photograph, sharp focus, even studio lighting, no other objects"
    },
    {
        "prompt_id": "LG",
        "label": "prior_control_green",
        "text": "a single green leaf centred on a plain light grey background, macro photograph, sharp focus, even studio lighting, no other objects"
    },
    {
        "prompt_id": "LN",
        "label": "unspecified_prior",
        "text": "a single leaf centred on a plain light grey background, macro photograph, sharp focus, even studio lighting, no other objects"
    }
]

SEEDS = [42, 777, 1337, 9999, 4242145]

SAMPLER = "euler_ancestral"
SCHEDULER = "simple"
STEPS = 9
CFG = 1.0
DENOISE = 1.0
WIDTH = 1024
HEIGHT = 1280
OUTPUT_FOLDER = "benchmark_colour_binding/renders"


def main():
    plan_rows = []
    row_idx = 1

    for p in PROMPTS:
        pid = p["prompt_id"]
        plabel = p["label"]
        ptext = p["text"]
        for seed in SEEDS:
            expected_fn = f"{pid}_baseline_seed{seed}_00001_.png"
            prefix = f"{OUTPUT_FOLDER}/{pid}_baseline_seed{seed}"
            plan_rows.append({
                "row_index": row_idx,
                "stage": "stage1_pilot",
                "prompt_id": pid,
                "prompt_label": plabel,
                "seed": seed,
                "sampler": SAMPLER,
                "scheduler": SCHEDULER,
                "steps": STEPS,
                "cfg": CFG,
                "denoise": DENOISE,
                "width": WIDTH,
                "height": HEIGHT,
                "output_prefix": prefix,
                "expected_filename": expected_fn,
                "prompt_text": ptext,
            })
            row_idx += 1

    if len(plan_rows) != 15:
        raise RuntimeError(f"Expected 15 plan rows, got {len(plan_rows)}")

    fieldnames = [
        "row_index", "stage", "prompt_id", "prompt_label", "seed",
        "sampler", "scheduler", "steps", "cfg", "denoise", "width", "height",
        "output_prefix", "expected_filename", "prompt_text"
    ]

    OUT_PLAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PLAN_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(plan_rows)

    print(f"Generated {OUT_PLAN_CSV} successfully:")
    print(f"  Total render rows: {len(plan_rows)}")
    print(f"  Prompts ({len(PROMPTS)}): {[p['prompt_id'] for p in PROMPTS]}")
    print(f"  Seeds ({len(SEEDS)}): {SEEDS}")


if __name__ == "__main__":
    main()
