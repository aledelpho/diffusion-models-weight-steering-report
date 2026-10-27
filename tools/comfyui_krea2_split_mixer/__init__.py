"""Arthemy Krea-2 Split Mixer - one slider per block half (attention, MLP) of the image model and of the text encoder.
Written 2026-10-27 by Claude for Alessandro, to compose presets freely on any prompt and seed from what the report
learned (diffusion-models-weight-steering-report, pages 21, 22, 29, 30, 31).

Two nodes. Each turns its sliders into a granular_json and applies it through the Arthemy Krea-2 tuner itself, in
"Real Value" mode (weight x (1 + d)), the exact path of every experiment in the report:

  ArthemyKrea2SplitMixerModel  MODEL -> MODEL, json, info   28 blocks x {attn, mlp}
      attn = blocks.N.attn.{wq, wk, wv, gate, wo};  mlp = blocks.N.mlp.{gate, up, down}
  ArthemyKrea2SplitMixerCLIP   CLIP -> CLIP, json, info     36 layers x {attn, mlp}
      attn = layers.L.self_attn.{q,k,v,o}_proj;  mlp = layers.L.mlp.{gate,up,down}_proj

`scale` multiplies every slider (a dose ladder with one knob). `extra_json` is merged last (exact keys win).
The json output can be saved as a preset or pasted into the tuner's granular_json.
"""
import json

GUIDE = {  # page 21, "A starting guide" (whole block; negative / positive; hand-drawn, provisional)
    0: "neg: more grain, detail, colour | pos: soft, hazy", 1: "neg: softer colours | pos: patchy colour, flat tints, grain",
    2: "neg: fine textures | pos: flat fills, colour blocks", 3: "neg: less natural light | pos: natural 3D light",
    4: "neg: fine detail | pos: coarse, abstract", 5: "neg: darker, dirtier | pos: brighter, cleaner",
    6: "neg: volume, organic | pos: more colour, stylised", 7: "neg: less concept bleeding | pos: more bleeding, deformation",
    8: "neg: expression, natural poses | pos: texture realism, flattening", 9: "neg: less realism of materials | pos: more realism",
    10: "neg: more expression | pos: less expression", 11: "neg: camera control, style | pos: deformation, abstraction",
    12: "neg: perspective, imperfections | pos: deformation", 13: "neg: organic | pos: geometric",
    14: "neg: distinct details | pos: colour contrast, texture depth", 15: "neg: depth, realistic detail | pos: flattened",
    16: "neg: complex textures | pos: muffled, abstract", 17: "neg: closer to the prompt | pos: simpler, further",
    18: "neg: depth and volume | pos: less depth", 19: "neg: shaped by form | pos: shaped by light",
    20: "neg: parts blend | pos: parts separate", 21: "neg: finer grain | pos: coarser grain",
    22: "neg: sharpens, flattens | pos: blurs, softens", 23: "neg: more saturation | pos: less saturation (page 22)",
    24: "neg: more colour contrast | pos: softer colours", 25: "neg: less colour blur | pos: more colour blur",
    26: "neg: fewer fine textures | pos: more fine texture", 27: "neg: blurs, darkens | pos: grain, lightens",
}
TE_NOTES = {  # pages 30-31, MLP doubled unless said otherwise
    0: "attn or MLP off: the picture writes the prompt as text (C77)", 5: "MLP x2: the elf goes anime (C70)",
    6: "MLP x2: realistic renders, characters lose traits, skin lighter (C73-C75); writes the internal signal",
    14: "MLP x2: cartoon, character traits lost (C73-C75)", 26: "MLP x2: keeps the Western comic (C73)",
    28: "MLP x2: keeps the comic and the character (C72-C75)",
}
DIT_ATTN = ("wq", "wk", "wv", "gate", "wo")
DIT_MLP = ("gate", "up", "down")
TE_ATTN = ("q_proj", "k_proj", "v_proj", "o_proj")
TE_MLP = ("gate_proj", "up_proj", "down_proj")


def _tuner(name):
    import nodes
    cls = nodes.NODE_CLASS_MAPPINGS.get(name)
    if cls is None:
        raise RuntimeError(f"{name} not found: the Arthemy Krea-2 tuner must be installed")
    zeros = {k: 0.0 for k, v in cls.INPUT_TYPES().get("required", {}).items() if isinstance(v, tuple) and v and v[0] == "FLOAT"}
    return cls(), zeros


def _merge(base, extra):
    extra = (extra or "").strip()
    if extra:
        e = json.loads(extra)
        if not isinstance(e, dict):
            raise ValueError("extra_json must be a JSON object")
        base.update({str(k): float(v) for k, v in e.items()})
    return base


def _info(sliders):
    on = [f"{k} {v:+.3f}" for k, v in sliders.items() if v]
    return "active: " + (", ".join(on) if on else "none")


class ArthemyKrea2SplitMixerModel:
    @classmethod
    def INPUT_TYPES(cls):
        req = {"model": ("MODEL",), "scale": ("FLOAT", {"default": 1.0, "min": -4.0, "max": 4.0, "step": 0.05,
                                                         "tooltip": "multiplies every slider"})}
        for b in range(28):
            for h in ("attn", "mlp"):
                req[f"b{b:02d}_{h}"] = ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.005,
                                                  "tooltip": f"block {b} {h}. Whole-block guide: {GUIDE[b]}"})
        return {"required": req, "optional": {"extra_json": ("STRING", {"default": "", "multiline": True})}}

    RETURN_TYPES = ("MODEL", "STRING", "STRING")
    RETURN_NAMES = ("MODEL", "granular_json", "info")
    FUNCTION = "mix"
    CATEGORY = "arthemy/krea2"

    def mix(self, model, scale, extra_json="", **sl):
        g = {}
        for b in range(28):
            for h, mats in (("attn", DIT_ATTN), ("mlp", DIT_MLP)):
                d = float(sl.get(f"b{b:02d}_{h}", 0.0)) * scale
                if d:
                    for m in mats:
                        g[f"blocks.{b}.{h}.{m}.weight"] = round(d, 6)
        g = _merge(g, extra_json)
        js = json.dumps(g)
        if not g:
            return (model, "{}", "no edit")
        tuner, zeros = _tuner("ArthemyKrea2ModelTuner")
        out = tuner.tune_model(model, mode="Real Value", vectors_override="", granular_json=js, **zeros)
        return (out[0], js, _info({k: v * scale for k, v in sl.items()}) + f" | scale {scale}")


class ArthemyKrea2SplitMixerCLIP:
    @classmethod
    def INPUT_TYPES(cls):
        req = {"clip": ("CLIP",), "scale": ("FLOAT", {"default": 1.0, "min": -4.0, "max": 4.0, "step": 0.05,
                                                       "tooltip": "multiplies every slider"})}
        for L in range(36):
            for h in ("attn", "mlp"):
                tip = f"text-encoder layer {L} {h}." + (f" Report: {TE_NOTES[L]}" if L in TE_NOTES else "")
                req[f"L{L:02d}_{h}"] = ("FLOAT", {"default": 0.0, "min": -1.0, "max": 2.0, "step": 0.01, "tooltip": tip})
        return {"required": req, "optional": {"extra_json": ("STRING", {"default": "", "multiline": True})}}

    RETURN_TYPES = ("CLIP", "STRING", "STRING")
    RETURN_NAMES = ("CLIP", "granular_json", "info")
    FUNCTION = "mix"
    CATEGORY = "arthemy/krea2"

    def mix(self, clip, scale, extra_json="", **sl):
        g = {}
        for L in range(36):
            for h, mats in (("attn", TE_ATTN), ("mlp", TE_MLP)):
                d = float(sl.get(f"L{L:02d}_{h}", 0.0)) * scale
                if d:
                    part = "self_attn" if h == "attn" else "mlp"
                    for m in mats:
                        g[f"layers.{L}.{part}.{m}.weight"] = round(d, 6)
        g = _merge(g, extra_json)
        js = json.dumps(g)
        if not g:
            return (clip, "{}", "no edit")
        tuner, zeros = _tuner("ArthemyKrea2CLIPTuner")
        out = tuner.tune_clip(clip, mode="Real Value", vectors_override="", granular_json=js, **zeros)
        return (out[0], js, _info({k: v * scale for k, v in sl.items()}) + f" | scale {scale}")


NODE_CLASS_MAPPINGS = {"ArthemyKrea2SplitMixerModel": ArthemyKrea2SplitMixerModel,
                       "ArthemyKrea2SplitMixerCLIP": ArthemyKrea2SplitMixerCLIP}
NODE_DISPLAY_NAME_MAPPINGS = {"ArthemyKrea2SplitMixerModel": "Arthemy Krea-2 Split Mixer (model: attn / MLP per block)",
                              "ArthemyKrea2SplitMixerCLIP": "Arthemy Krea-2 Split Mixer (text encoder: attn / MLP per layer)"}
