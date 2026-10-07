# C60 — form edits vs surface edits on comic prompts: result

2026-10-07. Pre-registration `docs/prereg_comic_form_test.md` (+ amendment 1: preference question and P3
dropped before any label; + amendment 2: empty "change" answers, fixed before counting). Renders: 191 of 191,
both checks identical to the pixel (`docs/RENDERS_2026-10-07_comic_form.md`). Key committed before the labels
(`bb51975`), labels committed as downloaded (`71bee42`). Observer: Alessandro, blind to which side was edited.
Code: `experiments/comic_form_test.py --measure --tally`. Data: `data/comic_form_layout.csv`,
`data/comic_form_eye_tally_alessandro.csv`.

## Gate

Presence of damage ≥ medio on the 15 repeats: agreement 1.00 on the edited side and on both sides. The gate
passes; P4 is decided. (The "change" answer agreed exactly on 0.67 of repeats; it is not gated.)

## Results

| | FORM (10 edits, blocks 1–19) | SURFACE (10 edits, blocks 20–27) | test | verdict |
|---|---|---|---|---|
| **P1** layout r with the baseline, mean per edit | median 0.721 | median 0.837 | MWU one-sided p = 0.007 | **holds** |
| **P2** eye change (poco 0 – molto 2), empties excluded | mean 1.59 (n = 10) | mean 0.47 (n = 9) | p = 0.0002 | **holds** |
| P2 sensitivity, empties = molto | 1.59 | 0.67 (n = 10) | p = 0.002 | holds |
| **P4** edited side with damage ≥ medio | 17 / 90 = 0.19 | 71 / 90 = 0.79 | | |
| baseline side, same pairs | 0 / 90 | 0 / 90 | SURFACE: Fisher p = 9e-33 | eye sees the damage |
| FORM: difference, Newcombe 95% | 0.19 [0.11, 0.28] | | upper bound ≥ 0.10, lower > 0 | **a cost is present** |

The 12 empty "change" answers (16 showings with the repeats) are all SURFACE pairs; whole block 26 + had none
answered, being destroyed in all nine.

## Where FORM pays

The 17 damaged FORM pairs come from four of the ten edits, all labelled **medio**, none forte:
block 19 MLP + (8 of 9), block 1 attention + (4 of 9), block 17 whole + (4 of 9), block 13 whole − (1 of 9).
The other six — 2 whole −, 8 MLP +, 8 whole +, 9 attention +, 9 whole +, 18 MLP − — are at 0 of 9. Looked at
at 100% (`Text2Img/benchmark_comic_form/sheets/form_damage_100pct.png`, fisherman, seed 1618033): the damage is
not the late blocks' grain; it sits in flat areas — the sky turns into blotchy flat patches under block 19 MLP +
and into rectangular blocks under block 1 attention +. Block 19 MLP + was clean on the C59 prompts and is the
most damaged FORM edit here: its cost depends on the prompt.

## What this changes

* **The lead of the C59 addendum becomes a claim** (pre-registered, new prompts and seeds, blind): on comic and
  cartoon prompts at ±0.35, these edits in blocks 1–19 change the picture more (P1, P2) and damage its surface
  far less (0.19 vs 0.79) than edits in blocks 20–27.
* **"Every push costs" (page 05) is not overturned by this test.** By the rule written before, the FORM set
  as a whole carries a detectable cost. What the test shows is that the cost is **edit-specific and
  prompt-specific**, not universal: six of the ten FORM edits produced no damage ≥ medio in 54 pairs, and the
  baseline sides none in 180. That six edits come out clean was not a pre-registered prediction; it is a
  descriptive reading and the next test to run if wanted (those six, new prompts, the same rule).
* Limits: one observer, who also chose the FORM set (in C59); one dose; three prompts, all illustration.
