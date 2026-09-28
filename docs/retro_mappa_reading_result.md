# The map, re-read — and the project's working dose is past a knee

**Date**: 2026-09-28 · **Material**: `benchmark_mappa` (dose sweep, 6 groups × 2 arms × 6 doses)
and `benchmark_profondita`/`_neg` (28 single blocks at 0.200), all measured weeks ago ·
**Script**: `experiments/retro_mappa_reading.py` → `data/retro_mappa_cells.csv`,
`data/retro_mappa_dose.csv` · **No render, and no image was read** — everything comes from
`data/retro_texture_axes.csv`.

---

## 1. The finding: 0.200 is on the wrong side of a cliff for two groups

Structure coherence along the dose ladder, ratio to the untouched render:

| group | arm | 0.020 | 0.035 | 0.050 | 0.080 | 0.120 | **0.200** |
|---|---|--:|--:|--:|--:|--:|--:|
| `Block_1` | pos | 0.992 | 0.996 | 0.996 | 0.997 | 0.986 | 0.988 |
| `Block_1` | neg | 1.001 | 0.999 | 1.010 | 1.005 | 1.007 | 1.020 |
| `Block_2` | pos | 1.002 | 0.999 | 0.994 | 0.998 | 1.002 | 1.013 |
| `Block_2` | neg | 0.997 | 1.001 | 1.000 | 0.992 | 0.989 | 0.993 |
| `Block_3` | pos | 0.995 | 0.995 | 0.999 | 1.002 | 1.013 | 1.009 |
| `Block_3` | neg | 0.991 | 0.994 | 0.981 | 0.976 | 0.970 | 0.981 |
| `Block_4` | pos | 0.989 | 0.984 | 0.978 | 0.967 | 0.961 | 0.979 |
| `Block_4` | neg | 1.000 | 1.002 | 1.000 | 1.000 | 0.993 | 1.002 |
| **`Block_5`** | **pos** | 0.997 | 0.996 | 0.994 | 0.996 | 0.994 | **0.950** |
| `Block_5` | neg | 1.001 | 1.001 | 1.008 | 1.008 | 1.018 | 1.033 |
| **`Block_6`** | **pos** | 1.005 | 1.009 | **1.016** | 1.012 | 1.009 | **0.927** |
| **`Block_6`** | **neg** | 0.993 | 0.984 | 0.978 | 0.958 | 0.926 | **0.794** |

Read as change in coherence per unit of log-dose, step by step — which removes the fact that the
steps are not equal:

| group | arm | ×1.75 | ×1.43 | ×1.60 | ×1.50 | **×1.67** | |
|---|---|--:|--:|--:|--:|--:|---|
| `Block_5` | pos | −0.002 | −0.006 | +0.006 | −0.007 | **−0.085** | 12× the previous step |
| `Block_6` | pos | +0.008 | +0.020 | −0.009 | −0.007 | **−0.162** | 23× |
| `Block_6` | neg | −0.015 | −0.018 | −0.042 | −0.079 | **−0.257** | 3.3×, and accelerating throughout |

**The last step is not the largest dose ratio** — the first is (×1.75). Yet it produces a collapse
in three conditions. `Block_6 pos` *improves* the drawing all the way to 0.120 and then falls off a
cliff; `Block_5 pos` is flat and then falls; `Block_6 neg` degrades throughout and then accelerates.

**0.200 is the dose almost every bench in this project uses.** For `Block_6` — the most-used group
in the corpus, the one page 08 is about — every result at 0.200 is measured past the knee.

## 2. What backing off actually costs

| group | arm | dose | displacement | coherence | |
|---|---|--:|--:|--:|---|
| `Block_6` | pos | 0.120 | 0.106 | **1.009** | the line is above baseline |
| `Block_6` | pos | **0.200** | 0.138 | **0.927** | +30 % movement, the drawing goes |
| `Block_5` | pos | 0.120 | 0.180 | 0.994 | |
| `Block_5` | pos | **0.200** | 0.225 | 0.950 | +25 % movement, the drawing goes |
| `Block_6` | neg | 0.120 | 0.241 | 0.926 | |
| `Block_6` | neg | **0.200** | 0.512 | 0.794 | +113 % movement — here the dose does buy something |

**For the two positive arms the last dose step is a bad trade: a quarter to a third more movement
for the whole drawing.** For `Block_6 neg` it is a real trade — the movement doubles — and whether
it is worth it depends on whether the drawing is wanted.

`Block_5 neg` has no knee at all and rises monotonically to 1.033: it is the cleanest knob on the
map by this axis, and nothing in the project has ever singled it out.

## 3. Each group has a scale signature, and they are not the ones the narrative assumed

Band energy against the untouched render, dose 0.200:

| group | arm | 1–2 px | 2–4 px | 4–8 px | 8–16 px | 16–32 px | shape |
|---|---|--:|--:|--:|--:|--:|---|
| `Block_1` | pos | 0.793 | 0.610 | **0.582** | 0.679 | 0.780 | **a mid-scale hole** |
| `Block_1` | neg | 1.116 | 1.452 | **1.520** | 1.286 | 1.125 | **a mid-scale hump** |
| `Block_2` | pos | 1.012 | 0.981 | 0.979 | 0.976 | 0.979 | flat — it does almost nothing |
| `Block_2` | neg | 0.928 | 0.977 | 0.962 | 0.956 | 0.953 | flat |
| `Block_3` | pos | 1.183 | 1.054 | 0.944 | 0.972 | 1.059 | fine detail up |
| `Block_3` | neg | 0.915 | 1.036 | 1.223 | 1.233 | **1.277** | **tilt: fine down, coarse up** |
| `Block_4` | pos | 0.733 | 0.827 | 1.009 | 1.086 | **1.167** | **tilt, the strongest on the map** |
| `Block_4` | neg | 1.054 | 1.183 | 1.178 | 1.099 | 1.125 | broad hump |
| `Block_5` | pos | 0.694 | 0.949 | **1.304** | 1.196 | 1.125 | fine stripped, mid added |
| `Block_5` | neg | 1.056 | 0.945 | 0.884 | 0.992 | 1.073 | a shallow notch |
| `Block_6` | pos | 0.950 | 1.135 | **1.275** | 1.070 | 0.893 | **a mid-scale hump** |
| `Block_6` | neg | 0.746 | **0.450** | 0.504 | 0.708 | 0.973 | **a notch at 2–8 px** |

Two things worth saying out loud.

**`Block_1` and `Block_6` act at the same scale.** Both peak at 4–8 px, `Block_1 neg` at ×1.520 and
`Block_6 pos` at ×1.275, and both cut a hole there on the opposite arm. The notebook's long-running
contrast between them — the first "amplifies deep and damages structure", the second "focuses and
makes a luminous grain" — is not a difference of *where* they act. On this axis they are the same
operator with different signs, and whatever separates them is not spatial scale.
That is a claim page 08 does not make and does not exclude; it is new, and it is free.

**`Block_4` is the tilt block.** 0.733 at the finest scale rising monotonically to 1.167 at the
coarsest — it removes fine detail and adds broad structure, the strongest monotone tilt on the map.
That is a much more specific description than "it changes contrast", and it fits what an observer
saw in its renders: flat colour, clean shapes, no speckle.

## 4. `blk27` is two-sided, which the earlier reading missed

| condition | displacement | coherence | |
|---|--:|--:|---|
| **`blk27` pos** | **0.379** | **1.023** | the largest line-preserving move of all 56 |
| `blk00` neg | 0.277 | 1.032 | |
| `blk18` neg | 0.164 | 1.005 | |
| `blk21` pos | 0.163 | 1.010 | |
| `blk16` pos | 0.134 | 1.015 | |
| `blk27` **neg** | — | **0.805** | 75th of 80, one of the corpus's worst |

**26 of 56 single-block conditions raise coherence at all.**

`style_damage_frontier.md` called `blk27` a trap and moved the recommendation to `blk16`. That was
right about the arm it examined and wrong as a statement about the block: **`blk27` destroys the
drawing pushed negative and strengthens it pushed positive**, and in the positive arm it is the
largest line-preserving move on the map — 2.8× `blk16`'s displacement on this metric.

*The displacement here is the root-mean-square of the log band ratios, a different quantity from
the `style_shift` of `style_damage_frontier.md`. The two rankings are not interchangeable and this
one is not a correction of that one.*

## 5. What this changes

* **A dose below 0.200 is the operating point for `Block_5 pos` and `Block_6 pos`.** 0.120 keeps
  three quarters of the movement with the drawing intact or better.
* **Every `Block_6` result in this project at 0.200 was measured past the knee.** Nothing is
  withdrawn on that basis — those results are what happens at 0.200, which is a real regime — but
  any of them read as "what `Block_6` does" describes the far side of a cliff.
* **`Block_5 neg` and `blk27 pos` were never singled out** and are, by this axis, two of the best
  behaved conditions in the corpus. Both deserve a pre-registration.
* **The `Block_1` against `Block_6` contrast needs a quantity that is not spatial scale**, because
  on scale they coincide.

## 6. Limits

Two prompts, three seeds, one drawing style, and — per `retro_axes_atlas_result.md` §2 — coherence
is near-blind on flat styles, so all of §1 and §4 are claims about line-bearing work. The knee is
located only as "between 0.120 and 0.200"; the ladder has no point in between, and finding where it
actually sits needs renders, which is register item **C21**, now for a second reason.
