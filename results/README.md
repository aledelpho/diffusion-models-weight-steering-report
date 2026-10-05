# Knobs inside the weights: single-block scaling in Krea-2 — results

> **Scope.** Everything here is about one model, Krea-2 (28 single-stream transformer blocks),
> edited without training by multiplying the weights of single blocks. It is an investigation
> into whether controllable "knobs" exist inside the weights, not a tool that competes with
> post-production. The exploratory lab notebook that led here is in [`../notebook/`](../notebook/)
> and stays the record of every test run; this folder holds only the results that were
> confirmed, or that the report needs in order to be honest about what was not.

> **New here?** Start from [the story](STORY.md): what we found, told with pictures. This page is the
> report: abstract, related work, and the table of every claim.

## Abstract

Does a text-to-image diffusion transformer hold controllable "knobs" in its own weights —
directions that do one thing, consistently across prompts, seeds and wordings, and can be reached
without training? We study Krea-2, a diffusion transformer with 28 single-stream blocks, edited by
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
family-coherent to the eye, but no metric we tried records that coherence, and one of them can
change a subject's identity. **A preset written by eye from the block map carries over to new
pictures:** calibrated on four character portraits and frozen, it gave three characters it had
never seen the look its author had described, about as coherently as on the four (0.51 against
0.61), and an observer blind to the condition chose it as the closer match in 56 of 56
comparisons; each character stays recognisable, though the face moves slightly more than under a
change of seed (ArcFace 0.74 against 0.80) and a prompted expression can go flat. Rewriting a prompt changes what a block does about as much as
changing the seed, and far less than changing the subject; the pre-registered test of this is
inconclusive by its own rule. We also report four claims that were made from statistics and
withdrawn after the images were opened, and the limits of a study whose eye passes were made by a
single observer who knew the conditions — all except the portrait test, which was judged blind.

## Introduction

The usual ways to steer a diffusion model add something to it: a trained adapter, a learned
direction, a hook on the activations at inference. This project asks whether some control is
already there, in the base weights, at the granularity of a block. The edit is the simplest
possible one: the eight weight matrices of a block are multiplied by one number, and a preset is a
vector of such numbers. Nothing is trained, nothing runs at inference beyond the patched weights,
and any preset can be written down in one line.

What that buys in practice is shown best by the last test. I looked at what every block does to
four drawn characters, wrote a preset of ten small numbers aiming at *a more American-comic look,
flat colours and clean lines*, froze it, and applied it to seven characters at four new seeds.
Three of them had never been rendered while I tuned it. Here they are, base above and preset below:

> **Try it yourself.** The same blind choice, 14 pairs, takes two minutes: [take the test](https://aledelpho.github.io/krea2-weight-knobs-results/try-the-test.html). Take it
> before looking at the pictures below if you can.

![The three characters never seen while the preset was tuned, large, at one seed: each keeps face, hair and costume, while the preset flattens the colour, removes many wrinkle and hatching lines, simplifies the ornament, and turns the tiefling's patterned jacket plain yellow.](../assets/28-portrait-preset/F28.4_portrait_held_out_large.webp)

Someone who had never seen the project, shown each pair side by side without knowing which was
which, picked the preset as the closer match to that description every time, 56 times out of 56.
The characters stay themselves, but not untouched: the face moves a little more than a change of
seed would move it, and a prompted expression can turn into a frown ([page 28](28-portrait-preset.md)).

The project started with hand-calibrated presets over the whole stack
([notebook page 01](../notebook/01-mark-style.md)) and an exploratory notebook of tests on
permutations, rotations and block groups ([notebook](../notebook/)). Single blocks turned out to be
the more useful unit: they are finer than the tuner's macro-blocks, and some of them behave the
same way on every prompt tried. The pages below report what survived confirmation:

* the edit and the instrument, including what the eye pass is and is not ([20](20-method.md));
* a map of the 28 blocks, and a provisional guide to what each one does ([21](21-block-map.md));
* one knob, saturation, confirmed ([22](22-saturation-knob.md));
* presets for a family of prompts ([23](23-prompt-family-presets.md));
* robustness to how the prompt is written ([24](24-wording.md));
* standard metrics on the same images ([25](25-standard-metrics.md));
* a preset made by eye from the map, tested blind on characters it never saw
  ([28](28-portrait-preset.md));
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
in this report; Block Patcher's regex is in fact finer than our per-block vector, reaching one tensor
at a time. Neither tool publishes a map, a dose, or a claim about what any block does: their author
calls them probing tools. **The contribution here is therefore not the edit but its
characterisation** — a measured per-block map with calibrated doses, pre-registered confirmations,
and the failures (`docs/prior_work_block_scaling_tools.md`).

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

## How to read the table below

The four words mean what they mean in the exploratory notebook: **Holds** passed a criterion
fixed before the data; **Ambiguous** was tested and does not decide; **Overturned** was tested
and failed; **Open** was not tested. Every row links to the page that makes the claim, and every
page shows its pre-registration, its data and its reservations.

## What holds and what does not

<!-- CLAIMS:BEGIN -->

| | What | What it rests on |
|---|---|---|
| **Holds** | [Hashed filenames do not hide the condition from an observer who knows the edits, so every eye pass in this report is declared as made with the condition known.](20-method.md#why-the-eye-pass-is-declared-open) | Pre-registered in notebook page 03: four-way forced choice, 17 of 20 and 12 of 20 correct against a 25 percent chance level; 12 of 20 joint hits against a threshold of 5. |
| **Holds** | [The tuner adds nothing of its own at zero, and a render made again days later, in another session and another bench, is the same file pixel for pixel; differences between conditions are therefore the edit and not the pipeline.](20-method.md#the-same-render-twice) | Integrity checks with a pass/fail criterion fixed before the value. Tuner in the graph at zero against no tuner: maximum channel difference 0 on 15 cells (notebook page 00). Before each confirmatory bench of this report, the rows that already existed on older benches were rendered again: 1 of 1 on the wording bench, 26 of 26 on the saturation bench, 1 of 1 on the prompt-family bench, all at maximum difference 0. |
| **Holds** | [Scaling block 23 alone moves the saturation of a Krea-2 picture in one direction, monotonically with the dose and roughly in proportion to it.](22-saturation-knob.md#direction-and-proportion) | Pre-registered. Chroma falls strictly from -0.45 to +0.30 in 15 of 16 prompt-seed cells (threshold 14); doubling the dose from -0.15 to -0.30 multiplies the gain by 1.76 (window 1.6-2.4). On every older render with a blk23 arm, 83 of 83 move chroma the expected way. |
| **Holds** | [Where blk23 reaches the same saturation gain as adding "colorful, vivid highly saturated colors" to the prompt, it leaves the rest of the picture closer to the original than the words do.](22-saturation-knob.md#against-the-words) | Pre-registered on layout r: 6 of 7 scorable cells, median +0.08. Confirmed afterwards with standard metrics: LPIPS 7 of 7, DINOv2 6 of 7. The comparison is possible in 7 of 16 cells only: in the other 9 the words add more saturation than blk23 at its strongest tested dose. |
| **Holds** | [A preset built from late blocks changes different subjects written in the same style in a common direction, clearly more than it does across styles.](23-prompt-family-presets.md#coherence-inside-a-family) | Pre-registered (C49), all four rules supported. Within-family coherence above between-family coherence on 6 of 6 tested arms, median gap +0.19 (threshold 0.10); median within-family coherence 0.53 (threshold 0.40), about 70 percent of the coherence the same arm has across two seeds of one prompt (0.76). Middle-block arms 0.16 (H3, H4). |
| **Holds** | [A block-reordering edit makes the subject take more of the frame, more so at the higher dose, on styles that did not exist when the prediction was frozen.](27-other-edits.md#the-subject-grows) | Pre-registered in notebook page 03: geometric mean area ratio 1.234 across 10 new styles, 9 of 10 above 1, Holm-corrected p 0.018 to 0.035. Whether the structure or the size of the edit causes it is open: the control that separates them was not rendered. |
| **Holds** | [Reordering whole blocks inside the checkpoint crosses the hatching strokes when pushed one way and runs them parallel when pushed the other, and the sign decides which.](27-other-edits.md#the-hatching-axis) | Pre-registered in notebook page 06, on 16 prompts sharing nothing with the corpus of the observation: 16 of 16 prompts and 79 of 80 image pairs in the predicted direction, Holm p 9.2e-5 at the permutation floor. |
| **Holds** | [An observer who did not know which image carried the preset chose it as the one closer to the look its author described, on every sheet.](28-portrait-preset.md#a-blind-observer) | Pre-registered amendment 2 (H4): 56 of 56 sheets, held-out characters 12/12 on the original and 12/12 on the mirrored set (p = 0.0002 each); she named LEFT exactly 28 times and never the same side on both versions of a pair (position check 0/28). One observer. |
| **Holds** | [A preset calibrated by eye on four character portraits changes three characters it never saw in a common direction, about as coherently as it changes the four it was tuned on.](28-portrait-preset.md#the-look-carries-over) | Pre-registered (C52), preset frozen before any test render. Median coherence across the held-out characters 0.51 (threshold 0.40), against 0.61 on the calibration characters (allowed gap 0.15); the preset agrees with itself across seeds at 0.78 (H1, H2). |
| **Ambiguous** | [How much a block rewrites the picture can be read, in part, from the spectra of its own MLP weights, beyond what its depth explains.](21-block-map.md#what-the-weights-show) | Pre-registered (C46). Best Spearman rho 0.615 with depth removed, above the Bonferroni threshold 0.57, so the rule says supported; leaving one block out moves it between 0.50 and 0.70, so a single block can undo it. Correlational, 28 blocks, one checkpoint. |
| **Ambiguous** | [Rewriting a prompt — reordering it, turning it into tags, using synonyms — changes the direction of a block's effect no more than changing the seed does, while changing the subject changes it a great deal.](24-wording.md#the-registered-rule) | Pre-registered (C45), verdict inconclusive by its own rule. Writing against seed, median -0.04 (threshold -0.10): met. Writing more alike than subject on 12 of 12 scored arms (threshold 75 percent): met. Writing more alike than a one-object content change on 0 of 12 (threshold 60 percent): not met. By eye, the same change under every writing on all 24 arms. |
| **Ambiguous** | [A block permutation makes an attribute the prompt asks for, and the model usually drops, appear in almost every render, while a sign scramble moving the weights exactly as far does nothing.](27-other-edits.md#a-curiosity-attributes-that-appear) | Exploratory, scored by me with the condition visible: 19 of 20 seeds against 1 of 20 for the stock model and 1 of 20 for the scramble. One prompt family; the test of generality was designed and never run. |
| **Overturned** | [The family-coherent change the eye saw on the middle blocks is a change of content that a content embedding, DINOv2, would record.](25-standard-metrics.md#a-content-embedding-does-not-see-it) | Pre-registered (H5): supported if the median within-family coherence of the five middle arms on DINOv2 changes reached the style-feature value plus 0.10 (0.26). It is 0.007, below the style-feature value 0.159: refuted. In DINOv2 space no arm is family-coherent (all W at most 0.06). |
| **Overturned** | [The central macro-blocks give way under a push in a different way from the two at the ends of the stack.](26-what-did-not-work.md#the-centre-is-not-special) | Pre-registered primary of the centre-push bench: T = +0.053, p = 0.19 over 495 relabellings, with the range guard passed, so a null and not an inconclusive. Block_5 sits in the centre and gives way hardest of all. |
| **Overturned** | [The difference between how consistent an edit's CLIP direction is on one prompt and on many prompts separates blocks that route meaning from blocks that filter structure.](26-what-did-not-work.md#semantic-routing) | Audit of an unpublished analysis: no script computes its p-values; doses are mixed under one key; the measure tracks how alike the images are; its second-ranked semantic router, blk26 +, lays the same mosaic of colour cells over any content. |
| **Overturned** | [Pushed to dose 0.500, the macro-block sliders Block_4 and Block_1 move the picture far from the baseline while keeping its line work, and are the best operating points found.](26-what-did-not-work.md#the-best-doses-by-the-statistic) | Published from two statistics, then retracted the next day when the renders were opened: Block_4 + at 0.500 leaves no subject, only a crumpled-stroke texture; Block_1 + at 0.500 is colour confetti. Block_4 + is already broken at 0.350. |
| **Overturned** | [Structure coherence, a statistic of oriented line work, can rank edits by how much of the drawing they preserve.](26-what-did-not-work.md#a-measure-with-the-sign-wrong) | Pre-registered eye veto: 7 agreements in 9 resolved pairs against a threshold of 8 in 12. Both disagreements are one condition, Block_6 + 0.080, which the statistic scores above its baseline and which I and six blind model observers call broken; Block_1 - 0.500 is the same case. The sign is wrong, not the size. |
| **Overturned** | [The preset changes a character's face no more than changing the seed does.](28-portrait-preset.md#the-face) | Pre-registered (H3), refuted: on both eligible held-out characters the face under the preset is less similar to the base (ArcFace 0.75 and 0.74) than the base is to itself at another seed (0.82 and 0.75). Described after the test: 0.74 on average against 0.80 for a seed change and 0.29 for two different characters. |
| **Open** | [A provisional, by-eye description of what each of the 28 blocks does in each direction, offered as a starting point for anyone who wants to try the tuner, not as a measured result.](21-block-map.md#a-starting-guide-what-each-block-seems-to-do) | Written by me while looking at the v4 bench (five prompts, one seed) on a page that also showed the 18 prompts of the styles and v3 benches. Where a measurement touches an entry, it agrees on blocks 00, 22, 23 and 27, partly on 01, and the statistic is the suspect on 26. Most Style-band entries have no measurement at all. |
| **Open** | [The blocks at the two ends of the stack change properties of the picture — colour, grain, sharpness — in the same way on every picture; the middle blocks change what is depicted, and differently on each picture.](21-block-map.md#what-the-ends-change-and-what-the-middle-changes) | At one dose for all blocks, a block is recognisable as itself on another picture only at the ends (positive: blocks 0, 1, 25, 26, 27; criteria fixed before measuring, p = 0.0015). The ends keep the layout (0.88 for 21-27) and the middle rewrites it (0.65 for 05-14); middle blocks change the content most by DINOv2 (page 25). Counted in rendering statistics, however, the ends move more of them at once (effective number 9.6 for 21-27 against 7.5 for 05-14), so "fewer things" holds for kinds of property, not for statistics. |
| **Open** | [Blocks near the output keep the composition of the picture and change its surface; the middle of the stack, worst at blocks 8 to 10 pushed positive, rewrites the picture itself.](21-block-map.md#where-the-layout-holds) | Exploratory, 23 prompts on three benches, doses calibrated by eye. Layout r with the baseline 0.88 for blocks 21-27, 0.65 for blocks 05-14; blk09 positive 0.46. Agrees with the pre-registered result of notebook page 05 that the cost of a push grows toward the output. |
| **Open** | [At the same dose, the blocks near the output reach visible artefacts first, while most middle blocks show none; the middle has room before artefacts but drifts toward pictures that are clean and incoherent.](21-block-map.md#how-far-each-block-can-be-pushed) | My artefact labels at dose 0.350, three prompts, one seed: blocks 4 to 11 OK in both directions; positive, strong artefacts on 19, 21, 22, 24 and 25, broken on 26 and 27. Agrees with the pre-registered result that the cost of a push grows toward the output (notebook page 05). The split into hard and soft limits is an observation, not measured. |
| **Open** | [Once the change shared by every edit is removed, blocks 08-10, 15-16 and 23-26 pushed positive change the picture in the same direction, and blocks 22-27 pushed negative do too.](21-block-map.md#blocks-that-push-together) | Groups formed on the 12 styles prompts and found again on 11 prompts of two other benches, with other seeds and other doses (residual correlation +0.15 to +0.37); the group 02-05 did not come back (+0.01 to +0.14). Not pre-registered. |
| **Open** | [Block 9 pushed positive can change the identity of a subject, turning the female blacksmith into a man, and it does so at one seed and not at the other.](23-prompt-family-presets.md#a-change-of-identity) | Eye notes on the oil and photo families at seed 1414213; at seed 5772156 she stays a woman in all three families. CLIPScore on the blacksmith prompts drops by 3.8, the largest drop of any arm. Two seeds, one subject. |
| **Open** | [Late-block presets are most coherent on cartoon prompts, less on oil paintings and least on photographs, where the eye found no common look for two of the arms.](23-prompt-family-presets.md#family-by-family) | Split by family after the test, descriptive: up to 0.80 on cartoon, 0.28-0.71 on oil, 0.12-0.53 on photographs; the eye said no common look for blk20 and blk23 on photographs, where the numbers are 0.29 and 0.12. |
| **Open** | [Middle blocks also give a family a recognisable common change, but it is a change of what is depicted, and no measure used here sees it.](23-prompt-family-presets.md#the-middle-blocks-the-eye-against-the-numbers) | Eye, deposited before the numbers: a common look in 8 of 12 Style-band cells and 2 of 3 blk09 cells. Style features: within-family coherence 0.06-0.17. DINOv2: 0.007, refuted as a substitute (page 25). |
| **Open** | [For an identical vocabulary, the order of the words changes the pose and framing of the picture but not what a block does to it.](24-wording.md#word-order) | Exploratory, one prompt in five orders, two seeds, 56 arms. Consistency across orders tracks consistency across seeds (r = 0.92) and is on average 0.06 higher; median 0.69 on the 43 arms larger than the reordering itself. Baselines of different orders differ by Delta E 16-31. |
| **Open** | [Middle-block edits change the content of the picture more than late-block edits and cost nothing measurable in image quality, while late blocks change less and cost more.](25-standard-metrics.md#depth-against-cost) | Pre-specified descriptive measurement, no decision threshold. DINOv2 similarity to the baseline 0.87 and 0.88 for blk17 + and blk09 +, against 0.90-0.96 for the late arms; BRISQUE -0.5 and -0.3 for those two, +9.6 for blk27 -0.25 and for the combo. |
| **Open** | [The portrait preset can flatten an expression the prompt asks for and remove small details the prompt names, while keeping the character recognisable.](28-portrait-preset.md#what-the-preset-takes-away) | Analyst's look after all numbers, not blind, on seven pairs selected because ArcFace marked them: the gnome's prompted wide-eyed curiosity becomes a frown at three seeds of three; the half-orc's snarl becomes a stern closed face; prompted dirt smudges and chalk dust vanish. No deformation in any of the seven. Untested; block 8 (+0.15) is the first suspect. |

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

Structure, sources and the list of notebook pages that enter the report:
`docs/report_outline.md`.
