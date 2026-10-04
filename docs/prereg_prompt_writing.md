# Pre-registration C45 — does the way a prompt is written change what a block does?

Written 2026-10-04, before any render. Renders are launched by Alessandro only.

## Claim under test (Alessandro, 2026-10-04)

*"Moving the weights gives similar results when the prompt describes the same
content; the structure of the text does not matter more than the content."*

`benchmark_prompt_order` supports it for **word order** only (`block_groups_and_prompt_order.md`
§3). This run varies the writing in ways that change what the text encoder
(Qwen3-VL 4B, an LLM, not CLIP) receives, while keeping the facts fixed, and adds a
content change at fixed writing as the comparison the claim needs.

## Design

Two subjects, four writings each, one content change each, two seeds, 24 arms.

| id | subject | writing | content |
|---|---|---|---|
| S1_W1 | elf brawler | original (tags-and-phrases mix) | reference — **reuses** `benchmark_prompt_order` V1_Original |
| S1_W2 | elf brawler | reordered | reference — **reuses** V5_Inverse |
| S1_W3 | elf brawler | pure tag list | same facts |
| S1_W4 | elf brawler | prose with synonyms | same facts |
| S1_C1 | elf brawler | as W1 | gauntlet changed (silver/electric → bronze/flames) |
| S2_W1 | lotus canoe | original prose | reference |
| S2_W2 | lotus canoe | sentences reordered | same facts |
| S2_W3 | lotus canoe | pure tag list | same facts |
| S2_W4 | lotus canoe | prose with synonyms | same facts |
| S2_C1 | lotus canoe | as W1 | sleeper changed (young woman/book/dress → old bearded man/flute/robe) |

Arms (doses and vectors copied from `data/prompt_order_experiment_plan_full.csv`,
so S1_W1/W2 can be reused): blocks **00, 02, 05, 08, 09, 12, 13, 15, 17, 19, 23, 27**,
both signs — 24 arms + baseline. Seeds 3141592 and 1234567. Settings identical to
`benchmark_prompt_order`: Krea-2 turbo bf16, euler_ancestral / simple, 9 steps,
cfg 1.0, 1024 × 1280, Tuner in Real Value.

New renders: 8 prompts × 25 conditions × 2 seeds = **400**, plus **1** reproducibility
render (V1_Original baseline, seed 3141592, must be pixel-identical to the existing
file before anything else is scored).

## Prompts (verbatim — to be copied, not edited)

**S1_W1** = `V1_Original`, **S1_W2** = `V5_Inverse`, texts in `data/prompt_order_experiment_plan_full.csv`.

**S1_W3**
```
realistic western comics style, bold ink outlines, hatched shadows, high angle, from above, top view, upper body portrait, close-up on gauntlet, dynamic pose, dramatic angle, strong perspective, female elf brawler, small pale antlers, pointed ears, young adult, tousled green hair, green hair fading to teal tips, thick green eyebrows, eyepatch over one eye, sharp bright green eye, tan sun-kissed skin, skin gradient, wide reckless grin, smug grin, half-closed eye, wildly smug expression, looking to her left, fur-collared dark navy jacket, gold wood-textured pauldron, black uniform, brown leather arm straps, heavy silver gauntlet, blue electric energy, crackling electricity, fist toward viewer, white empty background, flat background, warm light, deep amber shadows, sharp blue highlights on gauntlet
```

**S1_W4**
```
An illustration in a realistic Western comic-book manner, drawn with heavy inked contours and cross-hatched shading. We look down on her from high above, in an energetic half-length portrait framed tightly around her armored fist, with a bold pose, a striking camera angle and pronounced foreshortening. She is a young adult elven pugilist with a modest pair of pale antlers and pointed ears. Her messy green hair turns teal toward the ends, and her brows are dense and green. A patch covers one of her eyes; the other is a vivid, bright green and half shut. Her tanned, sun-warmed skin shades gradually from tone to tone. She wears a broad, reckless, self-satisfied smirk and an extremely smug look, and she glances toward her left. Her dark navy coat has a fur collar and a golden shoulder guard with a wood-grain texture, worn over a black uniform with brown leather straps around her arms. On one hand she wears a massive silver armored glove sparking with blue electricity, and she thrusts that fist toward the viewer. The backdrop is plain, empty and white. The light is warm, with deep amber shadows and crisp blue highlights running along the electrified glove.
```

**S1_C1** = `V1_Original` with exactly two substitutions:
`a heavy silver gauntlet crackling with blue electric energy` → `a heavy bronze gauntlet wreathed in orange flames`;
`sharp blue highlights along her electrified gauntlet` → `sharp orange highlights along her flaming gauntlet`.

**S2_W1** = `P2_lotuscanoe` text in `data/single_blocks_v3_plan.csv` (verbatim).

**S2_W2**
```
Refined fantasy illustration, smooth painterly digital brushwork, rich botanical detail, softly modeled forms, subtle luminous highlights, atmospheric depth, elegant color transitions, tranquil magical light, serene and mysterious, award winning, a breathtaking masterpiece. The pond becomes progressively darker toward the edges, shifting into deep teal, petrol and midnight blue. Pale pink lotus blossoms and buds emerge between dense emerald leaves. A luminous turquoise opening in the vegetation surrounds the canoe, revealing clear water, submerged rocks and delicate caustic light patterns below. Inside, a young woman sleeps peacefully on her back along the length of the boat. She wears a flowing ivory dress with soft layered fabric cascading around her legs, her bare feet visible near the stern. One arm bends above her head while the other rests across her torso holding a small closed book. Her head is turned gently to one side, long dark wavy hair spread across the wooden boards. The entire canoe is visible and positioned near the center, surrounded by immense round lotus leaves in many sizes. Dreamlike top down fantasy scene viewed from a perfectly vertical overhead camera, looking straight down onto a narrow weathered wooden canoe drifting through a vast deep lotus pond.
```

**S2_W3**
```
dreamlike fantasy scene, top-down view, perfectly vertical overhead camera, looking straight down, narrow weathered wooden canoe, drifting, vast deep lotus pond, entire canoe visible, canoe near center, immense round lotus leaves, lotus leaves in many sizes, young woman, sleeping peacefully, lying on her back along the boat, head turned to one side, long dark wavy hair spread on wooden boards, one arm bent above head, other arm across torso, holding a small closed book, flowing ivory dress, soft layered fabric around legs, bare feet near the stern, pale pink lotus blossoms, lotus buds, dense emerald leaves, luminous turquoise opening in the vegetation around the canoe, clear water, submerged rocks, caustic light patterns, pond darker toward the edges, deep teal, petrol blue, midnight blue, refined fantasy illustration, smooth painterly digital brushwork, rich botanical detail, softly modeled forms, subtle luminous highlights, atmospheric depth, elegant color transitions, tranquil magical light, serene, mysterious, award winning, breathtaking masterpiece
```

**S2_W4**
```
A fantasy scene with the quality of a dream, taken by a camera placed exactly overhead and aimed straight down at a slender, worn wooden canoe floating across an enormous, deep pond of lotuses. The whole boat can be seen, sitting close to the middle of the frame, ringed by huge circular lotus pads of varied sizes. In it a young woman lies asleep on her back, stretched along the boat, calm and at rest. Her face is tilted softly to one side and her long, dark, wavy hair fans out over the wooden planks. One of her arms is folded above her head; the other lies over her chest and holds a little closed book. She is dressed in a flowing gown of ivory, its soft layers of fabric spilling around her legs, and her bare feet show near the back of the canoe. Pale pink lotus flowers and buds rise among thick emerald leaves. Around the boat, a glowing turquoise gap in the plants shows clear water, rocks under the surface and fine rippling caustic light beneath. Toward its borders the pond grows steadily darker, turning deep teal, petrol and the blue of a midnight sky. An elegant fantasy painting with smooth digital brush strokes, lush botanical detail, gently sculpted shapes, delicate glowing highlights, a sense of atmospheric depth, graceful shifts of colour, calm enchanted light, peaceful and enigmatic, prize-winning, a stunning masterpiece.
```

**S2_C1** = S2_W1 with exactly these substitutions:
`a young woman sleeps peacefully on her back` → `an old bearded man sleeps peacefully on his back`;
`Her head is turned gently to one side, long dark wavy hair spread across the wooden boards` → `His head is turned gently to one side, long grey beard spread across the wooden boards`;
`holding a small closed book` → `holding a small wooden flute`;
`She wears a flowing ivory dress with soft layered fabric cascading around her legs, her bare feet visible near the stern` → `He wears a loose grey robe with heavy folds of fabric around his legs, his bare feet visible near the stern`.

Alessandro reads the eight texts before launch; any change is made here, in a commit,
before the first render.

## Measures (scored by Claude, code fixed before renders)

Per image: the 23 style features (`style_features.py`). Per arm and seed:
dF = F(arm) − F(baseline of the same prompt and seed), each feature divided by the SD
of that subject's baselines (all writings, both seeds). Per arm:

- `A_writing` — mean cosine of dF between different writings of the same content, same
  seed (6 pairs × 2 seeds per subject).
- `A_content_small` — cosine between W1 and C1, same seed.
- `A_subject` — cosine between S1_Wk and S2_Wk, same k and seed.
- `A_seed` — cosine between the two seeds, same prompt.
- `size` — mean |dF|; `size_writing` — the same quantity between baselines of different
  writings of one subject (what the writing alone does).

Arms scored: those with `size` > `size_writing` (decided on the data by this rule, not
by hand).

## Decision rule

- **Supported:** median over scored arms of (A_writing − A_seed) ≥ −0.10, **and**
  A_writing > A_subject on ≥ 75 % of scored arms, **and** A_writing > A_content_small on
  ≥ 60 %.
- **Refuted:** median (A_writing − A_seed) < −0.20, **or** A_writing > A_subject on
  < 50 % of scored arms.
- Otherwise **inconclusive**.

Secondary (reported, not decisive): the same with W3 (tags) alone against W1, since it
is the largest change of writing; the baseline-to-baseline change per writing (does
the writing alone change content?); a CLIP ViT-B/32 version of the same cosines, read
under the caveat of `semantic_routing_audit.md` §3.

## The eye, before the numbers

For each arm a sheet with one row per prompt of a subject (W1–W4, C1), baseline and
arm side by side, both seeds. Alessandro marks each arm *same change across writings:
yes / partly / no* and *same change after the content change: yes / partly / no*,
before seeing any number. If the eye and the rule disagree, the rule is the suspect
(pitfall 90) and the disagreement is reported, not resolved by picking one.
