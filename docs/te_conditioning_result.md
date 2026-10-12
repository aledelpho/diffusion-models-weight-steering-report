# C67 — result: what a text-encoder edit does to the conditioning, token by token (2026-10-12)

Pre-registration `docs/prereg_te_conditioning.md` + amendment 1 (float16 floor of the gate). 721 encodes, no images.
Gate (amended): baseline encoded twice identical; the two null edits bit-identical, maximum 0.000364 ≤ 2⁻¹¹; the
active check ≥ 0.048 everywhere it reaches → PASS. Changes ≤ 2⁻¹¹ are read as zero. Data:
`data/te_conditioning_edits.csv`, `te_conditioning_tokens.csv`, `te_conditioning_tests.csv`. Logit lens: pending
(GPU PC).

## Tests

| test | value | rule | verdict |
|---|---|---|---|
| E1 — the size of the conditioning change predicts how much the elf picture changed (C64, ±1.00) | ρ = 0.71 (n 140, p < 0.001); AUC for style changed vs unchanged 0.80 | ρ ≥ 0.50 | **supported** |
| E2 — word-order dependence: disagreement between the five orders in *which words* an edit moves predicts the 1–5 scores | ρ = −0.35 (n 20, p = 0.13) | ρ ≥ 0.50 | **not supported** (sign opposite) |
| E3 — characters: share of the change on the shared style words predicts "same direction" | ρ = 0.05 (n 34, p = 0.77) | ρ ≥ 0.40 | **not supported** |

## Reading

1. **The conditioning measures the size of the change well (E1).** The mean relative change over the words and
   the taps an edit can reach ranks the 140 elf edits as the eye ranked the pictures (ρ 0.71) and separates
   style-changed from unchanged pictures (AUC 0.80). It is the first instrument in this project that tracks the eye
   on text-encoder edits without looking at a picture. (Partly expected: earlier layers reach more taps and also
   change the picture more.)
2. **The same ordering as the eye, in numbers.** Median mean relative change over the 35 layers: MLP +1.00 0.89,
   attention +1.00 0.29, MLP −1.00 0.18, attention −1.00 0.11; at ±0.10 about 0.02–0.05. Doubling the MLP moves the
   conditioning three times more than doubling the attention and five times more than removing the MLP — the
   asymmetry C64 phase 1 saw by eye.
3. **q + k alone change nothing the DiT receives.** The three q+k-only edits (L05, L17, L29 at +1.00) are at the
   float16 floor at every position: QK-norm (RMS normalisation of queries and keys inside the attention) cancels a
   scaling of the q and k projections. The ~10/255 pixel difference C64 found for these edits does not come from the
   conditioning; its source is elsewhere (open).
4. **Which words move.** Attention edits put slightly more of their change on punctuation and function words than
   their share of the prompt (median 0.39–0.40 against 0.34 of the word slots); MLP edits stay at the prompt's share
   (0.34–0.36), and their most-moved words are content words (fist, leather, hair, eyepatch, gauntlet, "close",
   "upper"). The two L00 edits at −1.00 that make the picture render the prompt as text move a few content words
   enormously ("dark" 4.4, "jacket" 4.0, "viewer" 3.8 for attention; "gauntlet" 2.8 for the MLP).
5. **Why E2 and E3 fail.** The order dependence and the character exceptions the eye sees are **not** written in
   *which words* the edit moves: a strong MLP+ edit moves the same words in every order (its profile agrees across
   orders, which is why E2 comes out negative), yet the pictures go to different genres. Together with C65 this
   places the divergence downstream — in how the DiT reads a conditioning shifted as a whole — or in the direction
   of the change (stored as cosine and mean change, not yet analysed), not in its distribution over words.

## Limits

Relative change mixes direction and size; directions are not analysed here. The word grouping is a fixed rule. One
prompt per family. E1 is partly confounded with layer depth.

## Next (not decided)

* The logit lens (pending) — what each moved token turns into, and what L00 −1.00 does to the words it renders.
* The direction of the change: whether edits that the eye calls coherent across characters (C65) move the shared
  style words in the same direction in every prompt (cosine of the per-word change across prompts).
* E1 as an instrument: a cheap, image-free predictor of how much an edit will change the picture, to choose edits
  and doses before rendering.
