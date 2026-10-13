# Knobs inside the weights: single-block scaling in Krea-2 — results

> **Scope.** Everything here is about one model, Krea-2 (28 single-stream transformer blocks), edited
> without any training by multiplying the weights of single blocks. It's an investigation into whether
> controllable "knobs" already exist inside the weights — not a tool to compete with post-production. The
> exploratory lab notebook that led here is in [`../notebook/`](../notebook/) and stays the record of
> every test I ran; this folder holds only the results that were confirmed, or that I need here to be
> honest about what wasn't.

> **New here?** Start from [the story](STORY.md): what I found, told with pictures. This page is the
> report: abstract, related work, and the table of every claim.

## Abstract

Does a text-to-image diffusion transformer hold controllable "knobs" in its own weights —
directions that do one thing, consistently across prompts, seeds and wordings, and can be reached
without training? I study Krea-2, a diffusion transformer with 28 single-stream blocks, edited by
multiplying the weight matrices of one block by 1 + d. An exploratory atlas of 1,412 renders (23
prompts, every block in both directions) produced claims that were then frozen and tested on new
benches, each pre-registered with its decision rule and scoring code, opened by a pixel-identical
reproduction check, and scored only after an eye pass had been deposited. **Block 23 is a
saturation knob:** chroma moves monotonically with the dose in 15 of 16 prompt-seed cells, roughly
in proportion to it (doubling the dose multiplies the gain by 1.76), and at the same colour gain it
disturbs the rest of the picture less than adding "colorful" to the prompt (layout 6 of 7 cells,
LPIPS 7 of 7, DINOv2 6 of 7) — although in 9 of 16 cells the words reach further. **Presets built
from late blocks are coherent inside a family of prompts** written in one style: within-family
coherence 0.53 against 0.26 between families and 0.76 across seeds, strongest on cartoon and
weakest on photographs, at a visible cost in noise at the doses used. **Middle blocks change
content most** (DINOv2 similarity 0.87–0.88) at no measured quality cost and look
family-coherent to the eye, but no metric I tried records that coherence, and one of them can
change a subject's identity. **A preset written by eye from the block map carries over to new
pictures:** calibrated on four character portraits and frozen, it gave three characters it had
never seen the look its author had described, about as coherently as on the four (0.51 against
0.61), and an observer blind to the condition chose it as the closer match in 56 of 56
comparisons; each character stays recognisable, though the face moves slightly more than under a
change of seed (ArcFace 0.74 against 0.80) and a prompted expression can go flat. **Inside a block, the two halves differ:** labelled blind, the MLP is the noisier half in 13 of 19 cells and the attention only at the end of the stack; on new comic and cartoon prompts, edits to blocks 1-19 change the picture more than edits to blocks 20-27 and damage its surface in 19% of pairs against 79%, not in none. The fine-texture cost of a push measured earlier replicates on its own comic prompts and was not shown on photographs. **Editing the text encoder instead** (Qwen3-VL-4B, one layer half zeroed or doubled) changes the genre of a picture, and usually who is drawn, rather than its surface; how much the picture changes is predicted by how far the edit moves the conditioning (Spearman 0.71 and 0.80, pre-registered), though mostly by telling kinds of edit apart, but where it goes — anime in 39 of 50 genre switches — is explained neither by less attention on the style words nor by a push resembling the words "anime style"; removing the style words shows the fallback directly — the elf is then drawn as anime in 9 of 9 cases (pre-registered), while seven other characters fall back to painting or realistic renders, so there is no single default — and random pushes of the same size reach it only when they vary from token to token, while each real edit follows its own direction. Rewriting a prompt changes what a block does about as much as
changing the seed, and far less than changing the subject; the pre-registered test of this is
inconclusive by its own rule. I also report four claims that were made from statistics and
withdrawn after the images were opened, and the limits of a study whose eye passes were made by a
single observer who knew the conditions — all except the portrait test, which was judged blind.

## Introduction

The usual ways to steer a diffusion model *add* something to it: a trained adapter, a learned direction, a
hook on the activations at inference. I wanted to know whether some control is already there, hidden in
the base weights, at the scale of a single block. So I used the simplest edit I could think of: the
eight weight matrices of a block multiplied by one number. A preset is just a list of such numbers.
Nothing is trained, nothing runs at inference beyond the patched weights, and any preset fits in one line.

What does that buy you in practice? The last test shows it best. I looked at what every block does to
four drawn characters, wrote a preset of ten small numbers aiming at *a more American-comic look, flat
colours and clean lines*, froze it, and applied it to seven characters at four new seeds. Three of them
had never been rendered while I was tuning it. Here they are, base above and preset below:

> **Try it yourself.** The same blind choice, 14 pairs, takes two minutes: [take the test](https://aledelpho.github.io/krea2-weight-knobs-results/try-the-test.html). Take it
> before looking at the pictures below if you can.

![The three characters never seen while the preset was tuned, large, at one seed: each keeps face, hair and costume, while the preset flattens the colour, removes many wrinkle and hatching lines, simplifies the ornament, and turns the tiefling's patterned jacket plain yellow.](../assets/28-portrait-preset/F28.4_portrait_held_out_large.webp)

Someone who had never seen the project, shown each pair side by side without knowing which was which,
picked the preset as the closer match to that description every single time: 56 out of 56. The characters
stay themselves, but not untouched: the face moves a little more than a change of seed would move it, and
a prompted expression can turn into a frown ([page 28](28-portrait-preset.md)).

Then I turned to the other half of the model, the language model that reads the prompt. The same kind of
edit there doesn't add noise: it changes the *genre* of the picture, and often who is drawn. Where the
picture ends up depends on the edit and on the character — and when I took the style words away, each
character fell back to a style of its own ([page 30](30-the-text-encoder.md)).

I started with hand-calibrated presets over the whole stack ([notebook page 01](../notebook/01-mark-style.md))
and a notebook full of tests on permutations, rotations and block groups ([notebook](../notebook/)).
Single blocks turned out to be the more useful unit: they're finer than the tuner's macro-blocks, and some
of them behave the same way on every prompt I tried. The pages below report what survived confirmation:

* the edit and the instrument, including what the eye pass is and is not ([20](20-method.md));
* a map of the 28 blocks, and a provisional guide to what each one does ([21](21-block-map.md));
* one knob, saturation, confirmed ([22](22-saturation-knob.md));
* presets for a family of prompts ([23](23-prompt-family-presets.md));
* robustness to how the prompt is written ([24](24-wording.md));
* standard metrics on the same images ([25](25-standard-metrics.md));
* a preset made by eye from the map, tested blind on characters it never saw
  ([28](28-portrait-preset.md));
* inside a block: attention against MLP, where the noise sits, and what a middle-block edit costs
  ([29](29-inside-the-block.md));
* the text encoder: how hard an edit pushes the conditioning, and where the picture goes
  ([30](30-the-text-encoder.md));
* what did not work, and the limits ([26](26-what-did-not-work.md)); other kinds of edit
  ([27](27-other-edits.md)).

## Related work

**Layer and block specialisation.** B-LoRA finds two blocks of SDXL that separate content from
style [1]. Sparse autoencoders on SDXL Turbo find blocks specialised in composition, local detail,
and colour, illumination and style [2]. Stable Flow finds that the layers that matter for editing
in diffusion transformers are scattered through the stack, detecting them by bypassing layers and
measuring the DINOv2 change [3]; FluxSpace edits attributes through the representations of
transformer blocks in rectified-flow models [4]. Our map agrees that blocks specialise in a
diffusion transformer and that the specialisation is not contiguous (page 21), but works on the
weights rather than on activations.

**Training-free re-weighting.** FreeU rescales backbone and skip features of a U-Net at inference
to change output quality [5]. It is the closest precedent for scaling part of a network without
training; here the scaling is applied once to the weights of one block of a transformer.

**Learned controls in weight space.** Concept Sliders train low-rank adaptors that act as attribute
sliders [6]; weights2weights finds interpretable directions in the space of customised LoRA
weights [7]; LoRA Block Weight scales a LoRA's effect block by block in practice [8]. Here nothing
is learned and the knob is a block of the base model, not a learned direction.

**The same edit already exists as a tool.** Scaling the base weights of single blocks, training-free,
is what two ComfyUI tools for Flux, published in September 2024 and developed independently of the
tuner used here, already do: the `FluxBlocksBuster` node [17] gives one multiplier
per block, and Block Patcher [18] sweeps a list of regular expressions over the block tensors,
rendering one image per value. Read from their source, both apply exactly the operation studied here
— `W := W x v` through ComfyUI's `add_patches` with `strength_patch = 0` — and so does the tuner used
in this report; Block Patcher's regex is in fact finer than my per-block vector, reaching one tensor
at a time. Neither tool publishes a map, a dose, or a claim about what any block does: their author
calls them probing tools. **The contribution here is therefore not the edit but its
characterisation** — a measured per-block map with calibrated doses, pre-registered confirmations,
and the failures (`docs/prior_work_block_scaling_tools.md`).

**Learned per-block scaling.** Calibri calibrates a diffusion transformer with about a hundred
scaling coefficients — one per block, or one per attention and MLP layer, or one per gate — found by
an evolutionary search against a reward, and reports that the calibrated FLUX, SD-3.5 and Qwen-Image
models are better than the originals [19]. It is the closest published work to this report: the same
kind of edit, a multiplier on part of a block, but searched by a reward model rather than mapped by eye.
Scaling the output projection of an attention or an MLP, as my edits do among others, is close to
scaling that layer's output, which is what Calibri tunes. Calibri does not analyse attention against
MLP or early against late blocks; page 29 does, and finds that they differ.

**Inside the text side.** Knowledge about styles and objects can be localised in the text encoder of a
text-to-image model and edited there [20]; Diffusion Lens reads the intermediate layers of the text
encoder by generating images from them [21]; the per-token text embedding of a diffusion model can be
probed and edited token by token [22]. Where the picture reads each word has been studied through
cross-attention maps in U-Nets [23, 24] and, for dual-stream transformers, through the joint attention
[25]. Page 30 edits the weights of a language-model text encoder and follows the edit into the
conditioning and into the attention of a single-stream transformer, where the methods of [25] do not
apply directly.

**Model and metrics.** Krea-2 is described in its technical report [9]. Image quality and
similarity are measured with CLIP-IQA [10], BRISQUE [11], CLIPScore [12], LPIPS [13], DISTS [14],
SSIM [15] and DINOv2 [16] (page 25).

### References

1. Frenkel, Vinker, Shamir, Cohen-Or. *Implicit Style-Content Separation using B-LoRA.* ECCV 2024. arXiv:2403.14572
2. Surkov, Wendler, Mari, Terekhov, Deschenaux, West, Gulcehre, Bau. *One-Step is Enough: Sparse Autoencoders for Text-to-Image Diffusion Models* (first version titled *Unpacking SDXL Turbo: Interpreting Text-to-Image Models with Sparse Autoencoders*). arXiv:2410.22366
3. Avrahami, Patashnik, Fried, Nemchinov, Aberman, Lischinski, Cohen-Or. *Stable Flow: Vital Layers for Training-Free Image Editing.* CVPR 2025. arXiv:2411.14430
4. Dalva, Venkatesh, Yanardag. *FluxSpace: Disentangled Semantic Editing in Rectified Flow Transformers.* arXiv:2412.09611
5. Si, Huang, Jiang, Liu. *FreeU: Free Lunch in Diffusion U-Net.* CVPR 2024. arXiv:2309.11497
6. Gandikota, Materzyńska, Zhou, Torralba, Bau. *Concept Sliders: LoRA Adaptors for Precise Control in Diffusion Models.* ECCV 2024. arXiv:2311.12092
7. Dravid, Gandelsman, Wang, Abdal, Wetzstein, Efros, Aberman. *Interpreting the Weight Space of Customized Diffusion Models.* NeurIPS 2024. arXiv:2406.09413
8. hako-mikan. *sd-webui-lora-block-weight* (software). github.com/hako-mikan/sd-webui-lora-block-weight
9. Lee, Millon, Zhuo, Newton, Filatov, et al. (Krea). *Krea 2 Technical Report*, 23 June 2026. krea.ai/blog/krea-2-technical-report
10. Wang, Chan, Loy. *Exploring CLIP for Assessing the Look and Feel of Images.* AAAI 2023. arXiv:2207.12396
11. Mittal, Moorthy, Bovik. *No-Reference Image Quality Assessment in the Spatial Domain.* IEEE TIP 2012.
12. Hessel, Holtzman, Forbes, Le Bras, Choi. *CLIPScore: A Reference-free Evaluation Metric for Image Captioning.* EMNLP 2021. arXiv:2104.08718
13. Zhang, Isola, Efros, Shechtman, Wang. *The Unreasonable Effectiveness of Deep Features as a Perceptual Metric.* CVPR 2018. arXiv:1801.03924
14. Ding, Ma, Wang, Simoncelli. *Image Quality Assessment: Unifying Structure and Texture Similarity.* IEEE TPAMI 2022. arXiv:2004.07728
15. Wang, Bovik, Sheikh, Simoncelli. *Image Quality Assessment: From Error Visibility to Structural Similarity.* IEEE TIP 13(4), 2004.
16. Oquab, Darcet, Moutakanni, Vo, Szafraniec, et al. *DINOv2: Learning Robust Visual Features without Supervision.* arXiv:2304.07193
17. cubiq. *FluxBlocksBuster+*, node in *ComfyUI_essentials* (software), `conditioning.py`. github.com/cubiq/ComfyUI_essentials
18. cubiq. *Block_Patcher_ComfyUI — experimental sampler to iterate through blocks weight* (software). github.com/cubiq/Block_Patcher_ComfyUI
19. Tokhchukov, Mirzoeva, Kuznetsov, Sobolev. *Calibri: Enhancing Diffusion Transformers via Parameter-Efficient Calibration.* arXiv:2603.24800, 2026.
20. Basu, Rezaei, Kattakinda, Rossi, Zhao, Morariu, Manjunatha, Feizi. *On Mechanistic Knowledge Localization in Text-to-Image Generative Models.* arXiv:2405.01008
21. Toker, Orgad, Ventura, Arad, Belinkov. *Diffusion Lens: Interpreting Text Encoders in Text-to-Image Pipelines.* ACL 2024. arXiv:2403.05846
22. Yu, Luo, Wang, Zhao. *Uncovering the Text Embedding in Text-to-Image Diffusion Models.* arXiv:2404.01154
23. Hertz, Mokady, Tenenbaum, Aberman, Pritch, Cohen-Or. *Prompt-to-Prompt Image Editing with Cross Attention Control.* ICLR 2023. arXiv:2208.01626
24. Tang, Liu, Pandey, Jiang, Yang, Kumar, Stenetorp, Lin, Ture. *What the DAAM: Interpreting Stable Diffusion Using Cross Attention.* ACL 2023. arXiv:2210.04885
25. Helbling, Meral, Hoover, Yanardag, Chau. *ConceptAttention: Diffusion Transformers Learn Highly Interpretable Features.* arXiv:2502.04320

## How to read the table below

The four words mean what they mean in the exploratory notebook: **Holds** passed a criterion
fixed before the data; **Ambiguous** was tested and does not decide; **Overturned** was tested
and failed; **Open** was not tested. Every row links to the page that makes the claim, and every
page shows its pre-registration, its data and its reservations.

## What holds and what does not

<!-- CLAIMS:BEGIN -->

| | What | What it rests on |
|---|---|---|
| **Holds** | [With the tuner active, a patch that leaves every weight unchanged gives the same image pixel for pixel: the node and ComfyUI's patch path add nothing beyond the multiplication itself.](20-method.md#the-same-render-twice) | Pre-registered (C55), decisive rule fixed before the renders. Block 27's eight bf16 matrices multiplied by 1.0001 (no weight changes after rounding; the tuner reported 8 layers patched): maximum channel difference 0 against a baseline re-rendered in the same session, itself identical to the C47 baseline. Block 27 at +0.0001, which changes only its float32 scales, is also identical, as those parameters never reach the model (notebook page 13). One step of bf16 rounding (block 27 at ±0.004) changes 87-88% of the pixels. |
| **Holds** | [Hashed filenames do not hide the condition from an observer who knows the edits, so every eye pass in this report is declared as made with the condition known.](20-method.md#why-the-eye-pass-is-declared-open) | Pre-registered in notebook page 03: four-way forced choice, 17 of 20 and 12 of 20 correct against a 25 percent chance level; 12 of 20 joint hits against a threshold of 5. |
| **Holds** | [The tuner adds nothing of its own at zero, and a render made again days later, in another session and another bench, is the same file pixel for pixel; differences between conditions are therefore the edit and not the pipeline.](20-method.md#the-same-render-twice) | Integrity checks with a pass/fail criterion fixed before the value. Tuner in the graph at zero against no tuner: maximum channel difference 0 on 15 cells (notebook page 00). Before each confirmatory bench of this report, the rows that already existed on older benches were rendered again: 1 of 1 on the wording bench, 26 of 26 on the saturation bench, 1 of 1 on the prompt-family bench, all at maximum difference 0. |
| **Holds** | [Scaling block 23 alone moves the saturation of a Krea-2 picture in one direction, monotonically with the dose and roughly in proportion to it.](22-saturation-knob.md#direction-and-proportion) | Pre-registered. Chroma falls strictly from -0.45 to +0.30 in 15 of 16 prompt-seed cells (threshold 14); doubling the dose from -0.15 to -0.30 multiplies the gain by 1.76 (window 1.6-2.4). On every older render with a blk23 arm, 83 of 83 move chroma the expected way. |
| **Holds** | [Where blk23 reaches the same saturation gain as adding "colorful, vivid highly saturated colors" to the prompt, it leaves the rest of the picture closer to the original than the words do.](22-saturation-knob.md#against-the-words) | Pre-registered on layout r: 6 of 7 scorable cells, median +0.08. Confirmed afterwards with standard metrics: LPIPS 7 of 7, DINOv2 6 of 7. The comparison is possible in 7 of 16 cells only: in the other 9 the words add more saturation than blk23 at its strongest tested dose. |
| **Holds** | [A preset built from late blocks changes different subjects written in the same style in a common direction, clearly more than it does across styles.](23-prompt-family-presets.md#coherence-inside-a-family) | Pre-registered (C49), all four rules supported. Within-family coherence above between-family coherence on 6 of 6 tested arms, median gap +0.19 (threshold 0.10); median within-family coherence 0.53 (threshold 0.40), about 70 percent of the coherence the same arm has across two seeds of one prompt (0.76). Middle-block arms 0.16 (H3, H4). |
| **Holds** | [A block-reordering edit makes the subject take more of the frame, more so at the higher dose, on styles that did not exist when the prediction was frozen.](27-other-edits.md#the-subject-grows) | Pre-registered in notebook page 03: geometric mean area ratio 1.234 across 10 new styles, 9 of 10 above 1, Holm-corrected p 0.018 to 0.035. Whether the structure or the size of the edit causes it is open: the control that separates them was not rendered. |
| **Holds** | [Reordering whole blocks inside the checkpoint crosses the hatching strokes when pushed one way and runs them parallel when pushed the other, and the sign decides which.](27-other-edits.md#the-hatching-axis) | Pre-registered in notebook page 06, on 16 prompts sharing nothing with the corpus of the observation: 16 of 16 prompts and 79 of 80 image pairs in the predicted direction, Holm p 9.2e-5 at the permutation floor. |
| **Holds** | [An observer who did not know which image carried the preset chose it as the one closer to the look its author described, on every sheet.](28-portrait-preset.md#a-blind-observer) | Pre-registered amendment 2 (H4): 56 of 56 sheets, held-out characters 12/12 on the original and 12/12 on the mirrored set (p = 0.0002 each); she named LEFT exactly 28 times and never the same side on both versions of a pair (position check 0/28). One observer. |
| **Holds** | [A preset calibrated by eye on four character portraits changes three characters it never saw in a common direction, about as coherently as it changes the four it was tuned on.](28-portrait-preset.md#the-look-carries-over) | Pre-registered (C52), preset frozen before any test render. Median coherence across the held-out characters 0.51 (threshold 0.40), against 0.61 on the calibration characters (allowed gap 0.15); the preset agrees with itself across seeds at 0.78 (H1, H2). |
| **Holds** | [Even the middle-block edits chosen because they looked clean carry a visible surface cost on new prompts; the cost is concentrated in a few edits and depends on the prompt.](29-inside-the-block.md#what-the-middle-costs) | Pre-registered (C60) P4: edited-side damage of medium or stronger 0.19 against 0 on the baseline side, Newcombe 95% [0.11, 0.28], above the 0.10 bound for "no detectable cost". Four of the ten edits carry all of it (block 19 MLP + 8 of 9 pairs); six are at 0 of 9. Self-agreement on 15 repeats: 1.00. A follow-up on the six clean edits (C63, four new illustration prompts, 72 pairs) could not decide whether they are free: 4 of 72 damaged against 0, Newcombe [-0.005, 0.134], three of the four from block 9 attention +. |
| **Holds** | [On comic and cartoon prompts, edits to blocks 1-19 change the picture more than edits to blocks 20-27 at the same dose, and damage its surface far less often.](29-inside-the-block.md#form-against-surface) | Pre-registered (C60), new prompts and seeds, blind pairs. Layout r per edit: median 0.72 against 0.84, one-sided Mann-Whitney p = 0.007. Change seen by eye: 1.59 against 0.47 on a 0-2 scale, p = 0.0002 (0.002 with unanswered pairs scored as the most change). Damage of medium or stronger on the edited side: 17 of 90 pairs against 71 of 90; baseline sides 0 of 180. |
| **Holds** | [The style change along the dose is gradual rather than a sudden step (*: pooled over two edits that disagree).](30-the-text-encoder.md#a-dose-ladder) | Pre-registered (C74 H1), pooled over L06 and L14: gradual in 8 of 11 changing strips (0.73, bar 0.6), so the rule says gradual. *Split by edit, the two disagree: L14 is gradual in 6 of 6, L06 is a step in 4 of 5, from comic to photograph around d = 0.80. The split was not pre-registered. No strip changes style below d = 0.70. |
| **Holds** | [Along a dose ladder the intermediate pictures move toward the picture at full dose: the destination is set by the edit, not reached by a detour.](30-the-text-encoder.md#a-dose-ladder) | Pre-registered (C74 H2): yes in 10 of 11 changing strips of L06 and L14 (0.91, bar 0.7). The one "no" is the elf rogue under L06, which passes through a painted look before ending in anime. |
| **Holds** | [Up to the full dose (one MLP of the text encoder doubled), the edits change style and content without breaking the picture: the style moves before coherence is lost, and coherence is not lost at all.](30-the-text-encoder.md#a-dose-ladder) | Pre-registered (C74 H3, amendment 2 fixing what counts as loss of coherence): L06 and L14 MLP on three portraits at two seeds, twelve doses from 0.10 to 1.00. The style changes before coherence is lost in 11 of 11 changing strips (bar 2/3); coherence is marked lost in none of the 18 strips, the L28 control included. One labeller, not blind. |
| **Holds** | [At dose ±1, text-encoder edits change the genre and the content of a picture, usually including who is drawn, while costing less surface quality than a DiT preset.](30-the-text-encoder.md#genre-and-identity-not-surface) | Pre-registered prediction P2 (C65): BRISQUE change -1.52 against +8.09 for the DiT preset of page 28, CLIP-IQA -0.001 against -0.037. Identity (ArcFace, C65) kept for at most 2 eligible characters in 19 of 20 edits. Exploratory eye pass (C64, 140 edits): surface medium or strong in 8 of 140; strong changes 40 of 70 when a half is doubled against 4 of 70 when it is zeroed. |
| **Holds** | [Without its style words, each character falls back to a genre of its own; there is no single default style.](30-the-text-encoder.md#every-character-has-its-own-fallback) | Pre-registered (C73 H1): seven C52 portraits without "Western comics style", four seeds each. Painting for the elf rogue, dragonborn and tiefling, realistic for the half-orc, mixed painting / realistic / 3D for the dwarf, gnome and halfling; anime in 1 of 28. With the style clause all 28 are Western comic. One labeller, not blind. |
| **Holds** | [With its style words removed, the elf character is drawn as anime: anime is the model's fallback for this description when nothing names a style, though not its default for an empty prompt.](30-the-text-encoder.md#the-fallback-is-anime) | Pre-registered (C72 A1): the prompt without "realistic western comics style, bold ink outlines, hatched shadows", five word orders at two seeds, labelled anime in 9 of 9 labelled pictures (one unlabelled; bar 7 of 10). The same prompts with the style words: Western comic in 9 of 9. The empty prompt at four seeds: anime, realistic, anime, painting. One labeller, not blind. C73 found that anime is this prompt's fallback only: seven portraits without "Western comics style" fall back to painting or realistic renders (anime in 1 of 28). |
| **Holds** | [The size of the change a text-encoder edit makes to the conditioning predicts how much the picture changes, without looking at the picture.](30-the-text-encoder.md#the-size-of-the-push) | Pre-registered twice. C67 E1: mean relative change over the words and readings an edit reaches against the eye's "how much it changed" on 140 elf edits, Spearman 0.71 (threshold 0.50); style changed against unchanged, AUC 0.80. C70 G3d: against the mean intensity of change by eye over five word orders, 20 edits, Spearman 0.80 (threshold 0.50); G3, rate of genre switches, 0.73. Exploratory check added after a review: the relation is carried mostly by differences between kinds of edit. Within the MLP-doubled edits, the ones that change genre, it nearly vanishes (C67 material 0.06, n 35, with 28 of 35 already labelled strong; C70 material 0.36, n 11, p 0.28); within the other kinds it stays 0.46-0.66. |
| **Holds** | [Beyond a push shared by the whole prompt, an edit pushes small groups of two to four tokens in their own directions, and the boundaries of those groups follow the commas.](30-the-text-encoder.md#a-shared-push-made-of-small-regions) | Pre-registered (C68), all 12 readings, 241 encodes. Half-life of the residual similarity 3 tokens (median over 20 edits, range 2-5). H1: clauses pushed less alike than whole prompts across orders in 20 of 20 edits (0.54 against 0.97-0.99). H2: at equal distance, tokens of one clause pushed more alike than across clauses in 18 of 20, sign test p = 0.0002. |
| **Holds** | [Inside the image model, the two strongest text-encoder edits move where the picture reads each phrase of the prompt about twice as much as two mild edits.](30-the-text-encoder.md#inside-the-image-model) | Pre-registered (C69 P4), 25 re-renders pixel-identical to the originals: change of the attention maps against the original 0.29 and 0.30 for L06 and L12 MLP doubled, 0.16 and 0.13 for L10 MLP and L19 attention zeroed. |
| **Ambiguous** | [How much a block rewrites the picture can be read, in part, from the spectra of its own MLP weights, beyond what its depth explains.](21-block-map.md#what-the-weights-show) | Pre-registered (C46). Best Spearman rho 0.615 with depth removed, above the Bonferroni threshold 0.57, so the rule says supported; leaving one block out moves it between 0.50 and 0.70, so a single block can undo it. Correlational, 28 blocks, one checkpoint. |
| **Ambiguous** | [Rewriting a prompt — reordering it, turning it into tags, using synonyms — changes the direction of a block's effect no more than changing the seed does, while changing the subject changes it a great deal.](24-wording.md#the-registered-rule) | Pre-registered (C45), verdict inconclusive by its own rule. Writing against seed, median -0.04 (threshold -0.10): met. Writing more alike than subject on 12 of 12 scored arms (threshold 75 percent): met. Writing more alike than a one-object content change on 0 of 12 (threshold 60 percent): not met. By eye, the same change under every writing on all 24 arms. |
| **Ambiguous** | [A block permutation makes an attribute the prompt asks for, and the model usually drops, appear in almost every render, while a sign scramble moving the weights exactly as far does nothing.](27-other-edits.md#a-curiosity-attributes-that-appear) | Exploratory, scored by me with the condition visible: 19 of 20 seeds against 1 of 20 for the stock model and 1 of 20 for the scramble. One prompt family; the test of generality was designed and never run. |
| **Ambiguous** | [The fine-texture cost per block measured in notebook page 05 replicates on new seeds for its own two comic prompts, but does not extend as measured to photographs.](29-inside-the-block.md#the-cost-of-a-push-revisited) | Pre-registered attempt to overturn page 05 (C61): the gate failed (blocks 23-27, G = 0.989, p = 0.26) and the primary was undecided, so by its own rule nothing is decided. On P01 and P02, four new seeds: blocks 1-22 0.989 (page 05: 0.989), blocks 23-27 0.934 (0.932). On two photographs the tail turns into a gain (0.989 overall, block 27 at 1.27). |
| **Ambiguous** | [A random push of the conditioning as large as an edit's changes the genre of the picture as often as the edit does.](30-the-text-encoder.md#random-pushes-of-the-same-size) | Pre-registered (C72 C1-C3, amendment 2: read together). Per-token random pushes switch the genre about as often as the real edits (permuted 11/27, token 10/27, against 14/27; R 0.79 and 0.71, bar 0.5), mostly to anime (15 of 21 switches); the same random vector added to every token switches none (0/27). By the rule fixed before the labels the joint reading is "depends on the form of the push". |
| **Ambiguous** | [The strong edits make the five word orders read the same phrases in more different places than the mild edits do, from the first steps of sampling.](30-the-text-encoder.md#inside-the-image-model) | Pre-registered (C69 P1, P2). P1 holds by its rule with a margin of 0.003, and only L12 MLP doubled raises the divergence (+0.060); L06 does not (-0.004) although its pictures scored as high. P2 holds at step 0 but the separation is not kept at steps 3-6. |
| **Overturned** | [The family-coherent change the eye saw on the middle blocks is a change of content that a content embedding, DINOv2, would record.](25-standard-metrics.md#a-content-embedding-does-not-see-it) | Pre-registered (H5): supported if the median within-family coherence of the five middle arms on DINOv2 changes reached the style-feature value plus 0.10 (0.26). It is 0.007, below the style-feature value 0.159: refuted. In DINOv2 space no arm is family-coherent (all W at most 0.06). |
| **Overturned** | [The central macro-blocks give way under a push in a different way from the two at the ends of the stack.](26-what-did-not-work.md#the-centre-is-not-special) | Pre-registered primary of the centre-push bench: T = +0.053, p = 0.19 over 495 relabellings, with the range guard passed, so a null and not an inconclusive. Block_5 sits in the centre and gives way hardest of all. |
| **Overturned** | [The difference between how consistent an edit's CLIP direction is on one prompt and on many prompts separates blocks that route meaning from blocks that filter structure.](26-what-did-not-work.md#semantic-routing) | Audit of an unpublished analysis: no script computes its p-values; doses are mixed under one key; the measure tracks how alike the images are; its second-ranked semantic router, blk26 +, lays the same mosaic of colour cells over any content. |
| **Overturned** | [Pushed to dose 0.500, the macro-block sliders Block_4 and Block_1 move the picture far from the baseline while keeping its line work, and are the best operating points found.](26-what-did-not-work.md#the-best-doses-by-the-statistic) | Published from two statistics, then retracted the next day when the renders were opened: Block_4 + at 0.500 leaves no subject, only a crumpled-stroke texture; Block_1 + at 0.500 is colour confetti. Block_4 + is already broken at 0.350. |
| **Overturned** | [Structure coherence, a statistic of oriented line work, can rank edits by how much of the drawing they preserve.](26-what-did-not-work.md#a-measure-with-the-sign-wrong) | Pre-registered eye veto: 7 agreements in 9 resolved pairs against a threshold of 8 in 12. Both disagreements are one condition, Block_6 + 0.080, which the statistic scores above its baseline and which I and six blind model observers call broken; Block_1 - 0.500 is the same case. The sign is wrong, not the size. |
| **Overturned** | [The preset changes a character's face no more than changing the seed does.](28-portrait-preset.md#the-face) | Pre-registered (H3), refuted: on both eligible held-out characters the face under the preset is less similar to the base (ArcFace 0.75 and 0.74) than the base is to itself at another seed (0.82 and 0.75). Described after the test: 0.74 on average against 0.80 for a seed change and 0.29 for two different characters. |
| **Overturned** | [A single text-encoder edit moves different comic characters in the same direction, as the DiT preset of page 28 does.](30-the-text-encoder.md#no-common-direction-across-characters) | Pre-registered (C65 H1), refuted: coherent in 4 of 20 edits against a bar of 14; median coherence 0.21 against 0.51 for the DiT preset. Identity (ArcFace) is kept for at most 2 eligible characters in 19 of 20 edits. |
| **Overturned** | [A strong text-encoder edit sends each character to the genre that character falls back to without style words.](30-the-text-encoder.md#every-character-has-its-own-fallback) | Pre-registered (C73 H2), not supported: of 43 switched pictures of the four characters with a clear fallback, 0.28 land on that fallback, against 0.27 expected if destinations ignored the character (bar: +0.20). |
| **Overturned** | [Pictures that leave the Western-comic style are the ones whose image model pays less attention to the words that name the style.](30-the-text-encoder.md#not-less-attention-on-the-style-words) | Pre-registered three times, never supported. C69 P5 (between edits): L06 lowers the style share 0.095 to 0.054, L12 raises it to 0.121. C70 G1 (20 pictures, switched or not): AUC 0.46 (bar 0.70). C70 G1d (intensity 0-3): Spearman +0.05 (bar -0.40). |
| **Overturned** | [The edits that end in anime push the conditioning in the direction that writing "anime style" instead of "western comics style" would.](30-the-text-encoder.md#not-a-text-like-push) | Pre-registered (C71), 16 encodes, gate bit-identical. H1: cosine with the comics-to-anime direction against the number of anime pictures, Spearman -0.01 (bar 0.50). H2: with the anime-minus-painting direction, -0.00 (bar 0.40). Every cosine lies between -0.12 and +0.07. |
| **Open** | [A provisional, by-eye description of what each of the 28 blocks does in each direction, offered as a starting point for anyone who wants to try the tuner, not as a measured result.](21-block-map.md#a-starting-guide-what-each-block-seems-to-do) | Written by me while looking at the v4 bench (five prompts, one seed) on a page that also showed the 18 prompts of the styles and v3 benches. Where a measurement touches an entry, it agrees on blocks 00, 22, 23 and 27, partly on 01, and the statistic is the suspect on 26. Most Style-band entries have no measurement at all. |
| **Open** | [The blocks at the two ends of the stack change properties of the picture — colour, grain, sharpness — in the same way on every picture; the middle blocks change what is depicted, and differently on each picture.](21-block-map.md#what-the-ends-change-and-what-the-middle-changes) | At one dose for all blocks, a block is recognisable as itself on another picture only at the ends (positive: blocks 0, 1, 25, 26, 27; criteria fixed before measuring, p = 0.0015). The ends keep the layout (0.88 for 21-27) and the middle rewrites it (0.65 for 05-14); middle blocks change the content most by DINOv2 (page 25). Counted in rendering statistics, however, the ends move more of them at once (effective number 9.6 for 21-27 against 7.5 for 05-14), so "fewer things" holds for kinds of property, not for statistics. |
| **Open** | [Blocks near the output keep the composition of the picture and change its surface; the middle of the stack, worst at blocks 8 to 10 pushed positive, rewrites the picture itself.](21-block-map.md#where-the-layout-holds) | Exploratory, 23 prompts on three benches, doses calibrated by eye. Layout r with the baseline 0.88 for blocks 21-27, 0.65 for blocks 05-14; blk09 positive 0.46. Agrees with the pre-registered result of notebook page 05 that the cost of a push grows toward the output. |
| **Open** | [At the same dose, the blocks near the output reach visible artefacts first, while most middle blocks show none; the middle has room before artefacts but drifts toward pictures that are clean and incoherent.](21-block-map.md#how-far-each-block-can-be-pushed) | My artefact labels at dose 0.350, three prompts, one seed: blocks 4 to 11 OK in both directions; positive, strong artefacts on 19, 21, 22, 24 and 25, broken on 26 and 27. Agrees with the pre-registered result that the cost of a push grows toward the output (notebook page 05). The split into hard and soft limits is an observation, not measured. |
| **Open** | [Once the change shared by every edit is removed, blocks 08-10, 15-16 and 23-26 pushed positive change the picture in the same direction, and blocks 22-27 pushed negative do too.](21-block-map.md#blocks-that-push-together) | Groups formed on the 12 styles prompts and found again on 11 prompts of two other benches, with other seeds and other doses (residual correlation +0.15 to +0.37); the group 02-05 did not come back (+0.01 to +0.14). Not pre-registered. |
| **Open** | [Against a saturation slider applied to the finished image, block 23 is not a cleaner way to change colour: it also regenerates the picture and changes its lightness contrast. Adding colour it may look more natural than the slider; removing colour the slider looks more natural.](22-saturation-knob.md#against-a-slider-in-post-production) | C53, no new render; slider matched in chroma gain. Layout r 1.00 for the slider against 0.87 and 0.85 for blk23 (16 of 16 cells). Blind forced choice, one observer who knew the renders but not the side: adding colour blk23 chosen 12/16 and 11/16 (rule: 12 on both, not met); removing colour 1/16 and 4/16 (slider). The block also repairs shapes (a half-formed hood), so the choice mixes colour with content. The primary blind observer has not answered yet. |
| **Open** | [Block 9 pushed positive can change the identity of a subject, turning the female blacksmith into a man, and it does so at one seed and not at the other.](23-prompt-family-presets.md#a-change-of-identity) | Eye notes on the oil and photo families at seed 1414213; at seed 5772156 she stays a woman in all three families. CLIPScore on the blacksmith prompts drops by 3.8, the largest drop of any arm. Two seeds, one subject. |
| **Open** | [Late-block presets are most coherent on cartoon prompts, less on oil paintings and least on photographs, where the eye found no common look for two of the arms.](23-prompt-family-presets.md#family-by-family) | Split by family after the test, descriptive: up to 0.80 on cartoon, 0.28-0.71 on oil, 0.12-0.53 on photographs; the eye said no common look for blk20 and blk23 on photographs, where the numbers are 0.29 and 0.12. |
| **Open** | [Middle blocks also give a family a recognisable common change, but it is a change of what is depicted, and no measure used here sees it.](23-prompt-family-presets.md#the-middle-blocks-the-eye-against-the-numbers) | Eye, deposited before the numbers: a common look in 8 of 12 Style-band cells and 2 of 3 blk09 cells. Style features: within-family coherence 0.06-0.17. DINOv2: 0.007, refuted as a substitute (page 25). |
| **Open** | [For an identical vocabulary, the order of the words changes the pose and framing of the picture but not what a block does to it.](24-wording.md#word-order) | Exploratory, one prompt in five orders, two seeds, 56 arms. Consistency across orders tracks consistency across seeds (r = 0.92) and is on average 0.06 higher; median 0.69 on the 43 arms larger than the reordering itself. Baselines of different orders differ by Delta E 16-31. |
| **Open** | [Middle-block edits change the content of the picture more than late-block edits and cost nothing measurable in image quality, while late blocks change less and cost more.](25-standard-metrics.md#depth-against-cost) | Pre-specified descriptive measurement, no decision threshold. DINOv2 similarity to the baseline 0.87 and 0.88 for blk17 + and blk09 +, against 0.90-0.96 for the late arms; BRISQUE -0.5 and -0.3 for those two, +9.6 for blk27 -0.25 and for the combo. |
| **Open** | [The portrait preset can flatten an expression the prompt asks for and remove small details the prompt names, while keeping the character recognisable.](28-portrait-preset.md#what-the-preset-takes-away) | Analyst's look after all numbers, not blind, on seven pairs selected because ArcFace marked them: the gnome's prompted wide-eyed curiosity becomes a frown at three seeds of three; the half-orc's snarl becomes a stern closed face; prompted dirt smudges and chalk dust vanish. No deformation in any of the seven. Untested; block 8 (+0.15) is the first suspect. |
| **Open** | [In the first block the two halves compensate each other: either half lowered alone destroys the picture, while the whole block lowered by the same amount keeps its composition, though not its surface.](29-inside-the-block.md#the-first-block) | C59 at -0.35: attention alone and MLP alone break the image in 9 of 9 cells each by eye; the whole block keeps the layout in 3 of 3 cells (layout r 0.69-0.80 against 0.05-0.36) but is labelled strong blotches blind. The whole block exists at one seed only. |
| **Open** | [Pushed at the same dose, the MLP half of a block is noisier than its attention half in most blocks; the attention adds noise only at the very end of the stack.](29-inside-the-block.md#where-the-noise-sits) | Blind eye pass on the split atlas (C59), one seed, three prompts, one observer: of 19 block-sign cells with noise in either half, the MLP is noisier in 13, the attention in 2, tied in 4 (at medium or stronger: 7, 1, 3). Protocol fixed before the labels, no decision rule. The pre-registered measure of C58 could not decide. |
| **Open** | [When a text-encoder edit makes a Western-comic picture change genre, it lands on anime far more often than on anything else, and only edits that double a layer half do it.](30-the-text-encoder.md#where-the-switches-go) | Described, not tested (C70, one observer, seed 3141592, elf in five word orders). Of 100 edited pictures, 50 changed genre: 39 to anime, 11 to cartoon, none to realistic or painting. None of the four edits that zero a layer half changed genre; 13 of the 16 that double one did, in at least one order. |
| **Open** | [Where a strong text-encoder edit sends the picture depends on the edit's own direction, not only on its size.](30-the-text-encoder.md#random-pushes-of-the-same-size) | Reported, not tested (C72, 9 labelled cells per edit). L28 MLP doubled, the largest push, keeps the Western comic in 9 of 9 while random pushes of its size switch 16 of 18; L05 MLP doubled goes to anime in 9 of 9 while random pushes of its size switch 1 of 18. On seven portraits (C73, 14 pictures per edit): L06 MLP doubled gives realistic renders in 11 of 14, L14 cartoon in 9 of 14, L26 and L28 keep the Western comic in 14 of 14. |
| **Open** | [The first thing a text-encoder edit costs is the character: traits the prompt asks for (the half-orc's tusks, the dwarf's copper hair) and features of the original picture the prompt does not name (skin tone, ears, clothing) change before the style does, or without any style change.](30-the-text-encoder.md#a-dose-ladder) | Reported, not tested (C74, amendment 2, free-text traits, one labeller). In L06 and L14, a prompt trait is lost before the style changes in 5 of 10 strips, at the same dose in 2, after in 3. In the L28 control, which never changes style, traits are lost in 4 of 6 strips. The half-orc loses her tusks (asked) and her ears and grey skin (not named) under L06 by d = 0.70 while still drawn as a comic; under L14 the elf rogue's skin, dark in the original though the prompt names no skin tone, lightens. My notes did not separate asked traits from unnamed ones, and at one seed the original half-orc already shows no tusks. |
| **Open** | [Single phrases of the prompt carry strong priors of their own, and they match what surfaces under edits: a female dwarf with a beard, a uniform drawn as anime.](30-the-text-encoder.md#what-each-phrase-draws-alone) | Described (C72 block B, four seeds, one labeller): "female dwarf" and the full dwarf prompt give a bearded woman in 4 of 4; "uniform" an anime girl in 4 of 4; "realistic western comics style" a bearded cowboy comic in 4 of 4; "female antlered elf brawler" anime in 3 of 4; phrases without a person are mostly realistic (78 of 165). |

<!-- CLAIMS:END -->

## Pages

| page | question |
|---|---|
| [20 · The edit, the instrument, and what a result had to pass](20-method.md) | Does the edit do only what it says, and how honest is the eye? |
| [21 · A map of the 28 blocks](21-block-map.md) | Where in the stack does a single block change what? |
| [22 · One block that turns saturation up and down](22-saturation-knob.md) | Is there a knob that does one thing everywhere? |
| [23 · One preset for a whole family of prompts](23-prompt-family-presets.md) | Does a preset give one look to everything written in one style? |
| [24 · Does the way a prompt is written change what a block does?](24-wording.md) | Does a knob survive rewriting the prompt? |
| [25 · What the standard metrics see, and what they miss](25-standard-metrics.md) | What do the usual metrics say about the same images? |
| [26 · What did not work, and the limits of everything else](26-what-did-not-work.md) | Which claims were lost, how, and what this report cannot say? |
| [27 · Appendix A: other kinds of edit](27-other-edits.md) | What did block reordering and permutation show? |
| [28 · A preset made by eye, tested blind on characters it never saw](28-portrait-preset.md) | Can someone build a preset from the map that works on new pictures? |
| [29 · Inside a block — attention, MLP, and what an edit costs](29-inside-the-block.md) | Do the two halves of a block do different things, and is the noise the price of every push? |
| [30 · The text encoder — how hard it pushes, and where the picture goes](30-the-text-encoder.md) | What do the same edits do to the model that reads the prompt, and why do the pictures go where they go? |

Structure, sources and the list of notebook pages that enter the report:
`docs/report_outline.md`.
