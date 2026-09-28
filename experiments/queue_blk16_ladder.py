# -*- coding: utf-8 -*-
"""
experiments/queue_blk16_ladder.py
=================================
Queues renders for Bench 2: benchmark_blk16_ladder (72 renders).
Governed by docs/RENDERS_2026-09-28_leaf_collapse_and_blk16.md.

Design requirements:
  - Reads data/blk16_ladder_plan.csv
  - Drives blk16 single block with a 34-slot vectors_override in Real Value mode,
    with all named group inputs set to 0.0.
  - All generation parameters and vector override strings are read directly from the CSV.
  - Rows with treatment == "none" or condition == "none" bypass the tuner entirely.
  - Output folder: benchmark_blk16_ladder/renders
  - Supports --first N to queue only the first N rows for pre-launch verification.

Usage:
  python experiments/queue_blk16_ladder.py --first 3
  python experiments/queue_blk16_ladder.py --all
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PLAN_CSV = DATA_DIR / "blk16_ladder_plan.csv"

COMFY_HOST = "http://127.0.0.1:8188"
COMFY_OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")
OUTPUT_FOLDER_NAME = "benchmark_blk16_ladder/renders"


def check_comfy_online() -> bool:
    try:
        req = urllib.request.Request(f"{COMFY_HOST}/queue", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def get_queue_counts() -> tuple[int, int]:
    try:
        req = urllib.request.Request(f"{COMFY_HOST}/queue", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            running = len(data.get("queue_running", []))
            pending = len(data.get("queue_pending", []))
            return running, pending
    except Exception as e:
        print(f"Error querying queue: {e}")
        return -1, -1


def build_workflow(row: dict) -> dict:
    prompt_text = row["prompt_text"]
    seed = int(row["seed"])
    steps = int(row["steps"])
    cfg = float(row["cfg"])
    sampler_name = row["sampler"]
    scheduler = row["scheduler"]
    denoise = float(row.get("denoise", 1.0))
    width = int(row["width"])
    height = int(row["height"])
    output_prefix = row["output_prefix"]
    if not output_prefix.startswith(OUTPUT_FOLDER_NAME):
        filename_prefix = f"{OUTPUT_FOLDER_NAME}/{output_prefix}"
    else:
        filename_prefix = output_prefix

    treatment = row.get("treatment", "").strip()
    condition = row.get("condition", "").strip()
    vectors_override = row.get("vectors_override", "").strip()
    mode = row.get("mode", "Real Value")
    granular_json = row.get("granular_json", "").strip()

    wf = {
        "36": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "krea2_turbo_bf16.safetensors",
                "weight_dtype": "default"
            }
        },
        "47": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen3vl_4b_bf16.safetensors",
                "type": "krea2",
                "device": "default"
            }
        },
        "48": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "qwen_image_vae.safetensors"
            }
        },
        "45": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            }
        },
        "37": {
            "class_type": "ArthemyKrea2ResetPatcher",
            "inputs": {
                "model": ["36", 0],
                "clip": ["47", 0],
                "reset_model": True,
                "reset_clip": True
            }
        },
        "40": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["37", 1],
                "text": prompt_text
            }
        },
        "43": {
            "class_type": "ConditioningZeroOut",
            "inputs": {
                "conditioning": ["40", 0]
            }
        },
        "46": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["42", 0],
                "vae": ["48", 0]
            }
        },
        "61": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["46", 0],
                "filename_prefix": filename_prefix
            }
        }
    }

    # If row is baseline or treatment is none, bypass tuner
    if treatment == "none" or condition == "none" or (not vectors_override and treatment == ""):
        model_source = ["37", 0]
    else:
        wf["50"] = {
            "class_type": "ArthemyKrea2ModelTuner",
            "inputs": {
                "model": ["37", 0],
                "mode": mode,
                "vectors_override": vectors_override,
                "granular_json": granular_json,
                "Text_Fusion": 0.0,
                "Time_Embed": 0.0,
                "Projection": 0.0,
                "Block_1": 0.0,
                "Block_2": 0.0,
                "Block_3": 0.0,
                "Block_4": 0.0,
                "Block_5": 0.0,
                "Block_6": 0.0
            }
        }
        model_source = ["50", 0]

    wf["42"] = {
        "class_type": "KSampler",
        "inputs": {
            "model": model_source,
            "positive": ["40", 0],
            "negative": ["43", 0],
            "latent_image": ["45", 0],
            "seed": seed,
            "steps": steps,
            "cfg": cfg,
            "sampler_name": sampler_name,
            "scheduler": scheduler,
            "denoise": denoise
        }
    }

    return wf


def post_prompt(workflow: dict) -> str:
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFY_HOST}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        return res_data.get("prompt_id", "")


def main():
    parser = argparse.ArgumentParser(description="Queue Bench 2: BLK16 Ladder renders")
    parser.add_argument("--first", type=int, default=0, help="Queue only the first N rows (e.g. 3 for pre-check)")
    parser.add_argument("--all", action="store_true", help="Queue all rows in plan")
    parser.add_argument("--check-only", action="store_true", help="Check plan and verify files without queuing")
    args = parser.parse_args()

    if not check_comfy_online():
        sys.exit(f"ERROR: ComfyUI server is not reachable at {COMFY_HOST}. Start ComfyUI first.")

    if not PLAN_CSV.exists():
        sys.exit(f"ERROR: Plan file {PLAN_CSV} not found.")

    with open(PLAN_CSV, encoding="utf-8") as f:
        plan_rows = list(csv.DictReader(f))

    if args.first > 0:
        plan_rows = plan_rows[:args.first]
        print(f"Limiting to first {len(plan_rows)} tasks (Pre-check mode)...")
    elif not args.all and not args.check_only:
        print("Please specify --first N (e.g. --first 3) or --all. Use --check-only to dry-run.")
        sys.exit(1)

    print(f"Loaded {len(plan_rows)} tasks from {PLAN_CSV}.")
    running, pending = get_queue_counts()
    print(f"Current ComfyUI Queue: Running={running}, Pending={pending}")

    target_dir = COMFY_OUTPUT_ROOT / OUTPUT_FOLDER_NAME
    target_dir.mkdir(parents=True, exist_ok=True)

    queued_count = 0
    skipped_count = 0

    for idx, r in enumerate(plan_rows, 1):
        expected_fn = r["expected_filename"]
        target_png = target_dir / expected_fn

        # If already exists and not in check-only
        if target_png.exists():
            skipped_count += 1
            print(f"  [{idx}/{len(plan_rows)}] Already exists: {expected_fn}")
            continue

        cond = r.get("condition", "")
        prompt_id = r["prompt_id"]
        seed = r["seed"]
        print(f"  [{idx}/{len(plan_rows)}] Queuing row {r['row_index']} ({prompt_id}, seed {seed}, condition={cond}) -> {expected_fn}")

        wf = build_workflow(r)

        if not args.check_only:
            post_prompt(wf)
            queued_count += 1

    print(f"\nQueuing summary: Queued={queued_count}, Skipped={skipped_count} (existing)")
    if not args.check_only:
        r_after, p_after = get_queue_counts()
        print(f"ComfyUI Queue Status: Running={r_after}, Pending={p_after}, Total={r_after + p_after}")


if __name__ == "__main__":
    main()
