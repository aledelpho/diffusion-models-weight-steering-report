# Inventory of the notebook migration

**Written 2026-09-21, against commit `5f46c00` on `main`, working tree clean.**

This file exists because the previous pass planned the migration from an assumed structure
instead of a measured one, and underestimated it. Everything below was produced by listing,
counting and grepping the tree — not from memory. Where a number is stated, the command that
produced it is implied by the section heading; where something is *missing*, that was checked
by `test -f`, not inferred.

---

## 0. Nine things that are not what the migration plan assumed

These are stated first because several of them block work that the plan treats as ready.

1. **`notebook/_migrating.yaml` does not exist**, and never has (`git log --all` finds no
   commit that touched it). There is no ledger of the claims still waiting to be migrated, and
   therefore nothing for the validator to cross-check a page against. The list of pending
   claims survives only as the prose bullet list in the old README, reproduced in §5 below.

2. **The monolithic README is no longer in the working tree.** Commit `5f46c00` replaced it
   with a generated 475-word stub that is only the claims table. The 20,704-word source text —
   the thing the migration is supposed to cut from — lives at `c843d61:README.md` in git
   history, and nowhere else on disk. Any migration session must recover it first:
   `git show c843d61:README.md`.

3. **`experiments/notebook_figures.py` and `experiments/notebook_charts.py` do not exist**, and
   never have in any commit. `AUTHORING.md` §4.2 requires every figure to name a `builder`
   function in one of those two modules, §4.4 points at a palette defined in
   `notebook_charts.py`, and all eleven entries in `experiments/figures.yaml` name a builder
   (nine of them non-null). **Not one of those builders is implementable code that exists.**
   The eight figure files currently on disk therefore cannot be regenerated from their
   measurement files, and no new evidence figure can be registered in conformity with the
   contract until those modules are written. The validator does not catch this: it checks that
   the *output* file exists, never that the builder does.

4. **`experiments/extract_repro.py` does not exist either.** `AUTHORING.md` §5 instructs the
   author not to type the reproducibility block from memory but to have that script print it
   from the PNG text chunks. Both existing pages' reproducibility blocks were therefore typed
   by hand, which is the failure mode §5 was written to prevent.

5. **`docs/prereg_punto7_simmetria_segno.md` does not exist.** `05-knob-or-cost.md` declares it
   in front matter and links to it in the body. It is the only confirmatory page in the
   notebook, and the document that makes it confirmatory rather than exploratory is absent from
   the repository. The validator only checks that the field is non-null, not that the file
   resolves. The text appears to survive outside the repository (see §7, item 2).

6. **`data/stage7_manifest.csv` does not exist.** It is the declared `source` of both F01.1 and
   F01.2 — the two figures already registered for `01-mark-style`, the next page to be
   migrated. Candidate substitutes actually on disk: `data/stage7a_images.csv`,
   `data/stage7b_images.csv`, `data/style_features_stage7.csv`,
   `data/palette_features_stage7.csv`.

7. **The pitfall registry holds 63 entries, numbered 1–63 with no gaps.** Of the three staging
   files, `docs/_pitfalls_44_47_da_inserire.md` and `docs/_pitfalls_48_50_da_inserire.md` have
   **already been merged** — entries 44–50 are present in `errors_log.md` with identical
   opening text — and are now stale duplicates. Only
   `docs/_pitfalls_64_67_da_inserire.md` (entries 64–67) is genuinely pending. The true
   backlog is four entries, not eleven.
   *Closed 2026-09-21: 64–67 merged, the registry runs 1 to 67 contiguous, and all three
   staging files now carry a MERGED banner. They still need deleting by hand.*

8. **The validator self-test has 18 checks, not 20, and all 18 pass.** `CASES` holds 17
   injected faults plus the clean-tree check. It also copies the entire 2.4 GB tree once per
   case — roughly 48 GB of I/O per run — although the validator reads only `notebook/`,
   `experiments/figures.yaml` and `assets/<page-id>/`. On a tree pruned to those three inputs
   the same suite runs in seconds and reports the same 18/18, and the full validator reports
   the identical `0 error(s), 2 warning(s)`.

9. **`data/punto7_blocks.csv` and `data/bench_checks.csv` have no producing script.** Both were
   added as new files by `5f46c00`, and no script in `experiments/` mentions either filename.
   They are the sole source of every published number on the two live pages, and they are
   currently unreproducible from the repository.

A tenth item, smaller but concrete, is dealt with in §7: the alt text of F05.3 publishes the
retracted rectification ratio.

---

## 1. `docs/` — 44 markdown files and 2 directories

`dest` is the page of §6 that the document belongs to. `provenance` means the document is not
a chapter but supporting material a page cites (pre-registration, verdict, measurement note).

| file | what it is | dest |
|---|---|---|
| `errors_log.md` | The pitfall registry, 63 entries, plus the replication checklist. 11,162 words | cited by every page |
| `scope.md` | What the project is for, and what it refuses to claim | README / front page |
| `asset_pipeline.md` | Asset layout, batch figure conventions, repository weight | `AUTHORING.md` reference |
| `audit_metodologico_2026-09-20.md` | Methodological audit: what is wrong and what is missing | meta — read before migrating |
| `figure_brief.md` | Figure brief for the attribute-emergence experiment | 02, provenance |
| `_pitfalls_44_47_da_inserire.md` | **Stale** — already merged into `errors_log.md` | delete candidate |
| `_pitfalls_48_50_da_inserire.md` | **Stale** — already merged into `errors_log.md` | delete candidate |
| `_pitfalls_64_67_da_inserire.md` | Pitfalls 64–67, genuinely pending | merge into `errors_log.md` |
| `giornata_2026-09-18.md` | Day log, 18 Sept, 3,070 words | archive / provenance |
| `prereg_hatching_axis_stage7.md` | Pre-registration, hatching axis | 06, provenance |
| `prereg_attribute_emergence_stage7.md` | Pre-registration, attribute emergence | 02, provenance |
| `prereg_chromatic_signatures.md` | Pre-registration, chromatic signatures | 07, provenance |
| `prereg_hatching_order_stage8.md` | Pre-registration stub, hatching on objects — **not run** | 06, open question |
| `prereg_rotations_block1_vs_block6.md` | Pre-registration, Block_1 vs Block_6 | 08, provenance |
| `prereg_stage9_style_direction.md` | Pre-registration, style-dependence of direction | 09, provenance |
| `prereg_stage12_ingrandimento.md` | Pre-registration, subject enlargement on new corpus | 03, provenance |
| `prereg_stage2_corpus_nativo.md` | Pre-registration, hatching axis on native corpora, two architectures — **not run** | 14, open question |
| `previsione_01_composizionalita.md` | Frozen prediction: tonal effects of blocks add | 12, provenance |
| `previsione_02_saturazione_direzionale.md` | Frozen prediction: saturation depends on the angle between edits | 12, provenance |
| `reproduce_stage7.md` | How to reproduce stage 7 | 01/06, reproducibility |
| `rotations_block1_vs_block6_results.md` | Experimental results, Block_1 vs Block_6 | 08 |
| `pilot_rotations_verdict.md` | Re-analysis of the pilot rotations, verdict. 4,929 words | 04 |
| `stage9_verdict.md` | Stage 9 verdict under the restored criteria — not supported | 09 |
| `stage10_headlights_results.md` | Blind scoring of the headlights, results | 02 |
| `stage10_bbox_verification.md` | Bounding box, independent verification and a correction | 03 |
| `stage12_verifica.md` | Stage 12, independent verification | 03 |
| `observations_stage9.md` | Direct observations recorded before the measurement | 09, provenance |
| `punto7_attrito_e_rettificazione.md` | The negative arm: friction and rectification | 05 (migrated) |
| `block6_nel_latente.md` | Block 6 in the latent: the knob is there, the VAE hides half | 10 |
| `block6_e_struttura_gruppi.md` | The Block 6 theory, and non-contiguous groups | 10 |
| `coerenza_traiettoria.md` | Trajectory coherence: the seed watermark as a measure | 11 |
| `mappa_completa_sterzo_e_deriva.md` | The full map: steering against drift, why two concordant blocks cancel | 12 |
| `regola_angolo_9_coppie.md` | The angle rule on nine pairs | 12 |
| `mappa_krea2_primo_esito.md` | Exploratory block map on Krea-2, first outcome | 13 |
| `brief_mappa_esplorativa.md` | Brief for the exploratory block map | 13, provenance |
| `esistono_i_blocchi.md` | Do the "blocks" really exist? Measured on the 28 single blocks | 13 |
| `monotonia_profondita_esito.md` | Monotonicity with depth — refuted, and it is a step | 13 |
| `report_monotonia_profondita.md` | Per-single-block coherence report, 168 images | 13, provenance |
| `e_tutto_scrambling.md` | "Is it all just scrambling?" — how much of each edit is universal damage | 13 |
| `anima_stage1_results.md` | Anima stage 1: hierarchical transposition onto Cosmos-Predict2 | 14 |
| `anima_stage1_revisione.md` | Independent review of Anima stage 1 | 14 |
| `anima_dosesweep_verifica.md` | Anima dose sweep: independent verification and prereg verdict | 14 |
| `brief_dosesweep_completamento.md` | Brief: finish the Anima dose sweep, 30 images | 14, provenance |
| `brief_patch_anima_groupmap.md` | Brief: patch the tuner's `GROUP_MAP` for Anima | 14, provenance |
| `model_structures/` (13 files) | Architecture decompositions and tensor summaries for Krea-2, Anima, Qwen3-VL | reference, cited by 04/13/14 |
| `workflow/` (4 files) | ComfyUI graphs (10/11/12 nodes) and their README | reproducibility, cited by 00 |

---

## 2. `experiments/` — 70 Python scripts, plus `figures.yaml` and `__pycache__`

The directory holds 72 entries. Grouped by role, and marked **P** where the script's output is
cited by a document or a notebook page (i.e. it stands behind a published number) and **—**
where it does not.

| role | scripts | published? |
|---|---|---|
| **Notebook infrastructure** | `build_notebook.py`, `validate_notebook.py`, `test_validate_notebook.py` | P (the pipeline itself) |
| **Corpus and prompt construction** | `build_anima_corpus.py` **P**, `build_probe_corpus.py` **P**, `build_sealed_corpus.py` **P**, `select_confirmation_prompts.py` **P**, `stage6_prompts.py` —, `stage7_prompts.py` —, `stage8_prompts.py` —, `prepare_stage12_blind.py` —, `prepare_stage12_pattern.py` — | mixed |
| **Perturbation derivation and dose calibration** | `derive_blockshuffle.py`, `derive_chaos_edges_v2.py`, `derive_chaos_presets.py`, `derive_epsilon.py`, `derive_flat.py`, `derive_subset.py`, `measure_all_displacements.py`, `compute_rotation_displacement.py` **P**, `calibrate_matched_rotation_angles.py` **P** | 2 of 9 |
| **Render runners** | `run_stage7a.py` **P**, `run_stage7b.py` **P**, `run_stage9.py`, `run_stage12.py`, `run_epsilon.py`, `run_rotations_block1_vs_block6.py`, `run_style_features.py` | 2 of 7 |
| **Feature extraction** | `style_features.py` **P**, `style_from_manifest.py` **P**, `palette_from_manifest.py` **P**, `palette_stage4_baseline.py` **P**, `extract_block1_vs_block6_features.py`, `extract_pilot_benchmarks.py` **P**, `extract_rotation_comparisons.py`, `measure_pilot_rotation_directions.py` **P**, `measure_body_area.py`, `texture_diagnostics.py`, `color_freedom.py` | 6 of 11 |
| **Analysis** | `analyze_block1_vs_block6.py` **P**, `analyze_headlights.py` **P**, `analyze_pilot_rotations.py` **P**, `analyze_pilot_rotations_followup.py` **P**, `analyze_pilot_rotation_directions.py` **P**, `analyze_stage9_style_direction.py` **P**, `analyze_bbox_groundtruth.py`, `analyze_palette.py`, `analyze_palette_coherence.py`, `analyze_palette_sa.py`, `analyze_quantization.py`, `analyze_stage12_ingrandimento.py`, `analyze_stage12_pattern.py`, `analyze_stage5.py`, `analyze_style_features.py`, `analyze_texture.py`, `global_aggregation_corrected.py`, `stage5_followup.py`, `stage9_centering_sensitivity.py` **P**, `stage9_observation_quantification.py`, `score_headlights.py` **P**, `generate_block1_vs_block6_report.py` **P**, `block_sweep_maps.py` | 9 of 23 |
| **Figure building (legacy, not contract-conformant)** | `build_figures_headlights.py`, `build_figures_stage12.py`, `build_palette_sheet.py` | — |
| **Watchdogs and gates** | `watchdog_stage9.py`, `watchdog_stage12.py`, `watchdog_block1_vs_block6_shutdown.py`, `vlm_gate.py`, `make_anima_brief.py` | — |

Two observations that matter for the migration:

- **The three figure-building scripts predate the contract.** They read `data/figure_crops*.json`,
  which is a file of hard-coded crop rectangles — exactly what `AUTHORING.md` §4.3 rule 2
  forbids. They cannot be reused as builders; the locator machinery they would need does not
  exist (see §0 item 3).
- **No script writes `data/punto7_blocks.csv` or `data/bench_checks.csv`** (§0 item 9).

---

## 3. `data/` — 111 files

**Backing a published number** (the file is named by a document under `docs/` or by a page
under `notebook/`): 26 files. The two that matter most are the two with no producing script.

| file | cited by | produced by |
|---|---|---|
| `bench_checks.csv` | `00-the-bench.md`, `05-knob-or-cost.md` | **nothing in the tree** |
| `punto7_blocks.csv` | `05-knob-or-cost.md` | **nothing in the tree** |
| `prompts.json` | both live pages, `AUTHORING.md`, `docs/workflow/README.md` | 5 runner scripts consume it |
| `confirmation_prompts.csv` | `prereg_hatching_axis_stage7.md`, `reproduce_stage7.md` | `select_confirmation_prompts.py` |
| `stage7a_images.csv`, `stage7b_images.csv`, `stage6b_pilot_images.csv` | `reproduce_stage7.md` | `run_stage7a/b.py` |
| `style_features.csv`, `style_features_stage7.csv` | `prereg_hatching_axis_stage7.md`, `reproduce_stage7.md`, `pilot_rotations_verdict.md` | `style_features.py`, `style_from_manifest.py` |
| `palette_features_all.csv`, `palette_features_stage7.csv`, `palette_features_stage7_all.csv`, `palette_features_stage7a_candidates.csv`, `palette_condition_cosines*.csv` | `reproduce_stage7.md` | `palette_from_manifest.py`, `palette_stage4_baseline.py` (two of the six: nothing) |
| `palette_features_stage9.csv`, `stage9_headlights_raw.csv` | `giornata_2026-09-18.md` | `analyze_headlights.py`, `score_headlights.py` |
| `stage9_coherence_results.csv`, `stage9_centering_sensitivity.csv` | `stage9_verdict.md`, `prereg_stage9_style_direction.md` | `analyze_stage9_style_direction.py`, `stage9_centering_sensitivity.py` |
| `pilot_rotations*.csv` (6 files), `pilot_macro.csv`, `pilot_rotation_displacement.csv` | `pilot_rotations_verdict.md` | the `analyze_pilot_*` / `measure_pilot_*` family |
| `rotations_block1_vs_block6_results.csv`, `..._prompt_scores.csv`, `matched_rotation_calibration.json` | `rotations_block1_vs_block6_results.md`, its pre-registration | `analyze_block1_vs_block6.py`, `calibrate_matched_rotation_angles.py` |
| `stage4_images.csv` | `errors_log.md`, `prereg_chromatic_signatures.md` | render runners |
| `stage8_armA_results.csv` | `observations_stage9.md` | **nothing in the tree** |
| `prompts_anima_native.json`, `prompts_probe_krea2.json`, `prompts_sealed_krea2.json` | the Anima and exploratory-map briefs | `build_*_corpus.py` |
| `attribute_emergence.csv`, `comfy_graphs.json`, `figure_crops.json` | `asset_pipeline.md`, `figure_brief.md`, `workflow/README.md` | **nothing in the tree** |

**Consumed by a script but never cited by a document** (intermediate products): 64 files —
the `stage2/4/5/6/9/12_images.csv` manifests, the `_stage5_*.npz` caches, the `stage12_*` and
`stage9_bbox*`/`body_area` tables, the PCA and global-aggregation outputs, the progress logs.

**Named by nothing at all** — no script reads or writes them, no document mentions them by
name: **21 files.**

```
anima_dosesweep_features.jsonl      direzioni_per_dose.jsonl         stage8_armB_results.csv
attribute_emergence_recipe.json     direzioni_rotazioni_e_scramble.jsonl  stage8_armC_results.csv
block6_misure_dirette.jsonl         direzioni_spazio_stile.jsonl     stage8_images.csv
coerenza_per_blocco_singolo.jsonl   effetti_invarianti_seed.jsonl    stage8_progress.log
coerenza_traiettoria.jsonl          figure_crops_stage7.json         style_features_stage8.csv
composizione_stats.json             mappa_krea2_sweep_summary.csv    palette_features_stage8.csv
direzioni_blocchi_singoli.jsonl     mappa_sterzo_deriva.jsonl        risultati_monotonia_profondita.json
```

This list is not dead weight — it is the opposite. These are precisely the measurement files
behind the documents queued for pages 10 to 14 (`coerenza_traiettoria.md`,
`mappa_completa_sterzo_e_deriva.md`, `block6_nel_latente.md`, `esistono_i_blocchi.md`,
`monotonia_profondita_esito.md`, the Anima sweep). Those documents quote numbers **without
naming the file the numbers came from**, and no script in the repository regenerates them.
Every one of those pages will hit rule 7 the moment it is written. Establishing the
file ↔ number correspondence for these 21 files is a prerequisite for pages 10–14, and it is
work that does not exist in any plan yet.

---

## 4. `assets/` — 8 directories, 1,417 files, 100 MB

| directory | files | what it holds | page |
|---|---|---|---|
| `00-the-bench/` | 3 | F00.1 roundtrip sentinel (webp), F00.2 patch-path schema (svg), F00.3 noise-floor history (webp) | 00 — live |
| `05-knob-or-cost/` | 5 | F05.1–F05.4 (webp), F05.5 decomposition schema (svg) | 05 — live |
| `01_steering/` | 380 | 378 webp renders in 8 condition folders (`baseline`, `preset`, `preset_half`, `preset_neg`, `blockshuffle`, `blockshuffle_neg`, `randsign`, `randsign_neg`) + `_figures` + 2 workflow json | 01 — source renders |
| `01_steering_stage7/` | 608 | 608 webp in 7 condition folders (`baseline`, `preset_pos/neg`, `blockshuf_pos/neg`, `rand_pos/neg`) + `_figures` | 01 and 06 — the confirmation round |
| `02_attribute_emergence/` | 404 | 401 webp across 24 arm folders (`A1`–`A7` prompt-ablation arms, `B1`–`B7` subject variants, `C1`, `D0`–`D7` dose ladder, `E1`–`E3` model/clip split) + 3 json | 02 — source renders |
| `03_what_ends_up_in_the_picture/` | 3 | `_figures/` only: `subject_size_boxes.webp`, `blinding_4afc_trial.webp`, `photometric_signature.webp` | **03 — the directory the previous pass did not know about** |
| `hero/` | 9 | 6 gif (5-seed synchronised steering, timelapse, crop timelapse), 2 png strips, 1 webp | README / front page |
| `motion/` | 5 | 2 gif (six-block motion and ramp), 3 jpg (Anima dose examples, block map P01, composition P01) | 04, 12, 14 |

`03_what_ends_up_in_the_picture/_figures` contains finished figures for a page that does not
exist and is not in the eight-page plan. Their subjects — subject size, the 4AFC blinding
trial, the photometric signature — are Experiment 3 and §1.7 of the old README.

---

## 5. The old README (`git show c843d61:README.md`) — 20,704 words, 1,762 lines

| lines | section | destination |
|---|---|---|
| 1–14 | Title and framing | README (generated header) |
| 15–35 | What counts as a result here | README / `scope.md` |
| 36–107 | Live visual demonstration: synchronised 5-seed steering | README front matter, `assets/hero/` |
| 108–115 | The 53 KB parameter payload | README or 01 |
| 116–164 | Introduction — how I got here | README |
| 165–244 | What I think is actually going on | a standing "current model" page, or README |
| 245–389 | **What is established, and what is not** | **the claims ledger — source of the pending claims** |
| 390–844 | Experiment 1 — the style signature (§1.1–1.7) | **01**, with §1.5 → 07 and §1.6 → 06 |
| 845–1127 | Experiment 2 — attribute emergence (§2.1–2.11) | **02** |
| 1128–1218 | Experiment 3 — subject size, and how blind I was (§3.1–3.2) | **03** |
| 1219–1364 | Where in the model — a first look (§4.1–4.5) | **04**, with §4.5 → 04 or its own page |
| 1365–1575 | One long night — what each test was asking | splits: 00, 04, 10, 11, 12 |
| 1576–1610 | What happens tomorrow | README / roadmap |
| 1611–1730 | Roadmap, priorities 1–8, and Closed | README / roadmap |
| 1731–1757 | How to explore, and how to replicate | README |
| 1758–1762 | Credits, licence, context | README |

The claims ledger at lines 245–389 is a prose bullet list, not a table: **12 bullets under
"Established with reasonable confidence" and 11 under "Not established"**, 23 in total. Several
bullets carry more than one testable statement. That is the population `notebook/_migrating.yaml`
now tracks (written 2026-09-21, see §8); until a validator check reads it, there is still no
mechanical guarantee that a claim has not been published twice.

The "One long night" section is the one that does not map onto a single page: its six
subsections are six different experiments, and three of them (the watermark, the two-knob
composition, Block 6 in the latent) have no page in the eight-page plan at all.

---

## 6. The page map — fifteen pages, not eight

Four ids are already fixed by things on disk and cannot be renumbered without breaking them:
`00` and `05` are live pages, `01-mark-style` and `02-attribute-emergence` are already
registered in `experiments/figures.yaml`, and `assets/03_what_ends_up_in_the_picture/` fixes
`03`. Everything from `06` up is a proposal.

| id | title (working) | stage | material already on disk | what is missing |
|---|---|---|---|---|
| **00** | `00-the-bench` — Is the instrument lying to me? | verification | **live** | — |
| **01** | `01-mark-style` — The style signature | confirmatory (§1.1–1.4 exploratory, §1.3 pre-registered) | old README 390–566, 804–844; `assets/01_steering`, `01_steering_stage7`; F01.1/F01.2 registered | `data/stage7_manifest.csv` **absent**; no figure builder |
| **02** | `02-attribute-emergence` — What the edit puts in the picture | exploratory | **live** (2026-09-21) | filed `ambiguous`; the stage-12 headlight arm would confirm it |
| **03** | `03-what-ends-up-in-the-picture` — Subject size, and how blind I was | confirmatory | **live** (2026-09-21) | the missing sign-scramble control is a declared gap; the two hand-captioned figures in `_figures` stay unpublished (pitfall 40) |
| **04** | `04-where-in-the-model` — Position, displacement, and direction | exploratory | old README 1219–1364; `pilot_rotations_verdict.md`, `mappa_krea2_primo_esito.md`; `data/pilot_*` (8 files, all script-backed) | the §4.5 direction result is filed as hypothesis, not finding — keep that framing |
| **05** | `05-knob-or-cost` — What an edit steers, and what it costs | confirmatory | **live** | its pre-registration file is missing (§0 item 5) |
| **06** | `06-the-hatching-axis` | confirmatory | old README 681–803; `prereg_hatching_axis_stage7.md`, `reproduce_stage7.md`; `data/style_features_stage7.csv`, `confirmation_prompts.csv` | figure builders |
| **07** | `07-chromatic-signatures` | confirmatory, **ambiguous** | old README 567–680; `prereg_chromatic_signatures.md`; `data/palette_*` (6 files) | the "3 of 6 against a bar of 4" verdict must be written as ambiguous, not rounded |
| **08** | `08-block1-vs-block6` | confirmatory | `prereg_rotations_block1_vs_block6.md`, `rotations_block1_vs_block6_results.md`; `data/rotations_block1_vs_block6_*` (6 files) | — |
| **09** | `09-style-direction` | confirmatory, **overturned** | `prereg_stage9_style_direction.md`, `stage9_verdict.md`, `observations_stage9.md`; `data/stage9_coherence_results.csv`, `stage9_centering_sensitivity.csv` | must be typeset exactly like a `holds` page (AUTHORING §3) |
| **10** | `10-block6-in-the-latent` | exploratory | `block6_nel_latente.md`, `block6_e_struttura_gruppi.md`; pitfall 62 | `data/block6_misure_dirette.jsonl` is named by nothing (§3) |
| **11** | `11-the-seed-watermark` | exploratory | `coerenza_traiettoria.md` | `data/coerenza_traiettoria.jsonl`, `coerenza_per_blocco_singolo.jsonl` named by nothing |
| **12** | `12-composition-of-edits` | confirmatory (two frozen predictions) | `previsione_01_composizionalita.md`, `previsione_02_saturazione_direzionale.md`, `regola_angolo_9_coppie.md`, `mappa_completa_sterzo_e_deriva.md`; old README 1471–1520 | `data/composizione_stats.json`, `mappa_sterzo_deriva.jsonl`, `direzioni_*.jsonl` named by nothing; pitfall 61 applies to prediction 02 |
| **13** | `13-the-block-map` | exploratory | `esistono_i_blocchi.md`, `monotonia_profondita_esito.md`, `report_monotonia_profondita.md`, `e_tutto_scrambling.md`, `brief_mappa_esplorativa.md` | `data/mappa_krea2_sweep_summary.csv`, `risultati_monotonia_profondita.json` named by nothing |
| **14** | `14-anima-transposition` | exploratory / **open** | `anima_stage1_results.md`, `anima_stage1_revisione.md`, `anima_dosesweep_verifica.md`, two briefs, `prereg_stage2_corpus_nativo.md` (not run); `docs/model_structures/anima_*` | the cross-architecture test is designed, not run — this page is mostly `open` |

Not pages: the roadmap, the credits, "what happens tomorrow" and "how to replicate" belong in
the generated README; `scope.md` and `errors_log.md` stay where they are.

**Seven of the fifteen pages are confirmatory**, and each needs its pre-registration present
and linked. Six such files exist in `docs/`; the seventh (page 05) does not.

---

## 7. What has to exist before the migration can continue

In dependency order. Items 1–3 block every remaining page; items 4–6 block a specific one.

1. **`experiments/notebook_figures.py` and `experiments/notebook_charts.py`.** Nine non-null `builder` entries across the eleven registered figures name eight distinct
   functions: `knob_vs_cost_scatter`, `depth_profile`,
   `rectification_bars`, `toggle_animation` (×2), `noise_floor_history`, `scale_comparison`,
   `toggle_gif`, `contact_sheet`. None exists. Until they do, no page after 05 can register a
   conforming evidence figure, and the eight existing figures cannot be regenerated. A cheap
   first step that would also close a validator gap: have `validate_notebook.py` check that
   each non-null `builder` resolves to a callable in one of the two modules. That check would
   currently fail on all nine, which is the accurate state of the tree.

2. **`docs/prereg_punto7_simmetria_segno.md`.** The page that cites it is published and its
   status is `holds`. The text appears to survive as a project note dated 2026-09-20 12:48 UTC
   (14:48 Europe/Rome), which matches the deposit time the document itself states (~14:50
   Europe/Rome) and predates the renders it registers. Restoring that text verbatim would make
   the page's claim checkable again. **Left for the author to authorise**, because
   reconstructing the record that underwrites a published confirmatory claim is not a
   janitorial act.

3. **`notebook/_migrating.yaml`.** Twenty-four claim bullets, of which the two live pages
   absorb parts of three. Without the ledger there is no check against double publication, and
   the validator cannot enforce the rule the migration brief states.

4. **`data/stage7_manifest.csv`** — or a decision to repoint F01.1 and F01.2 at
   `data/stage7a_images.csv` / `stage7b_images.csv`. Blocks page 01.

5. **`experiments/extract_repro.py`.** Both live reproducibility blocks were typed by hand.
   One of them already carries `sha256: not recorded`.

6. **A locator function and its qualification run** for any crop on pages 01, 02 and 03. The
   crops that exist today live in `data/figure_crops*.json` as fixed rectangles — the thing
   pitfall 40 is about.

Separately, and not blocking: merge `docs/_pitfalls_64_67_da_inserire.md` into
`errors_log.md`, and remove the two staging files whose contents are already merged.


---

## 8. What changed on the night of 2026-09-21

Three commits on `main`, no push.

| commit | what |
|---|---|
| `4d066c6` | this inventory |
| `ed709c3` | F05.3's alt text published the retracted 12.4× rectification ratio; corrected to 9.1× against `data/punto7_blocks.csv` (13.621680 / 1.495314 = 9.11), in `figures.yaml`, on the page, and in the two `AUTHORING.md` examples that were teaching the wrong number |
| `aadf9fa` | page `02-attribute-emergence`, `experiments/notebook_figures.py` with its first real builder, `experiments/headlights_by_style.py` → `data/stage9_headlights_by_style.csv`, five registered figures under `assets/02-attribute-emergence/` |
| `0ab9261` | `notebook/_migrating.yaml` and this section |
| `4d0fde4` | `docs/report_notte_2026-09-21.md` |
| `f0fb0a2` | page 02 cited pitfalls 8 and 10, which are **rules** 8 and 10. `errors_log.md` carries two numberings — the 15 methodological rules and the 63-entry pitfall registry — and the prose documents reference the first. Corrected to 26, 34, 35, 39, 40, 50, each checked against the registry |
| `93f986e` | page `03-what-ends-up-in-the-picture`, `experiments/notebook_charts.py` with three real builders, `experiments/stage12_enlargement_by_prompt.py` → three derived tables, three registered charts |
| `3a4ea05` | inventory and report updated |
| `d69e29d` | the restored pre-registration of page 05; all eight of its predictions recomputed, P2 corrected from `s` to `m`; the validator now requires the `preregistration` file to exist; self-test 18 → 19 |
| `4b2931f` | the stage-12 headlight round: scored, verified against the sealed key, and reported as unresolvable — 9 styles of 10 never light one |
| `231d850` | pitfalls 64–67 merged; the registry runs 1 to 67 |
| `59392f7` | page `06-the-hatching-axis`, `experiments/stage7_hatching_axis.py` → two derived tables, two registered charts |

`notebook/_migrating.yaml`: 23 original bullets, **9 claims migrated, 16 pending**.

Items closed from §0: item 1 (the ledger exists), item 10 (the alt text), and most of item 3 —
**both** `notebook_figures.py` and `notebook_charts.py` now exist, with four working builders
between them (`barnacle_census`, `enlargement_by_prompt`, `discrimination_rates`,
`discriminability_vs_effect`). Still missing: `extract_repro.py`, and the eight builders the
00 and 05 figures name, which is why those eight figures still cannot be regenerated.

**The order in §6 was inverted deliberately.** The plan was 01 then 02. Page 01 cannot be
written to the contract: its evidence figures in `assets/01_steering/_figures` and
`assets/01_steering_stage7/_figures` sample at RGB (154, 149, 139) — a light theme — and
`AUTHORING.md` §4.4 requires that those be regenerated rather than recoloured, by a generator
that does not exist. `validate_notebook.py` would reject every one of them. Page 02's figures
are already dark and already built from their measurement files, so 02 went first.

**One number that does not reproduce, and it changes a verdict.**
`docs/stage12_verifica.md` §5 reports that the stage-12 primary test fails under the most
defensible statistic — 0.0176 raw, 0.0527 after Holm — and concludes "confirmed with
reservation". Two independent recomputations give **0.0117 raw and 0.0352 after Holm**, which is
also what `data/stage12_bbox_results.csv` has recorded since the round was run, next to its own
verdict of confirmed. All four readings of the statistic pass. Page 03 is therefore filed
`holds` and says so in the open; `data/stage12_enlargement_tests.csv` makes it a one-command
check.

**An arm that was rendered and never examined.** The stage-12 batch is 250 renders across five
conditions and the annotation round covered four. The 50 renders of `preset_pos_1x` were never
scored — and with them the **second confirmatory hypothesis that corpus was built to carry**.
`docs/prereg_stage12_ingrandimento.md` registers a headlight confirmation on those same images,
with its own frozen directional prediction, and no scoring file for it exists in `data/`. It
would turn page 02's ambiguous headlight claim into a confirmed one, on images that already
exist, with no new generation.

**Left for the author, not decided here:**

1. Page 02 is filed `status: ambiguous`, `stage: exploratory`. The contract forbids `holds` on
   an exploratory page, no threshold was frozen before either arm, the barnacle round was
   scored unblinded, and the pre-registered confirmation was never run. That reasoning is
   written into the page. It is still a judgement, and it is the one to overturn first if it
   reads as too severe.
2. Restoring `docs/prereg_punto7_simmetria_segno.md` (§7, item 2).
3. Merging `docs/_pitfalls_64_67_da_inserire.md` into `errors_log.md`, and removing the two
   staging files whose contents are already merged.
4. `.git/_stale_locks/` holds git lock files and temporary objects this session could not
   unlink — the connected folder denies deletion. The directory is inert and safe to delete.
