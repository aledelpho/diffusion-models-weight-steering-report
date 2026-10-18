---
id: 25-standard-metrics
title: What the standard metrics see, and what they miss
status: overturned
stage: confirmatory
date: 2026-10-17
preregistration: docs/prereg_standard_metrics.md
supersedes: []
pitfalls: [90]

corpus:
  renders: 1619
  prompts: 46
  seeds: [2718281, 3141592, 1618033, 4669201, 5772156, 1414213, 1234567, 42, 43, 44]

claims:
  - id: dinov2-sees-the-middle-block-coherence
    status: overturned
    statement: >
      The family-coherent change the eye saw on the middle blocks is a change of content that a
      content embedding, DINOv2, would record.
    evidence: >
      Pre-registered (H5): supported if the median within-family coherence of the five middle
      arms on DINOv2 changes reached the style-feature value plus 0.10 (0.26). It is 0.007,
      below the style-feature value 0.159: refuted. In DINOv2 space no arm is family-coherent
      (all W at most 0.06).
    anchor: "#a-content-embedding-does-not-see-it"
  - id: middle-blocks-go-deeper-at-no-measured-cost
    status: open
    statement: >
      Middle-block edits change the content of the picture more than late-block edits and cost
      nothing measurable in image quality, while late blocks change less and cost more.
    evidence: >
      Pre-specified descriptive measurement, no decision threshold. DINOv2 similarity to the
      baseline 0.87 and 0.88 for blk17 + and blk09 +, against 0.90-0.96 for the late arms;
      BRISQUE -0.5 and -0.3 for those two, +9.6 for blk27 -0.25 and for the combo.
    anchor: "#depth-against-cost"
  - id: vqascore-and-dinov2-track-trait-loss-and-edit-magnitude
    status: holds
    statement: >
      On text-encoder edits, three automatic measures reproduce the eye: VQAScore the loss of
      character traits, CSD-ViT-L how differently five word orders come out, and DINOv2-large how
      much an edit changed the picture.
    evidence: >
      Pre-registered (C66, docs/prereg_metric_validation.md, n = 657 renders): VQAScore
      (clip-flant5-xl) achieves pooled within-trait AUC = 0.885 against visual trait-loss
      annotations (threshold >= 0.80; per-trait AUC 1.000 elf, 0.995 fur, 0.985 antlers,
      0.885 pauldron, 0.830 tan, 0.824 eyepatch, 0.686 gauntlet); word-order dispersion across
      5 orders (T3, registered on CSD-ViT-L) rho = 0.844 (threshold >= 0.60), DINOv2-large
      reported at 0.898; change magnitude (T5, registered on DINOv2-large) rho = 0.661
      (threshold >= 0.50), CSD-ViT-L reported at 0.654. One observer's labels.
    anchor: "#calibrating-metrics-on-text-encoder-edits"
  - id: csd-and-clip-fail-cross-character-coherence-and-style-separation
    status: overturned
    statement: >
      A dedicated style descriptor (CSD-ViT-L) and zero-shot CLIP genre classification
      reproduce cross-character style direction coherence, separate style from content changes
      better than DINOv2, and classify visual genre above 60% accuracy.
    evidence: >
      Pre-registered (C66, docs/prereg_metric_validation.md): 4 of 7 calibration rules failed.
      Cross-character CSD change-vector coherence correlates negatively with eye labels (T1
      rho = -0.482, p = 0.0039, AUC = 0.056 vs threshold >= 0.75; T2 leave-one-out AUC = 0.383
      vs >= 0.70); style-changed AUC on CSD (0.796) does not exceed DINOv2 (0.815, T4);
      zero-shot CLIP ViT-L/14 genre accuracy is 0.593 (86/145), 1 image below the 0.600
      threshold (T6).
    anchor: "#calibrating-metrics-on-text-encoder-edits"
---

# What the standard metrics see, and what they miss

> **Overturned** · 1619 renders · cross-prompt coherence predictions refuted, within-prompt distance and VQAScore trait checks validated
> [← all results](README.md#what-holds-and-what-does-not)

> **The direction I'm chasing.** The results on the other pages rest on my eye and on statistics
> written for this project. A reader will ask what the usual metrics say: image quality, prompt
> adherence, perceptual distance, content similarity, style descriptors, and visual question
> answering. I wanted them on the same images, decided before they were computed.
>
> **What would kill it.** Standard metrics that contradict the published verdicts — or that fail to
> reproduce the eye's calls when calibrated directly against the visual notes.
>
> **Where we are.** On the diffusion transformer (962 renders), they confirm the saturation knob
> against the words and put a price on each preset, but DINOv2 misses cross-prompt family coherence
> (`W = 0.007`). On the text encoder (657 renders, C66), 3 of 7 calibration rules pass: `VQAScore`
> (`clip-flant5-xl`) catches lost character traits (`pooled AUC = 0.885`), and both `DINOv2-large`
> and `CSD-ViT-L` track word-order dispersion (`ρ = 0.898` and `0.844`) and overall change magnitude
> (`ρ = 0.661` and `0.654`). All 4 rules that require separating style from content or measuring
> cross-character direction coherence fail (`T1`, `T2`, `T4`, `T6`).

## In two minutes

No new renders: first, BRISQUE and CLIP-IQA (quality without a reference), CLIPScore (adherence to
the prompt), LPIPS, DISTS and SSIM (distance from the baseline), and DINOv2 cosine (same content as
the baseline) were computed on every image of the three confirmatory DiT benches (962 renders) —
wording, saturation, prompt family. Second, in C66 (`docs/prereg_metric_validation.md`), contrastively
trained style descriptors (`CSD-ViT-L`), `DINOv2-large`, zero-shot `CLIP ViT-L/14` genre
classification, and `VQAScore` (`clip-flant5-xl`) were tested against the pre-existing visual reading
notes across 657 text-encoder renders (`C64`, `C65`, `C72`, `C74`, `C75`).

![Middle blocks change the content most (DINOv2 0.87-0.88) at no BRISQUE cost, while the late blocks and the combined preset change less and cost up to +9.6 BRISQUE.](../assets/25-standard-metrics/F25.1_depth_vs_cost.webp)

Read the figure as two corners. Bottom right: the middle blocks, which move the content most and
leave BRISQUE where it was. Top left: the late blocks and the combined preset, which keep the
content and raise BRISQUE.

## The verdict

On the saturation knob the standard metrics agree with the published verdict: at the same colour
gain, block 23 stays closer to the original than the words "colorful" (LPIPS 7 of 7, DINOv2 6 of
7). On the prompt-family presets they put a price on each arm: the late blocks and the combo cost
up to +9.6 BRISQUE, the middle blocks nothing measurable, while changing the content most. Across
both the DiT and the text encoder, embedding cosine of *difference vectors* across different
subjects (`H5` on DINOv2, `T1` and `T2` on CSD-ViT-L) fails to reproduce what the eye calls "moving
in the same stylistic direction." By contrast, within-character distance from baseline (`T3`
word-order dispersion, `T5` change magnitude) and targeted visual question answering (`T7`
`VQAScore` for specific character traits, `AUC = 0.885`) pass their pre-registered thresholds and
are cleared for automated evaluation.

## Why I might be wrong

* **No-reference quality metrics miss what the eye calls noise.** blk26 +0.15 was judged not
  acceptable in every family by eye and costs +0.4 BRISQUE. A low BRISQUE is not evidence of a
  clean picture.
* **"No measured cost" is not "no cost".** It means these two metrics did not move.
* **The depth-against-cost reading is descriptive.** It was pre-specified as a measurement, with
  no rule that could fail.
* **CLIPScore on the saturation bench is not comparable across conditions.** It was computed
  against each image's own prompt, which for the word conditions includes the added words — a
  defect of the plan, recorded and not interpreted.
* **Difference-vector cosine confounds magnitude with cross-subject coherence.** In `T1` (`ρ = -0.482`),
  an edit that leaves all 7 characters in their original comic style produces small, noisy residual
  vectors (low pairwise cosine), whereas a destructive edit (`L06`, `L12`) pushes every image far
  from its baseline along a shared collapse component even when characters land in different visual
  genres.

## The data

### The saturation knob, again

| measure | blk23 closer to the original than "colorful" at the same chroma gain | median difference |
|---|---|---|
| LPIPS | **7 of 7** scorable cells | −0.10 |
| DINOv2 cosine | **6 of 7** | +0.019 |
| layout r (page 22, pre-registered) | 6 of 7 | +0.08 |

Quality: BRISQUE moves by −0.95 for "colorful", +0.87 for blk23 −0.45 and −3.7 for blk23 +0.30;
CLIP-IQA by at most 0.02 anywhere. The full comparison is on [page 22](22-saturation-knob.md).

### Depth against cost

| arm | ΔBRISQUE (higher = worse) | LPIPS to base | DINOv2 cosine to base | ΔCLIPScore, blacksmith |
|---|---|---|---|---|
| blk23 −0.30 | +3.4 | 0.27 | **0.96** | −0.9 |
| blk26 +0.15 | +0.4 | 0.38 | 0.92 | −0.2 |
| blk16 +0.30 | +3.3 | 0.45 | 0.92 | −1.2 |
| blk20 +0.45 | +5.3 | 0.46 | 0.92 | −1.9 |
| blk27 −0.25 | **+9.6** | 0.46 | 0.93 | −2.2 |
| combo | **+9.6** | 0.49 | 0.90 | −3.0 |
| blk13 −0.45 | −0.2 | 0.43 | 0.95 | −0.2 |
| blk03 +0.40 | +1.7 | 0.45 | 0.93 | −1.1 |
| blk06 +0.45 | +0.8 | 0.49 | 0.91 | −1.0 |
| blk17 +0.40 | −0.5 | 0.50 | **0.87** | −2.4 |
| blk09 +0.45 | −0.3 | **0.53** | **0.88** | **−3.8** |

Medians over 36 images per arm (`data/standard_metrics_summary.csv`). Not every middle block goes
deep: blk13 − stays at 0.95, close to the late blocks. The two that do, blk09 + and blk17 +, are
also the two that lower adherence most on the blacksmith prompts — where blk09 + turned the woman
into a man at one of the two seeds ([page 23](23-prompt-family-presets.md#a-change-of-identity)).

### A content embedding does not see it

H5 asked whether the middle blocks' common change, seen by eye inside each family, would show up
as coherence of DINOv2-embedding changes. Median within-family coherence of the five middle arms:
**0.007** against 0.159 on the style features and a threshold of 0.259. Refuted. In DINOv2 space
no arm is family-coherent, late blocks included (all W ≤ 0.06): the same change, "more realistic",
points one way for a fox and another way for a car in an embedding built around content.

### Wording, in DINOv2 space

A_content_small 0.29 > A_seed 0.22 > A_writing 0.16 ≫ A_subject 0.02: the same ordering as the
style features on [page 24](24-wording.md). The subject dominates; rewriting behaves like the seed.

### Calibrating metrics on text-encoder edits

Before using any automatic metric to judge text-encoder experiments ([page 30](30-the-text-encoder.md)),
C66 (`docs/prereg_metric_validation.md`, `docs/metric_validation_result.md`) tested four candidate
backbones — `CSD-ViT-L` (contrastive style descriptor, `768`-d), `DINOv2-large` (`1024`-d),
zero-shot `CLIP ViT-L/14` (`openai`), and `VQAScore` (`clip-flant5-xl`) — against the human visual
reading tables across 657 already-rendered text-encoder images (`data/metric_val_images.csv`,
`data/metric_val_tests.csv`).

| test | measure | n | value | rule for *validated* | verdict |
|---|---|---:|---|---|---|
| **T1** | Per sheet, median cosine between the 7 characters' CSD change vectors vs "same direction" (`yes` / `partly` / `no`) | 34 | `ρ = -0.482` (`p = 0.0039`), `AUC = 0.056` | `ρ ≥ 0.40` and `AUC ≥ 0.75` | **not validated** |
| **T2** | Per character, cosine of its CSD change with the mean change of the other six vs `follows` / `another way` | 238 | `AUC = 0.383` | `AUC ≥ 0.70` | **not validated** |
| **T3 (CSD)** | Per edit, CSD dispersion across the 5 word orders (minus originals) vs 1–5 visual scores | 20 | `ρ = 0.844` (`p = 0.0`) | `ρ ≥ 0.60` | **validated** |
| **T3 (DINOv2)** | Per edit, DINOv2 dispersion across the 5 word orders vs 1–5 visual scores | 20 | `ρ = 0.898` (`p = 0.0`) | reported | **reported** |
| **T4** | CSD distance to baseline, style `changed` vs `unchanged` (elf, 55 vs 97) | 152 | `AUC(CSD) = 0.796`, `AUC(DINOv2) = 0.815` | `AUC(CSD) ≥ 0.70` and `> AUC(DINOv2)` | **not validated** |
| **T5** | DINOv2 distance to baseline vs ordinal change rating (`none` … `strong`, elf) | 150 | `ρ = 0.661` (`p = 0.0`, `ρ_CSD = 0.654`) | `ρ ≥ 0.50` | **validated** |
| **T6** | CLIP ViT-L/14 zero-shot top-1 genre vs single genre named in the reading notes | 145 | `accuracy = 0.593`, `majority = 0.317` | `accuracy ≥ 0.60` and `≥ 0.467` | **not validated** |
| **T7** | `1 - VQAScore` (`clip-flant5-xl`) of the trait question, trait lost vs retained (elf) | 153 | `pooled AUC = 0.885` (78 lost) | `pooled AUC ≥ 0.80` | **validated** |
| **D** | CSD discrimination gap: mean cosine within the same named genre minus across genres | 145 | `gap = +0.2070` | reported | **reported** |

Across the seven character traits annotated on the 153 elf images (`data/metric_val_vqa.csv`),
`VQAScore` (`clip-flant5-xl`) separates trait loss from retention with a pooled within-trait AUC of
**`0.885`** (`data/metric_val_tests.csv`):

| trait | question (`clip-flant5-xl`) | lost (`n`) | within-trait AUC |
|---|---|---:|---:|
| `elf` | `"pointed elf ears"` | 4 | `1.000` |
| `fur` | `"a fur collar"` | 11 | `0.995` |
| `antlers` | `"a small pair of pale antlers"` | 17 | `0.985` |
| `pauldron` | `"a gold wood-textured pauldron"` | 14 | `0.885` |
| `tan` | `"tan sun-kissed skin"` | 7 | `0.830` |
| `eyepatch` | `"an eyepatch over one eye"` | 14 | `0.824` |
| `gauntlet` | `"a heavy silver gauntlet"` | 11 | `0.686` |
| **pooled** | — | **78** | **`0.885`** |

`T4` failed although `CSD-ViT-L` reaches `AUC = 0.796` on style changes, because `DINOv2-large`
reaches `0.815`. A likely reason, not tested: text-encoder edits that shift the style also change the
character's pose and accessories ([page 30](30-the-text-encoder.md)), which a content embedding sees. And in
`T6`, zero-shot `CLIP ViT-L/14` matched 86 of 145 single-genre notes (`0.593`, vs `0.317` majority
baseline), missing the pre-registered `0.600` threshold (`87/145`) by a single image (`data/metric_val_genre.csv`).

### Reproducing this

```yaml
model:
  checkpoint: krea2_turbo_bf16.safetensors
  weight_dtype: default
  sha256: not recorded — the file is outside the repository
sampling:
  sampler: euler_ancestral
  steps: 9
  cfg: 1.0
  denoise: 1.0
  scheduler: simple
  resolution: 1024x1280
  vae: qwen_image_vae.safetensors
  text_encoder: qwen3vl_4b_bf16.safetensors (CLIPLoader type krea2)
tuner:
  node: ArthemyKrea2ModelTuner, after ArthemyKrea2ResetPatcher
  version: not recorded — the tuner is a separate repository
  mode: Real Value, driven by a 34-slot vectors_override
prompts:
  files: [data/prompt_writing_plan.csv, data/blk23_colorful_plan.csv, data/prompt_family_plan.csv, data/metric_val_images.csv]
seeds: [2718281, 3141592, 1618033, 4669201, 5772156, 1414213, 1234567, 42, 43, 44]
conditions:
  - name: every condition of the three DiT benches and five TE benches, as listed on pages 22, 23, 24 and 30
    measured_D: not measured; the doses are per-block or per-layer gains, not calibrated displacements
outputs:
  folders: [benchmark_prompt_writing, benchmark_blk23_colorful, benchmark_prompt_family, benchmark_te_sweep, benchmark_te_pilot_2b, benchmark_te_word_order, benchmark_te_mlp_Continue, benchmark_te_surgical]
  manifest: data/standard_metrics_c45.csv, data/standard_metrics_c47.csv, data/standard_metrics_c49.csv, data/metric_val_images.csv
analysis:
  scripts:
    - experiments/standard_metrics.py           # 744fc3854a7b6a6be4b3ca95cacd54f2337d3ba3521119eb82d0936a3195c245 (GPU, piq + open_clip + DINOv2 ViT-B/14)
    - experiments/analyze_standard_metrics.py   # eb36aa06bca4a9db9a4537cb3a30e34a29975ed4b9c3af13d587322bfa83d08c
    - experiments/metric_validation.py          # ddeecc8e508264df1fde9832d67876b16a3a6c06c9d8ad8d0a35d64aba48d3ad (CSD-ViT-L + DINOv2-large + CLIP ViT-L/14 + VQAScore clip-flant5-xl)
  produces: data/standard_metrics_summary.csv, data/metric_val_tests.csv, data/metric_val_vqa.csv, data/metric_val_genre.csv
```

## Provenance

* **Renders.** benchmark_prompt_writing (401), benchmark_blk23_colorful (128), benchmark_prompt_family (433), metric_validation_te_corpus (657).
* **Pre-registration:** `docs/prereg_standard_metrics.md` and `docs/prereg_metric_validation.md`, written before any of the metrics was computed on these images.
* **Result document:** `docs/standard_metrics_result.md` and `docs/metric_validation_result.md`.
* **Data:** `data/standard_metrics_c45.csv`, `data/standard_metrics_c47.csv`,
  `data/standard_metrics_c49.csv`, `data/standard_metrics_summary.csv`, `data/metric_val_images.csv`,
  `data/metric_val_tests.csv`, `data/metric_val_vqa.csv`, `data/metric_val_genre.csv`.
* **Run notes:** `docs/RENDERS_2026-10-05_standard_metrics.md`.
