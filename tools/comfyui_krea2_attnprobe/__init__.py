"""Krea2 Attention Probe — a ComfyUI model-patch node for C69 (diffusion-models-weight-steering-report).

Attaches an attn1_patch to Krea-2's single-stream blocks that READS queries and keys (it changes nothing: the patch
returns no replacement) and records, for every sampling step and every block, how much attention each image region
pays to each group of text tokens:

    softmax over all keys (text + image) of  q_img . k / sqrt(d)   (RoPE applied as the model does),
    averaged over heads, summed over the text positions of each unit, image pooled `pool` x `pool`.

Text positions are those of the conditioning (template prefix stripped); `units` is a JSON list of [start, end)
spans over them, computed by the caller from the token ids. One .npz per step: attn (blocks, H/pool, W/pool, units)
float16, text_total (blocks, H/pool, W/pool) = attention mass on all text, sigma.
"""
import json
import os

import numpy as np
import torch


class Krea2AttentionProbe:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("MODEL",),
            "out_dir": ("STRING", {"default": ""}),
            "units": ("STRING", {"multiline": True, "default": "[]"}),
            "grid": ("STRING", {"default": "80,64"}),     # image tokens: rows, cols (1280 x 1024 px)
            "pool": ("INT", {"default": 2, "min": 1, "max": 16}),
        }}

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "patch"
    CATEGORY = "model_patches/probe"

    def patch(self, model, out_dir, units, grid, pool):
        from comfy.ldm.flux.math import apply_rope
        spans = json.loads(units)
        gh, gw = [int(x) for x in grid.split(",")]
        os.makedirs(out_dir, exist_ok=True)
        state = {"step": 0, "buf": {}, "tt": {}}

        def probe(q, k, v, pe=None, attn_mask=None, extra_options={}):
            if extra_options.get("block_type") != "single" or "img_slice" not in extra_options:
                return {}
            b = int(extra_options["block_index"]); nb = int(extra_options.get("total_blocks", 28))
            s0, s1 = extra_options["img_slice"]
            with torch.no_grad():
                qq, kk = q[:1].float(), k[:1].float()
                if pe is not None:
                    qq, kk = apply_rope(qq, kk, pe[:1] if pe.shape[0] > 1 else pe)
                hq, hk = qq.shape[1], kk.shape[1]
                if hk != hq:
                    kk = kk.repeat_interleave(hq // hk, dim=1)
                scale = qq.shape[-1] ** -0.5
                acc = None
                for h in range(hq):
                    a = torch.softmax((qq[0, h, s0:s1] @ kk[0, h].T) * scale, dim=-1)[:, :s0]   # (img, txt)
                    acc = a if acc is None else acc + a
                acc = acc / hq
                img = acc.shape[0]
                if img != gh * gw:
                    return {}
                per_unit = torch.stack([acc[:, s:e].sum(-1) for s, e in spans], dim=-1) if spans else acc.sum(-1, keepdim=True)
                tot = acc.sum(-1)
                def pool2(x):
                    x = x.reshape(gh // pool, pool, gw // pool, pool, *x.shape[1:]) if x.ndim == 2 else x.reshape(gh // pool, pool, gw // pool, pool)
                    return x.mean(dim=(1, 3))
                state["buf"][b] = pool2(per_unit.reshape(gh * gw, -1)).cpu().numpy().astype(np.float16)
                state["tt"][b] = pool2(tot).cpu().numpy().astype(np.float16)
            if b == nb - 1:
                sig = extra_options.get("sigmas")
                sig = float(sig.flatten()[0]) if torch.is_tensor(sig) else -1.0
                np.savez_compressed(os.path.join(out_dir, f"step{state['step']:02d}.npz"),
                                    attn=np.stack([state["buf"][i] for i in range(nb)]),
                                    text_total=np.stack([state["tt"][i] for i in range(nb)]), sigma=np.float32(sig))
                state["step"] += 1; state["buf"] = {}; state["tt"] = {}
            return {}

        m = model.clone()
        m.set_model_attn1_patch(probe)
        return (m,)


NODE_CLASS_MAPPINGS = {"Krea2AttentionProbe": Krea2AttentionProbe}
NODE_DISPLAY_NAME_MAPPINGS = {"Krea2AttentionProbe": "Krea2 Attention Probe (C69)"}
