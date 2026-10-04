# C47 result — blk23 is a monotone, near-linear saturation control; against "colorful" it keeps the picture better where it can reach the same saturation, and it reaches it in 7 of 16 cases

2026-10-04. Pre-registration: `prereg_blk23_vs_colorful.md` (+ amendment 1). Code:
`experiments/analyze_blk23_vs_colorful.py`, unchanged since commit 76e8180. Data:
`data/blk23_colorful_measures.csv`, `data/blk23_colorful_test.csv`; eye pass
`data/blk23_colorful_eye_alessandro.csv`, deposited (commit 8ecead3) before the scoring ran.
Renders 128/128, reproducibility 26/26 pairs pixel-identical.

## 1. Pre-registered verdicts

| test | result | verdict |
|---|---|---|
| V1 direction: chroma falls strictly from −0.45 to +0.30 | 15 / 16 cells (the exception: E7 seed 4669201, +0.15 → +0.30, −1.62 → −1.51) | **supported** |
| V2 proportion: Δchroma(−0.30) / Δchroma(−0.15), median | 1.76 | **approximately linear** |
| T0 cells where "colorful" did not raise chroma | 0 / 16 | — |
| T0b cells where "colorful" raised chroma beyond blk23 −0.45 | **9 / 16** | — |
| T1 layout kept at matched chroma, blk23 vs text | blk23 higher in 6 of the 7 scorable cells, median +0.082 | **blk23 better** (on 7 cells) |

The T1 verdict is the rule's, and it stands on 7 cells, not 16. The pre-registration set no
minimum number of scorable cells; that gap is stated here rather than repaired after the fact.

## 2. What the 9 unscorable cells say

In 9 of 16 cells the words reach a saturation that blk23 does not reach at its strongest
tested dose: E1 cartoon (+9.8 / +10.4 chroma for the text against +1.6 / +5.2 for blk23
−0.45), E3 oil (+9.3 / +10.5 against +3.8 / +2.2), C4 still life, P4 selfie, C3 fox seed
2718281. Medians over all 16 cells: text +5.7 chroma at layout r 0.80; blk23 −0.45 +3.9 at
layout r 0.87. So: **blk23 is the gentler lever, not a stronger one.** On the sepia photo the
order reverses (blk23 +5.2 / +3.9, text +2.2 / +1.8), as Alessandro noted by eye.

## 3. The eye

"Which changed the content more (colour ignored)":

| | the words | blk23 | equal |
|---|---|---|---|
| more colour, all 16 cells | 9 | 2 | 5 |
| — the 7 scorable cells | 2 | 1 | 4 |
| — the 9 cells beyond the ladder | 7 | 1 | 1 |
| less colour ("muted" vs +0.15/+0.30), 16 cells | 12 | 1 | 3 |

"Does blk23 move colour the expected way, growing with the dose": 16/16 yes when adding
colour; 8 yes and 8 partly when removing it. His notes on the "partly" cases: the
desaturation is small on the rally car, comes with softening or blur on the fox and the
still life, and on the selfie the skin desaturates faster than the background and turns
greenish.

Eye and numbers agree on direction. On the matched comparison they agree in sign but not in
size: where the rule says blk23 keeps the layout better (6/7), the eye mostly says "equal"
(4/7). Layout r at 64×80 counts small shifts the eye does not call a change of content.

## 4. What this supports, and what it does not

- **Supported:** blk23 negative raises saturation on every prompt tested, monotonically and
  roughly in proportion to the dose, while moving the layout less than the words that give
  the same colour gain — where it can give that gain.
- **Not supported:** that blk23 can replace "colorful" in general. On cartoon, oil and
  photographic portraits the words add more colour than blk23 at −0.45, and they also
  change the content more (eye, 7/9 of those cells; text layout r down to 0.44 on the
  cartoon).
- **The desaturating side is weaker and less clean:** blk23 +0.30 removes about 60 % of the
  chroma the words "muted, desaturated" remove (median −3.1 against −5.1), with softening and
  uneven hue shifts in half the cells.
- Open: doses beyond −0.45 (does blk23 reach the words' saturation before it degrades the
  image?) and other wordings of the prompt.
