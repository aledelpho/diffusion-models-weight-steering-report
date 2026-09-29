# Blocks 22–27 as "rendering controls" — one label holds, one nearly, four do not

**2026-09-29.** Tests fixed in [`prereg_late_blocks_render_controls.md`](prereg_late_blocks_render_controls.md)
(`ff06640`), with the amendment for Alessandro's "not really a knob" reading (`108f731`) deposited
**before any statistic was computed**. Data: `benchmark_single_blocks_atlas` (±0.350, one seed, three
prompts) and, for replication, `benchmark_profondita` (±0.200, seed 42, P01 and P02) against seed-42
baselines from `benchmark_latenti_b6` whose graph settings were checked to match. No render.

**Not blind for 22 and 23** — saturation and colourfulness per block had been printed the day
before. Blind for 24–27, for subject preservation and for the whole replication.

## The one claim that holds for the whole region — the subject barely changes

Layout similarity to the baseline (grey, 64×80, correlation), mean over 3 prompts × 2 signs:
**0.834 for blocks 22–27 against 0.771 for 0–21, exact Mann–Whitney p = 0.010.** Blocks **23 (0.896),
25 (0.891) and 24 (0.871) are the three most layout-preserving blocks of all 28.** The exception is
26 (0.717, among the lowest), whose positive arm dissolves the picture. *"Cambia pochissimo il
soggetto"* is right — for 22–25 especially.

## Label by label

| block | label | own measure | two poles (H1) | own measure the largest of six (H2a) | rank among 28 on own measure | replication (H4) | strong reading | lever reading |
|---|---|---|:-:|:-:|:-:|:-:|---|---|
| **27** | focus | concentration of sharpness | **3/3** | **yes** | **1** | **4/4** | **SUPPORTED** | not (H5) |
| **23** | saturazione | mean saturation | 2/3 | no — colourfulness larger | **1** | **4/4** | not | not |
| 26 | sharpness | high-frequency share | 3/3 | no — contrast (−4.16), focus, texture all larger | 3 | 3/4 | **partly** | not |
| 22 | vividezza | colourfulness | 2/3 | no | 21 | 3/4 | not | not |
| 24 | contrasto | RMS contrast | 2/3 | no | 18 | 2/4 | not | not |
| 25 | texture | LBP entropy | 1/3 | no | 21 | 2/4 | not | not |

**H5 — does each attribute live in the region?** For every measure the mean |swing| over 22–27 is
larger than over 0–21 (e.g. contrast 1.27 vs 0.50, focus 1.32 vs 0.28), but **none reaches p ≤ 0.05**
(saturation 0.063, contrast 0.056; six blocks against twenty-two). So under the lever reading, which
requires H5, **no label is supported** — by the rule, and with two near misses.

## Reading it

- **27 — focus — is the cleanest result of the day.** Its own measure is the one it moves most, it
  moves it more than any other block, on all three prompts, and it replicates at another seed and
  dose 4/4. **One caution about its positive arm**: the measure falls there because the confetti
  collapse spreads sharp detail uniformly over the frame. The meaningful direction is the negative
  one — sharp subject, soft background — which is what was seen on 2026-09-29's sheet.
  And H5 fails for focus precisely because focus is **not** spread over the region: 27 carries it
  almost alone (|z| 4.08; the other five average about 0.8). For this attribute the evidence goes
  against "many levers" and for "one block".
- **23 is the strongest saturation lever of all 28 blocks and replicates 4/4 — and still fails the
  strong rule**, by one prompt on H1 and because it moves colourfulness even more than saturation.
  Colourfulness and saturation are close relatives; **23 is the colour-intensity lever, under either
  name.** 22, labelled "vividezza", does not move colourfulness (rank 21/28). *Post hoc, not a test:*
  the two colour labels may both belong to 23.
- **26 moves everything** — contrast most of all, then focus, texture, sharpness. It is the block
  whose positive arm collapses the image; a general degradation moves every statistic at once. Not
  a sharpness control. *Post hoc:* the largest contrast swing of the six is 26's, not 24's.
- **24 and 25 show nothing measurable on their labels** — contrast and texture swings in the middle
  of the 28 blocks. His own doubt on 25 was right.

## On "not really a knob"

Alessandro's point — training never defined these attributes, so what exists is an approximation
spread over several levers — is reasonable and was tested as such (H5). The data are compatible
with the late region carrying more of every attribute than the early one, but with six blocks the
test cannot confirm it for any single attribute. And for the one attribute that clearly exists as a
control, focus, it is **one lever, not many**.

## Limits

One seed in the atlas; replication on one seed of profondita, two prompts. "Linear" is untested —
one dose per arm. Each label was mapped to one measure; a different measure of "contrast" or
"texture" could behave differently, and that choice was fixed before the numbers precisely so it
could not be tuned afterwards.

## Provenance

`experiments/late_blocks_measures.py atlas | profondita` → `data/late_blocks_atlas_extra.csv`,
`data/late_blocks_profondita.csv`; `experiments/late_blocks_tests.py` → `data/late_blocks_tests.csv`.
