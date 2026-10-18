# Pre-registration C88 — can the destination of a text-encoder edit be predicted from its push on the conditioning?

Written 2026-10-18 by Claude, **before any computation on these data for this question.** No renders: existing
encodes and existing genre labels only. Proposed by Alessandro (2026-10-18): the destination of an edit may look
random because it depends on the prompt, but in a predictable way.

## 1. Question

C65 and C73 found that one edit does not move different prompts the same way, and C71 that the push does not point
toward the text direction of "anime". Two readings remain:

* **Edit decides:** each edit has its destination; how a prompt deviates from it is not readable from the push.
* **Prompt modulates, predictably:** the push of an edit *on that prompt* carries where the picture goes, so pushes that
  look alike lead to the same genre, whatever the edit.

## 2. Data (fixed now)

Units are (edit, prompt) pairs. Each has one conditioning push, `dmean` (the mean over tokens of edited minus original
conditioning, 12 taps × 2560, saved by `tools/comfyui_krea2_probe`; the encoding does not depend on the seed), and
genre labels by Alessandro at two seeds.

* **Orders (C70):** the elf in five word orders × 20 edits = 100 units; labels `data/te_genre_alessandro.csv`
  (grids `te_genre_1234567`, `te_genre_3141592`, columns g1–g5 = V1–V5); pushes
  `Text2Img/benchmark_te_conditioning/order/<order>_<edit>.npz`.
* **Characters (C73):** 7 portraits × 11 edits = 77 units; labels `data/te_fallback_genre_alessandro.csv` (grids
  `fb_edits_<char>`, g1–g2 = the two seeds); pushes `Text2Img/benchmark_te_conditioning/chars/<char>_<edit>.npz`.

Empty labels and "rotto" are left out. Each (unit, seed) label is one case: up to 200 + 154.

## 3. Predictors (leave one prompt out)

For each held-out prompt (one word order, or one character), predictors are built from the other prompts of the same
data set only:

* **MAJ:** the most frequent genre among the training cases.
* **EDIT:** the most frequent genre of the *same edit* on the training prompts (ties → MAJ).
* **PUSH (primary):** 1-nearest-neighbour over all training units (any edit) by cosine similarity of the feature
  vector; the prediction is the neighbour's majority genre over its two seeds (ties → that neighbour's first seed).
  Feature: `dmean` with each tap normalised to unit length, then concatenated (12 × 2560), so every tap counts once.
* **SIZE (reported):** the same 1-NN on the 12 per-tap mean relative push sizes (`rel` averaged over tokens).

Accuracy = share of cases whose label equals the prediction, pooled over both data sets and also per data set.

## 4. Decision rules

1. **Prompt modulates, predictably:** PUSH − EDIT ≥ +0.10 pooled, **and** a permutation test (labels shuffled across
   prompts within each edit, 1000 times, seed 8888) gives p < 0.05 for that difference.
2. **Edit decides:** |PUSH − EDIT| < 0.05 and EDIT − MAJ ≥ +0.15.
3. Otherwise inconclusive.

Reported: the same split per data set; accuracy of PUSH on the cases where EDIT is wrong (the prompt's deviation);
SIZE against PUSH.

**Tool rule.** If rule 1 holds, the push on the conditioning, computable without rendering, predicts where an edit will
take a prompt: a tool can preview and choose edits per prompt. If rule 2, the tool can rely on a per-edit destination
and treat prompt deviations as noise.

## 5. Limits known in advance

One labeller; genre labels are coarse; the orders set is one character; 1-NN is a deliberately simple predictor, so a
negative result does not exclude a predictor that is better.

Script: `experiments/te_predict_destination.py` (written after this file, committed with it).
