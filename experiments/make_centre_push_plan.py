# -*- coding: utf-8 -*-
"""
experiments/make_centre_push_plan.py
====================================
Writes data/centre_push_plan.csv for docs/prereg_centre_push.md.

6 block groups x 2 signs x 4 doses x 2 prompts x 3 new seeds = 288 perturbed renders,
plus 6 baselines, plus 1 determinism row that must reproduce an existing benchmark_mappa render
pixel for pixel. 295 rows.

The prompt texts are read from the embedded graph of the benchmark_mappa baselines, so they are the
same strings, byte for byte. The drive is the group input of ArthemyKrea2ModelTuner in Real Value
mode with an empty vectors_override, exactly as benchmark_mappa was driven.

  python experiments/make_centre_push_plan.py [--mappa-root PATH]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "centre_push_plan.csv"

GROUPS = ["Block_1", "Block_2", "Block_3", "Block_4", "Block_5", "Block_6"]
SIGNS = [("pos", 1.0), ("neg", -1.0)]
DOSES = ["0.080", "0.200", "0.350", "0.500"]
PROMPTS = ["P01", "P02"]
SEEDS = [2718281, 3141592, 1618033]          # never used on benchmark_mappa
DET_ROW = ("P01", "Block_3", "pos", "0.200", 42)  # exists in benchmark_mappa

SAMPLER = dict(sampler="euler_ancestral", scheduler="simple", steps=9, cfg=1.0, denoise=1.0,
               width=1024, height=1280)


def prompt_text(mappa_root: Path, p: str) -> str:
    g = json.loads(Image.open(mappa_root / "renders" / f"{p}_baseline_krea2_seed42_00001_.png").info["prompt"])
    return g["40"]["inputs"]["text"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mappa-root", default=os.path.expanduser("~/mnt/benchmark_mappa"))
    args = ap.parse_args()
    texts = {p: prompt_text(Path(args.mappa_root), p) for p in PROMPTS}

    rows = []

    def add(arm, p, seed, group, sign, dose):
        if group is None:
            stem = f"{p}_baseline_krea2_seed{seed}"
            treatment, block_input, gain = "none", "", ""
        else:
            g = f"{float(dose) * (1 if sign == 'pos' else -1):.3f}"
            stem = f"{p}_{group}{sign}_{dose}_krea2_seed{seed}"
            treatment, block_input, gain = f"{group}={g}", group, g
        rows.append({"row_index": len(rows) + 1, "arm": arm, "prompt_id": p, "seed": seed,
                     "treatment": treatment, "block_input": block_input, "gain": gain,
                     "mode": "Real Value", "vectors_override": "", "granular_json": "",
                     **SAMPLER, "output_prefix": stem, "expected_filename": f"{stem}_00001_.png",
                     "prompt_sha1": hashlib.sha1(texts[p].encode("utf-8")).hexdigest()[:10],
                     "prompt_text": texts[p]})

    p, grp, sign, dose, seed = DET_ROW
    add("determinism", p, seed, grp, sign, dose)
    for p in PROMPTS:
        for seed in SEEDS:
            add("baseline", p, seed, None, None, None)
    for p in PROMPTS:
        for seed in SEEDS:
            for grp in GROUPS:
                for sign, _ in SIGNS:
                    for dose in DOSES:
                        add("push", p, seed, grp, sign, dose)

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
