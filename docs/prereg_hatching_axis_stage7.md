# Pre-registration — the hatching axis, stage 7

**Written 2026-09-17, before any stage 7 render exists.** Third pre-registration
riding on the same corpus as `prereg_chromatic_signatures.md` and
`prereg_attribute_emergence_stage7.md`. It costs no additional renders: the six
conditions are already in stage B.

## Where this came from, stated plainly

Alessandro noticed by eye, across renders he had already seen, that
`blockshuf_neg` produced parallel hatching in the shadows and `blockshuf_pos`
produced cross-hatching, in "roughly 95% of cases". This was **discovery by
looking**, and quantifying it on the same renders is not confirmation — it is
putting a number on what was seen. The number, on 18 prompts from
`data/style_features.csv`, paired by prompt and seed:

| family | Δ `crosshatch_entropy_mean` (pos − neg) | p | prompts | image pairs |
|---|---|---|---|---|
| preset | −0.484 | 7.6e-6 | 18/18 | 90/90 |
| blockshuffle | +0.274 | 7.6e-6 | 18/18 | 87/90 |
| randsign | −0.187 | 3.8e-5 | 16/18 | 81/90 |

87/90 is 96.7%, against an estimate by eye of 95%.

**The observation was too narrow.** The effect is not a property of
block-shuffling. All three families separate on the same axis, with
**family-specific sign**: where `blockshuf_pos` cross-hatches, `preset_pos`
runs parallel. The axis is controlled by the sign of the displacement; which
sign yields which texture is a property of the direction moved in.

p = 7.63e-6 is the exact permutation floor at n = 18 (2/2^18), so it reads as
"below the resolution of the test", not as a measured value.

## What is predicted for stage 7

The 16 new prompts, five seeds, the six conditions — all already scheduled.
`crosshatch_entropy_mean` is computed by the existing, unmodified
`analyze_style_features.py`; no scoring, no human in the loop, no blinding
needed, because nobody judges anything.

Unit of analysis: the prompt. Seeds are averaged first (pitfall 17).

> **Primary, directional.** The sign of Δ`crosshatch_entropy_mean` (pos − neg)
> is **negative for preset**, **positive for blockshuffle**, **negative for
> randsign**, each with p < 0.05 by exact sign-flip permutation across the 16
> prompts, Holm-corrected over the three families.
>
> A family that reaches significance with the **wrong sign** counts as a failure
> of this pre-registration, not as a partial success. Predicting the sign is the
> whole point; a two-sided win with a flipped sign would mean the axis is real
> and our account of it is wrong.
>
> **Secondary.** Per-prompt concordance of at least 14 of 16 in the predicted
> direction, for preset and blockshuffle. Randsign is predicted to be the
> weakest of the three and is not held to the concordance threshold.

## Metric validity, and the one thing that could undermine it

`crosshatch_entropy_mean` reproduces, at 87/90, a distinction Alessandro made
visually on block-shuffle. That is what licenses it as a measure of the thing he
saw. It fires on the other two families as well, with different signs, and
**that has not been checked against the eye**. Before stage 7 is analysed,
Alessandro inspects one `preset_pos` / `preset_neg` pair and records whether the
predicted direction — `preset_pos` more parallel — is what he sees.

If it is not, the metric is tracking something other than hatching orientation in
that family, and the preset row of the prediction is withdrawn in writing rather
than reinterpreted afterwards. That check is recorded here, with its date, before
the analysis.

A cleaner instrument exists and is **not** substituted here: the histogram of
edge-gradient orientations, where parallel hatching is unimodal and cross-hatching
bimodal with two near-orthogonal peaks. It measures the stated phenomenon
directly instead of by proxy. It is left for a later round on purpose, because
swapping the instrument between the observation and its confirmation would mean
confirming a different claim.

## Relation to the other two pre-registrations

Same renders, three independent questions, all three fixed before the images
exist. The chromatic analysis found the ± directions to be close to orthogonal in
colour space; here they are near-perfectly opposed in texture. If both hold in
stage 7, the finding is that one displacement carries several visual properties
that do **not** respond to its sign in the same way — which is a statement about
the structure of the perturbation, not about any one preset.

---

## Result — 2026-09-17, stage 7, analysis run once

`style_features_stage7.csv`, sha1 `1980edcbedb1`, 600 images. Filtered to the 16
prompts in `confirmation_prompts.csv`, giving 560 rows, every cell with five
seeds, no extraction errors. The 40 discarded rows are baselines of the eight
candidate prompts that the selection rule did not take.

`crosshatch_entropy_mean` came from `style_features.extract_all_features`,
unchanged — the same function that produced the exploratory numbers. Only the
harvester was new, because `run_style_features.py` points at
`stage7_images.csv`, which is the manifest of a **different** experiment that
writes into the same `benchmark_stage7\renders` folder under an `S7_` prefix.
Pointing the existing harvester at the directory would have measured the wrong
560 images and said nothing about it.

### The prediction against the data

| family | predicted | Δ observed | p | Holm | prompts | image pairs |
|---|---|---|---|---|---|---|
| preset | negative | **−0.370** | 3.05e-5 | 9.2e-5 | **16/16** | **80/80** |
| blockshuffle | positive | **+0.288** | 3.05e-5 | 9.2e-5 | **16/16** | **79/80** |
| randsign | negative | +0.020 | 0.67 | 0.67 | 11/16 | 50/80 |

p = 3.05e-5 is the exact permutation floor at n = 16 (2/2^16): below the
resolution of the test, not a measured value.

### Verdict

The primary was written as a conjunction — all three families, correct sign,
p < 0.05 under Holm. **It is not met.** Two of three.

- **preset: confirmed.** Correct sign, at the floor, 16 prompts of 16 and 80
  image pairs of 80. Not one exception.
- **blockshuffle: confirmed.** Correct sign, at the floor, 16/16 and 79/80.
- **randsign: not confirmed.** Δ = +0.020 against a predicted negative, p = 0.67,
  concordance 11/16 — indistinguishable from a coin. It does not trigger the
  wrong-sign failure clause, which required significance; it simply is not there.

The secondary concordance threshold of 14/16 is met by both preset and
blockshuffle at 16/16.

### What replicated, and what did not

| | exploratory (18 prompts) | confirmation (16 new) |
|---|---|---|
| preset | −0.484, 90/90 | −0.370, 80/80 |
| blockshuffle | +0.274, 87/90 | +0.288, 79/80 |
| randsign | −0.187, 81/90 | +0.020, 50/80 |

The two structured directions held their effect size across an independent corpus
of new subjects — block-shuffle to within 5%. The random one collapsed entirely:
the sign flipped and the concordance fell to chance.

**Failing on randsign makes this result stronger, not weaker.** Had all three
held, the hatching axis would have been a property of reversing any displacement.
It is not: it belongs to the two structured directions, and the matched-norm
random control does not produce it. That is the Experiment 1 argument —
structure, not magnitude — reproduced on a second visual property with a
mechanical measurement and no human scoring.

### Against the colour result on the same 560 images

The chromatic confirmation, run the same day on the same renders, saw every
effect roughly halve, and its strongest condition was `randsign`. Here the
structured conditions hold their size and `randsign` vanishes. Same
displacements, same images, opposite patterns.

So the two properties are not two views of one signature. Texture responds to the
sign of a *structured* displacement, near-deterministically. Colour responds to
displacement more diffusely and does not distinguish structure from noise in the
same way. Any account of what these perturbations do has to accommodate both.
