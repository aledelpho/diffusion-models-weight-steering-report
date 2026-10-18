"""Krea2 Conditioning Push — a ComfyUI node for C72 (diffusion-models-weight-steering-report).

Version 2 (amendment 1 of docs/prereg_te_default.md). The push is computed inside the workflow from two live encodes
of the same prompt, in the conditioning's own precision: `conditioning` (plain CLIP) and `conditioning_edit` (the
same CLIP under an ArthemyKrea2CLIPTuner edit). Version 1 read the float16 files of C67/C68 and failed its gate.
Krea-2's conditioning is (1, seq, 12 * 2560), tap-major per token. The real push is P = edit - plain. Variants, all
with the same Frobenius norm as P on every one of the 12 taps (taps P does not reach stay at zero):

  zero      the plain conditioning, untouched (gate: must reproduce the plain render pixel for pixel)
  real      the edited conditioning, untouched (gate: must reproduce the edit's render pixel for pixel)
  permuted  plain + P with its 2560 channels permuted (one permutation from noise_seed, same for every token and
            tap): same per-token structure, per-tap norm and large channels, random direction
  shared    plain + one random unit vector per tap (from noise_seed), added to every token, scaled to P's per-tap norm
  token     plain + independent Gaussian noise per token and tap (from noise_seed), scaled to P's per-tap norm
  file      (TEP2, 2026-10-18) the conditioning tensor saved by experiments/te_massive.py at push_path, used as is
            (no arithmetic, pitfall 92); the metadata of the plain conditioning is kept. Gate: the saved plain and
            edited conditionings must reproduce their renders pixel for pixel.

No weight of the image model is edited, and in permuted/shared/token the edited encoder only serves to measure P.
"""
import numpy as np
import torch


class Krea2ConditioningPush:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "conditioning": ("CONDITIONING",),
            "conditioning_edit": ("CONDITIONING",),
            "variant": (["zero", "real", "permuted", "shared", "token", "taps", "file"],),
            "noise_seed": ("INT", {"default": 7, "min": 0, "max": 2 ** 31 - 1}),
        }, "optional": {
            "taps": ("STRING", {"default": ""}),
            "push_path": ("STRING", {"default": ""}),
        }}

    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "push"
    CATEGORY = "conditioning/probe"

    def push(self, conditioning, conditioning_edit, variant, noise_seed, taps="", push_path=""):
        if variant == "zero":
            return (conditioning,)
        if variant == "file":
            t = torch.load(push_path, map_location="cpu")
            out = []
            for c, meta in conditioning:
                if tuple(t.shape) != tuple(c.shape):
                    raise ValueError(f"saved {tuple(t.shape)} != plain {tuple(c.shape)}")
                out.append([t.to(device=c.device, dtype=c.dtype), meta])
            print(f"[Krea2ConditioningPush] file {push_path} {tuple(t.shape)} {t.dtype}")
            return (out,)
        if variant == "real":
            return (conditioning_edit,)
        out = []
        for (c, meta), (e, _) in zip(conditioning, conditioning_edit):
            if c.shape != e.shape:
                raise ValueError(f"plain {tuple(c.shape)} != edit {tuple(e.shape)}")
            seq = c.shape[1]
            P = (e[0].float() - c[0].float()).cpu().numpy().reshape(seq, 12, -1)
            rng = np.random.default_rng(noise_seed)
            norms = np.linalg.norm(P, axis=(0, 2))
            if variant == "taps":
                sel = [int(x) for x in taps.split(",") if x.strip()]
                D = np.zeros_like(P)
                D[:, sel, :] = P[:, sel, :]
                print(f"[Krea2ConditioningPush] {variant} taps={taps} seed {noise_seed}: tap norms target {np.round(norms, 2).tolist()} "
                      f"applied {np.round(np.linalg.norm(D, axis=(0, 2)), 2).tolist()}")
                res = c.clone().reshape(c.shape[0], seq, 12, -1)
                res[:, :, sel, :] = e.reshape(e.shape[0], seq, 12, -1)[:, :, sel, :]
                out.append([res.reshape(c.shape), meta])
                continue
            elif variant == "permuted":
                D = P[:, :, rng.permutation(P.shape[2])]
            elif variant == "shared":
                u = rng.standard_normal((12, P.shape[2])); u /= np.linalg.norm(u, axis=1, keepdims=True)
                D = np.broadcast_to(u[None] * (norms / np.sqrt(seq))[None, :, None], P.shape).copy()
            else:
                g = rng.standard_normal(P.shape)
                D = g * (norms / (np.linalg.norm(g, axis=(0, 2)) + 1e-12))[None, :, None]
            print(f"[Krea2ConditioningPush] {variant} taps={taps} seed {noise_seed}: tap norms target {np.round(norms, 2).tolist()} "
                  f"applied {np.round(np.linalg.norm(D, axis=(0, 2)), 2).tolist()}")
            d = torch.from_numpy(D.reshape(seq, -1).astype(np.float32)).to(device=c.device)[None]
            out.append([(c.float() + d).to(c.dtype), meta])
        return (out,)


NODE_CLASS_MAPPINGS = {"Krea2ConditioningPush": Krea2ConditioningPush}
NODE_DISPLAY_NAME_MAPPINGS = {"Krea2ConditioningPush": "Krea2 Conditioning Push (C72/C79)"}

