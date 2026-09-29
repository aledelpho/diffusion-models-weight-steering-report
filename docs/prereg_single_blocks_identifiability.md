# Test spec — are single blocks identifiable controls? (single_blocks_atlas)

**Deposited 2026-09-29, after the renders existed but before any of them was measured or looked at
by the analyst.** It fixes how Alessandro's claim is tested, so the test cannot be chosen after the
numbers. It is exploratory in status (the renders predate it), but its criteria are fixed here.

## The claim

Alessandro: *working on single blocks instead of macro-blocks, "vedo un sacco di controlli
identificabili su ciò che accade in ogni zona".* Read operationally: **each single block, pushed
alone, does something specific to it — recognisable as that block's effect on a different image.**

## What already exists (searched in data, presets, render folders, docs)

`benchmark_profondita` / `_neg`: the same drive (one slot of `vectors_override`), all 28 blocks, both
signs, **dose 0.200, seeds 42/777/1337, prompts P01/P02** (336 renders; `texture_audit_profondita.csv`,
`style_features_profondita.csv`, `report_monotonia_profondita.md`). Also `blk16_ladder`,
`block1_dissection.md`, `first_block_knob_decisive_test.md`. **Single blocks are not new to the
project.** What is new: dose 0.350, two new prompts (S1 rally, F4 close-up), one seed.
The atlas's `P01_blacksmith` is the same text as `P01` there (sha `52e5b19ca6`), and its baseline
reproduces `benchmark_centre_push`'s pixel for pixel.

## Measure

Δ = z(render) − z(baseline, same prompt and seed), 23 style features, base-cloud z-scoring
(`groove_or_hole.py`). One seed per cell: **no within-cell noise estimate exists in this atlas.**

## T1 — identifiable across images (the claim itself)

For each sign, build M[i, j] = mean over the three prompt pairs (A, B) of cos(Δᵢ on A, Δⱼ on B).
Block i is **identifiable** if M[i, i] is the largest value in its row: seen on another image, its
effect looks more like itself than like any of the other 27 blocks. Chance = 1/28 per block.
**Count of identifiable blocks, per sign; significance by permuting the block labels of the second
prompt, 10 000 permutations.** A looser reading, reported alongside: M[i, i] within the row's top 3,
and "identifiable up to a neighbour" (row maximum at i ± 1).
**The claim is supported if the count exceeds the permutation 95th percentile in both signs.**

## T2 — replication on other seeds and another dose (P01 only)

Same construction with A = atlas at 0.350 seed 2718281, B = `benchmark_profondita` at 0.200, mean Δ
over seeds 42/777/1337, same prompt P01. Supported under the same rule. This is the stronger test:
different seeds, different dose, a bench nobody looked at for this purpose.

## T3 — does a block have two poles?

Per block, cos(Δ₊, Δ₋), mean over the three prompts. Reported as a profile over depth; no verdict.

## Descriptive — "what each zone controls"

Per block and sign: the three features with the largest |Δz| **whose sign agrees on all three
prompts**, the five band-energy ratios, mean saturation. This is the map he asked for; it is a
description, not a test, and it is shown next to T1 so that a block with an eloquent description but
no identifiability is not mistaken for a control.

## The limit that governs everything

**One seed.** C41 showed yesterday that at ±0.100 a slice of five tensors agreed with itself across
seeds at cos 0.06–0.39, and at ±0.350 at 0.46–0.78. A single block at 0.350 carries **13 tensors of
one block**, not five of one kind across five blocks, so that number does not transfer — but the
risk does: part of what looks like a block's effect on one seed may be that seed's trajectory. T2 is
the only check on it here.
