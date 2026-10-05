---
id: 21-block-map
title: A map of the 28 blocks
status: open
stage: exploratory
date: 2026-10-05
preregistration: null
supersedes: []
pitfalls: [64, 87, 90]

corpus:
  renders: 1583
  prompts: 26
  seeds: [2718281, 3141592, 1618033, 1234567]

claims:
  - id: ends-keep-the-layout-middle-rewrites-it
    status: open
    statement: >
      Blocks near the output keep the composition of the picture and change its surface; the
      middle of the stack, worst at blocks 8 to 10 pushed positive, rewrites the picture itself.
    evidence: >
      Exploratory, 23 prompts on three benches, doses calibrated by eye. Layout r with the
      baseline 0.88 for blocks 21-27, 0.65 for blocks 05-14; blk09 positive 0.46. Agrees with the
      pre-registered result of notebook page 05 that the cost of a push grows toward the output.
    anchor: "#where-the-layout-holds"
  - id: some-neighbouring-blocks-push-together
    status: open
    statement: >
      Once the change shared by every edit is removed, blocks 08-10, 15-16 and 23-26 pushed
      positive change the picture in the same direction, and blocks 22-27 pushed negative do too.
    evidence: >
      Groups formed on the 12 styles prompts and found again on 11 prompts of two other benches,
      with other seeds and other doses (residual correlation +0.15 to +0.37); the group 02-05 did
      not come back (+0.01 to +0.14). Not pre-registered.
    anchor: "#blocks-that-push-together"
  - id: stability-is-visible-in-the-weights
    status: ambiguous
    statement: >
      How much a block rewrites the picture can be read, in part, from the spectra of its own MLP
      weights, beyond what its depth explains.
    evidence: >
      Pre-registered (C46). Best Spearman rho 0.615 with depth removed, above the Bonferroni
      threshold 0.57, so the rule says supported; leaving one block out moves it between 0.50 and
      0.70, so a single block can undo it. Correlational, 28 blocks, one checkpoint.
    anchor: "#what-the-weights-show"
  - id: ends-change-properties-middle-changes-content
    status: open
    statement: >
      The blocks at the two ends of the stack change properties of the picture — colour, grain,
      sharpness — in the same way on every picture; the middle blocks change what is depicted, and
      differently on each picture.
    evidence: >
      At one dose for all blocks, a block is recognisable as itself on another picture only at the
      ends (positive: blocks 0, 1, 25, 26, 27; pre-registered, p = 0.0015). The ends keep the layout
      (0.88 for 21-27) and the middle rewrites it (0.65 for 05-14); middle blocks change the content
      most by DINOv2 (page 25). Counted in rendering statistics, however, the ends move more of
      them at once (effective number 9.6 for 21-27 against 7.5 for 05-14), so "fewer things" holds
      for kinds of property, not for statistics.
    anchor: "#what-the-ends-change-and-what-the-middle-changes"
  - id: output-end-breaks-first
    status: open
    statement: >
      At the same dose, the blocks near the output reach visible artefacts first, while most middle
      blocks show none; the middle has room before artefacts but drifts toward pictures that are
      clean and incoherent.
    evidence: >
      My artefact labels at dose 0.350, three prompts, one seed: blocks 4 to 11 OK in both
      directions; positive, strong artefacts on 19, 21, 22, 24 and 25, broken on 26 and 27. Agrees with the
      pre-registered result that the cost of a push grows toward the output (notebook page 05). The
      split into hard and soft limits is an observation, not measured.
    anchor: "#how-far-each-block-can-be-pushed"
  - id: by-eye-guide-to-each-block
    status: open
    statement: >
      A provisional, by-eye description of what each of the 28 blocks does in each direction,
      offered as a starting point for anyone who wants to try the tuner, not as a measured result.
    evidence: >
      Written by me while looking at the v4 bench (five prompts, one seed) on a page that also
      showed the 18 prompts of the styles and v3 benches. Where a measurement touches an entry,
      it agrees on blocks 00, 22, 23 and 27, partly on 01, and the statistic is the suspect on 26.
      Most Style-band entries have no measurement at all.
    anchor: "#a-starting-guide-what-each-block-seems-to-do"
---

# A map of the 28 blocks

> **Open** · 1583 renders · exploratory map, one pre-registered test on the weights
> [← all results](README.md#what-holds-and-what-does-not)

> **The direction I'm chasing.** If knobs live in the weights, they should live in particular
> places. I pushed every block on its own, in both directions, on 23 prompts, and wrote down
> what each one does, so that the confirmatory tests on the other pages had somewhere to aim.
>
> **What would kill it.** A stack where every block does a bit of everything, with no region
> that behaves differently from the others and nothing that comes back on a second set of
> prompts.
>
> **Where we are.** The two ends behave like controls on the surface of the picture; the middle
> rewrites what is depicted. A few groups of neighbouring blocks push the same way on a second
> set of prompts. This page is a map, not a test: only the weights claim was pre-registered,
> and it passed by a thin margin.

## In two minutes

The atlas behind this page is three benches — 12 prompts in eight styles, 6 prompts at two
seeds, 5 prompts with comic pages and crowns seen from above — with every block pushed on its own
in both directions at a dose I calibrated by eye. Looking at the sheets, the stack sorts itself
into four bands: Base (00–01, grain and detail), Style (02–18, light, form, abstraction), Details
(19–22) and Correction (23–27: saturation, sharpness, grain). My block-by-block definitions are
in `data/single_blocks_v4_definitions_alessandro.md`.

![Blocks 21 to 27 keep the layout of the picture (layout r around 0.88) while the middle of the stack, worst at block 9 positive, rewrites it.](../assets/21-block-map/F21.1_layout_stability_by_block.webp)

What the eye saw first was a split between blocks that redraw and blocks that re-shoot. Blocks
02–07 pushed positive keep frame, pose and props and redraw the subject (a younger face, a
cleaner line, smoke over the forge). Blocks 08–09 pushed positive change the picture itself: a
crown seen from above turns to a side view, the blacksmith becomes a photograph, the selfie
changes identity.

## The verdict

The ends of the stack are where a single block behaves like a surface control: the layout stays,
and colour, grain or sharpness move. The middle is where single blocks change content — viewpoint,
identity, medium — and are least predictable. A few groups of neighbouring blocks push in the
same direction on a second set of prompts. The split between stable and unstable blocks is
partly visible in the weights themselves, but that result is marginal.

## Why I might be wrong

* **This is a map, drawn after looking.** The bands are my reading of the sheets; only the
  weights test (C46) was frozen before the data.
* **The doses differ by block and by bench.** A block that looks stable may have been pushed less.
* **64×80 sees layout and colour, not grain.** The groups say nothing about blocks 00, 01, 21, 26
  and 27, whose effects are fine texture.
* **The replication of the groups is weak.** Second set of prompts, other seeds and doses, but
  the groups were chosen after seeing the first set and the measure was the same.
* **The weights result rests on n = 28** and one checkpoint, and a single block can flip it.
* **The guide to each block is one observer's shorthand.** It was written from a few prompts, at
  one dose per direction, by someone who knew which block he was looking at. Several entries are
  simplifications, some will turn out to be wrong, and the effect of many Style-band blocks
  changes with the prompt.

## The data

### Where the layout holds

Layout r is the correlation of the lightness channel with the baseline at 64×80 (1 = the same
composition), averaged over 23 prompts and both signs (`data/block_colour_layout.csv`):

| blocks | 00–01 | 02–04 | 05–14 | 15–20 | 21–27 |
|---|---|---|---|---|---|
| layout r | 0.75 | 0.75 | 0.65 | 0.73 | 0.88 |

The bands hold at the two ends and blur in the middle; the sharpest break is at the Correction
end, not between Style and Details. Positive pushes of blocks 08, 09 and 10 are the least stable
of all (0.55, 0.46, 0.51). This agrees with two pre-registered results of the exploratory
notebook: [every push costs fine texture and the cost grows toward the output](../notebook/05-knob-or-cost.md),
and [two places pushed the same distance move the picture in distinguishable directions](../notebook/08-block1-vs-block6.md)
— position, not only distance, decides what an edit does.

### What the ends change, and what the middle changes

A separate bench pushed every block by the same amount, 0.350, on three prompts, so that blocks
can be compared at equal dose. The test asked, before measuring, whether a block's change on one
picture is recognisable as that block's change on another. On the positive side only five blocks
are: 0, 1, 25, 26 and 27 — the two ends of the stack (p = 0.0015; on the negative side 0, 8, 20 and
27). Everywhere else, a block does something reproducible on the same picture but something
different on another (`docs/single_blocks_atlas_result.md`, `data/single_blocks_tests.csv`).

Put together with the layout above and with DINOv2 on page 25, the picture is consistent: the ends
act on **properties of the image** — colour, grain, sharpness, softness — and act the same way
whatever is depicted; the middle acts on **what is depicted** — viewpoint, shape, identity,
realism — and how it does so depends on the picture. The two sheets in the guide below show it
directly: the crown stays the same crown under blocks 21 to 27 and becomes another object under
many middle blocks.

One measure does not fit the simple wording "the ends change fewer things". Counting how many of 29
rendering statistics an edit moves at once (the participation ratio of the change, at dose 0.350),
the ends move more of them, not fewer: median 9.6 for blocks 21–27 and 10.1 for 00–01, against 7.5
for 05–14 (`data/block_change_breadth.csv`). Grain and sharpness move many texture statistics
together. The ends change fewer *kinds* of property, through many statistics; the middle changes
content, which rendering statistics only partly see.

### Blocks that push together

For each pair of arms on the same prompt, the change each makes to the picture is correlated
pixel by pixel after removing the prompt's common mode — the part of the change that every edit
shares, simply because any edit moves the picture away from that particular baseline. Before
removal the two signs of one block correlate positively on 27 of 28 blocks; after it, negatively
on 25 of 28.

![Once the change every arm shares is removed, positive arms 08-10 push the same way, 23-26 push the same way, and the early-middle blocks push against the late ones.](../assets/21-block-map/F21.2_residual_overlap_matrix.webp)

| group | styles, 12 prompts | other benches, 11 prompts |
|---|---|---|
| 08 · 09 · 10, positive | +0.24 to +0.27 | +0.15 to +0.23 |
| 23 · 24 · 25 · 26, positive | +0.21 to +0.51 | +0.23 to +0.37 |
| 15 · 16, positive | +0.17 | +0.21 |
| 02 · 03 · 04 · 05, positive | +0.19 to +0.23 | +0.01 to +0.14 — **does not come back** |
| block 05 against block 24, positive | −0.23 | −0.22 |

Negative arms 22–27 form one group as well (most pairs +0.19 to +0.54). Blocks 25 and 26 are
the exceptions where both signs push the same way even after removal — the two blocks I had
already marked as damaging in both directions. The tuner's six macro-block sliders (`Block_1` …
`Block_6`, each a run of consecutive blocks) cut across two of these groups: 08–10 straddles
`Block_2`/`Block_3` and 23–26 straddles `Block_5`/`Block_6`. A single block is the finer lever.

### What the weights show

A pre-registered test (C46) asked whether any of 34 statistics of a block's weight matrices
tracks how much the block rewrites the picture, beyond what depth alone explains. The
analyst's registered prediction was that depth would explain everything; it failed.

![The blocks that rewrite the picture most, 08 and 09, have the largest singular value of their MLP gate in the whole stack; the late blocks that keep the layout have the smallest.](../assets/21-block-map/F21.3_weights_vs_stability.webp)

| statistic | ρ raw | ρ with depth removed |
|---|---|---|
| `mlp.down.sigma1` | −0.41 | **−0.615** |
| `mlp.gate.stable_rank` | +0.53 | **+0.613** |
| `mlp.down.stable_rank` | −0.36 | **+0.585** |

Three statistics pass the Bonferroni threshold of 0.57; leaving one block out keeps them between
0.50 and 0.70. Two readings are worth recording. Blocks 08–09 have the strongest single direction
in their MLP gate in the stack (σ₁ 113 and 130 against 34–97 elsewhere). Blocks 26–27 write
through almost one direction (stable rank of the attention output 26 and 13 against 100–260
elsewhere), which is one mechanical reading of a knob. Block 23, the saturation knob of page 22,
does not stand out on any of the 40 values.

### How far each block can be pushed

At the same dose, blocks do not break at the same point. I labelled every edit of the equal-dose
bench by the artefacts I could see, from OK to BROKEN
(`data/single_blocks_eye_artifacts_alessandro.csv`).

![At the same dose 0.350 blocks 4 to 11 show no artefact in either direction, while most blocks from 19 to 27 pushed positive show artefacts and blocks 26 and 27 break the picture.](../assets/21-block-map/F21.4_sensitivity_map.webp)

The output end is the most sensitive: pushed positive, blocks 19, 21, 22, 24 and 25 show strong
artefacts at 0.350 and blocks 26 and 27 destroy the picture; their negative side is safer. This matches a
pre-registered result of the exploratory notebook — [the cost of a push grows toward the output, and
the tail is rectified](../notebook/05-knob-or-cost.md): positive pushes wreck it, negative ones barely
move it. The middle, from block 4 to 11, shows no artefact at this dose in either direction. These
labels became the starting doses of the later benches: up to 0.45–0.55 in the middle, 0.05–0.15
on the positive side of blocks 26 and 27.

Two kinds of limit show up, and the labels above see only the first:

* **a hard limit** — artefacts anyone recognises: grain, noise, a mosaic of colour cells, a broken
  frame. It arrives first at the output end;
* **a soft limit** — a picture that stays clean and well rendered but whose drawing has stopped
  making sense: faces flattened into masks, anatomy undone, objects fused or deformed. It is the
  limit of the middle blocks, and the harder one to see, because nothing in the picture looks like
  an error. Page 26 shows one example on a macro-block (faces turned into masks at 0.350).

The soft limit is my observation, not a measurement; no statistic in this project detects it, and
page 26 shows how statistics can read such a picture as an improvement.

### A starting guide: what each block seems to do

> **Read this as a map drawn by hand, not a measurement.** I wrote it while looking at the v4
> bench — four crowns and one comic page at seed 1234567 — on a page that also showed the 18
> prompts of the styles and v3 benches. Each entry is the change I found most evident; Style-band
> blocks do many other things. It is provisional and meant to be expanded and corrected. Its use
> is practical: where to start, roughly where "style" begins, and what to expect from each
> block in each direction.

The same guide in pictures, on two of the v4 prompts: each pair is the block pushed negative and
positive, at the doses below.

![Every block pushed in both directions on a crown seen from above: from block 21 onward the crown stays the same object, while middle blocks turn it into an open ring, a side view or another crown.](../assets/21-block-map/F21.6_guide_crown.webp)

![Every block pushed in both directions on a four-panel comic page: the last blocks change colour, softness and grain of the same panels, the middle blocks redraw the characters and the panels themselves.](../assets/21-block-map/F21.5_guide_comic.webp)

Doses are those of the v4 bench (`data/block_colour_layout.csv`, rows `v4`); they are where
these effects were seen, not safe defaults, and page 23 shows that doses chosen on single images
can be too strong for a preset.

| block | dose − / + | negative | positive |
|---|---|---|---|
| **Base** | | | |
| 00 | −0.20 / +0.25 | more grain, detail, colour variety, colour confetti | soft and hazy: less grain, detail and colour variety |
| 01 | −0.40 / +0.25 | softer colours, subtle textures | patchy colour, flat tints, more grain and detail (the opposite of 00) |
| **Style** | | | |
| 02 | −0.45 / +0.40 | fine textures and micro-detail; less camera control | flat fills, toward close-up, more camera control, colour blocks |
| 03 | −0.55 / +0.40 | less natural, less three-dimensional light | natural, three-dimensional light (changes a lot with the prompt) |
| 04 | −0.55 / +0.55 | fine-grained detail, less abstraction | coarse, merged detail; simplification and abstraction |
| 05 | −0.55 / +0.55 | darker, dirtier, messier | brighter, cleaner |
| 06 | −0.55 / +0.55 | more volume, more organic; fewer colours, less stylisation | more colour, more stylised and artificial; less volume |
| 07 | −0.55 / +0.55 | elements blend less (less concept bleeding), fewer deformations | elements blend more (more concept bleeding), more deformations |
| 08 | −0.55 / +0.55 | more expression and natural poses; less texture realism, less flattening | more texture realism, deformation and flattening; less expression |
| 09 | −0.55 / +0.55 | less realism of volumes and materials | more realism of volumes and materials |
| 10 | −0.45 / +0.45 | more expression (varies with the prompt) | less expression |
| 11 | −0.45 / +0.45 | more camera control, style emphasised; less deformation | more deformation and abstraction; camera control and style lost |
| 12 | −0.45 / +0.40 | more camera control, perspective, imperfections; less deformation | more deformation; less camera control, perspective, imperfections |
| 13 | −0.45 / +0.40 | organic | geometric |
| 14 | −0.55 / +0.40 | details more distinct; less colour contrast, less texture depth | more colour contrast and texture depth; details less distinct |
| 15 | −0.45 / +0.40 | more depth (light, shadow, reflections, translucency), more realistic detail | less depth (simplified, flattened subjects), less realistic detail |
| 16 | −0.45 / +0.30 | more complex textures, more detail, less abstraction | muffled textures, fewer details, more abstraction |
| 17 | −0.45 / +0.40 | less synthesis: less stylised, closer to the prompt | more synthesis: simpler, further from the prompt |
| 18 | −0.45 / +0.30 | more depth and volume | less depth and volume |
| **Details** | | | |
| 19 | −0.45 / +0.25 | subjects shaped by form, more complex detail | subjects shaped by light, less complex detail |
| 20 | −0.55 / +0.45 | parts of the subject blend together | parts of the subject separate, more distinct in colour |
| 21 | −0.45 / +0.25 | finer grain of detail and imperfection | coarser, accentuated grain of detail and imperfection |
| 22 | −0.45 / +0.25 | sharpens and flattens textures | blurs and softens textures (borders on Correction) |
| **Correction** | | | |
| 23 | −0.30 / +0.30 | more saturation | less saturation (page 22) |
| 24 | −0.40 / +0.20 | more colour contrast (flatter, more distinct colours), harsher textures | less colour contrast (softer, more complex colours), gentler textures |
| 25 | −0.45 / +0.25 | less colour blur | more colour blur (damaging in both directions on other benches) |
| 26 | −0.25 / +0.15 | fewer fine textures | more fine texture, adds grain |
| 27 | −0.25 / +0.05 | blurs and darkens | adds grain and lightens, like an aggressive sharpen filter |

Where a measurement touches an entry (`docs/block_groups_and_prompt_order.md` §4, on the
prompt-order images): the statistics agree on 00, 22, 23 and 27; on 01 "opposite of 00" holds for
grain and detail but not for the whole effect; on 26 the spectral statistic says the opposite, and
a 1:1 crop sides with the description — what reads as grain is a mosaic of colour cells. On page
23, blk09 + raised realism by eye on every family, as the guide says; blk17 + read on photographs
as "focus on the subject", which the guide does not anticipate. The other Style-band entries have
not been measured.

### Reproducing this

```yaml
model:
  checkpoint: krea2_turbo_bf16.safetensors
  weight_dtype: default
  sha256: not recorded — the file is outside the repository
sampling:
  sampler: euler_ancestral
  steps: 9
  cfg: 1.0
  denoise: 1.0
  scheduler: simple
  resolution: 1024x1280
  vae: qwen_image_vae.safetensors
  text_encoder: qwen3vl_4b_bf16.safetensors (CLIPLoader type krea2)
tuner:
  node: ArthemyKrea2ModelTuner, after ArthemyKrea2ResetPatcher
  version: not recorded — the tuner is a separate repository
  mode: Real Value, driven by a 34-slot vectors_override (one block at a time)
prompts:
  measured_on: data/block_colour_layout.csv (12 styles prompts, 6 v3 prompts, 5 v4 prompts)
seeds: [2718281, 3141592, 1618033, 1234567]
conditions:
  - name: single block, negative dose, each of 28 blocks
    dose: calibrated by eye per block and per bench
    measured_D: not measured; the dose is a per-block gain, not a calibrated displacement
  - name: single block, positive dose, each of 28 blocks
    dose: calibrated by eye per block and per bench
    measured_D: not measured
outputs:
  folders: [benchmark_single_blocks_styles, benchmark_single_blocks_v3, benchmark_single_blocks_v4, benchmark_single_blocks_atlas]
  manifest: no single committed manifest for all three benches; data/block_colour_layout.csv lists every measured image
analysis:
  scripts:
    - experiments/block_colour_layout.py        # 9b9aea19f1d6f43920cf0cc832d4be23063815d3290723cc4dd7e3bc27147de1
    - experiments/block_effect_overlap.py       # 29853a9f70e6f86987c119d0f74112517cf56e92a3754cb6cf212ca32c4ae188
    - experiments/block_weight_structure.py     # 1df6cc4b4cedf27e99efba52f19cf7318b7a5572f228e53abcd17e900e405645
    - experiments/block_change_breadth.py       # 564ed1578c1c6db997e489241d3cb1991f7ef5859de50c153e15b218bec575b1
  produces: data/block_colour_layout.csv, data/block_effect_overlap_mean.csv, data/block_weight_structure.csv, data/block_weight_structure_test.csv, data/block_change_breadth.csv
```

## Provenance

* **Renders.** benchmark_single_blocks_styles (684), benchmark_single_blocks_v3 (396), benchmark_single_blocks_v4 (332), benchmark_single_blocks_atlas (171).
* **Pre-registration (weights only):** `docs/prereg_block_weight_structure.md`, committed before
  any weight was read.
* **Result documents:** `docs/block_groups_and_prompt_order.md`,
  `docs/single_blocks_exploration_synthesis.md`, `docs/block_weight_structure_result.md`.
* **Observations:** `data/single_blocks_v4_definitions_alessandro.md` (the original, in Italian, of the guide to each block).
