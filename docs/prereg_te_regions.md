# Pre-registration C68 — how large are the regions of the prompt that a text-encoder edit pushes the same way?

Written 2026-10-12, **before any C68 encode.** No images. Code: `experiments/te_regions.py` (plan, queue, gate,
analysis, self-test); probe node `tools/comfyui_krea2_probe` with a new optional input `taps` (keeps only the given
tap indices in mode "full").

## Background and question

C67 found that each text-encoder edit pushes the *mean* conditioning in its own direction, almost the same for every
prompt (0.91–0.99 across word orders, characters and the watercolour), while the eye sees different genres for
different orders and characters. An exploratory look at the elf (`data/te_conditioning_regions_*.csv`) showed that,
inside one prompt, its sentences are pushed less alike (median 0.74) than the whole prompt is across prompts.
Hypothesis (Alessandro): the shared push is the same everywhere, but the part of the push specific to each region of
the prompt changes with the prompt, and that is where the divergence comes from. Question: **how large are these
regions?**

## Material

The 20 C65 edits on the five word orders of the elf and on the seven comic characters: 240 encodes, stored in full
for the last three taps (layers 29, 32, 35; every one of the 20 edits reaches them), plus one edit encoded twice.
The baselines are the C67 full files (all taps). Change = edited − baseline; **residual** = change minus its mean
over the prompt's positions (the shared push removed); template tokens dropped.

**Units** (fixed rules in `units()`): *clause* = run of tokens ending at a comma, full stop, colon or newline;
*sentence* = run ending at a full stop, colon or newline; *word* = the C67 word grouping. Units are matched across
word orders by their text (and occurrence); across characters only the frame units present in all seven prompts are
used (Western comics style, close-up portrait, frontal view, white background, simple background).

## Gate

The edit encoded twice is identical; on 10 edits the relative change recomputed from C68 files agrees with the C67
diff files within 2 × 2⁻¹¹ (both are limited by float16). Otherwise stop.

## The answer to "how large"

**Size** (reported, deciding nothing): for each prompt, the mean cosine between residuals of tokens at distance
k = 1 … 40; the **half-life** = the first k at which it falls to half its value at k = 1. Per edit the median over
the 12 prompts; the median and range over edits are the answer, in tokens (for scale: a clause of these prompts is
about 6 tokens, a sentence about 25).

## Tests

| test | measure | rule |
|---|---|---|
| H1 — regions exist (replication on 12 new prompts) | per edit: mean cosine between the clause-level changes inside a prompt (five orders) vs the C67 agreement of the whole-prompt change across orders | lower in ≥ 16 of 20 edits |
| H2 — region boundaries follow the punctuation | per edit: for token distance 1–8, mean residual cosine of pairs inside one clause minus pairs across clauses | positive in ≥ 15 of 20 edits, one-sided sign test p < 0.05 |
| H3 — the word-order dependence lives in the region residuals | per edit: 1 − mean cosine of matched clause residuals across the five orders, vs Alessandro's 1–5 scores (seed 3141592) | Spearman ρ ≥ 0.50 (sentence and word level reported) |
| H4a — characters | per edit: agreement of the frame residuals across the seven characters vs "same direction" (yes 2 / partly 1 / no 0) | ρ ≥ 0.40 |
| H4b — exceptions | per sheet: a character's frame residual against the mean of the other six, "follows" vs "another way" | AUC ≥ 0.70 |

## Limits

Three taps only (the last); a region effect that exists only at early taps is not seen. Units are punctuation-based,
not semantic. H3–H4 use the same eye labels as C67 (one observer); H3 rests on 20 edits. The residual removes the
mean push over the whole prompt, so a region that dominates the prompt also dominates that mean.
