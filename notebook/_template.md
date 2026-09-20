---
id: NN-short-name
title: A title in plain words, not a number
status: open                     # holds | ambiguous | overturned | open
stage: exploratory               # exploratory | confirmatory
date: YYYY-MM-DD
preregistration: null            # docs/prereg_....md — required when stage is confirmatory
supersedes: []
pitfalls: []

corpus:
  renders: 0
  prompts: 0
  seeds: []

claims:
  - id: short-kebab-id
    status: open
    statement: >
      One sentence, in the present tense, that a reader could disagree with.
    evidence: "What it rests on: n, the test, the effect size."
    anchor: "#a-heading-on-this-page"
---

# A title in plain words, not a number

> **Open** · 0 renders · 0 prompts
> [← all experiments](../README.md#what-holds-and-what-does-not)

## In two minutes

Written last, read first. What I wanted to know, what I did, what came out.
Plain language, figures, no mathematics. A curious reader stops here and has understood.

![Alt text written as the claim the figure makes, not as a description of it.](../assets/NN-short-name/F00.webp)

## The verdict

Three to six lines. This is the README row, expanded.

## Why I might be wrong

The reservations, before the data. If this section is short, it is short because there was
nothing more to say — not because it was skipped.

## The data

### How it was measured

### The numbers

### The controls

### Reproducing this

```yaml
model:
  checkpoint:
  sha256:
sampling:
  sampler:
  steps:
  cfg:
  scheduler:
  resolution:
  vae:
tuner:
  node:
  version:
  mode:
prompts:
  file:
  ids: []
seeds: []
conditions:
  - name:
    dose:
    measured_D:
outputs:
  folder:
  manifest:
analysis:
  script:
  sha256:
  produces:
```

## Provenance

* Pre-registration:
* Measurement files:
* Scripts:
* Renders:
* Pitfalls that apply:
