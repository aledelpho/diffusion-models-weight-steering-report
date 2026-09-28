# A groove or a hole? Outcome

**Date:** 2026-09-28.
**Pre-registration:** [`prereg_groove_or_hole.md`](prereg_groove_or_hole.md), with amendments
[01](prereg_groove_or_hole_amendment_01.md) and [02](prereg_groove_or_hole_amendment_02.md).
**Script:** `experiments/groove_or_hole.py`, committed before it was run (`16a03fc`).
Alessandro's prediction was deposited at `2a4f6e4`, before `--run`.
**Material:** 1,224 cells already on disk. **No render.**
**Data:** `data/groove_guards.csv`, `groove_cells.csv`, `groove_by_condition.csv`, `groove_tests.csv`,
`groove_position_tests.csv`.

---

## 1. The guards

Every guard passed before any distance was computed:

- **G0a** reproduced the parent's stage-9 row exactly (0.530427).
- **G0b** reproduced the parent's stage-7 row exactly (0.501902, Holm 0.002441).
- **G2-cloud:** 409 of 409 cloud rows resolved to a prompt text.
- **G1:** baselines matched on prompt, seed, sampler, steps, CFG and resolution in 1,224 cells of
  1,224.
- **G3:** no edit failed to reach the model.
- **G4:** cloud coverage was sufficient for every prompt.
- **G1b:** the same extractor on both sides (worst deviation 0.0000 sd).

The measure is the parent's measure.

## 2. The registered verdict: **not supported**

| | |
|---|--:|
| visible units (`V ≥ 1`) | **84** |
| of which holes (`Δout > 0`) | **53** (63%) |
| groove candidates (screen) | **0** |
| confirmed grooves (bench Q) | **0** |

By §4.3 and amendment 01 §2c the claim is **not supported**: there is no candidate, and more than half
of the visible units move away from the base model's repertoire. As §4.3 requires, the sentence that
goes with it:

> None of these 12 group-arms, 2 `blk16` arms, 56 single-block arms or 16 projections carves a
> groove, at these doses, by this measure. This does not show that no targeted preset can.

**Most targeted edits never became visible.**
- In bench Q all 16 projections stay below `V = 1` (median V 0.26–0.59): consistent across seeds, but
  smaller than a change of seed.
- `blk16` reaches `V ≥ 1` on only one prompt of two, at every dose.
- In bench M, the median V of the central groups only passes 1 at dose 0.200.

The visibility threshold is strict. It is also exactly the obstacle Alessandro described: *"for the
changes to show, they have to be pushed hard enough"*.

**The nearest miss.** `Block_5 pos` at 0.120: all 6 cells moved toward the repertoire (P01 −0.785,
P02 −0.130), the line was kept on both prompts (L 0.987 and 1.000), and V was 2.54 on P01. On P02 V
was **0.9996**, four ten-thousandths below the bar. By the frozen rule it is not a candidate, and
Stage B is not licensed. It is recorded here because it is the obvious unit to pre-register next,
and because a threshold that decides by four ten-thousandths should be named when it does.

## 3. The predictions, scored

**Analyst (§7).**

| prediction | outcome |
|---|---|
| no groove candidates, except possibly `Block_5 neg`, `blk16 pos` or `Block_4` | **right**: none. But the nearest miss is `Block_5 pos`, not `neg` |
| in M, the hole signature (ρ > 0 and top-dose Δout > 0) in at least 9 of 12 group-arms | **wrong**: 6 of 12 |
| no confirmed groove in Q | **right**: nothing in Q is even visible |
| probability of "supported" about 0.3 | not supported |

**Alessandro (§7, operationalised in amendment 02).** Descriptive comparisons on two prompts, as
declared.

| claim | M | D | verdict |
|---|---|---|---|
| **A1**: the ends break the line (share with L < 0.98) | ends 27.1% vs centre 13.5% | 30.6% vs 19.7% | **supported** |
| **A2a**: the centre moves the image more (median V) | ends higher at **all 6** doses (0.200: 2.33 vs 1.19) | ends 0.86 vs centre 0.77 | **not supported** |
| **A2b**: the centre finds visible changes that keep the line | centre 17.7% vs ends 16.7% | 21.1% vs 16.7% | **supported, by thin margins** |
| **A3**: coherent across seeds (proxy) | 0.57 (bar 0.67) | 0.70 | **partial** |
| **A4**: calibrating on one family spoils others | — | — | **untested** |

A2a fails the way §4 of amendment 02 said it probably would. The ends move the picture more, as every
earlier displacement measurement in this project found. A2b holds in both benches, but by one point
in M and four in D. That margin should not be read as a finding.

## 4. What the table shows that nobody registered: **the ends dig holes, the centre does not**

*Post hoc. Seen only after the registered analysis above was complete. It needs its own
pre-registration before it is a result.*

Splitting the visible units by position:

| | visible | holes | toward the repertoire, line kept | mean Δout, all units |
|---|--:|--:|--:|--:|
| **M, ends** (`Block_1`, `Block_6`) | 16 | **14** | 1 | **+0.358** |
| **M, centre** (`Block_2`–`Block_5`) | 23 | 11 | **8** | **+0.028** |
| **D, ends** (`blk00`–`04`, `blk24`–`27`) | 15 | **10** | 1 | **+0.316** |
| **D, centre** (`blk05`–`23`) | 23 | 13 | **7** | **+0.077** |

In bench M, all four end group-arms show the hole signature: Δout grows with dose, and the top-dose
Δout runs from +0.75 to +1.63. Of the eight central group-arms, six do not, and four of them end
*below* zero at 0.200.

The same pattern appears in two benches built differently: groups at six doses, and single blocks at
one dose. **When the ends become visible, they almost always leave the repertoire. When the centre
becomes visible, it does so about half the time, and otherwise moves toward the repertoire while
keeping the line.**

This is closer to Alessandro's account of the ends than to his account of the centre:
- the ends are where edits turn into something the model does not do, which is consistent with A1's
  artefacts;
- the centre does not move the picture *more*, but when it moves it enough, it moves it more often
  within the range of what the model already does.

**Why this is not yet a result.**
- It was found by looking at the output of a different analysis.
- It rests on two comic prompts.
- Several central units move toward the repertoire on one prompt and away on the other: `Block_4`
  in both signs, and `Block_2 neg` at 0.200 (`data/groove_by_condition.csv`). Only `Block_5 pos` and
  `Block_3 neg` agree on both prompts.
- "Toward the repertoire" is measured against a cloud of 52 prompts. This limit was declared in §10
  of the pre-registration.

## 5. What follows

1. **Pre-register the position effect as its own hypothesis**, on new prompts. The prediction:
   visible end edits leave the repertoire, visible central edits do not, at matched V. Stage B's
   budget (96 renders, 8 new prompts) fits it with 3 central and 3 end units.
2. **`Block_5 pos` at 0.120** is the first unit to include, because it is the nearest miss.
3. **The visibility threshold decides most of this study.** A perceptual check of what `V = 1` looks
   like (G_eye on a ladder of V) would tell whether the bar is too strict or just right.
4. **A4 needs a different design:** the same unit and dose, on a prompt family other than the one it
   was calibrated on.
