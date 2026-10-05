# -*- coding: utf-8 -*-
"""
experiments/queue_single_blocks_v3.py
=====================================
Queues renders for the Single-Block v3 bench (171 renders total: 3 prompts x 57 conditions).
Tuned doses based on Alessandro's notes.

Design requirements:
  - Reads data/realism_test_plan.csv
  - Drives each single block via ArthemyKrea2ModelTuner with a 34-slot vectors_override
    in Real Value mode.
  - Reset patcher ArthemyKrea2ResetPatcher inserted before the tuner.
  - Output folder: benchmark_realism_test/renders
  - Idempotent: skips renders already existing on disk or currently pending in ComfyUI queue.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PLAN_CSV = DATA_DIR / "realism_test_plan.csv"

COMFY_HOST = "http://127.0.0.1:8188"
COMFY_OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")
OUTPUT_FOLDER_NAME = "benchmark_realism_test/renders"
TARGET_DIR = COMFY_OUTPUT_ROOT / OUTPUT_FOLDER_NAME


def check_comfy_online() -> bool:
    try:
        req = urllib.request.Request(f"{COMFY_HOST}/queue", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def get_queue_counts() -> Tuple[int, int]:
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


def get_in_queue_prefixes() -> Set[str]:
    try:
        req = urllib.request.Request(f"{COMFY_HOST}/queue", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            running = data.get("queue_running", [])
            pending = data.get("queue_pending", [])
            prefixes = set()
            for item in running + pending:
                try:
                    p = item[2].get("61", {}).get("inputs", {}).get("filename_prefix", "")
                    if p:
                        prefixes.add(p)
                except Exception:
                    pass
            return prefixes
    except Exception:
        return set()


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
    vectors_override = row.get("vectors_override", "").strip()
    mode = row.get("mode", "Real Value")

    filename_prefix = f"{OUTPUT_FOLDER_NAME}/{output_prefix}"
    is_perturbed = bool(vectors_override)

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
        "42": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["50", 0] if is_perturbed else ["37", 0],
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

    if is_perturbed:
        wf["50"] = {
            "class_type": "ArthemyKrea2ModelTuner",
            "inputs": {
                "model": ["37", 0],
                "mode": mode,
                "vectors_override": vectors_override,
                "granular_json": "",
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


def load_plan() -> List[dict]:
    rows = []
    with open(PLAN_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def main():
    parser = argparse.ArgumentParser(description="Queue Single-Block v3 renders.")
    parser.add_argument("--all", action="store_true", help="Queue all renders in data/realism_test_plan.csv.")
    parser.add_argument("--first", type=int, default=0, help="Queue only first N rows.")
    parser.add_argument("--check-only", action="store_true", help="Print plan and queue status without queuing.")
    args = parser.parse_args()

    if not check_comfy_online():
        print(f"ERROR: ComfyUI is not reachable at {COMFY_HOST}")
        sys.exit(1)

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_plan()

    if args.first > 0:
        rows = rows[:args.first]
        print(f"Filtered to first {args.first} rows.")

    in_queue_prefixes = get_in_queue_prefixes()
    pending_rows = []
    already_done = []
    already_queued = []

    for r in rows:
        fn = r["expected_filename"]
        target_path = TARGET_DIR / fn
        prefix = f"{OUTPUT_FOLDER_NAME}/{r['output_prefix']}"
        if target_path.exists() and target_path.stat().st_size > 1000:
            already_done.append(r)
        elif prefix in in_queue_prefixes:
            already_queued.append(r)
        else:
            pending_rows.append(r)

    print(f"Total target renders:       {len(rows)}")
    print(f"Already rendered on disk:   {len(already_done)}")
    print(f"Currently in ComfyUI queue: {len(already_queued)}")
    print(f"To be newly queued:         {len(pending_rows)}")

    if args.check_only:
        print("\nCheck-only mode. Sample pending rows:")
        for r in pending_rows[:10]:
            print(f"  Row {r['row_index']:>3s} | {r['arm']:12s} | {r['condition']:16s} | {r['prompt_id']:15s} | seed={r['seed']} | {r['output_prefix']}")
        return

    if not pending_rows:
        print("All target renders already rendered or in queue! Nothing new to queue.")
        return

    print(f"\nQueuing {len(pending_rows)} renders to ComfyUI at {COMFY_HOST}...")
    queued_count = 0
    t0 = time.time()

    for idx, r in enumerate(pending_rows, 1):
        wf = build_workflow(r)
        pid = post_prompt(wf)
        queued_count += 1
        print(f"[{idx}/{len(pending_rows)}] Row {r['row_index']:>3s} -> Queued prompt {pid} ({r['output_prefix']})")

    elapsed = time.time() - t0
    print(f"\nSuccessfully queued {queued_count} tasks in {elapsed:.2f}s.")

    running, pending = get_queue_counts()
    print(f"ComfyUI Queue Verification: {running} running, {pending} pending tasks in queue.")


if __name__ == "__main__":
    main()

