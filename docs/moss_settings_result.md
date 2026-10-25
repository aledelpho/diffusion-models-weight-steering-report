# MOSS-S result — neither 25 steps nor the turbo LoRA passes; the edit doses were too small for the test to decide

2026-10-25. Pre-registration `docs/prereg_moss_settings.md`; renders and numbers by Antigravity
(`docs/RENDERS_2026-10-25_moss_settings.md`, 1fccab3): 84 of 84, LoRA loaded on 168 tensors (42 layers × 4), no key
missing. Times per picture: T8 19 s, E25 84 s, R50 163 s.

## Verdicts (as pre-registered)

| | S1 plain close to R50 (≤ 0.069) | S2 edits proportional (Spearman ≥ 0.80, ratio 0.5–2) | decision |
|---|---|---|---|
| E25 | **PASS**, median D 0.031 | **FAIL**, Spearman 0.47, ratio 0.90 | not a replacement |
| T8 | FAIL, 0.142 (expected, reported) | **FAIL**, Spearman 0.48, ratio 1.57 | not used |

Seed floor (median D between the two seeds): R50 0.137, E25 0.180, T8 0.105. **By the rule, R50 stays.**

## Why S2 could not decide (read after the rules, not pre-registered)

Every edit moved the picture very little: D to the plain picture 0.001–0.036 at R50 (median about 0.006), against a
seed floor of 0.137. At d = 0.10 and 0.30 on one layer, MOSS barely changes. A ranking of 16 distances that small is
dominated by noise, so a Spearman of 0.47 says little about whether the settings treat edits alike. The doses were
chosen too small for this test; S2 should be re-run at doses that move the picture (D 0.05–0.30).

Two exploratory observations: E25's plain pictures are close to R50's (S1), and the turbo makes the rally much more
sensitive (D up to 0.083 at d = 0.10 on DiT layer 20, against 0.008 at R50) but not the dwarf: the distilled model does
not respond to edits like the reference, at least on that prompt.

## What follows

* R50 remains the setting for MOSS (163 s per picture).
* A re-run of S2 at larger doses (MOSS-S2, about 70 min) would show whether E25, at half the time, treats edits like
  R50. The turbo stays out unless that re-run says otherwise.
* First sensitivity fact for MOSS: one MLP at d ≤ 0.30 moves the picture by at most about a quarter of a seed change.
