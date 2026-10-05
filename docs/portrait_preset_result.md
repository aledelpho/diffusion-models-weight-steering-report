# C52 result — the portrait preset carries over to unseen characters; the face moves a little more than a change of seed

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
- **Descriptive, after the test (not a rule):** ArcFace does discriminate these drawn faces. Over all
  detected baselines, same character at another seed 0.80 (39 pairs); **different characters 0.29**
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

## 4. Pending

Amendment 2: the human blind observer (`data/portrait_preset_blind_answers_human.csv`, not yet
received). It is the only blind judgement of the look and of identity in this test.
