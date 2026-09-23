---
id: 10-all-blocks-clean
title: All six block groups under matched rotation
status: open
stage: exploratory
date: 2026-09-23
preregistration: null
supersedes: []
pitfalls: [4, 10, 15, 30, 68, 72]

corpus:
  renders: 294
  prompts: 2
  seeds: [1618033, 2718281, 3141592]
  blocks: 6

claims:
  - id: response-grows-monotonically-with-angle
    status: open
    statement: >
      Response grows monotonically with rotation angle for every block group, with the output group
      (B6) moving the image most and the input group (B1) second, while middle groups remain
      substantially weaker.
    evidence: "B6 runs 0.63 / 1.65 / 3.71, B1 runs 0.12 / 0.40 / 0.90, middle groups 0.07 to 0.49 in data/all_blocks_clean_v2_response_by_block.csv."
    anchor: "#the-monotonic-response-across-angles"
  - id: specialization-disagrees-with-separability
    status: open
    statement: >
      The chroma/shape specialization ratio makes B1 and B6 the closest of all fifteen block pairs,
      yet pairwise separability tests put B1-B6, B1-B2, and B1-B4 at the exact permutation floor
      with similar cosines.
    evidence: "Gap 0.0073 (p = 0.067) in data/specialisation_vs_proximity.csv vs floor p = 0.03125 in data/all_blocks_clean_v2_separability.csv."
    anchor: "#chroma-shape-ratio-versus-separability"
  - id: output-lead-survives-dose-normalisation
    status: open
    statement: >
      The output group's lead over the input group is not an artefact of rotating every group
      by the same angle: correcting for the displacement each group actually received widens
      the lead instead of closing it.
    evidence: "B6 receives 0.740 of B1's displacement at a common angle, so the ratio 5.35 / 4.16 / 4.13 as rendered becomes 7.23 / 5.62 / 5.58 per unit of displacement, in data/sensitivity_by_block.csv."
    anchor: "#the-same-angle-is-not-the-same-dose"
---

# All six block groups under matched rotation

> **Open** · 294 renders · 2 prompts · 3 seeds · 2026-09-23
>
> * **The direction I'm chasing.** I wanted to map weight rotation across the full depth of the network -- not just comparing the extreme ends B1 and B6, but observing how all six block groups respond across three calibrated angles on clean, HUD-free renders.
> * **What would kill it.** If intermediate blocks showed no coherent response to rotation angle, or if steering directions collapsed into an undifferentiated drift identical across all blocks.
> * **Where we are.** Two statistics on the exact same 294 clean renders point in opposite directions: the chroma-to-shape ratio pairs B1 with B6 as the closest of all fifteen pairs, while pairwise separability puts B1-B6, B1-B2, and B1-B4 all at the exact permutation floor.

## In two minutes

This benchmark evaluates 294 HUD-free renders spanning all six DiT block groups (`B1` through `B6`), two Rademacher scrambled controls (`scrA`, `scrB`), and clean unperturbed baselines. Each condition was rendered across three rotation angles (`low` at 5 deg, `mid` at 10 deg, `high` at 15 deg), both signs (`pos` and `neg`), on two prompt archetypes (`P01`, `P02`) and three seeds.

Two findings emerge from this corpus, and they disagree on what `B1` is doing:

1. **Monotonic response with depth asymmetry.** Across all six block groups, the magnitude of output change grows monotonically with rotation angle. However, sensitivity is heavily concentrated at the output end: group `B6` moves the image by 0.63 at low, 1.65 at mid, and 3.71 at high angle. Group `B1` produces the second largest displacement (0.12, 0.40, 0.90), while the four intermediate groups (`B2` through `B5`) remain clustered at a fraction of that response (ranging from 0.07 to 0.49).
2. **A structural contradiction between specialization and separability.** When computing the ratio of chromatic shift to morphological shape change, `B1` and `B6` appear almost identical: their ratio gap is 0.0073 (permutation p = 0.067 over all 15 block pairs), suggesting they perform a similar functional trade-off at different depths. But testing directional separability tells a different story: at moderate dose (`mid`), `B1` separates from `B6`, `B2`, and `B4` at the exact sign-flip floor (p = 0.03125) with similarly negative cosines (-0.51, -0.48, -0.46). This indicates that `B1` is not uniquely paired with `B6`, but rather occupies an isolated direction distinct from multiple groups.

## The verdict

Both claims remain **Open**. This is an exploratory round with no frozen pre-registration, 2 prompts, and 3 seeds per cell. While the monotonic scaling with angle is unambiguous across every block group, the functional role of the input group `B1` cannot be resolved from this design alone: the aggregate feature ratio suggests common specialization with `B6`, while directional separability treats `B1` as distinct from several middle blocks.

## Why I might be wrong

1. **Two prompts cannot support a general claim about block specialization.** With only `P01` and `P02`, prompt-specific semantic features could dominate the feature vectors, mimicking structural alignment between blocks that would diverge on a broader palette of styles.
2. **The dose sign-flip pitfall (candidate pitfall 72).** In small sample regimes (6 cells per condition), any consistent directional sign across seeds reaches the mathematical permutation floor (p = 0.03125). In earlier benches, opposite rotation doses were caught reaching the exact floor with opposite signs.
3. **Chroma-shape ratios collapse complex multi-dimensional manifolds.** The ratio |norm_A_chroma / norm_A_shape| compresses dozens of extracted metrics into a single scalar. Two blocks could yield identical ratios while pushing completely orthogonal feature subspaces.
4. **The dose normalisation assumes this bench's `B1` and `B6` are the tuner's `Block_1 (All 0-4)` and `Block_6 (All 24-27)`.** That is what `data/matched_rotation_calibration_v4.json` calibrated, and the table above says `B6` spans blocks 23-27. One of the two is wrong, and nothing in the repository settles it: the bench wrote no record of which indices each group covered. `experiments/measure_block_group_displacements.py` writes the indices straight out of the node's own map, which will confirm the normalisation or retract it.
5. **144 of the 294 renders have no manifest row.** `data/rotations_clean_v2_manifest.csv` records the `B1`, `B6`, `scrA` and `scrB` arms -- 150 rows -- and the `B2` through `B5` arms were rendered into the same folder without one (pitfall 30). Their sampler, checkpoint hash and timestamps are unrecorded; only their resolution survives, in the feature tables, and it is 1024x1280 on all 294, so none of this page is HUD-contaminated.

## The data

The 294 renders were analyzed using the standard 23-feature extraction pipeline, isolating the antisymmetric response component $\Delta_A = (\Delta_{\text{pos}} - \Delta_{\text{neg}})/2$ to eliminate static baseline drift.

### The monotonic response across angles

The mean Euclidean norm of the antisymmetric response vector $\|A\|$ increases monotonically across all three rotation angles for every block group:

| Block Group | Low (5°) | Mid (10°) | High (15°) | Layers Spanned |
|---|---|---|---|---|
| **B1** | 0.118 ± 0.047 | 0.397 ± 0.052 | 0.897 ± 0.071 | Blocks 0-4 |
| **B2** | 0.092 ± 0.019 | 0.087 ± 0.034 | 0.134 ± 0.074 | Blocks 5-9 |
| **B3** | 0.170 ± 0.052 | 0.259 ± 0.087 | 0.385 ± 0.121 | Blocks 10-14 |
| **B4** | 0.141 ± 0.042 | 0.183 ± 0.016 | 0.441 ± 0.109 | Blocks 15-18 |
| **B5** | 0.070 ± 0.027 | 0.112 ± 0.029 | 0.166 ± 0.055 | Blocks 19-22 |
| **B6** | **0.634 ± 0.041** | **1.651 ± 0.123** | **3.706 ± 0.223** | Blocks 23-27 |

The output group `B6` exhibits dramatic leverage over the generated pixels, scaling to over four times the displacement of `B1` and over twenty times that of `B5` at high angle.

![The antisymmetric response of each of the six block groups at 5, 10 and 15 degrees, with the standard deviation across the six cells. Every group grows with angle, and at 15 degrees the output group B6 moves the image more than four times further than the next group.](../assets/10-all-blocks-clean/F10.1_depth_profile_by_angle.webp)

### The same angle is not the same dose

The table above is a depth profile of the **bench**, not yet of the model. Every group was
rotated by the same number of degrees, and a rotation by a fixed angle is not a fixed
perturbation: what the weights actually travel is `D = ||dW||_F / ||W||_F`, and it scales with
the rotated group's own norm. This is the confound that decides whether `B6` is more
*sensitive* or merely more *pushed*.

`data/matched_rotation_calibration_v4.json` answers it for the two ends. To reach the same
displacement, `B6` needs a larger angle than `B1`: 2.4723 degrees against 1.8295 at D =
0.0035, and the ratio holds at 1.351370, 1.351431 and 1.351339 across the three calibrated
doses -- constant to five figures, which is what `D` proportional to `sin(theta/2)` predicts
and is the evidence that one angle-independent ratio is legitimate. At a common angle, then,
**`B6` receives only 0.740 of `B1`'s displacement** -- and still moves the image four to five
times further.

Dividing one by the other widens the gap rather than closing it:

| Angle | B6 / B1 as rendered | B6 / B1 per unit of displacement |
|---|--:|--:|
| low (5°) | 5.35x | **7.23x** |
| mid (10°) | 4.16x | **5.62x** |
| high (15°) | 4.13x | **5.58x** |

![B6's response divided by B1's, at each of the three angles, before and after dividing each by the weight displacement the group actually received. Rotating by the same angle pushes B6 only 74 percent as far as B1, so correcting for the dose widens the gap from 4.1 to 5.4 times up to 5.6 to 7.2 times.](../assets/10-all-blocks-clean/F10.2_sensitivity_per_displacement.webp)

Two things are worth noticing and neither is settled here. The lead is **largest at the
smallest angle** and flattens from mid to high, which is what saturation at the output end
would look like; three angles cannot tell saturation from noise. And the normalisation covers
`B1` and `B6` only, because the calibration file covers only those two. `B2` through `B5`
carry `not measured` in `data/sensitivity_by_block.csv` rather than a guess;
`experiments/measure_block_group_displacements.py` reads the checkpoint and fills them in
without rendering anything.

### Chroma-shape ratio versus separability

Evaluating the balance between chromatic shift and structural linework yields the following specialization summary across the six groups:

| Block | Chroma Norm | Shape Norm | Texture Norm | Chroma / Shape Ratio |
|---|---|---|---|---|
| **B1** | 0.8746 | 1.1437 | 0.4386 | **0.7647** |
| **B2** | 0.3519 | 0.2616 | 0.1519 | 1.3455 |
| **B3** | 0.3163 | 0.5407 | 0.3064 | 0.5850 |
| **B4** | 0.5626 | 0.4476 | 0.2087 | 1.2569 |
| **B5** | 0.5554 | 0.5886 | 0.1763 | 0.9436 |
| **B6** | 2.0583 | 2.6662 | 1.8560 | **0.7720** |

The gap between `B1` and `B6` is |0.7647 - 0.7720| = **0.0073**, ranking 1st among all 15 pairwise comparisons (permutation p = 1/15 = 0.067). In contrast, middle groups average a pairwise gap of 0.4324, and end-to-middle pairs average 0.3561.

However, the directional cosine separability test at moderate rotation (`mid`) reveals that `B1` is negatively aligned with multiple groups, reaching the permutation floor across the board:

| Pair | Mean Cosine | Permutation p | Floor |
|---|---|---|---|
| **B1 - B6** | -0.5138 | 0.03125 | 0.03125 |
| **B1 - B2** | -0.4808 | 0.03125 | 0.03125 |
| **B1 - B4** | -0.4618 | 0.03125 | 0.03125 |
| **B4 - B6** | +0.7587 | 0.03125 | 0.03125 |
| **B3 - B6** | +0.4868 | 0.03125 | 0.03125 |

`B1` does not align directionally with `B6`; rather, it points away from `B6`, `B2`, and `B4` alike, showing that identical chroma/shape proportions do not imply shared directional vectors.

### Reproducing this

```yaml
model:
  checkpoint: krea2_turbo_bf16.safetensors
  weight_dtype: default
  sha256: not recorded -- the file is outside the repository
  text_encoder: qwen3vl_4b_bf16.safetensors
  vae: qwen_image_vae.safetensors
sampling:
  sampler: not recorded (needs bench manifest)
  steps: not recorded (needs bench manifest)
  cfg: not recorded (needs bench manifest)
  scheduler: not recorded (needs bench manifest)
  resolution: 1024x1280
tuner:
  architecture: block_rotation
  mode: six block groups, three angles (low=5°, mid=10°, high=15°), both signs
  blocks: [B1, B2, B3, B4, B5, B6]
prompts:
  P01: "Western comics style, sharp ink outlines, crosshatching..."
  P02: "Western comics style, expressive ink strokes, subtle shadows..."
seeds: [1618033, 2718281, 3141592]
conditions:
  - name: B1
    mode: rotation
    angles_deg: [5.0, 10.0, 15.0]
    measured_D: not measured on this bench -- nominal angles fixed at 5°, 10°, 15°. The
      displacement RELATIVE to B1 is 1.0 by construction; see data/sensitivity_by_block.csv
  - name: B2
    mode: rotation
    angles_deg: [5.0, 10.0, 15.0]
    measured_D: not measured -- nominal angles fixed at 5°, 10°, 15°
  - name: B3
    mode: rotation
    angles_deg: [5.0, 10.0, 15.0]
    measured_D: not measured -- nominal angles fixed at 5°, 10°, 15°
  - name: B4
    mode: rotation
    angles_deg: [5.0, 10.0, 15.0]
    measured_D: not measured -- nominal angles fixed at 5°, 10°, 15°
  - name: B5
    mode: rotation
    angles_deg: [5.0, 10.0, 15.0]
    measured_D: not measured -- nominal angles fixed at 5°, 10°, 15°
  - name: B6
    mode: rotation
    angles_deg: [5.0, 10.0, 15.0]
    measured_D: not measured on this bench -- nominal angles fixed at 5°, 10°, 15°. The
      displacement RELATIVE to B1 at a common angle is 0.739984, derived from
      data/matched_rotation_calibration_v4.json; see data/sensitivity_by_block.csv
  - name: scrA
    mode: scramble
    angles_deg: [5.0, 10.0, 15.0]
    measured_D: not measured -- nominal angles fixed at 5°, 10°, 15°
  - name: scrB
    mode: scramble
    angles_deg: [5.0, 10.0, 15.0]
    measured_D: not measured -- nominal angles fixed at 5°, 10°, 15°
  - name: baseline
    mode: identity
    measured_D: 0.0
outputs:
  directory: benchmark_rotations_clean_v2/renders
  manifest: data/rotations_clean_v2_manifest.csv -- 150 of the 294 renders. The B2 to B5
    arms were written into the same folder with no manifest row of their own.
analysis:
  feature_tables:
    - data/all_blocks_clean_v2_style_features.csv
    - data/all_blocks_clean_v2_palette_features.csv
  summary_tables:
    - data/all_blocks_clean_v2_response_by_block.csv
    - data/all_blocks_clean_v2_separability.csv
    - data/all_blocks_specialization_summary.csv
    - data/specialisation_vs_proximity.csv
    - data/sensitivity_by_block.csv
```

## Provenance

* Renders: all_blocks_clean_v2 (294)
* Feature extraction: `data/all_blocks_clean_v2_style_features.csv` and `data/all_blocks_clean_v2_palette_features.csv`
* Analysis scripts: `experiments/run_recovery_and_analysis.py` (phase 6 and phase 7), `experiments/sensitivity_curve.py` (the dose normalisation), `experiments/measure_block_group_displacements.py` (the displacements themselves, not yet run)
* Data files: `data/all_blocks_clean_v2_response_by_block.csv`, `data/all_blocks_clean_v2_separability.csv`, `data/all_blocks_specialization_summary.csv`, `data/specialisation_vs_proximity.csv`, `data/sensitivity_by_block.csv`
* Figures: F10.1 and F10.2, both registered in `experiments/figures.yaml` and built by `experiments/notebook_charts.py`
* Pitfalls that apply: 4, 10, 15, 30 (two arms sharing an output folder, one of them with no manifest), 68, 72
