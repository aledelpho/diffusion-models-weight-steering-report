# Pre-registration — Does the edit hold its direction *within a family of prompts*?

- **Written:** 2026-09-25
- **Status at writing:** no script exists. No cosine, no cross-prompt statistic of any kind
  has been computed on the corpora named below for this question.
- **Corpus:** existing renders only. **No new renders are generated for this study.**
- **Relates to:** `docs/prereg_arm_identifiability.md`, `docs/prereg_shared_axis.md`,
  `data/arm_coherence.csv`, `data/arm_identifiability_tests.csv`.

---

## 0. Where this question came from

Every cross-prompt statistic this project has published so far pools prompts that are not
comparable. `data/arm_coherence.csv` reports cross-prompt cosines near 0.21 over a prompt
set that mixes an upper-body armoured portrait with a photographic rally car. A direction
that fails to transfer between those two has not been shown to fail between two prompts a
user would actually put side by side.

On 2026-09-25 the observer (A.D.) stated the claim he had meant to test from the start:
that the effect he perceives is a coherent, recognisable signature **at least within a
family of similar prompts**. He then named the family by pointing at three render folders
(`benchmark_stage4_preset`, `benchmark_stage5`, `benchmark_stage6`).

This document tests that claim. It is not a re-run of an earlier study: no previous
analysis has ever conditioned a cross-prompt statistic on prompt family.

## 1. The question, stated as two tests

**T1 (the family gap).** Is the cosine between the displacement directions of two prompts
of the **same** family larger than between two prompts of **different** families?

**T2 (specificity).** Is any such gap larger for the calibrated preset than for the
norm-matched random control at the same displacement?

T1 alone cannot support the claim the observer cares about. If the gap is the same size for
the random control, the family-coherence is a property of the scene and the corpus, not of
the edit. **This outcome is stated here, before the computation, as the one the prior
evidence makes most likely** (`data/seed_stability_tests.csv`,
`data/mountain_reachability_tests.csv`).

## 2. Corpus — frozen

All rows come from three existing feature files produced by one extractor:
`data/style_features.csv`, `data/style_features_stage7.csv`, `data/style_features_stage9.csv`.

Four prompt families, defined by the prompt template and fixed before any computation:

| id | family | prompts | n | render run |
|----|--------|---------|---|------------|
| A1 | Western comics, extreme close-up head only, white background, **one pinned monochromatic hue per prompt** | F1–F4, G1–G6, H01–H08 | 18 | stage4 (2026-09-14), stage5 (2026-09-15), stage6 (2026-09-15) |
| A2 | same template as A1, **no colour clause** | S7_01–S7_06 | 6 | stage6b pilot (2026-09-15) |
| B  | Western comics, **upper-body portrait with armour**, no pinned hue | I01, I02, I05, I06, I07, I09, I10, I11, I12, I16, I17, I18, I20, I21, I23, I24 | 16 | stage7b (2026-09-17) |
| C  | **eight rendering styles**, one shared subject (rally car) | S1–S8 | 8 | stage9 |

A2 is matched one-to-one with G1–G6: same subject, with and without the colour clause
(prompt-text similarity 0.94, 0.94, 0.78, 0.95, 0.45, 0.95 for S7_01…S7_06 against G1…G6).

**Arms.** Every arm below is the *same preset file* in every corpus, verified from the
manifests:

- `preset_pos` = `Arthemy_Bench_Base.json` (in stage9 it is labelled `preset_pos_1x`, strength 1.0)
- `rand_pos` = `Arthemy_Bench_RANDSIGN.json` (stage9: `rand_pos_1x`)
- `blockshuf_neg` = `Arthemy_Bench_BLOCKSHUFFLE_NEG.json` (stage9: `blockshuf_neg_1x`)
- `preset_neg` = `Arthemy_Bench_NEG.json`, `rand_neg` = `Arthemy_Bench_RANDSIGN_NEG.json`,
  `blockshuf_pos` = `Arthemy_Bench_BLOCKSHUFFLE.json` — present in A1, A2, B only.

**Primary arm set** (available in all four families): `preset_pos`, `rand_pos`, `blockshuf_neg`.
**Secondary arm set** (families A1, A2, B only): the three remaining arms.

**Seeds.** 42, 777, 1337, 9999, 4242145 — the five seeds common to every corpus. No other
seed enters this study, including the extra baseline seeds present in stage5 and stage6.

**Inclusion rule.** A prompt enters an arm's analysis only if all five seeds are present for
that arm **and** the paired baseline exists at the same prompt and the same seed. This was
verified before writing: zero arm rows lack their paired baseline in any of the three files.
Any prompt failing this rule at run time is dropped and recorded in the output; it is not
repaired.

**Excluded by name:** `preset_half` (A1/A2 only, no counterpart elsewhere), `chaos_edges_v2`,
and every `*_2x` condition. `chaos_edges_v2` is additionally excluded because 20 rows of
`data/stage9_images.csv` carry a `prompt_sha1` that does not hash their own `prompt_text`;
that defect is reported separately and is not repaired by this study.

## 3. Representation — frozen

**Features.** The 23 numeric columns of the style extractor, in file order:
`stroke_width_median_px`, `stroke_width_std_px`, `stroke_width_cv`, `edge_density`,
`contour_mean_length_px`, `contour_n_components`, `crosshatch_entropy_mean`,
`crosshatch_entropy_p90`, `color_top4_cluster_share`, `color_cluster_entropy_norm`,
`color_n_effective`, `colorfulness_hs`, `luminance_hist_n_peaks`,
`shadow_edge_transition_width_px`, `shadow_edge_transition_width_std`, `glcm_contrast`,
`glcm_homogeneity`, `glcm_energy`, `glcm_correlation`, `lbp_entropy`, `lbp_uniform_share`,
`fft_radial_slope`, `fft_high_freq_share`.
`file`, `width_px`, `height_px` and every metadata column are not features.

**Standardisation.** One standardisation for the whole study: per-feature mean and standard
deviation computed **from baseline rows only**, pooled over all four families at the five
common seeds. Arm rows never enter the standardisation (pitfall 33). A feature with zero
variance among baselines is dropped and the drop is recorded.

**Displacement.** For prompt *p* and arm *a*:

    Δ(p, a) = mean over the 5 seeds of [ z(p, a, s) − z(p, baseline, s) ]

Baseline-anchored and seed-paired, so the scene is differenced out.

**Similarity.** Cosine between Δ vectors. Cosine, not correlation, and not Euclidean
distance: the question is direction, and cosine is scale-invariant, so a prompt that simply
reacts more strongly cannot dominate.

## 4. The statistics — frozen

For each arm *a*, over all unordered prompt pairs (p, q), p ≠ q:

- **W(a)** = mean cos(Δ(p,a), Δ(q,a)) over pairs whose prompts are in the **same** family
- **Bt(a)** = mean over pairs whose prompts are in **different** families
- **G(a) = W(a) − Bt(a)** — the family gap, the primary quantity

**Reliability ceiling.** With five seeds, for each prompt and arm, every 2/3 split of the
seeds (10 splits) gives two independent Δ vectors. `rel(a)` = mean over prompts and splits
of the cosine between them. `W(a)/rel(a)` is reported as the share of the reproducible
direction that transfers between prompts of one family. `rel(a)` is a descriptive ceiling,
not a test.

## 5. The nulls — frozen

**For G(a):** the family labels of prompts are exchangeable. Permute the assignment of
family labels to the 48 prompts, holding the family sizes (18, 6, 16, 8) fixed, recompute
G(a), **10 000 draws**, `random.Random(1337)`. One-sided (the claim predicts W > Bt):

    p = (1 + #{G_perm ≥ G_obs}) / (1 + 10 000),  floor 9.999e-05

The prompt is the unit and the pair is not: permuting prompt labels is the only null that
respects the dependence between pairs that share a prompt. **No test treats pairs as
independent observations.**

**For W(a) > 0:** percentile bootstrap over **prompts**, 2000 resamples,
`random.Random(1337)`; a resample redraws prompts with replacement and recomputes W from the
pairs among the drawn prompts. The 95 % interval is reported. Bootstrap over pairs is
forbidden for the same reason.

**Multiplicity.** Holm correction over the three arms of the primary set. The secondary arm
set is corrected separately, over its own three arms, and is labelled secondary in the output.

## 6. The confound that has to be measured, not declared away

**Family is confounded with render run.** Each of A2, B and C is a single run; A1 spans
three. Two prompts of the same family were, in most pairs, also rendered on the same day
with the same driver, the same model load and the same queue.

The confound is measured, not assumed absent:

- **Guard R1 — run gap inside A1.** Inside A1 alone, relabel prompts by their *run*
  (stage4 = 4 prompts, stage5 = 6, stage6 = 8) and compute the same gap statistic G_run(a)
  with the same permutation null (10 000 draws, same seed). A1 is one family, so under the
  claim being tested G_run should be near zero.
- **Guard R2 — cross-run family gap.** Recompute G(a) after deleting every pair whose two
  prompts share a run. Within-family pairs then survive only inside A1 (F×G, F×H, G×H:
  24 + 32 + 48 = 104 pairs). This is the version of the contrast that the run cannot explain.

## 7. Decision rules — frozen before the first computation

Applied to the primary arm `preset_pos`, on the 23-feature representation:

1. **Refuted** if G(preset_pos) ≤ 0, whatever the p-value.
2. **Confounded / ambiguous** if G(preset_pos) > 0 with Holm p < 0.05 **but** Guard R1 gives
   G_run ≥ 0.5 × G(preset_pos), **or** Guard R2 turns the cross-run gap non-positive. The
   result is then recorded as *ambiguous — family not separable from render run*, and is not
   published as a claim.
3. **Holds, but not specific to the preset** if G(preset_pos) > 0 with Holm p < 0.05, the
   guards pass, **and** G(rand_pos) is also > 0 with Holm p < 0.05 and
   G(preset_pos) < 2 × G(rand_pos). Wording fixed now: *prompt family predicts how much a
   weight edit transfers, for the calibrated preset and for a random edit alike.*
4. **Holds and specific** only if, in addition, G(preset_pos) ≥ 2 × G(rand_pos).
5. The claim **“the preset has a coherent signature within a family”** additionally requires
   the bootstrap 95 % interval of W(preset_pos) to exclude 0. A positive gap over a W that is
   itself indistinguishable from 0 means only that the between-family cosine is negative, and
   is recorded as such.

The 2× factor in rules 3 and 4 is arbitrary and is fixed here precisely so that it cannot be
chosen after seeing the numbers.

## 8. Sensitivity, pre-specified as sensitivity and not as a second primary

The whole analysis is repeated on the **19 texture features**, i.e. dropping
`color_top4_cluster_share`, `color_cluster_entropy_norm`, `color_n_effective`,
`colorfulness_hs`. Reason: every A1 prompt pins a *different* hue by construction, so the
colour features are built to disagree inside A1 and could suppress W(A1) for a reason that
has nothing to do with the edit. The texture-only result is reported alongside; it does not
replace the primary and cannot be substituted for it if the primary disappoints.

## 9. What would kill this study

- A prompt entering with fewer than five seeds, or without its paired baseline.
- Any arm whose preset file differs between corpora. The six file names were checked against
  five manifests before writing; a mismatch found at run time aborts the study.
- Guard R1 showing that the run explains as much as the family — the study then reports a
  confound, not a finding.
- A1 having only 3 runs means Guard R2 rests on 104 pairs from one family; if those 104 pairs
  give a cross-run gap whose sign disagrees with the full-pair gap, the primary is downgraded
  to ambiguous under rule 2 and no wording is published.
- Cosine in 23 dimensions with 48 prompts is a small-sample geometry. The expected cosine of
  two independent random directions is 0 with a standard deviation near 1/√23 ≈ 0.209; a W of
  0.2 is therefore **not** evidence of a shared direction on its own, which is why rule 5
  requires the bootstrap interval and not a comparison against zero by eye.

## 10. Outputs

- `data/family_coherence_inventory.csv` — one row per (family, prompt, arm): seeds found,
  baseline paired, included / excluded and why.
- `data/family_coherence_pairs.csv` — one row per (arm, representation, prompt pair): cosine,
  the two families, the two runs, same_family, same_run.
- `data/family_coherence_tests.csv` — one row per (arm, representation): W, Bt, G, permutation
  p, Holm p, rel, W/rel, bootstrap CI for W, Guard R1 and R2 values, the verdict from §7.

No figure is registered by this study. No existing claim changes status as a result of it
without a separate, explicit decision.
