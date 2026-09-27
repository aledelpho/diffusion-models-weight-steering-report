# Pre-registration — does the edit's signature survive an augmented image?

**Deposited**: 2026-09-27, **before any augmented image was generated or any statistic computed.**
**Material**: the 519 renders of `benchmark_mappa`, already on disk. **No render is generated** —
augmentation is image processing applied to copies, never a new sample from the model.
**Builds on**: [`transfer_test_result.md`](transfer_test_result.md), where the un-augmented transfer
scored **0.7083** against a same-prompt ceiling of **0.8299**, exact permutation p = 0.026.

---

## 1. The claim being tested, and whose it is

Alessandro's, stated on 2026-09-27: that a preset's signature is recognisable *"anche dopo che sono
state mescolate, girate, ricolorate e con aggiunta di Noise"*.

The repository supports a narrower version of it. `blinding-is-a-measurement-and-it-failed` records
a 4-way forced choice on hashed filenames — 17/20 and 12/20, **12/20 jointly against an 8.3 % chance
level** — but those were conditions whose **weights** had been shuffled, rotated and sign-scrambled.
**No study in this project has ever augmented the images and asked whether the signature survives.**
This is that study, in the quantitative form the transfer test gives it.

## 2. Design

Augment the **candidate side only**. The reference stays untouched, so the question is: *given a
clean reference, can the treatment still be identified when the candidates have been interfered
with?*

```
reference = (b, d, s) on P01, seed σ, untouched, centred on P01's untouched baseline mean
target    = AUG[(b, d, s) on P02, seed σ],  centred on AUG[P02 baselines] mean
foil      = AUG[(b', d, s) on P02, seed σ], b' matched in ||D||, same centring
hit  iff  cos(reference, target) > cos(reference, foil)
```

Two details that decide whether the measurement means anything:

* **The baselines are augmented too**, and the candidate side is re-centred on *those*. Otherwise the
  augmentation appears as a constant offset shared by target and foil and the test measures the
  augmentation instead of the signature.
* **One fixed metric.** The per-trait scale is the one already used in `transfer_test_mappa.py`,
  taken from the nine **untouched** baselines (pitfall 33). Re-deriving a scale per augmentation
  would make each condition a different metric and the conditions incomparable.

### The six augmentations, and what each is meant to destroy

| id | operation | destroys | preserves |
|---|---|---|---|
| `hflip` | horizontal mirror | chirality only | essentially everything |
| `rot90` | rotate 90° | orientation-dependent traits | colour, histogram, most texture |
| `hue` | hue rotation +60° | the 4 colour traits | texture, geometry |
| `desat` | 50 % saturation | colourfulness | structure |
| `noise` | Gaussian σ = 8 | high-frequency traits | colour, composition |
| `jpeg` | JPEG quality 40 | fine texture, differently | colour, composition |

Plus `identity`, a pipeline control that must reproduce **0.7083**.

Doses **0.050** and **0.200**, the two the parent pre-registration named. 72 items per condition,
7 conditions, **504 decisions**, from 525 augmented copies. Chance is **0.50** by construction.

## 3. Predictions, frozen before any augmented image exists

| # | prediction | confirmed if | falsified if |
|---|---|---|---|
| **A1** | the signature survives every augmentation | all six conditions pooled **> 0.50**, and at least **four of six > 0.60** | two or more conditions at or below **0.50** |
| **A2** | the destroyers of fine texture hurt most | `noise` and `jpeg` occupy the **bottom two** of the six ranks | either is in the **top two** |
| **A3** | **crossover**: which traits carry the signature depends on what was destroyed | under `hue`, colour-only transfer falls **below** texture-only; under `noise`, texture-only falls **below** colour-only — **both** directions | either crossover runs the other way |
| **A4** | `Block_6` is the robust one | `Block_6` scores **≥ 0.80** in at least **five of six** conditions | below 0.60 in three or more |

**A3 is the prediction worth having.** A main effect — "augmentation hurts" — is nearly free. A
crossover requires the signature to be carried by *different* traits depending on the attack, and
it is the version of the claim that could actually be wrong.

Trait subsets, fixed now: **colour** = the four `color_*` / `colorfulness_hs`; **texture** = the four
`glcm_*`, the two `lbp_*`, the two `fft_*`; **stroke** = the three `stroke_width_*`, `edge_density`,
the two `contour_*`, the two `crosshatch_*`; **tone** = `luminance_hist_n_peaks` and the two
`shadow_edge_transition_*`. `stroke_width_median_px` is quantised to a handful of values
(`where_the_stroke_shift_lives.md` §2) and is reported but never argued from.

## 4. Inference

The exact permutation over all **720** relabellings of the six P02 blocks is the null for every
condition, as in the parent study, because the naive binomial overstates by treating items that
reuse three seeds as independent. Both are printed; the permutation is the one quoted.

## 5. What this may not do

* It may not change the status of a published claim.
* It generates no render.
* A positive result says the signature survives **these six operations as measured by these 23
  traits**. It does not say a human would still recognise it, which is a different experiment and
  one this project's judge has just been shown unable to run.
