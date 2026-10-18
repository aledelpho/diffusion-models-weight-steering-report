# C98 result — micro-watersheds on a single leaf (existing renders)

2026-10-18. Pre-registration `docs/prereg_watersheds_leaf.md` and script `experiments/watersheds_leaf.py` (fd313a9,
before the run). Renders: the colour-binding corpus (`Text2Img/benchmark_colour_binding/renders`), prompts LP (purple
leaf), LG (green), LN (no colour word) at seeds 42, 777, 1337, 12 edits at 0.050 per cell (six block groups × two
signs). Outputs `data/watersheds_leaf_cells.csv`, `data/watersheds_leaf_tests.csv`; overlay
`Text2Img/_micro_watersheds/leaf_flip_overlay.jpg`.

## Verdicts

| rule | value | verdict |
|---|---|---|
| R1 — the same places flip across the 12 edits (texture removed) | median partial r ≥ 0.30 in **7 of 9** cells (0.27–0.46) | **replicated** (at the threshold) |
| R2 — one word (the colour) hits the same places | median 0.338 over 6 (0.02–0.52) | supported, with a wide spread |
| T1 — flips carry the change (reported) | share of squared change at Δ ≥ 32: 0.656 at 0.05, 0.878 at 0.20 | — |
| same-seed vs different-seed maps across prompts (reported) | +0.199 vs +0.047 | not a test here: at a seed the three prompts draw nearly the same leaf |

## What flips on a leaf (looked at, Claude, conditions known)

No object appears or disappears, unlike the archer's fletching. The places that flip most often are the **veins** and
the **outline** of the leaf, with the stem; on the purple leaf a halo around the contour (the serrated edge shifts).

## An exploratory control, after the run (not pre-registered)

Thin structures change under any small geometric jitter. A map of where the baseline changes when shifted by one pixel
(the maximum over four directions) was added as a second covariate:

| | texture only | texture + one-pixel jitter |
|---|---|---|
| leaf, cells ≥ 0.30 | 7 of 9 | **5 of 9** (0.15–0.40) |
| archer (C96), median partial r | 0.506 | **0.506** |

On the archer the fragile places are not moved edges; on the leaf part of the effect is jitter of veins and outline,
and part remains beyond it.

## Reading

The fragility replicates on a minimal picture, three new seeds and three prompts, but in a weaker and different form:
on a leaf with nothing optional to add or remove, the small edits reshuffle the same fine structures (veins, contour)
more than discrete details. The one-pixel jitter control should be reported for every test of this family; it is
added to C97 as an amendment before its analysis.
