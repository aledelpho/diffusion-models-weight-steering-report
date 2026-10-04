# Pre-registration C48 — how much each block writes into the residual stream

Written 2026-10-04, before the probe has run. Follows `block_weight_structure_result.md` §3,
which named this as the direct test that weights alone cannot give.

## What is measured

`tools/comfy_residual_probe/` — a read-only ComfyUI node. Forward hooks on each of the
28 `SingleStreamBlock`s of Krea-2 (`comfy/ldm/krea2/model.py`), installed only during
each model call. Per block and sampling step, on image tokens only: the norm of the
block's input (the stream), of what it adds (`write`), their ratio, the gated attention
and MLP contributions separately, and the cosine between the write and the stream.

Runs (`experiments/queue_residual_probe.py`, launched by Alessandro): the 23 baselines
of single_blocks_styles (12), v3 (6) and v4 (5), same seeds and settings, no weight
edit. 23 runs × 9 steps × 28 blocks = 5 796 rows.

**Gate:** the 23 probe images must be pixel-identical to the existing baselines
(`analyze_residual_probe.py --repro`). If not, the probe is not read-only and nothing
is scored.

## Predictions and decision rules (`experiments/analyze_residual_probe.py`)

Per block, everything is averaged over steps and runs. Stability is the same variable
as in C46 (`data/block_colour_layout.csv`).

- **P1 — leverage is relative write size.** The blocks that write more relative to the
  stream are the ones that reorganise the image. Spearman(ratio, stability) over 28
  blocks: **≤ −0.5 supported, > −0.3 refuted**, in between inconclusive. The
  depth-removed version is reported, not tested.
- **P2 — the C46 weight finding shows up in the activations.** Among blocks 02–20 the
  largest MLP write relative to the stream belongs to **block 08 or 09**. Otherwise
  refuted.
- **P3 — the assumption used in C46.** The stream norm grows with depth: Spearman(stream,
  block index) **≥ 0.8**. Otherwise refuted — and the "late blocks have a big stream to
  push against" part of the depth argument falls with it.

## Not covered

Edited models (the probe after the Tuner) are a natural second phase — how a blk23 or
blk09 edit changes the downstream writes — and are not registered here.
