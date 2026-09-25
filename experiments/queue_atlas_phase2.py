# -*- coding: utf-8 -*-
"""
experiments/queue_atlas_phase2.py
================================
Batch queuing script for Perturbation Atlas Phase 2 renders (567 tasks).
Queues S2_watercolor through S8_charcoal grouped by preset to minimize
model patching and weight reloads in ComfyUI.

Usage:
  python experiments/queue_atlas_phase2.py
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
PLAN_CSV = DATA_DIR / "perturbation_atlas_phase2_plan.csv"

COMFY_HOST = "http://127.0.0.1:8188"
OUTPUT_DIR_NAME = "benchmark_atlas_phase1/renders"


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


def main():
    if not check_comfy_online():
        sys.exit(f"ERROR: ComfyUI server is not reachable at {COMFY_HOST}.")

    with open(PLAN_CSV, encoding="utf-8") as f:
        plan_rows = list(csv.DictReader(f))

    print(f"Queuing PHASE 2 renders ({len(plan_rows)} tasks grouped by preset)...")

    queued_count = 0
    current_preset = None

    for r in plan_rows:
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
        prompt_id = r["prompt_id"]

        if row_type == "baseline":
            prefix = f"{OUTPUT_DIR_NAME}/{prompt_id}_baseline_seed{seed}"
            group_label = "[BASELINE]"
        else:
            p_stem = Path(preset_file).stem
            prefix = f"{OUTPUT_DIR_NAME}/{prompt_id}_{p_stem}_seed{seed}"
            group_label = f"[{p_stem}]"

        if preset_file != current_preset:
            current_preset = preset_file
            print(f"\n--- Loading group {group_label} ---")

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
        if queued_count % 21 == 0 or queued_count == len(plan_rows):
            print(f"  [{queued_count}/{len(plan_rows)}] tasks sent to queue")

    print(f"\nVerifying queue count at {COMFY_HOST}/queue...")
    running, pending = get_queue_counts()
    print(f"ComfyUI Queue Status: Running={running}, Pending={pending}, Total Registered in ComfyUI={running + pending}")
    print("\nPhase 2 batch queuing completed successfully.")


if __name__ == "__main__":
    main()
