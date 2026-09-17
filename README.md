# Weight-Space Steering in Diffusion Models: A Public Lab Notebook

> **Status & Framing**: This is an **open, public lab notebook**. It records real experiments, working hypotheses, and the raw findings gathered so far on **Krea-2 DiT (28 blocks)**.  
> The next step is a formal cross-architecture replication on [`circlestone-labs/Anima`](https://huggingface.co/circlestone-labs/Anima) (which is built on Cosmos-Predict2 with a Qwen3 0.6B text encoder, offering a true cross-family test). Everything here is shared openly to be inspected, reproduced and challenged.

<p align="center">
  <a href="index.html"><strong> Read Full Lab Notebook</strong></a> •
  <a href="viewer/viewer.html"><strong> Launch Interactive A/B Viewer</strong></a> •
  <a href="docs/errors_log.md"><strong> 33 Pitfalls Checklist</strong></a> •
  <a href="data/"><strong> Raw Datasets</strong></a>
</p>

---

## ✦ Live Visual Demonstration: Synchronized 5-Seed Steering

While experimenting with [**Arthemy-Krea2-Tuner**](https://github.com/aledelpho/comfyui-arthemy-krea2-tuner), I wanted to see if manipulating internal weights directly could predictably guide how a model draws — without retraining, without LoRAs, and without touching the prompt.

Below, you can see the **exact same 5 random seeds** (`4242145`, `42`, `1337`, `777`, `9999`) rendered across different weight configurations, all matched to the exact same Frobenius displacement ($D = 0.0538$):

> **Every figure below carries the prompt that produced it.** The prompt text is never edited between conditions — `prompt_sha1`, the first ten hex characters of its SHA-1, is how that is enforced and checked, and it is also the folder name under [`assets/`](assets/01_steering/). The complete list of all 24 prompts with their hashes is in [`data/prompts.json`](data/prompts.json).

### Subject 1: Sea-touched Siren (Cyan & Teal Rim Light)
<p align="center">
  <img src="assets/hero/5seed_timelapse.gif" alt="Sea-touched Siren 5-Seed Steering" width="100%">
</p>

<details>
<summary><code>G1</code> · <code>seatouched_teal</code> · <code>prompt_sha1 30de058455</code> — <strong>show the exact prompt</strong></summary>

```text
Western comics style, bold ink outlines, hatched shadows, hard teal-tinted rim light glowing along the edges of her face, seductive simmering menace, seen from an extreme tilted low angle with her chin raised, extreme close-up on the head only, tight framing, sharp dutch angle. ageless female sea-touched woman, long dark hair fanning as if suspended in water, thin webbed fin-like ridges tracing along her temple, cyan skin, sharply arched eyebrows, a narrow straight nose, wide teal eyes with slitted pupils half-lidded in cold allure, full lips curled in a knowing smirk, small barnacle-like clusters studding one earlobe, faint iridescent sheen along her jawline. white background, simple background, teal overall hue, monochromatic teal.
```

</details>

<details>
<summary><strong> Subject 2: Goblin with Sly Grin (Yellow Rim Light)</strong> — Click to expand 5-seed animation</summary>
<p align="center">
  <img src="assets/hero/5seed_goblin.gif" alt="Goblin 5-Seed Steering" width="100%">
</p>

<details>
<summary><code>G2</code> · <code>goblin_yellow</code> · <code>prompt_sha1 c6a4015aae</code> — <strong>show the exact prompt</strong></summary>

```text
Western comics style, bold ink outlines, hatched shadows, hard yellow-tinted rim light glowing along the edges of his face, sly calculating grin, seen from an extreme low tilted angle looking sharply up his chin, extreme close-up on the head only, tight framing, steep dutch angle. middle-aged male goblin, mottled olive-green skin, greasy tufts of black hair slicked into a lopsided topknot, one eyebrow arched high in shrewd amusement, small beady yellow eyes darting sideways, a long hooked nose with a slight downward curve, wide crooked grin showing several missing teeth, a small brass loop pierced through one nostril, thin wispy chin-whiskers braided into a point. white background, simple background, yellow overall hue, monochromatic yellow.
```

</details>
</details>

<details>
<summary><strong> Subject 3: Barbarian / Half-Orc in Screaming Rage (Red Rim Light)</strong> — Click to expand 5-seed animation</summary>
<p align="center">
  <img src="assets/hero/5seed_barbarian.gif" alt="Barbarian Half-Orc 5-Seed Steering" width="100%">
</p>

<details>
<summary><code>F1</code> · <code>halforc_red</code> · <code>prompt_sha1 7e8536f9bb</code> — <strong>show the exact prompt</strong></summary>

```text
Western comics style, bold ink outlines, hatched shadows, hard red-tinted rim light glowing along the edges of her face, ferocious screaming rage, seen from a steep low angle, extreme close-up on the head only, tight framing, dutch angle, sharp perspective. female half-orc, head thrown back with a wild tangle of black hair across her face, thick furrowed eyebrows pressed low in fury, wide crimson eyes wide with screaming rage, mouth stretched open in a full-throated roar baring a single sharp lower tusk, a thick iron ring pierced through the nose bridge, ferociously screaming expression. white background, simple background.
```

</details>
</details>

<details>
<summary><strong> Subject 4: Ancient Hag with Manic Determination (Chartreuse Rim Light)</strong> — Click to expand 5-seed animation</summary>
<p align="center">
  <img src="assets/hero/5seed_hag.gif" alt="Hag 5-Seed Steering" width="100%">
</p>

<details>
<summary><code>G4</code> · <code>hag_chartreuse</code> · <code>prompt_sha1 95acba3b41</code> — <strong>show the exact prompt</strong></summary>

```text
Western comics style, bold ink outlines, hatched shadows, hard chartreuse-tinted rim light glowing along the edges of her face, wild-eyed manic determination, seen from an extreme low angle shot through an imagined gap between her chin and chest, extreme close-up on the head only, tight framing, sharply canted dutch angle. very old female hag, deep umber-brown weathered skin, wild frizzed grey hair sticking straight up as if charged with static, an exaggeratedly long hooked nose nearly touching her upturned chin, small sunken eyes blazing wide with fevered focus, sagging jowls trembling around a muttering open mouth, three long grey chin-hairs twisted into tiny braids, a single large hoop stretching one earlobe low. white background, simple background, chartreuse overall hue, monochromatic chartreuse.
```

</details>
</details>

---

## 💡 The 53 KB Parameter Payload

> **Can 53 KB steer a 12.8 Billion parameter model?**  
> In diffusion models, we are used to thinking that changing style requires either fine-tuning the model or loading multi-megabyte (or gigabyte) LoRAs.  
> The presets tested here are tiny **53 KB** parameter deltas — just a lightweight configuration of calibrated block gains and Lie algebra rotations. Yet, as you can see across all seeds, they steer the visual rendering with remarkable consistency.

---

## Introduction — how I got here

Two years ago, as Arthemy, my workflow for training models looked like this. Download a model plus
a few fine-tunes with aesthetics close to what I wanted, then block-merge them at different
strengths per block until I landed on something near the look I had in mind. Alongside that, train
extremely narrow concept LoRAs and distil them as hard as I could: activate only specific sections,
train five of them, keep only what they had in common to squeeze the scope down further, then inject
the result back into the model.

At some point I started playing with values that are not supposed to be used. The question was
simple: instead of sliding between 0.0 and 1.0, what happens if I force a value below zero, or above
one? What came out was an amplification of one model's magnitude — but always *relative to a second
model*, because that is what a merge is.

That is when I started wondering whether the same block-merge operations could work with **one model
alone**. Amplify or attenuate some of its own sections mathematically, and see how the output
changes. My SDXL tool, [Arthemy Live-Tuner](https://github.com/aledelpho/Arthemy_Live-Tuner-SDXL-ComfyUI),
is the evidence of that first attempt — a prototype, and not much to look at, but the principle was
already there.

Those experiments convinced me that amplifying or attenuating distinct parts of a model changes its
style *coherently* rather than randomly: a direct, predictable manipulation of a probabilistic
system.

Only recently did two things sink in. The first is that the tooling for this does not exist.
Block-weighted merging is well covered — [supermerger](https://github.com/hako-mikan/sd-webui-supermerger),
Merge Block Weighted, [ComfyUI's native merge nodes](https://comfyanonymous.github.io/ComfyUI_examples/model_merging/)
— but every one of them needs at least two checkpoints: the knob mixes model A into model B, block
by block. [LoRA Block Weight](https://www.runcomfy.com/comfyui-nodes/ComfyUI-LoraBlockWeight) does the
same for an adapter's delta, and task arithmetic scales a task vector, which again presupposes a
fine-tune to difference against. What none of them does is operate on a **single** checkpoint with
nothing to mix it with, amplifying or attenuating a model's own sections against themselves. The
only public tools I could find that do that are ones I wrote myself.

The operation is arithmetically trivial — scale a block's weights by α. That is probably *why*
nobody wrote it up. What is not trivial, and what this notebook is about, is that the trivial
operation produces a coherent stylistic direction instead of degradation.

Which is the second thing that sank in: **none of what I was doing had ever been demonstrated
properly.** I had observed it on my own screen, repeatedly, and that is not the same as showing it.
So I decided to push the intuition until it breaks. At best it becomes a usable way to change a
model's style with no fine-tuning and no LoRA, from a configuration file under 100 KB.

This repository is the diary of that work, kept in the open: real experiments, working hypotheses,
and the raw data collected so far — including the failed attempts and the predictions that turned
out wrong, because those are as much a part of the story as the results that held.

---

## What is established, and what is not

**Two experiments, fifteen analyses, and one confirmation round.** That distinction matters more than it
sounds, so it is stated here rather than buried. Sections 1.1 to 1.4 rest on **1272 renders** across 24
prompts; every table there about stroke morphology, colour, PCA and CLIP is a *different measurement of that
same corpus*, not an independent replication. Experiment 2 rests on a separate corpus of **390 renders**.
Anyone counting "five experiments" from the section headings would be counting measurements.

Sections 1.5 and 1.6 are the exception, and they are the reason this page changed in September. Their
thresholds were **written down before the renders existed**, and they were tested on **560 new renders across
16 prompts sharing nothing with any earlier stage**. One of the two came back weaker than its exploratory
estimate and is reported as ambiguous; the other came back at full strength. Both outcomes are below.

**Established with reasonable confidence:**

* A tiny weight perturbation — 53 KB, calibrated by hand — shifts the mark style of a 12.8-billion-parameter
  diffusion model (Krea-2 DiT) coherently and repeatably across different seeds.
* This is **not** "the further you move from the checkpoint, the more the style changes". Controls at
  exactly the same Frobenius displacement but without the calibrated structure — block derangement,
  random sign flips — do not produce the same result. The direction matters, not just the distance.
* The standard instrument in this field (CLIP at 224×224) is blind to this kind of change, because it
  downsamples the image before looking at it and the stroke detail does not survive. Measured directly
  on mark morphology instead, the effect is statistically solid and replicates over 24 prompts.
* The mark-style effect generalises beyond the prompt it was found on (24 prompts tested, with a
  generalisation criterion declared in advance and met).
* The colour effect does **not** generalise: it is present only where the prompt pins the palette in
  detail, and vanishes when the model is free to choose the palette itself.
* A norm-matched block permutation moves a neglected prompt attribute from 1/20 to 19/20 — but only
  where the prompt already binds it, and randsign at the identical displacement does nothing at all.
* **Different weight edits move colour in directions that differ from one another.** Confirmed twice, on
  independent corpora, at the floor of the permutation test both times (§1.5). This is the surviving half of
  a two-part claim; the other half did not survive.
* **There is a hatching axis, and the sign of a structured displacement moves you along it.** The preset
  runs strokes parallel where block-shuffle crosses them, predicted by sign in advance and confirmed on
  16 new prompts at 16/16 and 80/80 image pairs, with the norm-matched random control absent (§1.6). This is
  the Experiment 1 argument — structure rather than magnitude — reproduced on a second visual property, with
  a mechanical measurement and no human scoring.

**Not established, and it is honest to say so here:**

* **Anything outside Krea-2, and anything outside one narrow corner of image space.** This is the limit that
  bounds every result on this page, so it is first. All 40 prompts — the 24 of Experiment 1 and the 16 of the
  confirmation round — are **upper-body or close-up character portraits**, and **all 40 contain the phrases
  `bold ink outlines` and `hatched shadows`**, with 39 of 40 opening on `Western comics style`. One model, one
  sampler configuration, one aesthetic register, one framing.
  * The hatching axis of §1.6 is therefore measured **inside a style that explicitly asks the model to
    hatch**. That the sign of a structured displacement decides parallel versus crossed marks is solid within
    that regime; whether the same displacement does anything at all to a style that does not hatch is
    untested, and the honest reading is that it might do nothing.
  * The colour work of §1.5 hit the same wall from the other side: on close-up portraits the measured swatches
    are skin and paper whatever the scene describes, which is why the hue-coverage requirement could not be
    met. **Prompt text is not a usable lever for controlling measured hue in this corpus.**
  * The cross-architecture test on Anima / Cosmos-Predict2 is designed and pre-registered, not run. The
    genre test — the same axis on objects rather than characters — is
    [`docs/prereg_hatching_order_stage8.md`](docs/prereg_hatching_order_stage8.md), also not run.

  Until those two exist, the accurate one-line summary of this repository is: *in one 12.8 B diffusion model,
  on comic-style character portraits, small structured weight edits move stroke morphology and hatching
  orientation in reproducible, direction-specific ways.* Every word in that sentence is doing work.
* Whether the attribute-emergence effect is a general property or something specific to the prompt
  template it was found on. The one positive case on a different subject uses an almost identical
  sentence structure, and the test that would settle it has not been run.
* Which *structural* property of the perturbation is the operative one. Two points — block derangement
  works, sign scramble does not — separate structure from magnitude, but they do not identify what
  about the structure does the work.
* **That every weight edit carries a chromatic signature of its own.** Tested with the threshold fixed in
  advance, it came back three of six against a bar of four. Three is ambiguous, it is written as ambiguous,
  and the difference matters: "every displacement has its own colour" is the claim that failed, "different
  displacements move colour differently" is the claim that held. Two biases pulled in opposite directions on
  that corpus and neither can be quantified after the fact: the prompts clustered into one hue arc, which
  makes cross-prompt coherence *easier* to detect, while **none of them named a colour**, which §1.4 had
  already found to be the condition under which the palette effect disappears. Whether the ambiguity is the
  effect's true size or an artefact of testing it on colour-free prompts is now a registered, unrun question.
* **That colour and texture are two readings of one signature.** On the same 560 renders they behave
  oppositely — colour effects halve and randsign leads them; texture holds its size and randsign disappears.
  Any single account of what these perturbations do still has to explain both, and none here does.

---
<p align="center">
  <a href="#introduction--how-i-got-here"><strong>Introduction</strong></a> •
  <a href="#what-is-established-and-what-is-not"><strong>What is established</strong></a> •
  <a href="#experiment-1--the-style-signature"><strong>Experiment 1 · Style signature</strong></a> •
  <a href="#experiment-2--attribute-emergence"><strong>Experiment 2 · Attribute emergence</strong></a> •
  <a href="#roadmap"><strong>Roadmap</strong></a>
</p>

## Experiment 1 — The style signature

<sub>**1272 renders · 24 prompts · stages 2, 4, 5, 6, 7**</sub>

> **The direction I'm chasing.** That a model's style is not one blob you can only move closer to or
> further from, but something with *directions* in it — and that if you push along different ones you
> get different looks, each consistent across seeds and subjects. If that is true, then a preset is a
> real instrument: you calibrate it once and it does the same thing on images it has never seen. That
> is the premise a tuner needs to make any sense at all.
>
> **What would kill it.** If a control that moves the weights exactly as far as my preset, but without
> the calibrated structure, produced the same signature — same axis, same separation — then there is no
> direction, only displacement, and the whole idea collapses. That test has been run and the controls
> do not match on mark geometry. The version still standing open is architectural: if the axis does not
> rebuild on a different model family, "direction" is a fact about Krea-2 and not about diffusion models.
>
> **Where we are.** The calibrated preset separates from both matched controls on mark geometry, and the
> two controls are indistinguishable from each other there. The signatures also differ *from one
> another* in a readable way — randsign spends its displacement on broad-band grain rather than on
> contours. What has not been shown is that several *different hand-calibrated presets* share a common
> coherence, for the simple reason that only one has ever been built and tested.

### 1.1 Same displacement, different directions

In traditional model merging and manual tuning, it is very easy to fool yourself: you tweak a few sliders, see a dramatic change, and assume you discovered a "style direction". But if your edit simply pushed the weights twice as far away from the baseline, you didn't discover a direction — you just added more displacement.

To test this fairly, **every single condition here is strictly matched in total Frobenius displacement ($D = 0.0538$)**:

* **Baseline (Unmodified Base Model)**:  
  The stock Krea-2 checkpoint. The one we all know and love.
* **Targeted Preset (+)**:  
  The configuration I calibrated by hand. It steers toward **solid western comics inking**: line continuity increases, contours become intentional silhouette borders, and gradients give way to bolder, readable shading blocks.
* **Targeted Preset (-)**:  
  Inverting the signs of that same edit does not break the image — it reveals an **equally valid, opposite aesthetic**: the heavy ink lines dissolve into fine, nervous, dense cross-hatching (reminiscent of vintage etching or rapid ballpoint linework).
* **Blockshuffle**:  
  Keeps the exact same values from the preset, but scrambles which block receives which profile. The continuity of the line work vanishes, producing softer, less decisive transitions.
* **Randsign**:  
  Takes the exact same tensors and gives each value a random sign. Here the model channels its displacement into high-frequency grain and broad-band texture. For certain analog or xerox aesthetics, someone might actually find this texture appealing — it has its own tactile consistency, but it acts on micro-surface noise rather than contour geometry.

**I was not hunting for the "best-looking" configuration — I was hunting for the one closest to the output I had in mind.** The preset is calibrated toward *my* target (solid western comics inking); it is not a claim that this target is objectively better than the cross-hatched etching of `preset(-)` or the woodcut grain of Blockshuffle. Someone chasing a different look would calibrate somewhere else and be equally right.

That is an aesthetic statement, and it is separate from the measurement. What the experiment shows is that **different weight perturbations have distinct, measurable internal geometric signatures**, and that those signatures fall into two groups:

* On **mark geometry** — stroke width, contour length, contour fragmentation — the hand-calibrated preset separates from *both* matched controls, and the two controls are indistinguishable from each other.
* On **texture frequency** — cross-hatch entropy, FFT radial slope — it is **Randsign** that stands apart, spending its displacement on broad-band grain rather than on contour geometry.

So the preset is not simply "further away" than the controls: it moves the drawing along a different kind of axis than they do, at identical displacement. Section 1.3 quantifies that separation, and Experiment 2 shows the same controls doing something none of these metrics would have caught. **"Statistically distinct" is not "artistically superior"** — the measurement says the hand-calibrated edit lands somewhere the controls do not; it says nothing about whether you should want to go there.

---

To see how these weight changes physically alter the drawing style without getting lost in mathematical formulas, look at the facial linework and wrinkles of the **Ancient Hag** (`seed 4242145`). Her wrinkled skin acts as a natural canvas for line morphology:

<p align="center">
  <img src="assets/hero/crop_timelapse.gif" alt="Linework and Wrinkle Transitions Across Conditions" width="450">
</p>

<details>
<summary><code>G4</code> · <code>hag_chartreuse</code> · <code>prompt_sha1 95acba3b41</code> · seed 4242145 — <strong>show the exact prompt</strong></summary>

```text
Western comics style, bold ink outlines, hatched shadows, hard chartreuse-tinted rim light glowing along the edges of her face, wild-eyed manic determination, seen from an extreme low angle shot through an imagined gap between her chin and chest, extreme close-up on the head only, tight framing, sharply canted dutch angle. very old female hag, deep umber-brown weathered skin, wild frizzed grey hair sticking straight up as if charged with static, an exaggeratedly long hooked nose nearly touching her upturned chin, small sunken eyes blazing wide with fevered focus, sagging jowls trembling around a muttering open mouth, three long grey chin-hairs twisted into tiny braids, a single large hoop stretching one earlobe low. white background, simple background, chartreuse overall hue, monochromatic chartreuse.
```

</details>

#### Side-by-Side Detail Comparison
Look closely at the nose bridge, cheek folds, and brow hatching across the exact same seed:

![Detail Crop Comparison Across All 5 Conditions](assets/hero/detail_crop_strip.png)

* **Baseline (Unmodified Base Model)**:  
  Standard balanced comic art, combining medium contour outlines with light, scattered cross-hatching.
* **Targeted Preset (+) — Solid Graphic Inking**:  
  Line continuity increases sharply. Shadows under the nose and jaw consolidate into solid black graphic ink masses, and the outer contours turn into decisive, bold silhouette lines.
* **Targeted Preset (-) — Vintage Etching & Fine Cross-Hatching**:  
  Inverting the preset sign causes the heavy ink masses to dissolve into hyper-dense, razor-thin hatching across every single wrinkle, giving it the feel of a 19th-century copperplate engraving.
* **Blockshuffle — Rustic Cross-Hatching**:  
  Shuffling block assignments produces heavy, multi-directional diagonal hatching with a rough, organic woodcut print texture.
* **Randsign — High-Frequency Stippling & Grain**:  
  Scrambling the signs channels the energy into fine surface stippling and micro-grain rather than structured contours.

<details>
<summary><strong>🔍 Click to view full-resolution portraits across all 5 conditions</strong></summary>

![Full Portrait Comparison Across Conditions](assets/hero/conditions_strip.png)
</details>

---

### 1.2 The ruler that couldn't see

When I first ran standard automated benchmarks on these images using standard **CLIP ViT-L-14 (224×224)** embeddings, the data seemed to show that "nothing was happening". 

It turned out the metric was blind:
* CLIP downsamples a 1024×1280 image down to 224×224 before computing anything. At that resolution, fine pen strokes and inking continuity simply disappear.
* When we built a second measurement space focused specifically on **luminance and stroke morphology** (contour continuity, edge transitions, ink distance transforms), the result flipped:
  - In stroke space, the contrast between the targeted preset and block derangement resolves clearly at **$P = 0.001$** (difference in directional coherence $+0.249$, 95% CI $[+0.104, +0.382]$).
  - On the principal stroke continuity axis (PC1), the preset separates cleanly from both controls. Across the full 24-prompt pool: $-2.532$, 95% CI $[-3.00, -2.07]$, $d_z = -2.30$, $p_{\text{Holm}} < 0.0001$ against Blockshuffle; $-2.117$, CI $[-2.69, -1.54]$, $d_z = -1.55$, $p_{\text{Holm}} < 0.0001$ against Randsign. The two controls do not separate from each other on that axis ($+0.415$, CI $[-0.37, +1.20]$, n.s.).

**No sign flips between the two spaces** — the point estimates keep their direction. What flips is *which contrast the instrument can statistically resolve*: in CLIP space it is `preset − randsign` ($P = 0.0011$) while `preset − blockshuffle` stays undecided ($P = 0.151$); in stroke space it is exactly the other way round ($P = 0.157$ and $P = 0.001$). Same pixels, same statistic, same ten prompts — only the feature space changes.

Evaluate line art with a 224px semantic model and you will resolve the wrong comparison, and conclude the wrong thing about which edit did something.

---

### 1.3 Does it hold on other subjects?

Milestone 1 was declared **in advance**, with an explicit falsification criterion:

> *If directional coherence does not replicate with a 95% CI excluding zero on the new family, the effect will be documented as prompt-family specific rather than general.*

The family has since been extended from 10 to **24 prompts**, split by **how much colour freedom the prompt leaves the model**:

* **18 colour-pinned prompts** — the palette is specified element by element (skin, hair, eyes, rim light), leaving the model almost no choice.
* **6 colour-free prompts** — every colour word is removed and only `colored` remains, so the model picks the palette itself.

The two sub-families were analysed separately and then pooled, with the PCA recomputed independently inside each pool.

#### The criterion is met — on the axis it named

On the 6 new full-colour prompts, both preset contrasts on the stroke-continuity axis exclude zero:

| Contrast on PC1 (colour-free family, $n = 6$) | $\Delta$ | 95% CI | $d_z$ |
| --- | --- | --- | --- |
| Preset $-$ Blockshuffle | $-1.958$ | $[-2.50, -1.42]$ | $-3.82$ |
| Preset $-$ Randsign | $-3.815$ | $[-5.67, -1.96]$ | $-2.16$ |
| Blockshuffle $-$ Randsign | $-1.857$ | $[-4.03, +0.31]$ | $-0.90$ |

Contour geometry replicates alongside it: contour length $+0.760\ [+0.37, +1.15]$ and contour fragment count $-0.560\ [-0.82, -0.30]$ against Blockshuffle. **The effect is not an artifact of tightly colour-pinned prompts.**

**Is it the same axis?** Necessary check, because "PC1" is only a label until you compare the loadings. Cosine between the PC1 loading vectors of the separate PCAs (sign of a component is arbitrary, so $|\cos|$):

| | pinned vs free | pinned vs pooled | free vs pooled |
| --- | --- | --- | --- |
| **PC1** | $0.837$ | $0.990$ | $0.906$ |
| PC2 | $0.670$ | $0.983$ | $0.775$ |
| PC3 | $0.379$ | $0.990$ | $0.361$ |

PC1 is substantially the same direction in all three pools. **PC3 is not** ($|\cos| = 0.36$ between sub-families), so PC3 results are not comparable across them and are not claimed here.

> **Honest caveat on power.** With $n = 6$ prompts, an exact sign-flip permutation test enumerates $2^6 = 64$ assignments, so its smallest possible two-sided $p$ is $2/64 = 0.031$ — and after Holm correction across three contrasts, **no effect of any size can reach $p < 0.05$ on this sub-family**. That structural ceiling is exactly why the criterion was pre-declared in terms of the confidence interval rather than a $p$-value. The CI is parametric and is doing the work here; the replication rests on interval estimation, not on significance.

#### What the pooled 24 prompts add

Stroke width now separates the preset from **both** controls for the first time ($+0.238$, $p_{\text{Holm}} = 0.016$ vs Blockshuffle; $+0.394$, $p_{\text{Holm}} = 0.020$ vs Randsign) — at 10 prompts this comparison was underpowered.

And a clean two-group structure emerges across the ten metrics:

* **Mark geometry and palette** — PC1, stroke width, contour length, effective colour count, top-4 palette share: the preset separates from **both** controls, and the two controls do **not** separate from each other.
* **Texture frequency** — crosshatch entropy, FFT radial slope, PC2: **Randsign** is the outlier, channelling its displacement into broad-band grain while preset and blockshuffle stay together.

In other words: *on every axis where the preset is distinguishable, the two matched controls are indistinguishable from each other* — and where the controls do differ, it is because one of them is adding noise rather than steering geometry.

---

### 1.4 Does colour follow the same pattern?

The palette effects are **specific to colour-pinned prompts**. Pooled over 24 prompts the preset reduces the effective colour count against both controls ($-0.376$ and $-0.237$, both $p_{\text{Holm}} \approx 0.001$) and concentrates the palette into its top four clusters ($+0.384$, $+0.234$). On the 6 colour-free prompts, none of that survives: every palette contrast contains zero.

The 6 colour-free prompts existed to answer a separate question: **given the freedom to pick a palette, do different weight edits pick different palettes?** No measurement built so far could see it — every colour metric in this repo re-aligns the global cast to the baseline first, a deliberate choice made after a block-level edit was caught winning a "universality" score purely by tinting every image the same way. That made *how many* colours measurable and *which* colours invisible.

Measured directly (mean LAB chroma of the subject, no cast normalisation, displacement from the same-seed baseline):

| Colour-free family, $n = 6$ | palette shift | vs. a seed change | direction shared across prompts | $p$ |
| --- | --- | --- | --- | --- |
| Preset $+$ | $1.41$ | $1.31\times$ | $-0.165$ | $0.81$ |
| Preset $-$ | $1.81$ | $1.69\times$ | $-0.013$ | $0.25$ |
| Blockshuffle $+$ | $1.30$ | $1.21\times$ | $-0.137$ | $0.75$ |
| **Blockshuffle $-$** | $1.82$ | $1.70\times$ | $\mathbf{+0.944}$ | $\mathbf{<0.0001}$ |
| Randsign $\pm$ | $1.53$–$1.57$ | $\approx 1.4\times$ | $+0.38$–$+0.40$ | $0.03$–$0.07$ |

**The preset does not steer colour.** It shifts each subject's palette by about a third more than a different random seed already does, and those shifts **do not point the same way** from one subject to the next — there is no palette it pulls toward.

The exception is instructive: **Blockshuffle $-$ does impose a coherent cast** ($+0.944$ against a null 95th percentile of $+0.334$), i.e. nearly every subject's colours move in the same LAB direction. The artifact this project was most afraid of — an edit that scores well by simply tinting everything — is produced here by a *control*, not by the hand-calibrated preset.

One systematic asymmetry worth recording: on both sub-families the **negative** direction of every condition moves the palette roughly $1.7\times$ more than its positive counterpart.

### 1.5 Does every weight edit have its own colour signature?

Here is the thing I actually wanted to know. I never set out to build a preset that changes colours — I was
working on line and stroke, and colour was just something I noticed moving on the side. So the question was
never "is mine better". It was: if I nudge the weights one way and you nudge them another way, do we each get
a colour of our own? Does every edit end up with its own palette, the way every illustrator ends up with one?

I wrote down two separate claims, because they are not the same claim and I wanted to be able to lose one and
keep the other.

**One — each condition pushes colour in a direction of its own.** For each condition and each prompt, the
palette is reduced to eight slots (six swatches, plus the paper and the ink), each as $(L^*, a^*, b^*)$, and
measured as the **difference from the same prompt and the same seed under baseline** — otherwise the numbers
just tell you which character is in the picture. Then: is the direction the same across *different* prompts?

**Two — the conditions differ from one another.** Because if all six pushed colour the same way, each would be
"coherent" and none would have a signature.

Both were registered in [`docs/prereg_chromatic_signatures.md`](docs/prereg_chromatic_signatures.md), with the
thresholds fixed in advance, and then tested on **16 new prompts, 560 new renders** that share no prompt with
anything measured before.

| condition | 18 prompts, exploratory | 16 new prompts, confirmation | Holm |
| --- | --- | --- | --- |
| Blockshuffle $-$ | $+0.087$ | $+0.109$ | $0.0022$ ✓ |
| Randsign $-$ | $+0.276$ | $+0.093$ | $0.011$ ✓ |
| Preset $+$ | $+0.119$ | $+0.059$ | $0.021$ ✓ |
| Randsign $+$ | $+0.196$ | $+0.048$ | $0.0510$ ✗ |
| Preset $-$ | $+0.025$ | $+0.017$ | $0.35$ ✗ |
| Blockshuffle $+$ | $+0.018$ | $+0.017$ | $0.35$ ✗ |

**Claim one: ambiguous, and recorded as ambiguous.** The rule written in advance said four or more of six
confirms it, two or fewer refutes it, and three is ambiguous and must not be rounded up. Three survived.
Randsign $+$ lands at Holm $= 0.0510$. It is not counted — that is the whole reason the threshold existed
before the data did.

**Claim two: confirmed, twice, on independent corpora.** Within-condition coherence $+0.057$ against
$+0.023$ between conditions, difference $+0.035$, against a label-permutation null whose 95th percentile is
$+0.007$. $p = 10^{-4}$, the floor of the test. The exploratory run gave $+0.080$ with the same $p$.

**The effects roughly halved on independent renders** — mean within-condition coherence fell from $+0.120$ to
$+0.057$, and the ranking reshuffled. A power curve built on the exploratory numbers promised ~100% at sixteen
prompts; the true effect was about half that, and sixteen turned out to be a floor rather than a margin.

**Part of that gap is an artefact of how the two runs were scaled, and it is ours.** Each run standardises its
24 dimensions by the spread of its *own* difference vectors, which is correct inside a run and wrong between
two. Rescaled on a single common basis, the two sit at $+0.087$ and $+0.054$ — a factor of 1.6, not 2.1. The
within-run figures in the table above stand; the *comparison* between them was inflated, and the corrected one
is what the next design should be sized against.

**And there is a second explanation for that halving, which this design cannot separate from the first.**
Every one of the 18 exploratory prompts pins the palette in its text — `monochromatic teal`, `yellow overall
hue`, a colour-tinted rim light. **Not one of the 16 confirmation prompts does.** §1.4, on a completely
different colour instrument, had already found the palette effect present where the prompt names a colour and
absent where it does not — and the confirmation was then run entirely on the side where §1.4 predicts little
to find. The corpus changed on that variable at the same moment it changed from exploratory to confirmatory.

That is our design error, and it is worth being precise about what kind. The pre-registration froze the
statistics, the thresholds and the scripts; it did not control the one prompt property this repository had
already implicated. A stratification rule *was* written — but it targeted the **measured** hue of the render,
not the **stated** colour in the prompt, which is the variable that mattered.

So §1.5 should not be read as "colour signatures are weak". It should be read as: *tested on prompts that do
not name a colour, three conditions of six carry a coherent chromatic direction, and whether naming a colour
changes that is now an open, registered question.* The test is cheap and is described in
[`docs/prereg_chromatic_signatures.md`](docs/prereg_chromatic_signatures.md): the same subject written twice,
with and without the colour clause, in one run.

**One thing that went wrong in the corpus, and it is worth more than the result.** The registered design
required four prompts in each of four 90° hue arcs. The selection returned **fourteen of sixteen in
0–90°, and none at all between 180° and 270°**. The rule ran correctly; the candidate pool did not contain
what it asked for. The reason is specific and useful: these are close-up character portraits, so the six
swatches are dominated by skin and paper no matter what the scene describes. **Prompt text is the wrong lever
for controlling measured hue.** That bias runs *towards* the result — a corpus of more similar prompts makes
cross-prompt coherence easier to detect, not harder — while the colour-pinning problem above runs against it.
They are not commensurable and neither is a defence; both are reasons the next run has to be designed
differently.

**Where the coherence actually lives.** Splitting the 24 dimensions into lightness and chromaticity separates
the conditions by kind. Randsign's coherence is largely **tonal**: $+0.502$ on the six $L^*$ steps alone,
where the preset does not survive correction at all. The preset's is **chromatic**: it survives on
$a^*, b^*$ and not on $L^*$. They are not two strengths of one effect. Randsign is mostly moving the greyscale.

Worth looking at before reading the numbers again, because it is the honest picture: four subjects with very
different baseline palettes, all seven conditions, one seed. **The colour does move** — nobody has to squint to
see it. What the statistics say is that it does not move the *same way* from one subject to the next often
enough for each condition to own a direction of its own.

<p align="center">
  <img src="assets/01_steering_stage7/_figures/colour_sampler.webp" alt="Four subjects across all seven conditions at seed 1337" width="100%">
</p>

<details>
<summary><code>I20</code> · <code>a_drow_man_with_swept_back_silver_hair</code> · <code>prompt_sha1 952efcc3c6</code> — <strong>show the exact prompt</strong></summary>

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A drow man with swept-back silver hair. armor made of dark adamantine, He wears a spider-web cowl and sharp chitinous shoulder guards. He's holding dual twin daggers drawn, predatory pose, mocking, sinister. subterranean purple cavern, simple background. magenta reflection on the adamantine.
```

</details>

And the same thing measured rather than eyeballed — the eight slots of each palette, condition under baseline,
on a neutral grey ground because a colour is judged against whatever surrounds it:

<p align="center">
  <img src="assets/01_steering_stage7/_figures/palette_stage7.webp" alt="Mean palettes per condition, baseline above and condition below" width="100%">
</p>

> Consistency worth noting rather than claiming: §1.4, using a completely different colour instrument, singled
> out Blockshuffle $-$ as the one condition imposing a coherent cast. This analysis, built the other way round
> and on other renders, puts Blockshuffle $-$ at the top too.

---

### 1.6 The hatching axis — a prediction made before the renders existed

This one started the way the barnacles did: I was just looking at pictures. In nearly every image I could
remember, `blockshuffle_neg` shaded with **parallel** strokes and `blockshuffle_pos` shaded with
**cross-hatching**. I said 95% by eye. The difference from every other thing in this notebook is that I said
it *before* the next batch was rendered, and that this one needs nobody to score anything — parallel versus
crossed is a spread of stroke orientations, and `crosshatch_entropy_mean` was already in the feature set from
the first day.

Measured on the old 18 prompts, my eye came out at **87/90 image pairs, or 96.7%**. But it also showed the
observation was too narrow, in a way I liked better than being right: **the preset does the same thing, with
the sign the other way round.** Where `blockshuffle_pos` crosses the strokes, `preset_pos` runs them parallel.
So it is not a fact about block-shuffling. There is an axis, the sign of the displacement moves you along it,
and which sign gives which texture depends on the direction you moved in.

That was written up as a directional prediction — the sign, per family, not just "there is an effect" — in
[`docs/prereg_hatching_axis_stage7.md`](docs/prereg_hatching_axis_stage7.md), before stage 7 rendered, with a
clause saying that a family reaching significance with the **wrong** sign counts as a failure and not as a
partial success.

Here is the axis, on one seed, cycling through the four conditions in the order the measurement puts them —
most parallel to most crossed. Watch the shading on the neck and the shoulder:

<p align="center">
  <img src="assets/hero/hatching_axis.gif" alt="The hatching axis: preset+, blockshuffle-, blockshuffle+, preset- on one seed" width="450">
</p>

<details>
<summary><code>I07</code> · <code>a_half_orc_man_with_a_shaved_head_and_facial_scars</code> · <code>prompt_sha1 402376662d</code> · seed 1337 — <strong>show the exact prompt</strong></summary>

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A half-orc man with a shaved head and facial scars. armor made of granite, He wears an iron jaw visor and layered stone shoulder pads. He's holding a heavy greataxe pointed down, relaxed pose, solemn, tired. cracked dry earth, simple background. blue reflection on the stone.
```

</details>

And held still, on the gloves and sleeve — a broad, densely shaded surface that stays put across all four
conditions, so what changes between the panels is the marking and not the drawing. Same prompt, same seed,
same crop box, in the order the measurement puts them:

<p align="center">
  <img src="assets/01_steering_stage7/_figures/hatching_detail_I09.webp" alt="Parallel versus crossed hatching on gloves and sleeve, four conditions, one seed" width="100%">
</p>

<details>
<summary><code>I09</code> · <code>a_dwarf_woman_with_twin_braided_ginger_pigtails</code> · <code>prompt_sha1 0a1c94584d</code> · seed 777 — <strong>show the exact prompt</strong></summary>

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A dwarf woman with twin braided ginger pigtails. armor made of copper, She wears an iron miner cap and thick square shoulder pads. She's holding a heavy pickaxe leaning forward, cheerful pose, grinning, confident. underground crystal mine, simple background. yellow reflection on the copper.
```

</details>

*The crop box is published in [`data/figure_crops_stage7.json`](data/figure_crops_stage7.json): choosing where
to look is a decision, and on a texture claim it is the decision that matters most. The same comparison on
chainmail and cloth ([`hatching_detail_I06.webp`](assets/01_steering_stage7/_figures/hatching_detail_I06.webp))
and on skin and background shading ([`hatching_detail_I07.webp`](assets/01_steering_stage7/_figures/hatching_detail_I07.webp)),
because a texture claim that only holds on one material is a claim about that material.*


**Result on the 16 new prompts:**

| family | predicted sign | $\Delta$ observed | $p$ | Holm | prompts | image pairs |
| --- | --- | --- | --- | --- | --- | --- |
| **Preset** | negative | $\mathbf{-0.370}$ | $3.05\times10^{-5}$ | $9.2\times10^{-5}$ | $\mathbf{16/16}$ | $\mathbf{80/80}$ |
| **Blockshuffle** | positive | $\mathbf{+0.288}$ | $3.05\times10^{-5}$ | $9.2\times10^{-5}$ | $\mathbf{16/16}$ | $\mathbf{79/80}$ |
| Randsign | negative | $+0.020$ | $0.67$ | $0.67$ | $11/16$ | $50/80$ |

$p = 3.05\times10^{-5}$ is the exact permutation floor at $n = 16$: below the resolution of the test, not a
measured value.

The primary was written as a conjunction across all three families, so strictly **it is not met** — two of
three. Preset and blockshuffle are confirmed at the floor, with sixteen prompts of sixteen and eighty image
pairs of eighty, not one exception. Randsign is simply absent: $11/16$ is a coin.

And this is what "80 image pairs out of 80" looks like. Two conditions, five seeds each, one prompt — the
texture is not a lucky render, it is what that direction does every time:

<p align="center">
  <img src="assets/01_steering_stage7/_figures/hatching_seed_stability.webp" alt="Block-shuffle negative versus positive across all five seeds" width="100%">
</p>

<details>
<summary><code>I09</code> · <code>a_dwarf_woman_with_twin_braided_ginger_pigtails</code> · <code>prompt_sha1 0a1c94584d</code> — <strong>show the exact prompt</strong></summary>

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A dwarf woman with twin braided ginger pigtails. armor made of copper, She wears an iron miner cap and thick square shoulder pads. She's holding a heavy pickaxe leaning forward, cheerful pose, grinning, confident. underground crystal mine, simple background. yellow reflection on the copper.
```

</details>

*All 16 prompts side by side are in [`hatching_census_stage7.webp`](assets/01_steering_stage7/_figures/hatching_census_stage7.webp),
and the crop boxes used are published in [`data/figure_crops_stage7.json`](data/figure_crops_stage7.json) — a
hand-chosen crop is a decision, so it is recorded rather than described.*

**Failing on randsign is what makes this result mean something.** Had all three held, the hatching axis would
have been a property of reversing *any* displacement. It is not. It belongs to the two structured directions,
and the control matched to the identical Frobenius displacement does not produce it — the Experiment 1
argument, structure rather than magnitude, reproduced on a second visual property, with a mechanical
measurement and nobody scoring anything by hand.

And the effect sizes **held** across an independent corpus of new subjects: preset $-0.484 \rightarrow -0.370$,
blockshuffle $+0.274 \rightarrow +0.288$, the latter within 5%.

> **The two results read against each other.** Same 560 renders, same day. Colour saw every effect halve and
> its strongest condition was randsign. Hatching saw the structured conditions hold their size and randsign
> vanish. Same displacements, same images, opposite patterns — so these are not two views of one signature.
> Texture responds to the sign of a *structured* displacement, close to deterministically. Colour responds to
> displacement more diffusely, and does not tell structure from noise the same way. Whatever these
> perturbations turn out to be doing, it has to account for both.

> **A note on how to count these.** Sections 1.1 to 1.4 are **four measurements of one corpus**, not
> four replications. The same 1272 renders are behind all of them, so agreement between them is a
> consistency check, not independent confirmation. None of the four was pre-registered — they emerged
> in sequence, in response to challenges.
>
> Sections 1.5 and 1.6 are different in kind, and that is the point of them. Both were **registered with
> their thresholds before the renders existed**, and both were tested on **560 renders across 16 prompts
> that share no prompt with any earlier stage**. Where they agree with the exploratory numbers, that is
> independent confirmation. Where they disagree — and 1.5 disagrees by a factor of two — the confirmation
> is what is reported.

---

## Experiment 2 — Attribute emergence

<sub>**390 renders · 24 sets · a separate corpus from Experiment 1**</sub>

> **The direction I'm chasing.** Everything in Experiment 1 is about *how* the model draws something it
> was already going to draw. This one asks something else: can a different weight calibration make a
> detail that is written in the prompt but normally ignored actually show up — consistently, at the
> same prompt structure? If it can, then weight-space tuning is not only a style knob, it touches what
> the model decides to put in the picture.
>
> **What would kill it.** If a sign-scrambled control carrying the identical displacement made the
> detail appear just as often, the effect would be about how hard you push, not about how you push.
> That test has been run: randsign scores 1/20, which is the stock model's exact rate. The version
> still open is generality — if a prompt with a completely different structure, but carrying the same
> two anchor phrases, fails to reproduce it, then this is a fact about one template and the section
> gets rewritten to say so.
>
> **Where we are.** The jump is 1/20 to 19/20 on the original prompt and 7/20 to 20/20 on a second one,
> with no seed going the other way in either. But it is a gain on a binding the prompt has to establish
> first, not a repair: remove either of two specific phrases and the effect falls back to the stock
> model's rate. One attribute, one prompt family, and the perturbation tested is a control rather than
> my own preset.

### 2.1 The effect

| Condition | Attribute present | 95% CI | vs. paired control | $p$ |
| --- | --- | --- | --- | --- |
| Blockshuffle, full prompt | **19 / 20** | [76%, 99%] | 18 discordant to 0 | $7.6 \times 10^{-6}$ |
| Stock model, same prompt | 1 / 20 | [1%, 24%] | — | — |
| Blockshuffle, second prompt | **20 / 20** | [84%, 100%] | 13 discordant to 0 | $2.4 \times 10^{-4}$ |
| **Randsign**, full prompt, identical $D$ | 1 / 20 | [1%, 24%] | vs. blockshuffle, 18 to 0 | $7.6 \times 10^{-6}$ |
| Stock model, second prompt | 7 / 20 | [18%, 57%] | — | — |

<p align="center">
  <img src="assets/02_attribute_emergence/_figures/detail_A1_vs_A5.webp" alt="Primary Finding: Blockshuffle Permuted Blocks vs Stock Base Model (First 6 Seeds)" width="100%">
</p>

> *Detail figure: First 6 canonical seeds (1337, 42, 4242145, 777, 9999, 101) cropped tight on the attribute region (all bounding boxes published in [`data/figure_crops.json`](data/figure_crops.json)). For the complete 20-seed contact sheet proving no omission, see the [Full Census Sheet (A1 vs A5)](assets/02_attribute_emergence/_figures/census_A1_vs_A5.webp).*

Not one seed goes the other way in either comparison. Two controls run in the same batch are what make this mean something.

**The keyword control.** With the barnacle phrase deleted from the prompt, the same weight configuration produces the attribute in **2 / 20** renders — the perturbation is not decorating earlobes on its own.

**The norm-matched control.** Randsign — the sign scramble carrying the *identical* Frobenius displacement $D = 0.0538$, differing from blockshuffle only in the structure of the perturbation and not its size — produces **1 / 20**. That is not "weaker": it is **exactly the stock model's rate**, on the same prompt and the same seeds, and the two are paired at one discordant seed each way. A perturbation of the same magnitude with scrambled signs instead of permuted blocks does *nothing at all*.

This is the control that decides what the finding is. Without it, the result would be vulnerable to the obvious reading — *any push of that size out of the checkpoint shakes a secondary token loose*. With it, that reading is dead: the effect is a property of **which** permutation, not of **how far** it moves.

<p align="center">
  <img src="assets/02_attribute_emergence/_figures/detail_A1_vs_A7.webp" alt="Frobenius-Matched Control: Blockshuffle vs RANDSIGN at D = 0.0538 (First 6 Seeds)" width="100%">
</p>

> *Detail figure: First 6 canonical seeds across identical Frobenius displacement $D = 0.0538$ (published boxes in [`data/figure_crops.json`](data/figure_crops.json)). See the [Full Census Sheet (A1 vs A7)](assets/02_attribute_emergence/_figures/census_A1_vs_A7.webp) for all 20 paired seeds.*

### 2.2 The finding is the conjunction, not the perturbation

The attribute does not appear whenever the weights are perturbed. It appears only when the prompt also supplies a **two-token local scaffold**: the ontological anchor `sea-touched` *and* the neighbouring morphological phrase `thin webbed fin-like ridges tracing along her temple`. Removing either one — a single-variable knockout, everything else byte-identical — collapses the effect:

| Prompt | `sea-touched` | `webbed fin-like ridges` | barnacle keyword | Result |
| --- | :---: | :---: | :---: | --- |
| G1 complete | ✓ | ✓ | ✓ | **19 / 20** |
| Siren/hag hybrid | ✓ | ✓ | ✓ | **20 / 20** |
| Only the ridges phrase removed | ✓ | ✗ | ✓ | **1 / 20** |
| Only `sea-touched` removed | ✗ | ✓ | ✓ | **0 / 10** |
| Keyword without any marine context | ✗ | ✗ | ✓ | 0 / 20 |
| Length- and syntax-matched neutral | ✗ | ✗ | ✓ | 0 / 20 |
| Teal sea hag, no ridges | ✓ | ✗ | ✓ | 0 / 20 |
| Ancient Hag + keyword, no marine context | ✗ | ✗ | ✓ | 0 / 20 |

The sharpest number in the whole experiment is the one that looks least impressive. With the ridges phrase removed, the perturbed model scores **1 / 20** — and the stock model on the complete prompt also scores **1 / 20**. Paired, they are **1 discordant seed each way, $p = 1.0$**: without the scaffold, the weight perturbation is statistically indistinguishable from not having applied it at all.

<p align="center">
  <img src="assets/02_attribute_emergence/_figures/detail_A1_vs_E3.webp" alt="Conjunctive Gate: Full Prompt with Temple Ridges vs Temple Ridges Phrase Removed (First 6 Seeds)" width="100%">
</p>

> *Detail figure: First 6 canonical seeds with vs. without the morphological temple-ridges phrase (published boxes in [`data/figure_crops.json`](data/figure_crops.json)). See the [Full Census Sheet (A1 vs E3)](assets/02_attribute_emergence/_figures/census_A1_vs_E3.webp) for all 20 paired seeds.*

So the 2×2 is:

| | Scaffold absent | Scaffold present |
| --- | --- | --- |
| **Stock model** | 0 / 20 | 1 / 20 |
| **Blockshuffle** | 0/20, 0/20, 0/20, 0/10, **1/20** (five independent cells) | **19 / 20**, **20 / 20** |

The effect lives in exactly one cell. **The perturbation does not add the attribute and does not repair the neglect — it acts as a gain on a binding the prompt must already have established, and that binding is fragile enough that one phrase carries it.**

### 2.3 Which half of the model carries it

The preset moves the DiT and the text encoder together. Run separately, on the same 20 seeds and the complete prompt:

| Where the perturbation is applied | Present | 95% CI | Comparison | $p$ |
| --- | --- | --- | --- | --- |
| DiT + text encoder | 19 / 20 | [76%, 99%] | — | — |
| **DiT only** (encoder left stock) | **12 / 20** | [39%, 78%] | vs. stock, 11 discordant to 0 | $9.8 \times 10^{-4}$ |
| **Text encoder only** (DiT left stock) | 3 / 20 | [5%, 36%] | vs. stock, 3 to 1 | $0.63$ — **not distinguishable** |
| Stock | 1 / 20 | [1%, 24%] | — | — |

The text encoder on its own does nothing measurable. The DiT carries most of the effect. Adding the encoder on top of the DiT still gains 6 discordant seeds to 0 ($p = 0.031$), so the two are not redundant — but at 19/20 the combination is against the ceiling and **the size of any synergy cannot be estimated from these data**. Measuring it would require repeating the 2×2 at a strength where nothing saturates.

### 2.4 Dose–response

Applying the same preset at scaled strength (10 seeds per point, complete prompt):

| Strength | 0.25 | 0.50 | 0.75 | 1.00 | 1.25 | 1.50 | 1.75 | 2.00 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Present | 1/10 | 5/10 \* | **10/10** | **19/20** | 8/10 | 6/10 | 5/10 | 1/10 |

\* four renders at 0.50 were judged ambiguous against the scoring rule and are recorded as `ambiguous` in the data rather than forced to 0 or 1.

<p align="center">
  <img src="assets/02_attribute_emergence/_figures/dose_response_strip.webp" alt="Resonance Curve: Strength Titration on Seed 1337 across 8 Strengths" width="100%">
</p>

> *Resonance curve: Panels show seed 1337 across 8 preset strengths. Scores in parentheses reflect the complete set (10 seeds per point, 20 at 1.00; asterisks denote ambiguous renders).*

There is an optimum around $0.75$–$1.00$ and both ends fail. That argues against "any disturbance of the weights helps" — at $2.00$ the displacement is largest and the attribute is gone. But at $n = 10$ the Wilson interval on $6/10$ is [31%, 83%]: **the extremes are separated, the intermediate points are not ordered by these data.**

### 2.5 What emerges is not quite what was asked for

The prompt says `studding one earlobe`. Across every positive render, the clusters sit on the **cheekbone and temple region**, not on or in the ear. The attribute emerges; its spatial binding does not. This is worth stating plainly because it changes what the result is evidence *for*: the perturbation recovers the *presence* of a neglected concept, and leaves its *placement* wrong in the same way the stock model would have.

<p align="center">
  <img src="assets/02_attribute_emergence/_figures/placement_crops.webp" alt="Morphological Landing: Barnacle Clusters Form on Cheekbone and Temple (Not on Earlobe)" width="100%">
</p>

> *Morphological landing: Individual 240×240 crops across 6 positive renders (published boxes in [`data/figure_crops.json`](data/figure_crops.json)), demonstrating that clusters consistently land on the cheekbone and temple rather than on the prompt-specified earlobe.*

### 2.6 What this does **not** establish

* **Two perturbations were tested, not the whole space.** Blockshuffle does it; randsign at the identical $D$ does not. That separates *structure* from *magnitude*, which is the distinction that mattered. It does not tell us which structural property is the operative one — block coherence is the obvious candidate, but "permutation rather than sign flip" and "preserves each block's internal correlations" are not distinguished by two points.
* **The hand-calibrated preset was not tested either.** The claim here is about a matched control from the main experiment, not about the author's preset.
* **One attribute, one prompt template.** G1 and the hybrid share nearly every token. Whether this generalises to other neglected attributes on unrelated characters is untested.
* **The scoring is unblinded**, by the author, with the condition visible. With 18 discordant seeds to 0 the headline will not flip, but the intermediate cells (the DiT-only 12/20, the 0.50 strength point) are exactly where a borderline call moves the number.
* **The ridges knockout deletes rather than substitutes.** The matched-neutral design used elsewhere in this experiment was not applied to it, so a residual prompt-length or token-position explanation is not formally excluded — though note that removing the phrase *shortens* the distance between `sea-touched` and the barnacle keyword, which cuts against a positional account rather than for it.

### 2.7 Where this sits

The phenomenon has a name: **catastrophic neglect**, the failure of a text-to-image model to render a concept its prompt explicitly contains. The published remedies operate at inference time on cross-attention — [Attend-and-Excite](https://arxiv.org/abs/2301.13826) and [attention-guided feature enhancement](https://arxiv.org/html/2406.16272v2) both re-weight attention maps during sampling. What is reported here is different in kind: a **static, prompt-preserving change in weight space**, found incidentally while running a matched control, that moves a specific neglected attribute from 5% to 95% presence without touching the prompt or the sampler.

There is a second difference, and it is architectural rather than methodological. **Krea-2 has no cross-attention in its blocks at all.** Text enters once upstream through `txtmlp` → `txtfusion` and reaches each of the 28 blocks as an adaptive modulation signal (`mod.lin`, a `[36864] = 6 × 6144` vector per block). The published remedies all re-weight cross-attention maps during sampling — maps this architecture does not have. So the token-competition behaviour reported here was found in a model where the standard fix has nothing to grab hold of. Structure for both checkpoints is published in [`docs/model_structures/`](docs/model_structures/). Whether it generalises beyond this attribute is exactly what 2.6 says is untested.

---

## Roadmap

### Experiment 2 · Resolved — emergence is about structure, not magnitude
* **The question was**: Experiment 2 shows a norm-matched block derangement moving a neglected attribute from 1/20 to 19/20. Would randsign, the sign scramble at the identical $D = 0.0538$, do the same?
* **Answer**: no. Randsign scores **1 / 20** — the stock model's exact rate. The pre-declared criterion said that above 15/20 the word "coherent" would come out of the claim; at or below 2/20 the structure of the perturbation becomes the operative variable. It landed at 1/20.
* **What is still open on the same axis**: two points do not identify *which* structural property matters, and the hand-calibrated preset has still never been run on this attribute.

### Experiment 2 · Open — a general mechanism, or a fact about one template?
* **Goal**: The only positive case on a different subject (the siren/hag hybrid, 20/20) shares almost every token with the original prompt, and every negative case carrying both anchors is structurally close too. So "it generalises" has not been tested — only "it survives a small edit" has.
* **Pre-declared Criterion**: A prompt with a different camera, a different register and a non-marine character, carrying an analogous pair of anchors — one ontological, one an adjacent local morphology — for a **different** neglected attribute. If the attribute emerges there, the conjunctive gate is a general mechanism. If it does not, Experiment 2 is rewritten as a finding about this prompt family and the word "mechanism" comes out of it.
* **Second question on the same run**: the hand-calibrated preset on the same 20 seeds, which has never been tested on this attribute at all.

### Experiment 1 · Partly resolved — the colour-free family was extended, and it did not go the predicted way
* **The question was**: the colour-count separation holds on 18 colour-pinned prompts and vanishes on 6 colour-free ones, but $n = 6$ cannot tell "absent" from "underpowered". The criterion declared in advance was to extend the colour-free family to at least 16 prompts, and to drop the palette claim if the cross-prompt chroma direction stayed below its permutation null.
* **What happened**: stage 7 is that extension. **None of its 16 prompts pins the palette** — no `monochromatic`, no `overall hue`, no tinted rim light; they describe materials and reflections and leave the model free. The cross-prompt direction did **not** stay below the null: three of six conditions clear a Holm-corrected permutation test (§1.5). So the trigger to drop the claim did not fire — but the fuller claim it was guarding, that every condition carries its own chromatic direction, came back three of six against a bar of four and is recorded as ambiguous.
* **The second question got a clean answer.** It asked whether Blockshuffle $-$ would keep producing a coherent cast, having scored $+0.944$ on an entirely different colour instrument in §1.4. On stage 7 it is the **top condition of all six** ($+0.109$, $p_{\text{Holm}} = 0.0022$). Two instruments, two corpora, same condition singled out. That a *matched control* is the most chromatically coherent perturbation in the set is now a finding and not a footnote.
* **What is still open**: the effective-colour contrast itself was not recomputed on stage 7 — only the direction analysis was. And the corpus failed its own hue-coverage requirement, for a reason that generalises: on close-up portraits the measured swatches are skin and paper whatever the prompt says, so **prompt text cannot be used as the lever for controlling measured hue**. Any future colour corpus has to change the framing, not the wording.

### Experiment 1 · Open — does naming a colour in the prompt govern the chromatic signature?
* **Goal**: the confirmation round of §1.5 differed from its exploratory set on a variable this notebook had already implicated — every exploratory prompt names a colour, none of the confirmation prompts do — so its ambiguous verdict has two readings the design cannot separate. A between-corpus look on a single common scale is suggestive and not decisive: prompts that name a colour are **1.6× more coherent**, but they also move **less** (amplitude ratio 0.67–0.85), so a stated colour appears to *constrain* the palette rather than to license the effect. Four conditions of six go one way, two the other.
* **Pre-declared Criterion**: matched pairs — the same subject written twice, identical character for character except the colour clause, rendered in one run under the same conditions and seeds. Two readouts: the paired amplitude, and the **cosine between the two members of a pair**, which separates "the clause constrains how far the palette moves" from "the clause changes where it goes". Those have never been distinguished.
* **A third arm, and the cheapest of the three**: the **empty prompt**. With no text to interpret, whatever still separates the conditions at a fixed seed is what the perturbation does independently of reading. Note what this is not: Krea-2 passes text through `txtmlp` → `txtfusion` and injects it as per-block modulation, so an empty string still produces an embedding. It is the empty-string prior, not the absence of conditioning.
* **Status**: a 180-render pilot is specified — four conditions rather than six, four pairs, five seeds — to size the effect before committing a full run. With four subjects the permutation floor is 2/2⁴ = 0.125, so the pilot cannot produce a significant result and will not be reported as one.

### Experiment 1 · Open — the hatching axis on objects, with an instrument that measures it directly
* **Goal**: §1.6 establishes the axis on character portraits using `crosshatch_entropy_mean`, which is a proxy: it correlates with how much line is on the page at all ($r = +0.52$, $R^2 = 0.27$), and a second proxy — how many separate pieces the drawing breaks into — disagrees with it about the ordering *across* families. The proxy settles the sign; it cannot settle the ladder.
* **Pre-declared Criterion**: [`docs/prereg_hatching_order_stage8.md`](docs/prereg_hatching_order_stage8.md), locked before the instrument was built. The instrument is the histogram of edge-gradient orientations — parallel hatching is unimodal, cross-hatching bimodal with two near-orthogonal peaks — and the prediction is a full ordinal ranking of four conditions, one ordering out of twenty-four, stated by eye in advance.
* **Why objects**: every prompt measured so far is a close-up character. A signature that survives a change of genre is a statement about the model; one that survives only among portraits is a statement about portraits. Stage 8 keeps a minority of subject prompts precisely so the instrument change and the genre change do not become inseparable.

### Both experiments · Open — replication across a different *conditioning mechanism*
* **Goal**: Apply the exact same $D$-matched protocol (sign scramble + block derangement) to [`circlestone-labs/Anima`](https://huggingface.co/circlestone-labs/Anima).
* **Why this is more than "another DiT"**: the two models do not condition on text the same way. Krea-2 fuses text once upstream and injects it per block as modulation, with no cross-attention anywhere in the backbone. Anima gives **every one of its 28 blocks its own cross-attention**, taking keys and values from the 1024-dimensional output of a dedicated 6-block `llm_adapter`. They also differ by 6× in per-block capacity (434 M parameters against 69 M) and by 3× in hidden dimension (6144 against 2048). A result that survives that crossing is not a fact about an implementation.

| | Krea-2 Turbo | Anima Base v1.0 |
| --- | --- | --- |
| Backbone | 28 blocks × **13 tensors** | 28 blocks × **20 tensors** |
| Parameters per block | 434.16 M | 69.21 M |
| Hidden dimension | 6144 | 2048 |
| Feed-forward | 16384, SwiGLU (×2.67) | 8192 (×4.0) |
| Attention | GQA, 48 query / 12 kv heads | MHA, 16 / 16 |
| **How text enters a block** | **adaptive modulation** (`mod.lin`, 6 × 6144) | **cross-attention** (k/v from a 1024-dim adapter) |
| Text adapter | 4 `txtfusion` blocks | 6 `llm_adapter` blocks |

* **A capability Anima has and Krea-2 does not**: because text influence is localised in `cross_attn.k_proj` and `v_proj` per block, the model-versus-encoder split of §2.3 can become a **three-way** split there — DiT self-attention, DiT cross-attention, text encoder. That decomposition is not available on Krea-2 at all.
* **Pre-declared Criterion**: PC1 rebuilt independently on the new architecture, with the preset separating from both controls at a 95% CI excluding zero. If it does not, the effect is documented as Krea-2 specific.

*(Additional technical tools — quadratic $\epsilon$-scaling, VLM judge calibration, and 30-prompt CLIP closure — are kept in the [`experiments/`](experiments/) directory and outlined in [§9 of the Lab Notebook](index.html#ripresa).)*


---

## How to Explore, and How to Replicate

* **Reproducing the confirmation round**: [`docs/reproduce_stage7.md`](docs/reproduce_stage7.md) has the full recipe for §1.5 and §1.6 — the seven presets, the manifests with every prompt verbatim, the exact commands, and the hash of every published input. All 600 renders are browsable as webp under [`assets/01_steering_stage7/`](assets/01_steering_stage7/); the full-resolution PNGs are a release asset, because colour measurements have to be re-extracted from PNG and not from webp.
* **Interactive A/B Viewer**: Open [`viewer/viewer.html`](viewer/viewer.html) in your browser to inspect image pairs side-by-side or toggle back-and-forth instantly with the spacebar.
* **Complete Lab Notebook**: Read [`index.html`](index.html) for all the mathematical formulations, KaTeX derivations, PCA loadings, and vector SVG forest plots.
* **The 33 Pitfalls Checklist**: Before trying this on another model, check [`docs/errors_log.md`](docs/errors_log.md) — it documents 33 real measurement mistakes made during this work that gave plausible-looking numbers but were totally wrong.
* **Re-run the Analysis**: `python experiments/global_aggregation_corrected.py` runs from a fresh clone — it resolves its inputs to `data/`, which holds the full feature matrix and the image manifests, and regenerates every aggregation table quoted above. It needs `numpy`, `pandas`, `scipy` and `scikit-learn`.
* **What you cannot re-run from a clone**: the scripts that read pixels — `analyze_texture.py`, `analyze_quantization.py`, `color_freedom.py`, `run_style_features.py` — need the complete render set (≈1 500 PNGs at 1024×1280), which is not committed here. `assets/` carries a representative subset for visual inspection only. Those scripts still point at local absolute paths and are published as the **record of how the numbers were produced**, not as a turnkey pipeline.
* **Repository size and original master PNGs**: a full clone is **~44 MB** (all images served as high-quality 480×600 WebP under `assets/01_steering/`, `assets/01_steering_stage7/` and `assets/02_attribute_emergence/`). The uncompressed 1024×1280 master PNG originals are preserved in full and packaged as GitHub Release assets:
  - [`stage7_renders_png.tar.gz`](https://github.com/aledelpho/diffusion-models-weight-steering-report/releases) (1.07 GB · 600 PNGs for Stage 7 confirmation round)
  - [`krea2_steering_png_originals.zip`](https://github.com/aledelpho/diffusion-models-weight-steering-report/releases) (498 MB · 370 master PNGs for Experiment 1)
  - [`krea2_attribute_emergence_png_originals.zip`](https://github.com/aledelpho/diffusion-models-weight-steering-report/releases) (642 MB · 392 master PNGs for Experiment 2)
  *Upload in progress — GitHub's asset endpoint is currently returning 5xx on multi-hundred-megabyte
  transfers, so the three archives are going up by hand. Their SHA-256 sums are already published in
  [`docs/reproduce_stage7.md`](docs/reproduce_stage7.md) and were computed before upload, so they verify
  whatever eventually lands.*

  Each PNG contains its embedded ComfyUI generation graph in a `tEXt` chunk. See [`docs/asset_pipeline.md`](docs/asset_pipeline.md) for layout specifications.
* **The generation graphs**: every committed PNG carries its ComfyUI graph in a `tEXt` chunk, so dragging one onto a ComfyUI canvas reloads exactly the pipeline that made it. The same graphs are also published as plain JSON — [`data/comfy_graphs.json`](data/comfy_graphs.json) for all 370 renders individually, and [`docs/workflow/`](docs/workflow/) for the three distinct topologies, pretty-printed and annotated.
* **Re-run the attribute-emergence experiment**: [`data/attribute_emergence_recipe.json`](data/attribute_emergence_recipe.json) carries, for each of the 24 sets of Experiment 2, the exact prompt text and its `prompt_sha1`, the preset file, the model and CLIP strengths, the seed list and the output folder and filename pattern. Two of the ten prompt variants hash to `30de058455` and `95acba3b41` — the untouched G1 and G4 already published in [`data/prompts.json`](data/prompts.json) — so the hashes verify themselves. [`data/attribute_emergence.csv`](data/attribute_emergence.csv) holds the per-seed score behind every number in Experiment 2, including the renders marked `ambiguous` rather than forced to a verdict.
* **The architecture itself**: [`docs/model_structures/`](docs/model_structures/) carries the full tensor map of every base checkpoint used here — name, dtype, shape, element count — for Krea-2, Anima Base v1.0 and both text encoders, plus two architectural write-ups with block anatomy. They are derived from the safetensors headers alone and contain **no weight values**. Every displacement figure quoted in this notebook is a *relative* Frobenius norm, and recomputing one needs those shapes; without them, "verify it yourself" is a promise a reader cannot keep.
* **A note on language**: every published table — column names, condition labels, feature names — is in English. The *comments* inside the scripts are in Italian, because that is how they were written while the work was happening and rewriting them afterwards would misrepresent the record. The code itself reads fine without them.

> **On the $p$-values.** Every $p$ in `data/global_aggregation_*.csv` comes from a sign-flip permutation test on the prompt-level means. With $n \le 16$ prompts all $2^n$ sign assignments are enumerated, so the $p$ is exact and its floor is $2/2^n$ — on the 6-prompt colour-free family that floor is $0.031$, which is why **no effect of any size can clear Holm correction there**. Above 16 prompts the test samples $100\,000$ assignments, so its floor is $\approx 10^{-5}$. The estimator reports $(k+1)/(N+1)$, so a $p$ can never print as an exact `0.0` — the smallest value in the 24-prompt tables is `1e-05`, which is the resolution floor and not a measured zero.

---

## Credits, Licence & Context

* **Authoring & Tuning Tool**: [aledelpho/comfyui-arthemy-krea2-tuner](https://github.com/aledelpho/comfyui-arthemy-krea2-tuner)
* **License**: [MIT](LICENSE). The code, the data tables and the text are all free to reuse, modify and build on, with attribution.
* **Lab Notebook**: `diffusion-models-weight-steering-report`
