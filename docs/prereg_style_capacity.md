# Pre-registration — How many distinguishable styles does the tuner produce at one displacement?

- **Written:** 2026-09-25, with the Phase 1 render queue at 52 %.
- **Status at writing:** **the data do not exist.** No image of this corpus has been measured,
  no feature file has been written, no distance has been computed. This is the only
  pre-registration in this project written before its renders finished.
- **Corpus:** `data/perturbation_atlas_phase1_plan.csv` (82 rows), governed by
  `docs/prereg_perturbation_atlas.md` and its amendments 01–06.
- **Relates to:** `docs/instrument_claim_map.md` §6 gap 1.

---

## 0. The claim this is for

The product is not a preset. It is the tuner: a tool that produces styles as ~50 KB files —
1 059 signed scalars against a 12.8-billion-parameter checkpoint. The claim that makes it a
product is a **capacity** claim:

> At one fixed displacement, the tuner produces **K** mutually distinguishable styles.

K is the number. This document fixes how K is computed, what null it is judged against, and
what K would have to be for the claim to fail — before any of it can be looked at.

## 1. What Phase 1 can and cannot answer

Phase 1 renders **one prompt**, `S1_photo` (sha1 `3dd4956c29`), at three seeds
(42, 777, 1337), for 13 conditions × 2 independent draws = **26 presets**, plus 3 baselines
and one determinism check. 78 perturbation images in total.

**Therefore K measured here is the capacity on one scene.** It is not the tuner's capacity.
Leave-one-prompt-out is impossible with one prompt, so nothing here can show that a preset's
identity survives a change of subject — a question this project has already answered separately
and positively for six presets (`data/arm_identifiability_tests.csv`) and negatively across
style domains (`docs/prereg_domain_specificity.md`). This limitation is not a caveat to be
added at the end; it goes in the name of the quantity: **K₁ₛ, capacity on one scene.**

Phase 2 is what would lift it, and the plan committed in `0604c2e` **cannot**: it carries 7
prompts, below the minimum of 8 frozen in the parent pre-registration. That plan is not used by
this study and should not be run as it stands.

## 2. Representation — frozen

Feature file expected at `data/style_features_atlas_phase1.csv`, produced by the existing style
extractor, with the same 23 numeric features as `docs/prereg_family_coherence.md` §3.

**Displacement.** Seeds are matched one-to-one with the three baselines, so for preset *p* and
seed *s*:

    Δ(p, s) = x(p, s) − x(baseline, s)

**Scale.** Each feature is divided by the **pooled within-preset standard deviation of Δ across
seeds**, pooled over all 26 presets (52 degrees of freedom). Distances are then in units of
seed noise, which is the only noise this design has. No standardisation is taken from the
features' overall spread, because that spread is the signal.

**Two geometries, both primary.**
- **Euclidean** distance between preset centroids — sensitive to *how much* a preset moves.
- **Cosine** distance (1 − cos) between preset centroids — sensitive only to *what* it changes.

Both are reported. §6 rule 3 says what it means when they disagree.

## 3. The statistic — frozen

For each of the C(26,2) = **325** preset pairs, the distance between the two centroids of three
Δ vectors.

**Distinguishable** = the pair's distance exceeds τ, the threshold of §4.

**K** = the number of connected components of the graph on 26 nodes whose edges join pairs that
are **not** distinguishable. Merging everything we cannot tell apart makes K conservative by
construction: K counts styles we can defend, never styles we hope for.

K is reported as K_euclid and K_cos, for 23 features and for the 19 texture features.

## 4. The null — a max-statistic permutation, so the 325 pairs cost nothing extra

Under the null, the 78 Δ vectors are exchangeable across presets. A draw reassigns them to 26
groups of 3, recomputes all 325 centroid distances, and records **the largest one**. With
**10 000 draws**, `random.Random(1337)`:

    τ = the 95th percentile of the null distribution of the maximum pairwise distance

Any observed pair above τ is distinguishable with family-wise error ≤ 5 % over all 325 pairs.
No Holm correction is applied on top: the max-statistic already carries the family, and applying
both would be double counting.

Reported alongside: the observed maximum, τ, and the count of pairs above τ.

## 5. The two questions that come free with this design, both pre-specified

**Q1 — is the region the unit of control, or is the draw?** Each of the 13 regions was drawn
twice, independently. So there are **13 within-region pairs** (draw 1 against draw 2 of the same
region) and **312 between-region pairs**.

    R = mean between-region distance − mean within-region distance

Null: permute the region labels over the 26 presets holding the 13×2 structure fixed, 10 000
draws, same seed, one-sided (the claim predicts R > 0).

- R > 0 and p < 0.05 → the **region** carries the style: isolating zones is a way to steer, and
  the hunt for useful zones has a handle.
- R ≈ 0 → the region does **not** determine the style; two draws inside one region differ as
  much as two regions do. The tuner would then be a generator of styles that cannot be aimed by
  choosing where to edit, which contradicts the stated purpose of building the atlas and must be
  reported as such.

Neither outcome is predicted here. Both are written down so that neither can be discovered
afterwards.

**Q2 — is capacity just sensitivity?** For each preset, distinctiveness = its mean distance to
the other 25; magnitude = ‖Δ‖ in the scaled space. Spearman ρ between them is reported. This is
the double reading the notebook already applies to blocks in
`output-lead-survives-dose-normalisation`: the atlas conditions sit at different depths, and
`position-beats-displacement` records that the last block group displaces 28 % less and moves
the image 3.7 times more. Frobenius matching equalises the **cause**, never the effect.

## 6. Decision rules — frozen before the first distance

1. **Refuted for this scene** if no pair exceeds τ. K = 1: at this displacement the tuner
   produces one style on `S1_photo`, whatever region is edited.
2. **K is reported as measured**, with its graph, and always named *capacity on one scene*. No
   sentence in this project may state a capacity for the tuner on the strength of Phase 1.
3. **Capacity is mostly magnitude** if K_cos < 0.5 × K_euclid. Wording fixed now: *the presets
   are told apart mainly by how much they move the image, not by what they change.*
4. **Capacity is dominated by sensitivity** if Spearman ρ of Q2 exceeds 0.8. Wording fixed now:
   *the atlas ranks regions by how strongly they respond, and distinctiveness adds little to
   that ranking.* This does not refute K; it renames it.
5. The Q1 outcome is reported in the words of §5, whichever way it falls.

## 7. What would kill this study

- **One prompt.** Everything above is conditional on `S1_photo`. A capacity that exists only on
  a rally car photographed in a jungle is not a product claim.
- **Three seeds.** Every centroid rests on three images, and the pooled noise estimate on 52
  degrees of freedom. The max-statistic null is honest about this — it will simply return a
  large τ if the design is underpowered, and K will come out small. A small K from Phase 1
  therefore does **not** license "the tuner makes few styles"; it licenses "Phase 1 could not
  resolve more than K".
- **Depth is confounded with region.** `early_*` and `late_*` differ in what they touch and in
  how much network remains downstream. The attention/mlp crossing at each depth is what
  separates them, and that separation is a question for the region analysis, not for K.
- **17 uncovered tensors.** `data/perturbation_atlas_regions.csv` records 17 model tensors in no
  region (first 2, last 4, tmlp 4, tproj 2, txtmlp 5). `uniform_all` and `model_only` include
  them; the eight block regions do not. Any comparison between those two families carries it.
- **A partial queue.** A preset enters only with all three seeds present and all three paired
  baselines. Anything less is dropped and recorded; it is never repaired.

## 8. Outputs

- `data/style_capacity_pairs.csv` — one row per (geometry, representation, preset pair):
  distance, within-region flag, above τ.
- `data/style_capacity_graph.csv` — one row per preset: component id, degree, distinctiveness,
  ‖Δ‖.
- `data/style_capacity_tests.csv` — one row per (geometry, representation): τ, observed maximum,
  pairs above τ, K, R and its p, Spearman ρ, and the verdict from §6.

No figure is registered. No claim enters `notebook/` from this study without a separate,
explicit decision.
