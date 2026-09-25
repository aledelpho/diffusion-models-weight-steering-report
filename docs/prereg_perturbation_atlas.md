# Pre-registration — An atlas of perturbations: does each one have a signature, and where does colour live?

- **Written:** 2026-09-25
- **Requires new renders.** Alessandro launches them; nothing here authorises a render.
- **Relates to:** `docs/prereg_arm_identifiability.md`,
  `docs/prereg_colour_identifiability.md`, `experiments/derive_chaos_presets.py`,
  `data/chaos_presets_calibration.csv`.

---

## 0. Why the design changes

Every study so far has been built around one preset and a handful of controls. Six arms,
of which two are the same perturbation with the sign flipped. That corpus can answer
"is this preset special" — and it has, repeatedly, with a no.

It cannot answer either of the two questions that are now the interesting ones:

1. **Does every perturbation carry its own signature**, or only some?
2. **Which regions of the model, when perturbed, move colour the most?**

The first needs many perturbations, not six. The second needs perturbations that differ
in *where* they land while being identical in *how hard* they push — otherwise "this
region moves colour more" is indistinguishable from "this region got a bigger shove".

This document is written after the observer proposed exactly that pivot, and after the
analyst's own visual criterion failed a blind test on 2026-09-25. **No hypothesis in this
document rests on anything either of us claims to see in an image.**

## 1. What already exists and is reused unchanged

`experiments/derive_chaos_presets.py` takes the base preset, computes the Frobenius norms
of the original model and CLIP weights, redistributes the perturbation onto a filtered
subset of blocks and components, and **rescales so that the total norm-weighted
displacement is preserved**, raising an error if the rescaling does not converge.

`data/chaos_presets_calibration.csv` records six such presets. All six carry
`d_model_measured = 267.3721462683354` and `d_clip_measured = 55.27659756535684`,
identical to twelve decimal places. **The magnitude matching is already exact and already
verified.**

This study extends that script's filter list. It does not reimplement it. Any change to
the rescaling logic invalidates the comparison with the existing chaos presets and must
be reported rather than made quietly.

## 2. The design — two factors, not one

**20 perturbations = 10 regions x 2 independent draws.**

A design of 20 perturbations that differ in *both* region and draw would confound the two:
a difference between two of them could be the region or the draw, and nothing would
separate them. Two draws per region is the minimum that allows the region effect to be
estimated at all, and it is stated here as a minimum, not as adequate power.

- **Region** (10 levels): where the perturbation is redistributed. §4.
- **Draw** (2 levels): two base perturbations produced by the tuner with the same
  parameters and **different seeds**, each redistributed onto all 10 regions.

Per perturbation: **3 noise seeds**, identical across all 20 and across the baselines.

Renders per prompt: 20 x 3 + 3 baselines = **63**.

## 3. The magnitude is matched in parameter space, and that is a limitation

The existing rescaling holds the **norm-weighted displacement of the weights** constant.
It does not hold the **displacement of the output** constant, and those are different
things: a region can move the output more simply by being more sensitive.

Therefore:

- "Region R moves colour most" from this design means **per unit of weight change**, which
  mixes *sensitivity* (this region matters more for everything) with *selectivity* (this
  region matters more for colour specifically).
- **Both are reported.** For every perturbation, record the total output displacement in
  the 23-feature space alongside the colour displacement, and report the colour effect
  **both raw and divided by the total**. The ratio is the selectivity; the raw number is
  the sensitivity times the selectivity.
- A page that quotes one without the other is wrong, and this sentence travels with the
  numbers.

## 4. The ten regions — the rule, not the list

The list is not fixed here, because it depends on the model's actual block structure,
which this document will not guess. The **rule** is fixed:

A factorial over **depth x component**, plus the degenerate cases:

- depth: early, early-middle, middle, late-middle, late (five bands of the DiT's blocks,
  contiguous and of equal size, covering all blocks with no gaps and no overlaps)
- component: attention, MLP
- that gives 8 of the 10 after dropping two cells; the two dropped cells and the reason
  are recorded
- plus **CLIP only** (no model patch) and **model only** (no CLIP patch)

Before anything is generated, the script **prints the exact block indices of each band and
the exact tensor-name patterns of each region, writes them to
`data/perturbation_atlas_regions.csv`, and stops.** Alessandro sees that list before a
single preset is derived. If the architecture makes the rule impossible to apply as
written, the script stops and reports rather than improvising a substitute.

## 5. Phases, and the gate between them

**Phase 1 — pilot, one prompt, 63 renders. Descriptive only.**

Purpose: confirm the 20 presets derive and rescale cleanly, confirm the renders land, and
measure the spread of output displacements. **No claim, no p-value, no verdict.** A single
prompt cannot support generalisation and this project has learned that repeatedly; the
pilot exists to catch a broken pipeline before 250 renders, not to answer anything.

Phase 1 reports one number that decides Phase 2: the **coefficient of variation of the
total output displacement across the 20**. If the norm matching in parameter space
produces output displacements that differ by more than a factor of three between regions,
the design is measuring sensitivity far more than anything else, and §3's ratio becomes
the primary statistic rather than a companion.

**Phase 2 — the real study. Minimum 8 prompts, 504 renders.**

`8 prompts x 3 seeds x 21 conditions = 504`. Eight is the minimum for the
leave-one-prompt-out validation that every identifiability result in this project uses;
twelve would clear the power gate of
`docs/prereg_mountain_reachability_amendment_01.md` §2 and is preferable if the GPU time
exists.

**Phase 2 does not start until Alessandro has seen Phase 1's report and said to proceed.**

## 6. Measurements — reused, plus one structural addition

Reused **unchanged**, so the numbers stay comparable with everything already committed:

- the 23 style features and the standardisation convention (baselines only, once, applied
  to all — pitfall 33);
- the leave-one-prompt-out classification machinery of
  `docs/prereg_arm_identifiability.md` §3–§5, with the permutation null of arm labels
  within each (prompt, seed) group, 1000 draws, `random.Random(1337)`, and **no binomial
  test anywhere**;
- the colour feature sets C1, C2, C3 of `docs/prereg_colour_identifiability.md` §2, and
  the `T` versus `T + C3` comparison against the dimension-matched permuted control of
  Amendment 01.

**One addition, justified structurally and not visually.** The current features describe
the palette's *shape* — how many colours, how concentrated, how saturated — and its mean
position. **Nothing encodes how far the palette spreads.** Two images can share a mean
hue and a cluster count while one holds two opposite hues and the other holds one. That
is a gap in the feature set, provable by reading the feature list, and it is the only
reason this addition is here:

- convex hull area of the palette in the `a*b*` plane, pixel-fraction weighted;
- the palette's diameter (largest CIEDE2000 between any two entries);
- circular variance of hue, and mean chroma `C* = sqrt(a*^2 + b*^2)`, reported separately.

Four features. They enter as a fourth colour set **C4** and are tested exactly like the
others.

## 7. Decision rules — frozen

**Question 1, identifiability.** 20-class leave-one-prompt-out accuracy against the
permutation null, Holm-corrected alongside the 2-class contrasts.

- Above the null at Holm `p < 0.05` -> **every perturbation carries a signature**, and the
  per-class recall table says whether all 20 do or only some. The §9 guards of
  `docs/prereg_arm_identifiability.md` apply: one class carrying it, or one fold carrying
  it, and no claim is promoted.
- Not above -> signatures are not decodable at 20 classes from these features, stated
  that way, with the sentence that this is a result about the features as much as about
  the perturbations.

**Question 2, where colour lives.** For each region, the colour displacement raw and as a
ratio to the total (§3), averaged over its two draws, with the prompt as the unit and the
exact sign-flip test across prompts.

- A region's ratio significantly above the others at Holm `p < 0.05` **and consistent
  across both draws** -> that region is where colour lives.
- Significant on one draw and not the other -> `ambiguous`. Two draws cannot distinguish
  a region effect from a draw effect when they disagree, and this design admits that in
  advance.
- Nothing significant -> colour is not localised to a region at this resolution.

## 8. What would kill this

- Phase 1 shows the derivation failing or the rescaling not converging for some regions:
  those regions are dropped, reported, and the design proceeds with fewer — never with a
  substitute chosen after seeing anything.
- The output displacements vary so much between regions that §5's factor-of-three gate
  fires: the study becomes a study of sensitivity, and says so.
- Fewer than 8 prompts are rendered: identifiability is descriptive only.
- The two draws disagree on every region: the design has no power to separate region from
  draw, and the honest outcome is that 2 draws was not enough.

## 9. Outputs

- `data/perturbation_atlas_regions.csv` — the ten regions, written and shown **before**
  any preset is derived.
- `data/perturbation_atlas_calibration.csv` — per preset: region, draw, alphas, measured
  displacements, convergence residual. Same columns as
  `data/chaos_presets_calibration.csv`.
- `data/perturbation_atlas_images.csv` — the render manifest.
- `data/perturbation_atlas_features.csv` — the 23 features plus C1–C4.
- `data/perturbation_atlas_tests.csv` — every test, with phase, corpus, feature set,
  classifier, guard flags and verdict named in each row.

No figure is registered and no page is written in the same run that produces these files.
