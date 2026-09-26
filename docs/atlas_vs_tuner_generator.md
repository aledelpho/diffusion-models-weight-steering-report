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

**(a) The comment's factual claim is contradicted by the checkpoint.** It says Krea-2 has no
`mod.lin` tensor. `docs/model_structures/krea2_turbo_bf16_details.json` lists
`blocks.0.mod.lin` … `blocks.27.mod.lin` as real keys, alongside `blocks.N.prenorm.scale` and
`blocks.N.postnorm.scale`. Whatever makes them inert, it is not their absence from the file. The
loader resolves keys by exact match and these match; `is_bookkeeping_sd_key` tests for `_scale`,
not `.scale`, so it does not catch them either. **The mechanism is still unexplained from the
source.**

**(b) `NORMS_block_scales` is still in the map and still in the UI.** It points at
`("prenorm.scale", "postnorm.scale")` — the other 56 tensors of `modulation_norm`. If the whole
region is inert, those 56 are inert too, and the node still offers a user a control that does
nothing. That is a live defect in the product, not an artefact of this experiment.

**The decisive check is one node execution**, and the node already prints the number: load
`presets/Arthemy_Atlas_modulation_norm_draw1.json` in the Preset Loader and read the info line.
The loader counts `n_model_matched` against `n_model_unmatched` and reports both. If matched is 84
the tensors are moved and the forward pass ignores them; if it is 0, or 28, the apply path is
dropping them and the displacement of **every preset in this project that touches a `.scale`
tensor is lower than its calibration says** — including the four `*_attn` regions, where 14 of 49
tensors are `qknorm` scales.

## 5. What the next atlas should be

Generated **through the node**, sweeping `target_block` × sign of `chaos_strength` × seed × a
declared `_chance` profile, with the resulting displacement **measured per preset and recorded**
rather than imposed. The magnitude confound then moves from the design to the analysis, where a
regression can remove it — and in exchange the corpus becomes a statement about the tool a user
actually holds.

It also answers, for free, the two questions the current atlas cannot: the node has **single-block
targets**, so per-block resolution is available; and `chaos_strength` takes a sign, so band × sign
is expressible in the UI.
