# Pre-registration C66 — which automatic measures reproduce Alessandro's eye on text-encoder edits?

Written 2026-10-12, **before any of these measures is computed** on any image. No new renders: only the 657
images already judged by eye (C64 phase 1, C65 characters, C65 word order). Code: `experiments/metric_validation.py`
(image list, model smoke test, embeddings, rules, self-test), committed with this document.

## Why

Text-encoder edits change genre and content while the surface stays clean (C64, C65). The instruments used so far
measure surface (BRISQUE, CLIP-IQA, the high-frequency ratio) or low-level style statistics (the 23 features), and
the last test showed the latter see a shared colour/contrast shift but not the genre the eye names. Before a new
instrument is used to decide anything about the text encoder, it must reproduce the eye on images already judged.
This is a calibration study: each measure is *validated* or *not validated*; there is no hypothesis about the
model.

## Instruments (fixed now)

| axis | model | use |
|---|---|---|
| style | CSD ViT-L (Somepalli et al., ECCV 2024; HF `tomg-group-umd/CSD-ViT-L`), the embedding the HF image-feature-extraction pipeline returns (first token if it returns tokens) | change vectors and distances |
| content / composition | DINOv2-large (`facebook/dinov2-large`), pooled output | distances |
| genre | CLIP ViT-L/14 zero-shot over 7 classes: western comic, anime, cartoon, oil painting, 3D render, photograph, watercolour | top-1 class |
| prompt traits | VQAScore, `clip-flant5-xl` (t2v_metrics) | P(yes) that a trait of the prompt is in the picture |

Raw CSD cosine is known to fail as an absolute style score on some corpora (arXiv 2605.09030); every CSD test here
uses change vectors or ranks within a set, never an absolute threshold on cosine, and the discrimination-gap
diagnostic of that paper is reported (D).

## Labels (already committed, by Alessandro)

* **C65 characters** (`data/te_characters_eye_joined.csv`): per sheet "same direction" yes / partly / no; per
  character follows / another way; per-character free texts.
* **C65 word order** (`data/te_order_grid_notes_alessandro.csv`): 1–5 "how much it changes with the order", seed
  3141592, 20 edits (originals: 2).
* **C64 phase 1** (`data/te_pilot_phase1_joined.csv`): how much it changed, style changed / unchanged, free notes.
* **Genre labels** are read from the free texts with fixed patterns (`GENRE_RE` in the code: anime|chibi, cartone|
  cartoon|animazione, olio, 3D|render, fotograf|fotorealis, acquerell, fumett); a text counts only if it names
  exactly one class. 145 texts qualify (comic 46, anime 44, cartoon 22, oil 20, 3D 7, photo 6).
* **Lost traits** of the elf are read from the C64 notes with fixed patterns (`ELF_TRAITS`): antlers, eyepatch,
  fur, pauldron, gauntlet, elf ears, tan skin. Positives: renders whose note says the trait was lost; negatives:
  the baseline and renders judged *none* / *slight* whose note does not mention it. "Lowered the arm without the
  gauntlet" is excluded by construction (the gauntlet is on the other arm).

## Rules

| test | measure | rule for *validated* |
|---|---|---|
| T1 | per sheet, median cosine between the 7 characters' CSD change vectors (edit − baseline) vs "same direction" | Spearman ρ ≥ 0.40 **and** AUC (yes vs no) ≥ 0.75 |
| T2 | per character, cosine of its CSD change with the mean change of the other six vs follows / another way | AUC ≥ 0.70 |
| T3 | per edit, CSD dispersion across the five word orders (mean pairwise 1 − cos, minus that of the five originals) vs the 1–5 scores | Spearman ρ ≥ 0.60 (the same with DINOv2 is reported) |
| T4 | CSD distance to the baseline, style *changed* vs *unchanged* (elf) | AUC ≥ 0.70 **and** higher than DINOv2's AUC on the same split |
| T5 | DINOv2 distance to the baseline vs how much it changed (none … strong, elf) | Spearman ρ ≥ 0.50 |
| T6 | CLIP top-1 genre vs the genre named in the note | accuracy ≥ 0.60 **and** ≥ majority-class rate + 0.15 |
| T7 | 1 − VQAScore of the trait, lost vs not (elf; traits with ≥ 3 positives) | AUC pooled within trait ≥ 0.80 |
| D | CSD: mean cosine within the same named genre minus across genres | reported |

A validated measure may be used to decide future text-encoder tests; a measure that is not validated is not used
for decisions. The thresholds are not moved after the run. Alessandro's own repeat agreement (C64: "how much"
7/10 exact; style 7/10; C65 sheets 2 of 3) caps what any measure can reach; it is reported next to each result.

## Order

1. Antigravity, GPU PC: `--smoke` (load the four models, print shapes for 3 images) — if any model cannot be
   loaded, stop: no substitute model is allowed.
2. `--embed` → `data/metric_val_emb.npz`, `metric_val_genre.csv`, `metric_val_vqa.csv`.
3. Claude commits them, then runs `--test` → `data/metric_val_tests.csv`.

## Limits

One observer; labels for T6 and T7 come from free notes that were not written as labels, so they are incomplete
(a trait not mentioned may still be lost). The images are mostly one prompt family (comic fantasy). A measure
validated here is validated for this kind of picture only.

## Planned next (not part of C66)

Measuring the text encoder's output directly — the 12 hidden-state taps Krea-2 reads, token by token — instead of
the images; to be pre-registered separately (C67).
