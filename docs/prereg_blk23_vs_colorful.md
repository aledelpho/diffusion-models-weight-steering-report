# Pre-registration C47 — blk23 as a saturation control, against "colorful" in the prompt

Written 2026-10-04, before any render. Scoring code: `experiments/analyze_blk23_vs_colorful.py`
(committed with this file).

## Claims under test (Alessandro)

1. blk23 is a valid saturation modifier: it moves colour in one direction, in proportion
   to the dose.
2. It can replace words such as "colorful" / "high saturation" in the prompt, with less
   unintended change of content ("concept bleeding").

What is already known (exploratory, `single_blocks_exploration_synthesis.md` §5): chroma
moves the expected way on 83 of 83 existing images; doubling the positive dose
multiplies the effect by about 2.2; no dose ladder exists on the negative side; the
text comparison has never been rendered.

## Design

Eight prompts, two seeds, eight conditions each: **8 × 2 × 8 = 128 renders.**

| prompt id | source plan | seed A (existing baseline) | seed B (new) |
|---|---|---|---|
| E1_cartoon, E3_oil, E7_sepiaphoto, C2_rally, C3_fox, C4_stilllife | `single_blocks_styles_plan.csv` | 2718281 | 4669201 |
| P3_archerforest | `single_blocks_v3_plan.csv` | 3141592 | 4669201 |
| P4_selfie | `single_blocks_v3_plan.csv` | 1618033 | 4669201 |

Prompt text: the `prompt_text` of the baseline row in the source plan, verbatim.

| cond | weights | text |
|---|---|---|
| `baseline` | none | prompt |
| `txtpos` | none | prompt + `, colorful, vivid highly saturated colors` |
| `txtneg` | none | prompt + `, muted colors, desaturated, low saturation` |
| `b23_m0.450` / `b23_m0.300` / `b23_m0.150` | slot 23 = −0.45 / −0.30 / −0.15 | prompt |
| `b23_p0.150` / `b23_p0.300` | slot 23 = +0.15 / +0.30 | prompt |

Suffix rule: strip trailing whitespace from the prompt; if it ends with `.` or `,`,
append the suffix without its leading comma, after one space; otherwise append it as
written. Settings as every single-block bench: euler_ancestral / simple, 9 steps,
cfg 1.0, 1024 × 1280, Tuner in Real Value, ResetPatcher before the Tuner.

Seed A re-renders conditions that already exist (baseline, and −0.30/+0.30 or +0.15
for some prompts): those must come out pixel-identical to the existing files and are
the bench's reproducibility check.

## Measures and decision rules

Per image against its own baseline, CIELAB at 64×80: change of mean chroma; layout
r (L channel correlation with the baseline).

- **V1 — direction.** Chroma falls strictly along −0.45 → −0.30 → −0.15 → 0 → +0.15 →
  +0.30 in at least 14 of 16 cells: supported; otherwise refuted.
- **V2 — proportion.** Median of Δchroma(−0.30) / Δchroma(−0.15): within 1.6–2.4
  "approximately linear"; outside, "monotone, not linear".
- **T1 — against the text.** In each cell, the blk23 dose giving the same chroma gain as
  `txtpos` is found by linear interpolation along the ladder, and the layout r at that
  dose is interpolated the same way. **blk23 better** if its layout r is higher in ≥ 75 %
  of scored cells and the median difference is ≥ 0.05; **text better** if blk23 wins in
  ≤ 25 %; otherwise no clear difference. Cells where the text does not raise chroma, or
  raises it beyond the ladder, are counted and reported separately (the first case
  would itself be a result: the words do not do what they say).

## The eye

For each cell, one row: baseline · txtpos · the blk23 rung closest in chroma to txtpos ·
b23_m0.450 · txtneg · b23_p0.300. Alessandro marks, per cell, which of txtpos and the
blk23 rung changed the content more (objects, faces, composition, style), before the
numbers are shown. If eye and T1 disagree, the disagreement is reported.

## Limits

One appended phrase per direction; other wordings ("vibrant", "saturated palette", at
the start of the prompt) may behave differently. E7_sepiaphoto puts the text in
conflict with the style on purpose.

## Amendment 1 (2026-10-04, after the renders, before any C47 number was computed)

The eye page (`experiments/build_blk23_colorful_eye_page.py`) shows the desaturating side as
well: for each cell, `txtneg` against blk23 +0.15/+0.30, with the same two questions. The
decision rules are unchanged; the extra marks are reported, not scored. Renders: 128/128
present, reproducibility 26/26 pairs identical (`RENDERS_2026-10-04_blk23_colorful.md`).
