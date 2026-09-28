# `Block_4` and `Block_6`: what the whole line of work produced

**Date**: 2026-09-28 · **Question**: Alessandro — did anything interesting come out of the
`Block_4` / `Block_6` game? · **Sources**: `internal_fights_by_group.md`,
`rectified_mask_result.md`, `style_damage_frontier.md`, `colour_gate_and_chroma_audit.md`,
`leaf_collapse_and_blk16_result.md`, and the data files they cite. **No new render, no new
measurement — this is an accounting.**

---

## 1. The ledger first, because most of it failed

| what was tried | outcome |
|---|---|
| find the internal fights | **held** — `Block_4` opposed on contrast in both arms, `Block_6` opposed on grain |
| rectify the fighting signs into a better slider | **unreadable** — M4 missed by 0.31 *and by direction*, so M5, the experiment, means nothing |
| show the mask beats its group | **half** — on contrast yes (+0.113), on grain the arithmetic failed first |
| show the two masks are independent axes (M6) | **grey** |
| rank the corpus by style against damage | **retracted** — the two axes correlated r = +0.798 |
| declare the top of that ranking the best operating points | **wrong, and by the largest possible margin** |

**The experiment the whole line was designed around did not produce its answer.** That has to be
said first, because what follows was not the plan.

## 2. What came out instead: they are two different kinds of operator

Everything since has pointed the same way, from three measurements that were built for other
purposes.

**(a) Composition.** How far the joint effect of two sub-blocks departs from the product of their
single effects, mean over the eight cells of each family (`data/rectified_mask_verdict.csv`):

| family | mean \|deviation\| | worst |
|---|--:|--:|
| `Block_4` only | **0.064** | 0.120 |
| `Block_6` only | **0.168** | 0.357 |
| combined | 0.170 | 0.398 |

**`Block_6`'s sub-blocks are 2.6× less predictable from their parts than `Block_4`'s.** M4 — the
prediction that killed the bench — is a `Block_6` condition, and the four largest deviations in the
table are all conditions containing `Block_6` at concordant signs.

**(b) Structure.** Coherence of the drawn line, ratio to baseline, over every condition of each
family at dose 0.200 (`data/texture_anisotropy.csv`, 80 conditions in all):

| family | n | mean | worst | best | above 1 |
|---|--:|--:|--:|--:|--:|
| `Block_4` | 16 | **1.0019** | blk19 pos 0.966 | B4_mask pos **1.041** | 7/16 |
| `Block_6` | 14 | **0.9148** | B6_mask neg **0.729** | blk26 neg 1.020 | 3/14 |

Three of the five best conditions in the corpus are `Block_4` family (`B4_mask pos` 1st,
`blk16 pos` 3rd, `blk15 pos` 5th). Four of the five worst are `Block_6` family. **The `Block_4`
family never drops below 0.966; the `Block_6` family reaches 0.729.**

**(c) Colour.** `Block_6` is an antisymmetric chroma knob — pos ×0.726, neg ×1.815, **18/18 cells**,
p = 1e-5. `Block_4` is weakly so, ×1.193 / ×0.927, 14/18, p = 0.031. And `Block_4 neg` is the edit
that removes a leaf's colour entirely in 9 seeds out of 20 while leaving the drawing intact
(IoU 0.877 against 0.895 for the seeds that keep their colour).

**Read together:** `Block_6` moves *how the picture is rendered* — tone, chroma, grain — powerfully,
antisymmetrically, and at the cost of the drawing. `Block_4` moves *what is drawn* — it keeps or
strengthens the line, its parts add up, and its failures are strange and specific rather than
general degradation. That is not a difference of degree along one axis. It is two mechanisms.

## 3. The single most useful thing it produced was not a mask

**`blk16`.** One slot in a 34-slot vector, inside `Block_4`. Across the dose ladder
(`data/blk16_ladder_cells.csv`):

| dose | 0.020 | 0.035 | 0.050 | 0.080 | 0.120 | 0.200 |
|---|--:|--:|--:|--:|--:|--:|
| style | 0.045 | 0.066 | 0.095 | 0.138 | 0.194 | **0.447** |
| coherence | 0.994 | 1.001 | 0.999 | 1.004 | 1.017 | **1.040** |

**Style multiplies by ten while the drawn line gets stronger, monotonically, 6/6 cells at the top
two doses.** It is the only edit measured in this project that buys both. And it was found only
because the mask corpus existed and forced a quality axis into being.

## 4. The trap in the same material

**`blk27`** was nominated three separate times — by Punto 7 §3 on swing, by
`internal_fights_by_group.md` as the one member that reverses its own group on grain, and by the
first version of the style/damage frontier as the best point among all 28 single blocks. It ranks
**75th of 80** on line preservation.

Every one of those three nominations came from a *displacement* statistic: how much the image moved.
None of them could distinguish moving toward something from falling apart. **Three independent
statistics agreeing is not corroboration when all three measure the same thing.** That is the
methodological lesson of the whole line, and it cost a wrong recommendation that only an observer
looking at a crop at 100 % caught.

## 5. What this does not say

* The mask idea is **not refuted**, it is untested: its arithmetic prerequisite failed on
  `Block_6`. A mask built on directly measured joint effects (register **C14**) is still open.
* "Two mechanisms" is a reading of three measurements, none of them pre-registered for this
  question. It predicts things — `Block_4` sub-blocks should keep composing where `Block_6`'s do
  not, at doses and on prompts not yet tried — and that is how it should be tested.
* Coherence is one number on one drawing style. A comic-line baseline is the case where it should
  work best. Until **C20** checks it on a photographic family, every structural claim here inherits
  that caveat.
* All of §2(b) and §3 rest on two prompts and three seeds.
