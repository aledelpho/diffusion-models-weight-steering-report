# C59 — the split atlas: result

2026-10-07. Exploratory atlas (plan: `docs/plan_split_atlas.md`, written before the renders). Renders:
`docs/RENDERS_2026-10-07_split_atlas.md` — both checks passed to the pixel (REPRO and SPLIT = WHOLE), 1016
of 1016 present. Numbers: `data/split_atlas_measures.csv` (per render), `data/split_atlas_blocks.csv`
(per block, part and cell), `data/split_atlas_summary.csv` (medians per block and part),
`data/split_atlas_additivity.csv` (whole vs halves, seed 2718281), `data/split_atlas_band_posthoc.csv`
(a post-hoc band measure, see "The measure fails"); post-hoc code: `experiments/split_atlas_posthoc.py`. Contact sheets (not in the repo):
`Text2Img/benchmark_split_atlas/sheets/` — one sheet per prompt, seed and group of seven blocks, plus
`crop_F4_blk26_27_pos.png`, `blk00_neg_cancel.jpg`, `blk00_neg_otherseeds.jpg`.

Design reminder: 28 blocks × {attention (wq, wk, wv, gate, wo), MLP (gate, up, down)} × {+0.35, −0.35}
× 3 prompts × 3 seeds. The whole block at ±0.35 exists only at seed 2718281 (equal-dose atlas), so every
whole-vs-halves comparison rests on 3 cells per block.

What follows was described from the images first (sheets for all 9 cells at blocks 0–27 at seed
2718281; blocks 21–27 at three further cells; block 0 at all 9), then checked against the numbers. The eye
pass is mine and is not blind; nothing here is a registered verdict.

## 1. Block 0: each half alone breaks the picture; the whole block does not

At −0.35, attention alone turns every image into a posterised, saturated scene or a field of colour
blocks (rally), and the MLP alone replaces the content (a faceless figure, a giant eye, an abstract
helmet shape): 9 of 9 cells for each half, by eye. The whole block at −0.35 keeps the picture in 3 of 3
cells at seed 2718281 (layout r 0.69–0.80, against 0.05–0.35 for attention alone and 0.24–0.36 for the
MLP alone at the same cells). At +0.35 the halves are milder (median layout r 0.55 attention, 0.73 MLP)
and the whole block is 0.74.

So the two halves of block 0 compensate each other: lowering both together is far safer than lowering
one. The whole-block sensitivity map (page 21) therefore understates how sensitive block 0's parts are.
A mechanism is not tested here; one candidate is that the two outputs are large and partly opposed in
the first block, so scaling one alone breaks a balance that scaling both preserves. Limit: the whole
block exists at one seed only.

## 2. The late noise is not always the MLP's

At +0.35 (eye; 6 of the 9 cells looked at for blocks 21–27, all consistent):

* **block 26:** the coarse mottled noise comes from the **attention** (heavy in every cell looked at);
  the MLP alone is clean;
* **block 27:** the noise comes from the **MLP** (heavy); attention alone adds a light speckle;
* **whole block:** at block 26 the image dissolves into noise in all 3 cells — far worse than either
  half; at block 27 it is close to the MLP's noise or slightly worse.

C58's thesis ("the MLP carries the noise") holds on block 23 and block 27; it does not hold as a rule
across the stack: at block 26 the noise belongs to the attention. At −0.35 neither half of 26–27 is
noisy; the MLP of block 27 at −0.35 smooths and darkens (background blur on the rally).

## 3. Texture steering in blocks 20–25 sits in the MLP

On page 05's HF, the swing r⁺/r⁻ of the MLP is further from 1 than the attention's in 37 of 54 cells
across blocks 20–25 (block medians: MLP 0.65–0.99, attention 0.94–1.15). The MLP smooths when pushed up and
etches when pushed down, as on block 23 in C58. Colour does not split the same way: at block 23 the
desaturation at +0.35 is mostly the attention's (median Δchroma −2.30 attention, −0.77 MLP, −2.27 whole),
while at blocks 24–25 the MLP desaturates at + (−1.61, −0.99) and the attention adds chroma at both
signs.

## 4. Expectations written before

* **E1 (the texture cost sits more in the MLP in most blocks): not supported.** The MLP's common mode is
  below the attention's in 11 of 28 blocks (133 of 252 cells: a coin). It holds clearly in blocks 22–25 (MLP 0.89–0.96, attention 1.01–1.03); in the
  other blocks where the MLP is lower (1, 5, 9, 12, 16, 18, 20) the gap is small, and in the early and
  middle blocks neither half shows a cost (common mode ≥ 1 in most).
* **E2 (whole ≈ attention + MLP where both are small, breaks where both are large): supported in shape,
  with the measure caveat below.** The error of the multiplicative prediction for HF grows with the
  halves' size (Spearman 0.42 over 168 cell-signs); the largest errors are blocks 26, 27, 0 and 25. Colour
  adds well outside block 0 (Δchroma whole vs sum of halves: r = 0.80, slope 0.77, n = 162); block 0 is
  the exception of section 1. Layout: in 114 of 150 cell-signs of blocks 1–25 the whole block moves the
  layout more than either half alone.

## 5. The measure fails on the noise that matters

Page 05's HF (σ = 1.5) does not see the block-26 collapse: the whole block at +0.35, which by eye is
pure noise in all three cells, reads 0.93–1.29; attention alone at block 26, heavily mottled, reads
0.82–1.19. The mottling is a few tens of pixels wide and replaces fine line work, so the fine-band
measure can even go down. A post-hoc band measure (blur σ 2 − blur σ 8; not pre-registered) catches the
whole block (1.17–1.51) and the MLP of 27, but still reads 0.88 for attention 26 on the close-up. C58
showed Immerkær's σ blind to the eye's noise; this atlas shows the same for page 05's HF. Neither scalar
can stand in for the eye on this question. All texture statements above (sections 3 and 4) are about
fine texture as page 05 defines it, not about the noise the eye sees.

## What would turn this into a claim

* A blind eye pass by Alessandro on the noise per block and part (the sheets exist), which would also
  give the labels to validate a noise measure against.
* The whole block 0 at −0.35 at the two other seeds (6 renders) to see if the compensation holds there.
* For block 26, a dose ladder on attention alone to see where the noise starts.

None of these is run; renders need Alessandro's authorisation.
