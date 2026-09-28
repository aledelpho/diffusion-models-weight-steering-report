# How much style does an edit buy, and what does it cost the picture?

**Date**: 2026-09-28 · **Trigger**: Alessandro on two `B4_mask` renders — *"two nice `Block_4`
effects, it didn't seem to ruin the image and changed the style noticeably while keeping the final
visual quality I was hoping for"* · **Material**: 840 renders already on disk, no new render ·
**Script**: `experiments/style_damage_frontier.py` → `data/style_damage_cells.csv` (840 rows),
`data/style_damage_frontier.csv` (140 conditions).

---

## 1. Making the criterion measurable

"Changes the style without ruining the image" is two quantities, and they have to be built out of
different parts of the picture or the comparison is circular.

* **`style_shift`** — how far the look moved: the norm of (ln contrast, ln grain, ln chroma,
  hue shift / 90°). Four axes, each already in use elsewhere in this project.
* **`layout_cost_z`** — how far the *picture* moved: RMS difference against the baseline on the 8×
  downsampled luminance, **after z-scoring both**. The low-pass keeps grain — which is style — from
  counting as damage. The z-scoring keeps a change of tone or contrast — also style, and already
  counted once — from counting as damage a second time. What survives is composition.
  It converts to a correlation: `r = 1 − cost²/2`.

**The two are never divided by one another.** A style-per-damage ratio puts a quantity that can
approach zero in the denominator, and this project got that wrong three times in a single day.
Conditions are ranked by **Pareto dominance** instead: a condition is on the frontier when nothing
else moves the style further *and* costs less layout.

Corpus: `benchmark_mappa` (6 groups × 2 arms × 6 doses), `benchmark_profondita`/`_neg` (28 single
blocks × 2 arms at 0.200), `benchmark_rectified_masks` (12 conditions). 140 conditions,
6 cells each.

## 2. The frontier

| family | condition | arm | dose | style | cost | structure `r` |
|---|---|---|--:|--:|--:|--:|
| mask | `B4B6_mask` | neg | 0.200 | **0.914** | 0.818 | 0.665 |
| mask | `B6_mask` | neg | 0.200 | 0.846 | 0.793 | 0.685 |
| group | `Block_5` | pos | 0.200 | 0.620 | 0.757 | 0.714 |
| mask | `B6_anti` | neg | 0.200 | 0.464 | 0.601 | 0.819 |
| **sub-block** | **`blk27`** | **neg** | 0.200 | **0.394** | **0.538** | **0.855** |
| group | `Block_6` | neg | 0.120 | 0.340 | 0.500 | 0.875 |
| group | `Block_6` | neg | 0.080 | 0.260 | 0.453 | 0.898 |
| group | `Block_6` | neg | 0.050 | 0.194 | 0.408 | 0.917 |
| group | `Block_6` | neg | 0.035 | 0.146 | 0.382 | 0.927 |
| group | `Block_6` | neg | 0.020 | 0.072 | 0.337 | 0.943 |

**Ten conditions out of 140.** Five of the ten are the `Block_6` negative dose ladder: below
dose 0.200, the cheapest style in the instrument is `Block_6` pushed negative, and nothing else
competes at those cost levels.

## 3. Is `Block_4` special? No — and the answer is useful anyway

The pair Alessandro reacted to, and the group it comes from:

| condition | style | cost | structure `r` |
|---|--:|--:|--:|
| `B4_mask` neg 0.200 | 0.372 | 0.727 | 0.736 |
| `B4_mask` pos 0.200 | 0.261 | 0.771 | 0.703 |
| `Block_4` pos 0.200 *(the whole group)* | 0.478 | 0.841 | 0.646 |
| `Block_4` neg 0.200 *(the whole group)* | 0.219 | 0.743 | 0.724 |

Two things are true at once.

**His reading of the mask against its group is right.** `B4_mask neg` delivers **1.7× the style
movement of `Block_4 neg` at a lower layout cost** (0.372 against 0.219, cost 0.727 against 0.743).
Restricting a group to two opposed sub-blocks bought style and did not spend picture. That is the
one place in this corpus where the rectified mask clearly beat the slider it came from, and it is
the thing he saw before any number said it.

**But `Block_4` is not on the frontier, and the operating point he liked is dominated.**
`blk27 neg` gives **more** style (0.394 against 0.372) at **much** lower cost (structure `r` 0.855
against 0.736). A single block, one slot in the vector, dominates the two-block `B4` mask on both
axes at once.

## 4. The eye agrees with the proxy — checked, not assumed

`layout_cost_z` measures departure from the baseline composition. That is **not** the same as
"looks good": an edit could keep the composition and still look broken. So the ranking was checked
against the images, same prompt and same seed as the pair Alessandro sent (`P01`, seed 777).

* **`blk27 neg`** — the cross-hatching of the baseline gives way to smooth, airbrushed modelling;
  the face is more fully rendered, the smoke and fire become atmospheric gradients, colour is
  richer. Pose, objects and layout unchanged. No artefacts.
* **`B6_anti neg`** — a harder, high-contrast "painted book cover" look, deep blacks, dramatic key
  light. Composition unchanged. No artefacts.

Both are larger and cleaner style moves than either arm of `B4_mask`, which is what the frontier
predicted. On this sample the proxy and the observer agree; it has not been checked at scale, and
it remains a proxy.

## 5. What this says about the instrument

* **The "block as a knob" objection is about groups, not about edits.** The best operating points
  in the whole corpus are a *single* sub-block (`blk27`) and *two-block* masks — not the six
  sliders the tool exposes. The group slider is the crudest object in the instrument.
* **`blk27` keeps nominating itself.** Punto 7 §3 singled it out on swing a week ago and said it
  *"deserves an experiment of its own"*; `internal_fights_by_group.md` found it the one member that
  reverses its whole group on grain; here it is the best style-per-damage point among all 28 single
  blocks. It still has not had that experiment.
* **Dose is a cheaper lever than block choice.** `Block_6 neg` occupies five frontier slots by dose
  alone. Any search for a good look should sweep dose on a good block before trying more blocks.

## 6. Limits

* `style_shift` weights four axes equally with no justification beyond convenience; a different
  weighting moves the ranking. The frontier's top and bottom are robust to it, the middle is not.
* `layout_cost_z` is a composition metric, not a quality metric. It cannot see an anatomical error,
  a broken hand or an incoherent object.
* Two prompts, three seeds, one model. Nothing here is pre-registered — it is a survey of existing
  material, and the ranking it produces is a hypothesis about where to look next.
