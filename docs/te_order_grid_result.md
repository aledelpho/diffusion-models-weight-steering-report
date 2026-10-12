# C65 part B by eye — does the word order send the same edit to different styles? (2026-10-12, exploratory)

Amendment 3 of `docs/prereg_te_characters.md`. Alessandro scored, on the grid viewer (`grid_viewer.py --set te_order`,
not blind: edit names visible), how much each edit's picture changes from one word order to the next (1 little – 5 a
lot), with notes. Seed 3141592 only (the 1234567 grid is not scored). Labels: `data/te_order_grid_notes_alessandro.csv`; table and correlations: `experiments/te_order_grid_tally.py`.

**Reference.** The five originals themselves (no edit) score **2**: reordering alone already changes the picture
a little.

| score | edits |
|---|---|
| 2 (as the originals) | L04 MLP−, L08 MLP−, L10 attn+, L10 MLP−, L12 attn+, L15 attn+, L19 attn−, L25 MLP+ |
| 3 | L02 MLP+, L14 attn+, L20 MLP+, L26 MLP+, L28 MLP+ |
| 4 | L05 MLP+, L09 attn+, L09 MLP+, L14 MLP+, L17 MLP+ |
| 5 | L06 MLP+, L12 MLP+ |

**Reading.**

* 12 of 20 edits make the five orders differ more than the originals do; all scores of 4–5 but one (L09 attn+) are
  strong MLP+ edits. On those the notes name a different genre per order ("lady oscar", cartoon, realistic comic;
  cat-woman animation vs bright comic vs realistic comic). On this seed, the answer to Alessandro's question is
  **yes for the strong MLP+ edits, no for the mild ones**: the same words in another order are carried to another
  style. On the DiT (2026-10-04, `docs/block_groups_and_prompt_order.md`) the blocks inspected by eye did the same thing in every order (blk19 and blk26 pos 10/10, blk17 pos 5/5), and the statistics put order no above seed.
* Style and content can part ways. L05 MLP+: style "very coherent" across orders, but the number of figures goes
  from 1 to 4. L17 MLP+: a shared composition, different drawing styles. L25 MLP+: the same new extreme close-up
  in every order.
* **Eye against the 23 statistics** (part B measures, both seeds; Spearman over the 20 edits): the eye score rises
  with the size of the edit (ρ = 0.76) and, against intuition, with cos_order (ρ = 0.63) — the edits whose low-level
  statistics move the same way in every order are the ones whose genre differs most. It falls with d = cos_order −
  cos_seed (ρ = −0.47). The statistics register a shared shift (flat colours, synthesis — noted by Alessandro on
  L14 MLP+) that the genre change rides on; this is why H2 was only "inconclusive" on them.

**Limits.** One prompt, one seed scored, one observer, not blind; correlations are post hoc. Scoring the
1234567 grid would say whether the ranking repeats.
