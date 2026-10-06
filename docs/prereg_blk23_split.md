# C58 — block 23 split in two: does the MLP carry the noise and the attention the colour?

2026-10-06. Written before any render or measure of the split arms. Renders authorised by Alessandro
on 2026-10-06.

## Thesis (Alessandro)

In the images he recognised as block 23, the noise comes from the block's MLP; the colour change comes
from its attention. From his exploration inside block 23 (`docs/inside_block23_exploration.md`) and
the architecture: a whole-block edit ×(1+d) changes only the eight matrices (norms and modulation never
reach the model), so it splits exactly into an **attention part** (wq, wk, wv, gate, wo) and an **MLP
part** (gate, up, down).

## Material

The C47 bench (`benchmark_blk23_colorful`): 8 prompts × 2 seeds = 16 cells, with the baseline (B) and
the whole block (W) already rendered at **−0.45** (more colour) and **+0.30** (less colour). New, in
`benchmark_blk23_split`, same prompts, seeds and settings, through the tuner's `granular_json` (Real
Value, each listed matrix ×(1+d), nothing else):

* **A** — attention only: `blocks.23.attn.{wq,wk,wv,gate,wo}.weight`
* **M** — MLP only: `blocks.23.mlp.{gate,up,down}.weight`

2 arms × 2 doses × 16 cells = 64 renders, plus three checks first:
* **REPRO:** W at −0.45 on `E1_cartoon` seed 2718281, re-rendered through the vector path, must equal
  the C47 file pixel for pixel.
* **SPLIT = WHOLE:** all eight matrices through `granular_json` (A and M together) at −0.45 and +0.30
  on the same cell must equal W pixel for pixel. This checks that the granular path patches exactly
  what the block vector patches, and that nothing outside the eight matrices matters. If either check
  fails, the bench stops.

## Measures (fixed now; computed only after the eye pass is deposited)

Per image, against the baseline of its cell:
* **ΔN — noise:** Immerkær's fast noise estimate (σ from the 3×3 Laplacian-difference mask, 1996) on the
  luminance at full resolution, minus the baseline's. Higher = more fine-grained high-frequency noise.
* **ΔC — colour:** change of mean chroma, CIELAB at 64×80 (the C47 metric).
* layout r (C47), and the edge-energy ratio used on Alessandro's exploration — descriptive.

## Gate, per dose

The thesis needs noise to attribute: **W adds noise (ΔN_W > 0) in at least 10 of 16 cells.** If not,
the noise hypotheses (H1, H2, H4) are void at that dose and reported as such.

## Hypotheses (decisive; −0.45 is the primary dose, +0.30 is reported the same way)

* **H1 — the MLP carries the noise:** ΔN_M > ΔN_A in at least 12 of 16 cells.
* **H2 — the MLP accounts for the whole block's noise:** |ΔN_M − ΔN_W| < |ΔN_A − ΔN_W| in at least 12
  of 16 cells.
* **H3 — the attention carries the colour:** ΔC_A has the sign of ΔC_W and |ΔC_A| > |ΔC_M| in at least
  12 of 16 cells.
* **H4 — a cleaner colour knob:** ΔN_A < ΔN_W and ΔC_A has the sign of ΔC_W, in at least 12 of 16 cells.

**The thesis holds** at a dose if H1 and H3 hold there; it is **refuted** at a dose if H1 fails with
ΔN_A ≥ ΔN_M in at least 12 of 16 cells, or H3 fails with |ΔC_M| ≥ |ΔC_A| in at least 12 of 16. Anything
else: not decided. (12 of 16 is p = 0.038 one-sided under a fair coin.)

## Eye pass, before the numbers

Alessandro, blind: for each cell and dose, the four images B, W, A, M in random positions on one sheet
(32 sheets, 4 shown twice), two questions — "which has the most noise / grain?" and "which has the most
saturated colours?". Deposited before `--measure` runs; reported beside the numbers, not decisive.
He has seen B and W before; A and M are new to him.

Code: `experiments/blk23_split.py`.
