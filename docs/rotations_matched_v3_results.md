# `rotations_matched_v3` — results

**Date**: 2026-09-23. **Corpus**: the ten style prompts S01–S10 on their original seeds
(42, 1337, 4242145), 9 conditions each, 270 renders, all 1024×1280, checkpoint recorded with its
sha256. `P01`/`P02` are in the bench but excluded from this analysis by the frozen script, because
they were added after the design was frozen.

**Script**: `experiments/analyze_rotations_matched_v3.py`, run **unmodified**,
sha256 `aec99c0481160e9ff2ea8605a7bc625371ed04bb941d9eca3483a50bcf505d5c`. It implements §1 of
`docs/prereg_rotations_block1_vs_block6.md` — the symmetrised leave-one-out same-block advantage
V(p) on the antisymmetric component A = mean over seeds of (f⁺ − f⁻)/2 — with an exact sign-flip
null over 10 prompts, floor 2/2¹⁰ = 0.001953, and Holm over four secondary spaces.

**Not committed by this session**: the device shell would not start, so no git command was run.

---

## 1. Primary finding: the null is not measurable

`scramble_B`, the sign scramble anchored on `Block_6`, **fails the pre-registered quality gate in
60 of its 60 renders**. Not most. All.

| condition | renders | gate failures | grad_ratio range | ΔL range |
| --- | ---: | ---: | --- | --- |
| `B1_pos` | 30 | 0 | 0.97 – 1.19 | −1.9 … +7.3 |
| `B1_neg` | 30 | 0 | — | — |
| `B6_pos` | 30 | 0 | 0.75 – 0.97 | −7.2 … +1.0 |
| `B6_neg` | 30 | **5** | 1.00 – 1.74 | −5.2 … +7.6 |
| `scrA_pos` / `scrA_neg` | 30 / 30 | 0 / 0 | 0.98 – 1.33 | −8.4 … +0.9 |
| **`scrB_pos`** | 30 | **30** | 0.85 – 1.42 | **−40.4 … −23.7** |
| **`scrB_neg`** | 30 | **30** | 0.68 – 0.97 | **+20.2 … +31.7** |

The failure is not noise and it is not marginal. It is a **systematic, antisymmetric luminance
pump**: the positive arm darkens every single render by 24 to 40 L units, the negative arm
lightens every single one by 20 to 32. The gradient ratio stays inside range throughout — the
images are not falling apart texturally, they are being driven off the luminance scale. Every
other arm in the bench sits inside ±8.

This is a property of the **site**, not of the dose. All four arms carry the same measured
displacement, D = 0.00709975–0.00710012, verified against the node. A sign scramble anchored on
`Block_1` is harmless; the same operation anchored on `Block_6` is not. That is a finding about
what the last block group does, and it is the first direct evidence of it.

**Consequence for the registered criterion.** §4 requires V > V_scr. V_scr is built from
`scramble_A` and `scramble_B`. Its `scramble_B` half is measured on images the pre-registration's
own gate rejects, unanimously. **The criterion is therefore not evaluable on this bench**, and
`confirmed = True` in `data/rotations_matched_v3_results.csv` must be read as *not evaluable*,
never as confirmed. Nothing here is a confirmatory result.

**Third occurrence.** The `Block_6`-anchored null has now failed three times: absent by design in
the triangle (pitfall 69, the borrowed floor), measured on HUD-contaminated pixels in the
published bench, and photometrically unusable here. The first two were bookkeeping. This one is
physical, and it says the control cannot be built this way at any dose the gate admits.

**Candidate pitfall 73.** *A null control that is photometrically degraded in a systematic,
antisymmetric way does not behave like noise — it behaves like a strong, highly coherent
direction, and it inflates the null it was meant to provide.* See §4 for where this shows.

---

## 2. The same-block advantage, on clean pixels

Reported as **descriptive**, because its criterion is not evaluable.

| space | V | prompts with V > 0 | p (exact sign-flip) | p Holm | V_scr | V − V_scr |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Texture (primary)** | **+1.142** | **10 / 10** | **0.001953** = the floor | — | +0.852 | +0.290 |
| Linework | +0.670 | 9 / 10 | 0.0137 | 0.0273 | −0.070 | +0.740 |
| Shadow | +1.746 | 10 / 10 | 0.001953 = the floor | 0.0078 | +0.086 | +1.660 |
| Palette | +0.595 | 9 / 10 | 0.0039 | 0.0117 | +0.647 | −0.053 |

**The advantage replicates.** On HUD-free renders, at a dose 6.3× lower, the primary-space
advantage is **+1.142 against the contaminated bench's +1.039**, both at the exact permutation
floor, both positive in 10 prompts of 10. Whatever the HUD did to the features, it did not
manufacture this.

**The excess over the null shrinks by 43%**: +0.290 here against +0.506 published — and the
comparison is not usable anyway, because the null on this bench rests on the degraded arm.

**Palette goes the other way**: V_scr exceeds V. §4 says why that is expected once the scramble is
a luminance pump.

---

## 3. What this corrects on the published page

Not applied. `notebook/08-block1-vs-block6.md` is untouched and still carries its contamination
banner. These are the numbers a decision would rest on.

**`blocks-separate-by-direction-not-distance` (holds).** The advantage survives, at the floor,
10/10. But its registered control does not exist on clean pixels, so the claim's own falsification
criterion is currently unevaluable. Status is yours to set; "holds" is not supportable as written
until a usable null exists.

**`block1-coheres-at-matched-displacement` (holds).** This one does not survive. Published:
0.949 for the first group, 0.958 for the last, "highly consistent across subjects rather than
unstable". Measured here in the primary space:

| | published (HUD) | v3 (clean) |
| --- | ---: | ---: |
| coherence, `Block_1` | 0.949 | **0.616** |
| coherence, `Block_6` | 0.958 | **0.843** |

and `Block_1`'s per-prompt values run from **0.093 to 0.990** — S04_gouache 0.093, S03_cyberpunk
0.281, S05_pencil 0.309, S09_fresco 0.319 against S08_papercraft 0.990. That is not consistency,
it is a wide scatter with a positive mean. *(Caveat: the v3 primary space is
`glcm_contrast`/`glcm_homogeneity`/`lbp_entropy`; confirm it is the same feature set the earlier
page called primary before treating this as like-for-like.)*

**`block1-does-not-replicate` (ambiguous).** Reinforced, and now with a magnitude. The
antisymmetric response norm in the primary space is **0.07–0.23 for `Block_1`** against
**0.44–1.23 for `Block_6`** — the last group moves the image four to eight times further at an
identical, measured displacement. The first group is not merely unstable; it barely responds.

**One caveat on V itself.** V is built partly from `B6_neg`, which fails the gate in 5 of 30 cells,
touching 2 prompts of 10 (`S01_oil`, `S06_pastel`). Their V values are +1.089 and +1.072, close to
the mean of +1.142, so dropping them would not change the sign or the floor — but the primary
statistic is not entirely free of degraded pixels either.

---

## 4. Why the Palette space inverts, and why it matters

`scramble_B` is the **most coherent arm in the bench** in the palette space: cross-prompt coherence
**0.903**, against 0.496 for `Block_1` and 0.392 for `Block_6`. A perturbation that shifts every
image's luminance by the same 20–40 units in the same direction produces exactly that — a large,
perfectly reproducible palette direction that has nothing to do with the perturbation's geometry.

So the one space where the registered criterion fails is the space where the artefact is
strongest, and the failure is explained by the artefact rather than by the anatomy. That is a
hypothesis consistent with the numbers, not a demonstration: it predicts that a `scramble_B`
brought inside the gate would lose most of its palette coherence, and that is testable with
renders, not with arithmetic.

---

## 5. What would make this evaluable

Three routes, none of them run here, in increasing cost.

1. **A different null.** Any norm-matched perturbation anchored on `Block_6` that survives the
   gate. The sign scramble is one choice among many and it happens to be a luminance pump; a
   permutation that preserves the block's mean gain might not be.
2. **`scramble_B` at a lower dose, declared asymmetric.** Cheapest in renders, but it breaks
   displacement matching between the two halves of the null, which is the thing the design exists
   to protect.
3. **Accept that the control is unavailable** and retire the criterion, reporting V with no null
   and saying plainly what that costs — which is most of its meaning, since the published +0.532
   null was itself the page's most important caveat.

## Files

* `data/rotations_matched_v3_results.csv` — one row per space
* `data/rotations_matched_v3_prompt_scores.csv` — V, V_scr and both coherences per prompt
* `data/rotations_matched_v3_gate_by_condition.csv` — the gate census that §1 rests on
