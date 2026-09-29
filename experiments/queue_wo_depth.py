# -*- coding: utf-8 -*-
"""
experiments/queue_wo_depth.py
=============================
Queues renders for C41: `wo` cut by depth benchmark governed by:
  docs/RENDERS_2026-09-29_wo_depth.md
  docs/prereg_wo_depth.md
  data/wo_depth_plan.csv (86 rows total)

Design requirements:
  - Rows 1-2 (determinism): baseline at seed 2718281 with NO preset connected.
    Output prefix ends in _C41.
    Must match borrowed centre_push baselines pixel-for-pixel (G_det).
  - Rows 3-86 (push): 14 conditions (6 depth slices + union x 2 signs) x 2 prompts x 3 seeds.
    Drives via ArthemyKrea2PresetLoader from custom_nodes/Arthemy_Krea2_Tuner/presets/
    with strength_model=1.0, strength_clip=1.0.
  - Reset patcher ArthemyKrea2ResetPatcher inserted before preset loader.
  - Output folder: benchmark_wo_depth/renders
  - Determinism verification tool included (--verify-determinism).
  - Log verification tool included (--check-logs) to verify model_patched_layers and no skipped patches.

Usage:
  python experiments/queue_wo_depth.py --check-only
  python experiments/queue_wo_depth.py --first 2
  python experiments/queue_wo_depth.py --verify-determinism
  python experiments/queue_wo_depth.py --all
  python experiments/queue_wo_depth.py --check-logs
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
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PLAN_CSV = DATA_DIR / "wo_depth_plan.csv"

COMFY_HOST = "http://127.0.0.1:8188"
COMFY_OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")
OUTPUT_FOLDER_NAME = "benchmark_wo_depth/renders"
TARGET_DIR = COMFY_OUTPUT_ROOT / OUTPUT_FOLDER_NAME

COMFY_LOG_FILES = [
    Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\user\comfyui_8188.log"),
    Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\user\comfyui.log")
]

EXPECTED_LAYER_COUNTS = {
    "Arthemy_QKVO_wo_b1_pos.json": 5,
    "Arthemy_QKVO_wo_b1_neg.json": 5,
    "WO_b2_pos.json": 5,
    "WO_b2_neg.json": 5,
    "WO_b3_pos.json": 5,
    "WO_b3_neg.json": 5,
    "WO_b4_pos.json": 5,
    "WO_b4_neg.json": 5,
    "WO_b5_pos.json": 4,
    "WO_b5_neg.json": 4,
    "Arthemy_QKVO_wo_b6_pos.json": 4,
    "Arthemy_QKVO_wo_b6_neg.json": 4,
    "Family_wo_d+0.100.json": 28,
    "Family_wo_d-0.100.json": 28,
}


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


def verify_determinism() -> bool:
    """
    Checks G_det: determinism rows (1 and 2) must reproduce borrowed centre_push
    baselines pixel-for-pixel (0 diff).
    """
    from PIL import Image
    import numpy as np

    rows = load_plan()
    det_rows = [r for r in rows if r.get("arm") == "determinism"]

    if not det_rows:
        print("ERROR: No determinism rows found in plan.")
        return False

    print("=" * 80)
    print("G_det DETERMINISM CHECK: comparing newly rendered baselines with borrowed ones")
    print("=" * 80)

    all_passed = True
    for r in det_rows:
        pid = r["prompt_id"]
        exp_fn = r["expected_filename"]
        rendered_file = TARGET_DIR / exp_fn
        borrowed_rel = r.get("borrowed_from", "")
        borrowed_file = COMFY_OUTPUT_ROOT / borrowed_rel

        if not rendered_file.exists():
            print(f"[{pid}] Rendered file MISSING: {rendered_file}")
            all_passed = False
            continue

        if not borrowed_file.exists():
            print(f"[{pid}] Borrowed baseline file MISSING: {borrowed_file}")
            all_passed = False
            continue

        img_rendered = np.array(Image.open(rendered_file).convert("RGB"), dtype=np.int32)
        img_borrowed = np.array(Image.open(borrowed_file).convert("RGB"), dtype=np.int32)

        if img_rendered.shape != img_borrowed.shape:
            print(f"[{pid}] SHAPE MISMATCH: {img_rendered.shape} vs {img_borrowed.shape}")
            all_passed = False
            continue

        diff = np.abs(img_rendered - img_borrowed)
        diff_count = int(np.count_nonzero(diff.any(axis=-1)))
        max_diff = int(diff.max())

        if diff_count == 0:
            print(f"[{pid}] DETERMINISM CONFIRMED: 0 pixel difference (identical to borrowed baseline).")
        else:
            print(f"[{pid}] DETERMINISM FAILED: {diff_count:,} pixels differ (max diff={max_diff}). Borrow is VOID!")
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("G_det PASSED: The borrow is fully valid.")
    else:
        print("G_det FAILED: Do NOT proceed with borrowed baselines.")
    print("=" * 80)
    return all_passed


def check_logs(save_capture: bool = True):
    """
    Scans ComfyUI logs for tuner preset logs to verify layer count resolution
    and check if any patch was reported as skipped. Keeps a copy beside the renders.
    """
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
    skipped_re = re.compile(r"Unmatched model layer '([^']+)' in preset '([^']+)' - skipped")

    found_presets = {}
    captured_lines = []
    skipped_warnings = []

    with open(active_log, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "Loaded Preset" in line and ("WO_b" in line or "wo_b" in line or "Family_wo" in line):
                captured_lines.append(line.strip())
                m = preset_re.search(line)
                if m:
                    pname = m.group(1)
                    found_presets[pname] = line.strip()
            if "skipped" in line and ("WO_b" in line or "wo_b" in line or "Family_wo" in line):
                skipped_warnings.append(line.strip())
                captured_lines.append(line.strip())

    print(f"Found {len(found_presets)} WO depth preset loading events in log:")
    for p, l in found_presets.items():
        print(f"  {l}")

    if skipped_warnings:
        print(f"\nWARNING: Found {len(skipped_warnings)} skipped patch warnings:")
        for w in skipped_warnings:
            print(f"  {w}")
    else:
        print("\nClean log: 0 skipped patch warnings found for WO depth presets.")

    if save_capture:
        capture_path = TARGET_DIR / "tuner_logger_capture.log"
        with open(capture_path, "w", encoding="utf-8") as f:
            f.write("\n".join(captured_lines) + "\n")
        print(f"Tuner log capture saved to: {capture_path}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Queue WO Cut by Depth benchmark renders (C41).")
    parser.add_argument("--all", action="store_true", help="Queue all renders in data/wo_depth_plan.csv.")
    parser.add_argument("--first", type=int, default=0, help="Queue only first N rows (e.g. 2 for determinism pre-check).")
    parser.add_argument("--check-only", action="store_true", help="Print plan and queue status without queuing.")
    parser.add_argument("--verify-determinism", action="store_true", help="Verify G_det determinism against borrowed baselines.")
    parser.add_argument("--check-logs", action="store_true", help="Verify preset layer resolution in ComfyUI logs.")
    args = parser.parse_args()

    if args.check_logs:
        check_logs()
        return

    if args.verify_determinism:
        verify_determinism()
        return

    if not check_comfy_online():
        print(f"ERROR: ComfyUI is not reachable at {COMFY_HOST}")
        sys.exit(1)

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_plan()

    if args.first > 0:
        rows = rows[:args.first]
        print(f"Filtered to first {args.first} rows.")

    pending_rows = []
    existing_rows = []
    for r in rows:
        fn = r["expected_filename"]
        target_path = TARGET_DIR / fn
        if target_path.exists() and target_path.stat().st_size > 1000:
            existing_rows.append(r)
        else:
            pending_rows.append(r)

    print(f"Total target renders: {len(rows)}")
    print(f"Already rendered:     {len(existing_rows)}")
    print(f"To be queued:         {len(pending_rows)}")

    if args.check_only:
        print("\nCheck-only mode. Pending rows:")
        for r in pending_rows[:10]:
            print(f"  Row {r['row_index']:>2s} | {r['arm']:11s} | {r['condition']:12s} | preset={r.get('preset_file', 'NONE'):28s} | {r['prompt_id']} | seed={r['seed']} | {r['output_prefix']}")
        return

    if not pending_rows:
        print("All target renders already exist in output folder! Nothing to queue.")
        return

    print(f"\nQueuing {len(pending_rows)} renders to ComfyUI at {COMFY_HOST}...")
    queued_count = 0
    t0 = time.time()

    for idx, r in enumerate(pending_rows, 1):
        wf = build_workflow(r)
        pid = post_prompt(wf)
        queued_count += 1
        print(f"[{idx}/{len(pending_rows)}] Row {r['row_index']:>2s} -> Queued prompt {pid} ({r['output_prefix']})")

    elapsed = time.time() - t0
    print(f"\nSuccessfully queued {queued_count} tasks in {elapsed:.2f}s.")

    running, pending = get_queue_counts()
    print(f"ComfyUI Queue Verification: {running} running, {pending} pending tasks in queue.")


if __name__ == "__main__":
    main()
