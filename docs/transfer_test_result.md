# A block edit is a transferable treatment — D3 confirmed, without a judge

**Date**: 2026-09-27 · **Material**: the 519 renders of `benchmark_mappa`, already on disk.
**No render, no judge call.** **Pre-registration**:
[`prereg_damage_or_style.md`](prereg_damage_or_style.md), prediction **D3**, frozen 2026-09-27 for a
VLM and carried over verbatim to feature space by Amendment 02 §E after the multi-image gate failed.
**Data**: `data/style_features_mappa.csv` (519 rows, 23 traits, extracted for this test),
`data/transfer_test_mappa.csv` (1080 decisions).

---

## 1. The question and the instrument

Damage is idiosyncratic; a treatment is transferable. So: does the same block edit, applied to a
**different prompt and a different seed**, land in the same place in trait space — against a foil
that is a **different block matched in ‖D‖ at that dose**?

```
reference = (b, d, s) on P01, seed σ, centred on P01's baseline mean
target    = (b, d, s) on P02, seed σ, centred on P02's baseline mean
foil      = (b', d, s) on P02, seed σ
hit  iff  cos(reference, target) > cos(reference, foil)
```

Centring per prompt removes the content; one scale, taken from the **baselines only** (pitfall 33).
Chance is exactly **0.50** by construction. The judge was never needed for this — it was a
2-alternative forced choice all along.

## 2. Result

| block | 0.050 | 0.200 | mean |
|---|--:|--:|--:|
| `Block_1` | 0.667 | **1.000** | 0.833 |
| `Block_2` | 0.333 | 0.500 | **0.417** |
| `Block_3` | 0.667 | 0.667 | 0.667 |
| `Block_4` | 0.333 | **1.000** | 0.667 |
| `Block_5` | 0.333 | **1.000** | 0.667 |
| `Block_6` | **1.000** | **1.000** | **1.000** |

**Pooled 0.7083** over 72 items, **5 of 6** blocks above chance.

> **D3: CONFIRMED** — the bar was > 0.60 with ≥ 5/6 blocks above 0.50.

**Exact permutation null**, over all **720** relabellings of the six P02 blocks — the null that
respects the dependence between cells that share images:

| | value |
|---|--:|
| null mean | 0.5183 |
| null sd | 0.0957 |
| null max | 0.8125 |
| **observed** | **0.7083** |
| **p** | **0.02639** (19 of 720 at or above) |

The naive binomial gives p = 2.7 × 10⁻⁴ and **overstates it**, because the 72 items reuse three
seeds across six blocks. The permutation figure is the one to quote. The exact sign test over the
12 block × dose cells is 8/12, p = 0.194 — the conservative test does **not** clear 0.05, and that
is the honest limit of a design with six items per cell.

## 3. The number to read it against

**Ceiling — the same edit, same prompt, different seed: 0.8299** over 864 items.

That is how often the signature survives a change of *seed alone*. Across a change of *content* it
survives **0.7083**. So a block edit's signature transfers at **85 % of its own reliability
ceiling**: most of what an edit does is a property of the edit, not of the picture it was applied to.

## 4. Three things the table says that were not predicted

* **It gets stronger with dose, not weaker.** Pooled over all six doses: 0.639, 0.639, 0.556, 0.611,
  **0.833, 0.861**. The high-dose images — the ones at 83–101 % of a seed distance, the ones the
  analyst had been calling saturated — carry the **most** recognisable treatment. Whatever is
  happening at 0.200, it is not the erasure of the signature.
* **`Block_6` is 1.000 at every one of the six doses.** Perfect transfer, 36 items, no miss. It is
  the same block that is the exception in `mappa_completa_sterzo_e_deriva.md` (steering fraction
  rising with dose), in the 2026-09-26 replication of it, and in the pixel decomposition.
* **`Block_2` is 0.417, below chance**, and 0.000 at dose 0.080. One block's signature does not
  transfer at all. No explanation is offered here; it is the obvious next thing to look at.

Declared **secondary and exploratory**: the pre-registration named two doses, and the six-dose table
is not part of D3. Its permutation p is also 0.026 (149/216 = 0.690).

## 5. What this does and does not settle

**Settles**: a block edit carries a signature that survives a change of subject and of seed, well
above a magnitude-matched foil. The edits are not noise, and at high dose they are *more*
identifiable, not less.

**Does not settle**: whether those high-dose images are pleasant, usable, or broken. Transferability
is not quality. A reproducible way of ruining a picture is still reproducible. The damage half of
`prereg_damage_or_style.md` remains unmeasured, and §F of Amendment 02 says why no feature in this
project can stand in for it.

**Limits**: two prompts, so the cross-prompt direction is measured in one direction only (P01 → P02)
and the unit of analysis is thin (pitfall 17); six items per cell; the 23 traits are the project's
own descriptor set and a signature invisible to them would not appear here.
