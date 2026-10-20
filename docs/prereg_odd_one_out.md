# Pre-registration C106 — can the eye sort pictures by the edit that made them? (two pairs and an odd one, no renders)

Written 2026-10-20 by Claude, **before the page and before any label.** Proposed by Alessandro: "if you gave me five
pictures, two pairs made with the same preset and one with a different preset, same prompt, I would tell the groups
apart with some ease". C104 asked him to judge groupings we gave him; here he has to **find** them.

## 1. Design

* **Trial:** five pictures of the same prompt — perturbation A at seeds s1 and s2, perturbation B at the **same** seeds
  s1 and s2, perturbation C at a third seed s3 — in random order. Alessandro assigns each picture to *gruppo 1*,
  *gruppo 2* or *sola*. Sorting by seed (A-s1 with B-s1) gives a wrong answer; sorting by perturbation gives the right
  one.
* **Chance:** five pictures can be split into two pairs and a single one in 15 ways: an exact answer by chance has
  probability **1/15**; the single picture by chance 1/5.
* **Material, no new renders:**
  * **TE set** — C103's test renders (`benchmark_te_depth_control2`): text-encoder edits L09, L26 and random pushes
    R09a/b/c, R26a/b/c, matched on picture change (D ≈ 0.3); seeds 2645751, 3316624, 2718281; prompts D1, S1, C4 (8
    perturbations) and P5 (L26, R26a/b/c). 4 trials per prompt: **16 trials**.
  * **DiT set** — the September stage-5 renders (`benchmark_stage5/renders`): image-model presets preset_pos,
    preset_neg, preset_half, blockshuf_pos, blockshuf_neg, rand_pos, rand_neg; seeds 42, 777, 1337, 9999, 4242145;
    prompts G1–G6. 2 trials per prompt: **12 trials**.
  * Perturbations and seeds drawn at random (seed 20201), A ≠ B ≠ C; 4 trials repeated for test–retest; order random;
    nothing on the page says which set a trial comes from.
* **Page:** `Text2Img/occhio_C106.html`; each picture can be opened full screen; export `odd_one_out_labels.csv`.

## 2. Rules (fixed now)

1. **The eye sorts by perturbation:** exact answers ≥ 50% of the 28 first showings and binomial p < 0.001 against 1/15.
   Reported separately for the TE set and the DiT set (each: exact ≥ 40% and p < 0.01).
2. **Not by seed (reported):** share of answers equal to the seed partition ({A-s1, B-s1}, {A-s2, B-s2}); chance 1/15.
3. **Reported:** single picture found (chance 1/5); pairs correct; per kind of A–B pair (an edit against a random push;
   two random pushes of the same layer; for the DiT set, the same preset at different strength or sign against
   different families); test–retest.

**Tool rule.** Rule 1 holds: each edit has a signature the eye can recognise across seeds, so presets are reproducible
looks, not noise. It fails: the per-seed consistency of C104 is not strong enough to recognise an edit without being
told which pictures belong together.

## 3. Limits

Alessandro has seen many of these pictures; the stage-5 presets are his own; the TE set's R09a was under-matched in
C103; 28 trials.

Script: `experiments/odd_one_out.py`.
