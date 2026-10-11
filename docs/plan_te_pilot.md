# C64 — text-encoder pilot: plan

2026-10-11. Written before any render. Exploratory calibration, asked for by Alessandro: one picture, one seed,
every layer of the text encoder split into attention and MLP, to see what breaks what and at which dose, using
the sub-block structure of the Arthemy Krea2 Tuner (`ArthemyKrea2CLIPTuner`, granular).

## What the text encoder is here (read from the code before planning)

* Krea-2 encodes the prompt with **Qwen3-VL-4B** (36 language layers, hidden 2560, attention with q/k norm,
  GQA 32/8) and conditions on a **stack of 12 hidden states**, `hidden_states[2, 5, 8, ..., 35]`
  (`comfy/text_encoders/krea2.py`), after the final norm. In comfy's loop the tap k is the **input** of layer k,
  so layers 0-34 feed at least one tap and **layer 35 is never read**. Layer L reaches every tap above it: layer 0
  reaches all twelve, layer 34 only the last.
* The 12 states are fused **inside the DiT** by `txtfusion` (two layer-wise blocks, two refiner blocks, a
  12-to-1 projector) and `txtmlp` — the six text slots (28-33) of the Model Tuner vector. They are DiT
  weights, not encoder weights; swept here too because they are the gate between the two.
* The visual tower (Qwen3-VL's `visual.*`) is not used for a text-only prompt.

## Design

* Prompt and seed: the green-haired elf brawler (`P1_elfbrawler`), seed 1618033 — the C60 baseline, known by eye.
* **Main:** language layers 0-34 × {attention: q, k, v, o_proj; MLP: gate, up, down_proj} × doses −1.0, −0.35,
  −0.1, +0.1, +0.35, +1.0 (Real Value, ×(1+d); −1.0 zeroes the half: a knockout) = 420 renders.
* **Text adapter (DiT side):** the six slots × the same six doses = 36.
* **Controls first (7):** the baseline re-rendered must equal the C60 file; layer 35 doubled; a visual block
  doubled; layer 2 MLP doubled; q and k alone doubled at layers 5, 17 and 29.
* 463 renders, about 4 h 30 min. Plan `data/te_pilot_plan.csv`, code `experiments/te_pilot.py`.

## Gates (the run stops if they fail)

* The baseline reproduces to the pixel.
* Layer 2 MLP doubled changes the image (otherwise the CLIP patch is not reaching the encoder).

## Expected, written before (descriptive, no thresholds)

* **E1 (structure):** layer 35 doubled and the visual block doubled give images identical to the pixel to the
  baseline. If either changes the image, the reading of the tap above is wrong.
* **E2 (QK-norm):** q and k alone doubled leave the image (almost) unchanged — the per-head RMS norm on q and k
  removes a uniform scale. The same prediction was made for the DiT and never tested.
* **E3:** the earlier the layer, the larger the change, because it reaches more taps.
* **E4 (the contrast with the DiT):** text-encoder edits change *what* is drawn — subject, attributes, prompt
  adherence — rather than adding surface noise, which in the DiT came from the late blocks. If the text encoder
  produces grain or blotches, this is wrong.

## What it is for

Calibration: a dose per layer and half that changes the picture without breaking it, and a map of which layers
change what, to choose the units and doses of a proper atlas (more prompts and seeds, blind eye pass). Nothing
here is a claim.

## Eye pass (added 2026-10-11, before the page is built and before any label)

Designed with Alessandro, who expects the text encoder to change content and style more than the DiT does.
Every render except the repro check is shown once beside the baseline (left, fixed), in shuffled order (rng
64) behind an anonymous id, with 20 unannounced repeats; the condition is hidden. Per render:

* **24 traits read off the prompt** — character (9), clothes (6), pose and framing (4), scene (2), style (3) —
  each starting at *present*, to be set to **absent / present / amplified** against the baseline;
* two shortcuts: *identical to the original*, and *turned into text / lettering* (sets every trait absent);
* **gauntlet arm against the original**: same arm / the other arm / ambiguous, halfway (added 2026-10-11,
  still before the page and any label). The prompt does not say which arm wears the gauntlet, so the arm is a
  binary choice the text leaves open. Alessandro saw renders where the hands cross with the gauntlet between
  them. The question is whether such hybrids sit where the arm flips along the dose or layer axis (a
  symmetry-breaking reading, cf. Raya & Ambrogioni 2023; Sclocchi, Favero, Wyart 2024) or appear scattered,
  which would point to ordinary limb errors instead. Default *same arm*; left empty for *turned into text*;
* **overall style**: unchanged / changed, with a free field for how;
* **surface against the original**: cleaner / as the original / worse slight / medium / strong (the
  relative scale Alessandro adopted in C63, fixed here in advance);
* a free field.

The key `data/te_pilot_eye_key.csv` is committed when the page is built, before any label. What will be read
from it is descriptive: which layers and halves remove, amplify or keep each trait, at which dose; where the
"text" outcome starts and stops; where the gauntlet changes arm and whether ambiguous poses border those
flips; whether surface damage appears at all (E4); and self-agreement on the repeats.
Code: `experiments/te_pilot.py --page`.
