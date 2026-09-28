# Render spec — C23, the dose ladder on the twenty leaf seeds

- **For:** Alessandro, who launches every render. **The analyst generates none.**
- **80 renders.** Nothing that already exists is re-rendered.
- **Origin:** [`leaf_collapse_predictors_result.md`](leaf_collapse_predictors_result.md) §5.

---

## 1. Why this, and why now

C22 came back negative and the negative is what makes this worth rendering. Nothing in the
unperturbed image — twelve features separately, or all twelve jointly against an exactly
enumerated null over 167 960 splits — distinguishes the nine seeds that lose their colour from the
eleven that do not. So the collapse is not a property of the picture the model was going to draw.

What is left is the **trajectory**, and the cheapest handle on a trajectory is **dose**. The outcome
at 0.200 is bimodal with an empty gap: nine cells at 0.034–0.085, then nothing until 0.518. That
shape is a bifurcation, not a threshold on a smooth quantity — **unless the gap fills in when the
dose is moved**, which is exactly what this bench tests.

## 2. The design

| | |
|---|---|
| prompt | the exact arm-A string, character for character |
| seeds | all twenty of arm A — the nine that fire and the eleven that do not |
| new doses | **0.050, 0.080, 0.120, 0.280** |
| reused, **not** re-rendered | the 20 baselines and the 20 cells at dose 0.200 |
| drive | tuner named input **`Block_4 = -dose`**, `vectors_override` **empty**, `granular_json` empty, mode `Real Value` |
| settings | `euler_ancestral`, `simple`, 9 steps, CFG 1.0, 1024 × 1280 |

**0.280 is not padding — it is the dose that decides D2.** If every seed has its own threshold and
the nine simply have lower ones, pushing past 0.200 must recruit some of the eleven. If nothing is
recruited, the eleven are not "seeds with a higher threshold", they are a different kind of seed.

`fire` / `quiet` labels travel in the plan as `group_at_0200` so the analysis cannot silently
regroup them after the fact.

## 3. Predictions, frozen before the renders

A **hit** is the same as in the parent bench: chroma ratio < 0.20 against that seed's own baseline
**and** IoU ≥ 0.70 with it.

| # | prediction | confirmed if | falsified if |
|---|---|---|---|
| **D1** | the switch is monotone per seed: once a seed fires it keeps firing at every higher dose | ≥ 18 of 20 seeds show a clean staircase | ≥ 5 seeds fire at one dose and not at a higher one |
| **D2** | the eleven quiet seeds have thresholds above 0.200 | ≥ 3 of 11 fire at **0.280** | **0 of 11** fire at 0.280 |
| **D3** | the firing rate is non-decreasing in dose across 0.050 → 0.080 → 0.120 → 0.200 → 0.280 | no decrease greater than 2 seeds | any decrease of ≥ 4 seeds |
| **D4** | the effect needs dose | strictly fewer hits at 0.050 than at 0.200 | as many or more at 0.050 |
| **D5** | **the gap persists at every dose** | < 10 % of all 100 cells land in chroma ratio [0.15, 0.45] | > 25 % land there |

**D5 is the experiment.** D1–D4 describe how the switch moves; D5 asks whether it is a switch at
all. If the gap fills in as the dose is swept, the outcome is a smooth function of something after
all and "bifurcation" is the wrong word — and that would be the more interesting result, because a
smooth quantity can be searched for, while a bifurcation can only be catalogued.

**Read D5 against D2.** The informative combinations:

* **D5 holds, D2 confirmed** — a genuine per-seed threshold on a discrete switch. The next question
  is what sets each seed's threshold, and it is a one-dimensional quantity, which is tractable.
* **D5 holds, D2 falsified** — the eleven never fire at any dose. Two populations of seeds, not one
  with a spread of thresholds, and C24 (decoding the trajectory) becomes the only route.
* **D5 falsified** — no switch. The bimodality at 0.200 was an accident of that one dose, and the
  whole framing since `leaf_collapse_and_blk16_result.md` §2 needs rewriting. That is recorded here,
  in advance, so it cannot be quietly dropped later.

## 4. Provenance checks before the full queue

The same two that caught nothing last time and are therefore worth repeating:

1. Queue the first three rows, stop, and read `vectors_override` (must be **empty**) and
   `Block_4` (must be **−dose**) back out of the PNG metadata, comparing with the CSV.
2. Confirm the analysis reuses the existing 0.200 and baseline renders rather than expecting new
   ones — 80 files should appear in the new folder, not 120.

`experiments/verify_leaf_and_blk16_provenance.py` is the pattern to copy for the first.

Plan: `data/leaf_dose_plan.csv`, built by `experiments/make_leaf_dose_plan.py`. **80 rows.**
Folder `benchmark_leaf_dose\renders`; filenames `LN_B4neg_0.050_krea2_seed2001_00001_.png` and so
on — the same convention as the parent bench, so the existing 0.200 cells drop straight in.

## 5. Standing constraints

- The analyst generates no render and requests none beyond this document.
- Nothing written under `notebook/`. No claim status changes.
- Validator at 0 errors before every commit; commit messages in Italian; repository content in
  English; **do not push**.
- **Nothing in this project may shut down or close the machine.**
