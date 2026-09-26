# Assessment of a proposed design: per-block dose calibration inside the sensitivity spectrum

**Date**: 2026-09-26 · **Proposal**: Alessandro · **Assessment**: analyst.
**Material**: existing data only (`data/sign_decomposition_cells.csv`, `data/sign_decomposition_qkvo_cells.csv`,
`benchmark_mappa`), plus two external papers. **No new renders.**
This is an assessment of a design, not a result. Nothing here changes a claim.

---

## 1. The proposal

> Different parts of the model have different sensitivity. Calibrate inside that spectrum: move
> `Block_26` and `Block_1` less, move `Block_12` up to six times more, define per-block maximum
> doses, then build presets that push **at that limit** but only in a handful of areas per block
> (e.g. two different sections per block), to see what happens inside the specific sensitivity
> curve with an instrument that makes the effect more visible.

The proposal has two halves. **The second half is right and the first half is aimed at a knob that
is already dead.**

## 2. The dose knob is nearly saturated

Fitting image motion against dose on the six macro-groups, over the full measured range
0.020 → 0.200:

| block | log–log slope of ‖D‖ vs dose |
|---|--:|
| `Block_1` | 0.160 |
| `Block_2` | 0.163 |
| `Block_3` | 0.199 |
| `Block_4` | 0.217 |
| `Block_5` | 0.197 |
| `Block_6` | 0.192 |

‖D‖ ∝ dose^0.19. **Six times the dose buys 6^0.19 = 1.39× the effect.** Over the whole ten-fold
sweep the image motion grows by about 1.5×. "Move `Block_12` six times more" is, in image terms,
worth 39 %.

## 3. And the sweep already sits past the top of the curve

Distance between two baselines of the same prompt at different seeds — the project's own yardstick
for *"this is a different picture"* (Punto 7 §7):

`P01` **398.9** · `P02` **563.3** (RMS 51 and 72 levels of 255).

Image motion as a percentage of that distance:

| block | 0.020 | 0.035 | 0.050 | 0.080 | 0.120 | 0.200 |
|---|--:|--:|--:|--:|--:|--:|
| `Block_1` | 60.6 % | 67.3 % | 71.6 % | 76.1 % | 81.7 % | 91.6 % |
| `Block_2` | 62.1 % | 72.1 % | 78.2 % | 82.1 % | 87.3 % | 95.2 % |
| `Block_3` | 62.3 % | 70.2 % | 76.1 % | 82.5 % | 90.7 % | **101.3 %** |
| `Block_4` | 57.5 % | 63.8 % | 69.3 % | 77.5 % | 85.5 % | 95.2 % |
| `Block_5` | 55.2 % | 61.6 % | 67.0 % | 73.6 % | 81.0 % | 89.2 % |
| `Block_6` | **50.1 %** | 57.0 % | 61.8 % | 66.6 % | 72.0 % | 83.4 % |

**At the smallest dose ever tested the image has already moved 50–62 % of the way to being a
different picture.** At the largest it is at 83–101 %. There is no maximum left to find: the
corpus has been past it throughout. **The limit worth defining is a minimum, not a maximum.**

## 4. The calibration itself is sound, cheap, and one analyst objection was wrong

* `‖m‖` against dose is a clean power law: R² = 0.924 … 0.998, worst residual 4.7 % in dose.
* The doses that equalise signed motion across the six groups span **0.039 … 0.089 — a factor 2.2**,
  not six.
* The analyst expected that equalising **total** motion would fail to equalise the **signed** part,
  because `F` differs by block. **Checked, and wrong**: equalising ‖D‖ delivers ‖m‖ within
  **0.98–1.07×** of target. `F` varies too little across these groups for the two normalisers to
  come apart. The naive version of the calibration is fine.
* It needs **zero renders**: the table can be fitted today from `data/sign_decomposition_cells.csv`.

So the calibration is easy. It is also, per §2 and §3, a calibration of a saturated variable.

## 5. Lowering the dose probably does not rescue it either

`F` against dose: slope **+0.018 per decade**. Extrapolating, `F = 0.60` would need dose
2.5 × 10⁻⁶ and `F = 0.50` would need 7 × 10⁻¹². The extrapolation is meaningless, and that is the
point: **`F` is not a function of dose.** It is flat because the sign-blindness is not a
large-perturbation artefact.

The direct check points the same way. The smallest perturbation measured anywhere in the project is
`wq_b6` at ‖D‖ = 151, **38 % of a seed change** — and it has the **highest** `F` of any cell
(0.741). Smaller did not mean more linear.

## 6. What the outside literature says about the premise

The proposal calibrates on **sensitivity** — how much the image moves. Two recent papers bear on
whether that is the right quantity.

* *Sensitivity, Causality, and Repair Dissociate* (arXiv 2608.03842) measures layer-wise
  representation divergence, activation patching and LoRA repair on a five-model panel and reports
  that the three maps are **systematically anti-correlated**: sensitivity vs causality
  **ρ = −0.72 to −0.88, p < 0.001**. *"Early layers show high divergence but low causal importance."*
  A dose schedule that equalises divergence is equalising the quantity that is anti-correlated with
  control.
* *Beyond Layer Importance in Layer-wise Sparsity* (arXiv 2606.15161) injects noise at a chosen
  depth at relative magnitude η and finds **early layers amplify** the perturbation while
  **middle and late layers absorb it and rotate the state back** toward the unperturbed one. That is
  a mechanism for the anti-correlation, and it matches `Block_6` being the most linear group here.
  Their working scale is **η = 10⁻²**, with **10⁻⁴** as the *small-perturbation control*.

## 7. The half of the proposal that is right

"Only a handful of areas per block, e.g. two different sections per block" is the right move, and it
is the one the measurements support — with one constraint. Arbitrary sub-block slices are not
meaningful units: the prior-work review (`prior_work_layer_specialisation.md`) found that features
are not axis-aligned with residual channels. **Functional** components are meaningful, and the
project now knows which ones carry control:

| | `wq` / `wk` (routing) | `wv` / `wo` (value) |
|---|--:|--:|
| sign-blind share `F` | 0.741 – 0.754 | 0.627 – 0.668 |
| traits that reverse with the sign | 0.067 – 0.120 | 0.538 – 0.758 |
| traits above noise per pair | 1.0 – 2.0 / 23 | 3.5 – 5.9 / 23 |

**Changing which component you touch moves `F` by 0.10–0.12. Changing the dose moves it by 0.018
per decade.** The component choice is worth about **six decades of dose** — a factor of a million.

## 8. Recommended shape

Sweep the **component**, not the dose. Hold dose fixed at one modest value, and enumerate the
components the tuner actually exposes — per pitfall candidate 71, the tool's own
`MODEL_SURGEON_MAP`, never the checkpoint hierarchy — crossed with depth. Primary outcome: signed
motion ‖m‖ per unit of weight displacement, and the share of the effect falling in the global mode.
Frobenius-match every cell, which the q/k/v/o bench did not do (23.50 … 65.06, 2.77×).

Two secondary items, cheap and worth carrying:

* the **downward** dose probe (below 0.020) as a control — our own data predicts it will show
  nothing, which is exactly why it is worth one small batch rather than a large one;
* `mod.lin` alone, to finish the dead-arm decomposition.

Sizing and launch are Alessandro's. No render is generated or requested here.
