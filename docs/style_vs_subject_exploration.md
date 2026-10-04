# Does a block's effect follow the style or the subject of the prompt? (exploratory)

2026-10-04, for Alessandro's question about "presets per prompt style". Not pre-registered;
the data (benchmark_single_blocks_styles) had been seen, but not with this measure.
Code `experiments/style_vs_subject_consistency.py`, data
`data/single_blocks_styles_style_features.csv`, `data/style_vs_subject_consistency.csv`.

Mean cosine of a block's style-feature change between prompts, seed 2718281:

| | all 56 arms | 28 strongest arms | late blocks 19–27 | middle blocks 03–12 |
|---|---|---|---|---|
| same style (cartoon), 5 different subjects | 0.21 | 0.25 | 0.38 | 0.10 |
| same subject (elf), 7 different styles | 0.08 | 0.10 | 0.24 | 0.04 |
| same style and subject, words moved (E1 vs E8) | 0.61 | — | — | — |

- Style-consistency is higher than subject-consistency on 41 of 56 arms (23 of the 28
  strongest). **Within one style, a block's effect is more alike across subjects than within
  one subject across styles** — Alessandro's impression, measured once.
- But "more alike" is not "alike": 0.2–0.25 is far from the 0.6–0.9 seen across seeds and
  writings (`prompt_writing_result.md`). Coherence across subjects inside a style exists
  mainly in the late blocks (19–27: 0.38; blk27 0.63–0.69, blk26 pos 0.58, blk20 pos 0.58,
  blk23 pos 0.54) and a few others (blk15 pos 0.42, blk16 pos 0.45, blk18 pos 0.38). The
  middle blocks 03–12 do different things on different subjects even in the same style (≈ 0.1).

Limits: one style family on the "same style" side (cartoon) against seven on the other, one
seed, the cartoon prompts are short and alike in structure. Confirmatory design: C49 in the
register.
