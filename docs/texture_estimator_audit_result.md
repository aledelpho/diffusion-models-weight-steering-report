# B1 — the grain statistic audited three ways: one conclusion survives, one reverses

**Date**: 2026-09-27 · **Material**: `benchmark_mappa`, 432 conditions + 6 baselines, already on
disk. **No render.** **Data**: `data/texture_estimator_audit.csv`.
**Trigger**: pitfall candidate 75 — a texture statistic summed over the whole frame reports the sum
of *grain added* and *contrast changed*.

---

## 0. Two corrections to yesterday's own numbers, first

**The flat-region estimator had a mask-alignment bug, twice.** The 9×9 local-variance map is offset
from the Laplacian map by **3 pixels**, and both earlier versions got the offset wrong — one
cropped the mask, the other took the top-left corner. The figures reported in
`looking_at_block1_and_block6.md` §3 (`Block_6` grain **1.322** / **0.728**) came from a misaligned
mask and are **withdrawn**.

**And with the alignment fixed, the flat-region estimator is useless as specified.** The flattest
40 % of a baseline has near-zero high-frequency energy *by construction*, so every perturbation
scores 7–19× and **0 of 6** blocks fall below 1. It cannot discriminate; it only says "something was
added to the smooth areas", which is always true. It is reported below for completeness and argued
from only as an ordering, never as a ratio.

The usable correction is the other one: **contrast normalisation**, `r_cnorm = [HF(x)/var(x)] /
[HF(base)/var(base)]`, which asks how much grain there is *per unit of contrast*.

## 1. The conclusion that survives

Punto 7's common mode `c = √(r⁺·r⁻)` — *"any perturbation, in any direction, removes fine
texture"* — and its correlation with depth:

| estimator | mean common mode | blocks below 1 | r(depth) |
|---|--:|--:|--:|
| `r_global` — what the project has used | **0.9691** | 5/6 | **−0.716** |
| `r_cnorm` — contrast-normalised | **0.9737** | 5/6 | **−0.779** |
| `r_flat` — flat regions (saturated, see §0) | 9.26 | 0/6 | −0.832 |

**`cost-grows-with-depth` is not an artefact of contrast.** The corrected estimator gives the same
mean to within 0.005 and a *stronger* depth correlation. Punto 7's headline (0.978 on 28 blocks)
reproduces here at 0.969 / 0.974 on six groups of a different corpus.

That is the answer to B1 as asked, and it is reassuring.

## 2. The conclusion that reverses, and it is a published claim

Between the two interpretable estimators, **3 of 12 cells at dose 0.200 disagree on the sign** — and
they are not scattered:

| block | sign | `r_global` | `r_cnorm` | |
|---|---|--:|--:|---|
| **`Block_1`** | **pos** | **0.860** | **1.091** | reverses |
| **`Block_1`** | **neg** | **1.038** | **0.950** | reverses |
| `Block_2` … `Block_5` | both | — | — | agree, 8/8 |
| **`Block_6`** | **pos** | **0.926** | **1.089** | reverses |
| `Block_6` | neg | 0.861 | 0.782 | agree |

`first-block-is-an-inverted-knob` (page 00… page 05, status **`holds`**) reads: *"The first block is
a knob that runs the opposite way to the tail: pushed positive it smooths, pushed negative it
etches."*

On this corpus, **per unit of contrast it does the opposite**: pushed positive it etches (1.091),
pushed negative it smooths (0.950).

The arithmetic is direct. `Block_1 pos` at 0.200 drops high-frequency energy to **0.860** — but it
drops the image's variance to **0.789** (contrast 0.888, squared). Less grain in absolute terms,
**more** grain relative to how much contrast is left. The published claim measures the first
quantity and states it as a fact about texture.

### What this does and does not license

* It does **not** overturn the claim. The claim was built on `benchmark_profondita`, 28 single
  blocks at ±0.200, and that corpus is **not currently reachable** — this is a different bench, six
  macro-groups, a different dose ladder.
* It does establish that **the claim's estimator is confounded with contrast, and that on the one
  corpus where the correction can be run, the correction reverses it.**
* The claim's status is Alessandro's decision. What the analyst records is that the test is now
  specified and cheap: connect `benchmark_profondita`, run `experiments/texture_estimator_audit.py`
  against it, compare `r_global` with `r_cnorm` for `blk00`. **Zero renders.**

## 3. Restating pitfall candidate 75

The mechanism holds; yesterday's example and number do not.

> **75** — *A texture statistic summed over the whole frame is confounded with contrast: a condition
> that flattens the image reports less texture even when it adds grain per unit of contrast. Divide
> by the image's own variance. Restricting to "flat regions" is **not** the fix — the flattest
> region of a baseline has near-zero texture by construction, so every condition scores an enormous
> ratio and nothing discriminates.*

The second sentence is the part worth keeping, because it is the fix the analyst reached for first
and it was wrong.

## 4. What else the table says

`Block_3` remains the cleanest bidirectional knob under **both** interpretable estimators —
pos 1.165 / 1.124, neg 0.886 / 0.905 — and no document in the project names it.

`Block_5 pos` is the strongest single smoother measured: 0.656 global, 0.584 contrast-normalised,
agreeing.
