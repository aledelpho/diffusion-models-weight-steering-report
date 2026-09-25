# Amendment 06 to `docs/prereg_perturbation_atlas.md`

- **Written:** 2026-09-25
- **Amends:** §3 of Amendment 05.
- **Everything else in the frozen document and in Amendments 01, 03, 04 and 05 is
  unchanged.**
- **Written before a single atlas preset has been derived and before any render exists.**

---

## 1. The gap

`scale_subset` splits a domain's patches with `split_indexed(patches, r"blocks\.(\d+)\.(.*)")`.
Keys that match go to `grouped` and are rescaled; **everything else goes to `rest`, which is
treated as fixed background and never touched.**

The `txtfusion.*` tensors added as a region by Amendment 04 §3 do not begin with `blocks.`.
They land in `rest`. A `txtfusion` region would therefore come out with its 49 tensors
untouched and the block tensors rescaled to compensate — the opposite of what it is meant
to do.

`modulation_norm` is unaffected: `blocks.{i}.mod.lin`, `prenorm.scale` and `postnorm.scale`
are block-indexed and reachable by the filter.

The region was specified without checking that the machinery could target it. That is the
author's error, the same kind as the five bands over twenty-eight blocks.

## 2. §3 of Amendment 05 replaced

Amendment 05 §3 called the combined-target change "the **only** modification to that logic
authorised anywhere in this study". That clause was written one message before a second
modification turned out to be necessary. It is replaced by this section, which authorises
exactly one more and no others.

`scale_subset` accepts **a predicate over tensor keys** in place of the block-index pattern.
A region is then any set of keys the predicate selects, block-indexed or not.

This is a generalisation, not a change of semantics: a predicate that reproduces the block
pattern must reproduce the existing behaviour exactly. **The convergence check, its
threshold and the exception it raises stay as they are.** The combined-target behaviour of
Amendment 05 §2 is unchanged.

The code path used is recorded in a column of
`data/perturbation_atlas_calibration.csv`.

## 3. The regression gate, re-run

The gate of Amendment 05 §3 runs again, unchanged, against the generalised function:
re-derive `CHAOS_ATTN`, `CHAOS_EDGES`, `CHAOS_MID`, `CHAOS_MLP`, `CHAOS_RAMP` and
`CHAOS_RAND2` and compare with `data/chaos_presets_calibration.csv`.

- Every `d_model_measured` and `d_clip_measured` reproduces to the twelve significant
  digits recorded, and `git diff` on that file is empty -> proceed.
- Anything moves -> **STOP**, and report what moved by how much. No tolerance is widened.

Appended to `data/perturbation_atlas_draw_check.csv` beside the first run's result.

## 4. Recorded incidental change

The first application of Amendment 05 removed a **byte-order mark** from the first line of
`experiments/derive_chaos_presets.py` (`﻿import os` became `import os`). It is harmless
under Python 3 and it was not intended. It is recorded here because an unintended change
that rides along with an intended one is exactly the kind of thing this project has agreed
to name rather than absorb.

## 5. Phase 2's prompt count is not settled here

The frozen §5 sets a minimum of 8 prompts for Phase 2 and prefers 12 or more; the power
gate of `docs/prereg_mountain_reachability_amendment_01.md` §2 needs 12. **Phase 1 is one
prompt regardless**, so the number is not required to launch it and is deliberately left
open. It is fixed before Phase 2 runs, in writing, and never after seeing a Phase 2 number.

## 6. What is not changed

The thirteen conditions and their tensor counts (Amendment 04 §3), the single combined
anchor `D` and its computation by the script (Amendment 05 §2), the scalar-only generated
perturbation (Amendment 03 §2), the four verification gates (Amendment 03 §4), the recorded
properties of the design (Amendment 04 §4), and every section of the frozen document remain
in force.
