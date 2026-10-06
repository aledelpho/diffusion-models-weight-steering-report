# C59 — the split atlas: every block's attention and MLP, apart, in both directions

2026-10-06. Exploratory atlas, asked for by Alessandro. Written before any render; renders authorised
by Alessandro on 2026-10-06.

## Why

On block 23 (C58) the two halves of a block did different things: the MLP carried the texture (it
smooths when pushed up, etches when pushed down) and most of the fine-texture cost that notebook page
05 treated as unavoidable; the attention carried a desaturation with much less of that cost; the
colour was split between the two. One block. The atlas asks where this holds across the stack.

## Design

* **Prompts and seeds:** the three prompts of the equal-dose atlas (`P01_blacksmith`, `F4_closeup`,
  `S1_rally`) at its seed 2718281 — where every whole block at ±0.35 already exists — plus seeds
  3141592 and 4669201 (new baselines rendered here).
* **Edits:** for each of the 28 blocks, the attention matrices alone (wq, wk, wv, gate, wo) and the MLP
  matrices alone (gate, up, down), at **+0.35 and −0.35** (Real Value, through `granular_json`): 28 × 2 ×
  2 × 3 prompts × 3 seeds = 1008 renders, plus 6 baselines and 2 checks = 1016. The equal dose matches
  the existing atlas and the sensitivity map (page 21), and is symmetric, so page 05's common mode is
  exact.
* **Checks first:** the atlas baseline re-rendered must be identical to the pixel; block 9 at +0.35 with
  all eight matrices through `granular_json` must be identical to the atlas's whole block 9. If either
  fails, nothing else runs.
* **Order:** seed 2718281 first, so that a short night still leaves a complete atlas at the seed where
  the whole blocks exist.

## Measures (fixed now)

Per render against its baseline: fine texture HF = std(gray − GaussianBlur(σ = 1.5)) (page 05), mean
chroma change and layout r (C47 metric). Per block, part and cell: r⁺, r⁻, **common mode √(r⁺ r⁻)** (the
texture cost) and swing r⁺/r⁻ (the texture steering). At seed 2718281 the whole block is measured the
same way, from the equal-dose atlas.

## What I expect, written before (descriptive, no thresholds)

* **E1:** in most blocks the texture cost (common mode below 1) sits more in the MLP than in the
  attention.
* **E2:** whole block ≈ attention + MLP holds for colour and texture where both halves are small, and
  breaks where both are large (the confetti of block 23 at +1.0).
* No expectation about which half rewrites the content (layout r) in the middle of the stack: that is
  what the atlas is for.

Eye: contact sheets per block, after the measures, for Alessandro to read; no blind pass planned for an
exploratory atlas.

Code: `experiments/split_atlas.py`. Directive: `docs/directives_antigravity_split_atlas.md`.
