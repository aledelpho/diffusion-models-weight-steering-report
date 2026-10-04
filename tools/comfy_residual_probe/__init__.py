"""Arthemy Residual Probe — a read-only ComfyUI node for Krea-2 (SingleStreamDiT).

Install: copy this folder into ComfyUI/custom_nodes/ and restart ComfyUI.
Use: MODEL -> [Arthemy Residual Probe] -> KSampler. It does not change the model's
output: it installs forward hooks only for the duration of each model call (through
model_function_wrapper) and removes them before returning.

For every model call (one per sampling step at cfg 1.0) and every block it appends one
row to `csv_path`, measured on the IMAGE tokens only (transformer_options["img_slice"]):

  stream      mean per-token L2 norm of the block's input x
  write       mean per-token L2 norm of (output - input), i.e. what the block adds
  ratio       write / stream
  attn_write  mean per-token norm of pregate * attn(...)
  mlp_write   mean per-token norm of postgate * mlp(...)
  cos_ws      mean per-token cosine between the write and the input
Text tokens share the stream but are not measured.
Written 2026-10-04 for docs/prereg_residual_probe.md.
"""
import csv
import os
import threading

import torch

_lock = threading.Lock()


def _tok_norm(t):
    return t.float().norm(dim=-1).mean().item()


class ArthemyResidualProbe:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("MODEL",),
            "csv_path": ("STRING", {"default": r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\residual_probe_raw.csv"}),
            "run_label": ("STRING", {"default": "run"}),
        }}

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "apply"
    CATEGORY = "Arthemy/diagnostics"

    def apply(self, model, csv_path, run_label):
        m = model.clone()
        state = {"call": 0}
        prev = m.model_options.get("model_function_wrapper", None)

        def wrapper(apply_model, args):
            dm = m.model.diffusion_model
            blocks = getattr(dm, "blocks", None)
            if blocks is None:
                raise RuntimeError("Residual probe: diffusion_model has no .blocks (not Krea-2?)")
            sig = args["c"].get("transformer_options", {}).get("sigmas", None)
            sigma = float(sig.flatten()[0]) if sig is not None else float("nan")
            call = state["call"]
            state["call"] += 1
            rows, cur, handles = [], {}, []

            def mk_mod(i):
                def h(mod, inp, out):
                    cur[i] = {"pregate": out[2], "postgate": out[5]}
                return h

            def mk_sub(i, key):
                def h(mod, inp, out):
                    cur.setdefault(i, {})[key] = out
                return h

            def mk_block(i):
                def h(mod, a, kw, out):
                    x = a[0]
                    to = kw.get("transformer_options", {})
                    s0, s1 = to.get("img_slice", [0, x.shape[1]])
                    xi, yi = x[:, s0:s1], out[:, s0:s1]
                    d = (yi.float() - xi.float())
                    c = cur.get(i, {})
                    aw = _tok_norm((c["pregate"] * c["attn"])[:, s0:s1]) if "attn" in c and "pregate" in c else float("nan")
                    mw = _tok_norm((c["postgate"] * c["mlp"])[:, s0:s1]) if "mlp" in c and "postgate" in c else float("nan")
                    st = _tok_norm(xi)
                    wr = d.norm(dim=-1).mean().item()
                    cos = torch.nn.functional.cosine_similarity(d, xi.float(), dim=-1).mean().item()
                    rows.append([run_label, call, round(sigma, 5), i, round(st, 4), round(wr, 4),
                                 round(wr / st, 6), round(aw, 4), round(mw, 4), round(cos, 5)])
                    cur.pop(i, None)
                return h

            for i, b in enumerate(blocks):
                handles.append(b.mod.register_forward_hook(mk_mod(i)))
                handles.append(b.attn.register_forward_hook(mk_sub(i, "attn")))
                handles.append(b.mlp.register_forward_hook(mk_sub(i, "mlp")))
                handles.append(b.register_forward_hook(mk_block(i), with_kwargs=True))
            try:
                if prev is not None:
                    out = prev(apply_model, args)
                else:
                    out = apply_model(args["input"], args["timestep"], **args["c"])
            finally:
                for hd in handles:
                    hd.remove()
            with _lock:
                new = not os.path.exists(csv_path)
                os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
                with open(csv_path, "a", newline="") as fh:
                    w = csv.writer(fh)
                    if new:
                        w.writerow(["run", "call", "sigma", "block", "stream", "write", "ratio",
                                    "attn_write", "mlp_write", "cos_write_stream"])
                    w.writerows(rows)
            return out

        m.set_model_unet_function_wrapper(wrapper)
        return (m,)


NODE_CLASS_MAPPINGS = {"ArthemyResidualProbe": ArthemyResidualProbe}
NODE_DISPLAY_NAME_MAPPINGS = {"ArthemyResidualProbe": "Arthemy Residual Probe (read-only)"}
