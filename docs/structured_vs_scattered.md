# Is a scattered edit a finer instrument than a coherent one? No, at matched displacement

**Date**: 2026-09-27 · **Question**: Alessandro's — a structureless scramble might look
chroma-specialised because scattering the perturbation over separated areas makes it easier to hit
the ones that carry colour, and moving *a whole block at once* might be the most destructive action
available. **Material**: features already extracted. **No render.** Exploratory.

---

## 1. The test the corpus allows

`data/preset_displacements.csv` records that the three condition families are matched **exactly**:

| preset | D model (abs) | D relative | D CLIP |
|---|--:|--:|--:|
| `Arthemy_Bench_BLOCKSHUFFLE` | 267.37214627 | 0.05381584 | 55.27659757 |
| `Arthemy_Bench_RANDSIGN` | 267.37214627 | 0.05381584 | 55.27659757 |
| `Arthemy_Bench_Base` (`preset`) | 267.37214627 | 0.05381584 | 55.27659757 |

Same Frobenius displacement to eight decimals. `rand` is a sign scramble with **no structure**;
`preset` is the hand-calibrated edit; `blockshuf` is a block permutation — structured, but a
different structure. **32 prompts** carry all three families plus at least three baselines:
F1–F4, G1–G6, S7_01–S7_06 and sixteen I-prompts.

Per prompt, per trait, displacement in units of that prompt's own baseline seed noise; then
`colour_z`, `texture_z`, and their ratio.

## 2. Result

| family | colour_z | texture_z | **colour / texture** | total displacement |
|---|--:|--:|--:|--:|
| `rand` (no structure) | 1.73 | 2.53 | **0.710** | 2.265 |
| `preset` (calibrated) | 1.72 | 2.62 | **0.710** | 2.318 |
| `blockshuf` (permutation) | 1.74 | 2.20 | **0.858** | 2.050 |

**H1 — "scattering catches colour better".** Ratio higher for `rand` than for `preset` in
**17/32** prompts (p = 0.86) and than for `blockshuf` in **13/32** (p = 0.38). The means for `rand`
and `preset` agree to three decimals. **Not supported.**

**H2 — "moving a whole coherent thing is the most destructive".** Total displacement higher for
`preset` than `rand` in **16/32** — exactly half, p = 1.00 — and for `blockshuf` in **12/32**
(p = 0.22). **Not supported.**

If anything the table leans the other way: the **most** structured edit, the block permutation, has
the **highest** colour/texture ratio (0.858) and the **lowest** total displacement (2.050) — a
smaller move, relatively more of it in colour. Neither difference is significant, so it is noted and
not argued.

## 3. Why the old table looked the way it did

The audit of 2026-09-23 found a structureless scramble classified as more chroma-specialised than
any real block, and concluded the classification measures magnitude. Two things complete that:

* the scramble in that table, `scrB`, was matched to **B6's** displacement — **the largest of the
  six** — so it was the biggest perturbation in the comparison;
* the ratio carries a **dimensionality bias of +0.16** in favour of chroma (5 features against 4),
  which the audit measured.

Magnitude plus a biased ratio accounts for the direction as well as the size. **There is no need to
posit that scattering is a finer instrument, and §2 says it is not.**

## 4. The part of the question this does *not* answer, and the tension it leaves

None of `rand`, `preset`, `blockshuf` is *"one whole block at a time"* — all three touch the whole
model. The whole-block edits live in `benchmark_mappa` and are **not** displacement-matched to
these, so the literal comparison Alessandro proposed is not in the corpus. It would need a bench
where one block group and a scramble carry the same D.

And one prior result points **against** the destructiveness half more sharply than §2 does.
`punto7_attrito_e_rettificazione.md` §1 quotes `stage1_gate`: *at identical weight displacement, a
**random** perturbation moves the image **1.68×** more than a structured scaling* (1.36 / 1.91 /
2.06 on three prompts), because *"the coherent edit is largely absorbed by the downstream
normalisations; noise has nothing to cancel it"*.

That says random is the **more** destructive, which is the opposite of H2. §2 here finds no
difference instead of a 1.68× gap — measured on 23 feature descriptors rather than on image
distance, and against a calibrated preset rather than a scaling. **The two measurements are not in
contradiction, they are not the same measurement**, and the discrepancy is recorded rather than
resolved.

## 5. What survives of the intuition

The mechanism Alessandro is reaching for — that a coherent edit is partly cancelled downstream while
a scattered one is not — **is already on record and holds**, in `stage1_gate`. What does not follow
from it is that scattering is therefore *more selective*: §2 shows the colour/texture split is the
same for a structureless scramble and a hand-calibrated preset at identical displacement.

Absorption and selectivity are different properties, and the data separates them.
