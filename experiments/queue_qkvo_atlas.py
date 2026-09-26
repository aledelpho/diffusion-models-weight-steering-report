# -*- coding: utf-8 -*-
"""
experiments/queue_qkvo_atlas.py
===============================
Batch queuing script for QKVO Atlas renders via ComfyUI API (RUNBOOK_qkvo_atlas_plan_1.md §7.3, §7.5).
  - Resumable: skips any render whose expected_filename already exists in output folder.
  - Determinism check: verifies S1_photo baseline seed 42 against benchmark_atlas_phase1 reference.
  - Groups renders by preset to minimize model reload / unet patching churn.
  - Writes data/qkvo_atlas_progress.log with timestamps for each completed image.

Usage:
  python experiments/queue_qkvo_atlas.py --check-only
  python experiments/queue_qkvo_atlas.py --verify-determinism
  python experiments/queue_qkvo_atlas.py --all
  python experiments/queue_qkvo_atlas.py --monitor
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PLAN_CSV = DATA_DIR / "qkvo_atlas_plan.csv"
PROGRESS_LOG = DATA_DIR / "qkvo_atlas_progress.log"

COMFY_HOST = "http://127.0.0.1:8188"
OUTPUT_DIR_NAME = "benchmark_qkvo_atlas/renders"

COMFY_OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")
TARGET_DIR = COMFY_OUTPUT_ROOT / OUTPUT_DIR_NAME
REF_BASELINE_FILE = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_atlas_phase1\renders\S1_photo_baseline_seed42_00001_.png")


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


def verify_determinism() -> Tuple[bool, int, int]:
    """
    Checks the freshly rendered S1 baseline against reference.
    Returns: (is_zero_diff, max_diff, diff_pixel_count)
    """
    from PIL import Image
    import numpy as np

    check_file = TARGET_DIR / "determinism_check_S1_photo_baseline_seed42_00001_.png"
    if not check_file.exists():
        check_file = TARGET_DIR / "S1_photo_baseline_seed42_00001_.png"

    if not check_file.exists():
        print(f"[FAIL] Rendered check file not found yet at {check_file}")
        return False, -1, -1

    if not REF_BASELINE_FILE.exists():
        print(f"[FAIL] Reference baseline file not found at {REF_BASELINE_FILE}")
        return False, -1, -1

    img_new = Image.open(check_file)
    img_ref = Image.open(REF_BASELINE_FILE)

    arr_new = np.array(img_new)
    arr_ref = np.array(img_ref)

    diff = np.abs(arr_new.astype(int) - arr_ref.astype(int))
    max_diff = int(np.max(diff))
    diff_count = int(np.sum(diff > 0))

    pixel_hash_new = hashlib.sha256(arr_new.tobytes()).hexdigest()
    pixel_hash_ref = hashlib.sha256(arr_ref.tobytes()).hexdigest()

    print(f"\n=== DETERMINISM CHECK VERIFICATION (§7.3) ===")
    print(f"File checked: {check_file.name}")
    print(f"  Pixel SHA256 (NEW): {pixel_hash_new}")
    print(f"  Pixel SHA256 (REF): {pixel_hash_ref}")
    print(f"  Max pixel diff:     {max_diff}")
    print(f"  Different pixels:   {diff_count} / {arr_new.size // 3}")

    is_exact = (max_diff == 0)
    if is_exact:
        print(">>> RESULT: ZERO pixel difference. The 8 existing baselines are reusable! <<<")
    else:
        print(f">>> RESULT: NON-ZERO pixel difference (max diff {max_diff}). 24 baselines must be rendered! <<<")

    return is_exact, max_diff, diff_count


def queue_single_row(r: dict) -> str:
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

    if row_type == "determinism_check":
        prefix = f"{OUTPUT_DIR_NAME}/determinism_check_{prompt_id}_baseline_seed{seed}"
    elif row_type == "baseline":
        prefix = f"{OUTPUT_DIR_NAME}/{prompt_id}_baseline_seed{seed}"
    else:
        p_stem = Path(preset_file).stem
        prefix = f"{OUTPUT_DIR_NAME}/{prompt_id}_{p_stem}_seed{seed}"

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
    return post_prompt(wf)


def log_progress(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    with open(PROGRESS_LOG, "a", encoding="utf-8") as fh:
        fh.write(line)
    print(f"  {line.strip()}", flush=True)


def monitor_queue(total_expected: int):
    """Monitors completion of renders in TARGET_DIR and logs them."""
    print(f"\n=== MONITORING QKVO ATLAS RENDERS ({total_expected} total) ===")
    seen_files = set()
    if TARGET_DIR.exists():
        for f in TARGET_DIR.glob("*.png"):
            seen_files.add(f.name)

    while True:
        running, pending = get_queue_counts()
        current_files = set(f.name for f in TARGET_DIR.glob("*.png")) if TARGET_DIR.exists() else set()
        new_files = current_files - seen_files

        for nf in sorted(new_files):
            seen_files.add(nf)
            log_progress(f"COMPLETED: {nf} ({len(seen_files)}/{total_expected})")

        if running == 0 and pending == 0:
            print(f"\nAll tasks finished processing in ComfyUI.")
            print(f"Total files on disk: {len(seen_files)}/{total_expected}")
            break

        time.sleep(5)


def main():
    parser = argparse.ArgumentParser(description="Queue QKVO Atlas Renders in ComfyUI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check-only", action="store_true", help="Queue only determinism check row")
    group.add_argument("--verify-determinism", action="store_true", help="Verify determinism check render against reference")
    group.add_argument("--all", action="store_true", help="Queue all planned renders (resumable)")
    group.add_argument("--monitor", action="store_true", help="Monitor output directory and update progress log")

    args = parser.parse_args()

    if args.verify_determinism:
        ok, max_d, diff_cnt = verify_determinism()
        sys.exit(0 if ok else 1)

    if not check_comfy_online():
        sys.exit(f"ERROR: ComfyUI server is not reachable at {COMFY_HOST}. Start ComfyUI first.")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    with open(PLAN_CSV, encoding="utf-8") as f:
        plan_rows = list(csv.DictReader(f))

    if args.check_only:
        r0 = plan_rows[0]
        print(f"Queuing DETERMINISM CHECK render (S1_photo seed 42)...")
        queue_single_row(r0)
        running, pending = get_queue_counts()
        print(f"Queued. ComfyUI status: Running={running}, Pending={pending}")
        return

    if args.monitor:
        total = len(plan_rows) - 1
        monitor_queue(total)
        return

    if args.all:
        print("=== AVVIO CODA QKVO ATLAS (RUNBOOK §7.5) ===")
        # Step A: Determinism Check
        check_file = TARGET_DIR / "determinism_check_S1_photo_baseline_seed42_00001_.png"
        need_check = not check_file.exists()
        if need_check:
            print("Esecuzione determinism check iniziale...")
            queue_single_row(plan_rows[0])
            # Wait for check file to appear
            print("In attesa del render determinism check...", end="", flush=True)
            for _ in range(60):
                if check_file.exists():
                    break
                time.sleep(2)
                print(".", end="", flush=True)
            print()

        is_zero_diff, max_diff, diff_cnt = verify_determinism()

        extra_baseline_rows = []
        if not is_zero_diff:
            print("\n[ATTENZIONE] Il determinism check ha rilevato drift. Aggiunta delle 24 baselines al batch (§7.3)...")
            # Build 24 baseline rows (8 prompts x 3 seeds)
            with open(DATA_DIR / "stage9_prompts.json", encoding="utf-8") as pf:
                all_prompts = json.load(pf)
            for p in all_prompts:
                for s in [42, 777, 1337]:
                    extra_baseline_rows.append({
                        "type": "baseline",
                        "condition": "baseline",
                        "preset_file": "",
                        "prompt_id": p["prompt_id"],
                        "seed": s,
                        "steps": 9, "cfg": 1.0, "denoise": 1.0, "sampler": "euler_ancestral", "scheduler": "simple",
                        "width": 1024, "height": 1280,
                        "prompt_text": p["text"],
                        "expected_filename": f"{p['prompt_id']}_baseline_seed{s}_00001_.png"
                    })

        # Step B: Resumable batch queuing of all conditions
        tasks_to_queue = extra_baseline_rows + [r for r in plan_rows if r["type"] in ("control", "perturbed")]
        total_tasks = len(tasks_to_queue)
        print(f"\nVerifica file su disco e accodamento resumabile ({total_expected if 'total_expected' in dir() else total_tasks} tasks)...")

        skipped_count = 0
        queued_count = 0

        for r in tasks_to_queue:
            exp_fn = r["expected_filename"]
            target_path = TARGET_DIR / exp_fn
            if target_path.exists():
                skipped_count += 1
                continue

            queue_single_row(r)
            queued_count += 1
            if queued_count % 24 == 0 or queued_count == (total_tasks - skipped_count):
                print(f"  [{queued_count + skipped_count}/{total_tasks}] Accodati: {queued_count}, Già completati: {skipped_count}", flush=True)

        print(f"\nAccodamento completato:")
        print(f"  - File già presenti (skippati): {skipped_count}")
        print(f"  - Nuovi compiti inviati alla coda: {queued_count}")

        running, pending = get_queue_counts()
        print(f"Stato coda ComfyUI: Running={running}, Pending={pending}, Totale registrati={running + pending}")

        # Write header to progress log
        log_progress(f"BATCH LAUNCHED: {queued_count} tasks queued, {skipped_count} skipped, {running + pending} in ComfyUI queue.")

        # Avvio del monitor per seguire il completamento
        monitor_queue(total_tasks)


if __name__ == "__main__":
    main()
