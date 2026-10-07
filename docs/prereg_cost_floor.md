# C61 — does every push cost fine texture? Pre-registration

2026-10-07. Written before any render. Asked for by Alessandro: an attempt to overturn the general wording of
notebook page 05's claim `cost-grows-with-depth` — "Pushing any block costs fine texture, in either direction,
and the cost grows the closer the block sits to the output."

## What page 05 found, and where it is open

Page 05 (pre-registered, 2026-09-20): every whole block at ±0.200, prompts P01 and P02, seeds 42, 777, 1337;
fine texture HF = std(gray − GaussianBlur σ 1.5); per block common mode c = √(r⁺ r⁻). Mean c 0.978, 23 of 28
blocks below 1, r = −0.659 with depth, a step at block 23. From `data/punto7_blocks.csv`: geometric mean of c
over blocks 1–22 is **0.989** (a 1.1% cost), over 23–27 **0.932**. Each block rests on 6 renders per sign.

Since then: C59 measured whole blocks at ±0.35 with the same HF and found c below 1 in only 13 of 28 blocks
(3 cells each); the eye found the late blocks and block 0 noisy and blocks 2, 3, 5, 7–9 clean; C60 found the
cost of individual edits to be edit- and prompt-specific. Page 05 itself notes no cost at D = 0.050. The open
question is whether the 1.1% in blocks 1–22 is a real, general cost or a small-sample figure on two prompts.

## Design

* **Edits:** every whole block 0–27 at +0.200 and −0.200 — page 05's dose and path (`vectors_override`,
  Real Value).
* **Prompts:** P01 and P02 (page 05's own, western comics) and two photographic prompts, S1_rally and
  P4_selfie — to test the "any" in the claim and Alessandro's idea that illustration is more malleable than
  photography.
* **Seeds:** four new, 1259921, 1732050, 2645751, 3162277. 28 × 2 × 4 × 4 = 896 edits + 16 baselines.
* **Check first:** P01, seed 42, block 9 at +0.200 must equal page 05's own render
  (`benchmark_profondita/renders`) to the pixel. If not, nothing else runs.
* 913 renders, about 8 h 40 min. Plan `data/cost_floor_plan.csv`, code `experiments/cost_floor_test.py`.

## Measure (page 05's, unchanged)

HF with OpenCV (`GaussianBlur(gray, (0,0), 1.5)`), r± = HF±/HF_baseline at the same prompt and seed,
c = √(r⁺ r⁻). The unit of analysis is the **cell** (prompt × seed, 16 cells), because the blocks of a cell share
one baseline. For each cell, G₁ = geometric mean of c over blocks 1–22, G₂ = over blocks 23–27.

## Predictions and decision rules

* **Gate (positive control):** mean log G₂ over the 16 cells below 0 with one-sided t p < 0.05, and mean G₂ <
  0.97. If the bench cannot see the late-block cost page 05 saw, H1 is not readable and nothing is overturned.
* **H1 (the attempt):** mean log G₁ over the 16 cells, with t intervals.
  * **"No cost" (page 05's general wording overturned for blocks 1–22 at this dose):** the 90% interval lies
    inside [log 0.99, log 1.01] **and** the 95% interval includes 0. This excludes page 05's 0.989.
  * **"Cost replicated":** the 95% interval lies entirely below 0.
  * Otherwise **undecided**.
* **H1 by family (secondary, same rules):** comic cells (8) and photographic cells (8) separately; and the
  difference comic − photo in mean log G₁ (Welch, two-sided) for Alessandro's malleability idea.
* **Per block (descriptive only, no verdict):** mean c and 95% interval for each of the 28 blocks.
* **Eye (needed for an overturn):** after the renders, a blind pair test (edit vs baseline, side random):
  120 pairs drawn at random from blocks 1–22, 40 from blocks 23–27, 15 repeats; damage on each side, nessuno /
  lieve / medio / forte. "No visible cost" for blocks 1–22 if the upper end of the 95% Newcombe interval of
  (edit rate − baseline-side rate) of damage ≥ medio is below 0.05. Positive control: blocks 23–27 rate above
  baseline (Fisher one-sided p < 0.05). Gate: presence agreement on repeats ≥ 0.8. The page and its key are
  committed before any label.

## What the result can change

* Gate passes, H1 "no cost" and the eye "no visible cost": the proposal to Alessandro is to split the claim —
  the depth step **holds**, "pushing any block costs" **overturned** for blocks 1–22 at ±0.200. Changing a
  published status is his decision.
* H1 "cost replicated": page 05 holds, strengthened on new seeds and prompts.
* Undecided: reported as such; no change.
* Limits written now: one dose; four prompts; the eye test has one observer; HF is page 05's measure of
  fine-texture loss and does not see added noise (C59), which is why the eye is required for an overturn.
