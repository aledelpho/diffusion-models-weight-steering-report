"""Krea2 Conditioning Probe — a ComfyUI output node for C67 (diffusion-models-weight-steering-report).

Encodes a prompt with the CLIP it receives (so any ArthemyKrea2CLIPTuner patch upstream is applied, exactly as for
CLIPTextEncode) and writes what Krea-2's DiT would receive to a .npz file, instead of generating an image.

Krea-2's conditioning is (1, seq, 12 * 2560): the 12 tapped hidden states of Qwen3-VL-4B (layers 2, 5, ..., 35,
final norm applied), template prefix stripped (comfy/text_encoders/krea2.py). The node stores it as (seq, 12, 2560).

mode = "full": cond (float16), ids (token ids aligned with the positions); optional "taps" keeps only those tap
       indices (C68 stores the last three, 9,10,11 = layers 29, 32, 35)
mode = "diff": against baseline_path (a "full" file of the same prompt): per position and tap the relative change
       |c - b| / |b| and the cosine, the change of the mean over positions per tap, and the ids.
"""
import json
import os

import numpy as np
import torch


class Krea2ConditioningProbe:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "clip": ("CLIP",),
            "text": ("STRING", {"multiline": True}),
            "out_path": ("STRING", {"default": ""}),
            "mode": (["full", "diff"],),
            "baseline_path": ("STRING", {"default": ""}),
        }, "optional": {
            "taps": ("STRING", {"default": ""}),   # C68: e.g. "9,10,11" keeps only those tap indices in mode "full"
        }}

    RETURN_TYPES = ()
    FUNCTION = "probe"
    OUTPUT_NODE = True
    CATEGORY = "conditioning/probe"

    def probe(self, clip, text, out_path, mode, baseline_path, taps=""):
        tokens = clip.tokenize(text)
        out = clip.encode_from_tokens(tokens, return_pooled=False, return_dict=True)
        cond = out["cond"]                                   # (1, seq, 12 * 2560)
        seq = cond.shape[1]
        c = cond[0].float().reshape(seq, 12, -1).cpu().numpy()
        key = next(iter(tokens))
        ids = [int(t[0]) if not torch.is_tensor(t[0]) else -1 for t in tokens[key][0]]
        ids = np.array(ids[-seq:], dtype=np.int64)           # the template prefix is stripped at the start
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        if mode == "full":
            sel = [int(t) for t in taps.split(",")] if taps.strip() else list(range(c.shape[1]))
            np.savez_compressed(out_path, cond=c[:, sel].astype(np.float16), ids=ids, taps=np.array(sel))
        else:
            b = np.load(baseline_path)["cond"].astype(np.float32)
            if b.shape != c.shape:
                raise ValueError(f"baseline shape {b.shape} != {c.shape}")
            d = c - b
            nb = np.linalg.norm(b, axis=-1) + 1e-6
            rel = np.linalg.norm(d, axis=-1) / nb
            cosv = (c * b).sum(-1) / (np.linalg.norm(c, axis=-1) * nb + 1e-6)
            np.savez_compressed(out_path, rel=rel.astype(np.float32), cos=cosv.astype(np.float32),
                                dmean=d.mean(0).astype(np.float16), ids=ids)
        print(f"[Krea2ConditioningProbe] {mode} {c.shape} -> {out_path}")
        return {"ui": {"text": [json.dumps({"seq": int(seq), "out": out_path})]}}


NODE_CLASS_MAPPINGS = {"Krea2ConditioningProbe": Krea2ConditioningProbe}
NODE_DISPLAY_NAME_MAPPINGS = {"Krea2ConditioningProbe": "Krea2 Conditioning Probe (C67)"}
