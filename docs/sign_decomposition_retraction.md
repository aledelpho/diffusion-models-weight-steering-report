# Retraction: today's pixel decomposition is a retracted measurement, re-derived

**Date**: 2026-09-26, same day · **Applies to**:
[`sign_decomposition_result.md`](sign_decomposition_result.md) §0, §2, §3, §5 and
[`prereg_sign_decomposition_pixels.md`](prereg_sign_decomposition_pixels.md) §1.
**Trigger**: Alessandro asked why *"it becomes a different image"* was being treated as a bad
outcome. Checking that framing led to the repository's own prior work on the same quantity.

---

## 1. The decomposition is not new and its pixel version was already retracted

[`mappa_completa_sterzo_e_deriva.md`](mappa_completa_sterzo_e_deriva.md), **2026-09-19**, on this
same corpus, §1:

> * **A = (Δ⁺ − Δ⁻)/2** — lo **sterzo**: la parte che si inverte cambiando segno al guadagno.
> * **S = (Δ⁺ + Δ⁻)/2** — la **deriva**: la parte che accade in entrambi i versi.
> Frazione di sterzo = |A|/(|A|+|S|).

That is exactly today's `m`, `c` and `F`, under Italian names, seven days earlier. And the pixel
version carries a retraction dated **2026-09-20**, pitfall 63:

> **RITRATTATO.** … *«meno della metà di ciò che un blocco fa ai pixel si inverte col segno»* **è una
> lettura sbagliata: 0.40 è il pavimento aritmetico della statistica, non un risultato.** Confrontando
> due condizioni fra cui *non può* esserci sterzo … la stessa frazione dà **0.394** e **0.390**,
> contro lo **0.409** delle coppie appaiate per segno. La differenza è 0.015.

## 2. I reproduce their table, including the null

Their published steering fraction against mine, recomputed from `data/sign_decomposition_cells.csv`:

| block | 0.020 | 0.050 | 0.120 | 0.200 | mine (mean) | theirs (mean) |
|---|--:|--:|--:|--:|--:|--:|
| `Block_1` | 0.393 | 0.404 | 0.397 | 0.397 | 0.398 | 0.403 |
| `Block_2` | 0.410 | 0.399 | 0.395 | 0.384 | 0.397 | 0.404 |
| `Block_3` | 0.411 | 0.408 | 0.401 | 0.398 | 0.404 | 0.411 |
| `Block_4` | 0.417 | 0.413 | 0.398 | 0.393 | 0.405 | 0.414 |
| `Block_5` | 0.419 | 0.417 | 0.407 | 0.394 | 0.409 | 0.421 |
| `Block_6` | 0.412 | 0.421 | 0.427 | **0.441** | **0.425** | **0.434** |

And their null:

| dose | same block (+,−) | cross-block, same sign | cross-block, opposite sign | gap |
|---|--:|--:|--:|--:|
| 0.020 | 0.410 | 0.392 | 0.385 | **+0.018** |
| 0.050 | 0.410 | 0.397 | 0.384 | **+0.013** |
| 0.120 | 0.404 | 0.394 | 0.381 | **+0.010** |
| 0.200 | 0.401 | 0.387 | 0.376 | **+0.014** |

Published gap: **0.015**. Full replication, seven days and one analyst later, of a table that was
already withdrawn.

## 3. The worse error is mine, and it is in the pre-registration

The floor of this statistic sits at a steering fraction of about **0.39–0.41**, which in the units
I used is **`F ≈ 0.69`**. My pre-registered P1 said *confirmed if `F < 0.25`*.

**I pre-registered a confirmation threshold that the statistic cannot reach in principle.** P1 and
P3 were not falsified by the data; they were unreachable by construction. A pre-registration whose
confirm region lies outside the estimator's range is not a pre-registration, and depositing it
before the data did nothing to protect against that.

The defect that would have caught it is the one the 19/09 authors used: **build the null first**.
I did build it — it is P6 — but I scored P6 as a failed prediction instead of reading it as the
floor it was. The number was on my own screen and I mislabelled it.

## 4. Why I did not find the prior work

My pre-registration §1 asserted that *"neither the sign comparison nor any other measurement in this
project has so far been made on the pixels of a positive/negative pair"*. That sentence is false and
one search would have shown it. I searched the repository for `rectif`, `symmetry`, `sign` — **in
English. The analysis documents are in Italian.** The quantity is called `sterzo` and `deriva`, and
`data/mappa_sterzo_deriva.jsonl` carries `normA`, `normS` and `corr_pos_neg` in its first line.

Third time in one day that the repository already held the answer: the stroke-width quantisation
(audit of 23/09), the CLIP claim wording, and now this.

**Pitfall candidate 72**: *in a bilingual repository, a novelty check run in one language is not a
novelty check.* Search both, or search the data files' column names, which are language-neutral.

## 5. What is withdrawn

* **§0 and §2 of `sign_decomposition_result.md`** — "two thirds of the pixel change does not depend
  on the sign" states the floor of the statistic, not a property of the model. Withdrawn.
* **P1 and P3** — withdrawn as unreachable, not as falsified.
* **§3's three-way decomposition** — the numbers (45 % / 23 % / 32 %) are arithmetically correct and
  they *explain* the floor the 19/09 retraction called "arithmetic": the floor is 0.39 rather than
  0.50 because of the 45 % component common to every block and every sign. Retained as an
  explanation of a known artefact, **not** as a finding about steering.
* **§5's P4 and P6** — P6 is the null, not a prediction. P4's falsification stands as a statement
  about `Block_6`'s ordering but inherits the caveat above.

## 6. What survives, tested against the same null

* **The q/k vs v/o split.** Steering fraction `wq`/`wk` **0.359–0.369** against `wv`/`wo`
  **0.411–0.434**, a gap of **+0.060 — four times the 0.015 floor variation**. The null built inside
  that corpus is 0.400 (cross-cell, same sign) and 0.411 (opposite sign): **q/k sits clearly below
  the null and v/o at or above it.** A two-sided effect against a data-built null, with complete
  separation of the eight cells and 8/8 scenes.
* **The trait-opposition test** — q/k 0.067–0.120 against v/o 0.538–0.758, chance 0.50. A per-trait
  sign count with a noise gate; it has no norm-ratio floor and is untouched.
* **`Block_6` as the exception.** Their table 0.418 → 0.459 with dose, mine 0.412 → 0.441, both
  rising while every other block falls, both above the cross-block null. This is the one part of
  the 19/09 table the retraction explicitly preserved, and it now has an independent replication.
* **P7, weakened.** HF(`c`)/HF(`m`) = **1.469** paired by sign, against **1.276** cross-block same
  sign and **1.158** cross-block opposite sign. The excess is real; the effect is the ratio
  1.469/1.276 ≈ **1.15**, not 1.47.
* **The dose-response exponent (0.19), the saturation percentages, and the images** — magnitudes,
  not ratios, untouched.

## 7. On "it becomes a different image"

The framing was Alessandro's objection and he is right, and the repository already agreed with him.
`coerenza_traiettoria.md` §2:

> un cambio di seed non è rumore, è una perturbazione **massimale** … σ_seed non fa da pavimento di
> rumore ma da **unità di confronto** per un'affermazione sullo *stile*.

A seed distance is a **ruler**, not a **ceiling**. An edit that moves the image as far as a re-roll
has moved it a long way; whether that is damage or a new style is a question the distance cannot
answer, and none of today's statistics address it. `assessment_per_block_dose_calibration.md` §3
used the ruler as a verdict — *"there is no maximum left to find"* — and that sentence imports a
value judgement the measurement does not support. **Withdrawn.**

The project already owns the instruments that could tell damage from style on this corpus — the 23
traits and the judge — and neither has been applied to `benchmark_mappa`. That is the open question,
and it is free of new renders.
