# Groups of blocks, and whether word order changes what a block does

2026-10-04. Exploratory: written **after** Alessandro described both questions and
after the renders below were opened. Nothing here was pre-registered; §5 says what a
confirmatory run would need.

Novelty check (pitfall 87): `docs/` and `notebook/` were searched for "word order",
"prompt order", "styleend", "common mode", "modo comune". The common mode is already
defined in `sign_decomposition_result.md` (c = (D+ + D-)/2) and in pitfall 64; no
document measures word order or pairs of single blocks against each other.

Data: `benchmark_single_blocks_styles` (12 prompts, seed 2718281, Alessandro's
per-block doses), `benchmark_single_blocks_v3` (6 prompts, 2 seeds) and `_v4`
(5 prompts, seed 1234567) — v3/v4 use doses different from styles and from each
other — and `benchmark_prompt_order` (one prompt, P1_elfbrawler, in five word
orders V1..V5, seeds 3141592 and 1234567, 56 arms each).

## 1. What was looked at, and what was seen

Contact sheets and 100 % crops were cut for: blocks 02–09, both signs, on eight
prompts (C1 blacksmith, C3 fox, E2 watercolour, E7 sepia, P3 archer, P2 lotus canoe,
P1 crown top-down, P4 selfie); 1:1 crops of background and face for blocks 03–08 pos
on C1, C3 and P3; the prompt-order sweep for blocks 00, 04, 09, 13, 17, 19, 23, 26,
27 on all five orders.

- **Blocks 02–07, positive, keep the layout and redraw the subject.** On the
  blacksmith, fox and archer the frame, pose and props stay put; the face is redrawn
  (younger, cleaner line, more frontal gaze in 05–06 on the archer, a smile in 07 on
  the blacksmith); smoke appears over the forge from 03 to 07.
- **Blocks 08–09, positive, change the picture, not the drawing.** The crown seen
  from above becomes a crown seen from the side (08, 09); the blacksmith becomes a
  photograph with a real out-of-focus window (08); the selfie changes identity and
  stops winking (08, 09); the fox is framed closer (08). The negatives of 02–09 are
  far milder; the exceptions seen are the crown turned into an open ring at blk06 and
  blk09 neg (dose 0.55).
- **Alessandro's example, "blocks 3–7 at high values end on a blurred background and
  a sharper subject", was not seen on the three prompts cropped at 1:1.** In 03–07 pos
  the background is as sharp as the baseline or sharper (pine needles, birch trunks,
  brick outlines). A blurred background with a sharp face appears once, at **blk08
  pos** on the blacksmith, together with the switch to a photographic look. He gave
  the example as an illustration, not a literal claim; it is recorded so that it is
  not later remembered as confirmed.

## 2. A measure for "the same things in different directions"

`experiments/block_effect_overlap.py`. For every prompt, each arm's change
D = render − baseline in CIELAB at 64×80. For every pair of arms on the same prompt:

- `where` — Spearman r between |D_a| and |D_b| over the grid: do they change the same
  regions?
- `signed` — Pearson r between D_a and D_b: do they push them the same way?
- `signed_resid` — the same after subtracting the prompt's **common mode** (mean D over
  all 56 arms).

The common mode has to go. Before removal the two arms of one block correlate
positively on 27 of 28 blocks (+0.10 to +0.68; blk27 is the exception, −0.17): any perturbation moves the picture
away from the particular baseline in a shared way, the same finding as the
"saturation up in 47 of 56 cells" of the atlas. After removal they correlate
negatively on 25 of 28 (−0.04 to −0.27; `data/block_effect_overlap_mean.csv`).

**Scale caveat.** 64×80 sees layout, light and colour. It is blind to grain and fine
texture, so it says nothing about blocks 00, 01, 21, 26 and 27 as Alessandro describes
them.

`where` has a floor of about 0.40 for every pair (changes concentrate on the subject
whatever the block) and spans 0.27–0.60: too narrow to rank pairs. The structure is
in `signed_resid`, mean over the 12 styles prompts (SE ≈ 0.03–0.07):

| group (positive arms) | pairs | styles, 12 prompts | v3+v4, 11 prompts |
|---|---|---|---|
| 08 · 09 · 10 (07) | 07–09, 08–09, 09–10 | +0.26, +0.27, +0.24 | +0.15, +0.23, +0.16 |
| 23 · 24 · 25 · 26 | 23–24, 24–25, 25–26 | +0.21, +0.31, +0.51 | +0.23, +0.37, +0.36 |
| 15 · 16 | 15–16 | +0.17 | +0.21 |
| 02 · 03 · 04 · 05 | 02–03, 03–04, 04–05 | +0.23, +0.19, +0.20 | +0.05, +0.01, +0.14 |
| early-middle against late | 05–24 | −0.23 (0/12 prompts positive) | −0.22 |

Negative arms: 22–27 form one group (13 of its 15 pairs +0.19 to +0.54, the two with blk24 at +0.08; v3+v4: 22–23 +0.28, 26–27 +0.50); 19–20 +0.20; 01–05 +0.28.

v3+v4 were not used to form the groups, so they are a replication in the weak sense:
same measure, other prompts, other seeds, other doses — chosen after seeing styles.
On that reading **08–10, 23–26 and 15–16 hold; 02–05 does not.** The anti-correlation
of the early-middle blocks with the late ones also holds.

What this says about the intuition, read narrowly. The groups that replicate are
groups of blocks that push the **same** way once the shared component is removed, not
opposite ways. "The same things in different directions" fits better *within* a
block, between its two signs: residually opposite, on top of a common mode that both
signs share. Two exceptions where both signs go the same way even after removal:
**blk25 (+0.34) and blk26 (+0.58)** — in agreement with Alessandro's earlier note
that blk25 "ruins the image in both directions".

## 3. Word order (Alessandro's claim)

Claim, as stated on 2026-10-04: *the weight edits move the output in the same way
whatever the word order, so the weights govern the content more than the way it is
written.*

**3a. The edit is the same across orders — by eye.** blk19 pos (0.35) removes or
shrinks the antlers, turns the gold pauldron into fur or straw texture and drops the
eyepatch, in 10 of 10 renders (5 orders × 2 seeds). blk17 pos turns the fur collar
into a slim lapel, shortens the hair and simplifies the figure toward a doll-like
version, 5 of 5 orders on seed 3141592. blk26 pos (0.20) lays a mosaic of small
colour cells over the whole frame, 10 of 10. blk00 neg (heavier hatching, freckles)
and blk23 pos (paler) are consistent too.

**3b. And by a layout-free measure.** `experiments/prompt_order_feature_consistency.py`
reduces each image to the 23 style features and each arm to the vector of feature
changes. Mean cosine of that vector between different orders (same seed) against
between different seeds (same order), `data/prompt_order_feature_consistency.csv`:

- for the 43 arms whose change is larger than what reordering alone does to the
  baseline (size > 1.11 baseline-SD units), `cos_order` is 0.39–0.98, median 0.69;
- `cos_order` tracks `cos_seed` across the 56 arms (r = 0.92) and is on average 0.06
  higher: **changing the word order disturbs the edit no more than changing the seed
  does.** The clearest single case goes the other way: blk09 pos, 0.60 across orders,
  0.14 across seeds;
- every arm with low consistency (blk01–06 neg, 13–14 neg, 08 pos, 11 neg: cos −0.04
  to 0.22) is among the 13 arms whose change is smaller than the reordering itself
  (size 0.76–1.07); the other three of those 13 (15, 16, 18 neg) reach 0.32–0.59. A
  change smaller than the reordering has no stable direction at this sample size; that
  is not evidence of order-dependence.

**3c. What the experiment cannot show.**

- The word order **does** change the picture: baseline-to-baseline ΔE between orders
  is 16–31 (`data/prompt_order_baselines.csv`), as large as most edits (ΔE 6–25). It
  changes pose and framing, not what is depicted: all ten baselines are the same
  character. So the result is: *given the same content, the word order changes the
  frame but not what a block does to it.*
- "More than the way it is written" is wider than the test. Only the order of an
  identical vocabulary varied. Synonyms, tags vs prose, emphasis, or omitting a
  detail — the ways of writing that change what the text encoder makes of the
  content — were not varied. One subject, one style.
- Reproducibility check passed: V1_Original on seed 3141592 is the same prompt as v3
  P1_elfbrawler on that seed, and the two baselines are pixel-identical (ΔE 0.000).

## 4. Alessandro's v4 definitions against the features (prompt-order data only)

`data/single_blocks_v4_definitions_alessandro.md`. Counted on the 10 prompt-order
images per arm (`data/prompt_order_style_features.csv`), feature higher than the
baseline in n of 10:

- blk00 neg "+ grana, + dettagli": high-frequency share up 10/10, GLCM contrast up
  10/10; pos "sfumato": 0/10 and 0/10. **Agrees.**
- blk01 "opposite to blk00": blk01 pos raises high-frequency share 10/10, neg 1/10 —
  opposite to blk00 **in grain and detail**. At 64×80 the two blocks are not opposite
  (residual r ≈ 0), so "opposite" holds for the texture, not for the whole effect.
- blk22 neg "evidenzia", pos "sfoca e ammorbidisce": edge density 10/10 vs 0/10.
  **Agrees.**
- blk23 saturation: colourfulness neg 10/10 up, pos 0/10. **Agrees.**
- blk27 neg blur, pos grain/sharpen: high-frequency share 0/10 vs 10/10. **Agrees.**
- blk26 pos "+ fine textures, adds grain": the high-frequency share goes **down** 10/10.
  The 1:1 crop settles it in his favour on the look: what blk26 pos adds at 0.20 is a
  mosaic of colour cells 10–20 px across, which reads as grain to the eye and as
  *low* frequency to a share-of-spectrum statistic. The statistic was the suspect, as
  pitfall 90 says it should be. The dose here (0.20) is above the 0.15 he set, and
  the result is destructive.

## 5. What a confirmatory run would need

Groups (§2): fix the three groups that replicated (08–10, 23–26, 15–16 positive;
22–27 negative) and the 05–24 anti-correlation **now**, then render the same 56 arms
on two new seeds of four styles prompts and score `signed_resid` with the same code.
About 4 × 2 × 57 = 456 renders. Word order (§3): two subjects, and a second axis that
changes the writing without changing the order (prose against tags, or synonyms) —
the condition the claim actually needs. Both are Alessandro's to launch.
