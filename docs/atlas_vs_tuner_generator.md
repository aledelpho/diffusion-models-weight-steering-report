# The atlas presets were not made by the tuner, and two components are inert

- **Written:** 2026-09-26, from the tuner source now readable at
  `custom_nodes/Arthemy_Krea2_Tuner/` and the checkpoint inventory in
  `docs/model_structures/krea2_turbo_bf16_details.json`.
- **Bears on:** `docs/prereg_perturbation_atlas.md`, `docs/prereg_style_capacity.md` and its
  amendment 02, and on how any capacity result may be worded.

---

## 1. The answer to the question that prompted this

**No.** The 26 atlas presets were not produced through the Chaos Block Surgeon node. They were
written by script, as flat per-tensor multiplier tables, and renormalised to the anchor
D = 273.02631162314486. The preset files say so themselves: `chaos_recipes_count: 0`,
`rotation_recipes_count: 0`. No recipe of any kind is in them.

## 2. What the tool's own generator actually offers

`ArthemyKrea2ModelChaosBlockSurgeonTuner` takes:

- `target_block` from `MODEL_TARGET_MAP` — **five-block groups** (`Block_1 (All 0-4)`,
  `Block_2 (All 5-9)`, `Block_3 (All 10-14)`, …) **and every single block individually**
  (`↳ Block_1A (0)` … ), plus `All Blocks (0-27)`;
- `tune_mode` — `Block-Level` or `Element-Level (Sub-atomic)`;
- `seed`;
- `chaos_strength`, a float from −99 to +99;
- one `<component>_chance` probability per component group, ten of them for the model.

## 3. Where that differs from the atlas, item by item

| | Chaos node (the product) | atlas presets (this experiment) |
|---|---|---|
| bands | 5-block groups **and single blocks** | 7-block quarters only |
| components | selected by **probability** per group | fixed, every tensor of the type |
| control variable | `chaos_strength`, a **magnitude** | **matched displacement** D, identical for all |
| granularity | block-level or element-level | block-level only |
| sign | `chaos_strength` may be negative | random per-tensor signs, no signed arms |

**This is not a detail.** The atlas measures *norm-matched arbitrary localised perturbations*.
That is the correct object for the causal question the project asked — is it the structure or the
magnitude — because matching D is what removes the magnitude confound. It is **not** the object a
user of the tool produces. A user picks a band, a strength and a seed, and gets whatever
displacement that happens to be.

So every capacity, identity and transfer number measured on the atlas describes a mathematical
idealisation of the tuner, not the tuner. None of them may be worded as a statement about what the
product does until a corpus generated **through the node** exists.

## 4. The dead arm, explained by the tuner's own source

`data/prereg_style_capacity_amendment_02` recorded that `modulation_norm`, both draws, renders
**bit-identical to the baseline** on all eight prompts. The tuner source contains this comment,
inside `MODEL_SURGEON_MAP`, where a widget used to be:

> `"MOD_lin_time"` used to sit here, mapped to `"mod.lin"`. […] The widget matched nothing and
> **every sweep over it produced images byte-identical to the baseline**. Removed rather than
> re-pointed: a tensor with no block index has no place in a SUB-BLOCK node.

So 28 of `modulation_norm`'s 84 tensors were **already known to be inert**, and the corresponding
control was removed from the node for exactly the symptom the atlas reproduced. The atlas
rediscovered it from pixels, independently, six months of commits later.

Two things follow, and the second is worse.

**(a) The comment's factual claim is wrong, and so is its diagnosis.** It says Krea-2 has no
`mod.lin` tensor and that "the widget matched nothing".
`docs/model_structures/krea2_turbo_bf16_details.json` lists `blocks.0.mod.lin` …
`blocks.27.mod.lin` as real keys, alongside `blocks.N.prenorm.scale` and
`blocks.N.postnorm.scale`. And the Preset Loader, run on 2026-09-26, reports:

> `Loaded Preset 'Arthemy_Atlas_modulation_norm_draw1' | Model: 84 scalar layers, 0 granular
> layers (x1.00) | CLIP: 0 scalar layers (x1.00)`

**84 of 84 matched.** Nothing was unmatched, nothing was skipped. The widget did not "match
nothing"; it matched everything and changed no pixel. The removal was done for the right symptom
with the wrong explanation, and that comment should not be trusted as a statement about the
checkpoint.

**(b) The scare about the displacement accounting is dead, and this is the important part.**
If the keys had failed to resolve, every preset in this project touching a `.scale` tensor would
have carried less displacement than its calibration claims — including the four `*_attn` regions,
where 14 of 49 tensors are `qknorm` scales. They resolve. **The Frobenius matching of the whole
project stands.** No published displacement is affected.

**(c) What is left is a statement about the model, not about the tool.** Eighty-four parameters —
`mod.lin`, `prenorm.scale`, `postnorm.scale`, across all 28 blocks — were rescaled by a
multiplier of `model_alpha = 0.9365`, at the same Frobenius displacement as every other atlas
condition, and the render is **byte-identical** to the baseline on all eight prompts. Not small:
zero.

Two mechanisms remain, and they are distinguishable by one more node execution:

1. **The forward pass does not read them.** Many DiT implementations use a non-affine norm and take
   the whole scale from the modulation path, which would leave `prenorm.scale` in the checkpoint as
   an unused parameter. Under this branch the 84 weights really move and the model ignores them.
2. **ComfyUI never materialises the patch for a parameter not named `.weight`.** The patch is
   registered by `add_patches` — hence the count of 84 — but `calculate_weight` is only ever
   applied to the tensors the patcher walks, and a `.scale` parameter may never be walked.

**The check:** bake the patched model with the tuner's own Saver, which "materializes every patched
weight" and reports `n_patched`, then compare the baked `blocks.0.prenorm.scale` against the
original checkpoint. **Different → branch 1**, the weights moved and the architecture is insensitive
to them, and that belongs in the sensitivity map as a genuine finding: *these 84 parameters are
inert to rescaling, which makes them the safest thing in the model to touch and the most useless.*
**Identical → branch 2**, and it is a ComfyUI-level limitation on which parameters a scalar patch
can reach, which the tuner should detect and refuse rather than report as 84 patched layers.

**Either way `NORMS_block_scales` is still exposed in the node's UI and does nothing.** That part
does not depend on the mechanism.

## 5. What the next atlas should be

Generated **through the node**, sweeping `target_block` × sign of `chaos_strength` × seed × a
declared `_chance` profile, with the resulting displacement **measured per preset and recorded**
rather than imposed. The magnitude confound then moves from the design to the analysis, where a
regression can remove it — and in exchange the corpus becomes a statement about the tool a user
actually holds.

It also answers, for free, the two questions the current atlas cannot: the node has **single-block
targets**, so per-block resolution is available; and `chaos_strength` takes a sign, so band × sign
is expressible in the UI.
