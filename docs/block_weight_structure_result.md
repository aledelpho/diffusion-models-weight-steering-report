# C46 result — the stable / unstable split is visible in the weights

2026-10-04. Pre-registration: `prereg_block_weight_structure.md` (commit ec03c89,
before any weight was read). Code: `experiments/block_weight_structure.py`.
Data: `data/block_weight_structure.csv` (28 blocks × 40 values),
`data/block_weight_structure_test.csv`.

## 1. Verdict by the pre-registered rule: H_struct supported — my prediction failed

Best Spearman ρ between a weight statistic and layout stability, depth removed
(quadratic in block index from both): **0.615** (`mlp.down.sigma1`, −0.615). Three of
34 statistics pass the Bonferroni threshold 0.57:

| statistic | ρ raw | ρ depth removed |
|---|---|---|
| `mlp.down.sigma1` | −0.413 | **−0.615** |
| `mlp.gate.stable_rank` | +0.528 | **+0.613** |
| `mlp.down.stable_rank` | −0.361 | **+0.585** |
| `attn.wo.stable_rank` | −0.588 | +0.566 |
| `mlp_write_proxy` | −0.810 | −0.528 |

H_depth — Claude's prediction that position alone explains stability — is **refuted by
the rule it was registered with**.

Robustness (not pre-registered): leave-one-block-out keeps |ρ| between 0.50 and 0.70
for the three passing statistics, so dropping a single block can take any of them
below 0.57. The verdict is real but marginal. Power iteration converged: 50 and 300
steps agree to four decimals on the four tensors checked.

## 2. What the numbers show, block by block

- **Blocks 08–09, the least stable (layout r 0.57–0.67), have the strongest single
  direction in their MLP gate in the whole stack.** σ₁(`mlp.gate`) 113 and 130 against
  34–97 elsewhere, and the lowest gate stable rank among the middle blocks (20 and
  15.5 against 25–74). These are the blocks that, by eye, change viewpoint, identity
  and medium (`block_groups_and_prompt_order.md` §1). Raw correlation of σ₁(`mlp.gate`)
  with stability over 28 blocks: −0.82.
- **Blocks 26–27 write through almost a single direction.** Stable rank of `attn.wo`
  26 and 13 (other blocks 100–260), of `mlp.down` 90 and 17.5 (others 140–400). A block
  whose output projection is close to rank one can push the image along very few
  directions, which is one mechanical reading of "a knob". Block 00 shares part of
  this (gate stable rank 8.2, the lowest of all).
- **blk23 does not stand out** from blocks 18–27 by more than 2 SD on any of the 40
  values. Its colour specificity is not visible as an anomaly in these statistics.

## 3. Limits

- n = 28, one checkpoint, correlational. A weight statistic that tracks stability is
  not shown to cause it.
- The quadratic depth model absorbs the U shape; after removal the correlations are
  driven by the middle (blocks 08–10 most of all). Signs can therefore flip between the
  raw and the residual column (`mlp.down.stable_rank`: −0.36 raw, +0.59 residual), and
  the residual column must not be read as "higher rank = more stable" across the
  whole stack.
- The residual-stream size per depth is still unmeasured. The direct test is the norm
  of each block's write relative to the stream (forward pass, Alessandro's GPU).

## 4. What follows

A testable consequence, stated before any render: if a block's leverage on the
picture runs through its dominant MLP-gate direction, then scaling **only `mlp.gate`**
of blk09 should reproduce a large part of the blk09 change, and scaling only
`attn.wo` of blk27 should reproduce most of the blk27 change. Both are cheap per-tensor
presets; whether to render them is Alessandro's decision.
