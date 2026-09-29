# Pre-registration — C41: `wo` cut by depth, and the whole against the sum of its parts

**Deposited 2026-09-29, before any render of this bench exists.** Governs
`data/wo_depth_plan.csv` (86 rows) and `experiments/make_wo_depth_presets.py`.

## 1. The question

`Family_wo_d±0.100` moves **one tensor in each of the 28 blocks** — the attention output projection,
8.2447 % of the model's parameters. `parameter_families_first_result.md` reports what it does. It
cannot report **where** it does it, because the 28 blocks moved together.

`benchmark_qkvo_atlas` already split that same set at the two ends, and the ends did not behave
alike: at blocks 0–4 `wo` is nearly neutral in both arms, at blocks 24–27 it is a strongly
antisymmetric fine-grain knob (band 0 at 0.9102 negative, 1.0806 positive). **So the family result is
a mixture.** This bench asks the two questions that follow:

1. **The depth profile.** What does each of the six positional groups do on its own, with the kind
   of parameter held fixed?
2. **Composition.** Is the union equal to the composition of its parts, or does moving 28 blocks
   together produce something none of the six produces?

Question 2 is the one that matters beyond this family. `rectified_mask_result.md` already found that
a composed prediction missed by 0.31 **and by direction**, on masks. If composition fails here too,
every result in this project that reasons about a group as "its members added up" is affected.

## 2. Design

| | |
|---|---|
| conditions | **14** — six slices (`b1`…`b6`) × two signs, plus the union × two signs |
| delta | **±0.100**, `Real Value` (multiplier 1.0 + delta) |
| prompts | `P01` (sha `52e5b19ca6`), `P02` (sha `7919c95fcf`) — **the prompts of `benchmark_centre_push`** |
| seeds | `1618033`, `2718281`, `3141592` — **the seeds of `benchmark_centre_push`** |
| cells | 14 × 2 × 3 = **84 renders** |
| baselines | **0 rendered.** The six baselines of `benchmark_centre_push` are borrowed |
| determinism | **2 rows**: one baseline re-rendered per prompt, to prove the borrow |
| total | **86 renders** |
| settings | `euler_ancestral` / `simple` / 9 steps / cfg 1.0 / denoise 1.0 / 1024×1280 — identical to `centre_push` |

The six slices are **pairwise disjoint** and their union is **exactly** the key set of
`Family_wo_d+0.100.json`; the generator refuses to write anything unless both hold, and it verified
them before emitting. `b1` and `b6` **reuse** `Arthemy_QKVO_wo_b{1,6}_{pos,neg}` from the atlas,
after checking they carry exactly the keys and delta the generator would have written — so two of
the fourteen conditions are already a replication of an existing preset on new prompts and seeds.

## 3. Measures

- **z** — the 23 style features of `experiments/style_features.py`, z-scored against the base cloud,
  as in `groove_or_hole.py`. Δ = z(condition) − z(baseline of the same prompt and seed).
- **band profile** — the five Gaussian-pyramid octaves of `retro_texture_axes.py`, as ratios.
- **L** — structure coherence, **reported but not used for any verdict**. On 2026-09-28 Alessandro's
  eye veto failed it on `benchmark_centre_push` (7 of 9, threshold 8) and found it **inverted** on
  named units. It appears here as a column, never as a criterion.
- **N(p)** — seed noise, the median pairwise distance among the base cloud's baselines of the same
  text. **Computed before the bench, from data already on disk: N(P01) = 1.2553, N(P02) = 2.8425**,
  16 baselines each. Any residual below this is not a finding.

## 4. Primary — composition, with a criterion and no p-value theatre

For each prompt, sign and seed: Σ = Σ₆ Δ(slice), and Δ_U = Δ(union).

- **ρ = ‖Δ_U‖ / ‖Σ‖** — above 1 the whole moves further than its parts added up, below 1 less.
- **cos(Δ_U, Σ)** — whether it moves in the same direction at all.
- **R = ‖Δ_U − Σ‖ / N(p)** — the composition residual in units of seed noise.

**Composition is called supported only if, in all four prompt × sign combinations, the seed-mean
satisfies cos ≥ 0.95 and 0.90 ≤ ρ ≤ 1.10.** One failure and it is not supported.

There are **two prompts**. Pitfall 17 says the prompt × condition is the unit, so four units cannot
carry a p-value that means anything. The criterion above is therefore a stated threshold, the three
seeds give the within-prompt spread, and **the spread is reported next to every number**. No test is
run that pretends the twelve cells are independent.

## 5. Secondary — the depth profile

- **S1.** Per group, ‖Δ‖ / N(p) and the five band ratios, both signs, both prompts.
- **S2.** Is `Block_6` the largest contributor to the union's band-0 change? Pre-specified from the
  atlas, where `wo_b6` moved band 0 by −9 % / +8 % while `wo_b1` moved it by +1.7 % / −0.8 %.
- **S3.** Is the band-0 effect **monotone in depth**? Reported as the six ordered values per sign and
  prompt, with the number of adjacent inversions. No trend test on six points.
- **S4.** Antisymmetry per group: cos(Δ_pos, Δ_neg). At −1 the two arms are a single axis; nearer 0
  they are different edits that happen to share a name.

## 6. Guards — all must pass before §4 is read

- **G_det.** Each determinism row must reproduce the borrowed `benchmark_centre_push` baseline
  **pixel for pixel**. If either fails, **the borrow is void**: six baselines must be rendered and
  this pre-registration re-run against them. Nothing in §4 is reported on borrowed baselines that
  did not reproduce.
- **G1.** 86 files present and non-empty.
- **G3.** No perturbed render identical to its baseline.
- **G_applied.** For every one of the fourteen conditions, the Preset Loader log must report the
  expected matched count (5, 5, 5, 5, 4, 4 for the slices; 28 for the union) **and** the render must
  differ from its baseline. This week's finding is precisely that the first of those two is not
  evidence of the second: three families reported 56, 56 and 28 layers matched and did nothing.
- **G_union.** Re-checked at analysis time from the preset files, not assumed: the six key sets are
  disjoint and their union is the union preset's key set.

## 7. Predictions — deposited now

- **Alessandro:** *(to be filled in before the analysis is read; left empty on purpose)*
- **Analyst:**
  - **Composition fails**, probability about **0.7**: at least one of the four combinations breaks
    the criterion, and it breaks on ρ rather than on cos — direction roughly preserved,
    **magnitude sub-additive (ρ < 0.9)**, because the six edits partly cancel through the residual
    stream. Reasoning: `rectified_mask_result.md`, where a composed prediction missed by 0.31 and by
    direction, is the only comparable measurement in the project and it failed.
  - **S2 confirmed**: `Block_6` carries the largest share of the union's band-0 change.
  - **S3 not monotone**: at least one adjacent inversion in the six, most likely at `Block_2`, the
    group that has behaved anomalously before (`signature_robustness_result.md`, below chance on
    stroke).
  - The per-group ‖Δ‖ will **not** be proportional to parameter count: `b5` and `b6` carry 4 tensors
    against 5 and should still move at least as much as `b2`.

## 8. The eye, which is not optional any more

After 2026-09-28 no verdict here rests on a statistic alone. Once the renders exist,
`build_annotation_page.py wo_depth` produces the annotation page, and **Alessandro looks at the six
slices and the union side by side at 1:1, on one prompt and one seed, before §4 is read to him.**
The question put to him: *does the union look like one of the six, like all of them at once, or like
something none of them is?* His answer is recorded verbatim next to the composition verdict. It does
not override the criterion; it is reported beside it, and where the two disagree, that disagreement
is the result.

## 9. Stopping rule

86 renders, once. No extra seeds if the spread is uncomfortable, no extra dose if ±0.100 turns out
to be small, no third prompt. A second dose is a new pre-registration.
