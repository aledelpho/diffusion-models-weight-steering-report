# Declaring the colour changes nothing measurable — both hypotheses fail

**Date**: 2026-09-27 · **Pre-registration**: [`prereg_declared_colour.md`](prereg_declared_colour.md),
commit `5aa4f52`, deposited before the statistic was computed. **No render, no new extraction** —
the matched corpus has existed since 2026-09-15.
**Data**: `data/style_features.csv`, `data/declared_colour_test.csv`.

---

## 1. Result

Six matched pairs: the same subject with a declared rim-light hue (A1) and without any colour
clause (A2). Displacement in units of each prompt's own baseline seed noise, five shared seeds, six
shared conditions. The **ratio** colour / texture is taken within the prompt, so global
perturbability cancels.

| pair | hue | text sim | colour z | texture z | **ratio** | colour z | texture z | **ratio** | |
|---|---|--:|--:|--:|--:|--:|--:|--:|---|
| | | | *declared* | | | *undeclared* | | | |
| G1 / S7_01 | teal | 0.94 | 0.955 | 1.251 | **0.763** | 1.893 | 1.951 | **0.970** | declared LESS |
| G2 / S7_02 | yellow | 0.94 | 1.634 | 1.937 | **0.844** | 1.071 | 2.199 | **0.487** | declared MORE |
| G3 / S7_03 | teal | 0.78 | 2.011 | 5.083 | **0.396** | 1.651 | 1.679 | **0.983** | declared LESS |
| G4 / S7_04 | chartreuse | 0.95 | 4.838 | 3.905 | **1.239** | 1.021 | 2.715 | **0.376** | declared MORE |
| G5 / S7_05 | blue | 0.45 | 1.638 | 2.026 | **0.809** | 1.710 | 6.316 | **0.271** | declared MORE |
| G6 / S7_06 | purple | 0.95 | 0.843 | 2.665 | **0.316** | 1.709 | 2.387 | **0.716** | declared LESS |

**3 of 6 each way.**

| test | result |
|---|--:|
| exact two-sided sign test, n = 6 | 3/6, **p = 1.000** (floor 0.031) |
| same, excluding pair 5 (text sim 0.45) | 2/5, **p = 1.000** |
| paired exact permutation on the ratio — *post-hoc, more powerful* | **p = 0.719** |
| `colour_z` alone, paired permutation | **p = 0.781** |

Per-pair differences: −0.207, +0.357, −0.588, +0.863, +0.538, −0.400. Mean **+0.094** against a
scatter of **±0.86** — the noise is nine times the effect.

> **Both pre-registered hypotheses fail. H-A (Alessandro: declared moves more) and H-C (ColorWave:
> declared moves less) are each unsupported. The analyst's deposited expectation was H-C and it is
> wrong too.**

## 2. The control passed, so this is a real null

`texture_z` was expected to show **no** difference between the arms — a colour clause is not about
texture, and if it moved, the design would be measuring something other than what it claims.

| | declared | undeclared | paired permutation |
|---|--:|--:|--:|
| `texture_z` | 2.811 | 2.874 | **p = 0.969** |

It did not move. The instrument is working and the null on colour is a null, not a broken
measurement. That is the difference between this result and a failed experiment.

## 3. What can and cannot be concluded

**Can**: adding an explicit colour declaration to the prompt does not detectably change how far a
weight edit moves the four colour descriptors, relative to how far it moves texture, on six matched
subjects in this style.

**Cannot**: that no such effect exists. With six pairs a sign test reaches its floor only on a 6/6
split, and the paired permutation could have seen a mean shift of about **0.44** in ratio units; the
observed shift is **0.094**. An effect present in four pairs of six, or smaller than about half the
ratio's own range, is invisible to this design. **This is a null with low power, and it is reported
as such.**

**And the ColorWave comparison is not a fair test of ColorWave.** That paper manipulates the prompt
and asks whether the *rendered colour* obeys it; here the prompt is fixed and the *weights* are
perturbed. The two studies share a noun and not an experiment. Its prediction was carried over
because it was the only competing direction available, and its failure here says nothing about the
paper.

## 4. Where this leaves the question

`colour_and_concept.md` §1 stands untouched and is still the strongest thing on this topic: the
colour response **transfers across subjects at chance** (0.514, p = 0.233) while texture transfers
at 0.778, p = 0.0097. Colour is bound to the content.

What this study adds is that **declaring the colour in the prompt is not the mechanism of that
binding** — or at least, not by an amount six matched pairs can see. If colour is pinned to the
concept, it is pinned whether or not the prompt names it, which is the more interesting version of
Alessandro's original intuition and not the one he predicted.

## 5. Limits

* Six pairs, one style (Western comics, extreme close-up, white background), one declared-colour
  form (a rim-light hue). A colour declaration attached to an **object** rather than to the
  **lighting** is a different manipulation and is not tested here.
* Pair 5 has prompt-text similarity 0.45; the primary and the sensitivity check agree, so it changes
  nothing, but the pair is weak.
* `G3` (declared, texture z = 5.08) and `S7_05` (undeclared, texture z = 6.32) are outliers that
  inflate and deflate their ratios respectively. With n = 6 there is no robust way to handle them
  and none was applied.
* Four colour descriptors. An effect invisible to them is invisible here.
