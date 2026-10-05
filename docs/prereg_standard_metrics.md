# Pre-registration C50 — standard metrics on C45, C47, C49

Written 2026-10-05, before any of these metrics was computed on these images. Requested by
Alessandro for the report (objection 5). Code: `experiments/standard_metrics.py` (runs on the
GPU PC), `experiments/analyze_standard_metrics.py` (scoring, tested on synthetic data).
No new renders.

## Metrics (per image, 512×640 unless stated)

| metric | what it measures | direction | implementation |
|---|---|---|---|
| BRISQUE | no-reference quality (natural-scene statistics) | lower = better | `piq.brisque` |
| CLIP-IQA | no-reference quality ("good"/"bad photo" prompts) | higher = better | `piq.CLIPIQA` |
| colourfulness | Hasler–Süsstrunk | — | numpy, full image |
| CLIPScore | adherence to the prompt text | higher = closer | open_clip ViT-B-32 laion2b; text truncated at 77 tokens |
| LPIPS, DISTS | perceptual distance from the baseline | lower = closer | `piq` |
| SSIM | structural similarity to the baseline | higher = closer | `piq.ssim` |
| DINOv2 cosine | same content as the baseline (self-supervised features) | higher = closer | ViT-B/14 CLS, 224×280 |

FID/KID are not used: they compare distributions and need thousands of images per condition.

## What is computed (all in `data/standard_metrics_summary.csv`)

**C47 (blk23 vs "colorful").**
- *M1*: the T1 comparison of `blk23_vs_colorful_result.md` repeated with LPIPS and with
  DINOv2 cosine in place of layout r: at the chroma gain of the words, interpolated along the
  blk23 ladder, which is closer to the baseline? Reported as wins / scorable cells.
- *M2*: median change against the baseline of BRISQUE, CLIP-IQA and CLIPScore for "colorful",
  blk23 −0.45, "muted" and blk23 +0.30.

**C49 (presets per family).**
- *Q*: per arm, median change of BRISQUE, CLIP-IQA, CLIPScore; median LPIPS and DINOv2 cosine;
  CLIPScore change on the six blacksmith prompts alone (does blk09 + lower adherence where it
  turns the woman into a man?).
- *H5 (prediction)*: the eye saw a family-coherent change on the middle blocks that the style
  features did not (`prompt_family_result.md` §3). If DINOv2 captures that content change, the
  median within-family coherence W of the five middle arms (blk09 +, blk03 +, blk06 +,
  blk13 −, blk17 +) computed on DINOv2-embedding changes is ≥ the style-feature value
  (0.159) + 0.10 → supported; ≤ 0.159 → refuted; otherwise inconclusive.

**C45 (writing).** A_writing, A_content_small, A_subject, A_seed recomputed on DINOv2-embedding
changes (descriptive: does the ordering seed ≈ writing, subject ≫ writing hold in a content
space?).

Nothing here changes a verdict already published; any disagreement with them is reported.
