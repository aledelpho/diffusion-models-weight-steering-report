# The signature survives every augmentation — and it was never in the colour

**Date**: 2026-09-27 · **Pre-registration**:
[`prereg_signature_robustness.md`](prereg_signature_robustness.md), commit `0b3a8c2`, deposited
before any augmented image existed. **No render generated.** 525 augmented copies, 504 decisions.
**Data**: `data/style_features_mappa_aug.csv`, `data/signature_robustness.csv`.

---

## 1. Result

Transfer across prompt and seed, candidate side augmented, chance 0.50, exact permutation null over
all 720 relabellings of the six P02 blocks:

| condition | all 23 traits | perm p | colour | texture | stroke | tone |
|---|--:|--:|--:|--:|--:|--:|
| `identity` (control) | **0.7083** | 0.026 | 0.514 | **0.778** | 0.750 | 0.514 |
| `hflip` | **0.7500** | 0.029 | 0.542 | 0.778 | 0.764 | 0.625 |
| `rot90` | **0.7083** | 0.024 | 0.569 | 0.778 | 0.750 | 0.583 |
| `hue` +60° | **0.7222** | 0.035 | **0.486** | 0.792 | 0.750 | 0.597 |
| `desat` 50 % | **0.7222** | 0.025 | 0.486 | 0.778 | 0.764 | 0.528 |
| `noise` σ = 8 | **0.7083** | 0.031 | 0.458 | 0.750 | 0.792 | 0.583 |
| `jpeg` q = 40 | **0.7083** | 0.040 | 0.556 | 0.778 | 0.722 | 0.569 |

The `identity` control reproduces **0.7083** exactly, as the parent study measured. The pipeline is
the same pipeline.

## 2. The four predictions

**A1 — CONFIRMED, and by more than was asked.** All six conditions above 0.60; the bar was four of
six. Every condition sits between **0.708 and 0.750**, i.e. **inside the range of the un-augmented
control**, with a permutation p between 0.024 and 0.040. Mirroring, rotating by 90°, rotating the
hue, halving the saturation, adding Gaussian noise and JPEG at quality 40 **did not measurably cost
anything**.

**A2 — not grey, untestable here.** The ranking came out `rot90` < `noise` < `jpeg` < `hue` <
`desat` < `hflip`, but the whole spread is 0.708 to 0.750 — **three items out of 72**. There is
nothing to rank. The prediction assumed some augmentation would hurt; none did, so the question it
asked does not arise on this data. Recorded as a prediction the design could not answer, not as a
result.

**A3 — FALSIFIED, and half of it was right.** Under `hue`, the colour-only transfer falls to
**0.486**, exactly as predicted. Under `noise`, texture-only was predicted to fall below colour-only
and instead held at **0.750** against colour's 0.458. The crossover needed both directions and got
one. Gaussian noise at σ = 8 does not reach the scale at which the texture descriptors carry the
signature.

**A4 — CONFIRMED, 6/6.** `Block_6` scores **1.000 under every augmentation**, 72 items, no miss.
It is now the exception in five separate analyses.

## 3. What was not predicted, and is the real result

Look down the subset columns rather than across the rows.

| subset | traits | share | permutation p |
|---|--:|--:|--:|
| **texture** — `glcm_*`, `lbp_*`, `fft_*` | 8 | **0.7778** | **0.0097** |
| **stroke** — `stroke_*`, `edge_density`, `contour_*`, `crosshatch_*` | 8 | **0.7500** | **0.0222** |
| all 23 | 23 | 0.7083 | 0.0264 |
| **colour** — `color_*`, `colorfulness_hs` | 4 | **0.5139** | **0.2333** |
| **tone** — `luminance_hist_n_peaks`, `shadow_edge_*` | 3 | 0.5139 | 0.1181 |

**The colour traits never carried the signature.** They sit at chance in the `identity` condition —
before any augmentation. The augmentations did not reveal a fragile channel; they revealed that
channel had no signal to lose.

And the consequence for the measurement itself: **texture alone (0.778, p = 0.0097) beats all 23
traits together (0.708, p = 0.026).** The colour and tone traits are diluting the descriptor. Across
all seven conditions texture-only stays at 0.750–0.792 with p ≤ 0.035 everywhere.

## 4. The tension with a published claim, stated and not resolved

`edits-move-colour-in-different-directions` (page 07, status `holds`) reads: *"Different weight
edits move the palette in directions that differ from one another, so the colour response is a
property of which edit was applied and not a single shared drift."*

That is a claim about edits **differing from each other**. This is a claim about a direction
**transferring to a different subject**. They are compatible, and together they say something more
useful than either alone:

> **The colour response is edit-specific but subject-specific too — it does not survive a change of
> content. The texture and stroke response does.**

No status is changed here. If page 07 is ever rewritten, this is the measurement it should cite.

## 5. Limits

* Six augmentations at one strength each. `noise` at σ = 8 and `jpeg` at q = 40 are moderate; a
  harsher setting might find the edge that this one did not.
* Two prompts, one transfer direction (P01 → P02), six items per cell — the parent study's limits
  carry over unchanged.
* This measures what **these 23 descriptors** see. A human observer's robustness is a different
  experiment, and the project's judge has just been shown unable to run it.
* `stroke_width_median_px` is quantised and sits inside the `stroke` subset; the subset is reported
  with it, and the subset's result does not depend on it — texture, which contains no quantised
  trait, is the stronger of the two.
