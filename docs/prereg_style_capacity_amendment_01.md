# Amendment 01 to `docs/prereg_style_capacity.md` — the corpus is eight prompts, not one

- **Written:** 2026-09-25, after the inventory of the delivered renders and **before any feature
  was extracted, any distance computed or any statistic seen.** The parent pre-registration is
  frozen at commit `8ac368b`, its script at `08c6266`, its multi-prompt guard at `7d2f023`.
- **Nature:** the corpus delivered is larger than the one the parent document was written for.
  This amendment states what that changes and freezes the new rules. It relaxes nothing.

---

## 1. What was delivered

`C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_atlas_phase1\renders`

| | |
|---|---|
| files | **649** (648 planned + 1 determinism check) |
| planned renders missing | **0** |
| prompts | **8** — `S1_photo`, `S2_watercolor`, `S3_lowpoly`, `S4_claymation`, `S5_ukiyoe`, `S6_pixel`, `S7_glass`, `S8_charcoal` |
| seeds | 42, 777, 1337 |
| presets | **26** = 13 regions × 2 independent draws |
| baselines | 24 = 8 prompts × 3 seeds, complete |
| perturbations | 624 = 26 × 8 × 3, every preset covering all 24 (prompt, seed) cells |

The parent document's §1 reads *"Phase 1 renders one prompt … therefore K measured here is the
capacity on one scene"*. That sentence no longer describes the corpus, and the limitation it
named is lifted.

**But note what the eight prompts are.** They are eight *different rendering styles* sharing one
subject. `docs/prereg_domain_specificity.md` measured, on this same corpus family, a transfer
cosine of ≈ 0.05 across a style boundary against ≈ 0.19 for the random control. So this is the
**hardest** possible test of a cross-scene identity, not a typical one. A preset that keeps its
identity across ukiyo-e, pixel art and photography is doing something strong; a preset that does
not is not thereby shown to lack identity between two comics prompts.

## 2. The three corrections, forced by the design

1. **Baselines are paired by (prompt, seed)**, never by seed alone.

       Δ(p, q, s) = x(preset p, prompt q, seed s) − x(baseline, prompt q, seed s)

   624 displacement vectors. The guard committed at `7d2f023` exists because the frozen loader
   keyed baselines by seed alone and would have anchored every displacement to whichever prompt
   was read last, silently.

2. **The null permutes within prompt.** Exchanging displacement vectors between prompts would
   mix scenes and inflate τ. Every permutation reassigns the 78 vectors of one prompt among the
   26 presets of that prompt, independently per prompt, 10 000 draws, `random.Random(1337)`.

3. **Scale.** Pooled within-(preset, prompt) standard deviation of Δ across seeds, pooled over
   all 208 (preset, prompt) cells — 416 degrees of freedom, against 52 in the parent document.

## 3. K — the aggregation rule, frozen before any K exists

Per prompt *q*: centroids over 3 seeds, 325 pairwise distances, τ_q from the max-statistic null
of §2 item 2, and the graph whose edges join pairs **not** distinguishable.

- **K_common — PRIMARY.** Two presets are declared indistinguishable if they are
  indistinguishable **in at least 5 of the 8 prompts**. K_common = connected components of that
  consensus graph. The majority threshold 5/8 is arbitrary and is fixed here so that it cannot
  be chosen afterwards. This counts styles that can be told apart *whatever the scene*, which is
  the product question.
- **K_median — secondary.** The median of K_q over the eight prompts: capacity inside one scene,
  the quantity the parent document could measure.
- **K_pooled — secondary.** Centroids taken over all 24 (prompt, seed) cells, i.e. averaging the
  displacement across scenes, with the same within-prompt null. This one requires a *shared
  direction*, not merely separability.

**Frozen interpretations.**

- K_common ≈ K_median → separability does not depend on the scene.
- K_common ≪ K_median → presets are distinguishable inside a scene but not the same way in every
  scene. Wording fixed now: *the tuner's presets have a per-scene identity, not a portable one.*
- K_pooled ≪ K_common → the presets are separable but their directions do not survive averaging
  across styles. Wording fixed now: *the identity is real and the direction is scene-dependent.*
  Given `prereg_domain_specificity.md`, this outcome is the one the existing evidence predicts,
  and it is written here in advance so that it cannot be presented later as a surprise.

Every K is reported for both geometries (Euclidean, cosine) and both representations (23
features, 19 texture), exactly as the parent document specifies. Rule 3 of the parent §6 —
*capacity is mostly magnitude if K_cos < 0.5 × K_euclid* — applies to K_common.

## 4. Q1 and Q2, adapted without changing their meaning

**Q1 — is the region the unit of control?** R_q = mean between-region distance − mean
within-region distance, per prompt; the reported R is the mean over the eight prompts. The null
permutes the region labels over the 26 presets, one relabelling applied to all prompts at once
because region membership is a property of the preset, 10 000 draws, same seed. The two frozen
readings of the parent §5 are unchanged.

**Q2 — is capacity just sensitivity?** Spearman ρ between distinctiveness and ‖Δ‖ per prompt;
the reported ρ is the median over prompts. The 0.8 rule of the parent §6 applies to it.

## 5. One analysis added, because the corpus now allows it

**Leave-one-prompt-out identification of the 26 presets.** Nearest centroid by cosine, eight
folds, one whole prompt held out per fold; chance 1/26 = 0.03846; null by permuting preset
labels within each (prompt, seed) group, 1000 draws, `random.Random(1337)`. Reported as
**secondary**, alongside per-preset recall.

This is the analysis the single-prompt design could not do, and it is the closest thing in this
study to the product claim: *a preset made by the tuner is recognisable on a scene it was never
tuned on.* It is added here, before any feature exists, and not after a K disappointed.

## 6. What still kills the study

- Three seeds. Every centroid rests on three images; the max-statistic null will return a large
  τ if that is not enough, and a small K will mean *this corpus could not resolve more*.
- Eight prompts that are eight different styles — see §1. Hard case, not neutral case.
- Depth confounded with region, and the 17 uncovered tensors, exactly as the parent §7.
- Frobenius matching equalises the cause, never the effect: Q2 is what keeps that visible.
