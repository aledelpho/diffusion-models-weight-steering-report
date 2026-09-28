# Amendment 02 to `docs/prereg_groove_or_hole.md`: Alessandro's prediction, made measurable

- **Written:** 2026-09-28, after Alessandro's prediction (§7) was deposited and **before** the script
  was run with `--run`. No `Δout`, `V` or group comparison had been computed.
- **Status:** the operational reading below is the analyst's. Alessandro had not reviewed it before
  the run. If he disagrees with it, the disagreement is recorded here as amendment 03, and it cannot
  change a number, because every quantity below is read from tables the run writes anyway.

---

## 1. What the prediction claims, and what it does not

The prediction does **not** claim a groove in the sense of §1 (moving toward the base model's
repertoire). It claims a **position effect**, in four parts:

| | claim | testable here? |
|---|---|---|
| **A1** | the first and last blocks create artefacts: grain, loose or out-of-focus pixels | yes, as loss of line coherence |
| **A2** | the central blocks move the image much more and find different styles or representations | yes, as visibility, and as visible changes that keep the line |
| **A3** | on a non-linear scale, but coherent across seeds | partly: seed agreement only |
| **A4** | calibrating on one prompt family probably spoils others | **no**: benches M and D hold two comic prompts |

## 2. Position classes

These follow the tuner's own groups (`0-4 | 5-9 | 10-14 | 15-19 | 20-23 | 24-27`):

- **Bench M.** Ends = `Block_1`, `Block_6`. Centre = `Block_2` to `Block_5`.
- **Bench D.** Ends = `blk00`–`blk04` and `blk24`–`blk27`, i.e. the members of `Block_1` and
  `Block_6`. Centre = `blk05`–`blk23`.
- **Bench K** (`blk16` only) and **bench Q** (bands b1 and b6 only) have no end/centre contrast
  and are not used for A1–A3.

The unit is the row of `data/groove_by_condition.csv`: (unit, sign, dose, prompt), with its `V`, its
`L` and its three seeds.

## 3. The operational predictions, frozen

Each is computed separately in M (all doses pooled, except A2a) and in D. Each is reported with
its two shares or medians. These are **descriptive** comparisons on two prompts: no p-value is
attached and none is claimed.

- **A1, the ends break the line.** Among all units, the share with `L < 0.98` is **higher at the
  ends than in the centre**.
- **A2a, the centre moves more.** The median `V` of the centre is **higher than** that of the ends:
  in M at **at least 4 of the 6 doses**, and in D at 0.200.
- **A2b, the centre finds usable changes.** The share of units with `V ≥ 1` **and** `L ≥ 0.98` is
  **higher in the centre than at the ends**.
- **A3, coherent across seeds.** Among central units with `V ≥ 1`, the share whose three seeds
  agree on the sign of `Δout` (0 of 3 or 3 of 3 negative) is **at least 2/3**.

**Verdict per claim:**
- **supported** if it holds in both M and D;
- **partial** if it holds in one;
- **not supported** if it holds in neither.

A4 is recorded as **untested**.

## 4. What is already known and bears on this

Stated so that nobody mistakes a replication for a discovery:

- **The displacement literature of this project points the other way on A2a.** The last group moves
  the picture most: 3.7× in the pilot (page 04). On clean rotations `Block_6` moves most, `Block_1`
  second, and the middle groups least (page 10). `V` is a new measure, but it is built from the same
  displacement, so the analyst expects **A2a not supported**.
- **Part of A1 is already visible in published coherence.** At 0.200, `Block_6` in both signs and
  `Block_5 pos` lose the line, and `Block_1` does not (`retro_mappa_reading_result.md`). `Block_5`
  is a centre group, so the analyst expects **A1 partial at most**.
- **A3's proxy is weak.** Agreement on the sign of `Δout` is not agreement on the style. A proper
  test would use direction cosines across seeds, which this run does not store. `02-attribute-emergence`
  already reports that every arm moves all five seeds together, the random ones included.

## 5. Implementation

`experiments/groove_position_readout.py` reads `data/groove_by_condition.csv` after `--run` and writes
`data/groove_position_tests.csv`. It is committed with this amendment, before `--run`.
