# C56 result — the push that completes the hood: 0.02 pushed negative, more or never pushed positive

2026-10-06. Pre-registration `docs/prereg_hood_threshold.md`; renders
`docs/RENDERS_2026-10-06_hood_threshold.md` (REPRO PASS, 41 of 41, 40 tuner patches logged). Labels:
Alessandro, blind (`data/hood_threshold_labels_alessandro.csv`, deposited before the tally); tally
`data/hood_threshold_tally.csv`.

**Reliability.** Self-agreement 7 of 8 repeats (threshold 7): usable. The one disagreement is blk10
+0.08 (*abbassato*, then *a metà*); the first label is used.

| block (band) | sign | 0.01 | 0.02 | 0.04 | 0.08 | 0.16 | threshold |
|---|---|---|---|---|---|---|---|
| blk10 (Style) | − | half | complete | complete | complete | complete | 0.02 |
| blk10 (Style) | + | half | half | lowered | lowered | complete | 0.04 |
| blk00 (Base) | − | half | complete | complete | complete | complete | 0.02 |
| blk00 (Base) | + | half | half | half | complete | complete | 0.08 |
| blk20 (Details) | − | half | complete | complete | complete | complete | 0.02 |
| blk20 (Details) | + | half | half | half | half | half | none within 0.16 |
| blk23 (Correction) | − | half | half | half | complete | complete | 0.08 |
| blk23 (Correction) | + | half | half | half | lowered | lowered | 0.08 |

* **Every response is a step.** Once the hood leaves the half-formed state it never returns to it
  higher up the ladder. 0.01 changes nothing on any block (like one bf16 step in C55).
* **The expectation holds in sign, weakly.** Spearman between threshold and the block's content
  change at equal dose: **−0.60** (8 points, one seed; no significance claimed). The block that
  changes content least, blk23, needs the largest push in both directions.
* **The sign matters more than the block.** Pushed negative, three of four blocks complete the hood
  at 0.02 — including blk20, which changes content little. Pushed positive, thresholds are higher
  (0.04 to none within 0.16), and two of four lower the hood instead of completing it. This matches
  block 27 in C54 (+0.05 still half, −0.075 complete). Whether "negative completes, positive lowers"
  is a property of this ridge or of the blocks cannot be told from one seed.

**What it adds to page 22.** A watershed is not tipped by any perturbation whatever: there is a
threshold, between 0.01 and 0.02 at best, and it depends on the block and, more, on the direction of
the push. Which way the picture falls also depends on the direction.
