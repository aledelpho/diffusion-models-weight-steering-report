#!/usr/bin/env python3
"""
experiments/make_swiglu_rectified_presets_and_plan.py
=====================================================
Generates 56 preset JSON files for the SwiGLU internal rectified masks across
all 28 blocks of Krea-2 (blocks.0 to blocks.27):
  - pos: mlp.gate.weight = +0.350, mlp.up.weight = -0.350
  - neg: mlp.gate.weight = -0.350, mlp.up.weight = +0.350

Syncs all 56 presets to ComfyUI custom node presets directory,
and creates data/swiglu_rectified_atlas_plan.csv (171 rows: 3 baselines + 168 perturbations).
"""
import csv
import datetime
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRESETS_DIR = ROOT / "presets"
COMFY_PRESETS_DIR = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_Krea2_Tuner\presets")
OUT_CSV = ROOT / "data" / "swiglu_rectified_atlas_plan.csv"

SEED = "2718281"
DOSE = 0.350
BLOCK_COUNT = 28  # blocks 0 to 27

PROMPTS = [
    (
        "P01_blacksmith",
        "Western comics style, bold ink outlines, hatched shadows, medium wide shot, "
        "static centred composition, eye-level camera, subject centred and filling the middle third of the frame. "
        "A blacksmith woman stands behind a heavy oak workbench, facing the viewer, both hands resting flat on the wood. "
        "She has coarse dark curls tied back, weathered brown skin, a leather apron over a coarse linen shirt, and a "
        "polished steel gauntlet on her left forearm. On the bench lie a hammered copper bowl, a coil of frayed rope, "
        "and three rough granite offcuts. Behind her on the left a forge fire glows with a warm orange to deep red "
        "gradient, and thin smoke rises against a flat dark stone wall on the right. Cold blue window light falls "
        "from the upper left across the steel."
    ),
    (
        "F4_closeup",
        "realistic western comics style, bold ink outlines, extreme expression, hatched shadows, "
        "hard blue-tinted rim light glowing along the edges of her face, screaming in terror, seen from a steep "
        "low angle, extreme close-up on the head only, pale skin, tight framing, dutch angle, sharp perspective. "
        "female elf, head turning in fear and surprise looking in camera, short blonde hair in a metty bob haircut, "
        "slim blonde eyebrows raised, wide teal eyes wide open, mouth stretched open in a full-throated panic scream, "
        "a gold necklace is flying around. white background, simple background, blue overall hue, monochromatic blue."
    ),
    (
        "S1_rally",
        "Style: realistic photography, stock photo, realism, photographic detail. "
        "Subject: a yellow and blue rally car cruising in a deep jungle, uneven street, "
        "daylight, lush plants, humidity, reflective ponds."
    )
]

SETTINGS = dict(
    mode="Real Value",
    sampler="euler_ancestral",
    scheduler="simple",
    steps=9,
    cfg=1.0,
    denoise=1.0,
    width=1024,
    height=1280
)


def main():
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    COMFY_PRESETS_DIR.mkdir(parents=True, exist_ok=True)

    created_presets = []

    # 1. Generate 56 preset files
    for b in range(BLOCK_COUNT):
        for sign in ["pos", "neg"]:
            pname = f"SwiGLU_rect_blk{b:02d}_{sign}"
            gate_val = DOSE if sign == "pos" else -DOSE
            up_val = -DOSE if sign == "pos" else DOSE

            body = {
                "name": pname,
                "author": "Antigravity (SwiGLU-Rectified)",
                "created_at": datetime.date.today().isoformat(),
                "version": 1,
                "suite_rotation_effective": False,
                "stats": {
                    "model_patched_layers": 2,
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
                "model_patches": {
                    f"blocks.{b}.mlp.gate.weight": gate_val,
                    f"blocks.{b}.mlp.up.weight": up_val
                },
                "model_granular_patches": {},
                "clip_patches": {},
                "clip_granular_patches": {},
                "chaos_recipes": {},
                "rotation_recipes": {},
                "chaos_rotation_recipes": {},
                "channel_recipes": {},
                "five_d_recipes": {}
            }

            json_path = PRESETS_DIR / f"{pname}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(body, f, indent=2)

            # Copy to ComfyUI presets folder
            shutil.copy2(json_path, COMFY_PRESETS_DIR / f"{pname}.json")
            created_presets.append(f"{pname}.json")

    print(f"Successfully generated and synced {len(created_presets)} SwiGLU rectified presets.")

    # 2. Build Plan CSV
    rows = []
    idx = 0

    # 3 Baselines
    for pid, ptext in PROMPTS:
        idx += 1
        fn = f"{pid}_baseline_krea2_seed{SEED}"
        rows.append(dict(
            row_index=str(idx),
            arm="baseline",
            condition="baseline",
            block_idx="-1",
            preset_file="",
            dose="0.000",
            sign="none",
            prompt_id=pid,
            seed=SEED,
            output_prefix=fn,
            expected_filename=f"{fn}_00001_.png",
            prompt_text=ptext,
            **{k: str(v) for k, v in SETTINGS.items()}
        ))

    # 168 SwiGLU Rectified Perturbations
    for b in range(BLOCK_COUNT):
        for sign in ["pos", "neg"]:
            preset_fn = f"SwiGLU_rect_blk{b:02d}_{sign}.json"
            cond = f"swiglu_rect_blk{b:02d}_{sign}"
            for pid, ptext in PROMPTS:
                idx += 1
                fn = f"{pid}_{cond}_d{DOSE:.3f}_krea2_seed{SEED}"
                rows.append(dict(
                    row_index=str(idx),
                    arm="swiglu_rectified",
                    condition=cond,
                    block_idx=str(b),
                    preset_file=preset_fn,
                    dose=f"{DOSE:.3f}",
                    sign=sign,
                    prompt_id=pid,
                    seed=SEED,
                    output_prefix=fn,
                    expected_filename=f"{fn}_00001_.png",
                    prompt_text=ptext,
                    **{k: str(v) for k, v in SETTINGS.items()}
                ))

    fieldnames = list(rows[0].keys())
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} plan rows written to {OUT_CSV}.")


if __name__ == "__main__":
    main()
