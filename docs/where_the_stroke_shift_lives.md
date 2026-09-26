# The stroke shift is not in the CLIP — and one row of yesterday's table was not a measurement

**Date**: 2026-09-26 · **Material**: `benchmark_atlas_phase1` (648 renders) and
`benchmark_qkvo_atlas` (433), both already on disk. **No new renders.**
**Status**: exploratory. Nothing here is pre-registered and nothing here changes the status of a
published claim.

---

## 1. A correction to my own wording

[`sign_decomposition_result.md`](sign_decomposition_result.md) §8 listed the traits that **never
reverse** between the two arms: `stroke_width_median_px` 0.00, `stroke_width_cv` 0.00, the colour
traits 0.14–0.16 — and summarised it as *"the sign does not govern colour or stroke width"*.

That sentence is easy to read as *"stroke width does not move"*. **It does not say that, and stroke
width does move.** An opposition rate of 0 means the trait moves **the same way whichever sign you
push** — it lives entirely in the common mode of §3, the 45 % + 23 % that carries no directional
information. A stroke-width shift observed in an earlier experiment is therefore **fully compatible**
with that row; it is not an anomaly needing a second mechanism.

## 2. But that row should not have been printed at all

`stroke_width_median_px` is **quantised**:

| corpus | images | distinct values of `stroke_width_median_px` |
|---|--:|---|
| `benchmark_qkvo_atlas` | 433 | **5** — 2.8, 4.0, 4.39, 5.6, 6.0 |
| `benchmark_atlas_phase1` | 648 | **10** — 2.0 … 8.4 |

An opposition rate computed on a five-step staircase is not a measurement of sign behaviour; it
measures how often two arms land on the same step. `stroke_width_cv` and `stroke_width_std_px` are
continuous (408 distinct values each) and are not affected, but their rate rested on 19 and fewer
above-noise pairs.

The audit of 2026-09-23 had already recorded this exact defect —
`audit_rotations_clean_v2_2026-09-23.md` line 108: *«`stroke_width_median_px` assume tre valori
(2.0, 2.8, 4.0): le medie «3.000» e le A di ±0.5 px sono salti di quantizzazione.»* It was in the
repository and I did not check it before printing a rate on that trait.

**The `stroke_width_median_px` row of §8 is withdrawn.** The rest of that table stands.

## 3. What the published claim actually says

`cliplult-is-a-dead-arm` (notebook page 00, status `holds`) reads:

> One of the text-encoder arms is exactly inert: it changes nothing at any dose, while **a sibling
> arm in the same run changes the image at every dose**.

It is a claim about **one arm**, not about the text encoder. The loose reading "the CLIP is dead" is
not what is published, and `observer_predictions_atlas_phase1.md` §5 drifted toward it in the
analyst's sealed prediction H, which reasoned that *"the CLIP half of every preset in this project
is close to inert"*.

## 4. The atlas settles it: the CLIP arm is not inert, and prediction H is falsified

`clip_only` patches 629 CLIP tensors and zero model tensors; `model_only` the reverse. Both anchored
at the same **absolute** displacement D = 273.026.

| preset | RMS difference from same-seed baseline (0–255) | correlation with baseline |
|---|--:|--:|
| `clip_only_draw1` | **51.13** | +0.629 |
| `clip_only_draw2` | **53.10** | +0.597 |
| `model_only_draw1` | 47.98 | +0.686 |
| `modulation_norm_draw1` | **0.0000** | — (the known dead arm) |

Decorrelation ceiling measured in this corpus (baseline vs baseline, different seed): **0.345**.
Neither arm reaches it, so neither has simply made a different picture.

**Prediction H is falsified.** The CLIP half is not close to inert; in pixels it moves the image at
least as much as the whole model does.

## 5. And yet the answer to the question is still no

On the 23 extracted traits, in units of each trait's seed-to-seed noise, **`clip_only` moves less
than `model_only` on all 23 of 23**:

| trait | `clip_only` | `model_only` | `early_attn` |
|---|--:|--:|--:|
| `stroke_width_median_px` | **0.89** | 2.65 | 2.63 |
| `stroke_width_std_px` | **1.32** | 3.80 | **6.68** |
| `stroke_width_cv` | **1.02** | 2.20 | 1.77 |
| `edge_density` | 1.29 | 3.19 | 3.83 |
| `contour_n_components` | 1.19 | 4.84 | 3.23 |
| `fft_high_freq_share` | 1.19 | **6.67** | — |

`clip_only` sits at **0.84–1.64×** the seed noise on every trait — that is, at or barely above the
floor. `model_only` runs 1.57–6.67×.

**The stroke shift does not come from the CLIP.** It comes from the DiT, and — by §1 — it lives in
the sign-blind part of the DiT's effect, which is why it never reverses.

The confound runs the right way: the atlas anchors D in **absolute** Frobenius, so CLIP receives
273.03/2156.89 = **0.1266** of its own norm against the model's 273.03/4968.28 = **0.0550** — a
factor 2.3 **more** relative perturbation. `clip_only` does less to style despite a 2.3× larger
relative dose.

## 6. The hypothesis this raises, not tested here

`clip_only` is as far from the baseline as `model_only` **in pixels** (corr 0.629 vs 0.686) and
uniformly closer **in style traits** (23/23). The natural reading is that perturbing the text
encoder changes **what is drawn** while perturbing the DiT changes **how it is drawn**.

This is generated by the numbers above and is therefore post-hoc. It would be tested by a statistic
that separates composition from rendering — subject position, scale and layout against texture and
palette — pre-registered before it is computed, on the renders already on disk. It is **not** a
result and is not claimed as one.

## 7. What a reader should take from this

* Nothing changes the status of `cliplult-is-a-dead-arm`, which remains true as written.
* One row of `sign_decomposition_result.md` §8 is withdrawn for a defect already in the repository.
* The sealed analyst prediction H in `observer_predictions_atlas_phase1.md` §5 is falsified and
  should be scored as such when the observer names his pair.
