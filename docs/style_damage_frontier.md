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

---

# Retraction and correction, same day

Alessandro, on native-resolution crops of the two renders §4 called clean: *"these images you keep
holding up as the best result actually have very visible structural defects — is it possible you
don't feel them as full of grain only because the patches of colour are looser?"*

He is right, §4 is withdrawn, and chasing the reason has cost this document three of its claims.

## 7. §4 is withdrawn: the look was done at the wrong resolution

"No artefacts" was asserted after viewing whole 1024 × 1280 frames rendered down to fit. That view
cannot show a pixel-level property, so the claim had no support whatever the images look like.
Re-cut at native resolution, 340 × 340 over the face:

* **`blk27 neg`** — the skin is covered in fibrous, creased filaments; the neck is streaked with
  sinewy strands; the brick wall and window behind the figure have dissolved into an unstructured
  wash; a stray glyph sits on the left shoulder.
* **`B6_anti neg`** — the same family of defect, further along: ink linework replaced by soft
  mottling, hair melting into the background, the background itself almost entirely black with no
  legible object in it.
* **`B4_mask neg`**, by comparison, keeps crisp line, coherent flat colour and a well-formed face.

**The observer's ranking was right and this document's was wrong.** What follows is why the
statistics could not see it.

## 8. Three estimator defects, measured

Bands are octaves of a Gaussian pyramid of (render − baseline), normalised by the baseline's own
energy in the same band (`experiments/damage_spatial_bands.py`, `data/damage_bands.csv`, 140
conditions). Orientation is the structure-tensor coherence (λ₁−λ₂)/(λ₁+λ₂) over a 9 × 9 window,
as a ratio to baseline (`experiments/texture_anisotropy.py`, `data/texture_anisotropy.csv`,
80 conditions at dose 0.200).

**(a) The grain statistic carries no information about how much fine texture was rewritten.**
Across 140 conditions, |ln(grain ratio)| against band-0 difference energy: **r = −0.054**.
`blk27 neg` reports grain **0.841** — "16 % less grain" — while its band-0 difference energy is
**1.53×** the baseline's own. **An edit can replace the finest texture wholesale and the summary
will report a decrease**, because a sum of squared second differences throws away everything but
the total.

**(b) §1's two axes are not independent, as claimed.** `layout_cost_z` against band-0 difference
energy: **r = +0.798**. The 8× downsample was supposed to isolate composition; it mostly tracks
how much fine detail changed. So the Pareto frontier in §2 is not "style against damage", it is
largely one quantity plotted against itself, and its ordering cannot be read as a trade-off.

**(c) Alessandro's spectral explanation is not what happened — the orientation is.** The middle
bands are not a blind spot: mid-band share is 0.353 to 0.466 across all 140 conditions, essentially
constant, and `blk27 neg` is *lower* in bands 1–3 than `B4_mask neg`. What separates them is not
where the energy sits but whether it is **oriented**. The baseline is comic linework — strongly
oriented ink strokes. Coherence ratio, 80 conditions:

| condition | coherence | cells above 1 | rank |
|---|--:|--:|--:|
| **`B4_mask` pos** | **×1.041** | 6/6 | **1 / 80** |
| `Block_4` neg | ×1.026 | 5/6 | 9 / 80 |
| `B4_mask` neg | ×0.974 | 0/6 | 65 / 80 |
| `blk27` neg | ×0.802 | 0/6 | 75 / 80 |
| `Block_6` neg | ×0.793 | 0/6 | 76 / 80 |
| `B6_anti` neg | ×0.789 | 0/6 | 77 / 80 |
| `B6_mask` neg | ×0.729 | 0/6 | 79 / 80 |
| `B4B6_mask` neg | ×0.718 | 0/6 | 80 / 80 |

**The five conditions this document recommended are the five largest losses of drawn line in the
corpus.** The condition Alessandro picked out by eye is **first of eighty**. He was not describing
a taste; he was reading a quantity nothing here was measuring.

His own phrasing turns out to be half right and worth keeping: the defect *is* a texture change,
and it *is* invisible to the grain number. But it is not that the patches are looser at some
particular scale — it is that the model stops drawing lines and starts smearing tone, at every
scale at once.

## 9. The corrected frontier, and `Block_4` is vindicated

Pareto on style ↑ and coherence ↑, 80 conditions at dose 0.200:

| family | condition | arm | style | coherence | |
|---|---|---|--:|--:|---|
| mask | `B4B6_mask` | neg | 0.914 | 0.718 | maximum style, line destroyed |
| mask | `B6_mask` | neg | 0.846 | 0.729 | same trade |
| group | `Block_5` | pos | 0.620 | 0.969 | |
| **group** | **`Block_4`** | **pos** | **0.478** | **0.994** | **style with the line intact** |
| **sub-block** | **`blk16`** | **pos** | **0.447** | **1.040** | **style with the line reinforced** |
| mask | `B4_mask` | pos | 0.261 | 1.041 | least style, best line |

**§3's conclusion is reversed. `Block_4` is not dominated — it is the family that does what
Alessandro asked for**, and `blk16 pos` (a member of `Block_4`, indices 15–19) delivers nearly the
whole group's style movement while *increasing* the orientation of the drawing. `blk27` should not
have been recommended: it buys its style by dissolving the line.

The original §3 remains true as written — `B4_mask neg` does beat `Block_4 neg` on style at lower
layout cost — but "layout cost" is defect (b), so that comparison should not be leaned on either.

## 10. What changes

* §2 and §4 of this document are superseded by §8 and §9. §1's independence claim is false.
* **`blk16`** is the new candidate for the single-block experiment, not `blk27`. Register **C19**
  is rewritten accordingly; `blk27` keeps its own entry as the grain anomaly, not as an operating
  point.
* Coherence is the project's first quality axis that is not a displacement measure. It is one
  number on one drawing style, and a comic-line baseline is exactly the case where it should work
  best — it needs checking on a photographic prompt family before it is trusted (**C20**).
* Three drafted defects, register §E: **78** judging a pixel-level property at a resolution that
  cannot show it; **79** declaring two axes independent without measuring their correlation;
  **80** an isotropic texture summary that reports a decrease while the texture is being replaced.
