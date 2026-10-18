# C99 result — minimal text-encoder perturbations flip the same fragile places

2026-10-18. Pre-registration `docs/prereg_watersheds_te.md` and script `experiments/watersheds_te.py` (607d5cb, before
any render). Renders by Antigravity (`docs/RENDERS_2026-10-18_watersheds_te.md`): 50 of 50; both gates (variant `zero`
against the C97 bases) max abs diff 0, re-checked by Claude. Output `data/watersheds_te_tests.csv`.

## Verdicts

| rule | value | verdict |
|---|---|---|
| **Q1** — the four text-encoder perturbations hit the image-model fragile places of C97 | median partial r **0.715** over 48 (bar 0.30) | **supported** |
| **Q2** — they agree among themselves | median ≥ 0.30 in **12 of 12** cells | agree |
| T4 alone — a random push of the conditioning, no weight changed (reported) | median **0.724** | — |
| size of changes, median mean Δ, image-model W / text-encoder T (reported) | 5.33 / 5.24 | comparable |
| with the one-pixel jitter covariate (reported) | 0.714 / 12 of 12 | unchanged |

## Reading

Touch the text encoder's layer 6, 14 or 28 by about 1% — or add a tiny random push to the conditioning without touching
any weight — and the same places of the picture flip as when the image model's blocks are touched, more consistently
than the image-model edits agree among themselves (0.715 against C97's 0.35–0.64). Together with C97 (prompt
micro-changes hit them too, the starting noise does not set them): the fragile places are a property of the picture
being drawn — its weakly bound details — not of the part of the model that is perturbed.

## Limits

As C97: two prompts, six seeds, ancestral noise not controlled; T4's size follows T1, so the four perturbations are of
similar, small size.
