# Two thirds of what a weight edit does to the image does not depend on which way you push it

**Date**: 2026-09-26 · **Material**: 432 + 192 renders already on disk
(`benchmark_mappa`, `benchmark_qkvo_atlas`). **No new renders were generated or requested.**
**Pre-registration**: [`prereg_sign_decomposition_pixels.md`](prereg_sign_decomposition_pixels.md)
(commit `0fb062e`) and its Amendment 01 (`9bf01f0`), both deposited before the corresponding
statistic was computed. **Observer prediction**:
[`observer_prediction_sign_opposition.md`](observer_prediction_sign_opposition.md) (`4706b78`).

**Seven analyst predictions: 1 confirmed, 4 falsified, 2 grey. The observer prediction was
confirmed and is argued here to be uninformative.**

---

## 0. In one sentence

Pushing a block of weights forward and pushing it backward do **not** produce opposite images: about
two thirds of the pixel change is identical whichever way you push, and that two thirds is grain,
while the third that the sign actually governs is structure.

## 1. The measurement

For a matched pair at `+d` and `-d` on the same block, prompt and seed, against the same-seed
baseline (determinism on this bench is on record in `data/bench_checks.csv`, max channel
difference 0):

```
c = (Dplus + Dminus)/2    the common mode -- what happens whatever the sign
m = (Dplus - Dminus)/2    the signed mode -- what reverses with the sign
F = |c|^2 / (|c|^2 + |m|^2)
```

`F = 0` is a linear knob. `F = 1` is a block that breaks the same way in both directions. The
project had asked this question once, in [`punto7_attrito_e_rettificazione.md`](punto7_attrito_e_rettificazione.md),
on a different corpus, at one dose, and with a ratio between two scalars. This is the directional
version, and the dose is swept.

## 2. The main prediction fell

Predicted: at the smallest dose the response is essentially first-order, so `F < 0.25`.
A first-order response *must* be mirrored — `I(W+δ) ≈ I(W) + Jδ` gives `cos(Dplus,Dminus) = -1`.

| block | 0.020 | 0.035 | 0.050 | 0.080 | 0.120 | 0.200 | mean |
|---|--:|--:|--:|--:|--:|--:|--:|
| `Block_1` | 0.704 | 0.699 | 0.685 | 0.692 | 0.697 | 0.696 | 0.696 |
| `Block_2` | 0.674 | 0.687 | 0.693 | 0.704 | 0.702 | 0.719 | 0.696 |
| `Block_3` | 0.672 | 0.675 | 0.678 | 0.689 | 0.689 | 0.696 | 0.683 |
| `Block_4` | 0.661 | 0.664 | 0.669 | 0.689 | 0.696 | 0.705 | 0.680 |
| `Block_5` | 0.657 | 0.654 | 0.661 | 0.672 | 0.679 | 0.704 | 0.671 |
| `Block_6` | 0.670 | 0.665 | 0.654 | 0.654 | 0.643 | **0.617** | **0.650** |
| **mean** | **0.673** | 0.674 | 0.673 | 0.683 | 0.684 | 0.690 | |

**Observed 0.673 at dose 0.020, predicted below 0.25.** P1 falsified. P3 (`F < 0.30` at 0.050)
falsified at 0.673. Over a **ten-fold** range of dose `F` moves by 0.017. There is no dose in this
range at which these block groups behave like knobs, and the smallest dose is not closer to
linearity than the largest.

Both prompts agree (`P01` 0.665 → 0.677, `P02` 0.680 → 0.702), and no cell of the 216 falls below
0.568.

## 3. Where the energy actually goes

The pairwise cosines did not close: the cosine between **different** blocks pushed the same way
(+0.411) was *higher* than the cosine between the **same** block pushed both ways (+0.348), which a
two-term model forbids. Decomposing the vectors directly (36 cells, declared **post-hoc**):

| component | share of the energy |
|---|--:|
| **global mode** — identical for every block *and* every sign | **45.2 %** |
| **block mode** — says which block was touched, not which way | **22.8 %** |
| **signed mode** — the only part the sign governs | **32.0 %** |

Read as an instrument specification: of everything a block edit does to the image, **45 % is not a
function of what you asked for at all**, 23 % tells you only that you touched *that* block, and
**32 % is the part you are steering**.

## 4. What the sign-blind part is made of — P7 confirmed

High-frequency share (fixed 3×3 Laplacian), dose 0.200:

| block | HF(`c`) | HF(`m`) | ratio |
|---|--:|--:|--:|
| `Block_1` | 0.839 | 0.640 | 1.31 |
| `Block_2` | 0.771 | 0.661 | 1.17 |
| `Block_3` | 0.722 | 0.564 | 1.28 |
| `Block_4` | 0.767 | 0.562 | 1.37 |
| `Block_5` | 0.851 | 0.613 | 1.39 |
| `Block_6` | **1.107** | 0.609 | **1.82** |

**6 / 6 blocks, 35 / 36 cells.** The sign-blind part is the high-frequency part; the part the sign
governs is structural. This is the VAE story of Punto 7 §1 — the decoder passes the loss of detail
and absorbs the addition — measured directly on pixels instead of inferred from a ratio.

## 5. What fell, and why some of it is my fault

* **P4 falsified, and partly mis-built.** Predicted `Block_6` would be the *most* rectified,
  following Punto 7 §3. It ranks **6th of 6** — the most linear group — and it is the only group
  whose linearity *increases* with dose (Spearman ρ = **−1.000**, 0.670 → 0.617). But Punto 7 §3
  measured an asymmetry of **amplitude** (`+0.200` violent, `−0.200` quiet); `F` measures
  **direction**. I mapped one onto the other in the pre-registration. The falsification is real as a
  result about `F`; it is **not** a contradiction of Punto 7, and the pre-registration was wrong to
  imply the two are the same quantity.
* **P6 falsified.** Predicted the same-block cosine would sit at least 0.30 below the different-block
  cosine. Observed gap **+0.064**. Antisymmetry is barely a same-block property at all — the global
  mode dominates everything.
* **P2 grey** (pooled ρ = +0.214 against a +0.50 bar), **P5 grey** (4/6 groups).

## 6. The same measurement on q/k/v/o — the split holds, by a fourth statistic

Amendment 01 froze: `F` higher for `wq`/`wk` than for `wv`/`wo`, gap > 0.15.

| cell | `F` | cos(+,−) | ‖D‖ | HF(`c`) | HF(`m`) |
|---|--:|--:|--:|--:|--:|
| `wq_b1` | 0.754 | +0.513 | 167.6 | 1.349 | 1.378 |
| `wk_b1` | 0.751 | +0.506 | 175.4 | 1.391 | 1.477 |
| `wq_b6` | 0.741 | +0.485 | 151.3 | 1.655 | 1.594 |
| `wk_b6` | 0.746 | +0.501 | 152.2 | 1.536 | 1.564 |
| `wv_b1` | 0.668 | +0.340 | 333.3 | 0.612 | 0.443 |
| `wo_b1` | 0.667 | +0.338 | 331.7 | 0.619 | 0.446 |
| `wv_b6` | **0.627** | +0.257 | 205.1 | 1.289 | 0.920 |
| `wo_b6` | **0.628** | +0.258 | 203.7 | 1.321 | 0.927 |

**Gap = +0.100 — grey against the frozen 0.15 bar.** But the ordering is **complete**: the lowest
q/k cell (0.741) is above the highest v/o cell (0.668), and the gap is positive in **8 / 8 scenes**
(exact sign-test floor 2/2⁸ = 0.0078) and 23 / 24 scene × seed units.

This is now the **fourth** statistic giving the same ordering, on two representations: the
feature-space cosines of `qkvo_analyze.py`, the trait-opposition rates below, the pixel `F` here,
and the pixel cos(+,−).

And §4's frequency story **splits by family**, which resolves the tension between the two corpora:
for `wv`/`wo` the signed mode is clearly lower-frequency than the common mode (0.44 vs 0.61,
0.92 vs 1.29 — the same pattern as the block groups), while for `wq`/`wk` the two are
**indistinguishable** (1.35 vs 1.38, 1.66 vs 1.59). On the routing path there is no structural
component to separate: everything it does is grain.

**A1-P2 failed**: `F` below 0.673 in only **4 / 8** cells (bar was ≥ 6). The reasoning — that a
single projection injects less broadband noise than ten tensor types — was wrong for `wq`/`wk`,
which are *more* sign-blind than a whole block group, not less.

## 7. A confound found in the q/k/v/o bench, and a retraction

**The eight q/k/v/o cells are not Frobenius-matched.** Their model displacements run from
**23.50** (`wk_b6`) to **65.06** (`wo_b1`), a spread of **2.77×**. The runbook did not require
matching and the analyst did not check it before reporting.

* **`F` survives it.** `r(Δw, F) = −0.31` across the eight cells, and the dose calibration measured
  in §2 — `F` moves +0.017 over a **ten-fold** dose range — bounds the effect of a 2.77× spread at
  about **+0.007**, against an observed gap of **+0.100**. Fourteen times the confound.
* **Anything comparing magnitudes across cells does not survive it.** The "distinctiveness within
  band" figures reported on 2026-09-26 (`b1: wv 5.49 > wq 5.43 > wk 5.28 > wo 5.25`;
  `b6: wv 7.58 > wk 7.44 > wq 7.42 > wo 7.24`) are **withdrawn**: they compare distances at unequal
  dose. `wo_b1` was given 1.85× the weight displacement of `wv_b1` and still moved less, so the
  qualitative reading survives, but the numbers as printed do not.
* Likewise the steerable energy: raw, `v/o` carries **1.95×** the signed norm of `q/k`; divided by
  weight displacement the ratio falls to **1.48×** and the separation is no longer complete
  (`wk_b6` 3.26 > `wo_b1` 2.94). **The honest statement is ~1.5× with overlap, not 2×.**

## 8. The trait-opposition test

Alessandro's prediction, recorded verbatim before computing: more than 80 % of presets show at least
one extracted trait moving in the opposite direction between the two arms. **Observed 99.5 %
(191/192) — confirmed, and uninformative**, exactly as the objection deposited with it stated: with
23 traits the chance of no opposition anywhere is 2⁻²³.

The informative version — the share of **above-noise** traits that oppose, against a chance level of
0.50 — separates the two families cleanly:

| cell | opposed share | traits above noise, per pair |
|---|--:|--:|
| `wq_b6` | **0.067** | 1.9 / 23 |
| `wk_b6` | 0.085 | 2.0 / 23 |
| `wk_b1` | 0.091 | 1.4 / 23 |
| `wq_b1` | 0.120 | 1.0 / 23 |
| `wo_b1` | 0.538 | 4.4 / 23 |
| `wv_b1` | 0.541 | 3.5 / 23 |
| `wo_b6` | 0.690 | 5.9 / 23 |
| `wv_b6` | **0.758** | 5.3 / 23 |

Pooled it is 0.509 — indistinguishable from chance, and the analyst's frozen expectation of "below
0.5" is **not** confirmed. The pooled number is the average of two opposite populations and means
nothing.

Which traits reverse, pooled over all cells: `fft_radial_slope` 1.00, `lbp_uniform_share` 0.98,
`lbp_entropy` 0.97, `glcm_contrast` 0.92, `edge_density` 0.89 — **texture and frequency**. Which
never reverse: `stroke_width_median_px` 0.00, `stroke_width_cv` 0.00,
`shadow_edge_transition_width_std` 0.07, and the four colour traits 0.14–0.16 — **stroke geometry
and colour**. The sign governs grain; it does not govern colour or stroke width, which move the same
way whatever you do.

## 9. Looking at the images

Descriptive, not a result. On `S1_photo` seed 42, the pair that the numbers separate most:

* **`wq_b6` (routing)**: the `+` and `−` renders are **almost the same image as each other**, and
  both differ from the baseline in the same way. The `c` and `m` maps trace the same edges.
* **`wv_b6` (value)**: the two renders differ visibly and the subject is re-drawn — the car changes
  size and lateral position. The common mode enlarges the subject; the signed mode slides it.

This is what `F = 0.74` versus `F = 0.63` looks like at 1× gain, and it is the first time in this
project that a positive and a negative arm have been compared as images rather than as descriptors.

## 10. What this means for the tuner

1. **There is no small-dose linear regime to retreat into.** Halving the dose does not buy back
   proportionality; it buys a smaller version of the same two-thirds-wasted move.
2. **Three quarters of a block-group edit carries no directional information** (45 % global +
   23 % block identity). A tuner that reports Frobenius displacement is reporting mostly the part of
   the move that does not steer.
3. **The value path is where the control is.** `wv`/`wo` deliver about 1.5× the signed motion per
   unit of weight displacement, and 3–6 traits above noise per pair against 1–2 for `wq`/`wk`.
4. **`q`/`k` are close to unusable as signed controls** — opposition 0.07–0.12, and no structural
   component at all. If the tuner exposes them as signed sliders, the sign is close to decorative.

## 11. Limits

* Two prompts on `benchmark_mappa` (unit of analysis, pitfall 17); no prompt-level p-value is
  claimed there, only 6/6 cell unanimity. Eight scenes on the q/k/v/o bench, where the sign test has
  a floor of 0.0078.
* Everything is measured in **pixels**, i.e. in the band the VAE passes. Punto 7 §6's warning
  applies unchanged.
* `A01` and the `Projection` / `Text_Fusion` / `Time_Embed` slots were left out of the primary
  design and are not analysed here.
* **Nothing in this document changes the status of a published claim.** Punto 7 §3 and §5 are in
  contact with §5 above; the decision is not the analyst's.
