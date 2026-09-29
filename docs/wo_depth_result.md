# C41 — `wo` cut by depth: the verdict fails, and the test could not have passed

**2026-09-29.** Governed by [`prereg_wo_depth.md`](prereg_wo_depth.md), deposited (`642f361`) before
any render. 254 renders by Alessandro; six baselines borrowed from `benchmark_centre_push`.

> **Eye first.** §8 of the pre-registration asks Alessandro to look at the six slices and the union
> side by side at 1:1 **before** the composition verdict is read to him. The page is
> `benchmark_wo_depth/presets.html`. His answer goes in §8 below, verbatim.

## 0. What was already known — searched in docs, notebook, data and presets

- **`assessment_sign_aligned_stacking.md`** and `regola_angolo_9_coppie.md`: composition of **pairs**
  of block groups, ρ = ‖Δ(A+B)‖ / ‖Δ(A)+Δ(B)‖, nine pairs **at dose 0.200**. `B5+B1` added (4/4),
  `B5+B4` did not (0/4), `B1+B4` was super-additive (ρ = 1.167). That document flags that the law was
  measured only in a degraded regime and that **a low-dose replication was queued**.
- **`rectified_mask_result.md`**: a composed prediction missed by 0.31 and by direction, on masks.
- **`composition_by_family.csv`**: scalar predicted-vs-observed for masks, small deviations.
- **Nothing** composed **one kind of parameter across depth**, or more than two parts at once.

## 1. Guards — all pass

| guard | result |
|---|---|
| **G_det** | both re-rendered baselines equal the borrowed ones **pixel for pixel** (max \|d\| = 0). The borrow is valid |
| G1 | 254/254 present; prompt, seed, steps, size and preset name read from each render's own graph match the plan |
| G3 | 0 perturbed renders identical to their baseline |
| G_applied | every preset reported its expected matched count — 5, 5, 5, 5, 4, 4 and 28 |
| G_union | at all six signed doses, the six slices are disjoint and their union is the union preset's key set |

## 2. Confirmatory and exploratory — who decided what, and when

The pre-registration covers **±0.100** only. Its §9: *"A second dose is a new pre-registration."*
±0.200 and ±0.350 were added by commit `f9834af` — rendered 08:11–09:47, committed at 10:04, with
new presets that I have checked (disjoint, union exact, deltas consistent). They carry no
pre-registration, so **every number they produce below is exploratory and cannot move the
verdict.** They are used, because they turned out to be where the information is.

## 3. The pre-registered verdict: composition NOT SUPPORTED

Seed means, ranges over the three seeds in brackets. Criterion: cos ≥ 0.95 **and** 0.90 ≤ ρ ≤ 1.10 in
all four prompt × sign combinations.

| dose | prompt | ρ = ‖U‖/‖Σ‖ | cos(U, Σ) | ‖U − Σ‖ / N | ‖U‖ / N | ‖Σ‖ / N | |
|---|---|--:|--:|--:|--:|--:|---|
| −0.100 | P01 | 0.398 [0.34–0.47] | 0.664 [0.47–0.78] | 3.18 | 1.56 | 4.01 | fails |
| −0.100 | P02 | 0.582 [0.20–1.28] | 0.602 [0.29–0.89] | 2.35 | 0.78 | 2.68 | fails |
| +0.100 | P01 | 0.514 [0.44–0.61] | 0.662 [0.59–0.71] | 2.72 | 1.78 | 3.54 | fails |
| +0.100 | P02 | 0.432 [0.17–0.64] | 0.569 [0.50–0.64] | 1.74 | 0.71 | 2.01 | fails |

**Not supported**, on both criteria, in all four. That is the verdict and it stands.

## 4. Why that verdict is not informative — post hoc, and the defect is mine

Look at the magnitudes. At ±0.100 the union moves **0.7–1.8 units of seed noise**; the sum of the
six slices moves **2.0–4.0**. If each slice's displacement were mostly a **seed-specific kick**
rather than a reproducible direction, adding six of them would add six kicks and give ‖Σ‖ about √6 ≈
2.4 times one — which is roughly what is observed. The pre-registration did not anticipate this, so
it was checked (`experiments/wo_depth_noise_diagnostic.py`, `data/wo_depth_noise_diagnostic.csv`):

| dose | prompt | union vs itself across seeds (mean cos) | slices vs themselves (mean) | seed-averaged ρ | seed-averaged cos |
|---|---|--:|--:|--:|--:|
| −0.100 | P01 | 0.811 | 0.385 | 0.443 | 0.698 |
| −0.100 | P02 | **0.326** | **0.057** | 0.448 | 0.760 |
| +0.100 | P01 | 0.875 | 0.367 | 0.563 | 0.703 |
| +0.100 | P02 | **0.131** | 0.156 | 0.474 | −0.083 |

**At ±0.100 a slice at one seed and the same slice at another point in nearly unrelated directions
(mean cos 0.06–0.39).** On `P02` even the **union** barely agrees with itself (0.33 and 0.13). The
criterion demanded cos ≥ 0.95 between the union and the sum of parts — **a level the union does not
reach against its own replicate.** The test was unpassable at this dose whatever composition does.
It cannot distinguish *"composition fails"* from *"at ±0.100 there is no reproducible direction to
compose"*. Drafted as **pitfall 89**.

This also bears on the queued low-dose replication of the angle rule: **at low dose, for `wo`
slices, there may be no stable direction between which to measure an angle.**

## 5. What the bench does say — all exploratory

### 5a. The union is more reproducible, and more of a single axis, than any of its parts

At ±0.100 on `P01` the union agrees with itself at cos 0.81–0.88 while its parts manage 0.37–0.39.
And the union's positive and negative arms are **antiparallel** (cos(+, −) = **−0.87** and **−0.85**
at ±0.100, `data/wo_depth_secondaries.csv`) while most slices are not (b2 +0.05 / +0.92, b3 +0.18 /
+0.82). Moving 28 blocks together produces **a cleaner, more consistent edit than moving any five of
them** — the seed-specific parts cancel, a shared component survives. Whatever composition is, it is
not "the union is the sum of six noisy kicks".

### 5b. On fine grain, the parts DO compose — multiplicatively

On one scalar, the band-0 (1–2 px) energy ratio, the natural composition is multiplicative: the
union should equal the product of the six slices. Post hoc (`wo_depth_band_composition.py`):

| dose | P01: product → union | P02: product → union |
|---|---|---|
| −0.350 | 0.430 → 0.475 | 0.372 → 0.341 |
| −0.200 | 0.674 → 0.706 | 0.693 → 0.713 |
| −0.100 | 0.828 → 0.838 | 0.921 → 0.889 |
| +0.100 | 1.226 → 1.177 | 1.102 → 1.070 |
| +0.200 | 1.327 → 1.282 | 1.202 → 1.163 |
| +0.350 | 1.383 → 1.235 | 1.296 → 1.238 |

**Within 1–11 % in all twelve.** And with one systematic tilt: on the **positive** arm the union is
below the product **six times out of six** (ln-ratio 0.65–0.88) — the grain added by the six slices
together is less than their product predicts, the saturation `assessment_sign_aligned_stacking.md`
already suspected. On the negative arm it is on both sides of 1.

So the reading is: **an aggregate scalar composes; the 23-feature vector at low dose does not,
because at low dose that vector is mostly seed-specific.** It is consistent with
`B5+B1` adding on four tone scalars in 2026-09-19's Previsione 01.

### 5c. The depth profile of fine grain is a U on the negative arm

Band-0 ratio per slice, seed means, `b1 … b6`:

| | b1 | b2 | b3 | b4 | b5 | b6 |
|---|--:|--:|--:|--:|--:|--:|
| −0.350 P01 | **0.690** | 0.993 | 0.983 | 0.986 | 0.895 | **0.726** |
| −0.350 P02 | **0.758** | 0.901 | 0.892 | 0.947 | 0.933 | **0.692** |
| −0.200 P01 | **0.866** | 0.966 | 1.011 | 0.998 | 0.934 | **0.857** |
| −0.100 P01 | **0.940** | 0.998 | 0.982 | 1.003 | 0.965 | **0.932** |

**Both ends strong, the middle nearly inert.** `wo` removes fine grain at the first and last groups
and barely at all in between.

### 5d. The atlas's "front is neutral" does not replicate on these prompts

`b1` and `b6` here are the same presets as `benchmark_qkvo_atlas`, on different prompts. The atlas
(eight styles) had `wo_b1` near-neutral on band 0 (1.017 / 0.992) and `wo_b6` antisymmetric
(0.910 / 1.081). Here, at the same ±0.100:

- `b6` keeps its **direction** (up on the positive arm, down on the negative) at about half the size;
- `b1` on `P01` is **as strong as `b6`** (1.056 / 0.940) and on `P02` neutral (0.995 / 1.007).

**The "neutral front" was a property of the atlas's prompts, not of `wo_b1`.** The sentence in
`parameter_families_first_result.md` §1b that relayed it is annotated accordingly. And in z space it
is `b1`, not `b6`, whose two arms are consistently antiparallel (cos(+, −) −0.40 to −0.88 at every
dose and prompt); `b6` is so only at ±0.100 on `P02`.

## 6. The predictions, scored

| analyst prediction | outcome |
|---|---|
| composition fails, p ≈ 0.7 | **formally right**, but for a reason I did not foresee — §4 |
| it fails on ρ, **direction preserved** | **wrong** — cos 0.57–0.66, the direction is not preserved |
| S2: `b6` carries the largest band-0 share | **not confirmed** at ±0.100 (2 of 4); `b6` in 7 of 12 over all doses |
| S3: not monotone, inversion most likely at `b2` | not monotone **right**; the location **wrong** — the shape is a U, not a `b2` anomaly |
| `b5`/`b6` move at least as much as `b2` | on `P01` yes, on `P02` no — at ±0.100 on `P02` everything sits near one noise unit |

Alessandro's slot was left empty and stays empty; it was not filled before the analysis.

## 7. Limits

Two prompts, one drawing style, three seeds. Every result in §5 is exploratory, and §5b chose its
statistic after the primary was seen. Band 0 is a single scalar out of five octaves and 23 features.

## 8. The eye

Alessandro's notes are in `data/wo_depth_eye_notes_alessandro.md`, **verbatim**. Two facts about how
they were produced, so they are not over-read:

- they were written **after** the composition verdict had been posted in the conversation, so §8's
  order (look first, verdict second) was not kept;
- they describe the six slices one by one and left the union empty; asked the §8 question
  directly — *does the union look like one of the six, like all of them, or like something none of
  them is?* — he answered, **also after the verdict**:

> **"Mi sembra l'unione di tutte insieme."**

### 8·0. His answer against the verdict — the disagreement is the result

§8 of the pre-registration: *where the eye and the criterion disagree, that disagreement is the
result.* They disagree, and three measurements sit on different sides of it:

| | says | status |
|---|---|---|
| the pre-registered criterion (23-feature direction and magnitude) | **not** the sum of its parts | confirmatory — but unpassable at ±0.100 (§4, pitfall 89) |
| fine-grain energy, product of six slices vs union | **the sum of its parts**, within 1–11 % in 12/12 | exploratory, post hoc (§5b) |
| direction: is the union closer to the sum, or to its best single slice? | **closer to one slice** — sum wins in **7/36** cells, 4/12 seed-averaged; the winning slice is almost always an end, `b6` on the negative arm, `b1` on the positive | exploratory, post hoc (`wo_depth_union_like.py`) |

**A reading that reconciles all three, and that is a hypothesis, not a finding:** the union *is*
all six together, but the middle four contribute little — §5c showed `b2`…`b5` nearly inert on fine
grain — so "all six together" and "the two ends together" produce nearly the same picture. The eye
sees the sum; the direction test, which is dragged by the four middle slices' seed-specific noise
(§4), prefers a single end. It predicts that **Δ(b1) + Δ(b6) is as close to the union as the full
sum, or closer**. That prediction is **not tested here**: it goes into the pre-registration of C42,
before it is looked at.

### 8a. His words against the measures

Before any number was computed, each phrase was mapped to one measure and a predicted sign
(`docs/wo_depth_eye_mapping.md`, committed `75a1268`). Tested at ±0.350, 6 cells per claim
(`experiments/wo_depth_eye_check.py` → `data/wo_depth_eye_check.csv`). **E12 and E13 reuse S4's
statistic, whose values the analyst had already printed: they are not blind.**

| | his words | measure | agrees | per prompt | |
|---|---|---|--:|---|---|
| **E9** | b6 −: più grigio | mean saturation | **6/6** | 3/3 · 3/3 | ×0.85–0.92, p = 0.016 |
| **E11** | b6 +: colori che si saturano | mean saturation | **6/6** | 3/3 · 3/3 | ×1.10–1.25, p = 0.016 |
| **E10** | b6 −: più giallino | hue, distance to 55° | **5/6** | 3/3 · 2/3 | +15° to +24° on P01 |
| **E8** | b3 +: colori più accesi | colourfulness | **5/6** | 3/3 · 2/3 | |
| E4 | b1 +: colori più vibranti | colourfulness | 4/6 | 1/3 · 3/3 | |
| E12 | b2: il più positivo somiglia al più negativo | cos(Δ₊, Δ₋) > 0 | 4/6 | 2/3 · 2/3 | not blind |
| E1, E3, E6 | linee / tratti più spessi o più sottili | median stroke width | 3/6, 2/6, 3/6 | | **the measure cannot see it** — see below |
| E5, E7 | tinte / colori piatti | effective colour count | 2/6, 3/6 | | chance |
| **E2** | b1 −: **colori meno accentuati** | colourfulness | **0/6** | 0/3 · 0/3 | **the opposite in every cell**, ×1.11–1.20 |
| E13 | b1, b3, b6 "chiare" more bipolar than b2, b4 "non chiare" | seed-mean cos(Δ₊, Δ₋) | P01 yes, P02 no | | not blind |

Three readings, none of them more than exploratory:

1. **On `b6` his eye and the measures agree completely**: greyer and yellower one way, more saturated
   the other, in every cell. It is the strongest agreement between his descriptions and a number
   this project has recorded.
2. **Line thickness cannot be tested with this measure.** `stroke_width_median_px` takes a handful of
   discrete values — its ratios here are exactly 1.000, 1.429, 0.714, 0.700 — so it moves in whole
   pixels or not at all. 3/6 is the measure's resolution, not a verdict on his eye.
3. **E2 is contradicted, and the likely reason is in his own note.** On `b1` at −0.350 he wrote
   *colori meno accentuati* **and** *effetto "coriandoli"*. Colourfulness is a per-pixel statistic, and
   confetti is exactly high-frequency colour speckle: it can raise colourfulness while the colour of
   the drawing's areas goes down. That is a hypothesis about the measure, not a rescue of the claim —
   the same failure `L` showed on the eye veto, a statistic reading a regular artefact as "more".

### 8b. A flag on `Block_6` and colour

`chroma_redistribution.md` measured the **whole** `Block_6` group (every tensor) on the leaf prompts:
frame chroma pos ×1.488, neg ×1.814. The `wo` slice of the same blocks, here: saturation **up on the
positive arm** (same direction) but **down on the negative arm** (×0.85–0.92, the opposite). Different
prompts and a different colour measure, so this is not yet a contradiction. If it holds, **`wo` is
not what makes `Block_6 neg` raise chroma** — some other tensor in those four blocks is, and the
group's effect is again a mixture.

## 9. Provenance

`experiments/analyze_wo_depth.py --extract --guards --run` → `data/wo_depth_measures.csv` (260 rows),
`wo_depth_guards.csv`, `wo_depth_composition_cells.csv`, `wo_depth_composition_summary.csv`,
`wo_depth_profile.csv`. Post hoc: `wo_depth_noise_diagnostic.py`, `wo_depth_band_composition.py`;
secondaries: `wo_depth_secondaries.py`. Page: `build_annotation_page.py wo_depth`.
