# The animations: what is in the repository, and what each one still needs

2026-09-24 · one new animation built, seven inherited ones inventoried · no renders were made

A still shows that two images differ. It cannot show a reader that the layout stayed fixed
while one thing changed, and it cannot show the same edit landing the same way on five
different seeds. That is what the animations did in the old monolithic README, and the
migration lost them: they are all still on disk, in `assets/hero/` and `assets/motion/`, with
**no entry in `experiments/figures.yaml`, no page referencing them and no script behind them**.
Eight files, 10.5 MB, invisible to the notebook.

## Built today

**F02.7 `assets/02-attribute-emergence/F02.7_headlights_switch.gif`** — 7 frames, 1.45 MB,
1012x333. One prompt, the same five seeds throughout, and every one of the bench's seven arms
in turn. Nothing moves between frames except the edit. On `S2_watercolor` six arms light no
headlights in any of the five seeds and the seventh, the calibrated preset at double
amplitude, lights all five. Built by `experiments/build_animations.py`, registered, referenced
from page 02.

Three things it carries that the stills do not. Each cell shows the verdict the **blind
scorer** gave that exact image, read out of `data/stage9_headlights_key.csv` joined to
`data/stage9_headlights_raw.csv`, ambiguous cells included and marked rather than rounded
away. Each header shows the mean L* shift of that arm from `data/stage9_preset_shift.csv`,
because the preset darkens the whole frame and a reader deciding whether a lamp is lit or
merely brighter than a darker scene needs that number in front of them. And the provenance
strip counts, from the scoring, how many arms of seven light a majority — it is not typed, so
it cannot be wrong about the figure above it.

**Why watercolour and not low-poly.** Low-poly was the style asked for, and the data does not
support the sentence the figure would carry. On `S3_lowpoly` two arms of seven reach a
majority, not one: the preset at double amplitude lights 5 of 5, and the negative block
derangement at *single* amplitude lights 3 of 5 — which the aggregate row of 6 lit in 38 hides
entirely, and which is worth an experiment of its own. The untouched model also already lights
one seed of five there. `--prompt S3_lowpoly` rebuilds it; both were built and compared before
choosing. On watercolour the count is 0 in six arms and 5 of 5 in the seventh.

The scorer's keystrokes 0/1/2 are recorded with no legend anywhere. The builder recovers it —
0 unlit, 1 ambiguous, 2 lit — and **asserts** it: `blockshuf_neg_2x` has 0 lit and 1 ambiguous
in `data/stage9_headlights_results.csv`, and exactly one cell of that arm carries code 1 and
none carries code 2. If a rescoring ever breaks that correspondence the build stops.

**F02.8 `…/F02.8_headlights_switch_lowpoly.gif`** — the same seven frames on `S3_lowpoly`,
committed beside F02.7 rather than instead of it. Two arms of seven reach a majority there,
not one, and the untouched model already lights a seed: the pair is the argument that one
style is an illustration and the census is the measure.

**F02.9 `…/F02.9_arm_coherence.webp`** — not an animation, but the answer to the question the
animations provoke. Five seeds that share nothing but the prompt all move the same way, and
`experiments/arm_coherence.py` puts a number on it: across the seeds of one prompt the mean
cosine between difference vectors runs 0.50 to 0.91, against 0.10 for a change of seed. It
also writes the arm-against-arm matrix (preset ×1 against ×2: +0.957), the per-style breakdown,
where low-poly's preset at single amplitude falls to +0.325 with pairs from −0.22 to +0.73, and
the test that decides what the coherence means.

That test is the reason the figure's title reads the way it does. The norm-matched **sign
scramble** — a random perturbation with no structure in it — clears the seed null on 8 styles
of 8 exactly as the preset does, and no structured arm separates from it (+0.143 to +0.250,
Holm 0.094 to 0.148, `data/arm_coherence_tests.csv`). Coherence across seeds is a fact about
holding the seed fixed, not about structure. A figure that had stopped at "every arm is a
direction" would have invited precisely the inference the control refutes.

## Inherited, and what each needs

Every one of these needs the same three things before it can go back into a page: a builder in
`experiments/build_animations.py` that rebuilds it from the renders, a `source` naming the
measurement its labels come from, and an entry in `experiments/figures.yaml`. The column that
differs is what stands in the way.

| File | What it shows | Belongs on | What it needs |
|---|---|---|---|
| `hero/5seed_goblin.gif` | 5 seeds x 5 conditions, whole frames, one goblin prompt | 01 | a builder over `data/stage5_images.csv`; renders in `benchmark_stage5` and `benchmark_stage4_preset` |
| `hero/5seed_hag.gif` | the same layout, the sea-hag prompt | 01 or 02 | same builder, different prompt |
| `hero/5seed_barbarian.gif` | the same layout, the barbarian prompt | 01 | same builder, different prompt |
| `hero/5seed_timelapse.gif` | the same layout, cycling conditions rather than prompts | 01 | same builder |
| `motion/six_blocks_ramp.gif` | 24 frames, six block groups side by side, sweeping the gain from -0.200 to +0.200 | 05 or 10 | a `ramp` builder; the source bench is unconfirmed, probably `benchmark_mappa` |
| `motion/six_blocks_motion.gif` | 10 frames, the same six groups as difference maps, "where it moves" | 05 | a `diffmap` builder; same bench question, and the null it is differenced against has to be named |
| `hero/hatching_axis.gif` | 4 frames, a **close crop** of one figure, hatching orientation flipping with the sign | 06 | **blocked**: the contract forbids a crop that is not a named locator with a measured hit rate (this project has published five crops of twenty that did not contain what their captions said) |
| `hero/crop_timelapse.gif` | 5 frames, a **close crop** of a face, baseline against the sign scramble | 01 | **blocked**, same reason |

Two further notes on the two blocked ones. Both also fail the dark-background check that
`validate_notebook.py` runs on every registered figure — their corners are the render's own
pale paper, not the surface — so even with a locator they would need matting. And the honest
alternative is cheaper than it looks: the same pair at whole-frame scale already exists as
F01.1, and the crop is there to make a fine detail visible, which a 2x inset on the dark
surface would do without asserting where to look.

## What the builder is

`experiments/build_animations.py` composes frames on the notebook's own surface `#1a1a19`,
pastes whole renders at a fixed cell width, draws the seed under each and the verdict as a
badge in the status palette, and writes an animated GIF. It takes `--renders` so the bench
root can be pointed anywhere, `--out-dir` so a run can be inspected before it lands in
`assets/`, and `--list`. Adding one of the rows above is a function of about forty lines, plus
its `figures.yaml` entry.

These files are large by the standards of the rest of the notebook — 0.7 to 3.1 MB against
30 KB for a chart — and that is the right trade. A reader who can see the switch flip does not
have to take the table's word for it.
