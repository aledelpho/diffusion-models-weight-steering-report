# Pre-registration C69 — the bridge in the DiT: where and when the same text-encoder push splits word orders

Written 2026-10-12, **before any C69 render.** Code: `experiments/te_bridge.py` (plan, queue, reproduction gate,
count, analysis, readings, self-test) and the ComfyUI node `tools/comfyui_krea2_attnprobe` (`Krea2AttentionProbe`),
committed with this document. Plan: `data/te_bridge_plan.csv` (25 rows). Renders authorised by Alessandro on
2026-10-12.

## Question

C67 and C68 found that a text-encoder edit gives the conditioning a push that is nearly the same for every prompt
(direction cosine 0.91–0.99 across prompts, regions of about three tokens bounded by commas, stable across prompts).
Yet in C65 B the strong MLP+ edits sent the five word orders of the same prompt to different genres (scores 4–5 of 5;
notes: "dal fumetto all'anime, al cartoon"). If the push is the same, the divergence must arise in the DiT. Where
(which blocks) and when (which sampling steps)?

## Prior work, and what is new here

Cross-attention maps as a reading of where a word lands in the image are standard for U-Nets (Prompt-to-Prompt, Hertz
et al. 2022; DAAM, Tang et al. 2023). For MM-DiT, ConceptAttention (arXiv 2502.04320) reads the joint attention, but
it is written for the dual-stream blocks of Flux/SD3; Krea-2 has 28 *single-stream* blocks over one joint sequence, so
the text-to-image part has to be cut out of the full attention (what the node does). Early Semantic Commitment
(ICML 2026 workshop) and the symmetry-breaking literature (Raya & Ambrogioni 2023; Sclocchi et al. 2024) predict that
the global layout and genre are fixed in the first steps. We are not aware of a study that measures how a
text-encoder *weight* edit changes the image-to-text attention of a single-stream DiT across word orders.

## Material

Seed 3141592, the five word orders of C65 B (V1 Original … V5 Inverse), five conditions each: the baseline and four
C65 edits, chosen by the order-grid scores before any attention is seen —

* **strong** (score 5): L06 MLP +1.00, L12 MLP +1.00;
* **mild**: L10 MLP −1.00, L19 attention −1.00.

All 25 images already exist (`benchmark_prompt_order`, `benchmark_te_characters`); they are rendered again, same
workflow, with the probe between the model and the sampler.

## What is measured

At every one of the 9 steps and in every one of the 28 blocks, the node takes the queries and keys after QK-norm,
applies RoPE as the model does, and computes for each image token the softmax over **all** keys (text and image),
averaged over heads, keeping the text part. Text positions are grouped into the **clauses** of the prompt (the C68
`units(…, "clause")` rule on the C67 token ids of each order; 36 clauses per order). The image is pooled 2×2
(80×64 tokens → 40×32). Also saved: the attention mass on all text per region.

* **order divergence** of a clause = 1 − mean pairwise cosine between its maps in the five orders (clauses matched by
  text); averaged over the clauses present in all orders.
* **change vs baseline** = 1 − cosine between a clause's map under an edit and under the baseline, same order.
* **style share** = attention on the three style clauses ("realistic western comics style", "bold ink outlines",
  "hatched shadows") divided by the attention on all text.

## Gate (before anything is read)

Every C69 image must be **pixel-identical** to the existing image of the same order, condition and seed, and every
render must have left 9 attention files. The probe only reads; if it changed a single pixel, nothing below is
computed.

## Readings (fixed now)

| reading | rule |
|---|---|
| P1 | the strong edits raise the order divergence (vs baseline, mean over steps and blocks) more than the mild ones: holds if min(strong) > max(mild) |
| P2 | first step at which both strong edits exceed both mild ones in order divergence: holds if ≤ step 2 (genre fixed early) |
| P3 | the five blocks where the strong edits raise the order divergence most — reported, decides nothing |
| P4 | the strong edits move the maps away from the baseline more than the mild ones: min(strong) > max(mild) |
| P5 | **default-style hypothesis** (Alessandro, 2026-10-12, added before any render): the strong edits lower the style share more than the mild ones: max(Δ strong) < min(Δ mild) |
| P6 | attention mass on all text, per condition — reported |

P5 comes from Alessandro's remark: when the weight of the "comics" words drops, a default illustrative style
(anime, a strong dataset prior) or a stereotype can take over. The order-grid notes already describe anime under
several edits (L02 MLP+, L06 MLP+, L12 attention+, L14 attention+). If P5 holds, the genre switch goes together with
less attention on the words that name the style; if P6 also drops, the image attends less to the text overall and
the prior has more room.

## Limits

* Attention mass is not influence. The value vectors change too, so an edit can change what a clause *says* without
  changing where it is read.
* One seed, one prompt family, two edits per group. P1, P2, P4 and P5 are ordinal comparisons between 2 and 2 edits
  and give no p-value.
* The clause matching across orders is exact text; repeated clauses ("background" in V3 and V5) are matched by
  occurrence.
* Pooling 2×2 and averaging heads hide head-specific roles.
* The default-style reading in P5 does not show that the attractor is anime. That needs a genre measure on the
  images (C66, paused).
