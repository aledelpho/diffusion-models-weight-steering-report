#!/usr/bin/env python3
"""Render plan for the blk16 dose ladder. 72 renders.

Origin: docs/style_damage_frontier.md sections 9-10. `blk16` is the single block that moves style
most while RAISING the orientation of the drawing -- style 0.447, structure coherence x1.040, 6 of
6 cells above 1, against the corpus where the five conditions this project had recommended are its
five largest losses of drawn line. It is a member of `Block_4`, the family Alessandro identified by
eye before any statistic did. It replaces `blk27` as the single-block candidate (register C19).

THE DRIVE MUST MATCH benchmark_profondita: single blocks there were driven through
`ArthemyKrea2ModelTuner` in `Real Value` mode with a 34-slot `vectors_override` -- 28 transformer
blocks, 2 txtfusion layerwise, 2 refiner, 1 projector, 1 txtmlp -- and every named group input at
0.0. This is NOT the mechanism the leaf bench uses, and the two must not be mixed.

Baselines already exist in benchmark_mappa for both prompts and all three seeds. Nothing to
re-render. Writes data/blk16_ladder_plan.csv. No render is generated here.
"""
import csv, json, os
from PIL import Image

BASE = os.path.expanduser("~/mnt/benchmark_mappa--renders")
OUT = "data/blk16_ladder_plan.csv"
IDX = 16
PROMPTS = ["P01", "P02"]
SEEDS = [42, 777, 1337]
DOSES = ["0.020", "0.035", "0.050", "0.080", "0.120", "0.200"]
SETTINGS = dict(mode="Real Value", sampler="euler_ancestral", scheduler="simple",
                steps=9, cfg=1.0, denoise=1.0, width=1024, height=1280)


def prompt_text(p):
    """Carried from the baseline render's own metadata, so the text cannot drift."""
    f = f"{BASE}/{p}_baseline_krea2_seed42_00001_.png"
    wf = json.loads(Image.open(f).info["prompt"])
    for node in wf.values():
        if node.get("class_type") == "CLIPTextEncode":
            t = node["inputs"].get("text", "")
            if isinstance(t, str) and len(t) > 40:
                return t
    raise RuntimeError(f"no prompt text found in {f}")


def vector(dose, arm):
    v = [0.0] * 34
    v[IDX] = round(float(dose) * (1 if arm == "pos" else -1), 3)
    return v


def main():
    texts = {p: prompt_text(p) for p in PROMPTS}
    rows = []
    for dose in DOSES:
        for arm in ("pos", "neg"):
            v = vector(dose, arm)
            vs = ",".join(f"{x:.3f}" for x in v)
            for p in PROMPTS:
                for s in SEEDS:
                    pre = f"{p}_blk{IDX:02d}{arm}_{dose}_krea2_seed{s}"
                    rows.append(dict(
                        condition=f"blk{IDX:02d}{arm}_{dose}", prompt_id=p, seed=s, dose=dose,
                        arm=arm, nonzero_slots=json.dumps({str(IDX): v[IDX]}),
                        vectors_override=vs, granular_json="",
                        output_prefix=pre, expected_filename=f"{pre}_00001_.png",
                        prompt_text=texts[p], **SETTINGS))
    for i, x in enumerate(rows, 1):
        x["row_index"] = i
    cols = ["row_index", "condition", "prompt_id", "seed", "dose", "arm", "mode",
            "nonzero_slots", "vectors_override", "granular_json", "sampler", "scheduler",
            "steps", "cfg", "denoise", "width", "height", "output_prefix",
            "expected_filename", "prompt_text"]
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for x in rows: w.writerow({k: x[k] for k in cols})
    print(f"{len(rows)} rows -> {OUT}")
    print(f"  {len(DOSES)} doses x 2 arms x {len(PROMPTS)} prompts x {len(SEEDS)} seeds")
    print(f"  slot {IDX} only; every other slot 0.000; 34 slots per vector")


if __name__ == "__main__":
    main()
