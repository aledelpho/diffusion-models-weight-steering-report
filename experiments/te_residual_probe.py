"""Zero-render residual-stream write probe across all 36 layers of Qwen3-VL-4B.

Note on ComfyUI's TransformerBlock.forward (comfy/text_encoders/llama.py:798-815):
  `output = x` is mutated in-place at the end of the block via
  `torch.add(residual, x, out=output)`.
Therefore, a standard post-forward hook on the block sees `inp[0] == out[0]`.
We capture `h_in` via a `forward_pre_hook` (cloning before in-place overwrite),
`dh_attn` via a hook on `self_attn`, and `dh_mlp` via a hook on `mlp`.
"""
import csv, math, sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
COMFY = Path(r"D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI")
CLIP_PATH = Path(r"D:\StabilityMatrix-win-x64\Data\Models\TextEncoders\qwen3vl_4b_bf16.safetensors")
TAPS = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]

OUT_BY_PROMPT = REPO / "data" / "te_residual_probe_by_prompt.csv"
OUT_SUMMARY = REPO / "data" / "te_residual_probe_summary.csv"

CANONICAL_PROMPTS = {
    "knight": "A medieval knight in ornate steel plate armor with gold filigree trim and a flowing crimson cape, standing in a cobblestone courtyard at dusk",
    "portrait": "Close-up studio portrait of an elderly fisherman with deep weathered wrinkles, white beard, and a yellow oilskin raincoat, dramatic side lighting",
    "street": "A narrow rain-slicked Tokyo alleyway at night, glowing neon kanji signs reflecting in puddles, steam rising from a street food cart",
}


def load_prompts():
    prompts = dict(CANONICAL_PROMPTS)
    with open(REPO / "data" / "te_characters_plan.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["char"] not in prompts:
                prompts[r["char"]] = r["prompt_text"]
    return prompts


def main():
    sys.path.insert(0, str(COMFY))
    import torch
    import comfy.sd

    prompts = load_prompts()
    print(f"Loaded {len(prompts)} prompts: {list(prompts.keys())}")

    clip = comfy.sd.load_clip(
        ckpt_paths=[str(CLIP_PATH)],
        embedding_directory=str(COMFY / "models" / "embeddings"),
        clip_type=comfy.sd.CLIPType.KREA2,
    )

    # Locate the 36 TransformerBlock modules
    layers = None
    for name, mod in clip.cond_stage_model.named_modules():
        if name.endswith("model.layers") and hasattr(mod, "__len__") and len(mod) == 36:
            layers = mod
            break
    assert layers is not None, "Could not locate 36-layer ModuleList in Qwen3-VL-4B"

    # Integrity gate: verify clean determinism before attaching hooks
    t0 = clip.tokenize(prompts["knight"])
    c_a = clip.encode_from_tokens_scheduled(t0)[0][0].detach().float().cpu()
    c_b = clip.encode_from_tokens_scheduled(t0)[0][0].detach().float().cpu()
    gate_diff = float((c_a - c_b).abs().max().item())
    print(f"DETERMINISM GATE max_abs_diff = {gate_diff}")
    assert gate_diff == 0.0, f"Determinism gate failed: {gate_diff}"

    rows = []
    max_recon_err = 0.0

    for pid, text in prompts.items():
        store = {}
        handles = []

        for idx, blk in enumerate(layers):
            def make_pre(i):
                def _pre(mod, args):
                    store[(i, "in")] = args[0].detach().float().cpu().clone()
                return _pre

            def make_attn(i):
                def _attn(mod, args, out):
                    t = out[0] if isinstance(out, tuple) else out
                    store[(i, "attn")] = t.detach().float().cpu().clone()
                return _attn

            def make_mlp(i):
                def _mlp(mod, args, out):
                    t = out[0] if isinstance(out, tuple) else out
                    store[(i, "mlp")] = t.detach().float().cpu().clone()
                return _mlp

            def make_post(i):
                def _post(mod, args, out):
                    t = out[0] if isinstance(out, tuple) else out
                    store[(i, "out")] = t.detach().float().cpu().clone()
                return _post

            handles.append(blk.input_layernorm.register_forward_pre_hook(make_pre(idx)))
            handles.append(blk.self_attn.register_forward_hook(make_attn(idx)))
            handles.append(blk.mlp.register_forward_hook(make_mlp(idx)))
            handles.append(blk.register_forward_hook(make_post(idx)))

        tokens = clip.tokenize(text)
        c_out = clip.encode_from_tokens_scheduled(tokens)[0][0].detach().float().cpu()

        for h in handles:
            h.remove()

        if pid == "knight":
            hook_diff = float((c_out - c_a).abs().max().item())
            print(f"HOOK NON-INTRUSION GATE max_abs_diff = {hook_diff}")
            assert hook_diff == 0.0, f"Hooks altered output: {hook_diff}"

        for idx in range(36):
            h_in = store[(idx, "in")][0]      # [seq_len, 2560]
            dh_attn = store[(idx, "attn")][0]
            dh_mlp = store[(idx, "mlp")][0]
            h_out = store[(idx, "out")][0]
            dh_blk = dh_attn + dh_mlp

            # Relative reconstruction error in BF16 arithmetic
            recon_rel = float((h_in + dh_blk - h_out).norm().item() / (h_out.norm().item() + 1e-12))
            if recon_rel > max_recon_err:
                max_recon_err = recon_rel

            n_in = float(h_in.norm().item())
            n_out = float(h_out.norm().item())
            n_blk = float(dh_blk.norm().item())
            n_attn = float(dh_attn.norm().item())
            n_mlp = float(dh_mlp.norm().item())

            # Per-token cosine between attn write and mlp write
            dot = float((dh_attn * dh_mlp).sum().item())
            cos_am = dot / (n_attn * n_mlp + 1e-12)

            # Exclude token 0 (BOS/sink) to measure content-token write ratios
            h_in_c = h_in[1:]
            dh_blk_c = dh_blk[1:]
            dh_attn_c = dh_attn[1:]
            dh_mlp_c = dh_mlp[1:]
            n_in_c = float(h_in_c.norm().item())
            n_blk_c = float(dh_blk_c.norm().item())
            n_attn_c = float(dh_attn_c.norm().item())
            n_mlp_c = float(dh_mlp_c.norm().item())

            rows.append({
                "prompt_id": pid,
                "seq_len": int(h_in.shape[0]),
                "layer": idx,
                "is_tap": 1 if idx in TAPS else 0,
                "norm_in": round(n_in, 6),
                "norm_out": round(n_out, 6),
                "r_block_all": round(n_blk / (n_in + 1e-12), 6),
                "r_attn_all": round(n_attn / (n_in + 1e-12), 6),
                "r_mlp_all": round(n_mlp / (n_in + 1e-12), 6),
                "mlp_over_attn_all": round(n_mlp / (n_attn + 1e-12), 6),
                "r_block_content": round(n_blk_c / (n_in_c + 1e-12), 6),
                "r_attn_content": round(n_attn_c / (n_in_c + 1e-12), 6),
                "r_mlp_content": round(n_mlp_c / (n_in_c + 1e-12), 6),
                "mlp_over_attn_content": round(n_mlp_c / (n_attn_c + 1e-12), 6),
                "cos_attn_mlp": round(cos_am, 6),
            })

    print(f"MAX BF16 RECONSTRUCTION RELATIVE ERROR = {max_recon_err:.6f}")

    with open(OUT_BY_PROMPT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    summary = []
    for idx in range(36):
        sub = [r for r in rows if r["layer"] == idx]
        summary.append({
            "layer": idx,
            "is_tap": 1 if idx in TAPS else 0,
            "tap_idx": TAPS.index(idx) if idx in TAPS else -1,
            "mean_norm_in": round(float(np.mean([r["norm_in"] for r in sub])), 4),
            "mean_norm_out": round(float(np.mean([r["norm_out"] for r in sub])), 4),
            "mean_r_block_all": round(float(np.mean([r["r_block_all"] for r in sub])), 6),
            "mean_r_attn_all": round(float(np.mean([r["r_attn_all"] for r in sub])), 6),
            "mean_r_mlp_all": round(float(np.mean([r["r_mlp_all"] for r in sub])), 6),
            "mean_mlp_over_attn_all": round(float(np.mean([r["mlp_over_attn_all"] for r in sub])), 6),
            "mean_r_block_content": round(float(np.mean([r["r_block_content"] for r in sub])), 6),
            "mean_r_attn_content": round(float(np.mean([r["r_attn_content"] for r in sub])), 6),
            "mean_r_mlp_content": round(float(np.mean([r["r_mlp_content"] for r in sub])), 6),
            "mean_mlp_over_attn_content": round(float(np.mean([r["mlp_over_attn_content"] for r in sub])), 6),
            "mean_cos_attn_mlp": round(float(np.mean([r["cos_attn_mlp"] for r in sub])), 6),
        })

    with open(OUT_SUMMARY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)

    print(f"Wrote {OUT_BY_PROMPT.name} ({len(rows)} rows) and {OUT_SUMMARY.name} ({len(summary)} rows)")
    for s in summary:
        if s["layer"] in (0, 1, 2, 5, 6, 11, 14, 17, 20, 23, 26, 28, 29, 32, 35):
            print(
                f"L{s['layer']:02d} (tap={s['tap_idx']:2d}): "
                f"r_blk_all={s['mean_r_block_all']:.4f} (attn={s['mean_r_attn_all']:.4f}, mlp={s['mean_r_mlp_all']:.4f}, m/a={s['mean_mlp_over_attn_all']:.2f}) | "
                f"r_blk_cnt={s['mean_r_block_content']:.4f} (attn={s['mean_r_attn_content']:.4f}, mlp={s['mean_r_mlp_content']:.4f}, m/a={s['mean_mlp_over_attn_content']:.2f})"
            )


if __name__ == "__main__":
    main()
