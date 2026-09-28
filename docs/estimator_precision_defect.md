# Two numerical defects in the estimators added on 2026-09-28, and what they moved

**Date**: 2026-09-28 · **Found by**: the cross-check Alessandro's question forced —
*"did you add the two axes to this calculation?"* · **Script**:
`experiments/retro_axes_crosscheck.py` · **No render.**

---

## 1. How they surfaced

`data/retro_texture_axes.csv` re-measures all 3 735 renders with `scipy.ndimage` filters, chosen
for speed. The documents of the same day used hand-rolled filters. Before reading one against the
other, the two were compared on the corpus where both exist: **they disagreed by up to 0.024 on
coherence and 0.056 on band-2**, enough for `B6_mask pos` to cross 1.0 between versions.

Neither version is a rounding of the other. Both hand-rolled filters were wrong, in two unrelated
ways.

## 2. Defect A — a summed-area table in float32

`experiments/texture_anisotropy.py` and `experiments/measure_blk16_ladder.py` computed the 9 × 9
window mean of the structure tensor as a summed-area table: a cumulative sum over 1.3 million
values of order 1e-4, then differenced. In float32 that is catastrophic cancellation.

Against the true window mean of one 9 × 9 patch:

| | value | relative error |
|---|--:|--:|
| true mean | 1.9465448e-04 | — |
| cumsum, float32 | 1.9290124e-04 | **9.0e-03** |
| cumsum, float64 | 1.9465448e-04 | 7.6e-12 |
| `uniform_filter` | 1.9465448e-04 | 7.6e-12 |

**0.9 % per window, 2.5 % on the aggregate coherence** of one render — 0.6235 reported against
0.6078 true. The fix is one line: a proper separable uniform filter.

## 3. Defect B — a convolution that zero-pads

`experiments/damage_spatial_bands.py` and `experiments/mask_damage_taxonomy.py` built the Gaussian
pyramid with `np.convolve(..., mode="same")`, which pads with zeros. At the frame edge that
invents a step from the image to nothing, and the band decomposition reports it as detail.

**On a constant image, whose true band energy is exactly 0, it reports 4.0e-4** — about a quarter
of a real render's band-0 energy. Away from an 8-pixel frame the two conventions agree to 0.000 %,
so the whole error is border. On a real render it inflates band-0 energy by **3.5 %**.

## 4. What moved, and what did not

Everything below is recomputed; the corrected values are in the documents themselves.

**Unchanged.**

* The bottom of the coherence ranking, which is what the retraction of `style_damage_frontier.md`
  rests on. Ranks 75 to 80 are the same six conditions in the same order: `blk27 neg`,
  `Block_6 neg`, `B6_anti neg`, `B4B6_anti neg`, `B6_mask neg`, `B4B6_mask neg`. **The five
  conditions this project recommended on 2026-09-27 are still the five worst in the corpus.**
* The whole of `mask_damage_taxonomy_result.md`: the peak at 4–8 px, the mask above its anti-mask
  in 12 of 12 cells (p = 0.0005), the monotone-against-notch distinction, and the combined
  condition sitting closer to `Block_6` (3.4× to 9.9×, was 3.8× to 11.5×).
* `K1`, `K2` and `K3` on the `blk16` ladder, and `K2`'s monotonicity exactly.
* Everything computed from `retro_texture_axes.csv`, including the atlas re-reading and the answer
  to `C20` — that file was correct from the start.

**Changed, and corrected in place.**

* **The top of the coherence ranking.** `B4_mask pos` was published as **1st of 80** and is
  **12th**; `blk16 pos` was 3rd and is 15th. The claim that the condition an observer picked out
  by eye ranked first is **withdrawn**: it ranks twelfth, still above the median and still far
  above everything this project had recommended, which is a weaker statement and the true one.
* 26 of 80 conditions move more than five places. **The middle of that ranking was never
  reliable** and should not be quoted at single-rank resolution.
* `Block_4` against `Block_6` on composition: 0.0189 against 0.0532, **2.81×, p = 0.093** — was
  4.29× and p = 0.065. Still not significant, and now weaker.
* Family coherence means: `Block_4` 0.9911 (7 of 16 above 1), `Block_6` 0.9234 (5 of 14).
* `blk16 pos` at dose 0.200: coherence **1.0146**, not 1.040, and **4 of 6 cells above 1**, not
  6 of 6. `K3`'s frozen band was computed with the broken estimator; recomputed on both sides it
  is **1.0146 against 1.0146**, so the across-bench determinism claim is better supported than
  before, not worse.

## 5. The rule this earns

**An estimator added to this project is cross-checked against an independent implementation before
anything is published from it.** Both defects were found in under an hour once two implementations
existed; neither was visible from one. The guard is now a script
(`experiments/retro_axes_crosscheck.py`) that exits non-zero when the two disagree, and it should
be run whenever either side changes.

Drafted defects **84** (a summed-area table in float32) and **85** (a convolution that zero-pads
at the frame edge, on a statistic that reads the frame edge as content), in
`docs/open_work_register.md` §E.

**And the uncomfortable part.** Both defective estimators were written on the same day as the
documents that used them, to answer a criticism about trusting numbers that had never been checked
against a picture. They were then used to overturn three published readings. Two of those three
survive unchanged; one had its headline number wrong by eleven ranks. The lesson is not that the
new axes were wrong — it is that **a new instrument is at its least trustworthy exactly when it is
producing its most interesting result.**
