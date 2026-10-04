# Pre-registration C46 — is the stable / unstable split visible in the weights?

Written 2026-10-04, **before any weight of `krea2_turbo_bf16.safetensors` was read**
for this question. Committed before the script runs.

## Question

Alessandro: do the blocks that behave as near-linear knobs (stable) have a different
internal structure from the blocks that rewrite the image and its style?

Fact already known: architecturally they are identical. Each of the 28 blocks has the
same 13 tensors with the same shapes (`docs/model_structures/krea2_turbo_bf16_details.json`):
eight 2-D (`attn.wq/wk/wv/wo/gate`, `mlp.up/gate/down`) and five 1-D
(`attn.qknorm.{q,k}norm.scale`, `prenorm.scale`, `postnorm.scale`, `mod.lin` 36 864 =
6 × 6144). Any difference is in the values.

## The behavioural variable (already measured, fixed here)

`stability_b` = mean `layout_r` of block b over both signs and all 23 prompts in
`data/block_colour_layout.csv` (commit 81b89af). It is U-shaped in depth: ends high
(21–27: 0.88), middle low (05–14: 0.65).

## Weight statistics (computed per block, 28 values each)

For each 2-D tensor W: Frobenius norm ‖W‖_F; spectral norm σ₁ (power iteration, 50
steps, fixed seed 0); stable rank ‖W‖_F² / σ₁². Derived: attention write proxy
σ₁(wo)·σ₁(wv); MLP write proxy σ₁(down)·max(σ₁(up), σ₁(gate)). For each 1-D
tensor: mean and SD; for `mod.lin`, the norm of each of its six 6144-chunks
(descriptive only — the chunk order is not documented). 8 × 3 + 2 + 4 × 2 = **34
statistics** enter the test; the `mod.lin` chunks are reported, not tested.

## Hypotheses and decision rule

- **H_depth (Claude's prediction):** stability comes from position — near the input
  and the output the representation is closest to the latent, and a late block has few
  layers after it to amplify its change. Predicts that no weight statistic explains
  `stability_b` once depth is accounted for.
- **H_struct (alternative):** stable blocks are built differently.

Depth is removed by regressing both `stability_b` and each statistic on
(b, b²) and taking residuals. Test: Spearman ρ between residuals, n = 28.
Threshold for 34 tests (Bonferroni, two-sided α = 0.05 → p < 0.0015): **|ρ| ≥ 0.57**.

- **H_struct supported** if at least one statistic reaches |ρ| ≥ 0.57 on residuals.
- **H_depth supported** if none reaches 0.57 **and** none reaches 0.40.
- Between 0.40 and 0.57 for the best statistic: inconclusive; reported as such.

Secondary, descriptive, not tested: raw (not residualised) correlations; whether blk23
stands out from blocks 18–27 by more than 2 SD on any statistic.

## Known limit, stated now

Weights alone ignore the size of the residual stream at each depth, which in
transformers usually grows with depth. A null here does not prove H_depth; the direct
test is the norm of each block's write relative to the stream, which needs a forward
pass on Alessandro's GPU (proposed, not scheduled).

## Implementation

`experiments/block_weight_structure.py` (read-only; parses the safetensors header,
reads BF16 as uint16 → float32, no torch). Output `data/block_weight_structure.csv`
and `data/block_weight_structure_test.csv`.
