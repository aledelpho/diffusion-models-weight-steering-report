# Single blocks: what the exploration of 2026-09-29 → 2026-10-04 established

Status: **exploratory**. Every item below was found by looking first and measuring
second, on data that was already in hand. None of it is confirmed until the
pre-registered runs named at the end are rendered and scored. This page is the
summary Alessandro asked to fix in a commit before the confirmatory work starts.

Sources: `single_blocks_atlas_result.md`, `late_blocks_render_controls_result.md`,
`block1_dissection.md`, `block_groups_and_prompt_order.md`,
`semantic_routing_audit.md`, `data/single_blocks_v4_definitions_alessandro.md`,
`data/block_colour_layout.csv`.

## 1. Single blocks are a better unit than the six macro-blocks

- The groups that survive on two independent prompt sets (styles: 12 prompts; v3+v4:
  11 prompts, other seeds and doses) are positive 08–10, 23–26, 15–16 and negative
  22–27 (`block_groups_and_prompt_order.md` §2). Two of them straddle a macro-block
  boundary (08–10 across Block_2/Block_3; 23–26 across Block_5/Block_6).
- The group that looked natural inside a macro-block, 02–05, did not replicate.
- `Block_1` reproduces `blk00` alone (ratio 1.010) at five times the weight
  displacement (`block1_dissection.md` §4).

Alessandro's phrase for the picture: *knobs of knobs* — a single block is still
broad, but it is closer to one lever than a macro-block is.

## 2. Every edit has a shared part and a specific part

Before the common mode is removed, the two signs of one block correlate positively
on 27 of 28 blocks; after removal they correlate negatively on 25 of 28. Any edit
moves the picture away from the particular baseline in a shared way (the "cost"); the
direction that belongs to the block sits on top of it.

## 3. A block does the same thing whatever the word order

Five orders of one prompt × two seeds: the change a block makes is as stable across
orders as across seeds (r = 0.92 between the two consistencies over 56 arms; median
cosine 0.69 on the 43 arms larger than the reordering itself), and by eye blk19 pos,
blk26 pos (10/10) and blk17 pos (5/5) make the same change every time. The order
does move pose and framing (ΔE 16–31 between baselines). Only the order of an
identical vocabulary was varied: **the claim about writing in general is open**
(→ `prereg_prompt_writing.md`).

## 4. Where the stack is a set of knobs and where it is not

Layout kept (L-channel r with the baseline, 64×80, mean over 23 prompts and both
signs; `data/block_colour_layout.csv`):

| blocks | 00–01 | 02–04 | 05–14 | 15–20 | 21–27 |
|---|---|---|---|---|---|
| layout r | 0.75 | 0.75 | 0.65 | 0.73 | 0.88 |

Alessandro's bands (Base / Style / Details / Correction) hold at the two ends and
blur in the middle; the data show the break at the Correction end, not between
Style and Details.

## 5. blk23 is the cleanest colour lever found so far — not yet a linear one

- Chroma moves the same way on **23 of 23 prompts in both signs** (no other block
  does this), and chroma is the largest share of what it changes (|Δchroma| / ΔE
  0.34; no other arm above 0.25). Layout r 0.89–0.90.
- Doubling the positive dose (0.15 → 0.30) multiplies the chroma loss by 2.2
  (median; 1.6–3.5 over 11 prompts): monotone, somewhat accelerating. The negative
  side has one dose only.
- At 0.30 it is not free of content changes, by eye: a black headband appears (E1
  pos), the outline turns dark red (E1 neg), the rally car's livery changes (pos).
- Whether it beats writing "colorful / high saturation" in the prompt, at matched
  chroma, on content drift, has **not** been tested.

## 6. Alessandro's per-block definitions against measurement

Agree with the features on blk00, blk22, blk23, blk27; blk01 is opposite to blk00 in
grain and detail but not overall; on blk26 pos the statistic disagreed and the 1:1
crop sided with the eye (`block_groups_and_prompt_order.md` §4).

## 7. Withdrawn or not supported

- "Blocks 3–7 at high values end on a blurred background" — not seen at 1:1 on three
  prompts; the blurred background appears at blk08 pos with a photographic switch.
- The "semantic routing" reading of CLIP coherence (`semantic_routing_audit.md`).

## 8. Confirmatory runs that follow

| id | question | document |
|---|---|---|
| C44 | block groups on two new seeds | `open_work_register.md` |
| C45 | writing vs content | `prereg_prompt_writing.md` |
| C46 | is the stable/unstable split visible in the weights? | `prereg_block_weight_structure.md` |
| C47 | blk23 against "colorful" in the prompt | `open_work_register.md` |
