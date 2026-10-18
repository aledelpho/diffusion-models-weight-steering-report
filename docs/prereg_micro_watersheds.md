# Pre-registration C96 — micro-watersheds: do minimal edits flip the same small regions of a picture?

Written 2026-10-18 by Claude, **before any computation on these renders for this question.** No new renders.
Hypothesis by Alessandro (2026-10-18): every picture holds many small details balanced between two solutions
("argini"); the half-formed hood (page 22) is the visible case of a property found at every scale. Minimal edits
should then not change pixels a little everywhere, but flip irregular patches, and the same patches whatever the edit.

## 1. Data (fixed now)

The archer `P3_archerforest`, seed 3141592 (the hood seed), image model edits:

* **Small set (primary):** C56 ladder `Text2Img/benchmark_hood_threshold`, blocks 00, 10, 20, 23, both signs, doses
  0.010, 0.020, 0.040 (24 renders), plus C55 `Text2Img/benchmark_null_patch` N3 and N4 (block 27 ±0.004, one bf16
  step on every weight) — 26 edits.
* **Larger set (reported):** the same ladder at 0.080 and 0.160 (16 renders).
* **Reference:** the ladder's baseline (checked pixel-identical to C55 N0 before use; if not, stop).

Change map of an edit: Δ(x) = max over RGB of |edit − baseline| at pixel x, in 0–255.

## 2. Predictions and rules

**T1 — flips, not a uniform shimmer.** For each edit, the share of total squared change carried by pixels with
Δ ≥ 32. *Supported* if the share is ≥ 0.50 in ≥ 2/3 of the small edits; *refuted* if ≤ 0.20 in ≥ 2/3.

**T2 — the same places (primary).** The picture is cut into 16 × 16-pixel patches (the image model's token size:
8× VAE × 2×2 patch). Per edit, the patch change energy is the mean Δ² in the patch. Texture of the baseline per patch:
mean Sobel gradient magnitude of its luminance. For every pair of small edits, the Pearson correlation of log(1 + patch energy) **after removing texture** (each
vector regressed linearly on log(1 + texture), residuals correlated). *(Written so after the selftest showed that a
Spearman correlation over all patches is dominated by the ordering of the near-zero shimmer and misses sparse flips;
changed before any real data was read.)* *Supported* if the median partial correlation over all pairs is ≥ 0.30; *refuted* if ≤ 0.10; between:
inconclusive. Reported: the same without the texture control; pairs of opposite sign; pairs of different blocks.

**T3 — two solutions (secondary).** Patches that flip (patch mean Δ ≥ 32) in ≥ 25% of all 42 edits are "recurring".
For each, the patch's pixels across the baseline and the 42 edits are reduced to their first principal component, and
Sarle's bimodality coefficient is computed. *Supported* if ≥ 50% of recurring patches have a coefficient > 0.555
(the value of a uniform distribution); otherwise not supported. Reported only if there are at least 10 recurring
patches.

**Reported, deciding nothing:** size of flip regions (connected components of Δ ≥ 32, 8-connected) against the
16-pixel token grid; how the flip share and overlap grow with dose (0.01 → 0.16).

## 3. What this can and cannot say

It can say whether, on this seed, minimal edits flip the same places and whether those places hold two alternatives.
It cannot say *what decides* the places — the starting noise, the content, or the token grid. That needs other seeds
and the starting noise itself (follow-up: the same tiny edits on several seeds and two prompts, with the initial
latent noise saved on the GPU; renders, to be approved).

**Tool rule.** If T2 holds, every picture carries a map of fragile places, measurable from a few tiny edits; a tool
can show where an edit will reshuffle details by chance, and tell intended changes from incidental ones. If refuted,
incidental changes are spread and cannot be anticipated.

## 4. Limits known in advance

One prompt, one seed — and a seed chosen because it sits on a watershed, so it may be more fragile than most.
`euler_ancestral` adds noise at each step: part of what flips may be the sampler's path, not the picture.

Script: `experiments/micro_watersheds.py` (written after this file, committed with it).
