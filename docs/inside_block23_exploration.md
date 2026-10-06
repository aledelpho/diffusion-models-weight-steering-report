# Inside block 23 — Alessandro's exploration and what the architecture says (2026-10-06)

Exploratory; Alessandro's own renders made in ComfyUI with the Model Sub-Block Tuner
(`Text2Img\Esperimenti`, 16 files, settings read from the workflow saved in each PNG). Dragonborn
(`R6_dragonborn_cleric`), seed 2645751, the C52 settings; compared with the phase C baseline at the
same seed. Not a bench, not pre-registered; numbers are descriptive. Doses are Sub-Block Tuner
"Real Value" deltas: +1.0 means ×2, −1.0 means ×0.

## His finding

* The MLP of block 23 is what degrades the picture; the attention value and output projections are
  what desaturate it; and `ATTN_wv_value` and `ATTN_wo_out` seem interchangeable.

## Measured on his 16 files (against the baseline: mean chroma change at 64×80, layout r, edge energy ratio)

| file | edit inside block 23 | chroma | layout r | edges |
|---|---|---|---|---|
| 00016 | wv ×2, wo ×3 | −3.0 | 0.76 | ×1.15 |
| 00029 | wo ×4 | −2.6 | 0.79 | ×1.11 |
| 00030 | wv ×4 | −2.6 | 0.79 | ×1.11 |
| 00025 | wv ×0, wo ×0 (attention removed) | **+3.7** | 0.81 | ×0.84 |
| 00018 | MLP up ×2 | −0.4 | 0.85 | ×0.80 |
| 00019 | MLP down ×2 | −0.4 | 0.85 | ×0.80 |
| 00017 | MLP up ×2, down ×2 | +0.1 | 0.82 | ×0.52 |
| 00021 / 00022 | MLP down ×3 / up ×3 | −0.2 | 0.80 | ×0.62 |
| 00020 | MLP down ×0 (MLP removed) | +0.5 | 0.84 | ×1.23 |
| 00023 = 00027 | MLP gate ×3 | −0.2 | 0.79 | ×0.56 |
| 00026 | MLP gate ×3, down ×3 | −1.0 | 0.70 | ×0.59 |
| 00028 | MLP up ×1.5, down ×1.5 | −0.4 | 0.84 | ×0.75 |
| 00024 | norm scales ×3 | 0.0 | **1.00** | ×1.00 — **pixel-identical to the baseline** |
| 00031 | every component ×1.35 | −2.1 | 0.82 | ×0.65 |

Pixel-identical pairs: **00029 = 00030** (wo ×4 and wv ×4), **00018 = 00019** (up ×2 and down ×2),
00023 = 00027 (same setting twice), 00024 = the baseline.

The split he saw holds in these numbers: the attention path carries the colour (more gain → less
chroma, removed → +3.7), the MLP carries detail (more gain → fewer edges, a softer picture; removed →
more edges), with little chroma change.

## Why — read from `comfy/ldm/krea2/model.py`

```
Attention:  q, k, v, gate = wq(x), wk(x), wv(x), gate(x)
            q, k = qknorm(q, k)                      # RMSNorm per head
            out = attention(q, k, v)                 # linear in v
            return wo(out * sigmoid(gate))
SwiGLU:     return down(silu(gate(x)) * up(x))
RMSNorm:    weight = scale + 1                       # the stored scale is zero-centred
Block:      x += pregate * attn((1+prescale) * prenorm(x) + preshift)
            x += postgate * mlp((1+postscale) * postnorm(x) + postshift)
```

* **wv and wo are one knob.** The attention output is linear in v, so scaling wv by s or wo by s
  multiplies the block's attention contribution by s either way; only their product matters. At ×4 the
  two renders are identical to the pixel because 4 is a power of two and the bf16 rounding is exact; at
  a factor such as ×3 they should differ only by rounding.
* **up and down are one knob** for the same reason (the MLP output is linear in up(x)); identical at
  ×2. The MLP gate is different: it goes through SiLU.
* **wq and wk should be dead knobs.** q and k are normalised (QK-norm) right after the projection, so
  scaling wq or wk by s is cancelled, up to rounding. Not yet tested.
* **The attention gate is a separate, non-linear knob** (through a sigmoid).
* **Norm scales, QK-norm scales and the modulation vectors never reach the model** — already found
  empirically in notebook page 13 ("three kinds of parameter are unreachable", 6 pairs of 6 identical,
  any dose), and seen again here (00024) and in C55 N2. A likely mechanism, not yet verified: these
  are float32 parameters of plain modules (`RMSNorm.scale`, `DoubleSharedModulation.lin`), which
  ComfyUI's `ModelPatcher.load` patches only for modules it loads completely; when the 26 GB model is
  loaded partially they are skipped silently. To check: whether `comfyui.log` says "loaded partially".

**So a whole-block edit ×(1+d) reduces to four effective knobs:** attention gain (1+d)², MLP gain
(1+d)², the attention gate and the MLP gate; wq, wk and every norm do nothing. Block 23 pushed
negative (more colour) cuts the attention gain — which is where the colour is — and the MLP gain at
the same time, which is where the detail is.

## Correction to C55

`docs/null_patch_result.md` read N2 (block 27 at +0.0001, float32 scales only) as "likely below the
precision at which they are used". The better reading: those parameters never reach the model at all
(page 13). Corrected there.

## What would make this a result (not run; renders need Alessandro's authorisation)

1. **Predictions, cheap:** wq ×3 and wk ×3 on block 23 → identical, or nearly, to the baseline;
   wv ×3 against wo ×3 → nearly identical. 3 renders.
2. **A cleaner saturation knob?** On the C47 bench (8 prompts × 2 seeds), block 23's attention gain
   alone (wo only) against the whole block, at matched chroma: does it change colour with less noise
   and less change to the rest? Pre-registered like C47/C53.
