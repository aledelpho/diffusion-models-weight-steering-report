# C59 eye pass — result

2026-10-07. Protocol: `docs/split_atlas_eye_protocol.md` (+ amendment 1, class `piatto`). Key committed before
the labels (`4aaeeec`), labels committed as downloaded before any count (`ac878a8`):
`data/split_atlas_eye_alessandro.csv`. First-showing table with key: `data/split_atlas_eye_tally_alessandro.csv`.
Observer: Alessandro, blind to block and part. Seed 2718281, 168 sheets + 20 repeats.

## Self-agreement (protocol point 1)

Per class, presence agreement on the 20 repeats is 0.90–1.00, so no class is excluded by the 0.8 rule.
That number is inflated by the base rate: 12 of 20 repeats were clean both times. For "any artefact" the
agreement is 0.80 and Cohen's κ 0.41. All four disagreements are a **lieve** label on one showing and
nothing on the other; the two repeats labelled medio or stronger the first time (chiazze 2; grana 1 twice)
came back the same. Reading: **lieve is not reproducible; medio and forte are**, on very few repeats.
Below, counts are given at any intensity and at medio or stronger (≥ 2).

## Overall

68 of 168 sheets carry at least one artefact; 46 carry noise (chiazze, grana, collasso, retino), 27 of
them at medio or stronger. Blocks 2, 3, 5, 7–9 are clean in all six conditions.

## Where the noise sits (protocol point 3)

Among the 19 block × sign cells where at least one half is noisy, the MLP is noisier in 13, the attention
in 2, tie in 4. At ≥ 2: MLP noisier in 7 (block 0 −; 22, 23, 24, 25 +; 26 −; 27 −), attention in 1 (25 −),
tie in 3 (0 +, 26 +, 27 +). The kind differs within a tie: at block 26 + the attention gives mottling and
partial collapse (chiazze 2, collasso 2), the MLP medium grain (grana 2).

**This reverses my reading in `docs/split_atlas_result.md` §2**, which said that at block 26 the noise
belongs to the attention and the MLP alone is clean, and that C58's thesis does not hold as a rule. I read
that from 192-pixel thumbnails. At full resolution (`sheets/check_*.jpg`) the MLP of block 26 at + does
carry a visible grain, and the attention of block 27 at + a clear mottling, not "a light speckle". On the
blind labels, C58's thesis — the noise is mostly the MLP's — holds across the stack, with the attention
contributing at the very end (25–27).

## Whole vs halves (protocol point 4)

Any artefact: in 19 of 35 cells with an artefact somewhere, the whole block is worse than both halves; in
6 it is better than the worse half; 10 equal. Noise alone: 8 worse, 8 better, of 24. The whole block is
superadditive for artefacts in general — mostly content replacement (`sostituito`), flattening and
posterisation in blocks 10–21 at +, where the halves are clean — but not for noise. Block 26 at + is the
clear superadditive noise case (collasso 3 vs 2).

**Block 0 at −0.35, correction to §1 of the result:** the whole block is labelled chiazze **forte**. It
keeps the composition (layout r 0.69–0.80, which is what §1 measured) but not the surface: at full
resolution it is heavily mottled. The halves still fail harder (attention: posterisation 3; MLP:
retino 3 and content replaced 3). So the halves compensate for content, not for texture.

## Measures against the eye (protocol point 5)

444 per-prompt rows (sheets marked "non in tutti e tre" left out), 105 noisy, 75 at ≥ 2. Raw ratios do
not rank noise (AUC 0.42 for page 05's HF, 0.40 for the post-hoc band: noise lowers them about as often as
it raises them). The size of the change, |log ratio|, ranks it moderately: AUC 0.76 (HF) and 0.75 (band)
for any noise, 0.81 and 0.80 for ≥ 2. |log ratio| measures any texture change, smoothing included, so it is
a change detector, not a noise detector. Neither scalar can replace the eye on this question.

## Things the free field caught

* Two blind guesses about block 23: the attention of block 23 at + was flagged as "Blk_23? lowers the
  saturation, especially on the comic" — right block, right part of the effect (C58). The attention of
  block 24 at + was flagged "more colour, no artefacts — smells of block 23": wrong block, right
  observation (chroma +2.5 and +3.7 on the two illustrations, 0 on the rally).
* The rally reacts differently from the two illustrations: retino appears on the car where the
  illustrations get softening or posterisation (8 notes); colour shifts towards green-yellow on the car
  (blocks 11 whole +, 12 MLP +).
* Many sheets judged clean were also judged better than the baseline on the comic (blocks 8 MLP + and
  whole +, 9 attention + and whole +, 13 whole −, 18 MLP −, 2 whole −; block 1 attention + too, with a
  blur on the car). Not a protocol measure; noted for a later test.
