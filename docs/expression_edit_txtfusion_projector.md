# The "expression" edit — what `txtfusion.projector.weight` {8: -0.6, 9: -0.9} does, read from code and weights

2026-10-05. Alessandro uses this single granular entry in many of his presets to restore facial
expressions, which in his reading were dulled by Krea-2's safety training. Recorded here before any
test of it. Nothing below is a measurement of its effect on images.

## What the tensor is

`comfy/ldm/krea2/model.py`, `TextFusionTransformer`: the text conditioning is a stack of **12 hidden
states of Qwen3-VL-4B**, taps `[2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]`
(`comfy/text_encoders/krea2.py`, `KREA2_TAP_LAYERS`). Each tap goes through two shared fusion blocks;
then `self.projector = Linear(12, 1, bias=False)` collapses the 12 taps into one sequence with a
**plain weighted sum — no softmax** — before the refiner blocks and the DiT. The projector is the
whole tensor: 12 numbers, F32.

Index 8 is Qwen layer **26**; index 9 is Qwen layer **29** (of 36).

## What the edit does to it

The tuner's `build_granular_patch` turns a dict of digit keys into a **sparse additive diff**
(`flat_diff[idx] = value`, then added through ComfyUI's `diff` patch). It does **not** replace the
value. Read from `krea2_turbo_bf16.safetensors`:

| tap | Qwen layer | original | after the edit |
|---|---|---|---|
| 8 | 26 | **−0.512** | −1.112 |
| 9 | 29 | **−0.891** | −1.791 |

All 12 original weights: −0.054, −0.161, 0.371, 0.504, 0.707, 0.395, 0.398, −1.438, −0.512, −0.891,
−0.609, 0.113. The model already **subtracts** layers 23–32 (taps 7–10); the edit roughly **doubles
the subtraction of layers 26 and 29**.

## What follows, and what does not

- This is a **text-conditioning** edit, outside the 28 DiT blocks studied in the results notebook. The
  `F_proj` family (this tensor scaled as a whole) was found live in C35: +1.000 moved pixels by 32/255.
- "Censorship lives in layers 26–29 of the text encoder" is **not** shown by any of this. What is shown
  is narrower: the edit changes how two late language-model layers are mixed into the conditioning.
  The safety-training explanation is Alessandro's hypothesis.
- The entry is additive. If it was meant to *replace* the weights with −0.6 and −0.9, the actual edit
  is much larger than intended (−1.11 and −1.79 instead of −0.6 and −0.9); the look calibrated by eye
  is the additive one.

## Test to register before any render (not yet written)

Expression-bearing portraits (the C52 prompts with an explicit expression, plus foils), four
conditions — base, base + this edit, the C52 preset, preset + this edit — a blind forced choice
"which shows the described emotion more?", identity sheets that include different characters, and
blk08 + alone as the competing explanation for the C52 preset's flattened expressions.
