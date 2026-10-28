# C113 result — dose ladders of four encoder edits: where each one is right, where it breaks

Pre-registration: `docs/prereg_te_dose2.md` (+ amendments 1–2). Renders: `docs/RENDERS_2026-10-28_te_dose2.md` (192 new,
80 reused from C112; gate pixel-identical). **Amendment 2: the blind pass was abandoned before any label; rules 0–2
were not applied.** This is a descriptive calibration: Alessandro's non-blind marks on the full sheets
(`data/te_dose2_marks.csv`, page `experiments/te_dose2_marks_page.py`) next to DINOv2 (`data/te_dose2_dino.csv`).

## Marks (blue tree / helmet — identical on the two prompts in all 16 rows)

| edit | level 1 | level 2 | level 3 | level 4 | usable window |
|---|---|---|---|---|---|
| E06 | 0.4 raise | **0.8 right** | 1.2 lower ("not too much") | 1.6 broken | 0.8 to just under 1.2 |
| E14 | 0.4 raise | **0.8 right** | 1.2 broken | 1.6 broken | about 0.8 |
| E28 | **1.06 right** | 1.59 lower ("a touch", tree) | 2.12 lower | 2.65 lower | 1.06 to just under 1.59 |
| P01 | 0.71 raise | 1.41 raise | 2.12 broken | 2.83 broken | above 1.41, below 2.12 |

## DINOv2 at the marked "right" doses (descriptive)

| edit, dose | tree: D from plain / plain seed spread; consistency | helmet: same |
|---|---|---|
| E06 0.8 | 0.510 / 0.383 = 1.33; 0.32 | 0.275 / 0.056 = 4.96; 0.58 |
| E14 0.8 | 0.525 / 0.383 = 1.37; 0.41 | 0.178 / 0.056 = 3.20; 0.52 |
| E28 1.06 | 0.708 / 0.383 = 1.85; 0.31 | 0.107 / 0.056 = 1.93; 0.36 |
| P01 1.41 | 0.190 / 0.383 = 0.50; 0.02 | 0.067 / 0.056 = 1.21; 0.21 |

At level 1 (C112's doses) consistency was 0.05, 0.02 (tree) and 0.10, 0.27 (helmet) for E06 and E14.

## Reading

1. **Each edit has a narrow usable window, and it was the same on both prompts.** E06 and E14 at about 0.8 (C112's 0.4
   was too weak, as Alessandro guessed), E28 at about 1.06, P01 between 1.41 and 2.12. Past the window the pictures
   either leave the prompt the same way at every seed (E06 at 1.2 turns the helmet into a black figurine and the tree
   into a green painted landscape; E28 from 1.59 a cartoon devil, close-ups of leaves) or break into noise (E06 1.6,
   E14 from 1.2, P01 from 2.12). E14 goes from right to broken in one step.
2. **At the right dose the edit moves the picture more than a change of seed does, by DINOv2,** for E06, E14 and E28 on
   both prompts (ratio 1.3–5.0), and the direction is shared across seeds (0.31–0.58). This is the condition C112
   lacked (amount no more than a seed change), but it is non-blind here and must be confirmed (C114).
3. **DINOv2 consistency alone would mislead:** it keeps rising past the window because the pictures leave the prompt
   in the same way at every seed.

## Limits

Non-blind; one observer who proposed the hypothesis; two prompts; four levels per edit (windows bracketed, not
located); P01's best dose was not rendered; Krea-2 turbo only.

## For C114 (blind demonstration on unseen prompts)

Doses: E06 0.8, E14 0.8, E28 1.06, P01 about 1.75 (inside its bracket, not yet rendered). Questions as C112 amendment 2
plus whether the edit overrides colour and style words in the prompt.
