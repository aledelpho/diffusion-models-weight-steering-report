# -*- coding: utf-8 -*-
"""
experiments/queue_swiglu_rectified_atlas.py
===========================================
Queues renders for the SwiGLU Internal Rectified Mask Atlas (171 renders total):
  - 3 baselines
  - 168 SwiGLU rectified perturbations:
      28 blocks x 2 arms (pos: +gate/-up, neg: -gate/+up) x 3 prompts
      dose: 0.350, seed: 2718281

Design requirements:
  - Reads data/swiglu_rectified_atlas_plan.csv
  - Drives each single-block SwiGLU rectified condition via ArthemyKrea2PresetLoader
    with strength_model=1.0, strength_clip=1.0.
  - Reset patcher ArthemyKrea2ResetPatcher inserted before preset loader.
  - Output folder: benchmark_swiglu_rectified_atlas/renders
  - Idempotent: skips renders already existing on disk or currently pending in ComfyUI queue.
  - Tool --check-logs included to verify each preset matched exactly 2 scalar layers.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PLAN_CSV = DATA_DIR / "swiglu_rectified_atlas_plan.csv"

COMFY_HOST = "http://127.0.0.1:8188"
COMFY_OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")
OUTPUT_FOLDER_NAME = "benchmark_swiglu_rectified_atlas/renders"
TARGET_DIR = COMFY_OUTPUT_ROOT / OUTPUT_FOLDER_NAME

COMFY_LOG_FILES = [
    Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\user\comfyui_8188.log"),
    Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\user\comfyui.log")
]


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
    preset_file = row.get("preset_file", "").strip()

    filename_prefix = f"{OUTPUT_FOLDER_NAME}/{output_prefix}"
    has_preset = bool(preset_file)

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
                "clip": ["70", 1] if has_preset else ["37", 1],
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
                "model": ["70", 0] if has_preset else ["37", 0],
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

    if has_preset:
        wf["70"] = {
            "class_type": "ArthemyKrea2PresetLoader",
            "inputs": {
                "model": ["37", 0],
                "clip": ["37", 1],
                "preset": preset_file,
                "strength_model": 1.0,
                "strength_clip": 1.0,
                "custom_path": ""
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


def check_logs(save_capture: bool = True):
    active_log = None
    for p in COMFY_LOG_FILES:
        if p.exists() and p.stat().st_size > 0:
            active_log = p
            break

    if not active_log:
        print("ComfyUI log file not found.")
        return

    print("=" * 80)
    print(f"SCANNING COMFYUI LOG: {active_log}")
    print("=" * 80)

    preset_re = re.compile(r"Loaded Preset '([^']+)'")
    found_presets = {}
    captured_lines = []
    skipped_warnings = []

    with open(active_log, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "Loaded Preset" in line and "SwiGLU_rect" in line:
                captured_lines.append(line.strip())
                m = preset_re.search(line)
                if m:
                    found_presets[m.group(1)] = line.strip()
            if "skipped" in line and "SwiGLU_rect" in line:
                skipped_warnings.append(line.strip())
                captured_lines.append(line.strip())

    print(f"Found {len(found_presets)} SwiGLU rectified preset loading events in log:")
    for p, l in list(found_presets.items())[:10]:
        print(f"  {l}")
    if len(found_presets) > 10:
        print(f"  ... and {len(found_presets) - 10} more.")

    if skipped_warnings:
        print(f"\nWARNING: Found {len(skipped_warnings)} skipped patch warnings:")
        for w in skipped_warnings:
            print(f"  {w}")
    else:
        print("\nClean log: 0 skipped patch warnings found for SwiGLU rectified presets.")

    if save_capture:
        capture_path = TARGET_DIR / "tuner_logger_capture.log"
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
        with open(capture_path, "w", encoding="utf-8") as f:
            f.write("\n".join(captured_lines) + "\n")
        print(f"Tuner log capture saved to: {capture_path}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Queue SwiGLU Rectified Atlas renders.")
    parser.add_argument("--all", action="store_true", help="Queue all renders in data/swiglu_rectified_atlas_plan.csv.")
    parser.add_argument("--first", type=int, default=0, help="Queue only first N rows.")
    parser.add_argument("--check-only", action="store_true", help="Print plan and queue status without queuing.")
    parser.add_argument("--check-logs", action="store_true", help="Verify preset layer resolution in ComfyUI logs.")
    args = parser.parse_args()

    if args.check_logs:
        check_logs()
        return

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
            print(f"  Row {r['row_index']:>3s} | {r['arm']:17s} | {r['condition']:20s} | preset={r.get('preset_file', 'NONE'):26s} | {r['prompt_id']:15s} | {r['output_prefix']}")
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
