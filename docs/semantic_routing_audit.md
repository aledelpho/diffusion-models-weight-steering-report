# Audit of `docs/semantic_routing_analysis.md` (untracked, not published)

2026-10-04. The document and its scripts (`experiments/analyze_vector_coherence_aggregated.py`,
`export_final_csv.py`, `data/krea2_unet_semantic_routing_full*.csv`) appeared in the
working tree between 2026-10-02 and 2026-10-03, written by another assistant. They are
not committed. This note says what in them holds and what does not; whether the
document is kept, rewritten or dropped is Alessandro's decision.

## What the document claims

"Delta_Crollo" = mean pairwise cosine between CLIP (ViT-B/32) embedding changes of one
arm across the prompt-order images (called "same prompt", N = 10) minus the same on
26 images from v3, v4, styles and the atlas ("different prompts"). A large positive
delta is read as a **semantic router**, a delta near zero as a **structural filter**;
16 of 56 arms are said to survive Bonferroni; the conclusion recommends restricting
"semantic weight surgery" to those arms and "structural" edits to blk00.

## Defects

1. **No file computes the p-values.** No script in the repository runs a test or a
   Bonferroni correction; the p-values, the "31/56" and the "16/56" cannot be
   reproduced. The text names 7 survivors, then 5 more, i.e. 12, not 16.
2. **Dose is not part of the key.** Arms are keyed as `blk19_pos`, with no dose. The
   "same prompt" set is at 0.35 for most blocks (blk26 pos 0.20); the "different
   prompts" set mixes the styles doses (blk19 pos 0.25, blk26 pos 0.15), v3/v4 doses
   and the atlas (0.35). Where a prompt has two doses of one arm (v3/v4 blk23 pos at
   0.15 and 0.30) the dictionary keeps whichever file is read last and drops the
   other without warning: N = 26 for blk23 pos is 12 + 6 + 5 + 3, one dose per prompt.
3. **The delta measures how alike the images are, not routing.** All ten "same prompt"
   images show the same character; the 26 others show 26 different scenes. A fixed
   operation (desaturate 20 %) moves a CLIP embedding in a direction that depends on
   the content — the document says so itself in its "lk23 paradox" and treats it as an
   exception. It is the general case: every arm with a visible effect is expected to
   show a positive delta, so the measure cannot separate "semantic" from "structural".
4. **The eye contradicts the ranking.** The #2 "semantic router", blk26 pos, at 0.20 on
   the prompt-order images lays a mosaic of 10–20 px colour cells over the whole frame,
   white background included, in 10 of 10 renders (1:1 crops,
   `block_groups_and_prompt_order.md` §4). That is the least semantic effect in the
   set — the same artefact on any content — and it is at a dose above the 0.15 cap
   Alessandro set for this block. Its "same prompt" coherence is high because the
   artefact is identical on ten near-identical images.
5. **Failing to reject is not evidence of zero.** "lk00 fails Bonferroni, which
   reinforces the thesis that it is purely structural" inverts the logic; and the
   quoted p = 0.0029 is evidence *against* a zero delta at any conventional uncorrected
   level.
6. **Pairwise similarities are not independent.** 10 vectors give 45 pairwise cosines;
   a test that treats them as N = 10 or N = 45 independent values is mis-sized either
   way.
7. **Architecture.** Krea-2 is a 28-block diffusion transformer, not a U-Net; "lk00…lk27"
   are not the repository's block names.
8. **An operating recommendation from a statistic alone** ("operators should restrict
   interventions to…"), the error recorded as pitfall 90.

## What survives

The **same-prompt column on its own** is useful and agrees with the layout-free
measure in `block_groups_and_prompt_order.md` §3b: for a fixed content, most arms move
the CLIP embedding the same way whatever the word order. The **different-prompts
column on its own** is also informative: the arms whose CLIP direction is most stable
across 26 different scenes are blk27 pos (0.27), blk00 neg (0.21), blk26 pos (0.17),
blk27 neg (0.16) — grain, blur and texture, the most content-independent effects by
eye. Their difference, read as "semantic routing", is what does not hold.
