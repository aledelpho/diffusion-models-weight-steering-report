# Run plan — `rotations_clean_v1`: the rotation bench re-rendered without the HUD

**For**: the agent driving ComfyUI. Execute the phases in order. Every phase has an abort
condition; if one fires, stop and report — do not continue and do not improvise a workaround.

**Why this run exists.** All 555 renders of the three rotation benches were saved at 1024×1760:
a 1280-tall picture with a 480-pixel HUD strip attached. A HUD in the frame moves the
measurements, so every texture and palette feature computed on them is contaminated. See
`docs/hud_contamination_1024x1760.md` and `data/hud_contaminated_images.csv`.

**What this run is, and is not.** It is a **clean-pixel pilot on two prompts**, not a
replacement for `notebook/08-block1-vs-block6.md`. That page's registered statistic is a
leave-one-out test across ten prompts and cannot be computed from two. This run answers three
questions and no others:

1. Are the renders HUD-free, and does the pipeline now record what made them?
2. Does the direction separation between the two block groups survive on clean pixels, on a
   6-unit paired test with its own exact floor?
3. Is the separation dose-dependent, over a matched-displacement sweep?

A positive result licenses re-rendering the full ten-prompt bench. It does not restore the
published claims. A negative result is decisive in the other direction and saves 210 renders.

---

## Phase 0 — calibration, no rendering

Solve the rotation angle per block group for each of three matched displacements, on the
weights, using `experiments/calibrate_matched_rotation_angles.py` (the script that produced
`data/matched_rotation_calibration.json`).

| target D (relative, whole model) | why this value |
| --- | --- |
| 0.030 | below the registered point, above the round-trip floor |
| **0.045** | the registered point — 23.69° for `Block_1`, 32.21° for `Block_6`, residual 6e-07. **Do not re-solve it; reuse the calibrated angles.** |
| 0.060 | above the registered point, still under the usable-regime ceiling |

* Block groups: `Block_1` = blocks 0–4, `Block_6` = blocks 24–27. Unchanged.
* Tolerance: the two groups' measured D must agree to **≤ 1e-6** at each level. Bisection must
  **fail loudly** rather than return its nearest candidate (pitfall 13).
* Scrambles: `scramble_A` is a sign scramble of the `Block_1` rotation on the same tensors,
  `scramble_B` the same for `Block_6`, one fixed RNG seed each, recorded. **Measure their D
  and write it down** — a scramble does not inherit the target displacement (pitfall 45).
* Persist everything to `data/matched_rotation_calibration_v2.json`: per level and per group,
  the angle, the measured `d_model`, the tensor count, the scramble seeds and their measured D.

**Abort if** any level cannot be matched to 1e-6, or a scramble's measured D differs from its
anchor's by more than 2%.

---

## Phase 1 — corpus

**Prompts — two, both from `data/prompts_probe_krea2.json`, verbatim, never edited:**

| id | tag | sha1 |
| --- | --- | --- |
| P01 | `forge_bench` (the blacksmith woman) | `52e5b19ca6` |
| P02 | `greenhouse` (the botanist man in the glasshouse) | `7919c95fcf` |

Verify each prompt's sha1 before rendering; a mismatch means the text was edited and the run
is void.

*Two things to record about this choice, because they change what the run can claim.* These
two prompts are the only ones in the project with a **measured seed-to-seed noise floor**
(1.65% and 1.84% on fine texture, 18 baseline seeds each) and with a deliberately controlled
material and colour composition — which is why they suit a 6-unit pilot. But their own source
file declares they *"do not enter any statistic"*, and this run contradicts that note: amend
the note or accept the contradiction, do not ignore it. And they share **one style** and differ
by **subject**, where the contaminated bench had ten styles and one subject. This pilot
therefore varies the opposite axis, and generality across styles is untested by it.

**Seeds — three, new, fixed here before any render:**

```
2718281   3141592   1618033
```

None of the three appears anywhere in `data/`. Verified 2026-09-21.

**Unit of analysis**: the (prompt, seed) cell. **6 cells.**

---

## Phase 2 — render

**Output folder**: `benchmark_rotations_clean_v1/renders` — **new, and used by nothing else.**
Never write into `rotations_block1_vs_block6/`: that folder already holds two experiments'
images and reading it as one corpus is how pitfall 30 happened for the third time.

Sampling, unchanged from the bench being replaced: `euler_ancestral`, 9 steps, CFG 1.0,
denoise 1.0, `simple` scheduler, **1024×1280**.

Render in three blocks, in this order. Stop after any block and the run is still useful.

| block | conditions | cells | renders | what it buys |
| --- | --- | ---: | ---: | --- |
| **A** | `baseline`, then `B1`/`B6`/`scrA`/`scrB` × `pos`/`neg`, all at **D = 0.045** | 9 | **54** | the primary test, and the answer to "is the HUD gone" |
| **B** | `B1`/`B6` × `pos`/`neg` at **D = 0.030** and **D = 0.060** | 8 | **48** | the dose axis on the real pair |
| **C** | `scrA`/`scrB` × `pos`/`neg` at **D = 0.030** and **D = 0.060** | 8 | **48** | the null at the other two doses |

**Total 150 renders** (9 + 8 + 8 = 25 conditions × 6 cells).

One baseline per cell, shared across all doses and conditions — 6 baseline renders in total,
inside block A's 54.

---

## Phase 3 — the gate, before any feature is extracted

Run these in order and **abort the whole run on the first failure**. Nothing downstream is
allowed to touch an image that has not passed.

1. **Dimensions.** Every PNG is exactly **1024 × 1280**. Any other size means the HUD is still
   attached; abort and report the offending files. This is the single check the whole run
   exists for.
2. **Count.** The number of files equals the number of rows planned for the blocks that ran.
3. **No stragglers.** The output folder contains nothing but this run's files.
4. **Eyeball.** Save one 3×3 contact sheet of whole frames, `qc_output/rotations_clean_v1/`,
   and look at it. Dimensions alone would not catch a HUD drawn *inside* the frame.

---

## Phase 4 — manifest

Write `data/rotations_clean_v1_manifest.csv`, **one row per render**, with every column below.
The reproducibility audit of 2026-09-21 found that no manifest in this repository records the
checkpoint, the VAE or the text encoder on any page. This run closes that gap for itself, and
the columns are not optional:

```
run_id, prompt_id, prompt_sha1, seed, condition, dose_target_D, angle_deg, measured_D,
checkpoint, checkpoint_sha256, vae, text_encoder, tuner_node, tuner_version, tuner_mode,
sampler, steps, cfg, scheduler, denoise, width, height,
image_path, baseline_path, renders_root, suite_git_sha, timestamp
```

Read these out of the ComfyUI graph the PNG carries in its `tEXt` chunk, not from this
document. If a field genuinely is not in the graph, write `not recorded` — never a plausible
value.

---

## Phase 5 — analysis, declared here before the data exist

**Do not modify any analysis script.** Feature extraction is `style_features.py` and
`analyze_palette` as they stand.

**Direction of a condition, per cell**: Δ = features(condition) − features(baseline), same
prompt and same seed. **Direction of a block group**: the antisymmetric part
**A = (Δ⁺ − Δ⁻) / 2**. This is the project's settled convention and it is invariant to the
centring convention — the exact ambiguity that dissolved stage 9's result (pitfall 37).

**Primary statistic, one per cell**, 6 cells:

```
s  =  cos(A_scrA, A_scrB)  −  cos(A_B1, A_B6)
```

positive when the two real block groups are further apart in direction than two arbitrary
perturbations of the same displacement are from each other.

**Null**: exact sign-flip permutation over the 6 cells. Floor **2 / 2⁶ = 0.03125**.

**Criterion, frozen**: the hypothesis is supported only if `s > 0` with `p < 0.05` in the
primary space named by `docs/prereg_rotations_block1_vs_block6.md`, which is unchanged.

**Multiplicity.** Six units admit exactly **one** test at α = 0.05. There is one primary and no
family. The other four measurement spaces are reported beside it, uncorrected, and labelled
secondary — they cannot confirm anything on their own.

**Dose (blocks B and C only)**: report `s` at each of the three matched displacements, as three
numbers with their per-cell values. Declared **descriptive**: three doses on six cells is not a
dose-response test, and it will not be written up as one (pitfall 49).

**What the run may conclude.** That the separation survives HUD-free pixels on two subjects in
one style, or that it does not. It may not conclude anything about ten styles, and it does not
restore `08-block1-vs-block6`, whose claims stay flagged until the full bench is re-rendered.

---

## Deliverables

1. `data/matched_rotation_calibration_v2.json`
2. `benchmark_rotations_clean_v1/renders/` — up to 150 PNGs, all 1024×1280
3. `data/rotations_clean_v1_manifest.csv`
4. `data/rotations_clean_v1_style_features.csv`, `..._palette_features.csv`
5. `data/rotations_clean_v1_prompt_scores.csv` — the 6 per-cell values of `s`
6. `data/rotations_clean_v1_results.csv` — `s`, its p, and the five spaces
7. `qc_output/rotations_clean_v1/` — the contact sheet from the gate
8. A short run log: what was rendered, what the gate returned, what aborted if anything

Report the gate's result first, before any statistic. If phase 3 fails, that is the finding.
