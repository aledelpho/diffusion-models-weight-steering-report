# The decisive test — `first-block-is-an-inverted-knob` is a contrast artefact

**Date**: 2026-09-27 · **Corpus**: `benchmark_profondita` and `benchmark_profondita_neg` — **the
corpus the claim was built on**, 28 single blocks × 2 prompts × 3 seeds at ±0.200, 336 renders.
**No render generated.** **Data**: `data/texture_audit_profondita.csv`.
**Follows**: [`texture_estimator_audit_result.md`](texture_estimator_audit_result.md), which found
the reversal on a different bench and specified this test.

---

## 1. The claim

`first-block-is-an-inverted-knob`, notebook page 05, status **`holds`**:

> *The first block is a knob that runs the opposite way to the tail: pushed positive it smooths,
> pushed negative it etches.*
>
> Published evidence: r⁺ = 0.841, r⁻ = 1.100, swing = 0.764.

## 2. Result

Baselines taken from `benchmark_mappa` at the same prompts and seeds — identical prompt text,
sampler, scheduler, steps, CFG and resolution, verified, and licensed by
`deterministic-across-sessions`.

| `blk00` | r⁺ | cells < 1 | r⁻ | cells < 1 | swing |
|---|--:|--:|--:|--:|--:|
| **`r_global`** — the project's estimator | **0.805** | **6/6** | **1.115** | 1/6 | **0.722** |
| **`r_cnorm`** — per unit of contrast | **1.009** | 4/6 | **0.944** | 4/6 | **1.069** |

**The global estimator reproduces the published claim.** 0.805 / 1.115 / 0.722 against the published
0.841 / 1.100 / 0.764 — not identical, because the baselines here come from a different bench, but
the same numbers and the same story, unanimously across all six cells on the positive arm.

**The contrast-normalised estimator does not.** And the interesting part is not that it reverses:

> **Per unit of contrast, `blk00` is not a knob in either direction.** r⁺ = 1.009 with 4 of 6 cells
> below 1, r⁻ = 0.944 with 4 of 6 cells below 1. Both arms sit at chance. There is no knob to
> invert.

### The arithmetic

`r_global / r_cnorm` is exactly the variance ratio.

* `blk00 pos`: 0.805 / 1.009 → variance falls to **0.798**, contrast to **0.893**.
* `blk00 neg`: 1.115 / 0.944 → variance rises to **1.181**, contrast to **1.087**.

**The first block raises and lowers contrast, and the "inverted knob" is that contrast change read
through a statistic that does not divide by it.** Positive lowers contrast → less absolute
high-frequency energy → "smooths". Negative raises contrast → more → "etches". Nothing about fine
texture is required to explain either.

## 3. What else moves, and what holds

**Nine of twenty-eight blocks change the sign of at least one arm** between the two estimators:
`blk00`, `blk03`, `blk09`, `blk11`, `blk18`, `blk19`, `blk21`, `blk22`, `blk23`. A third of the
depth map is estimator-dependent.

**Punto 7 §1 survives, weakened.** The common mode `c = √(r⁺·r⁻)`:

| estimator | mean | blocks below 1 | sign test | r(depth) |
|---|--:|--:|--:|--:|
| published | 0.978 | 23/28 | — | −0.659 |
| `r_global` here | 0.9521 | **26/28** | p = 1.1 × 10⁻⁶ | −0.594 |
| `r_cnorm` | **0.9716** | **20/28** | **p = 0.0178** | −0.568 |

*"Any perturbation, in any direction, removes fine texture"* **holds** under the correction — the
direction is the same, the sign test still clears 0.05, and the depth correlation barely moves. But
the effect **halves**: a 4.8 % loss becomes **2.8 %**, and the count falls from 26/28 to 20/28.

So the two conclusions of Punto 7 separate cleanly. **§1 is real. §4 is an artefact.**

## 4. What the analyst is and is not saying

* The claim's status is **not changed here**. That is Alessandro's decision, and it is what the
  register calls **A6**.
* What is established: the claim's estimator is confounded with contrast; on the claim's **own
  corpus**, dividing by contrast removes the effect entirely rather than reversing it; and the
  mechanism — `blk00` moving contrast in opposite directions on the two arms — is measured, not
  supposed.
* What is **not** established: that `blk00` does nothing. It moves contrast, measurably and
  bidirectionally. That is a real effect and arguably a more useful one than the published claim —
  **the first block is a contrast knob, and contrast is a control a user would actually want.** It
  has never been stated that way and no page claims it.
* A caveat stated rather than buried: the baselines are from `benchmark_mappa`, not from the
  `benchmark_pavimento_rumore` set Punto 7 used. The global numbers reproduce to within 0.04, so
  the substitution is not driving the result, but it is a difference.

## 5. Cheapest next step

Rewriting `blk00` as a **contrast** knob needs no renders: the variance ratios are already in
`data/texture_audit_profondita.csv` for all 28 blocks and both arms. If contrast turns out to be
monotone in depth, or to separate the first block from the tail as cleanly as the discredited grain
story did, that is a replacement claim with a better estimator behind it.
