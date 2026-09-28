# The observer's four categories, and the quantity nobody was measuring

**Date**: 2026-09-28 · **Origin**: Alessandro, given the 36-panel sheet of the rectified masks
with no labels, described it in five lines · **Material**: `benchmark_rectified_masks`, already on
disk · **Script**: `experiments/mask_damage_taxonomy.py` → `data/mask_damage_taxonomy.csv` ·
**No render.**

---

## 1. What he said

> rows 1–2 (`B4_mask`, `B4_anti`) — almost no visible grain or blur
> row 3 (`B6_mask`) — alternating **very strong grain** / **soft grain**
> row 4 (`B6_anti`) — alternating **weaker grain** / **loose blur**
> row 5 (`B4B6_mask`) — same as row 3
> row 6 (`B4B6_anti`) — same as row 4

Columns alternate positive, negative. Two structural claims are buried in that, and neither is a
matter of taste:

* **A** — the combined conditions look like the `Block_6` ones, not like the `Block_4` ones.
* **B** — the *kind* of damage follows the arm sign, while mask-against-anti changes only how much.

## 2. Energy at each scale, which is what none of the existing statistics reported

Absolute band energy of the render divided by the same band of its untouched baseline. Above 1
means detail was **added** at that scale, below 1 means it was **removed**. Every statistic this
project had — grain, contrast, coherence, displacement — collapses the scales into one number
first.

| condition | arm | 1–2 px | 2–4 px | 4–8 px | 8–16 px | 16–32 px | |
|---|---|--:|--:|--:|--:|--:|---|
| `B4_mask` | pos | 1.029 | 1.074 | 1.105 | 1.165 | 1.187 | flat, near 1 |
| `B4_mask` | neg | 0.693 | 0.837 | 0.872 | 0.827 | 0.852 | flat, near 1 |
| `B4_anti` | pos | 0.889 | 0.896 | 0.918 | 0.968 | 1.035 | flat, near 1 |
| `B4_anti` | neg | 0.981 | 0.975 | 1.013 | 1.024 | 1.061 | flat, near 1 |
| **`B6_mask`** | **pos** | 0.985 | 1.486 | **2.013** | 1.472 | 0.920 | **added at 4–8 px** |
| **`B6_mask`** | **neg** | **0.393** | 0.456 | 0.584 | 0.705 | 0.800 | **monotone stripping** |
| `B6_anti` | pos | 1.292 | 1.483 | **1.562** | 1.372 | 1.201 | added at 4–8 px, weaker |
| `B6_anti` | neg | 0.789 | **0.455** | 0.515 | 0.742 | 0.975 | **a notch at 2–8 px** |
| **`B4B6_mask`** | **pos** | 1.108 | 1.665 | **2.217** | 1.599 | 1.012 | added at 4–8 px |
| **`B4B6_mask`** | **neg** | **0.363** | 0.408 | 0.515 | 0.598 | 0.662 | monotone stripping |
| `B4B6_anti` | pos | 1.206 | 1.386 | **1.410** | 1.231 | 1.126 | added at 4–8 px, weaker |
| `B4B6_anti` | neg | 0.845 | **0.445** | 0.497 | 0.701 | 0.959 | a notch at 2–8 px |

**His five lines are this table.**

* **Rows 1–2, "almost no artefacts":** the four `Block_4` profiles never leave 0.69–1.19 at any
  scale. They are the only conditions in the bench that do not restructure the surface.
* **"Very strong grain" against "weaker grain"** — both are energy added with its peak at
  **4–8 pixels**, and the mask is the stronger one: ×2.01 against ×1.56, and ×2.22 against ×1.41.
  Per cell, on the positive arm, the mask exceeds its anti-mask at 4–8 px in **12 of 12 cells**,
  exact sign test **p = 0.0005**.
* **"Soft grain" against "loose blur"** — both are energy removed, and the shape is what separates
  them. `B6_mask neg` and `B4B6_mask neg` strip **monotonically**, hardest at the finest scale
  (0.393 and 0.363) and progressively less as the scale grows. `B6_anti neg` and `B4B6_anti neg`
  cut a **notch**: the finest scale is largely kept (0.789, 0.845), 2–8 px is gutted (≈ 0.45), and
  16–32 px comes back to ≈ 0.97. Two different damages, and the observer had already given them
  two different names.

**The grain statistic got the first comparison backwards.** It reports `B6_anti pos` at 1.191 and
`B6_mask pos` at 1.092 — the anti-mask grainier than the mask, the opposite of both the eye and the
band-2 energy, in 12 of 12 cells. It is normalised by contrast and reports its own direction:
drafted defect 80 again, on a third statistic.

## 3. Claim A, and the instrument that got it wrong first

Distance between the combined condition and each single, in the space of the log band profile:

| | arm | to `Block_6` | to `Block_4` | |
|---|---|--:|--:|---|
| `B4B6_mask` | pos | **0.102** | 0.402 | 3.9× closer to `Block_6` |
| `B4B6_mask` | neg | **0.140** | 0.525 | 3.8× closer |
| `B4B6_anti` | pos | **0.084** | 0.326 | 3.9× closer |
| `B4B6_anti` | neg | **0.044** | 0.510 | 11.5× closer |

**Four of four, by factors of 3.8 to 11.5.** Adding `Block_4` to `Block_6` changes the surface
almost not at all — which is why row 5 is row 3 and row 6 is row 4.

The first version of this test measured distance on the 8× downsampled luminance — the layout — and
returned 1.09× and 0.91×, i.e. nothing. The claim was about how the surface looks, and layout is
the wrong space for it. **The measurement was not wrong; it was aimed at the wrong quantity**, which
is the same failure as reading texture through a statistic that has already summed over scale.

## 4. What this adds

* **A new quantity for the bench: the scale at which an edit changes the surface.** Every existing
  statistic sums over scale before reporting. The four categories an observer produced in five
  lines are four distinct band profiles, and they are invisible to all of them.
* **Two named damage modes**, with measurable signatures: *monotone stripping*, hardest at the
  finest scale, and *a mid-scale notch* that keeps the finest and coarsest detail. Both are
  `Block_6` negative; which one you get is set by the relative sign of the two sub-blocks.
* **`Block_6` dominates the combination on texture**, by 3.8× to 11.5×, while
  `rectified_mask_result.md` §4 could only say that composition predicted direction better for
  opposed than concordant signs at p = 0.077. This is the same structure, seen where it is large.
* The band-2 ordering (mask above anti, 12/12, p = 0.0005) is the first thing in the mask bench
  that separates mask from anti-mask cleanly on any statistic. **M5 asked whether the mask beats
  the anti-mask and could not be read because its arithmetic failed. On texture scale, it does.**
  That is not the pre-registered question and does not revive it; it is a new one, and it should be
  pre-registered before it is claimed.

## 5. Limits

Two prompts, three seeds, one dose, one drawing style. The band decomposition is a Gaussian
pyramid on luminance and ignores colour entirely. And the four categories were supplied by one
observer looking at one sheet before the measurement existed — which is what makes them worth
testing, and also means the analysis was aimed by them rather than chosen in advance.
