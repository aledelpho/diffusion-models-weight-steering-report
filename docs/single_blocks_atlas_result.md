# Single-block atlas — some blocks are controls, most are not, and the ends carry them

**2026-09-29.** `benchmark_single_blocks_atlas`: 171 renders — 28 blocks × 2 signs × 3 prompts
(`P01_blacksmith`, `S1_rally`, `F4_closeup`) + 3 baselines, **dose ±0.350, one seed (2718281)**, one
slot of `vectors_override` at a time. Test fixed before measuring:
[`prereg_single_blocks_identifiability.md`](prereg_single_blocks_identifiability.md) (`63471bd`).
No render generated here.

## 0. "We never worked on sub-blocks" — not so

Checked in the artefacts (pitfall 88): **`benchmark_profondita` and `_neg` did exactly this** — the
same drive, all 28 blocks, both signs, at 0.200, seeds 42/777/1337, prompts P01/P02, 336 renders
(`texture_audit_profondita.csv`, `style_features_profondita.csv`, `report_monotonia_profondita.md`,
2026-09-20). So did `blk16_ladder`, `block1_dissection.md`, `first_block_knob_decisive_test.md`.
What is new here is the dose, two new prompts, and — the part that matters — a test of whether a
block's effect is **the same thing on different pictures**. The atlas's `P01_blacksmith` is the same
text as `P01` everywhere else, and its baseline reproduces `benchmark_centre_push`'s pixel for pixel.

## 1. Guards

All 171 present; the drive read from each render's own graph equals the plan's `vectors_override`;
no perturbed render identical to its baseline.

## 2. T1 — is a block recognisable as itself on another picture?

M[i, j] = cos(Δ of block i on one prompt, Δ of block j on another), averaged over prompt pairs.
Block i is identifiable if its own column is the row maximum. Chance ≈ 1 of 28.

| sign | identifiable | permutation 95th pct | p | which | top-3 |
|---|--:|--:|--:|---|--:|
| + | **5 / 28** | 3 | 0.0015 | **0, 1, 25, 26, 27** | 7 |
| − | **4 / 28** | 3 | 0.0085 | **0, 8, 20, 27** | 7 |

**By the deposited rule the claim is supported** — above the permutation threshold in both signs.
**By its size it is narrow**: 23–24 of 28 blocks are not recognisable across pictures, the mean
own-cosine is only 0.148 (+) and 0.054 (−), and the recognisable ones are, on the positive arm,
**exactly the two ends of the stack**.

## 3. T2 — same picture, another seed and another dose

Atlas (0.350, seed 2718281) against `benchmark_profondita` (0.200), prompt P01. **Deviation from the
spec:** the spec averaged profondita over seeds 42/777/1337; the base cloud holds a P01 baseline at
**seed 42 only**, so T2 uses one seed of profondita.

| sign | identifiable | p | which | top-3 | mean own-cos |
|---|--:|--:|---|--:|--:|
| + | **9 / 28** | 0.0001 | 0, 14, 16, 17, 19, 20, 22, 25, 27 | 16 | 0.394 |
| − | **8 / 28** | 0.0001 | 0, 11, 15, 16, 17, 18, 24, 27 | 14 | 0.343 |

On the **same picture**, about a third of the blocks reproduce across seed and dose — including
several in the middle (14–22). On **different pictures** (T1), only the ends do. **Most middle
blocks do something reproducible, but what they do depends on the image.**

## 4. T3 — two poles, or one direction?

cos(Δ₊, Δ₋) per block, mean over the three prompts: **negative only for blocks 0, 1 and 24**. For
**25 of 28** blocks pushing + and pushing − move the image the **same** way (block 4: +0.76, 12:
+0.56). And across the 56 block × sign cells, **saturation rises in 47** and fine-grain energy
(band 0) in **40**, whichever the sign. For most single blocks the largest thing they do is a
**common mode** — more colour, more grain — not a slider with two ends. It is the "price" Alessandro
asked about on 2026-09-28, visible here one block at a time, and it agrees with
`sign_decomposition_result.md` (45 % of an edit's effect is a mode shared by every block and sign).

## 5. The map — what each zone does

`data/single_blocks_map.csv`: per block and sign, the features whose change has the same sign on all
three prompts. **Chance matters here**: with three prompts a feature agrees by accident with p = 1/4,
so **≈ 5.8 of 23 "consistent" features are expected from nothing**; ≥ 10 has p = 0.041 per cell, 2.3
of 56 cells expected by chance, **14 observed**:

| block | sign | consistent features | leading changes |
|---|---|--:|---|
| 00 | − | 14 | uniform texture ↑, hatching ↑, homogeneity ↓ |
| 00 | + | 10 | spectrum slope ↑, stroke variability ↑, stroke width ↓ |
| 01 | − / + | 10 / 13 | shadow variability ↓ / uniform texture ↑, hatching ↓, high frequencies ↑ |
| 08, 10, 18, 20 | − | 10 | hatching ↓ (8); contours ↑ (10); shadow softness ↓ (18); high frequencies ↑↑ (20) |
| 17 | + | 11 | stroke variability ↓, high frequencies ↓ |
| 23 | + | 12 | shadow variability ↓, colourfulness ↓, softer shadows |
| 25 | + | 15 | shadow variability ↓, hatching ↑, softer shadows |
| 26 | + | 21 | shadow variability ↓↓, homogeneity ↓↓, contours ↑↑ — the collapse |
| 27 | − / + | 12 / 18 | high frequencies ↑↑ / homogeneity ↓↓ — the collapse |

Every other block × sign sits at or near the chance level of consistent features.

## 6. Looked at (reduced resolution — composition, not grain)

`benchmark_single_blocks_atlas/_sheets/ends_vs_middle.png`, blocks 0, 27, 12 on all three prompts:

- **`blk00` is a genuine two-pole control, the same on all three pictures**: − more contrast and
  grit (the close-up's skin goes granular), + softer, flatter, lighter.
- **`blk27` is identifiable for the wrong reason**: its positive arm dissolves every picture into the
  same colour confetti. **Identifiable is not the same as usable** — a collapse is recognisable
  precisely because it is always the same. Its negative arm softens and blurs the background.
- **`blk12` changes content, not style**: framing, a window, the car's position, the hair's shape —
  differently on each prompt, which is why T1 cannot recognise it.

## 7. What this means for "we got everything wrong"

It does not overturn the macro-block work; it sharpens it. The macro-block results kept finding
that **the ends of the stack matter and the middle is mixed** — the U-shaped grain profile of `wo`
yesterday, `Block_1` and `Block_6` as the strongest groups. Single blocks say the same, more
precisely: **block 0 is a clean bipolar style control, blocks 25–27 are strong and recognisable but
their positive arm collapses the image, and the middle blocks mostly move content in
picture-specific ways plus a common "more colour, more grain" mode.** Averaging five of those into a
macro-block mixes one or two real controls with several image-specific kicks — which is why the
macro-blocks looked noisier than their best member.

## 8. Limits

**One seed.** T1's failures in the middle could partly be that seed's trajectory rather than the
image; T2 is the only check and uses one profondita seed. One dose (0.350), which for 26–27 is past
collapse. The "controls" of §5 are features with consistent sign, not effect sizes against noise —
no within-cell noise exists in this atlas.

## 9. For Alessandro's eye

`benchmark_single_blocks_atlas/presets.html` — 28 cards, −0.350 / baseline / +0.350, three prompts.
The analyst's reading is not in the page. The useful comparison is **across prompts**: a block that
does the same thing to the blacksmith, the car and the face is a control.

## 10. Provenance

`experiments/analyze_single_blocks.py --guards --extract` → `data/single_blocks_guards.csv`,
`single_blocks_measures.csv`; `single_blocks_tests.py` → `single_blocks_tests.csv`;
`single_blocks_map.py` → `single_blocks_map.csv`; page: `build_annotation_page.py single_blocks_atlas`.
