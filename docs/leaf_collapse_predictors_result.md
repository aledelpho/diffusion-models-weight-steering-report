# C22 — what separates the nine seeds that fire? Nothing visible in the output

**Date**: 2026-09-28 · **Question**: register **C22**, raised by
[`leaf_collapse_and_blk16_result.md`](leaf_collapse_and_blk16_result.md) §2 · **Material**: the 40
arm-A renders of `benchmark_leaf_collapse`, already on disk · **Script**:
`experiments/leaf_collapse_predictors.py` → `data/leaf_collapse_predictors.csv`,
`data/leaf_collapse_clustering.csv` · **No render. Exploratory, and negative.**

---

## 1. The setup

Twenty seeds, one prompt, one edit (`Block_4 = -0.2`), and an outcome with nothing in the middle:
nine cells between chroma ratio 0.034 and 0.085, eleven between 0.518 and 1.311. The only input
that differs is the seed. The question is whether the seed announces itself in advance.

**The seed's fingerprint used here is its own unperturbed baseline**, which is a deterministic
function of it. The initial latent is not reconstructed — that means reimplementing ComfyUI's RNG
exactly, and a near-miss would be indistinguishable from a null result. This is a proxy and is
reported as one.

## 2. Twelve features, none of them survives

Listed before any was computed, not chosen after seeing which separates. Exact two-sided
Mann-Whitney on 9 against 11, Bonferroni over twelve.

| feature | fire | quiet | p | corrected |
|---|--:|--:|--:|--:|
| centroid y | 0.48716 | 0.48092 | 0.046 | 0.557 |
| orientation | 90.42° | 89.93° | 0.067 | 0.809 |
| centroid x | 0.49974 | 0.50033 | 0.201 | 1.000 |
| contrast | 0.03464 | 0.03928 | 0.331 | 1.000 |
| grain | 0.00181 | 0.00232 | 0.370 | 1.000 |
| foreground share | 0.12952 | 0.14856 | 0.412 | 1.000 |
| solidity | 0.99995 | 1.00000 | 0.450 | 1.000 |
| edge density in leaf | 0.01283 | 0.01459 | 0.656 | 1.000 |
| mean value in leaf | 0.35439 | 0.34953 | 0.824 | 1.000 |
| hue | 37.73° | 38.63° | 0.882 | 1.000 |
| elongation | 1.576 | 1.563 | 0.882 | 1.000 |
| **chroma** | **0.50326** | **0.50309** | **1.000** | 1.000 |

**Zero of twelve survive.** One feature below 0.05 raw is exactly what twelve tests produce by
chance, and it is the one with the least mechanistic claim on the outcome.

**The obvious hypothesis dies first.** If the edit multiplied chroma down and the seeds already
near the edge fell off, baseline chroma would separate the groups. Its means are **0.50326 against
0.50309** and the two sets are completely interleaved — the lowest-chroma baseline of the twenty
fires, the second lowest does not. Nothing about how colourful the leaf was going to be predicts
whether the colour survives.

## 3. Nor is there a joint structure

Twelve univariate tests can miss something that exists only in combination. Multivariate, and not
circular — it looks only at the baselines, which know nothing about the outcome: similarity is the
Pearson correlation of the 8× downsampled, z-scored luminance (shape and layout, blind to tone and
colour), the statistic is mean within-group similarity pooled over both groups, and the null is
**all 167 960 ways of splitting twenty seeds 9/11, enumerated exactly**.

> observed 0.84985, **exact permutation p = 0.535**.

Dead centre of the null. The nine do not occupy a region of seed space that the baselines can see.

## 4. What the edit does is the same in all twenty

| | n | IoU with own baseline | |
|---|--:|--:|---|
| fire | 9 | **0.877** (min 0.740) | |
| quiet | 11 | **0.895** (min 0.764) | |

**The drawing is preserved identically in both groups.** The edit does the same thing to the leaf
in all twenty seeds; in nine of them it additionally takes the colour away. The 108.6° mean hue
shift of the firing group is **not a finding** — hue is undefined at chroma 0.04 and that number is
an artefact of measuring an angle on a grey image. It is recorded here only so it is not quoted
later.

## 5. What this rules out, and what is left

**Ruled out:** that the collapse is a property of the image the model was going to draw. Nothing in
the endpoint of the unperturbed trajectory — its colour, its shape, its texture, its position, or
the twelve of them jointly — distinguishes the seeds that will lose their colour from the ones that
will not.

**What is left** is that the collapse lives in the *trajectory*, not its endpoint: the edit and the
sampling path interact somewhere in the middle of denoising, and by the time the unperturbed image
exists the evidence is gone. That is consistent with the shape of the outcome — bimodal with an
empty gap, a bifurcation rather than a threshold on any smooth quantity.

**Cheap next steps, in order of information per render:**

1. **Dose ladder on the firing seeds.** The same nine seeds plus nine quiet ones at doses 0.050,
   0.080, 0.120, 0.200. If the switch has a per-seed dose threshold, that is the bifurcation
   parameter and it is measurable. 72 renders.
2. **Intermediate-step decoding.** Decode the latent at steps 3, 5 and 7 for four firing and four
   quiet seeds. If the two groups separate before the last step, the trajectory hypothesis is
   testable directly and the separation point is the answer. Needs a workflow change, not just a
   queue.
3. Only after those: reconstructing the initial latent, which is the expensive and fragile route.

## 6. Limits

Twenty seeds, one prompt, one dose, one edit. A predictor with an effect size smaller than this
design can see would be missed — with 9 against 11, only a large separation is detectable, and
"no predictor" here means "no large predictor among these twelve". The baseline is a proxy for the
seed and not the seed itself.
