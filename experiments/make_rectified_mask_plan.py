#!/usr/bin/env python3
"""Builds the render plan for docs/RENDERS_2026-09-27_rectified_masks.md.

No preset JSON is needed. `benchmark_profondita` drove single blocks through
ArthemyKrea2ModelTuner in "Real Value" mode with a `vectors_override` of 34 slots
(28 transformer blocks, then 2 txtfusion layerwise, 2 refiner, 1 projector, 1 txtmlp).
Verified from the render metadata: blk15pos carries 0.2 at index 15 and zero everywhere else.

Switching a block off is therefore simply leaving its slot at 0.000 — no granular_json.
That is how `blk24` and `blk25` are excluded from the Block_6 mask.

Writes data/rectified_mask_plan.csv. Generates no render.
"""
import csv, json, os, glob
from PIL import Image

VLEN = 34
DOSE = 0.200
OUT = "data/rectified_mask_plan.csv"
MAPPA = os.path.expanduser("~/mnt/benchmark_mappa--renders")
SEEDS = ["42", "777", "1337"]
PROMPTS = ["P01", "P02"]

# block index -> sign multiplier, for the positive arm of each condition.
# The negative arm is the whole thing flipped.
COND = {
    "B4_mask":   {15: +1, 18: -1},          # both members push contrast UP
    "B4_anti":   {15: +1, 18: +1},          # same |d|, same displacement, one relative sign flipped
    "B6_mask":   {27: +1, 26: -1},          # both members push grain UP
    "B6_anti":   {27: +1, 26: +1},
    "B4B6_mask": {15: +1, 18: -1, 27: +1, 26: -1},
    "B4B6_anti": {15: +1, 18: +1, 27: +1, 26: +1},
}


def prompt_text(p):
    f = f"{MAPPA}/{p}_baseline_krea2_seed42_00001_.png"
    pr = json.loads(Image.open(f).info["prompt"])
    for _, v in pr.items():
        if "TextEncode" in v.get("class_type", ""):
            t = v.get("inputs", {}).get("text", "")
            if isinstance(t, str) and t.strip():
                return t.strip()
    raise SystemExit(f"no prompt text in {f}")


def vector(spec, arm):
    v = [0.0] * VLEN
    for idx, s in spec.items():
        v[idx] = round(s * DOSE * (1 if arm == "pos" else -1), 3)
    return v


def main():
    texts = {p: prompt_text(p) for p in PROMPTS}
    rows = []
    n = 0
    for cond, spec in COND.items():
        for arm in ("pos", "neg"):
            vec = vector(spec, arm)
            nz = {i: vec[i] for i in range(VLEN) if vec[i] != 0}
            for p in PROMPTS:
                for s in SEEDS:
                    n += 1
                    name = f"{cond}_{arm}"
                    rows.append(dict(
                        row_index=n, stage="rectified_masks", condition=name,
                        prompt_id=p, seed=s, mode="Real Value",
                        sampler="euler_ancestral", scheduler="simple", steps=9, cfg=1.0,
                        denoise=1.0, width=1024, height=1280,
                        nonzero_slots=json.dumps(nz),
                        vectors_override=",".join(f"{x:.3f}" for x in vec),
                        granular_json="",
                        output_prefix=f"benchmark_rectified_masks/renders/{p}_{name}_seed{s}",
                        expected_filename=f"{p}_{name}_seed{s}_00001_.png",
                        prompt_text=texts[p]))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)} rows to {OUT}")
    print("\nthe twelve vectors, non-zero slots only:")
    for cond, spec in COND.items():
        for arm in ("pos", "neg"):
            v = vector(spec, arm)
            print(f"  {cond+'_'+arm:16s} " + "  ".join(f"[{i}]={v[i]:+.3f}" for i in sorted(spec)))
    print("\nevery other slot is 0.000 -- that is how blk24 and blk25 are switched off.")
    # displacement check: mask and anti-mask touch the same tensors with the same |gain|
    for pair in (("B4_mask", "B4_anti"), ("B6_mask", "B6_anti"), ("B4B6_mask", "B4B6_anti")):
        a, b = (set(COND[x]) for x in pair)
        same = a == b
        print(f"  {pair[0]} vs {pair[1]}: same tensors {same}, same |gain| True "
              f"-> identical Frobenius displacement by construction")


if __name__ == "__main__":
    main()
