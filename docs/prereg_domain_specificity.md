# Pre-registration — Is the calibrated preset *domain-specific* where the random control is not?

- **Written:** 2026-09-25
- **Corpus:** existing renders only. **No new renders are generated for this study.**
- **Relates to:** `docs/prereg_family_coherence.md` and its amendments 01–03,
  `data/family_coherence_by_family_pair.csv`.

---

## 0. Disclosure, first, because it governs how the result may be read

**The pattern this document tests was seen before this document was written.** It appeared in
`data/family_coherence_by_family_pair.csv`, the post-hoc decomposition that withdrew the
verdict of the family-coherence study. The numbers that prompted it are, for the B–C pairs,
`preset_pos` +0.0772 against `rand_pos` +0.2610.

Therefore the p-value produced here is **not a discovery p-value**. What this document buys is
narrower and real: it fixes the statistic, the null and the decision rule before the test is
run, so that the effect cannot be reshaped to fit; and it states the guards that could kill it.
Whatever comes out, the finding is **provisional and requires replication on a corpus not used
here**. That replication is a render request and is specified in §8.

## 1. The question

Two prompts of the same style domain share a displacement direction; two prompts of different
domains do not. This is true of any edit. The question is whether the **calibrated preset loses
more** when the domain boundary is crossed than a **norm-matched random edit at the same
displacement** does.

If it does, the preset is doing something contingent on the style it is acting on, while the
random edit carries a generic component that survives anywhere. If it does not, the preset's
direction is simply a scaled version of what any perturbation does.

The claim has a shape that an artefact struggles to imitate: a **crossover**. The preset must
transfer *better* than random within a domain and *worse* than random across it. A uniform
scale difference, a noise-floor difference or a feature-saturation artefact produces a main
effect, not a crossover.

## 2. Corpus — frozen

Two families from `docs/prereg_family_coherence.md` §2, and no others:

- **B** — `I01, I02, I05, I06, I07, I09, I10, I11, I12, I16, I17, I18, I20, I21, I23, I24`
  (16 prompts): Western comics, upper-body portrait with armour. Arms from run
  `stage7b_20260917_132611`, baselines from `stage7a_20260917_121226`.
- **C** — `ST1`…`ST8` (8 prompts, `S1_photo`…`S8_charcoal`): eight rendering styles on one
  subject. Arms and baselines from run `stage9_20260918_085644`.

A1 and A2 are **excluded** because they carry a different harness version
(`suite_git_sha = ff680ad0a33ee142`). B and C share `ba28b12532175220`, the same sampler
(`euler_ancestral`), 9 steps, cfg 1.0 and 1024×1280.

Arms, identical preset files in both families: `preset_pos` = `Arthemy_Bench_Base.json`,
`rand_pos` = `Arthemy_Bench_RANDSIGN.json`, `blockshuf_neg` = `Arthemy_Bench_BLOCKSHUFFLE_NEG.json`
(labelled `*_1x`, strength 1.0, in the stage9 manifest). Seeds 42, 777, 1337, 9999, 4242145.

## 3. Representation — frozen, and deliberately not reused verbatim

Features, Δ definition and cosine exactly as in `docs/prereg_family_coherence.md` §3.
**One difference, fixed here:** the standardisation is computed from the baselines of **this
study's 24 prompts only** (24 × 5 = 120 baseline rows), not from the 48-prompt set, so that the
study is self-contained and family C is not compressed by the variance of corpora it is being
compared against.

The 48-prompt standardisation already on disk in `data/family_coherence_pairs.csv` is carried
as a **cross-check**. If the two standardisations disagree on the **sign** of the primary
statistic, the study is declared inconclusive (§6 rule 4).

## 4. The statistics — frozen

Per arm *a*, over prompt pairs:

- `W_B(a)` — mean cosine over the 120 B×B pairs
- `W_C(a)` — mean cosine over the 28 C×C pairs
- `W(a)` — mean over all 148 within-domain pairs
- `X(a)` — mean over the 128 B×C pairs
- `D(a) = W(a) − X(a)` — how much direction is lost at the boundary

**Primary statistic:** `Δ = D(preset_pos) − D(rand_pos)`. The claim predicts `Δ > 0`.

**Crossover, reported alongside and required by rule 2:** `W(preset_pos) − W(rand_pos) > 0`
together with `X(preset_pos) − X(rand_pos) < 0`.

## 5. The null — exact in form, sampled in practice

The arm label `preset_pos` ↔ `rand_pos` is exchangeable **within each prompt**: under the null,
which of a prompt's two displacement vectors is called the preset carries no information. The
null distribution is over the 2²⁴ label assignments, one binary choice per prompt, which is the
sign-flip permutation this project uses elsewhere; the exact floor would be 2/2²⁴ = 1.192e-07.

Exhaustive enumeration is 16.8 million assignments over 148 + 128 pairs and is not run.
**20 000 assignments** are drawn with `random.Random(1337)`, giving

    p = (1 + #{Δ_perm ≥ Δ_obs}) / (1 + 20 000),  achievable floor 4.99975e-05

The prompt is the unit; pairs are never treated as independent. No binomial test.

`blockshuf_neg` is tested the same way against `rand_pos`, as a separate statistic, and is
**not** merged into the primary. Holm over the two tests.

## 6. Decision rules — frozen before the first computation

1. **Refuted** if `Δ ≤ 0`.
2. **Refuted** if the crossover fails, i.e. if `X(preset_pos) ≥ X(rand_pos)` or
   `W(preset_pos) ≤ W(rand_pos)`. A one-sided difference is not what is claimed.
3. **Inconclusive — instrument** if the split-half reliability of Δ, measured per arm and per
   family as in `docs/prereg_family_coherence.md` §4, is below **0.50** for `preset_pos` on
   family C. A cross-domain cosine built on an unreliable vector means nothing.
4. **Inconclusive — representation** if the sign of Δ differs between the standardisation of §3
   and the 48-prompt cross-check, or between the 23-feature and the 19-feature texture
   representation.
5. **Holds, provisionally** if `Δ > 0`, Holm p < 0.05, and rules 2–4 all pass. Wording fixed
   now: *within one style domain the calibrated preset transfers its direction better than a
   norm-matched random edit, and across a style boundary it transfers worse; the effect is
   provisional and has not been replicated on an independent corpus.*
6. **Not specific to calibration** if rule 5 is met and `blockshuf_neg` also reaches
   `Δ ≥ 0.5 × Δ(preset_pos)` with Holm p < 0.05. Wording then: *structured edits, calibrated or
   block-shuffled, are domain-contingent; the sign-scrambled control is not.*

No claim from this study enters `notebook/` without a separate, explicit decision, whatever the
outcome.

## 7. What would kill this study

- Family C is 8 prompts and 28 within-family pairs. `W_C` rests on a thin base and its own
  prompts are eight different styles, so `W_C` is expected to be low for every arm; the pooled
  `W(a)` is therefore dominated by B. This is stated now so that a large `D(a)` is not read as
  more than "B-internal coherence minus B-to-C transfer".
- Family C's baselines include pixel art and stained glass, where edge density, stroke width and
  colour-cluster features can saturate. A saturated feature contributes a near-constant
  component to Δ for every arm, which would depress cosines for all arms alike; it damages rule
  5 only if it acts asymmetrically on the preset, which the crossover requirement of rule 2 is
  there to catch.
- B's baselines come from `stage7a` and B's arms from `stage7b`; C's come from one run. The
  determinism evidence of `docs/prereg_family_coherence_amendment_03.md` §1 is what licenses
  ignoring this. If that evidence is ever contradicted, this study falls with it.

## 8. The replication this study cannot provide

One render run containing **both** domains, queued together: at least four comics prompts and
four style prompts, each with `baseline`, `preset_pos`, `rand_pos`, `blockshuf_neg` at the five
standard seeds — 8 × 4 × 5 = **160 renders**. Only that design separates "style domain" from
"which corpus a prompt was rendered in" by construction rather than by argument. It is a render
request; it belongs to the observer.

## 9. Outputs

- `data/domain_specificity_tests.csv` — one row per (arm contrast, representation,
  standardisation): W_B, W_C, W, X, D, Δ, permutation p, Holm p, reliability per family, verdict.
- `data/domain_specificity_pairs.csv` — one row per (arm, pair): cosine, the two domains.
