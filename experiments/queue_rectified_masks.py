# -*- coding: utf-8 -*-
"""
experiments/queue_rectified_masks.py
====================================
Queues the 72 renders specified in docs/RENDERS_2026-09-27_rectified_masks_3.md.
Uses data/rectified_mask_plan.csv to configure ArthemyKrea2ModelTuner with vectors_override (34 slots).
Renders are grouped by condition to minimize patching and VRAM churn.

Usage:
  python experiments/queue_rectified_masks.py
"""

from __future__ import annotations

import csv
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PLAN_CSV = DATA_DIR / "rectified_mask_plan.csv"

COMFY_HOST = "http://127.0.0.1:8188"
OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")


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


def build_workflow(
    prompt_text: str,
    seed: int,
    steps: int,
    cfg: float,
    sampler_name: str,
    scheduler: str,
    denoise: float,
    width: int,
    height: int,
    vectors_override: str,
    filename_prefix: str
) -> dict:
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
        },
        "50": {
            "class_type": "ArthemyKrea2ModelTuner",
            "inputs": {
                "model": ["37", 0],
                "mode": "Real Value",
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
        },
        "42": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["50", 0],
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
    if not check_comfy_online():
        sys.exit(f"ERROR: ComfyUI server is not reachable at {COMFY_HOST}. Start ComfyUI first.")

    if not PLAN_CSV.exists():
        sys.exit(f"ERROR: Plan file {PLAN_CSV} not found.")

    with open(PLAN_CSV, encoding="utf-8") as f:
        plan_rows = list(csv.DictReader(f))

    print(f"Loaded {len(plan_rows)} tasks from {PLAN_CSV}.")

    initial_running, initial_pending = get_queue_counts()
    print(f"Current ComfyUI Queue: Running={initial_running}, Pending={initial_pending}")

    queued_count = 0
    skipped_count = 0
    current_condition = None

    for r in plan_rows:
        expected_file = OUTPUT_ROOT / r["output_prefix"]
        # Expected file with 00001_.png
        target_png = expected_file.parent / (expected_file.name + "_00001_.png")
        if target_png.exists():
            skipped_count += 1
            continue

        cond = r["condition"]
        if cond != current_condition:
            current_condition = cond
            print(f"\n--- Loading Condition [{current_condition}] ---")

        seed = int(r["seed"])
        steps = int(r["steps"])
        cfg = float(r["cfg"])
        denoise = float(r["denoise"])
        width = int(r["width"])
        height = int(r["height"])
        sampler = r["sampler"]
        scheduler = r["scheduler"]
        prompt_text = r["prompt_text"]
        prefix = r["output_prefix"]
        vectors_override = r["vectors_override"]

        wf = build_workflow(
            prompt_text=prompt_text,
            seed=seed,
            steps=steps,
            cfg=cfg,
            sampler_name=sampler,
            scheduler=scheduler,
            denoise=denoise,
            width=width,
            height=height,
            vectors_override=vectors_override,
            filename_prefix=prefix
        )

        post_prompt(wf)
        queued_count += 1
        print(f"  [{queued_count}/{len(plan_rows) - skipped_count}] Queued: {prefix}")

    print(f"\nQueuing complete: Queued={queued_count}, Skipped={skipped_count} (already on disk)")
    final_running, final_pending = get_queue_counts()
    print(f"ComfyUI Queue Status: Running={final_running}, Pending={final_pending} (Total in queue: {final_running + final_pending})")


if __name__ == "__main__":
    main()
