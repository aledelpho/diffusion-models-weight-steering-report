import sys
import argparse
import time
from typing import List, Tuple, Set
import urllib.request
import urllib.error
import json
import csv
from pathlib import Path

COMFY_HOST = "http://127.0.0.1:8188"
PLAN_CSV = Path(r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\prompt_order_experiment_plan_seed2.csv")
OUTPUT_FOLDER_NAME = "benchmark_prompt_order"
TARGET_DIR = Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_prompt_order\renders")

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
    prompt_text = row["prompt"]
    seed = int(row["base_seed"])
    steps = int(row["steps"])
    cfg = float(row["cfg"])
    sampler_name = row["sampler"]
    scheduler = row["scheduler"]
    denoise = float(row.get("denoise", 1.0))
    width = int(row["width"])
    height = int(row["height"])
    output_prefix = row["filename_prefix"]
    vectors_override = row.get("vector", "").strip()
    mode = "Real Value"

    filename_prefix = f"{OUTPUT_FOLDER_NAME}/{output_prefix}"
    is_perturbed = row['cond_id'] != 'baseline'

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


def main():
    if not TARGET_DIR.exists():
        TARGET_DIR.mkdir(parents=True)
        
    rows = []
    with open(PLAN_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    print(f"Total target renders:       {len(rows)}")

    print(f"\nQueuing renders to ComfyUI at {COMFY_HOST}...")
    queued_count = 0
    t0 = time.time()

    for idx, r in enumerate(rows, 1):
        target_path = TARGET_DIR / r["expected_filename"]
        if target_path.exists() and target_path.stat().st_size > 1000:
            continue
        wf = build_workflow(r)
        pid = post_prompt(wf)
        queued_count += 1
        print(f"[{idx}/{len(rows)}] Queued prompt {pid} ({r['filename_prefix']})")

    elapsed = time.time() - t0
    print(f"\nSuccessfully queued {queued_count} tasks in {elapsed:.2f}s.")

    running, pending = get_queue_counts()
    print(f"ComfyUI Queue Verification: {running} running, {pending} pending tasks in queue.")


if __name__ == "__main__":
    main()
