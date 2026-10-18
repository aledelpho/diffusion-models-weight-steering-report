# Pre-registration C99 — do minimal text-encoder perturbations flip the same fragile places as minimal image-model edits?

Written 2026-10-18 by Claude, **before any C99 render.** Approved by Alessandro the same day. Follows C97
(`docs/watersheds_origin_result.md`): five minimal edits of the image model flip the same places in 12 of 12 cells,
prompt micro-changes hit them too (0.488), and the places follow the content, not the starting noise. The text
encoder's *weights* were never touched at minimal dose.

## Design (48 renders + 2 gates)

The same 12 cells as C97: `P3_archerforest` and `D1_dwarf_paladin` × seeds 3141592, 2645751, 1618033, 2718281,
3316624, 4123105. The C97 bases and image-model edits W1–W5 are reused. Four new perturbations per cell, through
`Krea2ConditioningPush` (as C72/C79; variant `real` reproduces a text-encoder edit bit for bit, C79 gate):

* `T1` — text encoder layer 6 MLP × (1 + 0.004) (about one bf16 step on its three matrices), variant `real`;
* `T2` — layer 14 MLP × 1.01, variant `real`;
* `T3` — layer 28 MLP × 0.99, variant `real`;
* `T4` — a random push with no weight changed: variant `token` (independent Gaussian noise per token and tap, noise
  seed 99), scaled per tap to the push of `T1`.

**Gates:** the archer at 3141592 and the dwarf at 2645751 rendered with variant `zero` through the same workflow must
equal the C97 bases pixel for pixel.

## Measures (as C97)

Δ = max over RGB of |perturbed − base|; 16-pixel patches; log(1 + mean Δ²); partial correlation after a linear
regression on log(1 + base texture); the one-pixel jitter covariate of C97 amendment 1 reported alongside.

## Rules (fixed now)

1. **Q1 — the same places (primary).** Per cell and per T, partial correlation between the T map and the mean map of
   C97's W1–W5. *Supported* if the median over the 48 values is ≥ 0.30; *refuted* if ≤ 0.10; otherwise inconclusive.
2. **Q2 — the text-encoder perturbations agree among themselves (secondary).** Per cell, median partial correlation over
   the 6 pairs of T1–T4; *agree* if ≥ 0.30 in ≥ 9 of 12 cells.
3. **Reported:** Q1 for T4 alone (a random push of the conditioning, no weights); size of the changes (mean Δ) of T
   against W; Q1 and Q2 with the jitter covariate.

**Tool rule.** Q1 supported: fragility is a property of the picture, whatever half of the model is perturbed; one map of
fragile places serves every kind of edit. Refuted: each half has fragile places of its own.

## Limits

Doses differ between the halves (one bf16 step or 1% against C97's 0.4–1%); `T4` follows `T1`'s size, which may be
tiny; the ancestral noise is not controlled (as C97).

Script: `experiments/watersheds_te.py`. Directive: `docs/directives_antigravity_watersheds_te.md`.
