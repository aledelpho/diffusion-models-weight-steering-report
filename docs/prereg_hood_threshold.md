# C56 — how small a push completes the hood, block by block

2026-10-06. Exploratory; written before any render. Renders authorised by Alessandro on 2026-10-06.

## Question

The archer (`P3_archerforest`, seed 3141592) has a half-formed hood (C54): 58 of 69 existing edits
complete it, one bf16 rounding step on block 27 does not (C55), blk27 +0.05 does not, blk27 −0.075
does. Alessandro asks whether the dose needed depends on how sensitive a block is to content.

## Content sensitivity (fixed before the renders)

From the equal-dose atlas (`benchmark_single_blocks_atlas`, ±0.35, three prompts, seed 2718281):
median of 1 − layout r against the baseline, per block and sign
(`data/atlas_equal_dose_content_change.csv`, computed 2026-10-06 before this plan). One block per
band of page 21, spanning the range (mean of the two signs):

| band | block | content change at ±0.35 (− / +) |
|---|---|---|
| Style | blk10 | 0.272 / 0.343 |
| Base | blk00 | 0.305 / 0.262 |
| Details | blk20 | 0.132 / 0.166 |
| Correction | blk23 | 0.095 / 0.107 |

## Renders

4 blocks × 2 signs × doses 0.01, 0.02, 0.04, 0.08, 0.16 = 40, plus one re-render of the baseline as
reproduction check (row 0). C47 settings. Plan `data/hood_threshold_plan.csv`.

## Labels

Alessandro, blind to block, sign and dose: the 40 renders and the baseline in random order, 8
shown twice, the C54 labels (*completo (in testa)* / *abbassato* / *a metà* / *assente* / *non
riesco a dirlo*). Self-agreement below 7 of 8 → labels reported as unreliable, no table.

## What is reported

* For each block and sign, the label at each dose, and the **threshold**: the smallest dose labelled
  anything other than *a metà* (no threshold within 0.16 if none).
* Whether the response is a step (half below the threshold, changed at every dose above) or not.
* **Expectation, written now:** the more a block changes content, the lower its threshold — order
  blk10 ≤ blk00 < blk20 < blk23. Checked by the rank correlation (Spearman) between the 8
  block-sign thresholds and the 8 content-change values above, reported with its sign and value; no
  significance threshold (8 points, one seed). A threshold "none within 0.16" ranks last.

Code: `experiments/hood_threshold.py`.
