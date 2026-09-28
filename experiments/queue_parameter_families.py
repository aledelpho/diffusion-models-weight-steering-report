# -*- coding: utf-8 -*-
"""
experiments/queue_parameter_families.py
=======================================
Queues renders for parameter families benchmark governed by:
  docs/RENDERS_2026-09-28_parameter_families.md
  data/family_bench_plan.csv

Design requirements:
  - Two-stage architecture:
      Stage 1 (Gate): 12 renders (6 families, delta=+1.00, P01 & P02, seed 42).
      Stage 2 (Ladder): <= 144 renders (advancing families that moved in Stage 1 + F_wo reference).
  - Drives via ArthemyKrea2PresetLoader from custom_nodes/Arthemy_Krea2_Tuner/presets/
    with strength_model=1.0, strength_clip=1.0.
  - Reset patcher ArthemyKrea2ResetPatcher inserted before preset loader.
  - Prompts P01 and P02 mapped to canonical benchmark prompt texts.
  - Output folder: benchmark_parameter_families/renders
  - Decoded-pixel gate evaluation tool included (--evaluate-gate) against benchmark_mappa baselines.
  - Log verification tool included (--check-logs) to verify model_patched_layers and no skipped patches.

Usage:
  python experiments/queue_parameter_families.py --stage 1
  python experiments/queue_parameter_families.py --evaluate-gate
  python experiments/queue_parameter_families.py --stage 2
  python experiments/queue_parameter_families.py --check-logs
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
from typing import Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PLAN_CSV = DATA_DIR / "family_bench_plan.csv"

COMFY_HOST = "http://127.0.0.1:8188"
COMFY_OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")
OUTPUT_FOLDER_NAME = "benchmark_parameter_families/renders"
TARGET_DIR = COMFY_OUTPUT_ROOT / OUTPUT_FOLDER_NAME
MAPPA_DIR = COMFY_OUTPUT_ROOT / "benchmark_mappa" / "renders"
COMFY_LOG_FILES = [
    Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\user\comfyui_8188.log"),
    Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\user\comfyui.log")
]

PROMPTS = {
    "P01": (
        "Western comics style, bold ink outlines, hatched shadows, medium wide shot, "
        "static centred composition, eye-level camera, subject centred and filling the middle third of the frame. "
        "A blacksmith woman stands behind a heavy oak workbench, facing the viewer, both hands resting flat on the wood. "
        "She has coarse dark curls tied back, weathered brown skin, a leather apron over a coarse linen shirt, "
        "and a polished steel gauntlet on her left forearm. On the bench lie a hammered copper bowl, a coil of frayed rope, "
        "and three rough granite offcuts. Behind her on the left a forge fire glows with a warm orange to deep red gradient, "
        "and thin smoke rises against a flat dark stone wall on the right. Cold blue window light falls from the upper left across the steel."
    ),
    "P02": (
        "Western comics style, bold ink outlines, hatched shadows, medium wide shot, "
        "static centred composition, eye-level camera, subject centred and filling the middle third of the frame. "
        "A botanist man stands among potting benches, facing the viewer, one hand on a terracotta pot. "
        "He has straight pale hair, freckled fair skin, a knitted wool cardigan over a cotton shirt, "
        "and small round glasses. Broad waxy monstera leaves crowd the left of the frame and fine ferns the right. "
        "A glass carafe half full of water sits on the bench in front of him, beside damp dark soil and a brass watering can. "
        "Behind him the greenhouse panes show a pale cyan to warm cream sky gradient, with condensation beading on the glass."
    ),
}

BASELINES = {
    "P01": MAPPA_DIR / "P01_baseline_krea2_seed42_00001_.png",
    "P02": MAPPA_DIR / "P02_baseline_krea2_seed42_00001_.png",
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
    prompt_id = row["prompt_id"]
    prompt_text = PROMPTS[prompt_id]
    seed = int(row["seed"])
    steps = int(row["steps"])
    cfg = float(row["cfg"])
    sampler_name = row["sampler"]
    scheduler = row["scheduler"]
    denoise = float(row.get("denoise", 1.0))
    width = int(row["width"])
    height = int(row["height"])
    output_prefix = row["output_prefix"]
    preset_file = row["preset"]

    filename_prefix = f"{OUTPUT_FOLDER_NAME}/{output_prefix}"

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
        "70": {
            "class_type": "ArthemyKrea2PresetLoader",
            "inputs": {
                "model": ["37", 0],
                "clip": ["37", 1],
                "preset": preset_file,
                "strength_model": 1.0,
                "strength_clip": 1.0,
                "custom_path": ""
            }
        },
        "40": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["70", 1],
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
                "model": ["70", 0],
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


def load_plan(stage_filter: Optional[str] = None) -> List[dict]:
    rows = []
    with open(PLAN_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if stage_filter and r["stage"] != stage_filter:
                continue
            rows.append(r)
    return rows


def evaluate_gate() -> Dict[str, dict]:
    """
    Evaluates Stage 1 Gate: compares numpy arrays of decoded pixels between
    the gate render and its baseline in benchmark_mappa.
    Returns: dict of family -> {
        'moved': bool,
        'p01_diff': int,
        'p02_diff': int,
        'details': str
    }
    """
    from PIL import Image
    import numpy as np

    gate_rows = load_plan(stage_filter="1_gate")
    results = {}

    for pid, base_path in BASELINES.items():
        if not base_path.exists():
            print(f"ERROR: Baseline file not found: {base_path}")
            return {}

    base_images = {
        pid: np.array(Image.open(path).convert("RGB"), dtype=np.int32)
        for pid, path in BASELINES.items()
    }

    # Group gate rows by family
    family_rows: Dict[str, List[dict]] = {}
    for r in gate_rows:
        fam = r["family"]
        family_rows.setdefault(fam, []).append(r)

    print("=" * 80)
    print("STAGE 1 GATE EVALUATION (Pixel content vs benchmark_mappa baselines)")
    print("=" * 80)

    for fam, f_rows in family_rows.items():
        fam_moved = False
        diff_info = {}
        missing_count = 0

        for r in f_rows:
            pid = r["prompt_id"]
            expected_fn = r["expected_filename"]
            rendered_path = TARGET_DIR / expected_fn

            if not rendered_path.exists():
                missing_count += 1
                diff_info[pid] = "MISSING"
                continue

            img_arr = np.array(Image.open(rendered_path).convert("RGB"), dtype=np.int32)
            base_arr = base_images[pid]

            if img_arr.shape != base_arr.shape:
                diff_info[pid] = f"SHAPE_MISMATCH ({img_arr.shape} vs {base_arr.shape})"
                fam_moved = True
                continue

            diff = np.abs(img_arr - base_arr)
            pixel_diff_count = int(np.count_nonzero(diff.any(axis=-1)))
            max_diff = int(diff.max())
            mean_diff = float(diff.mean())

            if pixel_diff_count > 0:
                fam_moved = True
                diff_info[pid] = f"DIFF: {pixel_diff_count:,} px, max={max_diff}, mean={mean_diff:.4f}"
            else:
                diff_info[pid] = "IDENTICAL (0 diff)"

        results[fam] = {
            "moved": fam_moved,
            "missing": missing_count,
            "diff_info": diff_info
        }

        status = "PASSED (MOVED)" if fam_moved else ("WAITING (FILES MISSING)" if missing_count > 0 else "FAILED / NULL (0 DIFF)")
        print(f"Family {fam:10s} : {status}")
        for pid, info in diff_info.items():
            print(f"    {pid}: {info}")

    print("=" * 80)
    # Check predictions G1, G2, G3
    print("PREDICTIONS SUMMARY:")
    if "F_wo" in results:
        r = results["F_wo"]
        print(f"  G1 (F_wo must move): {'CONFIRMED' if r['moved'] else 'FALSIFIED (STOP, PIPELINE BROKEN)'}")
    if "F_norms" in results:
        r = results["F_norms"]
        print(f"  G2 (F_norms must NOT move): {'CONFIRMED (0 diff)' if not r['moved'] and r['missing'] == 0 else 'MOVED / UNVERIFIED'}")
    return results


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

    preset_re = re.compile(r"Loaded Preset '(Family_[^']+)'")
    skipped_re = re.compile(r"Unmatched model layer '([^']+)' in preset '([^']+)' - skipped")

    found_presets = {}
    captured_lines = []
    skipped_warnings = []

    with open(active_log, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "Loaded Preset" in line and "Family_" in line:
                captured_lines.append(line.strip())
                m = preset_re.search(line)
                if m:
                    pname = m.group(1)
                    found_presets[pname] = line.strip()
            if "skipped" in line and "Family_" in line:
                skipped_warnings.append(line.strip())
                captured_lines.append(line.strip())

    print(f"Found {len(found_presets)} Family preset loading events in log.")
    for p, l in found_presets.items():
        print(f"  {l}")

    if skipped_warnings:
        print(f"\nWARNING: Found {len(skipped_warnings)} skipped patch warnings:")
        for w in skipped_warnings:
            print(f"  {w}")
    else:
        print("\nClean log: 0 skipped patch warnings found for Family presets.")

    if save_capture:
        capture_path = TARGET_DIR / "tuner_logger_capture.log"
        with open(capture_path, "w", encoding="utf-8") as f:
            f.write("\n".join(captured_lines) + "\n")
        print(f"Tuner log capture saved to: {capture_path}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Queue Parameter Families benchmark renders.")
    parser.add_argument("--stage", choices=["1", "2", "all"], default="1",
                        help="Which stage to queue: '1' (12 gate renders, default), '2' (ladder), 'all' (entire plan)")
    parser.add_argument("--check-only", action="store_true", help="Print plan and queue status without queuing.")
    parser.add_argument("--evaluate-gate", action="store_true", help="Evaluate Stage 1 Gate against baselines.")
    parser.add_argument("--check-logs", action="store_true", help="Verify preset layer resolution in ComfyUI logs.")
    parser.add_argument("--passing-families", type=str, default="",
                        help="Comma-separated list of families to queue for Stage 2 (e.g. 'F_wo,F_qknorm'). If empty, defaults to F_wo + gate passers.")
    args = parser.parse_args()

    if args.check_logs:
        check_logs()
        return

    if args.evaluate_gate:
        evaluate_gate()
        return

    if not check_comfy_online():
        print(f"ERROR: ComfyUI is not reachable at {COMFY_HOST}")
        sys.exit(1)

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    if args.stage == "1":
        stage_filter = "1_gate"
        rows = load_plan(stage_filter=stage_filter)
        print(f"Loaded Stage 1 Gate plan: {len(rows)} renders.")
    elif args.stage == "2":
        stage_filter = "2_ladder"
        all_stage2_rows = load_plan(stage_filter=stage_filter)
        # Determine allowed families
        allowed: Set[str] = set()
        if args.passing_families:
            allowed = {f.strip() for f in args.passing_families.split(",") if f.strip()}
        else:
            # Try to auto-evaluate gate
            gate_res = evaluate_gate()
            allowed = {"F_wo"}  # F_wo always included as reference
            for fam, r in gate_res.items():
                if r["moved"]:
                    allowed.add(fam)
        print(f"Allowed families for Stage 2: {sorted(allowed)}")
        rows = [r for r in all_stage2_rows if r["family"] in allowed]
        print(f"Filtered Stage 2 Ladder plan: {len(rows)} renders.")
    else:  # all
        rows = load_plan(stage_filter=None)
        print(f"Loaded full plan: {len(rows)} renders.")

    # Filter out already existing renders
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
        print("\nCheck-only mode. First 5 pending rows:")
        for r in pending_rows[:5]:
            print(f"  Row {r['row_index']:>3s} | {r['stage']} | {r['family']:8s} | delta={r['delta']:>6s} | {r['prompt_id']} | seed={r['seed']} | {r['output_prefix']}")
        return

    if not pending_rows:
        print("All target renders already exist in output folder! Nothing to queue.")
        return

    # Queue fast batch
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

    # Immediate queue verification
    running, pending = get_queue_counts()
    print(f"ComfyUI Queue Verification: {running} running, {pending} pending tasks in queue.")


if __name__ == "__main__":
    main()
