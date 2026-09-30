#!/usr/bin/env python3
"""Plan for benchmark_single_blocks_styles — exploratory, no hypothesis.
Same drive as benchmark_single_blocks_atlas (one slot of a 34-slot vectors_override, Real Value),
one seed (2718281, the atlas seed), eight prompts: the F4 fantasy close-up subject verbatim under six
open styles, one vintage sepia photograph, and the cartoon prompt again with the style moved to the
END. Per-block, per-arm dose calibrated from Alessandro's artefact reading at 0.350
(data/single_blocks_eye_artifacts_alessandro.csv), capped at 0.450 as he asked:
OK 0.450 · VWA 0.400 · WA 0.300 · SA 0.250 · VSA 0.200 · BROKEN 0.150.
Writes data/single_blocks_styles_plan.csv. No render."""
import csv, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "single_blocks_styles_plan.csv")
LABELS = os.path.join(ROOT, "data", "single_blocks_eye_artifacts_alessandro.csv")
SEED = "2718281"
DOSE = {"OK": 0.450, "VWA": 0.400, "WA": 0.300, "SA": 0.250, "VSA": 0.200, "BROKEN": 0.150}
SUBJECT = ("extreme expression, hard blue-tinted rim light glowing along the edges of her face, screaming in "
           "terror, seen from a steep low angle, extreme close-up on the head only, pale skin, tight framing, "
           "dutch angle, sharp perspective. female elf, head turning in fear and surprise looking in camera, "
           "short blonde hair in a metty bob haircut, slim blonde eyebrows raised, wide teal eyes wide open, "
           "mouth stretched open in a full-throated panic scream, a gold necklace is flying around. white "
           "background, simple background.")
PROMPTS = [
    ("E1_cartoon", "Cartoon style illustration. " + SUBJECT),
    ("E2_watercolor", "Watercolor painting. " + SUBJECT),
    ("E3_oil", "Oil painting. " + SUBJECT),
    ("E4_colorpencil", "Colored pencil drawing. " + SUBJECT),
    ("E5_childrensbook", "Children's book illustration. " + SUBJECT),
    ("E6_claymation", "Claymation, stop-motion style. " + SUBJECT),
    ("E7_sepiaphoto", "Vintage sepia photograph. " + SUBJECT),
    ("E8_cartoon_styleend", SUBJECT + " Cartoon style illustration."),
]
SET = dict(mode="Real Value", sampler="euler_ancestral", scheduler="simple", steps=9, cfg=1.0,
           denoise=1.0, width=1024, height=1280)

def main():
    lab = {}
    for r in csv.DictReader(open(LABELS, encoding="utf-8")):
        lab[(int(r["block"]), r["sign"])] = r["label_verbatim"].split(" ")[0]
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
                l = lab[(b, sign)]; d = DOSE[l]; v = d if sign == "pos" else -d
                vo = [0.0] * 34; vo[b] = v
                cond = f"blk{b:02d}_{sign}_d{d:.3f}"
                pre = f"{pid}_{cond}_krea2_seed{SEED}"
                rows.append(dict(row_index=i, arm="perturbation", condition=cond, block_idx=b, dose=f"{d:.3f}",
                                 sign=sign, eye_label_at_0350=l, prompt_id=pid, seed=SEED,
                                 nonzero_slots=json.dumps({str(b): v}),
                                 vectors_override=",".join(f"{x:.3f}" for x in vo),
                                 output_prefix=pre, expected_filename=pre + "_00001_.png",
                                 prompt_text=text, **SET))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print(f"{len(rows)} righe -> {OUT}")
    print("dosi per braccio:", Counter((r['sign'], r['dose']) for r in rows if r['arm'] == 'perturbation' and r['prompt_id'] == 'E1_cartoon'))

if __name__ == "__main__":
    main()
