# MOSS-Image SFT against Krea-2 — reading the structure before any edit (MOSS0)

2026-10-25, Claude, from `docs/moss_survey.md`, `data/moss_structure_*.csv` and the ComfyUI source copied in
`docs/moss_source/` (ComfyUI 19ae172bf; tuner dbe83af). No weight loaded, no render.

## Image model

| | Krea-2 turbo | MOSS-Image SFT (bf16, 10.2 GB) |
|---|---|---|
| blocks | 28 (`blocks.#`) | 42 (`layers.#`), all of one kind |
| width | 6144 | 3072 (MLP 8192, 24 heads of 128) |
| modulation (AdaLN) | one per block (`blocks.#.mod.lin`) | **one shared by all 42 blocks** (`shared_block_modulation`) |
| per-block matrices | attention, MLP, norms | `proj.qkv` (fused q, k, v), `proj.o`, `proj.ffn_up_gate` (fused gate and up), `proj.ffn_down`, q/k norms |
| text path | 12 encoder readings mixed (txtfusion) | the encoder's **last layer only**, refined by a 2-block `text_embedder`, then joined to the image tokens in every block (single stream) |
| sampling | 9 steps, CFG 1 | 25-50 steps, CFG 2.5-3 (`er_sde` in the templates) |

Consequences for the edit W x (1+d): attention and MLP of each block can be edited as in Krea (the fused tensors scale
as a whole: q, k and v together, gate and up together). With q/k norms, scaling q and k changes nothing once
normalised, so attention edits act through v and o; the algebraic mirror found in C101 (d = -2 is the identity for
q, k, v, o scaled together) must be checked here too. Per-block modulation edits do not exist on MOSS. The text
tokens pass through every block, so an image-model edit also changes how the prompt is read inside the DiT.

## Text encoder

| | Krea-2: Qwen3-VL-4B | MOSS: Qwen3.5-9B, W4A8 GPTQ (7.3 GB) |
|---|---|---|
| layers | 36, all full attention | **32: 24 linear-attention (gated delta-rule) + 8 full attention** (every fourth, 3, 7, ..., 31) |
| width | 2560 | 4096 (MLP 12288) |
| what reaches the image model | 12 readings (layers 2, 5, ..., 35) | the last layer only |
| weights | bf16 | **4-bit codebook**: `weight` (I8, two 4-bit codes per byte) x `weight_codebook` (16 values) x `weight_s_rel` (F8, one per 16 inputs) x `weight_s_channel` (F32, one per output) |
| prompt | plain | a chat template with an open think block |

Consequences: (1) W x (1+d) on a quantised matrix is exact by scaling `weight_s_channel` by (1+d): no requantisation,
no extra quantisation error. That applies to every MLP (gate, up, down; 32 layers), to the full-attention projections
(8 layers) and to the linear-attention projections (`in_proj_qkv`, `in_proj_z`, `out_proj`; 24 layers). (2) With one
reading, Krea results that depend on the 12 readings (C79, C87) have no counterpart; the size-of-push and genre results
(page 30) can be tested directly. (3) Two kinds of layer give a new question: do linear-attention and full-attention
layers behave differently when edited? The vision tower and the MTP layer in the file are not used for text-to-image.

## What the tuner needs (MOSS1)

* Image model: a key map from Krea names to MOSS names (`blocks.N.attn.*` → `layers.N.proj.qkv / proj.o`,
  `blocks.N.mlp.*` → `layers.N.proj.ffn_up_gate / ffn_down`), with 42 blocks; no modulation knobs.
* Text encoder: the edit on `weight_s_channel` for quantised matrices, on `weight` for bf16 ones; the loader type
  `moss_image`; layer indices 0-31.
* Gates before any experiment: d = 0 pixel-identical to the plain render; an `s_channel` edit equal (within tolerance) to
  the dequantised weight scaled in float32 on one layer; one known strong edit visibly changing a picture.
