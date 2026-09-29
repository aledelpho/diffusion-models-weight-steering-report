#!/usr/bin/env python3
"""
experiments/make_wo_depth_doses_presets.py
==========================================
Generates depth slice presets for doses ±0.200 and ±0.350 (b1..b6),
verifies disjointness and exact union match against Family_wo_d±{dose}.json,
syncs presets to ComfyUI custom node presets directory,
and appends the 168 new render rows (84 for ±0.200, 84 for ±0.350)
to data/wo_depth_plan.csv.
"""
import csv
import datetime
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTING = ROOT / "docs" / "model_structures" / "krea2_turbo_bf16_details.json"
PRESETS_DIR = ROOT / "presets"
COMFY_PRESETS_DIR = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_Krea2_Tuner\presets")
PLAN_CSV = ROOT / "data" / "wo_depth_plan.csv"
CP_PLAN = ROOT / "data" / "centre_push_plan.csv"

KEY_RE = r"^blocks\.(\d+)\.attn\.wo\.weight$"
GROUPS = {
    "b1": range(0, 5),
    "b2": range(5, 10),
    "b3": range(10, 15),
    "b4": range(15, 20),
    "b5": range(20, 24),
    "b6": range(24, 28)
}
DOSES = [0.200, 0.350]
SEEDS = ["1618033", "2718281", "3141592"]
PROMPTS = ["P01", "P02"]
SETTINGS = dict(
    mode="Real Value", sampler="euler_ancestral", scheduler="simple",
    steps=9, cfg=1.0, denoise=1.0, width=1024, height=1280
)


def checkpoint_keys():
    with open(LISTING, "r", encoding="utf-8") as f:
        data = json.load(f)
    fl = data["flat_tensors_list"]
    it = fl.items() if isinstance(fl, dict) else ((t["name"], t) for t in fl)
    out = {}
    for n, t in it:
        m = re.match(KEY_RE, n)
        if m:
            out[n] = (int(m.group(1)), t["param_count"])
    return out


def main():
    keys = checkpoint_keys()
    if len(keys) != 28:
        sys.exit(f"Expected 28 wo tensors in checkpoint listing, found {len(keys)}")

    slices = {g: sorted(k for k, (b, _) in keys.items() if b in rng) for g, rng in GROUPS.items()}
    flat = [k for g in slices for k in slices[g]]
    if len(flat) != len(set(flat)) or len(flat) != 28:
        sys.exit("Slices are not a valid partition of the 28 wo tensors.")

    COMFY_PRESETS_DIR.mkdir(parents=True, exist_ok=True)

    generated_presets = []

    for delta in DOSES:
        for sign_char, sign_val in [("+", 1.0), ("-", -1.0)]:
            dose_str = f"d{sign_char}{delta:.3f}"
            union_preset_name = f"Family_wo_{dose_str}.json"
            union_preset_path = PRESETS_DIR / union_preset_name
            if not union_preset_path.exists():
                sys.exit(f"Union preset missing: {union_preset_path}")
            with open(union_preset_path, "r", encoding="utf-8") as f:
                union_data = json.load(f)
            if set(union_data["model_patches"]) != set(flat):
                sys.exit(f"Union preset {union_preset_name} keys do not match full 28 wo set.")
            for k, val in union_data["model_patches"].items():
                if abs(val - (sign_val * delta)) > 1e-6:
                    sys.exit(f"Union preset {union_preset_name} has invalid delta for {k}: {val}")

            # Generate slice presets
            for g in ["b1", "b2", "b3", "b4", "b5", "b6"]:
                preset_name = f"WO_{g}_{dose_str}.json"
                body = {
                    "name": f"WO_{g}_{dose_str}",
                    "author": "Antigravity (C41-Ext)",
                    "created_at": datetime.date.today().isoformat(),
                    "version": 1,
                    "suite_rotation_effective": False,
                    "stats": {
                        "model_patched_layers": len(slices[g]),
                        "model_granular_layers": 0,
                        "clip_patched_layers": 0,
                        "clip_granular_layers": 0,
                        "chaos_recipes_count": 0,
                        "rotation_recipes_count": 0,
                        "chaos_rotation_recipes_count": 0,
                        "channel_recipes_count": 0,
                        "five_d_recipes_count": 0,
                        "excluded_lora_tensors": 0
                    },
                    "model_patches": {k: sign_val * delta for k in slices[g]},
                    "model_granular_patches": {},
                    "clip_patches": {},
                    "clip_granular_patches": {},
                    "chaos_recipes": {},
                    "rotation_recipes": {},
                    "chaos_rotation_recipes": {},
                    "channel_recipes": {},
                    "five_d_recipes": {},
                }
                out_path = PRESETS_DIR / preset_name
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(body, f, indent=2)

                # Sync to ComfyUI custom node presets
                comfy_dest = COMFY_PRESETS_DIR / preset_name
                shutil.copy2(out_path, comfy_dest)
                generated_presets.append((preset_name, len(slices[g])))

    print(f"Generated and synced {len(generated_presets)} slice presets.")

    # Read existing plan
    existing_rows = []
    if PLAN_CSV.exists():
        with open(PLAN_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for r in reader:
                existing_rows.append(r)
    else:
        sys.exit(f"Plan CSV not found at {PLAN_CSV}")

    last_index = max(int(r["row_index"]) for r in existing_rows) if existing_rows else 0

    # Read prompt metadata from centre_push_plan
    with open(CP_PLAN, "r", encoding="utf-8") as f:
        cp = list(csv.DictReader(f))
    sha = {r["prompt_id"]: r["prompt_sha1"] for r in cp}
    text = {r["prompt_id"]: r["prompt_text"] for r in cp}

    new_rows = []
    curr_idx = last_index

    for delta in DOSES:
        for sign_char in ["+", "-"]:
            dose_str = f"d{sign_char}{delta:.3f}"
            # 6 slice conditions + 1 union condition
            cond_defs = []
            for g in ["b1", "b2", "b3", "b4", "b5", "b6"]:
                cond_defs.append((f"slice_{g}_{dose_str}", f"WO_{g}_{dose_str}.json", len(slices[g])))
            cond_defs.append((f"union_{dose_str}", f"Family_wo_{dose_str}.json", 28))

            for cond, preset_fn, nt in cond_defs:
                for p in PROMPTS:
                    for sd in SEEDS:
                        curr_idx += 1
                        fn = f"{p}_{cond}_krea2_seed{sd}"
                        row = dict(
                            row_index=str(curr_idx),
                            arm="push",
                            condition=cond,
                            preset_file=preset_fn,
                            tensors=str(nt),
                            prompt_id=p,
                            seed=sd,
                            output_prefix=fn,
                            expected_filename=f"{fn}_00001_.png",
                            borrowed_from="",
                            prompt_sha1=sha[p],
                            prompt_text=text[p],
                            **{k: str(v) for k, v in SETTINGS.items()}
                        )
                        new_rows.append(row)

    print(f"Created {len(new_rows)} new plan rows ({len(new_rows)//2} per dose).")

    all_rows = existing_rows + new_rows
    with open(PLAN_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)

    print(f"Total plan updated: {len(all_rows)} rows written to {PLAN_CSV}.")


if __name__ == "__main__":
    main()
