#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT = DATA_DIR / "single_blocks_v4_plan.csv"

TUNED_DOSES = {
    0:  {"neg": 0.200, "pos": 0.250},
    1:  {"neg": 0.400, "pos": 0.250},
    2:  {"neg": 0.450, "pos": 0.400},
    3:  {"neg": 0.550, "pos": 0.400},
    4:  {"neg": 0.550, "pos": 0.550},
    5:  {"neg": 0.550, "pos": 0.550},
    6:  {"neg": 0.550, "pos": 0.550},
    7:  {"neg": 0.550, "pos": 0.550},
    8:  {"neg": 0.550, "pos": 0.550},
    9:  {"neg": 0.550, "pos": 0.550},
    10: {"neg": 0.450, "pos": 0.450},
    11: {"neg": 0.450, "pos": 0.450},
    12: {"neg": 0.450, "pos": 0.400},
    13: {"neg": 0.450, "pos": 0.400},
    14: {"neg": 0.550, "pos": 0.400},
    15: {"neg": 0.450, "pos": 0.400},
    16: {"neg": 0.450, "pos": 0.300},
    17: {"neg": 0.450, "pos": 0.400},
    18: {"neg": 0.450, "pos": 0.300},
    19: {"neg": 0.450, "pos": 0.250},
    20: {"neg": 0.550, "pos": 0.450},
    21: {"neg": 0.450, "pos": 0.250},
    22: {"neg": 0.450, "pos": 0.250},
    23: {"neg": 0.300, "pos": 0.300},
    24: {"neg": 0.400, "pos": 0.200},
    25: {"neg": 0.450, "pos": 0.250},
    26: {"neg": 0.250, "pos": 0.150},
    27: {"neg": 0.250, "pos": 0.050},
}

SEED = "1234567"

PROMPTS = [
    ("P1_crown_topdown", "realistic dark fantasy painting, thick oil brushstrokes, dramatic lighting. A heavy golden royal crown encrusted with glowing ruby gems, resting on a crimson velvet cushion. viewed from directly above, extreme top-down angle, bird's eye view, perfect overhead shot. dark stone floor background."),
    ("P2_crown_bottomup", "realistic dark fantasy painting, thick oil brushstrokes, dramatic lighting. A heavy golden royal crown encrusted with glowing ruby gems, resting on a crimson velvet cushion. viewed from directly below, extreme low angle, worm's-eye view, looking straight up. dark stone floor background."),
    ("P3_crown_rusted", "realistic dark fantasy painting, thick oil brushstrokes, dramatic lighting. A heavy rusted iron royal crown encrusted with glowing ruby gems, resting on a crimson velvet cushion. viewed from the front. dark stone floor background."),
    ("P4_crown_glass", "realistic dark fantasy painting, thick oil brushstrokes, dramatic lighting. A heavy translucent glass royal crown encrusted with glowing ruby gems, resting on a crimson velvet cushion. viewed from the front. dark stone floor background."),
    ("P5_comic_panels", "Comic book page layout, single image divided into four equal rectangular panels by thick bold black borders. Panel 1 (Top Left): A fierce male barbarian with a thick braided beard, wearing animal furs, swinging a bloody battleaxe in a snowy forest. Panel 2 (Top Right): A serene female elven sorceress with long flowing silver hair, wearing a glowing blue silk robe, casting a bright healing spell in a dark cave. Panel 3 (Bottom Left): A cunning goblin rogue with green skin and large ears, wearing dark leather armor, holding two curved daggers, sneaking through a crowded medieval market. Panel 4 (Bottom Right): A massive red dragon with glowing yellow eyes and sharp scales, breathing a stream of intense orange fire into the night sky. High quality, ultra-detailed comic illustration, distinct color palettes in each panel, masterpiece.")
]

SET = dict(mode="Real Value", sampler="euler_ancestral", scheduler="simple", steps=9, cfg=1.0,
           denoise=1.0, width=1024, height=1280)

def build_plan():
    rows, i = [], 0
    for pid, text in PROMPTS:
        i += 1
        pre = f"{pid}_baseline_krea2_seed{SEED}"
        rows.append(dict(row_index=i, arm="baseline", condition="baseline", block_idx="", dose="0.000",
                         sign="", eye_label_at_0350="", prompt_id=pid, seed=SEED, nonzero_slots="{}",
                         vectors_override="", output_prefix=pre, expected_filename=pre + "_00001_.png",
                         prompt_text=text, **SET))
        for b in range(28):
            for sign in ("neg", "pos"):
                i += 1
                d = TUNED_DOSES[b][sign]
                v = d if sign == "pos" else -d
                vo = [0.0] * 34
                vo[b] = v
                cond = f"blk{b:02d}_{sign}_d{d:.3f}"
                pre = f"{pid}_{cond}_krea2_seed{SEED}"
                rows.append(dict(row_index=i, arm="perturbation", condition=cond, block_idx=b, dose=f"{d:.3f}",
                                 sign=sign, eye_label_at_0350="", prompt_id=pid, seed=SEED,
                                 nonzero_slots=json.dumps({str(b): v}),
                                 vectors_override=",".join(f"{x:.3f}" for x in vo),
                                 output_prefix=pre, expected_filename=pre + "_00001_.png",
                                 prompt_text=text, **SET))
    return rows

def main():
    rows = build_plan()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} righe -> {OUT}")

if __name__ == "__main__":
    main()
