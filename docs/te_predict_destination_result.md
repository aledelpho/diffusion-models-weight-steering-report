# C88 result — predicting where an edit goes from its push on the conditioning

2026-10-18. Pre-registration `docs/prereg_te_predict_destination.md`; script `experiments/te_predict_destination.py`
(both committed in 86a205d before the run; afterwards only the render-root path was changed so the script finds the
encodes on the Linux mount). Outputs `data/te_predict_tests.csv`, `data/te_predict_cases.csv`. No renders.

## Data as found (amendment, written after the run, changes no rule)

The pre-registration expected genre labels at two seeds for the word orders. Only seed 3141592 is labelled
(`te_genre_1234567` is empty), so the orders contribute 100 cases, not 200. One character unit has no labels
(gnome, L12). Totals: 176 units, 252 cases (orders 100, characters 152).

## Verdict

| predictor (leave one prompt out) | pooled | orders | characters |
|---|---|---|---|
| MAJ, most frequent genre | 0.472 | 0.500 | 0.454 |
| EDIT, the same edit's usual genre on the other prompts | 0.583 | 0.730 | 0.487 |
| **PUSH**, nearest push direction (any edit) | **0.587** | 0.740 | 0.487 |
| SIZE, nearest per-tap push size (reported) | 0.579 | 0.710 | 0.493 |

* **Rule: inconclusive.** PUSH − EDIT = +0.004 (permutation p = 0.37): the push adds nothing to knowing which edit it
  is. "Edit decides" needed EDIT − MAJ ≥ +0.15 and got +0.111, so neither branch is met.
* **Why PUSH equals EDIT.** In **252 of 252** cases the nearest push is the *same edit* on another prompt. The mean push
  of an edit is a fingerprint of the edit: it barely depends on the prompt, so it cannot carry how a prompt deviates.
* Where the edit's usual genre is wrong (105 cases), PUSH is right in 0.21, MAJ in 0.27: no signal there.
* On the characters, even the edit's own destination barely beats the majority (0.487 against 0.454): across
  characters an edit's destination is weakly predictable at all, as C65 and C73 found.

## Reading

Alessandro's hypothesis (the destination depends on the prompt in a predictable way) is **not refuted** by this: it
is not testable with this feature. The prompt-specific part of where a picture goes is not in the direction of the mean
push, which is almost the same on every prompt. It must come from what the push meets: the prompt's own conditioning
and its priors (the fallback without style words, C73; the priors of single phrases, C72), or the per-token
structure that the mean hides. That is a new hypothesis, not tested here: predict the destination from the edit
*and* the prompt's own fallback.

## Limits

One labeller; coarse genre labels; one seed for the orders; a deliberately simple 1-NN predictor on the mean over
tokens.
