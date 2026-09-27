# -*- coding: utf-8 -*-
"""
experiments/queue_colour_object_sweep.py
=======================================
Queues Stage 2 block sweep renders (78 tasks) via ComfyUI API.
Governed by docs/RENDERS_2026-09-27_colour_object_pilot.md (§3).

Usage:
  python experiments/queue_colour_object_sweep.py
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
PLAN_CSV = DATA_DIR / "colour_object_sweep_plan.csv"

COMFY_HOST = "http://127.0.0.1:8188"


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


def build_sweep_workflow(
    prompt_text: str,
    seed: int,
    steps: int,
    cfg: float,
    sampler_name: str,
    scheduler: str,
    denoise: float,
    width: int,
    height: int,
    block_name: str,
    gain: float,
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
        }
    }

    if block_name != "none" and gain != 0.0:
        # Connect ArthemyKrea2ModelTuner (node 50)
        tuner_inputs = {
            "model": ["37", 0],
            "mode": "Real Value",
            "vectors_override": "",
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
        tuner_inputs[block_name] = float(gain)

        wf["50"] = {
            "class_type": "ArthemyKrea2ModelTuner",
            "inputs": tuner_inputs
        }
        model_source = ["50", 0]
    else:
        model_source = ["37", 0]

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
    if not check_comfy_online():
        sys.exit(f"ERROR: ComfyUI server is not reachable at {COMFY_HOST}. Start ComfyUI first.")

    with open(PLAN_CSV, encoding="utf-8") as f:
        plan_rows = list(csv.DictReader(f))

    COMFY_OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")
    queued_count = 0
    skipped_count = 0
    current_block_sign = None

    for r in plan_rows:
        prefix = r["output_prefix"]
        target_png = COMFY_OUTPUT_ROOT / (prefix + "_00001_.png")
        if target_png.exists():
            skipped_count += 1
            continue

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
        block = r["block"]
        gain = float(r["gain"])

        tag = f"{block}_{r['sign']}" if row_type == "perturbed" else "baseline"
        if tag != current_block_sign:
            current_block_sign = tag
            print(f"\n--- Loading group [{current_block_sign}] (gain={gain:.3f}) ---")

        wf = build_sweep_workflow(
            prompt_text=prompt_text,
            seed=seed,
            steps=steps,
            cfg=cfg,
            sampler_name=sampler,
            scheduler=scheduler,
            denoise=denoise,
            width=width,
            height=height,
            block_name=block,
            gain=gain,
            filename_prefix=prefix
        )

        post_prompt(wf)
        queued_count += 1
        print(f"  [{queued_count}/{len(plan_rows) - skipped_count}] Queued: {prefix}")

    print(f"\nQueuing complete: Queued={queued_count}, Skipped={skipped_count} (already on disk)")
    print(f"\nVerifying queue count at {COMFY_HOST}/queue...")
    running, pending = get_queue_counts()
    print(f"ComfyUI Queue Status: Running={running}, Pending={pending}, Total Registered in ComfyUI={running + pending}")
    print("\nStage 2 sweep batch queuing completed successfully.")


if __name__ == "__main__":
    main()
