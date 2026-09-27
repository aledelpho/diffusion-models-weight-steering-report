# -*- coding: utf-8 -*-
"""
experiments/make_colour_object_sweep_plan.py
===========================================
Generates Stage 2 sweep render plan for colour/object dissociation study.
Governed by docs/RENDERS_2026-09-27_colour_object_pilot.md (§3).

Factors:
  - Prompts (2): LP (purple), LG (green)
  - Block groups (6): Block_1 through Block_6
  - Signs (2): pos (+0.050), neg (-0.050)
  - Dose: 0.050
  - Seeds (3): 42, 777, 1337
  - Perturbed: 2 prompts x 6 blocks x 2 signs x 3 seeds = 72 renders
  - Baselines: 2 prompts x 3 seeds = 6 renders
  - Total: 78 renders

Naming convention (matches benchmark_mappa):
  - Perturbed: {prompt}_{block}{sign}_{dose:.3f}_krea2_seed{seed}_00001_.png
    e.g. LP_Block_3pos_0.050_krea2_seed42_00001_.png
  - Baseline:  {prompt}_baseline_krea2_seed{seed}_00001_.png
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_PLAN_CSV = DATA_DIR / "colour_object_sweep_plan.csv"

PROMPTS = [
    {
        "prompt_id": "LP",
        "text": "a single purple leaf centred on a plain light grey background, macro photograph, sharp focus, even studio lighting, no other objects"
    },
    {
        "prompt_id": "LG",
        "text": "a single green leaf centred on a plain light grey background, macro photograph, sharp focus, even studio lighting, no other objects"
    }
]

BLOCKS = ["Block_1", "Block_2", "Block_3", "Block_4", "Block_5", "Block_6"]
SIGNS = ["pos", "neg"]
DOSE = 0.050
SEEDS = [42, 777, 1337]

OUTPUT_FOLDER = "benchmark_colour_binding/renders"
SAMPLER = "euler_ancestral"
SCHEDULER = "simple"
STEPS = 9
CFG = 1.0
DENOISE = 1.0
WIDTH = 1024
HEIGHT = 1280


def main():
    plan_rows = []
    row_idx = 1

    # 1. Six Baselines
    for p in PROMPTS:
        pid = p["prompt_id"]
        ptext = p["text"]
        for seed in SEEDS:
            prefix = f"{OUTPUT_FOLDER}/{pid}_baseline_krea2_seed{seed}"
            expected_fn = f"{pid}_baseline_krea2_seed{seed}_00001_.png"
            plan_rows.append({
                "row_index": row_idx,
                "type": "baseline",
                "prompt_id": pid,
                "block": "none",
                "sign": "none",
                "dose": 0.0,
                "gain": 0.0,
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

    # 2. 72 Perturbed renders (grouped by block & sign for GPU efficiency)
    for blk in BLOCKS:
        for sgn in SIGNS:
            gain = DOSE if sgn == "pos" else -DOSE
            for p in PROMPTS:
                pid = p["prompt_id"]
                ptext = p["text"]
                for seed in SEEDS:
                    cond_label = f"{blk}{sgn}"
                    prefix = f"{OUTPUT_FOLDER}/{pid}_{cond_label}_{DOSE:.3f}_krea2_seed{seed}"
                    expected_fn = f"{pid}_{cond_label}_{DOSE:.3f}_krea2_seed{seed}_00001_.png"
                    plan_rows.append({
                        "row_index": row_idx,
                        "type": "perturbed",
                        "prompt_id": pid,
                        "block": blk,
                        "sign": sgn,
                        "dose": DOSE,
                        "gain": gain,
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

    if len(plan_rows) != 78:
        raise RuntimeError(f"Expected 78 rows, got {len(plan_rows)}")

    fieldnames = [
        "row_index", "type", "prompt_id", "block", "sign", "dose", "gain",
        "seed", "sampler", "scheduler", "steps", "cfg", "denoise", "width", "height",
        "output_prefix", "expected_filename", "prompt_text"
    ]

    OUT_PLAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PLAN_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(plan_rows)

    print(f"Generated {OUT_PLAN_CSV} successfully:")
    print(f"  Total render rows: {len(plan_rows)} (6 baselines + 72 perturbed)")
    print(f"  Blocks ({len(BLOCKS)}): {BLOCKS}")
    print(f"  Signs: {SIGNS} (dose {DOSE:.3f})")
    print(f"  Seeds ({len(SEEDS)}): {SEEDS}")


if __name__ == "__main__":
    main()
