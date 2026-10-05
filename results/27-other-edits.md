---
id: 27-other-edits
title: "Appendix A: other kinds of edit"
status: ambiguous
stage: exploratory
date: 2026-10-05
preregistration: null
supersedes: []
pitfalls: [87, 90]

corpus:
  renders: 1730
  prompts: 54

claims:
  - id: derangement-sign-decides-the-hatching
    status: holds
    statement: >
      Reordering whole blocks inside the checkpoint crosses the hatching strokes when pushed one
      way and runs them parallel when pushed the other, and the sign decides which.
    evidence: >
      Pre-registered in notebook page 06, on 16 prompts sharing nothing with the corpus of the
      observation: 16 of 16 prompts and 79 of 80 image pairs in the predicted direction, Holm p
      9.2e-5 at the permutation floor.
    anchor: "#the-hatching-axis"
  - id: derangement-enlarges-the-subject
    status: holds
    statement: >
      A block-reordering edit makes the subject take more of the frame, more so at the higher
      dose, on styles that did not exist when the prediction was frozen.
    evidence: >
      Pre-registered in notebook page 03: geometric mean area ratio 1.234 across 10 new styles, 9
      of 10 above 1, Holm-corrected p 0.018 to 0.035. Whether the structure or the size of the
      edit causes it is open: the control that separates them was not rendered.
    anchor: "#the-subject-grows"
  - id: permutation-brings-out-what-was-asked
    status: ambiguous
    statement: >
      A block permutation makes an attribute the prompt asks for, and the model usually drops,
      appear in almost every render, while a sign scramble moving the weights exactly as far
      does nothing.
    evidence: >
      Exploratory, scored by me with the condition visible: 19 of 20 seeds against 1 of 20 for
      the stock model and 1 of 20 for the scramble. One prompt family; the test of generality
      was designed and never run.
    anchor: "#a-curiosity-attributes-that-appear"
---

# Appendix A: other kinds of edit

> **Ambiguous** · 1730 renders · results from the exploratory notebook, a different kind of edit
> [← all results](README.md#what-holds-and-what-does-not)

> **The direction I'm chasing.** Before single blocks, this project edited the weights in other
> ways: reordering whole blocks inside the checkpoint, permuting them, scrambling signs. Some of
> those results passed pre-registered tests, and one produced an observation worth keeping.
>
> **What would kill it.** Nothing new is tested here. The appendix only reports, with their
> status, results that live in the exploratory notebook.
>
> **Where we are.** Two pre-registered results hold for block reordering. One observation —
> attributes appearing that the model normally leaves out — is kept as a curiosity, with its
> weaknesses stated.

## In two minutes

These edits are not single-block scaling. A block derangement swaps the weights of whole blocks
with one another, scaled by a dose; a permutation reorders them; a sign scramble flips signs so
that the weights move exactly as far without any structure. They are reported here because two
of their results are pre-registered and replicated, and because one of them tells something about
what a weight edit can bring into a picture. The full pages, with figures, data and
reproducibility blocks, are in the exploratory notebook.

## The verdict

Block derangement has two confirmed effects: the sign of the edit decides whether hatching strokes
cross or run parallel (16 of 16 prompts), and the edit enlarges the subject in the frame (9 of 10
new styles). A permutation brought out an attribute the prompt asked for and the model usually
leaves out, in 19 of 20 seeds; it is an observation, not a result, and is boxed as such below.

## Why I might be wrong

* **These are a different family of edits** from the rest of the report. Nothing here says
  anything about single blocks.
* **The hatching measure was not checked against the calibrated preset**, which moves it the
  other way; for that preset the measure may not track hatching at all (notebook page 06).
* **The enlargement may be a matter of size, not structure.** The scramble at equal distance was
  not rendered.
* **The attribute observation was scored by me, with the condition visible,** on one prompt family.

## The data

### The hatching axis

In a comic-style corpus, block derangement pushed positive crossed the hatching strokes and pushed
negative ran them parallel. A pre-registered test on 16 new prompts confirmed the sign: crosshatch
entropy +0.288, 16 of 16 prompts, 79 of 80 pairs. The same test overturned the third family of the
prediction — the sign scramble's exploratory effect did not come back (5 of 16 prompts). Full page:
[notebook page 06](../notebook/06-the-hatching-axis.md).

### The subject grows

Pre-registered on ten styles that did not exist when the prediction was frozen: under block
derangement at double dose the subject's area grows by a geometric mean of 1.234, in 9 of 10
styles, with all three predicted signs correct. The same round measured the blinding of the eye
pass and found it failed ([page 20](20-method.md#why-the-eye-pass-is-declared-open)). Full page:
[notebook page 03](../notebook/03-what-ends-up-in-the-picture.md).

### A curiosity: attributes that appear

> **Observed, not established.** A prompt asked for "small barnacle-like clusters studding one
> earlobe". The stock model drew them in 1 of 20 seeds; a block permutation drew them in 19 of 20;
> a sign scramble moving the weights exactly as far (D = 0.0538) drew them in 1 of 20. On a
> separate corpus — a rally car in a jungle, eight drawing styles, no lights named in the prompt —
> lit headlights went from 10 of 35 at baseline to 31 of 38 under one edit and to 0 of 39 under
> another.
>
> **Its weaknesses.** A different kind of edit from the rest of this report. The barnacle round
> was scored by me with the condition visible. The headlights were scored blind, but on the very
> renders that produced the observation; the exact test is at its floor (p = 0.031, Holm 0.19).
> The pre-registered confirmation on a second corpus could not decide anything: 9 of its 10
> prompts never lit a headlight in any condition. One prompt family; the test of generality was
> designed and never run.

What makes it worth keeping is the control: the same distance in weight space, without structure,
does nothing. How the weights move mattered, not how far. Full page:
[notebook page 02](../notebook/02-attribute-emergence.md).

### Reproducing this

```yaml
model:
  checkpoint: krea2_turbo_bf16.safetensors
  weight_dtype: default
  sha256: not recorded — the file is outside the repository
sampling:
  source: each notebook page's own reproducibility block (pages 02, 03, 06)
tuner:
  node: ArthemyKrea2PresetLoader (preset JSON files in presets/)
  version: recorded per page in the notebook
  mode: preset_json
prompts:
  source: notebook pages 02, 03 and 06
seeds: as recorded on each notebook page
conditions:
  - name: block derangement, block permutation, sign scramble, calibrated preset
    measured_D: recorded per condition on each notebook page (for example 0.0538 for the norm-matched scramble)
outputs:
  source: notebook pages 02, 03 and 06
analysis:
  source: notebook pages 02, 03 and 06
```

## Provenance

* **Renders.** notebook page 02 (920), notebook page 03 (250), notebook page 06 (560).
* **Pre-registrations:** `docs/prereg_hatching_axis_stage7.md` (page 06),
  `docs/prereg_stage12_ingrandimento.md` (page 03); `docs/prereg_attribute_emergence_stage7.md`
  (page 02, the generality test that was never run).
* **Pages:** [02](../notebook/02-attribute-emergence.md),
  [03](../notebook/03-what-ends-up-in-the-picture.md), [06](../notebook/06-the-hatching-axis.md).
