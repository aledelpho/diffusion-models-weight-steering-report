---
id: 26-what-did-not-work
title: What did not work, and the limits of everything else
status: overturned
stage: exploratory
date: 2026-10-05
preregistration: null
supersedes: []
pitfalls: [87, 88, 89, 90]

corpus:
  renders: 295
  prompts: 2
  seeds: [2718281, 3141592, 1618033]

claims:
  - id: strong-centre-pushes-hold-the-line
    status: overturned
    statement: >
      Pushed to dose 0.500, the macro-block sliders Block_4 and Block_1 move the picture far from
      the baseline while keeping its line work, and are the best operating points found.
    evidence: >
      Published from two statistics, then retracted the next day when the renders were opened:
      Block_4 + at 0.500 leaves no subject, only a crumpled-stroke texture; Block_1 + at 0.500 is
      colour confetti. Block_4 + is already broken at 0.350.
    anchor: "#the-best-doses-by-the-statistic"
  - id: structure-coherence-tracks-damage
    status: overturned
    statement: >
      Structure coherence, a statistic of oriented line work, can rank edits by how much of the
      drawing they preserve.
    evidence: >
      Pre-registered eye veto: 7 agreements in 9 resolved pairs against a threshold of 8 in 12.
      Both disagreements are one condition, Block_6 + 0.080, which the statistic scores above
      its baseline and which I and six blind model observers call broken; Block_1 - 0.500 is
      the same case. The sign is wrong, not the size.
    anchor: "#a-measure-with-the-sign-wrong"
  - id: centre-of-the-stack-yields-differently
    status: overturned
    statement: >
      The central macro-blocks give way under a push in a different way from the two at the ends
      of the stack.
    evidence: >
      Pre-registered primary of the centre-push bench: T = +0.053, p = 0.19 over 495
      relabellings, with the range guard passed, so a null and not an inconclusive. Block_5 sits
      in the centre and gives way hardest of all.
    anchor: "#the-centre-is-not-special"
  - id: clip-delta-separates-semantic-from-structural
    status: overturned
    statement: >
      The difference between how consistent an edit's CLIP direction is on one prompt and on many
      prompts separates blocks that route meaning from blocks that filter structure.
    evidence: >
      Audit of an unpublished analysis: no script computes its p-values; doses are mixed under
      one key; the measure tracks how alike the images are; its second-ranked semantic router,
      blk26 +, lays the same mosaic of colour cells over any content.
    anchor: "#semantic-routing"
---

# What did not work, and the limits of everything else

> **Overturned** · 295 renders · retractions and the limits of this report
> [← all results](README.md#what-holds-and-what-does-not)

> **The direction I'm chasing.** A report that shows only what held invites the reader to wonder
> what was left out. This page collects the claims this project made and then lost, how they were
> lost, and what the remaining pages cannot say.
>
> **What would kill it.** A retraction stated more softly than the claim was, or a limit the
> other pages hide.
>
> **Where we are.** Four claims are withdrawn here. Every one of them was made from a statistic
> and undone by opening the images. That pattern is why every confirmatory page of this report
> puts the eye pass first.

## In two minutes

On 2026-09-28 the analysis of the centre-push bench, written by the assistant I work with,
recommended two edits as the best operating points of the project: the macro-block sliders
`Block_4` and `Block_1` pushed to 0.500. Two statistics said they moved the picture far (V,
distance from the baseline in units of seed noise) while keeping its line work (L, structure
coherence). Nobody had opened those renders. I had been saying the images were breaking; the
analysis kept answering with numbers.

![The two doses a statistic ranked best, Block_4 and Block_1 positive at 0.500, are a crumpled-stroke texture and colour confetti with no subject left.](../assets/26-what-did-not-work/F26.1_destroyed_by_the_statistic.webp)

Opened at my prompting the next day, both are destroyed. A destroyed picture is far from its baseline, so V is high; and a
regular texture is oriented line everywhere, so L is high too. High V with high L meant "destroyed
into a regular texture". The bench proposed to push them further was withdrawn.

## The verdict

Four claims are overturned: that strong pushes of two macro-blocks keep the drawing; that the
structure-coherence statistic can tell damage from steering; that the centre of the stack gives
way differently from its ends; and that a CLIP-based delta separates "semantic" from "structural"
blocks. The common cause is a statistic read without the images. Every result that survives in
this report was scored after an eye pass deposited in advance — which makes that eye, a single
observer who knows the conditions, the largest limit of the report.

## Why I might be wrong

* **The retractions rest on the same eye** whose limits are listed below. For the eye veto, six
  blind model observers agreed with me on every pair both could resolve.
* **Some of these statistics may be repairable.** Structure coherence at a smaller window might
  flip the two units it gets wrong; that has not been run.
* **The centre-push null concerns macro-blocks**, groups of consecutive blocks, not single blocks.

## The data

### The best doses by the statistic

| macro-block, positive | V at 0.500 | L at 0.500 | what the render shows |
|---|---|---|---|
| `Block_4` | 3.28 | 1.204 | no subject; crumpled-paper texture of dense black strokes |
| `Block_1` | 3.84 | 1.058 | no subject; colour confetti |

Arm means over prompts and seeds (`docs/centre_push_result.md` §4); the figure shows the unit
means of one prompt (`data/centre_push_units.csv`). At 0.350, `Block_4` + already flattens faces
into masks; `Block_1` + at 0.350 on this prompt and seed keeps the blacksmith intact, framed
closer. The retraction is in `docs/centre_push_result.md` §4, where the original table is kept and
struck through.

### A measure with the sign wrong

The centre-push bench had a pre-registered eye veto: twelve pairs of renders, and for each I said
which was more broken. I resolved 9 and agreed with L on 7, below the registered 8 of 12, so the
label "L not validated by eye" applies. Seven of nine is not a rout. The rout is in the two
disagreements: both are `Block_6` + 0.080, which L scores above its own baseline and which I, and
six blind model observers in both orientations of the sheets, call broken. `Block_1` − 0.500 is
the same case (L 1.02–1.03, broken in both pairs). A statistic that says a picture gained
structure on the condition three independent looks call damaged has the sign wrong.

### The centre is not special

The bench's primary asked whether the four central macro-blocks give way under a push differently
from the two at the ends. T = +0.053, p = 0.19; the range guard passed, so this is a null.
`Block_5`, in the centre, gives way hardest of all; `Block_1`, at an end, less than five of the
eight central arms. A post hoc reclassification of `Block_5` as an end gives p = 0.02 and is
recorded as such, not as the verdict. The single-block map on [page 21](21-block-map.md) shows why
macro-blocks were the wrong unit: they cut across the groups that push together.

### Semantic routing

An analysis written by another assistant, never published, ranked 56 single-block arms by the
difference between how consistent an arm's CLIP-embedding change is across ten images of one
prompt and across 26 images of different prompts, and read a large difference as a "semantic
router". The audit (`docs/semantic_routing_audit.md`) found:

* no script in the repository computes the p-values it quotes, and its survivor count is 12 in
  the text and 16 in the summary;
* doses are not part of the key, so different doses of one arm are mixed or silently dropped;
* the difference measures how alike the images are: ten renders of one character against 26
  different scenes; every visible edit is expected to score positive;
* its second-ranked "semantic router", blk26 +, lays the same mosaic of colour cells over any
  content, white background included — the least semantic effect in the set.

What survives is each column on its own: for a fixed content most arms move the CLIP embedding
the same way whatever the word order ([page 24](24-wording.md#word-order)), and the arms most
stable across 26 different scenes are grain, blur and texture.

### What the numbers could not see

[Notebook page 11](../notebook/11-what-the-numbers-could-not-see.md) records three more cases.
Five conditions recommended from displacement statistics ranked 75th to 80th of 80 on structure
coherence; the condition picked by eye ranked 12th. An edit removed all colour from a leaf while
leaving the leaf intact, in 9 of 20 fresh seeds and 0 of 20 controls, and never when the prompt
named a colour — an open lead on which colours an edit can reach. A generality test for that
effect was run on subjects whose colour was never in doubt, so its null meant nothing.

The style-direction result of [notebook page 09](../notebook/09-style-direction.md) is also
overturned; it is discussed beside the result it seems to contradict, on
[page 23](23-prompt-family-presets.md#against-an-earlier-overturned-result).

### Lessons kept as rules

* **No sentence about how a render looks without opening it** at 1:1. When the eye and a statistic
  disagree, the statistic is the suspect (pitfall 90).
* **A distance from the baseline cannot tell steering from damage.** A destroyed image is far.
* **Before claiming that something has not been done, search for it** (pitfalls 87, 88).
* **Before fixing a threshold on the agreement of two measured things, measure how well each agrees
  with itself** (pitfall 89).

### Limits of this report

* **One model.** Krea-2 only; whether any of this transfers to another architecture is untested.
* **One observer, who knows the conditions.** Every eye pass is mine; hashed names do not blind me
  (page 20). All images are published so that the eye pass can be repeated.
* **Small confirmatory samples.** 16 to 40 cells per test; seven cells for the matched comparison
  of page 22.
* **Doses calibrated on single images.** Some are too strong for a preset (page 23).
* **One test is inconclusive by its own rule** (page 24); the weights result is marginal
  (page 21); the middle blocks' coherence is seen by eye only (pages 23, 25).
* **Not run:** a forward-pass measurement of each block's write into the residual stream; a
  clean-up pass after a preset; the character-consistency test proposed on page 23.

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
tuner:
  node: ArthemyKrea2ModelTuner
  version: not recorded — the tuner is a separate repository
  mode: macro-block group gains Block_1 … Block_6
prompts:
  file: data/centre_push_plan.csv
  ids: [P01, P02]
seeds: [2718281, 3141592, 1618033]
conditions:
  - name: Block_1 … Block_6, both signs, doses 0.080, 0.200, 0.350, 0.500
    measured_D: not measured; V is reported in units of the seed noise of the same prompt
outputs:
  folder: benchmark_centre_push/renders
  manifest: data/centre_push_plan.csv
analysis:
  script: experiments/analyze_centre_push.py
  sha256: 53e00f1353f070aa35be907fe4503b6c715528b962980786ced4d810b5d3ee6a
  produces: data/centre_push_units.csv, data/centre_push_tests.csv, data/centre_push_veto_result.csv
```

## Provenance

* **Renders.** benchmark_centre_push (295).
* **Pre-registrations:** `docs/prereg_centre_push.md`, `docs/prereg_centre_push_model_eye.md`.
* **Result documents and retractions:** `docs/centre_push_result.md` §4,
  `docs/centre_push_eye_veto_result.md`, `docs/semantic_routing_audit.md`.
* **Pitfalls:** `docs/errors_log.md`, `docs/_pitfalls_88_da_inserire.md`,
  `docs/_pitfalls_89_da_inserire.md`, `docs/_pitfalls_90_da_inserire.md`.
* **Related notebook pages:** [09](../notebook/09-style-direction.md),
  [11](../notebook/11-what-the-numbers-could-not-see.md).
