# Authoring contract for this notebook

This file is the specification that every page under `notebook/` follows. It is written to be
read by a person adding an experiment, and by an assistant asked to add one on their behalf.
Read it before creating or editing any page.

`experiments/validate_notebook.py` enforces most of what follows. If a rule here is not yet checked
by that script, it says so. **A rule that is not enforced is a rule that will be broken**, so
prefer adding a check over adding a paragraph.

---

## 1. Language

**The notebook is written in English.** Every page, every heading, every caption, every alt
text, every column name in a published table, and every value of `status` and `statement` in
the front matter.

The reason is not style. This notebook is read by people who do not share a first language
with its author, and increasingly by language models asked to check, summarise or extend it.
Both audiences are served by one language, used consistently.

Script comments may remain in Italian where they were written that way — that is the historical
record and rewriting it would misrepresent it. Nothing a reader of the notebook sees is in
Italian. The validator flags common Italian function words found in `notebook/*.md`.

---

## 2. Page anatomy

Every page has the same five sections, in this order. A reader who has read one page knows
where to look in every other.

```markdown
---
<front matter — see §3>
---

# A title in plain words, not a number

> **Holds** · 168 renders · 28 blocks · pre-registered 2026-09-20
> [← all experiments](../README.md#what-holds-and-what-does-not)

## In two minutes

What I wanted to know, what I did, what came out. Plain language, figures, no mathematics.
A curious reader stops here and has understood the finding. This section is not a summary
written afterwards — it is the reason the rest of the page exists, so write it first.

## The verdict

Three to six lines. This is literally the row that appears in the README table, expanded.

## Why I might be wrong

The reservations, **before** the data.

## The data

### How it was measured
### The numbers
### The controls

### Reproducing this
<the reproducibility block — see §5>

## Provenance

Pre-registration · measurement files · scripts · renders · the pitfalls that apply.
```

### Why "Why I might be wrong" comes before the data

Because this notebook already does it — the rotation pilot documented its own methodological
trap before reporting its result — and that is the habit worth making structural. In a fixed
position it stops being an occasional virtue. A reader learns that the section is always
there, and that when it is short, it is short because there was nothing more to say.

---

## 3. Front matter

Required on every page. The README table is **generated** from these blocks, never written by
hand: a hand-kept table that disagrees with its own item list is pitfall 25, and this project
has already paid for that once.

```yaml
---
id: 05-knob-or-cost              # must equal the filename without .md
title: What an edit steers, and what it costs
status: holds                    # holds | ambiguous | overturned | open
stage: confirmatory              # exploratory | confirmatory | verification
date: 2026-09-20
preregistration: docs/prereg_punto7_simmetria_segno.md   # or: null
supersedes: []                   # page ids this page replaces
pitfalls: [2, 43, 57, 60, 61]    # entries in docs/errors_log.md that apply here

corpus:
  renders: 168
  prompts: 2
  seeds: [42, 777, 1337]
  blocks: 28

claims:
  - id: cost-grows-with-depth
    status: holds
    statement: >
      Pushing any block costs fine texture in either direction, and the cost grows
      closer to the output.
    evidence: "Pre-registered. 23 of 28 blocks, r = -0.659, 11-14σ."
    anchor: "#the-common-mode-is-friction-not-a-knob"
---
```

### The four states

| state | meaning |
|---|---|
| **holds** | Survived a threshold fixed before the data existed, or replicates across independent corpora |
| **ambiguous** | Tested, and the answer is neither yes nor no. Written as ambiguous, never rounded |
| **overturned** | Tested and not supported — or supported once and withdrawn. **Typeset exactly like `holds`** |
| **open** | Not yet tested. A question, not a result |

`overturned` carries the same visual weight as `holds` on the index page. That is deliberate
and is not negotiable in the template: a notebook that displays its negative results smaller
than its positive ones is selecting, whatever its text says.

### Rules the validator enforces

- `id` equals the filename.
- Every `claims[].anchor` resolves to a real heading on that page.
- Every claim has a non-empty `statement` and `evidence`.
- A page with `status: holds` and `stage: exploratory` fails: an exploratory result cannot
  hold. Use `open` or `ambiguous`.
- A page with `preregistration: null` and `stage: confirmatory` fails.

### The three stages

**exploratory** — looking, with no threshold fixed in advance. Cannot hold.
**confirmatory** — a hypothesis tested against a criterion frozen before the data. Needs a
pre-registration.
**verification** — an integrity check: does the instrument do what it claims. The criterion is
fixed before the value and the outcome is pass or fail, but it is not a hypothesis about the
model, so it needs no pre-registration and it can hold. `00-the-bench.md` is the case this
stage was added for; the schema had no room for it until that page was written.

---

## 4. Figures

### 4.1 Two kinds, and they never look alike

**Evidence figures** — renders, difference maps, charts. Generated by a script that reads a
measurement file. They carry condition, prompt, seed, *n* and the source file.

**Explanatory figures** — schemas: how an edit is built, where the 28 blocks sit, what the
S/A decomposition is. Drawn by hand as SVG. **They never carry a measured number** and they
are visually marked as schemas, so no reader mistakes an explanation for a result.

> One line, and it is the whole rule: **a figure carries numbers only if a script read them
> from a file. Otherwise it carries none.**

### 4.2 Every figure is registered

No figure is referenced from a page unless it has an entry in `experiments/figures.yaml`:

```yaml
- id: F05.3
  page: 05-knob-or-cost
  kind: paired_bars              # scatter|strip|toggle|contact_sheet|ramp|diffmap|paired_bars|schema
  builder: rectification_bars    # a function in experiments/notebook_figures.py
  source: data/punto7_amplitudes.csv    # null only for kind: schema
  caption_from: source           # source | static (static allowed only for schema)
  crop: whole                    # whole | locator:<name>
  alt: >
    Paired bars of per-block amplitude at +0.200 against -0.200. Block 26 moves 9.1 times
    further in the positive direction than in the negative.
```

### 4.3 Crops — the rule that Antigravity's figures broke

A caption typed by hand next to a crop chosen by hand can assert something the data denies,
and nothing catches it. That is pitfall 40, and it has already happened here: five crop
rectangles out of twenty did not contain the headlights they were captioned as showing.

Therefore:

1. **The default is the whole frame.** A crop must be justified, not assumed.
2. **A crop is never a literal rectangle in a figure script.** It is a *locator*: a named
   function that takes the image **and its row in the measurement file** and returns a box.
   Hard-coded pixel rectangles fail validation.
3. **A locator is evaluated per (prompt, condition, seed)** — never once per prompt. Different
   seeds put the content in different places; that is the whole reason this rule exists. If you
   are showing the headlights of a car, the box must be found in *that* render, not in a
   sibling.
4. **A locator is qualified before it is used.** Run it across the corpus, check a sample
   against the declared criterion, and publish the hit rate next to the figure. Below the
   declared threshold, fall back to the whole frame and say so.
5. **If no locator exists for the thing being discussed, show the whole frame.** A crop you
   cannot verify is a claim you cannot support.

### 4.3b The control panel of a toggle — corrected after building one

An alternation makes any difference vivid, so every toggle carries a control panel. The first
version of this rule said the control was *two baselines at different seeds*. That was wrong,
in exactly the way pitfall 55 describes: at a fixed seed, a change of seed is not noise, it is
a maximal perturbation. Measured on the first toggle built, the different-seed control panel
moved by **29.8 of 255 — more than block 0 (22.9)** and as much as block 27 (31.7). It did not
calibrate anything; it swamped the thing it was supposed to calibrate.

**The control is the same baseline twice.** It is bit-identical, so that panel does not move at
all, and every flicker in the others is the edit. `notebook_figures.py` enforces this: a control
whose two frames differ by a single pixel is refused.

A different seed is still worth quoting — as a *ceiling*, in the caption, never as the floor.

A crop is itself an assertion — that the thing worth looking at is inside the box. It is
checked like any other assertion.

### 4.4 Theme

Every generated figure renders on the dark surface `#1a1a19`, using the palette in
`experiments/notebook_charts.py`. The three categorical slots (`#3987e5`, `#d95926`, `#199e70`) are
validated for colour-vision deficiency against that surface; do not substitute values without
re-running the validator.

The validator samples the border pixels of every generated figure and **fails on a light
background**. Several existing figures were produced in a light theme and must be regenerated
rather than recoloured.

Further:

- Depth (block index) is **ordered**, so it is encoded with a sequential ramp — one hue, light
  to dark — never with categorical colours. Categorical hues encode identity, not rank.
- Labels wear text colours, never the series colour.
- Direct labels are selective: the outliers, not every point.
- 2 px of surface between adjacent panels; never a shared border.
- A provenance strip under every evidence figure: `prompt · condition · seed · n · source file`.

### 4.5 Alt text

Required on every figure, and written as **the claim the figure makes**, not as a description
of its appearance. "Paired bars of amplitude by block" is a description. "Block 26 moves 9.1
times further in the positive direction than in the negative" is the claim.

This serves screen readers, it serves a model reading the page, and it serves the author: a
figure whose alt text cannot be written does not have a job.

### 4.6 Cadence

One figure every two to four paragraphs. The validator reports any run of more than four
consecutive paragraphs without one. It reports rather than fails — cadence is a target, not a
law — but a page that trips it repeatedly is a page that has drifted back into being a wall of
text.

---

## 5. Reproducibility block

Required in `## The data`. The test it has to pass: **could a stranger with the checkpoint
recreate these renders without asking a question?**

````markdown
### Reproducing this

```yaml
model:
  checkpoint: krea2_turbo_fp8_scaled.safetensors
  sha256: <hash>
sampling:
  sampler: euler_ancestral
  steps: 9
  cfg: 1.0
  scheduler: simple
  resolution: 1280x1024
  vae: <name>
tuner:
  node: ArthemyKrea2ModelTuner
  version: <commit>
  mode: granular_json
prompts:
  file: data/prompts.json
  ids: [P01, P02]
seeds: [42, 777, 1337]
conditions:
  - name: blk00pos
    dose: +0.200
    measured_D: 0.045745      # measured, never nominal — pitfall 13
outputs:
  folder: benchmark_profondita/renders
  manifest: data/punto7_manifest.csv
analysis:
  script: experiments/verifica_punto7.py
  sha256: <hash>
  produces: data/punto7_swing_common_mode.csv
```
````

**Do not type this block from memory — read it out of the renders.** Every PNG carries the
graph that made it in a text chunk, so `experiments/extract_repro.py` can print this block for
any bench. The first draft of the two pages here was typed from memory and got the checkpoint
name, the tuner mode and the resolution all wrong, in the one block whose entire purpose is to
be right.

Two of these fields exist because of specific past failures. `measured_D` is measured and not
nominal, because a bisection once returned its best candidate instead of failing (pitfall 13).
`outputs.folder` is unique per experiment, because two runs once shared an output root and the
harvester silently measured the wrong images (pitfall 30 — which has since recurred twice).

---

## 6. Adding a new experiment

The order matters. Steps 1 and 2 happen **before** the renders exist.

1. `cp notebook/_template.md notebook/NN-short-name.md` and fill the front matter. `status`
   starts as `open`.
2. If the experiment is confirmatory, write the pre-registration in `docs/` first and link it.
   Freeze the analysis script **by hash and by copy** — a hash alone was not enough once
   (pitfall 32).
3. Render. Write the manifest. Never into a folder another experiment uses.
4. Analyse. Persist every table to disk; nothing lives only in a terminal buffer.
5. Register the figures in `experiments/figures.yaml`, build them, look at them.
6. Write `## The data`, then `## Why I might be wrong`, then `## In two minutes` last — it is
   written last and read first.
7. Set `status`, fill `claims`, run `python experiments/validate_notebook.py`.
8. `python experiments/build_notebook.py` regenerates `index.html` and the README table.

**Before drawing any conclusion, analyse every arm already on disk.** An unused arm is not a
spare, it is an unexamined control (rule 15). This rule was written on the morning of
2026-09-20 and broken the same afternoon, on 361 renders across three prompts of which one
prompt had been looked at. The validator now compares the render count declared in
`corpus.renders` against the manifest and reports the gap.

---

## 7. Where things live

```
README.md                  entry point · generated claims table · how to reproduce
index.html                 GENERATED from notebook/*.md — never edited by hand
notebook/
  AUTHORING.md             this file
  _template.md             the skeleton
  00-the-bench.md          does the instrument lie? sentinels, dead arms, noise floor
  01-...                   one file per experiment
data/                      measurement files — the only source of any published number
docs/                      pre-registrations, verdicts, errors_log.md, asset_pipeline.md
experiments/
  notebook_charts.py       chart module (statistics)
  notebook_figures.py      figure module (renders)
  figures.yaml             the figure registry
  build_notebook.py        generator
  validate_notebook.py     the checks
assets/<page-id>/          figures for that page, WebP 480×600 q82
```

`index.html` is generated. Editing it by hand recreates the situation this structure exists to
end: two documents with the same content, different section numbers and a hand-maintained
correspondence between them.

---

## 8. What the validator checks today

This table is audited against the script, not written from memory. A contract that claims a
check it does not run is worse than one that admits the gap: the first version of this table
listed `corpus.renders` against the manifest as implemented, and it never was.

| | check | severity |
|---|---|---|
| ✓ | Front matter present, `id` matches filename, required keys present | error |
| ✓ | `status` is one of the four; `holds` + `exploratory` rejected; `confirmatory` without a pre-registration rejected | error |
| ✓ | Every claim has `statement`, `evidence`, `status`, and an `anchor` that resolves to a heading on that page | error |
| ✓ | No claim id is used twice, on one page or across pages | error |
| ✓ | The five sections present, in order | error |
| ✓ | Reproducibility block present, valid YAML, all required keys, `measured_D` on every condition | error |
| ✓ | Every figure referenced by a page is registered in `figures.yaml`, and registered *to that page* | error |
| ✓ | **The figure file actually exists on disk** | error |
| ✓ | **A link to a sibling page resolves to a page that exists** | error |
| ✓ | Every registered figure has `alt`, `source` (unless a schema), and `caption_from: source` (unless a schema) | error |
| ✓ | `crop` is `whole` or `locator:<name>` — pixel rectangles rejected | error |
| ✓ | A `toggle` declares a control | error |
| ✓ | Generated figure files have a dark background | error |
| ✓ | Italian function words in `notebook/*.md` | error |
| ✓ | Alt text present and not trivially short | error / warn |
| ✓ | `TODO` placeholders left in a reproducibility block | warn |
| ✓ | Figure cadence — more than four consecutive paragraphs without one | warn |
| ✓ | A registered figure that its page never references | warn |
| ✗ | `corpus.renders` against a manifest — **not implemented**: there is no per-page manifest file to count against. Until there is, that number is the one field on a page that nothing verifies |
| ✗ | Locator hit rates — needs the renders, so it runs on the machine that holds them |

And one check that lives outside the validator, in `experiments/extract_repro.py`: every render
in a bench must share one sampler configuration. A bench whose images were made at different
step counts is not a bench, and nothing else in the repository would notice.
