# -*- coding: utf-8 -*-
"""
experiments/verify_render_metadata.py
=====================================
Performs strict pre-launch metadata verification on test renders.
Governed by user instructions for docs/RENDERS_2026-09-28_leaf_collapse_and_blk16.md:
  1. Compares vectors_override and group inputs from PNG metadata against plan CSVs.
  2. Verifies that baseline rows have the tuner completely disconnected (KSampler model from node 37,
     tuner node absent or unlinked), NOT connected with zero gain.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
COMFY_OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")


def verify_leaf_collapse(first_n: int = 3) -> bool:
    plan_path = DATA_DIR / "leaf_collapse_plan.csv"
    with open(plan_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))[:first_n]

    renders_dir = COMFY_OUTPUT_ROOT / "benchmark_leaf_collapse" / "renders"
    print(f"\n==================================================")
    print(f"VERIFYING BENCH 1: LEAF COLLAPSE (First {len(rows)} renders)")
    print(f"==================================================")

    all_ok = True

    for r in rows:
        fn = r["expected_filename"]
        img_path = renders_dir / fn
        if not img_path.exists():
            print(f"[FAIL] Missing PNG file: {img_path}")
            all_ok = False
            continue

        im = Image.open(img_path)
        prompt_raw = im.info.get("prompt")
        if not prompt_raw:
            print(f"[FAIL] {fn}: No 'prompt' metadata found in PNG!")
            all_ok = False
            continue

        wf = json.loads(prompt_raw)
        treatment = r.get("treatment", "none").strip()
        expected_seed = int(r["seed"])
        expected_steps = int(r["steps"])
        expected_cfg = float(r["cfg"])
        expected_sampler = r["sampler"]
        expected_scheduler = r["scheduler"]
        expected_prompt = r["prompt_text"]

        # 1. Check KSampler inputs
        ksampler = wf.get("42", {})
        ks_inputs = ksampler.get("inputs", {})
        if ks_inputs.get("seed") != expected_seed:
            print(f"[FAIL] {fn}: Seed mismatch! Expected {expected_seed}, got {ks_inputs.get('seed')}")
            all_ok = False
        if ks_inputs.get("steps") != expected_steps:
            print(f"[FAIL] {fn}: Steps mismatch! Expected {expected_steps}, got {ks_inputs.get('steps')}")
            all_ok = False
        if ks_inputs.get("cfg") != expected_cfg:
            print(f"[FAIL] {fn}: CFG mismatch! Expected {expected_cfg}, got {ks_inputs.get('cfg')}")
            all_ok = False
        if ks_inputs.get("sampler_name") != expected_sampler:
            print(f"[FAIL] {fn}: Sampler mismatch! Expected {expected_sampler}, got {ks_inputs.get('sampler_name')}")
            all_ok = False
        if ks_inputs.get("scheduler") != expected_scheduler:
            print(f"[FAIL] {fn}: Scheduler mismatch! Expected {expected_scheduler}, got {ks_inputs.get('scheduler')}")
            all_ok = False

        # 2. Check Prompt Text
        clip_encode = wf.get("40", {}).get("inputs", {})
        actual_text = clip_encode.get("text", "")
        if actual_text.strip() != expected_prompt.strip():
            print(f"[FAIL] {fn}: Prompt text mismatch!")
            all_ok = False

        # 3. Check Tuner Connection
        model_source = ks_inputs.get("model", [])
        if treatment == "none":
            # Baseline: tuner MUST BE DISCONNECTED / BYPASSED!
            if model_source != ["37", 0]:
                print(f"[FAIL] {fn}: BASELINE VIOLATION! KSampler model source is {model_source}, expected ['37', 0] (bypassed tuner)!")
                all_ok = False
            elif "50" in wf:
                print(f"[FAIL] {fn}: BASELINE VIOLATION! Node 50 (ArthemyKrea2ModelTuner) is present in baseline workflow!")
                all_ok = False
            else:
                print(f"[PASS] {fn} (Baseline, seed {expected_seed}): Tuner is TRULY BYPASSED (KSampler directly connected to node 37).")
        else:
            # Perturbed: tuner MUST BE CONNECTED at node 50
            if model_source != ["50", 0]:
                print(f"[FAIL] {fn}: KSampler model source is {model_source}, expected ['50', 0] (tuner connected)!")
                all_ok = False
            tuner = wf.get("50", {})
            t_inputs = tuner.get("inputs", {})

            block_input = r.get("block_input", "")
            expected_gain = float(r.get("gain", 0.0))
            actual_gain = float(t_inputs.get(block_input, 0.0))
            if actual_gain != expected_gain:
                print(f"[FAIL] {fn}: Gain mismatch on {block_input}! Expected {expected_gain}, got {actual_gain}")
                all_ok = False

            # Check that other named blocks are 0.0
            named_blocks = ["Text_Fusion", "Time_Embed", "Projection", "Block_1", "Block_2", "Block_3", "Block_4", "Block_5", "Block_6"]
            for nb in named_blocks:
                if nb != block_input and float(t_inputs.get(nb, 0.0)) != 0.0:
                    print(f"[FAIL] {fn}: Block {nb} should be 0.0, got {t_inputs.get(nb)}")
                    all_ok = False

            # Check vectors_override is empty
            if t_inputs.get("vectors_override", "") != "":
                print(f"[FAIL] {fn}: vectors_override should be empty, got {t_inputs.get('vectors_override')}")
                all_ok = False

            print(f"[PASS] {fn} (Perturbed, seed {expected_seed}): Tuner correctly connected: {block_input}={actual_gain}, vectors_override='', mode={t_inputs.get('mode')}.")

    return all_ok


def verify_blk16_ladder(first_n: int = 3) -> bool:
    plan_path = DATA_DIR / "blk16_ladder_plan.csv"
    with open(plan_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))[:first_n]

    renders_dir = COMFY_OUTPUT_ROOT / "benchmark_blk16_ladder" / "renders"
    print(f"\n==================================================")
    print(f"VERIFYING BENCH 2: BLK16 LADDER (First {len(rows)} renders)")
    print(f"==================================================")

    all_ok = True

    for r in rows:
        fn = r["expected_filename"]
        img_path = renders_dir / fn
        if not img_path.exists():
            print(f"[FAIL] Missing PNG file: {img_path}")
            all_ok = False
            continue

        im = Image.open(img_path)
        prompt_raw = im.info.get("prompt")
        if not prompt_raw:
            print(f"[FAIL] {fn}: No 'prompt' metadata found in PNG!")
            all_ok = False
            continue

        wf = json.loads(prompt_raw)
        expected_seed = int(r["seed"])
        expected_steps = int(r["steps"])
        expected_cfg = float(r["cfg"])
        expected_sampler = r["sampler"]
        expected_scheduler = r["scheduler"]
        expected_prompt = r["prompt_text"]
        expected_vec = r["vectors_override"].strip()
        expected_mode = r.get("mode", "Real Value")

        # 1. Check KSampler inputs
        ksampler = wf.get("42", {})
        ks_inputs = ksampler.get("inputs", {})
        if ks_inputs.get("seed") != expected_seed:
            print(f"[FAIL] {fn}: Seed mismatch! Expected {expected_seed}, got {ks_inputs.get('seed')}")
            all_ok = False
        if ks_inputs.get("steps") != expected_steps:
            print(f"[FAIL] {fn}: Steps mismatch! Expected {expected_steps}, got {ks_inputs.get('steps')}")
            all_ok = False
        if ks_inputs.get("cfg") != expected_cfg:
            print(f"[FAIL] {fn}: CFG mismatch! Expected {expected_cfg}, got {ks_inputs.get('cfg')}")
            all_ok = False
        if ks_inputs.get("sampler_name") != expected_sampler:
            print(f"[FAIL] {fn}: Sampler mismatch! Expected {expected_sampler}, got {ks_inputs.get('sampler_name')}")
            all_ok = False
        if ks_inputs.get("scheduler") != expected_scheduler:
            print(f"[FAIL] {fn}: Scheduler mismatch! Expected {expected_scheduler}, got {ks_inputs.get('scheduler')}")
            all_ok = False

        # 2. Check Prompt Text
        clip_encode = wf.get("40", {}).get("inputs", {})
        actual_text = clip_encode.get("text", "")
        if actual_text.strip() != expected_prompt.strip():
            print(f"[FAIL] {fn}: Prompt text mismatch!")
            all_ok = False

        # 3. Check Tuner Connection & vectors_override
        model_source = ks_inputs.get("model", [])
        if model_source != ["50", 0]:
            print(f"[FAIL] {fn}: KSampler model source is {model_source}, expected ['50', 0]!")
            all_ok = False

        tuner = wf.get("50", {})
        t_inputs = tuner.get("inputs", {})
        actual_vec = t_inputs.get("vectors_override", "").strip()
        if actual_vec != expected_vec:
            print(f"[FAIL] {fn}: vectors_override mismatch!\n  Expected: {expected_vec}\n  Got:      {actual_vec}")
            all_ok = False

        if t_inputs.get("mode") != expected_mode:
            print(f"[FAIL] {fn}: Mode mismatch! Expected {expected_mode}, got {t_inputs.get('mode')}")
            all_ok = False

        # Check all named group inputs are 0.0
        named_blocks = ["Text_Fusion", "Time_Embed", "Projection", "Block_1", "Block_2", "Block_3", "Block_4", "Block_5", "Block_6"]
        for nb in named_blocks:
            if float(t_inputs.get(nb, 0.0)) != 0.0:
                print(f"[FAIL] {fn}: Named input {nb} should be 0.0, got {t_inputs.get(nb)}")
                all_ok = False

        # Verify specifically that slot 16 contains the expected dose
        vec_vals = [float(x.strip()) for x in actual_vec.split(",")]
        expected_dose = float(r["dose"])
        if len(vec_vals) != 34:
            print(f"[FAIL] {fn}: Vector length is {len(vec_vals)}, expected 34!")
            all_ok = False
        elif abs(vec_vals[16] - expected_dose) > 1e-4:
            print(f"[FAIL] {fn}: Slot 16 value is {vec_vals[16]}, expected {expected_dose}!")
            all_ok = False
        else:
            non_zero_slots = [(i, val) for i, val in enumerate(vec_vals) if abs(val) > 1e-5]
            if len(non_zero_slots) != 1 or non_zero_slots[0][0] != 16:
                print(f"[FAIL] {fn}: Expected only slot 16 non-zero, got non-zero slots: {non_zero_slots}")
                all_ok = False
            else:
                print(f"[PASS] {fn} (Condition {r['condition']}, seed {expected_seed}): vectors_override has slot 16 = {vec_vals[16]:+.3f} (all other 33 slots 0.000), named inputs all 0.0.")

    return all_ok


def main():
    ok1 = verify_leaf_collapse(3)
    ok2 = verify_blk16_ladder(3)

    if ok1 and ok2:
        print("\n==================================================")
        print("[PRE-CHECK SUCCESSFUL] ALL 6 TEST RENDERS MATCH THE PLAN CSV EXACTLY!")
        print("  - Bench 1: baseline has tuner TRULY DISCONNECTED, perturbed has Block_4=-0.2.")
        print("  - Bench 2: vectors_override has slot 16 active and named inputs all 0.0.")
        print("Ready for full queue launch.")
        print("==================================================")
        sys.exit(0)
    else:
        print("\n==================================================")
        print("[PRE-CHECK FAILED] Metadata mismatch detected! Full bench will NOT be launched.")
        print("==================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
