#!/usr/bin/env python3
import csv
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "realism_test_plan.csv"

SEED = "13371337"

PROMPTS = [
    ("T1_base", "A portrait of a red fox sitting in a snowy forest, looking at the camera."),
    ("T2_real", "realistic, photorealistic, highly detailed. A portrait of a red fox sitting in a snowy forest, looking at the camera."),
    ("T3_paint", "painterly, visible brushstrokes, illustration. A portrait of a red fox sitting in a snowy forest, looking at the camera.")
]

SET = dict(mode="Real Value", sampler="euler_ancestral", scheduler="simple", steps=9, cfg=1.0,
           denoise=1.0, width=1024, height=1280)

def main():
    rows = []
    i = 0
    for pid, text in PROMPTS:
        # Baseline
        i += 1
        pre_base = f"{pid}_baseline_krea2_seed{SEED}"
        rows.append(dict(row_index=i, arm="baseline", condition="baseline", block_idx="", dose="0.000",
                         sign="", prompt_id=pid, seed=SEED, nonzero_slots="{}",
                         vectors_override="", output_prefix=pre_base, expected_filename=pre_base + "_00001_.png",
                         prompt_text=text, **SET))
        
        # Blk03 Pos
        i += 1
        d = 0.550
        v = {"2": d}
        pre_pos = f"{pid}_blk03_pos_d{d:.3f}_krea2_seed{SEED}"
        rows.append(dict(row_index=i, arm="blk03_pos", condition="single_block", block_idx="03", dose=f"{d:.3f}",
                         sign="pos", prompt_id=pid, seed=SEED, nonzero_slots=json.dumps(v),
                         vectors_override=json.dumps(v), output_prefix=pre_pos, expected_filename=pre_pos + "_00001_.png",
                         prompt_text=text, **SET))
        
        # Blk03 Neg
        i += 1
        v = {"2": -d}
        pre_neg = f"{pid}_blk03_neg_d{d:.3f}_krea2_seed{SEED}"
        rows.append(dict(row_index=i, arm="blk03_neg", condition="single_block", block_idx="03", dose=f"{d:.3f}",
                         sign="neg", prompt_id=pid, seed=SEED, nonzero_slots=json.dumps(v),
                         vectors_override=json.dumps(v), output_prefix=pre_neg, expected_filename=pre_neg + "_00001_.png",
                         prompt_text=text, **SET))

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Plan scritto in {OUT} ({len(rows)} righe).")

if __name__ == '__main__':
    main()
