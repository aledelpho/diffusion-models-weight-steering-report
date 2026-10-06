# C55 — is the tuner clean when it is active? A patch that changes no weight

2026-10-06. Proposed; **no render runs until Alessandro authorises it.**

## The question (Alessandro)

Every claim so far rests on "the tuner adds nothing of its own at zero" (page 20). But at zero the
tuner adds no patch at all: the zero check proves the node is clean when it is *skipped*, not when it
is *active*. If activating a patch introduced something beyond the multiplication — a different code
path, a cast, rounding noise — part of what we attribute to the edits would come from the node.

## What the code says (read 2026-10-06)

* `Arthemy_Krea2_Tuner.py` (`tune_model`): only tensors whose multiplier differs from 1.0 receive a
  patch; every other tensor is left out of the patch list.
* A patch is `add_patches({key: (dummy,)}, strength_patch=0.0, strength_model=1+d)`. In
  `comfy/lora.py` `calculate_weight` this is `weight *= strength_model` in float32; the dummy diff is
  skipped because its strength is 0.0 (`if strength != 0.0`).
* `comfy/model_patcher.py` `patch_weight_to_device` then casts back with
  `comfy.float.stochastic_rounding`, which for bfloat16 is a plain `.to(bfloat16)`: deterministic
  round-to-nearest. Stochastic rounding exists only for float8, not used here.
* So an active patch should be exactly `bf16(W × (1+d))`, on the patched tensors only.
* Measured on `krea2_turbo_bf16.safetensors`, the 8 matrices of block 27 (bf16): multiplying by
  1.0001 changes **0.00%** of the weights after rounding (the change is below half a bf16 step);
  by 1.002, 2.9%; by 1.004 and above, 100% (every weight moves by about one step). The 4 norm scales
  and `mod.lin` of the block are float32 and change by any d.

## Renders (4, archer `P3_archerforest`, seed 3141592, C47 settings)

| id | tuner input | what changes in the weights | prediction if the node is clean |
|---|---|---|---|
| N1 | `granular_json`: the 8 bf16 matrices of block 27 at 0.0001, Real Value | nothing: every weight rounds back to itself | **pixel-identical to the baseline** |
| N2 | vector: block 27 at +0.0001 | the float32 scales of block 27 by 1e-4, nothing else | close to the baseline; anything is possible on this unstable seed |
| N3 | vector: block 27 at +0.004 | every weight of block 27 moves by ~one bf16 step | the smallest real change of the matrices |
| N4 | vector: block 27 at −0.004 | same, other sign | |

**Decisive rule (N1 only):** pixel-identical to the baseline → the active node adds nothing beyond
the multiplication. Any pixel different → the node, or the patch path of ComfyUI, adds something of
its own; every result that rests on small doses is then suspect until explained.
N2–N4 are descriptive: how small a real change is enough to move this unstable seed (does the hood
complete at one bf16 step?). They are labelled by eye, blind, with the C54 labels.
