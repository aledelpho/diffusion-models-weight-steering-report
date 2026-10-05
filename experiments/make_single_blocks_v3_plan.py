#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plan for benchmark_single_blocks_v3 — exploratory single block sweep with tuned doses.
6 prompts total (3 previous with seed 3141592 + 3 new with seed 1618033).
Tuned per-block doses based on Alessandro's notes on benchmark_single_blocks_styles.
Writes data/single_blocks_v3_plan.csv. No render."""
import csv
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT = DATA_DIR / "single_blocks_v3_plan.csv"

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

SEED_V1 = "3141592"
SEED_V2 = "1618033"

PROMPT_GROUPS = [
    (SEED_V1, [
        ("P1_elfbrawler", (
            "realistic western comics style, bold ink outlines, hatched shadows, smug grin with half-closed eye, "
            "seen from a high angle, from above, top view, dynamic, upper body portrait, close-up on gauntlet, "
            "dynamic pose, dramatic angle, strong perspective. female antlered elf brawler, tousled green hair "
            "fading to teal at the tips, thick green eyebrows, an eyepatch over one eye, pointed ears, tan "
            "sun-kissed skin gradient, small pair of pale antlers, young adult, a sharp bright green visible eye, "
            "wide reckless grin. fur-collared dark navy jacket with a gold wood-textured pauldron, black uniform, "
            "brown leather arm straps. looking to her left, wearing a heavy silver gauntlet crackling with blue "
            "electric energy, showing fist to viewer, wildly smug expression. "
            "Background: white empty background, flat background. Lighting: warm light, deep amber shadows and sharp "
            "blue highlights along her electrified gauntlet."
        )),
        ("P2_lotuscanoe", (
            "Dreamlike top down fantasy scene viewed from a perfectly vertical overhead camera, looking straight down "
            "onto a narrow weathered wooden canoe drifting through a vast deep lotus pond. The entire canoe is visible "
            "and positioned near the center, surrounded by immense round lotus leaves in many sizes. Inside, a young woman "
            "sleeps peacefully on her back along the length of the boat. Her head is turned gently to one side, long dark wavy "
            "hair spread across the wooden boards. One arm bends above her head while the other rests across her torso "
            "holding a small closed book. She wears a flowing ivory dress with soft layered fabric cascading around her legs, "
            "her bare feet visible near the stern. Pale pink lotus blossoms and buds emerge between dense emerald leaves. "
            "A luminous turquoise opening in the vegetation surrounds the canoe, revealing clear water, submerged rocks and "
            "delicate caustic light patterns below. The pond becomes progressively darker toward the edges, shifting into "
            "deep teal, petrol and midnight blue. Refined fantasy illustration, smooth painterly digital brushwork, rich "
            "botanical detail, softly modeled forms, subtle luminous highlights, atmospheric depth, elegant color transitions, "
            "tranquil magical light, serene and mysterious, award winning, a breathtaking masterpiece"
        )),
        ("P3_archerforest", (
            "A young adult female, appearing of Caucasian ethnicity, with brown hair and piercing, focused eyes, crouches "
            "low amidst dense evergreen foliage. She wears a dark grey hood obscuring some of her hair, a vibrant crimson "
            "cloak draped over her shoulders, and earthy brown trousers. Her attire includes a dark tunic and leather bracers "
            "on her forearms, adorned with metal studs. Dirt smudges mark her arms and face, suggesting a wilderness survivalist. "
            "She firmly grips a wooden bow, an arrow nocked and its feather fletching visible, her posture tense and alert. "
            "Her expression is one of intense concentration and stealth. The environment is a dark, natural forest setting, "
            "with thick pine branches and textured bark in the foreground and background. The lighting is dim and dappled, "
            "creating dramatic shadows and highlighting her form with a subtle, mystical glow. The overall mood is suspenseful "
            "and wild, with a realistic, painterly style reminiscent of fantasy concept art. The composition is a medium close-up, "
            "capturing her action and intense gaze, viewed from a slightly low angle. The texture is pronounced, with visible "
            "brushstrokes and traces of paint that imitate the painting process using layered tones. Loose, energetic brushstrokes "
            "create a sense of movement and action. A sense of depth is achieved through varying densities of brushstrokes. "
            "The painting style resembles abstract realism and impressionism. Soft shadows and highlights reflect every "
            "detail and give the scene volume."
        )),
    ]),
    (SEED_V2, [
        ("P4_selfie", (
            "A young woman poses for a playful outdoor selfie under a clear blue sky, holding a large iced green drink with a straw. "
            "Her dark curly hair is styled loosely with strands framing her face, and she wears a light cream textured top, a delicate necklace, "
            "and a statement ring. Her dotted manicure and winking expression add a fun, carefree touch, while the bright sunlight and "
            "low-angle perspective give the image a fresh, summery, candid feel."
        )),
        ("P5_gingervampire", (
            "A gorgeous 18-year-old girl. Photorealistic portrait of a ginger vampire girl with long, voluminous curly red hair cascading "
            "over her shoulders, pale porcelain skin with subtle freckles, glowing amber eyes, and sharp vampire fangs slightly visible in a "
            "mysterious smile. She has a lean athletic physique with a toned stomach and defined waist, elegant posture, and graceful but predatory "
            "presence, navel. Wearing a dark gothic outfit — fitted black leather corset and flowing shadowy fabric — standing in dim moonlight. "
            "Dramatic cinematic lighting, soft mist, gothic castle background, cold blue and silver tones contrasting with her fiery hair, "
            "ultra-detailed skin texture, realistic lighting, 85mm lens, shallow depth of field, hyperrealistic, 8k, high contrast, "
            "atmospheric, dark fantasy aesthetic. Thick muscular thighs."
        )),
        ("P6_ghostgirl", (
            "illustration of Full-body portrait of a slim young woman drawn as a semi-translucent, softly glowing ghost with pale-blue skin dusted "
            "in sparkle/star specks, floating weightlessly with her lower legs and feet fading into an ethereal wisp. Voluminous translucent "
            "pale silvery-blue hair worn in a high ponytail tied with a royal-blue bow, soft bangs, vaporous trailing ends. Gentle, faintly shy "
            "expression with a soft downward gaze and blushed cheeks. She wears a royal/cobalt-blue puff-sleeved blouse with a ruffled front placket "
            "and collar, a long tan/caramel-brown bib apron over it (front pocket, dark brown/burgundy tie-bow at the back), dark brown/maroon leggings, "
            "and translucent pointed slip-on shoes that fade from ghost-blue to reddish-pink at the toes. She holds a white coffee mug at waist level "
            "in one hand while her other hand is raised in a delicate pinching/sprinkling gesture above it, and a swirling starry ribbon of orange-and-purple "
            "cosmic steam curls up from the mug. Pose: floating upright, roughly front-facing."
        )),
    ]),
]

SET = dict(mode="Real Value", sampler="euler_ancestral", scheduler="simple", steps=9, cfg=1.0,
           denoise=1.0, width=1024, height=1280)


def build_plan():
    rows, i = [], 0
    for seed, prompts in PROMPT_GROUPS:
        for pid, text in prompts:
            i += 1
            pre = f"{pid}_baseline_krea2_seed{seed}"
            rows.append(dict(row_index=i, arm="baseline", condition="baseline", block_idx="", dose="0.000",
                             sign="", eye_label_at_0350="", prompt_id=pid, seed=seed, nonzero_slots="{}",
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
                    pre = f"{pid}_{cond}_krea2_seed{seed}"
                    rows.append(dict(row_index=i, arm="perturbation", condition=cond, block_idx=b, dose=f"{d:.3f}",
                                     sign=sign, eye_label_at_0350="", prompt_id=pid, seed=seed,
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
