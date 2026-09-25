# -*- coding: utf-8 -*-
"""
experiments/queue_atlas_phase1.py
================================
Batch queuing script for Perturbation Atlas Phase 1 renders via ComfyUI API.
Follows ComfyUI Pilot Standard Generation Workflow:
  1. Workflow extracted directly from benchmark reference PNG metadata.
  2. Dynamic parameter injection (prompt, seed, preset, output prefix).
  3. Fast batch queuing via HTTP POST /prompt.
  4. Immediate queue verification via GET /queue.

Usage:
  python experiments/queue_atlas_phase1.py --check-only
      Queues ONLY the determinism check (S1 baseline seed 42).

  python experiments/queue_atlas_phase1.py --verify-determinism
      Checks SHA-256 of the freshly rendered check file against reference:
      08d0193a58aee459c41905029ef04fa795af9ff71cd20ff14fc2ba278e404637

  python experiments/queue_atlas_phase1.py --all
      Queues all 81 Phase 1 renders (3 baselines + 78 perturbations).
"""

from __future__ import annotations

import argparse
import csv
import json
import hashlib
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PLAN_CSV = DATA_DIR / "perturbation_atlas_phase1_plan.csv"

COMFY_HOST = "http://127.0.0.1:8188"
OUTPUT_DIR_NAME = "benchmark_atlas_phase1/renders"

REFERENCE_HASH = "08d0193a58aee459c41905029ef04fa795af9ff71cd20ff14fc2ba278e404637"
COMFY_OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")


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


def build_workflow_prompt(
    prompt_text: str,
    seed: int,
    steps: int,
    cfg: float,
    sampler_name: str,
    scheduler: str,
    denoise: float,
    width: int,
    height: int,
    preset_file: str,
    filename_prefix: str
) -> dict:
    """
    Builds the ComfyUI API prompt dictionary.
    If preset_file is provided, routes through ArthemyKrea2PresetLoader (node 70).
    If empty (baseline), connects ArthemyKrea2ResetPatcher (node 37) directly.
    """
    workflow = {
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
                "clip": ["70", 1] if preset_file else ["37", 1],
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
                "model": ["70", 0] if preset_file else ["37", 0],
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

    if preset_file:
        workflow["70"] = {
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

    return workflow


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


def verify_determinism() -> bool:
    check_file = COMFY_OUTPUT_ROOT / OUTPUT_DIR_NAME / "determinism_check_S1_photo_baseline_seed42_00001_.png"
    if not check_file.exists():
        # Fallback to standard filename if named without prefix
        check_file = COMFY_OUTPUT_ROOT / OUTPUT_DIR_NAME / "S1_photo_baseline_seed42_00001_.png"

    if not check_file.exists():
        print(f"[FAIL] Rendered file not found yet at {check_file}")
        return False

    with open(check_file, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    print(f"File checked: {check_file}")
    print(f"  Calculated SHA256: {file_hash}")
    print(f"  Reference  SHA256: {REFERENCE_HASH}")

    if file_hash == REFERENCE_HASH:
        print("\n>>> DETERMINISM CHECK: PASS! Bit-identical match verified. Environment is intact. <<<")
        return True
    else:
        print("\n>>> DETERMINISM CHECK: FAIL! Non-identical hash. Environment has drifted. STOP! <<<")
        return False


def main():
    parser = argparse.ArgumentParser(description="Queue Perturbation Atlas Phase 1 Renders in ComfyUI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check-only", action="store_true", help="Queue only determinism check")
    group.add_argument("--all", action="store_true", help="Queue all 81 Phase 1 renders")
    group.add_argument("--verify-determinism", action="store_true", help="Verify hash of determinism check render")

    args = parser.parse_args()

    if args.verify_determinism:
        ok = verify_determinism()
        sys.exit(0 if ok else 1)

    if not check_comfy_online():
        sys.exit(f"ERROR: ComfyUI server is not reachable at {COMFY_HOST}. Please start ComfyUI first.")

    with open(PLAN_CSV, encoding="utf-8") as f:
        plan_rows = list(csv.DictReader(f))

    if args.check_only:
        targets = [plan_rows[0]]
        print(f"Queuing DETERMINISM CHECK render (1 task)...")
    else:
        # Rows 2 to 82 (the 81 Phase 1 renders)
        targets = [r for r in plan_rows if r["type"] in ("baseline", "perturbation")]
        print(f"Queuing ALL PHASE 1 renders ({len(targets)} tasks)...")

    queued_count = 0
    for r in targets:
        row_type = r["type"]
        seed = int(r["seed"])
        steps = int(r["steps"])
        cfg = float(r["cfg"])
        denoise = float(r["denoise"])
        width = int(r["width"])
        height = int(r["height"])
        sampler = r["sampler"]
        scheduler = r["scheduler"]
        prompt_text = r["prompt_text"]
        preset_file = r["preset_file"]

        if row_type == "determinism_check":
            prefix = f"{OUTPUT_DIR_NAME}/determinism_check_{r['prompt_id']}_baseline_seed{seed}"
        elif row_type == "baseline":
            prefix = f"{OUTPUT_DIR_NAME}/{r['prompt_id']}_baseline_seed{seed}"
        else:
            p_stem = Path(preset_file).stem
            prefix = f"{OUTPUT_DIR_NAME}/{r['prompt_id']}_{p_stem}_seed{seed}"

        wf = build_workflow_prompt(
            prompt_text=prompt_text,
            seed=seed,
            steps=steps,
            cfg=cfg,
            sampler_name=sampler,
            scheduler=scheduler,
            denoise=denoise,
            width=width,
            height=height,
            preset_file=preset_file,
            filename_prefix=prefix
        )

        post_prompt(wf)
        queued_count += 1
        print(f"  [{queued_count}/{len(targets)}] Queued: {prefix}")

    print(f"\nVerifying queue count at {COMFY_HOST}/queue...")
    running, pending = get_queue_counts()
    print(f"ComfyUI Queue Status: Running={running}, Pending={pending}, Total Registered={running + pending}")
    print("\nBatch queuing completed successfully.")


if __name__ == "__main__":
    main()
