# Pre-registration MOSS3b — confirming the MOSS atlas at 50 steps, and three follow-ups

Written 2026-10-26 by Claude, **before any render.** Alessandro: three hours of renders available, confirmations at 50
steps plus further tests. Script `experiments/moss_atlas2.py`, plan `data/moss_atlas2_plan.csv` (160 renders: 16 at R50,
about 45 min; 144 at T10, about 55 min).

## A — confirmation at R50 (blacksmith, seed 2718281)

The plain picture and the 12 cells drawn in MOSS3 before any render (seed 31337): te22 attn +1, dit21 MLP −1, dit38 MLP
+1, dit07 attn +1, dit26 attn +1, dit23 attn +1, dit40 attn −1, dit13 MLP +1, te29 MLP +1, te12 MLP −1, te00 MLP +1, te00
attn −1. **Rule (MOSS2 protocol):** blind page after the renders, each card the T10 and the R50 pair of one cell (matched)
or of two different cells (control, fixed rotation), random order, repeats; "same kind of change?" scored 1 / 0.5 / 0.
Confirmed as a whole if matched ≥ 0.67 and control ≤ 0.33; a cell is confirmed at ≥ 0.5. Cells where neither setting
changes the picture visibly are reported as such ("non si vede").

**A′ — targeted (reported, not in the rule):** three findings named after looking at the sheets, so not a fair sample:
te00 attn +2 (comic-cover grid), dit24 MLP +2 (another person), dit32 attn −1 (breakage). Also reported: the R50 plain
against the T10 plain (does 50 steps draw the "Western comics style" the turbo ignored?).

## B — text-encoder stacks (T10, three atlas prompts)

All TE layers 1–31 edited together: MLP +1, MLP +0.5, MLP −0.5, attention +1. **Rule:** a stack is *additive* if its
median DINOv2 distance is at least 3 times the median of single TE MLP +1 edits (MOSS3). Tests whether MOSS's text
encoder is robust layer by layer only, or as a whole.

## C — the DiT's text embedder (T10, three prompts; reported)

The two `text_embedder` blocks that refine the text inside the DiT: attention output (`proj`, weight only, bias kept) and
`ffn_down`, at +1, +2, −1. Reported: their median distance against the median of all DiT block edits. A sensitive embedder
would be where MOSS's text side can be steered.

## D, E — second seed (T10, blacksmith at 3141592)

DiT MLP +2 at all 42 blocks, TE attention removed at all 32 layers, DiT MLP removed at blocks 0, 4, …, 24 and 28–41.
**Rule:** the depth ordering replicates if, at the new seed, |Spearman(layer, D)| ≥ 0.5 **and** Spearman with the seed-2718281
values per layer ≥ 0.5 (computed for the two full columns).

## Limits

One prompt for A; A′ chosen after looking; DINOv2 distance for B–E.
