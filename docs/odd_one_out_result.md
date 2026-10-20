# C106 result — the eye sorts pictures by the edit that made them, not by the seed

2026-10-20. Pre-registration `docs/prereg_odd_one_out.md` (08a7b0e). No renders (C103's text-encoder renders and the
stage-5 image-model presets). Labels committed as downloaded (aff6f26; 32 trials). Rules: `experiments/odd_one_out.py
--rules` → `data/odd_one_out_tests.csv`.

## Verdicts

| rule | value | verdict |
|---|---|---|
| **1 — all trials** | exact sorting **20 of 28 = 0.71**; binomial p 5.5e-18 against 1/15 | **the eye sorts by perturbation** |
| 1 — text-encoder set | 11 of 16 = 0.69; p 3.7e-10 | **the eye sorts by perturbation** |
| 1 — image-model presets | 9 of 12 = 0.75; p 4.8e-09 | **the eye sorts by perturbation** |
| 2 — answers equal to the seed partition | **0 of 28** (chance 1/15) | — |
| 3 — single picture found | 20 of 28 (chance 1/5); pairs correct 45 of 56 | — |
| 3 — test–retest | 4 of 4 same outcome | — |

By kind of A–B pair (reported): image-model presets of different families 6/9, same family (sign or strength) 3/3;
text-encoder edit against random push 2/2, two random pushes of the same layer 4/7, other 5/7.

## Reading

Five pictures of one prompt, two made with perturbation A, two with B at the same two seeds, one with C: Alessandro found
the exact grouping in 71% of trials where chance gives 7%, and never grouped by seed, although every trial was built so
that sorting by seed (same composition) was the tempting wrong answer. A fixed perturbation — an image-model preset, a
text-encoder edit or a random push of the text encoder — leaves a signature the eye recognises across seeds without
being told what belongs together. This confirms C104 in a stronger, unprompted form.

## Exploratory (after the rules)

The failures cluster where the trial holds two or three **random pushes at layer 26**: all three were R26 in T06 and T20
(both failed); T08 and T21 (failed) paired two R26 pushes or an R26 with another random push; whenever the L26 edit was
one of the three (T10, T13, T25), the trial succeeded. Random pushes at layer 26 look more alike to the eye than other
pairs; this matches, at least in part, DINOv2's "shared direction" reading at layer 26 in C103 (which C104's grouping
question did not support). On the image-model side, failures include a preset against its own half-strength version as
the odd one (T04).

## Limits

28 trials; Alessandro knows many of these pictures and the stage-5 presets are his own (no labels were shown);
R09a was under-matched in C103.
