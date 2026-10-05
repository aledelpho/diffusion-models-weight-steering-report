# C52 result — the portrait preset carries over to unseen characters, and a blind observer sees it 56 times in 56; the face moves a little more than a change of seed

2026-10-05. Pre-registration `prereg_portrait_preset.md` (+ amendments 1 and 2). Preset frozen in
`4da5117`; plan, scoring code and self-test committed in `7805d84`, before any phase C render.
Renders: `docs/RENDERS_2026-10-05_portraits_phase_c.md` — REPRO pixel-identical, 57/57.
Alessandro's eye pass committed before any number (`c285253`): "yes" to every question, not blind.

## 1. Pre-registered rules

| rule | threshold | result | verdict |
|---|---|---|---|
| G_S the preset agrees with itself across seeds | median S ≥ 0.50 | **0.78** | pass |
| H1 the look transfers to the held-out characters | median W_held ≥ 0.40 | **0.51** | **supported** |
| H2 no worse than on the calibration characters | W_held ≥ W_cal − 0.15 | **0.51** vs 0.61 | **supported** |
| H3 identity holds | every eligible held-out: ID_edit > ID_seed, and median ID_edit ≥ 0.50 | 0 of 2 above ID_seed; median 0.74 | **refuted** |

Data: `data/portrait_preset_tests.csv`, `data/portrait_preset_measures.csv`.

## 2. Reading H3 — refuted by its rule, and what the numbers say

- **Eligible:** halfling (H3) and dragonborn (R6). ArcFace found no face in 3 of 4 gnome preset
  images and in 2 tiefling images (1 baseline, 2 presets of 8), so G5 and T7 are out. The dragonborn,
  expected to fail detection, passed.
- **Per character:** ID_edit 0.75 vs ID_seed 0.82 (halfling); 0.74 vs 0.75 (dragonborn). The
  calibration characters show the same pattern (0.71 vs 0.79, 0.83 vs 0.86, 0.76 vs 0.79). The
  preset moves the face a little more than changing the seed does, on every character measured.
- **Descriptive, after the test (not a rule):** ArcFace does discriminate these drawn faces. Means over
  all detected baselines (medians 0.80, 0.27 and 0.75), same character at another seed 0.80 (39 pairs); **different characters 0.29**
  (312 pairs, max 0.68); baseline vs preset, same seed, 0.74 (23 pairs). The preset keeps the face far
  closer to itself than to any other character, and slightly further than a seed change. The rule
  asked for "no more change than a seed" and the prompts are specific enough that the seed barely
  changes the face (0.80); that bar was not met.
- **Not interpreted:** whether the lost detections on the gnome mean a deformed face or only a more
  stylised one. That needs the images at 1:1.

## 3. Blind forced choice — amendment 1 (model observers): not completed, observer 1 void

The first model observer answered LEFT on **51 of 56** sheets. On its own (diagnostic, n = 1, not the
registered majority of three) the position gate fails: same side in 23 of 28 mirrored pairs. Its
choices are at chance (held out: preset 7/12 and 6/12). **Observers 2 and 3 were not run** — a
deviation from amendment 1, taken by the analyst because an identical instance with the same prompt
would almost certainly read position again (cost ≈ 5 M tokens). The registered verdict is therefore
*not completed*; the observer-1 answers are in `data/portrait_preset_blind_answers_model_obs1.csv`,
its diagnostic tally in `data/portrait_preset_blind_tests_model_obs1_diagnostic.csv`. A model
instance reading two drawings at once did not separate them; this says nothing yet about the preset.

## 4. Blind forced choice — amendment 2 (human observer)

Alessandro's partner, who had not seen the project, answered all 56 sheets with Alessandro out of the
room (`data/portrait_preset_blind_answers_human.csv`, tally `data/portrait_preset_blind_tests_human.csv`).

| | original set | mirrored set | verdict |
|---|---|---|---|
| position gate: same side on both versions of a pair | 0 of 28 | | pass |
| **H4** preset chosen as "more American comic / animation", held out | **12/12** (p = 0.0002) | **12/12** | **supported** |
| **H5** "same character", held out | 12/12 | 12/12 | supported — see caveat |
| calibration (reported, not decisive): preset chosen | 16/16 | 16/16 | |

She picked the preset in **56 of 56 sheets**, every character 8 of 8, and named LEFT exactly 28
times: she read the pictures, not the position, and never contradicted herself on a mirrored pair.

**Caveat on H5.** No sheet showed two *different* characters, so "YES" on every sheet could not have
been wrong: the identity question had no foil and cannot discriminate. H5 passes by its rule, but
the evidence on identity is ArcFace (§2), not this. A future identity test needs pairs of different
characters mixed in.

**Other limits.** One observer, close to the author, though blind to which image carried the preset
and to what was expected. The question named the target look; she was asked which image matched it,
not to describe what changed.

## 4b. The analyst's look at the cases ArcFace marked (after all numbers; not blind; selected, not random)

Seven base | preset pairs, chosen because ArcFace lost the face or gave the lowest ID_edit: the gnome
at three seeds (no face found in the preset), the tiefling at two (no face in the baseline at 2645751,
so that failure is not the preset's), the half-orc at 3605551 (0.63, the lowest) and the dwarf at
3316624 (0.64). Composites in `Text2Img/benchmark_portraits/inspect/`, viewed at 60%.

- **No deformation.** In none of the seven is the face broken, melted or anatomically wrong; the lost
  detections on the gnome are not damage. Every pair is recognisably the same character: glasses,
  ears, beard and robe on the gnome; horns, scarf and yellow jacket on the tiefling.
- **What the preset does, every time:** flatter skin tones (the gnome's skin turns olive-grey), fewer
  hatching lines, cleaner contours — the look Alessandro described.
- **What it removes, and the prompt asked for.** Small surface marks disappear with the hatching: the
  half-orc's dirt smudges/freckles across the nose (named in the prompt), the gnome's glowing chalk
  dust on the cheeks (named), the tiefling's embroidered coat pattern. "Clean lines" also means "fewer
  small details", including requested ones.
- **What it changes that it should not.** **Expression.** The gnome, prompted "wide-eyed manic
  curiosity", is wide-eyed and mild in all three baselines and frowning, brows lowered, mouth turned
  down, in all three presets. The half-orc's "fierce defiant snarl" becomes a closed, glossy-lipped
  stern face that also looks more idealised — the largest identity drift of the seven, matching its
  lowest ArcFace score. The tiefling's horns change shape at 3605551 (curled ram horns to blocky
  upright ones). The dwarf at 3316624 looks the same person to me; there the low score seems to come
  from the shading.
- **A hypothesis, not tested:** the preset contains blk08 +0.15, which Alessandro's own guide lists as
  "less expression and natural poses". It is the first candidate for the lost expressions; scaling
  blk08 alone on these portraits would test it.

So the blind observer's "same character" and ArcFace's "a little further than a seed" are both right
on these images: the character is kept; its expression and its smallest prompted details are not
always.

## 5. What C52 lets Alessandro say

- **Supported, blind:** a preset he calibrated by eye on four characters gives three characters he
  never saw the look he described — chosen in 24 of 24 held-out comparisons by an observer who did not
  know which image carried it — and the change is as coherent across them as across the calibration
  set's (0.51 against 0.61, H1–H2).
- **Measured, not met:** the face moves slightly more than a change of seed (ArcFace 0.74 against
  0.80), while staying far from any other character (0.29).
- **Seen by the analyst, not tested:** the preset can flatten expressions (the gnome's curiosity,
  three seeds of three) and removes small prompted marks (dirt, chalk dust).
- **Open:** a real identity test with foils; whether blk08 + is what removes the expressions.
