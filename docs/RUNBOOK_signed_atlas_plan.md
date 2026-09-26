# Plan — the signed atlas, built inside ComfyUI

- **Written:** 2026-09-26. No render has been made for it.
- **Why:** the current atlas gives a region a *magnitude* and not a *direction*. Measured: the two
  independent draws of a region are separated by 1.07–1.84 times their own displacement and their
  mean cosine is **+0.106** — nearly orthogonal (`data/region_draw_consistency.csv`). A region plus
  a coin-flip per weight does not define an axis. A fixed sign does.
- **And it fixes the other defect at the same time.** `docs/atlas_vs_tuner_generator.md` records that
  the present atlas was designed against the checkpoint while importing the tool, so none of its
  conditions corresponds to anything a user can select. This one is built from the node's own
  controls, so every condition is reproducible by moving widgets.

---

## 1. The instrument

**`ArthemyKrea2ModelBlockSurgeonTuner`** — the tool's own docstring calls it *"Tier 2:
High-precision **deterministic** Sub-Block diffusion model component tuning"*. It takes a
`target_block` from `MODEL_TARGET_MAP` and an explicit gain per component group. **No seed, no
chance, no draw.** Set the gain negative and you have the opposite arm, exactly antipodal in the
weights by construction.

Not the Chaos node: that one randomises, which is the thing this design removes.

## 2. The 26 conditions

Bands: the node's **own** six groups, as the widget lists them (`Block_1 (All 0-4)` …), not the
seven-block quarters of the old atlas.

Components: `attn` = the five attention groups set to one gain; `mlp` = the three MLP groups set to
one gain. Nothing mixed.

| # | conditions |
|---|---|
| 24 | 6 bands × {attn, mlp} × {+, −} |
| 2 | **`NORMS_block_scales` over `All Blocks (0-27)`, + and −** → the **declared negative control** |
| **26** | total — the same budget as the atlas already rendered |

The negative control is the point of §5 of `docs/atlas_vs_tuner_generator.md`: a condition known in
advance to be inert, named as such in the plan. `modulation_norm` produced renders byte-identical to
the baseline on all eight prompts; `NORMS_block_scales` is 56 of those 84 tensors and is still
exposed in the UI. **If the pipeline reports those two as distinguishable from the baseline or from
each other, the pipeline is broken and nothing else in the run may be read.**

## 3. The gain, and why it is not matched

Use **one gain for every condition** — the node's own default magnitude is fine — and **measure the
displacement it produces** rather than solving for a target:

    python experiments/measure_all_displacements.py --all --out data/preset_displacements_signed.csv

This is deliberate and it reverses the old choice. Matching D was right for the causal question
(structure or magnitude). It is wrong here, because a user does not hold D fixed: he sets a gain. So
the magnitude difference between bands stays in the data, where a regression can remove it, instead
of being engineered out of the design. Every result is reported twice — raw, and per unit of measured
displacement — exactly as `output-lead-survives-dose-normalisation` requires.

## 4. Corpus

The same 8 prompts and the same 3 seeds (42, 777, 1337) as the atlas already on disk, plus the 8
baselines already rendered — they are reusable, the pipeline is byte-deterministic across a week.

    26 presets × 8 prompts × 3 seeds = 624 renders.

Save each preset with the Preset Saver so the run is reproducible from files, and record the
`Model: N scalar layers` line the loader prints for **every** preset: that one line is what caught
the dead arm.

## 5. What this corpus answers that the present one cannot

1. **Is a band a direction?** Cos(+arm, −arm) per band. Antipodal in the weights by construction; how
   far the image response mirrors it is the measurement. `tail-is-rectified` predicts the tail will
   **not** mirror — positive wrecks, negative barely moves, 9.1× on block 26 — so a band-by-band
   asymmetry map is the expected product, not a failure.
2. **Is the band the unit of control now?** Same within/between contrast as Q1, but with the sign
   fixed the two arms of a band are related by construction, so the question finally has content.
3. **Where do the existing random presets sit?** Each ± pair defines an axis. Every one of the 24
   random presets already rendered gets a coordinate on it: how much of it lies along the band's
   coherent direction and how much is perpendicular. **624 renders already on disk become
   interpretable in a new frame, at no cost.**
4. **The safety map, per band and per component**, in the tool's own coordinates — which is what
   "calibrate the generator" was always supposed to produce.

## 6. The alternative, and it may matter more — the channel atlas

The observer's hypothesis: in a UNet (SD, Illustrious) each block carried a distinguishable role;
in a monolithic DiT the same functions are **distributed along the whole depth**. Everything measured
here is consistent with that: `cost-grows-with-depth` is a gradient and not a set of roles,
`specialization-disagrees-with-separability` has the two instruments disagreeing about which blocks
are alike, and the atlas finds depth gives magnitude and not direction.

**If a function is spread over every block, then the block is the wrong place to look for it.** In a
residual-stream transformer the one coordinate system every block shares is the **channel**: all 28
blocks read from and write to the same 6144-dimensional bus. A "topic" that lives in the model but
in no single block would appear as **a set of channels used consistently across depth** — localised
in width, global in depth, which is the exact complement of everything measured so far.

The tool already has the knob and the research has never used it:
`ArthemyChannelMagnitudeTuner` — *"Vertical Tuning: Partition residual stream channels
(d_model=6144) by static L2 energy into 12 logarithmic bands"* — and the preset format already
carries a `channel_recipes` field, **empty in all 14 presets**. Six sweeps have been run over depth;
the width has never been touched.

**Design, same budget:** 12 channel bands × {+, −} = 24 presets, the same 8 prompts and 3 seeds,
624 renders. It is a **crossed** design against the signed atlas above: one localises in depth and
is global in width, the other the reverse.

**Prediction, to be frozen before it runs:** if the observer's hypothesis holds, the channel bands
should behave *more* coherently than the depth regions did — cos(+, −) closer to −1, a real
within-band consistency, identifiability driven by direction and not only by magnitude. If they
behave the same as the depth regions, the distribution is not channel-aligned either and the search
has to move to a functional partition found from effects rather than from names or energy.

**One caution to state now.** The 12 bands are cut by **static L2 energy of the weights**, not by
function. Energy is a proxy, and if topics do not align with it the bands will mix them. So the
honest first question is narrow: *do energy-defined channel bands behave coherently at all?* A yes
licenses the next step; a no does not refute the hypothesis, it refutes the proxy.

## 7. Which to run first

They cost the same. The signed atlas **completes** a line of work whose numbers are already half
interpreted and whose questions are already posed. The channel atlas **opens** an axis with no prior
at all and, if the observer's reading of monolithic models is right, is where the structure actually
is. That choice is the observer's; both plans are here so it is an informed one.
