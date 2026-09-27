# Looking at Block 1 and Block 6 — and a grain measure that hides what it is measuring

**Date**: 2026-09-27 · **Trigger**: Alessandro asked the analyst to *look* at the Block 1 and
Block 6 renders rather than only measure them, on the grounds that much of the coherence the numbers
report might be images "highly disturbed in the same way". **Material**: `benchmark_mappa` and
`benchmark_atlas_phase1`, already on disk. **No render generated.** Exploratory.

---

## 1. What the images show, at native resolution

`P01`, seed 42, dose 0.200, crop of the apron and shirt:

| condition | what is visible |
|---|---|
| baseline | clean ink hatching, flat colour fills |
| **`Block_1 pos`** | hatching **reduced**, fills flatter, fewer ink strokes — smoother |
| **`Block_1 neg`** | hatching **increased**, heavier crosshatch on apron and wall — etched |
| **`Block_6 pos`** | a **dense granular stipple** over the whole garment; linework dissolved into speckle |
| **`Block_6 neg`** | **soft, almost airbrushed**; ink outlines gone, everything gradient |

Alessandro's recollection — that the two blocks break the image *differently*, the first in the
structure and the last with a luminous grain — is **correct and visible**. And neither is "disturbed
in the same way" as the other: both remain coherent pictures, differing on different axes.

## 2. The global grain measure says the opposite of the image, for Block 6

High-frequency energy over the whole frame, relative to the same-seed baseline, dose 0.200,
averaged over 2 prompts × 3 seeds:

| block | pos | neg | reading from the global number |
|---|--:|--:|---|
| `Block_1` | **0.848** | 1.038 | pos smooths, neg etches |
| `Block_2` | 1.031 | 0.902 | pos etches, neg smooths |
| `Block_3` | **1.159** | **0.879** | pos etches, neg smooths |
| `Block_4` | 0.746 | 0.989 | both smooth |
| `Block_5` | 0.643 | 1.048 | pos smooths, neg etches |
| **`Block_6`** | **0.933** | **0.842** | **"both smooth"** |

Per cell, `Block_3` is the cleanest knob in the set — **6/6** cells above 1 on the positive arm and
**0/6** on the negative. Nobody has said so. And `Block_1` replicates
`first-block-is-an-inverted-knob` on a corpus that claim was not built on: **0/6** cells above 1 on
the positive arm.

But `Block_6` reads as *"both signs smooth"* — while the crop plainly shows a stipple being added on
the positive arm.

## 3. The measure was hiding it, and here is the mechanism

The global statistic sums high-frequency energy over the whole frame. `Block_6 pos` also **lowers
global contrast** (0.914 of baseline), and a flatter image has less high-frequency energy
everywhere, which swamps a stipple added locally.

Restricting the same measure to the **flattest 40 % of the baseline** — where a stipple shows and
structure does not, the estimator `punto7_attrito_e_rettificazione.md` §7 already uses:

| block | sign | **grain in flat regions** | global HF | global contrast |
|---|---|--:|--:|--:|
| `Block_1` | pos | 1.230 | 0.860 | 0.888 |
| `Block_1` | neg | 1.388 | 1.038 | 1.050 |
| `Block_2` | pos | 1.547 | 1.029 | 0.993 |
| `Block_3` | pos | **1.687** | 1.165 | 1.021 |
| `Block_5` | pos | **0.792** | 0.656 | 1.059 |
| `Block_5` | neg | 1.381 | 1.054 | 0.973 |
| **`Block_6`** | **pos** | **1.322** | 0.926 | 0.914 |
| **`Block_6`** | **neg** | **0.728** | 0.861 | 1.037 |

**`Block_6` adds 32 % grain in flat areas on the positive arm and removes 27 % on the negative.**
A sign swing of **1.82×**, the largest of the six — and the global measure called it "both smooth".

> **A grain statistic summed over the whole frame cannot separate *grain added* from *contrast
> lowered*. On `Block_6` the two happen together and the second hides the first.**

This is a defect of the measure, not of the data, and it was found by looking at the pixels after
the number had already been reported. Pitfall candidate **74**: *a texture statistic that is not
normalised for contrast, or restricted to regions where texture is the only thing present, reports
the sum of two effects and can report the wrong sign of the one being asked about.*

It does not overturn a published claim. `first-block-is-an-inverted-knob` is about the global
statistic and replicates here. `tail-is-rectified` is about amplitude and is untouched. What changes
is that **`Block_6`'s grain behaviour is strongly bidirectional and was previously invisible.**

## 4. What this says about the transfer result

Alessandro's objection was that the transfer score of 0.708 might be detecting images that are all
damaged in the same way. The images say otherwise: `Block_1` and `Block_6` are damaged in
*visibly different* ways, on different axes, and both remain coherent pictures. That is a reason to
take the transfer result more seriously, not less.

The sharper version of the objection survives, and it is not answerable by measurement: if
`Block_6` reliably produces a stipple, a classifier that recognises it is recognising a
**reproducible visual treatment**. Whether a reproducible treatment is a *style* or a *defect* is an
aesthetic judgement, not a statistic — which is what Alessandro said two days ago and what the
damage-or-style study was built to ask a judge, before the judge failed its gate.

## 5. A separate observation from the atlas, at D = 273

A glitch detector (isolated saturated 8×8 tiles, run over all 648 atlas renders; baseline level
0.0150) finds the mosaic corruption is **not a property of a region**:

| condition | mean glitch score |
|---|--:|
| **`early_attn_draw2`** | **0.0485** |
| `late_mlp_draw2` | 0.0299 |
| *baseline* | *0.0150* |
| `early_attn_draw1` | 0.0139 |
| `late_mlp_draw1` | 0.0078 |

**`early_attn_draw1` and `early_attn_draw2` are the same region at the same displacement, and one
glitches while the other is below baseline.** The catastrophic outcome belongs to the **draw**, not
to the region — consistent with the atlas giving a region a magnitude and not a direction
(cos between a region's two draws = +0.106).
