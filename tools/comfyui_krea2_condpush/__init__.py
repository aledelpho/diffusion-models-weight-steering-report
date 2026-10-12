"""Krea2 Conditioning Push — a ComfyUI node for C72 (diffusion-models-weight-steering-report).

Adds a displacement to Krea-2's conditioning (1, seq, 12 * 2560) after CLIPTextEncode, built from two "full" files of
the C67/C68 probes (stored as (seq, 12, 2560) float16): the baseline of a prompt and the same prompt under a
text-encoder edit. The real push is P = edit - baseline. Variants, all with the same Frobenius norm as P on every
one of the 12 taps (taps P does not reach stay at zero):

  zero      no displacement (gate: must reproduce the plain render pixel for pixel)
  real      P itself (positive control: must reproduce the edit's render closely)
  permuted  P with its 2560 channels permuted (one permutation from noise_seed, same for every token and tap):
            same per-token structure and per-tap norm, random direction
  shared    one random unit vector per tap (from noise_seed), added to every token, scaled to P's per-tap norm
  token     independent Gaussian noise per token and tap (from noise_seed), scaled to P's per-tap norm

No weight is edited. The node prints the per-tap norms it applied.
"""
import numpy as np
import torch


def _load(path):
    return np.load(path)["cond"].astype(np.float32)          # (seq, 12, 2560)


class Krea2ConditioningPush:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "conditioning": ("CONDITIONING",),
            "baseline_path": ("STRING", {"default": ""}),
            "edit_path": ("STRING", {"default": ""}),
            "variant": (["zero", "real", "permuted", "shared", "token"],),
            "noise_seed": ("INT", {"default": 7, "min": 0, "max": 2 ** 31 - 1}),
        }}

    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "push"
    CATEGORY = "conditioning/probe"

    def push(self, conditioning, baseline_path, edit_path, variant, noise_seed):
        out = []
        for c, meta in conditioning:
            seq = c.shape[1]
            if variant == "zero":
                out.append([c, meta]); continue
            P = _load(edit_path) - _load(baseline_path)
            if P.shape[0] != seq:
                raise ValueError(f"push has {P.shape[0]} positions, conditioning has {seq}")
            rng = np.random.default_rng(noise_seed)
            norms = np.linalg.norm(P.reshape(seq, 12, -1), axis=(0, 2))           # per tap
            if variant == "real":
                D = P
            elif variant == "permuted":
                D = P[:, :, rng.permutation(P.shape[2])]
            elif variant == "shared":
                u = rng.standard_normal((12, P.shape[2])); u /= np.linalg.norm(u, axis=1, keepdims=True)
                D = np.broadcast_to(u[None] * (norms / np.sqrt(seq))[None, :, None], P.shape).copy()
            else:
                g = rng.standard_normal(P.shape)
                g *= (norms / (np.linalg.norm(g, axis=(0, 2)) + 1e-12))[None, :, None]
                D = g
            got = np.linalg.norm(D, axis=(0, 2))
            print(f"[Krea2ConditioningPush] {variant} seed {noise_seed}: tap norms target {np.round(norms, 2).tolist()} "
                  f"applied {np.round(got, 2).tolist()}")
            d = torch.from_numpy(D.reshape(seq, -1)).to(device=c.device, dtype=torch.float32)[None]
            out.append([(c.float() + d).to(c.dtype), meta])
        return (out,)


NODE_CLASS_MAPPINGS = {"Krea2ConditioningPush": Krea2ConditioningPush}
NODE_DISPLAY_NAME_MAPPINGS = {"Krea2ConditioningPush": "Krea2 Conditioning Push (C72)"}
