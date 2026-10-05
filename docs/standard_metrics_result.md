# C50 result — standard metrics confirm blk23 against "colorful", price the presets, and do not see the middle blocks' coherence

2026-10-05. Pre-registration `prereg_standard_metrics.md`; code `standard_metrics.py` (run by
Antigravity on the GPU, commit aa6122d) and `analyze_standard_metrics.py` (unchanged since
aa8fed1). All numbers: `data/standard_metrics_summary.csv`.

## C47 — blk23 against "colorful"

- **M1, at the same chroma gain:** blk23 is closer to the baseline than the words by **LPIPS
  in 7/7** scorable cells (median −0.10) and by **DINOv2 in 6/7** (median +0.019). Same answer as
  the layout measure (6/7): the standard metrics confirm T1.
- **M2, quality:** BRISQUE moves little (words −0.95, blk23 −0.45 +0.87, blk23 +0.30 −3.7);
  CLIP-IQA changes by ≤ 0.02 everywhere. blk23 does not cost measurable quality at these doses.
- *Defect found in the pre-registered design:* CLIPScore was computed against each image's own
  prompt, which for the text conditions includes the added words. CLIPScore changes for
  `txtpos`/`txtneg` are therefore not comparable with the blk23 ones and are not interpreted.

## C49 — what each preset costs, and how deep it goes

| arm | ΔBRISQUE (↑ worse) | LPIPS to base | DINOv2 cos to base | ΔCLIPScore, blacksmith prompts |
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

- **The middle blocks change the picture most deeply at no measured quality cost.** blk09 + and
  blk17 + have the lowest DINOv2 similarity to the baseline (content changed most) and the
  highest LPIPS, with BRISQUE unchanged or slightly better. The late blocks change less and
  cost more (blk27 −0.25 and the combo +9.6 BRISQUE).
- **blk09 + lowers prompt adherence most on the blacksmith prompts (−3.8 CLIPScore)**, where the
  eye saw the woman become a man: the number agrees with the observation.
- blk26 +0.15: the eye judged its noise unacceptable; BRISQUE (+0.4) and CLIP-IQA do not see it.
  On that point the no-reference metrics are not a substitute for looking.

## H5 — refuted

Median within-family coherence of the middle arms on DINOv2-embedding changes: **0.007**, against
0.159 on the style features. DINOv2 does not see the family-coherent change the eye saw; in
DINOv2 space no arm is family-coherent (all W ≤ 0.06), because the same change ("more realistic")
points in different directions for a fox and for a car in a content-centred embedding. The
middle blocks' coherence remains an eye-only observation.

## C45 on DINOv2 (descriptive)

A_content_small 0.29 > A_seed 0.22 > A_writing 0.16 ≫ A_subject 0.02 — the same ordering as the
style features: the subject dominates, the writing behaves like the seed, a one-object content
change disturbs least.
