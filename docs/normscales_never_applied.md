# 48 renders of the q/k/v/o atlas were made with an edit that never reached the model

**Date**: 2026-09-28 · **Found by**: verifying Antigravity's re-reading of
`benchmark_qkvo_atlas`, which correctly reported the `normscales` conditions at exactly zero
displacement and described them as "acting as an identity operation" · **No render.**

---

## 1. The observation, and why "identity operation" is not the end of it

In `data/retro_qkvo_atlas_cells.csv`, `normscales_all_pos` and `normscales_all_neg` return
**1.0000 on every measured quantity** — coherence, all five band energies, variance, chroma, hue —
and displacement exactly 0.00000, pooled over eight styles and three seeds.

A zero like that has two very different explanations, and the distinction decides whether 48
renders are a control or a hole:

* **a null by design** — the preset asks for nothing, and the condition is a sanity check;
* **an edit that did not arrive** — the preset asks for something and the tool did not apply it.

## 2. It is the second

**The preset is not empty.** `presets/Arthemy_QKVO_normscales_all_pos.json` carries
`stats.model_patched_layers = 56` and 56 entries of the form

```
blocks.0.prenorm.scale  = 0.1
blocks.0.postnorm.scale = 0.1
...
```

For comparison, `Arthemy_QKVO_wo_b6_neg.json` carries four entries
(`blocks.24..27.attn.wo.weight = -0.1`) and moves the image plainly.

**The workflow is identical in structure.** Both renders load their preset through the same node,
`ArthemyKrea2PresetLoader`, at `strength_model = 1.0`, after the same `ArthemyKrea2ResetPatcher`.
Nothing distinguishes them but the file name.

**And the output is the baseline, exactly.** Comparing pixel content rather than file bytes — the
PNGs differ only because each embeds its own workflow, which names its own preset:

> **18 of 18 `normscales` renders checked have pixel content identical to their baseline, maximum
> absolute difference 0.** The control, `wo_b6_neg`, differs as it should.

A weight change of 0.1 on 56 layers that produces a bit-identical image is not a weak effect. It is
no effect: **the patch never reached the weights.**

## 3. The likely mechanism, stated as likely

`Arthemy_Krea2_Tuner.py` knows these keys — line 312 maps `NORMS_block_scales` to
`("prenorm.scale", "postnorm.scale")`. But its channel-scale adapter contains an explicit guard:

```python
if weight.ndim < 2 or weight.shape[axis] != self.scales.numel():
    ...
    logger.warning(f"[Arthemy Channel Scale] '{key}' has {tuple(weight.shape)} but the "
                   f"channel vector is {self.scales.numel()} long on axis {axis}; "
                   "this patch was skipped.")
    return weight
```

**Norm scales are 1-D tensors**, so `weight.ndim < 2` is true for every one of them, and the patch
is skipped — with a warning that goes to a log nobody was reading at render time.

This is stated as the likely mechanism and not as proven: confirming it means running the tuner and
watching that logger, or diffing the patched weights, and neither was done here. What *is* proven is
§2 — the edit did not reach the image.

## 4. What it costs

* **48 renders** of `benchmark_qkvo_atlas` (2 conditions × 8 styles × 3 seeds) are duplicates of
  baselines that already exist in `benchmark_atlas_phase1`.
* **Any statement in this project that norm scales do little or nothing is unsupported.** It is not
  a finding about the model; it is a finding about the tool. Nothing has been found that makes such
  a statement yet — this document exists so that none is made later.
* The q/k/v/o atlas's other conditions are unaffected: they patch `attn.w*.weight`, which is 2-D,
  and they move the image.
* **A "no effect" result from this tuner is not evidence of no effect until the patch is shown to
  have been applied.** The tuner writes a warning when it skips; nothing in this project's render
  pipeline captures it.

## 5. What to do

1. **Capture the tuner's warnings at render time.** The one line that would have caught this in
   April is already written and already emitted; it goes nowhere. Any bench script that drives the
   tuner should record its logger output beside the renders.
2. **Verify a preset moved the image before analysing it.** The check is one hash of the decoded
   pixels against the baseline, it costs nothing, and it belongs in the provenance step next to the
   metadata check that already exists (`verify_leaf_and_blk16_provenance.py`).
3. If norm scales are still a question worth asking, they need a patch path that handles 1-D
   tensors — which is a change to the tuner, not to a bench.

Drafted defect **86**: *a tool that skips a patch it cannot apply, warns into a log nobody reads,
and returns a perfectly clean null.* Register §E.

**Credit where it is due:** Antigravity's re-reading surfaced the zero and put it in its table
rather than smoothing it away. The gap was only in stopping at "identity operation" — which is what
the number looks like, and not what it is.
