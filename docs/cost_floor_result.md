# C61 — does every push cost fine texture? Result

2026-10-08. Pre-registration `docs/prereg_cost_floor.md` (+ amendment 1, written with 18 of 913 renders done and
nothing measured). Renders: 913 of 913, check identical to the pixel to page 05's own render
(`docs/RENDERS_2026-10-08_cost_floor.md`; the queue stopped overnight at 796 and was resumed). Code:
`experiments/cost_floor_test.py --measure --verdicts`. Data: `data/cost_floor_measures.csv`,
`data/cost_floor_cells_G1.csv`, `data/cost_floor_per_block.csv`.

## Verdicts, applied as written

| rule | value | verdict |
|---|---|---|
| **Gate**: blocks 23–27, mean G₂ < 0.97 and one-sided p < 0.05 | G₂ = 0.989, p = 0.26 | **FAIL** |
| **H1** all 16 cells, blocks 1–22 | G₁ = 0.996; 90% [0.984, 1.009]; 95% [0.981, 1.011] | **undecided** |
| H1 comic (P01, P02; 8 cells) | G₁ = 0.989; 95% [0.980, 0.997] | **cost replicated** |
| H1 photo (S1_rally, P4_selfie; 8 cells) | G₁ = 1.003; 95% [0.971, 1.036] | undecided |
| comic − photo, mean log G₁ | −0.015, Welch p = 0.33 | no difference shown |

The gate failed, so by the pre-registered rule H1 is not readable and **nothing is overturned**. H1 would have
been undecided anyway: the cell-to-cell spread of log G₁ (0.028) left a 90% interval 2.5% wide, wider than the
±1% band. The eye test was required only for an overturn, which is no longer possible.

## Why the gate failed (descriptive)

On the comic prompts the late-block cost is there exactly as page 05 found it: G₂ = 0.934 (page 05: 0.932).
On the photographic prompts it is not: G₂ = 1.048. The difference comes mostly from block 27 pushed positive,
which on photographs raises fine-texture energy by a median 62% (r⁺ 1.62, c 1.27), against 1.09 on comics;
blocks 23–26 alone give 0.939 on comics and 0.993 on photographs. Page 05's HF reads texture *loss* as cost; on
a photograph a late push adds high frequency instead, and the measure counts it as a gain. Whether that gain
is visible noise was not measured (no eye test). Including block 27 in the gate, a block page 05 itself called
"an outlier on every axis", was a design weakness of this pre-registration, not a finding.

## What this changes

* **Page 05 holds on its own ground.** On P01 and P02 with four new seeds, blocks 1–22 cost 1.1% (G₁ 0.989,
  page 05: 0.989) and blocks 23–27 6.6% (0.934 vs 0.932). That is a clean replication of both numbers.
* **The "any" is not established beyond comics.** On photographs the same measure is too noisy to decide for
  blocks 1–22 and flips sign at the tail. Page 05's claim rests on two comic prompts and its wording ("any
  block") is broader than its evidence; this test neither confirms nor overturns the broader reading.
* No status change proposed. If wanted, a note on page 05: replicated on new seeds for its two prompts;
  untested in general, with the photographic tail behaving differently on the same measure.
* Per block (descriptive, 16 cells): only blocks 9, 18, 19 and 23–25 have a 95% interval wholly below 1;
  blocks 20 and 21 wholly above.
