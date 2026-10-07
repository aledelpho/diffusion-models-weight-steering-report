# C60 — form edits vs surface edits on comic prompts: pre-registration

2026-10-07. Written before any render. Asked for by Alessandro to test the post-hoc lead of the C59 eye pass
(`docs/split_atlas_eye_result.md`, addendum): the edits he praised for the comic change the image more than
the edits spoiled by noise, and do it without damaging the surface. Also tests, on these edits, the
general statement of notebook page 05 that every push costs fine texture.

## Edits (fixed by rule, not by hand)

* **FORM set (10):** the sheets praised for the comic in the C59 eye pass (rule in the addendum):
  block 1 attention +, 2 whole −, 8 MLP +, 8 whole +, 9 attention +, 9 whole +, 13 whole −, 17 whole +,
  18 MLP −, 19 MLP +.
* **SURFACE set (10):** drawn with rng 60 from the 16 C59 sheets labelled noise ≥ medio with no structural
  class, block ≥ 20, not marked "non in tutti e tre": 20 whole −, 22 MLP +, 22 whole +, 23 MLP +, 26 MLP +,
  26 whole +, 27 attention −, 27 attention +, 27 MLP +, 27 whole +.
* Dose ±0.35, Real Value, through `granular_json` (whole = all eight matrices; shown identical to the
  pixel to the vector path in C59).

## Renders

New prompts, none used in C59: `P02` (botanist, western comics), `P1_elfbrawler` (western comics),
`F1cartoon_fisherman` (cartoon) — two comics and one cartoon, to see if the lead survives a change of style
within illustration. New seeds 1618033, 1414213, 2236067. 20 edits + baseline × 3 prompts × 3 seeds =
189, plus 2 checks first (split block 19 MLP + and whole block 8 + via granular, both at the C59 cell, each
must equal the C59 file to the pixel; if either fails nothing else runs). 191 renders, about 1 h 50 min.
Plan `data/comic_form_plan.csv`, code `experiments/comic_form_test.py`.

## Eye test (built after the renders; key committed before any label)

180 pairs (edit vs its baseline, same prompt and seed), left/right random, form and surface mixed and
shuffled; 15 pairs repeated unannounced. Per pair:

1. **Preference for this style:** A / B / uguale.
2. **Surface damage** (grana, chiazze, retino, collasso), for A and for B separately: nessuno / lieve /
   medio / forte.
3. **How much the picture changed between A and B:** poco / medio / molto.

Only medio and stronger counts as damage (C59: lieve did not reproduce).

## Predictions

Analysis unit for P1–P3: the edit (10 vs 10), each edit's value averaged over its 9 pairs, one-sided
Mann–Whitney, α = 0.05.

* **P1 (measure):** mean layout r (C47 metric) of FORM edits lower than of SURFACE edits.
* **P2 (eye, change):** mean change score (poco 0, medio 1, molto 2) higher for FORM than SURFACE.
* **P3 (eye, preference):** share of non-tie pairs where the edit is preferred higher for FORM than
  SURFACE. Reported alongside, not tested against 50%: the pooled share for FORM (if FORM edits are
  preferred over the baseline in most pairs, that is a separate, descriptive result).
* **P4 (the cost, the question about page 05):** damage ≥ medio on the edited side.
  * SURFACE: rate higher than on the baseline sides (Fisher one-sided, pairs pooled, α = 0.05) — a check
    that the eye sees the damage this test is about.
  * FORM: **no detectable cost** is declared if the upper end of the 95% Newcombe interval for
    (FORM edit rate − baseline-side rate) is below 0.10. If it is above, the cost is not excluded; if the
    lower end is above 0, FORM edits do carry a cost.
* **Gate:** if presence agreement for damage ≥ medio on the 15 repeats is below 0.8, P4 is reported as not
  decided.

## What the result can change

* P1–P3 hold → the lead becomes a claim: on comic and cartoon prompts, edits in blocks 1–19 change form
  and light more than late-block edits, and are preferred more, at this dose.
* P4 FORM "no detectable cost" → evidence against the general wording of page 05's `cost-grows-with-depth`
  ("pushing any block costs fine texture"); the depth gradient would stand. Changing that claim's status
  stays Alessandro's decision.
* Limits written now: the FORM set was chosen on the eye of the same observer who will judge; new prompts
  and seeds guard against overfitting to images, not against the observer's taste. One observer.
