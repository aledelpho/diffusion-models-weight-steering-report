# Model structures — what was inspected, and how

These files describe **how the checkpoints are built**, not what they contain. For every tensor
they record the name, dtype, shape, element count and byte size. **No weight values are included**,
and none of these files lets anyone reconstruct a model.

They were produced by reading only the **safetensors header** — the JSON block at the start of the
file that lists the tensor table. Nothing beyond that header was read, and no checkpoint is
redistributed here.

They are published for one reason: every displacement figure in this notebook is a *relative*
Frobenius norm, and checking those numbers requires knowing the exact shapes. Without this, "verify
it yourself" is a promise a reader cannot keep.

## What is here

| File | Model | Tensors | Parameters |
|---|---|---|---|
| `anima_base_v10_*` | Anima Base v1.0 (Cosmos-Predict2 2B) | 685 | 2,091,068,928 |
| `qwen_3_06b_base_*` | Qwen3 0.6B — Anima's text encoder | 310 | 596,049,920 |
| `krea2_turbo_bf16_*` | Krea-2 Turbo | 430 | 12,820,073,036 |
| `qwen3vl_4b_bf16_*` | Qwen3-VL 4B — Krea-2's text/vision encoder | 713 | 4,437,815,808 |
| `qwen3vl_4b_fp8_scaled_*` | the same encoder, FP8 E4M3 with companion scales | 1,217 | 4,437,832,188 |

Plus two architectural write-ups with block anatomy and diagrams:
[`anima_architecture_decomposition.md`](anima_architecture_decomposition.md) and
[`krea2_architecture_decomposition.md`](krea2_architecture_decomposition.md).

These are the base checkpoints the experiments run on.

## Two traps these files expose

**The base checkpoint and a ComfyUI-saved copy share no tensor names.** Anima Base v1.0 prefixes
every key with `net.` (`net.blocks.0.self_attn.q_proj.weight`); a checkpoint saved out of ComfyUI
uses `model.diffusion_model.` instead. The two spellings have **zero keys in common**, so any
offline script that reads the file directly — norm computation, control derivation, integrity gates
— has to handle both, or it will find nothing and say so only if it was written to. This is
[pitfall 15](../errors_log.md) in a new costume.

**The LLM adapter blocks are not shaped like the main blocks.** In Anima, `blocks.N` carries 20
tensors with `self_attn.output_proj` and `mlp.layer1` / `mlp.layer2`; `llm_adapter.blocks.N` carries
19, with `self_attn.o_proj`, `mlp.0` / `mlp.2`, three extra norm tensors and — unlike the main
blocks — **biases**. One sub-tensor map cannot cover both, and a map that silently matches nothing
is the failure mode this notebook keeps running into.

## Licensing

These are factual descriptions of file layout, in the same category as a `config.json` or a model
card. They are published under this repository's [MIT licence](../../LICENSE); the checkpoints
themselves remain under their own licences and are not distributed here.
