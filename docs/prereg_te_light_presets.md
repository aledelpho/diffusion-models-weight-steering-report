# Pre-registration C109 — light text-encoder presets: four layers at about ±0.30 instead of one layer doubled

Written 2026-10-22 by Claude, **before any C109 encode or render.** Proposed by Alessandro after C107–C108: "anziché
raddoppiare un layer, potremmo provare a modificare quattro layer con modifiche nel range di ±0.300x per vedere se
spostare di poco più layer possa conservare una maggiore coerenza"; he asked for a deep version with 12 presets.
Renders authorised by him the same day.

## 1. Why

Single-layer text-encoder edits leave a recognisable signature (C104, C106) and a family resemblance across subjects
(C105: content score within a domain 0.38, across 0.50 for E14/E26), but where they send the style depends on the whole
description (C107, C108). On the image model, small doses spread over many blocks gave presets that held across a
family of prompts (pages 23, 28). Question: at the **same picture change**, does a light preset spread over four layers
carry a more coherent change across subjects than one layer pushed hard?

## 2. Design

* **Presets (12),** drawn with `random.Random(10909)` (`data/te_light_presets_presets.csv`, committed now): four distinct
  MLP layers each, sign random, nominal dose ±0.30 per layer; P01–P06 from the middle layers 7–24, P07–P12 from 1–34.
* **Strength x** multiplies the four doses (x = 1 is the nominal ±0.30). **Calibration as C105**, per subject × preset:
  target DINOv2 distance 0.25 (window 0.20–0.32, accepted 0.15–0.40), median over the calibration seeds 1618033,
  2718281; ladder x = 0.5, 1, 2, 3.3 (x ≤ 3.3 keeps every dose above −1), then up to two bisection rounds.
* **Subjects (8), test seeds (2), gates:** as C105 (four Western-comic portraits, rally, still life, lotus canoe, leaf;
  2645751, 3316624; six plain renders pixel-identical to the existing ones).
* **Script:** `experiments/te_light_presets.py`, C105's code with the perturbations replaced; calibration up to about
  1,000 renders, test up to 208.
* **Comparison:** C105's single-layer edits E14 and E26, same subjects, seeds and target, re-shown in the same blind pass.

## 3. Blind labels (Alessandro), page written after the renders, before any label

C105's units and questions, unchanged: four subjects as plain → changed, "content of the same kind?" and "style of the
same kind?", answers *stesso* / *qualcosa di simile* / *in modi diversi* / *non si vede* (scores 1 / 0.5 / 0; *non si
vede* excluded). Per preset × test seed: WC, WO, X1, X2. Also E14 and E26 from C105 (16 units), 12 controls N (each
subject with a different preset), 8 repeats; order random, conditions hidden.

## 4. Rules (fixed now), content primary

0. Null: control N content score ≤ 0.20, otherwise the pass is not valid.
1. **Light presets carry more coherently:** content score of all preset units minus that of the E14/E26 units of the
   same pass **≥ 0.20** → *spread light presets are more coherent across subjects*; ≤ −0.20 → *less coherent*; otherwise
   *no difference*.
2. **Across domains:** mixed units (X1, X2) of the presets minus the null **≥ 0.30** → *the preset transfers across
   domains* (C105's rule).
3. **Reported:** middle (P01–P06) against full range (P07–P12); per preset scores; style the same way; reached pairs and
   the median strength x (does the nominal ±0.30 already reach D 0.25?); test–retest.

## 5. Limits

Random presets, not chosen by eye; one observer who knows the hypothesis; two test seeds; the comparison edits come from
another render session (same pipeline, gated pixel-identical). A preset that reaches the target only at x ≈ 3 is not
"light" any more; rule 3 reports it.
