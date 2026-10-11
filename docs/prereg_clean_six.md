# C63 — are the six "clean" middle-block edits really free? Pre-registration

2026-10-11. Written before any render. Asked for by Alessandro. Follows C60 (`docs/comic_form_result.md`): of
the ten middle-block (FORM) edits, six produced no damage of medium or stronger in 54 pairs. That was a
descriptive reading after the fact; this test asks it of new pictures.

## Edits (fixed by the C60 result, not by hand)

* **CLEAN (6):** block 2 whole −, block 8 MLP +, block 8 whole +, block 9 attention +, block 9 whole +,
  block 18 MLP − — the C60 FORM edits at 0 of 9 damaged pairs.
* **CONTROL (2):** block 22 MLP + and block 27 MLP + — C60 SURFACE edits damaged in 8 and 9 of 9 pairs. A
  positive control: on these prompts the eye must still see damage where it is expected.
* Dose ±0.35, Real Value, `granular_json` (whole = all eight matrices).

## Renders

Four illustration prompts never used in C59 or C60 (the sets the six were chosen on): `C3_fox` (cartoon),
`F1cartoon_lighthouse` (cartoon), `E5_childrensbook` (children's book), `P5_comic_panels` (a comic page in four
panels). Three new seeds: 1325719, 2193847, 3047581. 8 edits + baseline × 4 prompts × 3 seeds = 108, plus one
check first: the elf at seed 1618033 with block 8 MLP +0.35 must equal its C60 file to the pixel; if not,
nothing else runs. 109 renders, about 1 h. Plan `data/clean_six_plan.csv`, code `experiments/clean_six_test.py`.

## Eye test (built after the renders; key committed before any label)

As C60, without the preference question: 96 pairs (edit vs its own baseline, side random), CLEAN and CONTROL
mixed and shuffled, 10 repeats unannounced. Per pair: surface damage on A and on B (none / slight / medium /
strong), and how much the picture changed (little / medium / much). Damage = medium or stronger.

## Predictions

* **Gate 1 (the eye sees damage here):** CONTROL edited sides damaged more often than their baseline sides,
  Fisher one-sided p < 0.05 (24 pairs).
* **Gate 2 (self-agreement):** presence of damage ≥ medium agrees on ≥ 0.8 of the repeats.
* **H (the six are free):** over the 72 CLEAN pairs, the upper end of the 95% Newcombe interval of
  (edited-side rate − baseline-side rate) of damage ≥ medium is **below 0.10** → "no detectable cost". If the
  lower end is above 0 → "a cost". Otherwise undecided. Both gates must pass for H to be read.
* Per edit (descriptive): damaged pairs out of 12, and the change score.

## What the result can change

H "no detectable cost" with both gates → a claim on results page 29: six named middle-block edits at ±0.35
carry no detectable surface cost on illustration prompts — the basis for a comic preset to be tested next.
Otherwise → reported; the C60 reading stays descriptive. Limits written now: one observer (who chose the C59
edits the six came from), illustration only, one dose; 72 pairs can exclude a cost above about 5–10%, not a
small one.
