# Pre-registration C98 — micro-watersheds on existing renders: a single leaf, 3 prompts × 3 seeds, 12 small edits each

Written 2026-10-18 by Claude, **before any computation on these renders for this question.** No new renders. A
replication of C96 on pictures nobody has looked at for this question, while C97 renders.

## Data (fixed now)

`Text2Img/benchmark_colour_binding/renders` (C49–C51 colour-binding corpus): prompts `LP` (a single purple leaf), `LG`
(green), `LN` (no colour word) — the same sentence otherwise, a leaf centred on plain light grey, macro photograph —
at seeds 42, 777, 1337. Per (prompt, seed) cell: the baseline `<P>_baseline_krea2_seed<s>` and 12 edits at dose 0.050
(`Block_1`…`Block_6` × pos/neg, the tuner's six block groups). 9 cells. The 0.200 edits are reported only.

A leaf on a plain background is a hard case for the hypothesis: few optional details, little texture.

## Measures (as C96/C97)

Δ = max over RGB of |edit − baseline|; 16 × 16 patches; log(1 + mean Δ²) per patch; partial correlation = Pearson
after a linear regression on log(1 + baseline Sobel texture).

## Rules

1. **R1 — replication (primary).** Per cell, the median partial correlation over the 66 pairs of the 12 edits.
   *Replicated* if ≥ 0.30 in ≥ 7 of 9 cells; *not replicated* if ≥ 0.30 in ≤ 3; otherwise mixed.
2. **R2 — one word of the prompt hits the same places (secondary).** At each seed, the change between two baselines that
   differ by the colour word (LP vs LN, LG vs LN) against the mean map of the 12 edits of LN at that seed (partial
   correlation, LN texture). *Supported* if the median of the 6 values is ≥ 0.30; *refuted* if ≤ 0.10.
3. **Reported:** T1 (share of squared change at Δ ≥ 32); the same at 0.200; same-seed vs different-seed similarity of
   fragility maps across prompts (not a test of noise against content here: the three prompts draw nearly the same
   picture at a seed).

Script: `experiments/watersheds_leaf.py`.
