"""Arthemy MOSS Tuner - weight x (1+d) on MOSS-Image (MOSS1, diffusion-models-weight-steering-report).
Written 2026-10-25 by Claude from docs/moss_structure_reading.md. A separate node: the Krea-2 tuner is not touched.

Two nodes, both taking `granular_json`, a JSON object {key: d}; every matrix named is replaced by weight x (1 + d):

  ArthemyMossModelTuner  MODEL -> MODEL   keys of the DiT, e.g. "layers.20.proj.ffn_down.weight",
                                          "layers.20.proj.qkv.weight", "layers.20.proj.o.weight",
                                          "layers.20.proj.ffn_up_gate.weight" (fused gate and up)
  ArthemyMossCLIPTuner   CLIP  -> CLIP    keys of Qwen3.5-9B, e.g. "layers.6.mlp.down_proj.weight",
                                          "layers.7.self_attn.o_proj.weight", "layers.0.linear_attn.out_proj.weight"

The edit is an object patch on a clone (the loaded model is never modified). Version 2 (2026-10-25, after gate C
failed): ComfyUI loads MOSS with dynamic VRAM (ModelPatcherDynamic), which streams weights from its own storage and
ignores object patches; the tuners therefore always work on a NON-dynamic clone (clone(disable_dynamic=True)), even
with an empty JSON, so that "{}" checks that this route alone changes nothing (gate A). Version 3: the CLIP clone
encodes with the patcher's own model (CLIP.clone keeps the old cond_stage_model otherwise). A bf16 weight is replaced by
(weight in float32 x (1 + d)) cast back to its dtype. A W4A8 quantised weight (comfy_kitchen QuantizedTensor) keeps its
packed codes, codebook and group scales; only its per-output-channel scale `s_channel` is multiplied by (1 + d), which is
the same as scaling the dequantised weight (dequantisation is codes x s_rel x s_channel, no correction term in this
checkpoint). An empty JSON applies no edit but still takes the non-dynamic route.
"""
import dataclasses, json
import torch


def _parse(s):
    s = (s or "").strip()
    if not s:
        return {}
    d = json.loads(s)
    if not isinstance(d, dict):
        raise ValueError("granular_json must be a JSON object {key: d}")
    return {str(k): float(v) for k, v in d.items() if float(v) != 0.0}


def _resolve(module, key, anchors):
    """Full parameter name in `module` for a short key, by a unique suffix match after one of `anchors`."""
    names = [n for n, _ in module.named_parameters()]
    for a in anchors:
        hit = [n for n in names if n.endswith(a + key)]
        if len(hit) == 1:
            return hit[0]
        if len(hit) > 1:
            raise ValueError(f"key {key!r} is ambiguous: {hit[:4]}")
    raise ValueError(f"key {key!r} not found")


def _get(module, name):
    obj = module
    for part in name.split("."):
        obj = getattr(obj, part)
    return obj


def scaled_weight(w, d):
    """weight x (1 + d), keeping the storage format."""
    try:
        from comfy.quant_ops import QuantizedTensor
    except Exception:
        QuantizedTensor = ()
    data = w.data if isinstance(w, torch.nn.Parameter) else w
    if QuantizedTensor and isinstance(data, QuantizedTensor):
        p = data._params
        if getattr(p, "s_channel", None) is None:
            raise ValueError(f"quantised layout {data._layout_cls} has no s_channel: not supported")
        if getattr(p, "correction", None) is not None:
            raise ValueError("a correction term is present: scaling s_channel would not scale the weight")
        p2 = dataclasses.replace(p, s_channel=(p.s_channel.float() * (1.0 + d)).to(p.s_channel.dtype))
        new = QuantizedTensor(data._qdata, data._layout_cls, p2)
    else:
        new = (data.float() * (1.0 + d)).to(data.dtype)
    return torch.nn.Parameter(new, requires_grad=False)


def apply_edits(patcher, root, edits, anchors):
    for key, d in edits.items():
        name = _resolve(root, key, anchors)
        prefix = "" if root is patcher.model else None
        if prefix is None:
            raise RuntimeError("edits must resolve against patcher.model")
        patcher.add_object_patch(name, scaled_weight(_get(root, name), d))
    return patcher


class ArthemyMossModelTuner:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"model": ("MODEL",), "granular_json": ("STRING", {"multiline": True, "default": "{}"})}}
    RETURN_TYPES = ("MODEL",)
    FUNCTION = "tune"
    CATEGORY = "arthemy/moss"

    def tune(self, model, granular_json):
        edits = _parse(granular_json)
        m = model.clone(disable_dynamic=True)
        apply_edits(m, m.model, edits, ["diffusion_model."])
        return (m,)


class ArthemyMossCLIPTuner:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"clip": ("CLIP",), "granular_json": ("STRING", {"multiline": True, "default": "{}"})}}
    RETURN_TYPES = ("CLIP",)
    FUNCTION = "tune"
    CATEGORY = "arthemy/moss"

    def tune(self, clip, granular_json):
        edits = _parse(granular_json)
        c = clip.clone(disable_dynamic=True)
        # Version 3: CLIP.clone() keeps the old cond_stage_model while the patcher gets a new, non-dynamic model;
        # encoding must run on the model the patcher loads and patches.
        c.cond_stage_model = c.patcher.model
        apply_edits(c.patcher, c.patcher.model, edits, ["language_model.", "model."])
        return (c,)


NODE_CLASS_MAPPINGS = {"ArthemyMossModelTuner": ArthemyMossModelTuner, "ArthemyMossCLIPTuner": ArthemyMossCLIPTuner}
NODE_DISPLAY_NAME_MAPPINGS = {"ArthemyMossModelTuner": "Arthemy MOSS Model Tuner (w x (1+d))",
                              "ArthemyMossCLIPTuner": "Arthemy MOSS CLIP Tuner (w x (1+d))"}
