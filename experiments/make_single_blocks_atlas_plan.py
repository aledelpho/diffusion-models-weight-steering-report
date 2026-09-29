#!/usr/bin/env python3
"""
experiments/make_single_blocks_atlas_plan.py
============================================
Creates render plan for the Single-Block Atlas (171 renders):
  - 3 Prompts:
      1. P01_blacksmith: Western comics blacksmith woman
      2. F4_closeup: Western comics screaming female elf close-up
      3. S1_rally: Realistic photography jungle rally car
  - 28 Blocks: blk00 to blk27 (the exact constitutive layers of Block_1..Block_6)
  - 2 Doses: +0.350 and -0.350
  - 1 Seed: 2718281 (the center-push / C41 reference seed)
  - 3 Baselines: 1 unperturbed baseline per prompt

Drive: ArthemyKrea2ModelTuner in Real Value mode with a 34-slot vectors_override,
with the target block slot set to ±0.350 and all others at 0.000.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_CSV = ROOT / "data" / "single_blocks_atlas_plan.csv"

SEED = "2718281"
DOSE = "0.350"
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


def make_vector(block_idx: int, sign: str, dose: float) -> str:
    vec = [0.0] * 34
    val = dose if sign == "pos" else -dose
    vec[block_idx] = round(val, 3)
    return ",".join(f"{x:.3f}" for x in vec)


def main():
    rows = []
    idx = 0

    # 1. Baselines (3 renders)
    for pid, ptext in PROMPTS:
        idx += 1
        fn = f"{pid}_baseline_krea2_seed{SEED}"
        rows.append(dict(
            row_index=str(idx),
            arm="baseline",
            condition="baseline",
            block_idx="-1",
            dose="0.000",
            sign="none",
            prompt_id=pid,
            seed=SEED,
            nonzero_slots="{}",
            vectors_override="",
            output_prefix=fn,
            expected_filename=f"{fn}_00001_.png",
            prompt_text=ptext,
            **{k: str(v) for k, v in SETTINGS.items()}
        ))

    # 2. Perturbations: 28 blocks x 2 signs x 3 prompts = 168 renders
    for b in range(BLOCK_COUNT):
        for sign in ["pos", "neg"]:
            v_str = make_vector(b, sign, float(DOSE))
            sign_char = "+" if sign == "pos" else "-"
            slot_json = json.dumps({str(b): (float(DOSE) if sign == "pos" else -float(DOSE))})
            cond = f"blk{b:02d}_{sign}_d{DOSE}"

            for pid, ptext in PROMPTS:
                idx += 1
                fn = f"{pid}_blk{b:02d}_{sign}_d{DOSE}_krea2_seed{SEED}"
                rows.append(dict(
                    row_index=str(idx),
                    arm="perturbation",
                    condition=cond,
                    block_idx=str(b),
                    dose=DOSE,
                    sign=sign,
                    prompt_id=pid,
                    seed=SEED,
                    nonzero_slots=slot_json,
                    vectors_override=v_str,
                    output_prefix=fn,
                    expected_filename=f"{fn}_00001_.png",
                    prompt_text=ptext,
                    **{k: str(v) for k, v in SETTINGS.items()}
                ))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} plan rows written to {OUT_CSV}:")
    print(f"  - 3 baselines")
    print(f"  - 168 single-block perturbations (28 blocks x 2 doses x 3 prompts)")


if __name__ == "__main__":
    main()
