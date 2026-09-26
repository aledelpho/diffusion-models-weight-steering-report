# Observer prediction — sign opposition in the extracted traits

**Recorded**: 2026-09-26, **before** the statistic below was computed, and before Alessandro had
seen any feature-level +/− comparison. Recorded by the analyst at his dictation.

## 1. The prediction, verbatim

> «Io prevedo almeno un effetto "opposto" nella maggior parte di loro (più del 80%), in almeno un
> tratto estratto, rispetto al baseline.»

## 2. How it is operationalised, fixed now

Corpus: `benchmark_qkvo_atlas/renders`, features in `data/style_features_qkvo.csv` (433 rows, 23
traits). Baseline for a scene/seed = the `normscales_all` control, which is byte-identical to an
unperturbed render (exact zero displacement, verified in `experiments/qkvo_analyze.py`).

For one pair (cell, scene, seed) and one trait `t`:

```
opposed(t)  iff  sign( t(+) - t(base) ) != sign( t(-) - t(base) )   and both differences nonzero
```

**Prediction O1 (his, as stated)**: more than **80%** of the pairs have `opposed(t)` true for **at
least one** trait `t`.

Two granularities are reported, because "la maggior parte di loro" is ambiguous between them:
per **pair** (192 units: 8 cells × 8 scenes × 3 seeds) and per **cell** (8 units, a cell counting
as opposed if the majority of its 24 pairs are).

## 3. The analyst's objection, also recorded before computing

**O1 as stated is nearly unfalsifiable and will almost certainly "pass".** With 23 traits, if each
trait opposed independently with probability 1/2, the chance that *none* of the 23 opposes is
2⁻²³ ≈ 1.2 × 10⁻⁷. So "at least one trait out of 23" is expected in ~100% of pairs under pure noise.
A pass tells us nothing.

The informative version, which is therefore reported alongside it and is the quantity the analyst
will argue from:

**O1′**: the **number of opposed traits per pair**, out of the traits whose two differences both
exceed the seed-to-seed noise of that trait, compared against the chance expectation of 50%.

* If the blocks are **linear knobs**, nearly every above-noise trait should oppose → fraction → 1.
* If the perturbation is **sign-blind**, almost none should → fraction → 0.
* Chance, with no relation between the arms, is **0.5**.

The analyst's frozen expectation for O1′, deposited here before computing: the fraction of opposed
above-noise traits is **below 0.5** — i.e. the two arms agree more often than they disagree — because
the pixel decomposition of the same day (`prereg_sign_decomposition_pixels.md`) found the sign-blind
share of the image change to be about two thirds. Falsified if the fraction exceeds 0.60.

This document is deposited before either number is read.
