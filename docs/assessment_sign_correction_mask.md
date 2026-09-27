# Assessment — a sign-correction mask: rectify a block's internals so its parts stop cancelling

**Date**: 2026-09-27 · **Proposal**: Alessandro — if parts of a block push a property in opposite
directions, and *that* is why a block is not a knob, then identify the opposed parts and **flip
their sign** while the knob is moved, so that every part pushes the same way.
**Material**: `data/style_features_qkvo.csv`, already extracted. **No render.**
This supersedes nothing in [`assessment_sign_aligned_stacking.md`](assessment_sign_aligned_stacking.md),
which answered a different question — combining *whole blocks* rather than rectifying *inside* one.

---

## 1. The premise is supported

Three measurements say a block's parts partly cancel:

* **45 % global mode, 23 % block identity, 32 % signed** (`sign_decomposition_result.md` §3) —
  most of what an edit does carries no directional information.
* **Image motion goes as dose^0.19.** Heavy sublinearity is what partial cancellation produces:
  six times the dose buys 1.39 times the effect.
* **Inside one perturbation, components behave oppositely.** The routing path reverses with the sign
  in 0.067–0.120 of above-noise traits; the value path in 0.538–0.758.

So the proposal is not built on a guess. And it has a natural form: a per-unit sign mask
**s ∈ {−1, +1}ᴺ** applied to the gain vector, chosen so every unit's contribution to the target
property has the same sign.

## 2. The control already exists, which is unusual and worth saying

`Arthemy_Bench_RANDSIGN` is a **random** sign mask at matched Frobenius displacement
(D = 267.37214627, identical to `BLOCKSHUFFLE` and to the calibrated preset). The proposal is a
**measured** sign mask.

> **A measured mask must beat a random mask at the same displacement.** That comparison needs no new
> control and no new null — the project built it a fortnight ago.

And there is already one measurement of a structured rearrangement against a random one at identical
D: `permutation-adds-a-neglected-attribute`, **19/20 against 1/20**. Structure beat noise massively
on a semantic attribute. That is the existence proof the proposal needs.

## 3. The pre-check that decides whether a mask is constructible — and it fails

A fixed mask requires a unit's sign to be **stable**. If the direction a unit pushes a property
depends on what is in the picture, no fixed mask can exist.

Tested on the eight q/k/v/o cells × 23 traits × 8 scenes, sign taken as
`sign(mean(pos) − mean(neg))` when the difference exceeds that trait's seed noise:

| unit | traits with a unanimous sign across 8 scenes | 7/8 | traits below noise in > 4 scenes |
|---|--:|--:|--:|
| `wq_b1` | **0** | 0 | **23 / 23** |
| `wk_b1` | **0** | 0 | **23 / 23** |
| `wv_b1` | 0 | 0 | 10 |
| `wo_b1` | 0 | 0 | 12 |
| `wq_b6` | **0** | 0 | **23 / 23** |
| `wk_b6` | 0 | 0 | 21 |
| **`wv_b6`** | **4** | 1 | 11 |
| **`wo_b6`** | **3** | 2 | 9 |

**7 of 184 (unit, trait) pairs have a unanimous sign. Chance alone predicts 1.4.**
No trait has four or more sign-stable units, so **no mask can be written for any trait at this
granularity.**

And the reason is in the last column: for `wq` and `wk`, **21–23 of 23 traits never clear the seed
noise in the majority of scenes.** There is no sign to read because there is no effect to sign.

## 4. What this does and does not kill

**Killed**: the simplest version — one fixed global sign mask over q/k/v/o × band, read from the 23
global descriptors. The data does not support it, and this pre-check cost nothing where the
experiment would have cost 288 renders.

**Not killed**, and each is a nameable reason the pre-check may be the wrong test:

1. **The eight cells are not displacement-matched** — 23.50 to 65.06, a factor 2.77
   (`sign_decomposition_result.md` §7). A unit given a third of the dose is below noise partly
   *because* of that. The pre-check should be rerun on a matched bench before it is treated as
   final.
2. **These are coarse units.** The proposal is about *finer* granularity, where cancellation should
   be more visible, not less. Eight units is the wrong scale to refute a sub-block hypothesis.
3. **The 23 traits are global descriptors.** They average over the whole frame. A mask for a
   localised property — a colour on an object — could not show up here at all, and that is exactly
   the property the leaf study is about.
4. **Scene-invariance may be too strong a requirement.** A mask that holds within a style family,
   or per prompt, would be weaker than hoped and still useful.

**One thing survives and points the same way as everything else today**: `wv_b6` and `wo_b6` are the
only units with any sign-stable traits at all — 4 and 3 of 23 against 1.4 by chance. If a mask is
ever built, it will be built around the **value path in the late band**.

## 5. The cheapest path that would make this testable

In order, and none of it is launched:

1. **Rerun this pre-check on a Frobenius-matched bench.** Until the units carry equal displacement,
   "below noise" and "given less dose" are the same observation. This is the objection that most
   threatens the negative result above.
2. **Pick a target property that is not a global descriptor** — contrast is the obvious one, since
   `blk00` has just been shown to be a contrast knob
   (`first_block_knob_decisive_test.md` §4), and contrast has a clean per-image estimator.
3. **Then** the mask, at matched displacement, against `RANDSIGN` at the same D.

Alessandro launches renders. This is an assessment.
