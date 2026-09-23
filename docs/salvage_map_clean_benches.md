# Salvage map — what the clean benches can rebuild

**Date**: 2026-09-23. **Not committed by this session**: the device workspace was unavailable, so
this file was written to disk but no git command was run. Commit it before relying on it.

Between 2026-09-22 and 2026-09-23 four HUD-free benches landed in `data/`. This document says
what each one can replace, what it already shows, and what is still missing. No page has been
edited, no claim's status changed, nothing deleted.

## 1. The HUD gate, checked on every new file

Every row of every new manifest and feature table records **1024×1280**. Not one row at 1760.

| file | rows | dimensions |
| --- | ---: | --- |
| `rotations_clean_v1_manifest.csv` | 150 | 1024x1280 |
| `rotations_clean_v1_steps5_manifest.csv` / `_style_features.csv` | 150 / 150 | 1024x1280 |
| `rotations_clean_v1_steps7_manifest.csv` / `_style_features.csv` | 150 / 150 | 1024x1280 |
| `rotations_clean_v2_manifest.csv` / `_style_features.csv` | 150 / 150 | 1024x1280 |
| `rotations_matched_v3_manifest.csv` / `_features.csv` | 324 / 324 | 1024x1280 |
| `all_blocks_clean_v2_style_features.csv` | 294 | 1024x1280 |

`rotations_matched_v3_manifest.csv` also records **`checkpoint_sha256` = `78bbf8f4165eda19…`**,
the VAE and the text encoder. That is the field the audit of 2026-09-21 found missing from every
manifest in the repository. For this bench the gap is closed. `v1` and `v2` still carry
`checkpoint_sha256: not recorded`.

## 2. The map

| what is broken | what can rebuild it | state |
| --- | --- | --- |
| `08-block1-vs-block6`, all three claims (HUD) | **`rotations_matched_v3`** — 12 prompts × 3 seeds = 36 cells, the ten original style prompts **on their original seeds** plus `forge_bench`/`greenhouse` on the three new ones, 9 conditions each | rendered, gated, audited — **not analysed**: no `_results.csv`, no `_prompt_scores.csv` |
| `04-where-in-the-model`, position against displacement (HUD) | **`all_blocks_clean_v2`** — all six block groups, three angles (±5/±10/±15), both signs, scrambles and baseline, 2 prompts × 3 seeds = 294 renders, full feature set | rendered and summarised in `all_blocks_specialization_summary.csv` — no test yet |
| the triangle's missing `Block_6`-anchored null (pitfall 69) | `rotations_matched_v3` carries `scramble_B` | **rendered and unusable** — see §3.2 |
| "is the registered dose inside the usable regime" — never asked | `rotations_matched_v3_pilot_gate.csv` | answered, and the answer is uncomfortable — §3.3 |

## 3. What the new data already says

### 3.1 The statistic flips sign with the dose, at the floor, inside one run

`rotations_clean_v1` rendered the same 6 cells at three matched displacements and scored the
primary texture statistic *s* = cos(scrA, scrB) − cos(B1, B6) at each. Per cell
(`rotations_clean_v1_prompt_scores.csv`):

| displacement | sign of *s* across the 6 cells | exact sign-flip p | reads as |
| --- | --- | --- | --- |
| D = 0.030 | **+ in 6 of 6** (+0.58 … +1.30) | 0.03125 = the floor | hypothesis supported |
| D = 0.045 — the registered point | **− in 6 of 6** (−0.65 … −1.12) | 0.03125 = the floor | hypothesis rejected |
| D = 0.060 | 4 positive, 2 negative | not significant | nothing |

`rotations_clean_v2`, which drops displacement matching and uses fixed angles instead, returns
*s* = **+0.88, p = 0.03125, `supported: True`** at 10°.

Three runs on clean pixels, two of them at the exact permutation floor, **pointing in opposite
directions**. With 6 cells the floor is 2/2⁶ = 0.03125, so any consistent sign lands on it: the
design offers no protection at all against the dose being the thing that decides the sign. None
of these three results should be published as a finding. What they establish is the pitfall.

**Candidate pitfall 72**: *a paired statistic on few units, evaluated at several doses, returns
the permutation floor at whichever dose its sign happens to be consistent. Choosing which dose to
report after seeing them is pitfall 68 wearing a dose label.* The remedy is the one the notebook
already uses elsewhere: fix the dose before the data, or declare the dose axis as the test.

This also means the contaminated page 08 result is not simply "wrong because of the HUD". It sat
at one point of a curve that changes sign, and nothing in its design would have revealed that.

### 3.2 The `Block_6`-anchored null destroys the image

`rotations_matched_v3_quality_gate.csv`, 288 renders, gate on `grad_ratio` and `dL`:

| condition | passed | failed |
| --- | ---: | ---: |
| `Block_1_pos` / `Block_1_neg` | 36 / 36 | 0 / 0 |
| `Block_6_pos` | 36 | 0 |
| `Block_6_neg` | 31 | 5 |
| `scramble_A_pos` / `scramble_A_neg` | 36 / 36 | 0 / 0 |
| **`scramble_B_pos`** | **1** | **35** |
| **`scramble_B_neg`** | **2** | **34** |

`scramble_B` — the sign scramble anchored on `Block_6` — fails **69 of its 72 renders**, and is
69 of the 74 failures in the whole bench. The null that the primary statistic needs cannot be
measured at this dose.

This is the third time the `Block_6`-anchored null has been the missing piece: the triangle had
none (pitfall 69, the borrowed floor), the b1b6 bench measured one on contaminated pixels, and
now a clean render of it does not survive its own quality gate. It is consistent with what
`05-knob-or-cost` already publishes — the tail is rectified and a perturbation there is violent —
but that page is about *rotating* the tail, not about scrambling its signs, and nothing so far
predicted that the scramble would be the arm that breaks.

**Consequence**: the primary statistic as written cannot be computed on gated `v3` data. Three
ways out, all yours to pick: lower the dose for `scramble_B` only and declare the asymmetry;
change the null to one that survives; or report the gate failure as the result and say the
comparison is not available at a usable dose.

### 3.3 The registered dose is far above the usable regime

`rotations_matched_v3` runs at **D = 0.0071**, chosen by a pilot gate over three candidates on
three prompts (`rotations_matched_v3_pilot_gate.csv`, 72 rows):

| D | renders passing the gate |
| --- | --- |
| 0.0071 | 18 of 24 |
| 0.0106 | 16 of 24 |
| 0.0141 | 13 of 24 |

The registered design used **D = 0.045** — **6.3× the dose the gate settles on**, and 3.2× the
highest dose the pilot even tested. On the full corpus at 0.0071 the gate still rejects 74 of 288.

Nothing in the contaminated bench ever ran this gate, so this is new information about the old
design and not only about the new one. It does not by itself invalidate page 08 — but it means the
published result was measured well outside a range that clean renders say is usable.

### 3.4 Page 04's open question, from clean pixels

`all_blocks_specialization_summary.csv` gives, per block group, the norm of the antisymmetric
component in three spaces and their ratio:

| block | ‖A‖ chroma | ‖A‖ shape | ‖A‖ texture | chroma/shape |
| --- | ---: | ---: | ---: | ---: |
| B1 | 0.875 | 1.144 | 0.439 | **0.765** |
| B2 | 0.352 | 0.262 | 0.152 | 1.345 |
| B3 | 0.316 | 0.541 | 0.306 | 0.585 |
| B4 | 0.563 | 0.448 | 0.209 | 1.257 |
| B5 | 0.555 | 0.589 | 0.176 | 0.944 |
| B6 | **2.058** | **2.666** | **1.856** | **0.772** |

B6 is two to six times larger than every other group in all three spaces — the depth effect. But
its **profile** is almost exactly B1's: 0.772 against 0.765, while the middle groups scatter from
0.585 to 1.345. Read at face value that is *same job, different magnitude* — which points at
**proximity, not specialisation**, the reading `08-block1-vs-block6` records as still open.

This is one summary table on 2 prompts × 3 seeds with no test and no null. It is a hypothesis
worth testing, not an answer. But it is the first clean evidence that bears on that question, and
the test is cheap: the renders already exist.

## 4. What is missing

1. **`rotations_matched_v3` has no analysis.** Manifest, features, audit and two gates are on
   disk; `_results.csv` and `_prompt_scores.csv` are not. This is the one step between here and a
   clean replacement for page 08 — blocked on the `scramble_B` decision in §3.2.
2. **`all_blocks_clean_v2` has no test.** Summary table only, no null, no p.
3. **`v1` and `v2` record no `checkpoint_sha256`.** `v3` does.
4. **No page cites any of this yet.** Pages 04 and 08 still carry their contamination banner and
   their original numbers.
