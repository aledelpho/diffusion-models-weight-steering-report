# Dissecting Block_1 — the slider is one block with four passengers

**Date**: 2026-09-27 · **Proposal**: Alessandro — work only on `Block_1`, dissect it, cutting it
different ways (sub-block, or by tensor type inside), and expect that rectifying opposed parts would
help the target while costing more image quality, because a single slider groups far more than one
thing. **Material**: all already on disk. **No render.** Exploratory.

---

## 1. Both cuts already exist, and the tool already exposes them

`Arthemy_Krea2_Tuner.py` line 2045: **`"Block_1": ["blocks.0.", "blocks.1.", "blocks.2.",
"blocks.3.", "blocks.4."]`** — and lines 2307–2311 expose **`Block_1A` … `Block_1E`** individually.
Both cuts are controls the tool offers, so pitfall candidate 71 is satisfied.

| cut | corpus | status |
|---|---|---|
| **by depth**, `blk00` … `blk04` at ±0.200 | `benchmark_profondita` / `_neg` | rendered, 2 prompts × 3 seeds |
| **by tensor type**, `wq/wk/wv/wo` over the same band | `benchmark_qkvo_atlas` (`b1` **is** `Block_1 (All 0-4)`) | rendered, 8 scenes × 3 seeds |
| **the whole**, `Block_1` at six doses | `benchmark_mappa` | rendered |

Target property: **contrast**, because `blk00` has just been shown to be a contrast knob
(`first_block_knob_decisive_test.md`) and contrast has a clean per-image estimator that is not one
of the 23 global descriptors — which was objection 3 against the sign-mask pre-check.

## 2. Cut by depth: one block does everything

Variance ratio against the same-seed baseline, dose 0.200:

| sub-block | pos | cells > 1 | neg | cells > 1 | |
|---|--:|--:|--:|--:|---|
| **`blk00`** | **0.797** | **0/6** | **1.177** | **6/6** | unanimous, both arms |
| `blk01` | 1.000 | 3/6 | 0.980 | 2/6 | at noise |
| `blk02` | 0.981 | 2/6 | 1.004 | 4/6 | at noise |
| `blk03` | 0.954 | 1/6 | 0.987 | 1/6 | at noise |
| `blk04` | 0.984 | 3/6 | 0.975 | 1/6 | at noise |

**There is no internal fight on contrast. There is one active block and four inert ones.**

### The cancellation test

Same per-block gain in both cases, compared in logs because these are ratios:

| arm | sum of the five parts | the group | group / sum |
|---|--:|--:|--:|
| pos | 0.734 | 0.788 | **1.074** |
| neg | 1.115 | 1.104 | **0.990** |

**The parts compose additively.** Nothing is cancelling, so there is nothing for a sign mask to
rectify — on this property.

## 3. Cut by tensor type: nothing, and the reason matters

| tensor | pos | cells > 1 | neg | cells > 1 |
|---|--:|--:|--:|--:|
| `wq_b1` | 0.999 | 13/24 | 1.001 | 13/24 |
| `wk_b1` | 0.998 | 16/24 | 1.002 | 13/24 |
| `wv_b1` | 1.011 | 16/24 | 1.014 | 14/24 |
| `wo_b1` | 1.011 | 18/24 | 1.011 | 15/24 |

All four within 1.4 % of 1, every cell count a coin flip. **No attention projection in this band
moves contrast.**

Two readings, and they are not exclusive: the effect may live in tensors the q/k/v/o cut never
touched (MLP, gate, norm scales), **or** the band cut dilutes it — a `b1` preset spreads its gain
over blocks 0–4, of which §2 says four are inert. The second is sufficient on its own.

*(These four cells are not displacement-matched — 33.32 to 65.06, a factor 1.95 — so their
magnitudes are not comparable to each other. Their signs are.)*

## 4. The measurement that answers the quality question

`blk00` alone at 0.200 and the whole `Block_1` group at 0.200 produce **the same contrast shift**
(0.797 against 0.788). So they can be compared at matched effect, which is what the question needs.

Displacement in the 23-trait space, in units of seed noise:

| condition | ‖displacement‖ | per block | collateral on the other 22 traits |
|---|--:|--:|--:|
| `Block_1` (blocks 0–4) | **22.13** | 4.43 | 21.97 |
| **`blk00` alone** | **22.34** | **22.34** | 22.19 |

**Ratio 1.010.** One block reproduces the entire group — the same effect, the same collateral, at a
fifth of the weight displacement.

Two consequences, and the second is uncomfortable:

1. **The `Block_1` slider is `blk00` with four passengers.** Four fifths of its Frobenius budget
   buys nothing measurable, in contrast or in any of the 23 traits. Anyone wanting this effect
   should use `Block_1A`.
2. **Narrowing the edit did not reduce the collateral.** 22.19 against 21.97 — identical. So the
   damage is not caused by the breadth of the edit; **it is intrinsic to the block that does the
   work.** You cannot have `blk00`'s contrast without `blk00`'s collateral, and no sharper cut will
   give it to you.

That is a direct answer to the proposal's worry, and it is the pessimistic one: the collateral is
not a side-effect of grouping. Grouping is merely wasteful.

## 5. What this raises

* **A Frobenius-matching problem.** Every comparison that used `Block_1` as a unit matched the
  *nominal* displacement of five blocks against other conditions, while its *effective* size is one
  block. The displacement is what it is; what is not proportional is the effect. Which published
  comparisons this touches has not been checked, and should be.
* **Four blocks that do nothing at dose 0.200** sits next to the open claim `two-arms-undiagnosed`
  (*"Two more arms produce no change at all and nobody yet knows whether that is the architecture or
  a bug in delivery"*). Whether `blk01`–`blk04` are inert or merely weak is a dose question and is
  cheap to settle: they exist at ±0.200 only.
* **Limits**: two prompts; one property plus 23 global descriptors, which cannot see a localised
  effect; and the tensor-type cut covers attention only, never the MLP.
