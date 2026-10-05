# Report outline — "Knobs inside the weights: single-block scaling in Krea-2"

Draft structure, 2026-10-05. Every claim below points to the document and data that carry it.
Scope: **Krea-2 only** (Anima follows as separate work). Framing agreed with Alessandro: an
**investigation into whether controllable "knobs" exist inside the weights**, not a tool that
competes with post-production. Language of the report: English.

## 0. Abstract (to write last)

Training-free scaling of single transformer blocks of a 12-B-class single-stream DiT; what it
does, what is reproducible, what is not; one confirmed colour knob (blk23), confirmed
family-coherent presets from late blocks, deeper content changes from middle blocks seen by
eye; the evidence standard used (pre-registration, eye-first, pixel-identical controls).

## 1. Introduction

- Question: are there directions in a diffusion model's own weights that behave like knobs —
  consistent across prompts, seeds and wordings?
- Why weights and not activations or adapters: no training, no inference-time hooks, presets
  are a vector of 28 numbers.
- Contributions (each with its section): (a) a per-block map of Krea-2 from 5 000+ renders;
  (b) blk23 as a near-linear saturation knob (§5); (c) prompt-family presets (§6); (d)
  robustness to wording (§7); (e) the method itself and its failure log (§3, §9).

## 2. Related work

- **Block/layer specialisation in diffusion models.** B-LoRA finds two SDXL blocks that
  separate content and style [1]. SAE analysis of SDXL Turbo finds blocks specialised in
  composition, local detail, and colour/illumination/style [2]. Stable Flow finds that "vital
  layers" in DiTs are scattered through the stack, detected by bypassing layers and measuring
  DINOv2 change [3]. FluxSpace edits attributes through representations of transformer
  blocks in rectified-flow models [4]. Our results agree that specialisation exists in a DiT
  and that it is not contiguous (§4).
- **Training-free re-weighting of the backbone.** FreeU rescales U-Net backbone and skip
  features at inference to change output quality [5] — the closest precedent for "scale a
  part of the network, no training".
- **Learned controls.** Concept Sliders train low-rank adaptors as attribute sliders [6];
  weights2weights finds interpretable directions in the space of customised (LoRA) weights [7];
  LoRA Block Weight scales a LoRA's effect per block in practice [8]. Difference: here the base
  weights themselves are scaled; nothing is trained, and the knob is a block, not a learned
  direction.
- **Model.** Krea-2 technical report [9].
- **Metrics.** LPIPS, DISTS, SSIM, BRISQUE, CLIP-IQA [10], CLIPScore, DINOv2.

## 3. Method

- Krea-2 structure: 28 single-stream blocks, 13 tensors each, 8 reachable 2-D
  (`docs/model_structures/`, `normscales_never_applied.md` for the inert 1-D tensors).
- The edit: per-block multiplier 1 + δ through `ArthemyKrea2ModelTuner` (Real Value),
  34-slot vector; doses calibrated by eye per block (`RENDERS_2026-09-30_single_blocks_styles.md`).
- Protocol: exploratory pass by eye → claim written down → pre-registration with decision
  rules and code committed → renders → eye pass deposited → scoring. Reproducibility gate:
  a re-render must be pixel-identical before anything is scored.
- Measures: 23 style features; CIELAB layout/chroma; standard metrics (§8).

## 4. A map of the 28 blocks (exploratory)

- Single-block atlas and styles bench; Alessandro's per-block definitions
  (`data/single_blocks_v4_definitions_alessandro.md`) against measurements
  (`block_groups_and_prompt_order.md` §4).
- Bands: Base (00–01), Style (02–18), Details (19–22), Correction (23–27); stability by
  layout (0.75 / 0.65 / 0.73 / 0.88) — clean at the ends, blurred in the middle.
- Groups that replicate across prompt sets: 08–10, 15–16, 23–26 (+), 22–27 (−); macro-blocks cut
  through them (`block_groups_and_prompt_order.md` §2).
- Weight structure: the split is visible in MLP spectra (C46, marginal)
  (`block_weight_structure_result.md`).
- Figures: atlas strip per block; group matrix; layout-stability by depth.

## 5. A saturation knob: blk23 (C47, confirmatory)

- 83/83 existing images in the expected direction (`blk23_saturation_all.csv`).
- New renders: monotone 15/16, near-linear (×1.76), keeps the picture better than "colorful"
  at matched chroma — layout 6/7, LPIPS 7/7, DINOv2 6/7; reaches the words' saturation in only
  7/16 cells; no measurable quality cost (`blk23_vs_colorful_result.md`,
  `standard_metrics_result.md`).
- Figure: one row per prompt — base, "colorful", blk23 ladder.

## 6. Presets for a prompt family (C49, confirmatory)

- H1–H4 supported: late-block presets coherent within a family (W 0.53 vs B 0.26, seed 0.76);
  cartoon ≫ oil > photo; eye agrees family by family (`prompt_family_result.md`).
- Middle blocks: coherent to the eye, not in style statistics nor DINOv2 (H5 refuted); they
  change content most (DINOv2 0.87–0.88) with no BRISQUE cost, and can change identity
  (blk09 +: the female blacksmith read as a man at one of two seeds in oil and photo, CLIPScore −3.8 on those prompts).
- Cost: late blocks and the combo raise BRISQUE (+9.6 for blk27 −0.25 and combo); blk26's noise
  is seen by eye, not by the metrics.
- Figure: 6 subjects × 3 families for one late block and for blk09.

## 7. Wording does not change what a block does (C45 + prompt order)

- Word order: edit as stable across orders as across seeds (`block_groups_and_prompt_order.md` §3).
- Rewriting (order, tags, synonyms): writing ≈ seed, subject ≫ writing; pre-registered verdict
  inconclusive because a one-object content change disturbs even less (`prompt_writing_result.md`).

## 8. Standard metrics (C50)

Summary table from `standard_metrics_result.md`; where metrics and eye disagree (blk26 noise,
middle-block coherence), say so.

## 9. What did not work, and the error log

- Retractions: Block_4/Block_1 at 0.500 recommended from statistics, destroyed by eye; the
  "semantic routing" CLIP analysis (`semantic_routing_audit.md`); coherence measure discredited.
- Pitfalls 78–90 as method lessons (look at 1:1 before speaking; the statistic is the suspect).

## 10. Limits

One model; single non-blind rater (the author) — all images published; confirmatory samples
small (16–40 cells per test); doses calibrated on single images are too strong for presets;
C45 inconclusive by its own rule; weight-structure result marginal; residual-stream probe not
run; "clean-up later" not tested.

## 11. Outlook

Anima; lower-dose presets and a clean-up pass; a character-consistency test for middle blocks
(below); the residual-stream probe.

## Notebook pages: which enter the report (decided 2026-10-05)

| page | status | edit type | in the report |
|---|---|---|---|
| 00 the bench | holds | — | **§3 Method**: tuner is identity at zero, renders reproduce bit-for-bit across restarts |
| 05 knob or cost | holds, pre-reg. | per-block sign | **§4 and §6**: every push costs fine texture and the cost grows toward the output (r = −0.66 with depth); blk00 is an inverted knob. Agrees with C50 (late blocks cost most) and with Alessandro's blk00 definition |
| 08 Block_1 vs Block_6 | holds, pre-reg. | matched-distance rotations | **§4**: two places pushed the same distance move the image in distinguishable directions — position, not distance |
| 03 what ends up in the picture | holds, pre-reg. | block derangement | **§3 (blinding)** and **appendix A**: subject enlargement replicates on 10 new styles; hashed filenames do not blind an expert eye — the measured reason the eye pass is declared non-blind |
| 06 hatching axis | holds, pre-reg. | block derangement | **appendix A**: the sign of the displacement decides crossed vs parallel hatching, 16/16 prompts |
| 09 style direction | **overturned**, pre-reg. | calibrated whole-stack preset, derangement | **§6 and §9, must be discussed**: an earlier pre-registered test found that a whole-stack preset's direction does *not* follow the style more than the subject. C49 found the opposite for single late blocks. Different edits and designs; the report states both and does not claim to reconcile them |
| 11 what the numbers could not see | open | various | **§9**: displacement statistics cannot tell steering from damage (why eye-first); undeclared colours are the fragile route (9/20 vs 0/20) as an open lead |
| 01 mark style | open, exploratory | 53 KB preset | **§1**, one paragraph: where the project started |
| 02 attribute emergence | ambiguous | permutation | **appendix A, boxed as an observed curiosity** (Alessandro, 2026-10-05): a block permutation made the requested "barnacle-like clusters" appear in 19/20 seeds against 1/20 stock and 1/20 for a norm-matched scramble; lit car headlights — never named in the prompt — went 10/35 → 31/38 under one edit and 0/39 under another. Stated with its weaknesses: a different edit type from single-block scaling; the barnacle round scored by the author with the condition visible; the headlights scored blind but on the renders that produced the observation; the pre-registered confirmation could not resolve (9 of 10 prompts never lit a headlight); one prompt family |
| 07 chromatic signatures | ambiguous | various | one line in §5 at most (small effect, +0.057 vs +0.023) |
| 04 where in the model, 10 all blocks clean | ambiguous / open | block groups, rotations | **left out**: superseded by the single-block atlas |

## Open question raised by Alessandro (2026-10-05), for §6/§11

*Middle blocks (e.g. blk09) are the most valuable: they change the image more deeply, in ways
post-production cannot reproduce — useful for a series of assets with a fixed prompt structure
and style, varying only the subject.* What the data say so far: deeper change at no measured
quality cost (supported, C50); family-coherent to the eye (8/12 Style cells, 2/3 blk09), not to
any metric; but also the least predictable and able to change a subject's identity — a risk for
a series where characters must stay the same. Proposed test (C51): fixed characters across
poses/scenes in one style, middle-block preset on/off; does the identity hold?

## References

1. Frenkel, Vinker, Shamir, Cohen-Or — *Implicit Style-Content Separation using B-LoRA*, ECCV 2024. arXiv:2403.14572
2. Surkov, Wendler, Mari, Terekhov, Deschenaux, West, Gulcehre, Bau — *One-Step is Enough: Sparse Autoencoders for Text-to-Image Diffusion Models* (v1: *Unpacking SDXL Turbo…*). arXiv:2410.22366
3. Avrahami, Patashnik, Fried, Nemchinov, Aberman, Lischinski, Cohen-Or — *Stable Flow: Vital Layers for Training-Free Image Editing*, CVPR 2025. arXiv:2411.14430
4. Dalva, Venkatesh, Yanardag — *FluxSpace: Disentangled Semantic Editing in Rectified Flow Transformers*. arXiv:2412.09611
5. Si, Huang, Jiang, Liu — *FreeU: Free Lunch in Diffusion U-Net*, CVPR 2024. arXiv:2309.11497
6. Gandikota, Materzyńska, Zhou, Torralba, Bau — *Concept Sliders: LoRA Adaptors for Precise Control in Diffusion Models*, ECCV 2024. arXiv:2311.12092
7. Dravid, Gandelsman, Wang, Abdal, Wetzstein, Efros, Aberman — *Interpreting the Weight Space of Customized Diffusion Models* (weights2weights), NeurIPS 2024. arXiv:2406.09413
8. hako-mikan — *sd-webui-lora-block-weight* (software). github.com/hako-mikan/sd-webui-lora-block-weight
9. Lee, Millon, Zhuo, Newton, Filatov, et al. (Krea) — *Krea 2 Technical Report*, 23 June 2026. krea.ai/blog/krea-2-technical-report
10. Wang, Chan, Loy — *Exploring CLIP for Assessing the Look and Feel of Images*, AAAI 2023. arXiv:2207.12396

All references (here and in `results/README.md`, 1-16) checked on 2026-10-05 against the project
pages, publisher pages or paper headers. Corrections made that day: reference 2 has a new title and
two more authors in its current arXiv version; Stable Flow appeared at CVPR 2025; FluxSpace and the
Krea 2 report now carry their authors.
