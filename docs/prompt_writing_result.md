# C45 result — the way a prompt is written does not change what a block does; the subject does. Pre-registered verdict: inconclusive

2026-10-04. Pre-registration: `prereg_prompt_writing.md` (+ amendment 1). Code:
`experiments/analyze_prompt_writing.py`, unchanged since commit b030123 (before any render).
Data: `data/prompt_writing_style_features.csv`, `data/prompt_writing_arms.csv`,
`data/prompt_writing_test.csv`. Eye pass `data/prompt_writing_eye_alessandro.csv`, deposited
(bf7b92e) before the test ran. Renders 401/401, REPRO pixel-identical.

## 1. The eye

Alessandro, verbatim: *"C45 per me è sempre Sì"* — for every arm, on both subjects, the block
does the same thing across the four writings, and the same thing after the content change.

## 2. Pre-registered rule

Scored arms (change larger than what the writing alone does to the baseline, size >
1.15): **12 of 24** — blk00 ±, blk09 −, blk12 +, blk13 +, blk15 +, blk17 ±, blk19 +, blk23 +,
blk27 ±.

| condition | needed | result | |
|---|---|---|---|
| median (A_writing − A_seed) | ≥ −0.10 | **−0.04** | met |
| A_writing > A_subject | ≥ 75 % of arms | **100 %** (12/12) | met |
| A_writing > A_content_small | ≥ 60 % of arms | **0 %** (0/12) | not met |

**Verdict by the rule: inconclusive.** Not "supported", because the third condition fails
completely.

## 3. What the three numbers say

- **Writing ≈ seed.** Rewriting the prompt (reordering, tags, synonyms) changes the direction
  of a block's effect no more than changing the seed does. Tags alone against the original
  (`W1_vs_W3_tags`) behave like the other writings. This replicates `prompt_order` on a second
  subject and on writings that change what the text encoder receives.
- **Subject ≫ writing.** The same arm points in very different directions on the elf and on
  the canoe (A_subject 0.00–0.52 against A_writing 0.45–0.92 on the scored arms). What the
  picture contains decides what the block does to it.
- **The small content change disturbed the effect *less* than rewriting.** A_content_small
  (W1 against C1, identical wording except the changed object) is higher than A_writing on
  every scored arm. The reason is visible in the baselines: C1 is closer to W1 in layout
  (L-channel r 0.68–0.76) than the rewritings are (0.48–0.76). Changing one object kept the
  picture; rewriting the prompt moved pose and framing. The pre-registration assumed the
  opposite ordering, and the third condition was built on that assumption.

## 4. Reading Alessandro's claim against this

*"Moving the weights gives similar results when the prompt describes the same content; the
structure of the text does not matter more than the content."*

- First half: **supported** by eye (24/24 arms) and by numbers (writing ≈ seed).
- Second half: **supported for a large change of content** (another subject, 12/12 arms),
  **not for a small one** (a different gauntlet or sleeper changes the block's effect less
  than a rewrite). Stated plainly: the text's structure matters about as much as the seed, and
  less than the subject; a one-object change matters less than either.
- The style features are partly sensitive to layout, so "how close two edits are" mixes the
  block's effect with how similar the two pictures were to start with. This favours C1
  (closest layout) and penalises the rewrites; it does not explain A_subject.

## 5. Limits

Two subjects. On S2 (lotus canoe) the arms are about half as strong as on S1 and only 12 of
24 arms pass the size threshold over both. One seed pair.
