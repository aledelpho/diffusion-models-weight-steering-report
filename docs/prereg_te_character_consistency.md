# Pre-registration C92 — do characters deviate from an edit's usual destination consistently across edits?

Written 2026-10-18 by Claude, **before any computation for this question.** No renders. Replaces the first wording of
C92 ("predict the destination from the prompt's fallback"), which C73 H2 already tested and did not support (switched
pictures land on the character's fallback 0.28 against 0.27 by chance).

## Question

Alessandro's hypothesis: the destination of a text-encoder edit depends on the prompt in a predictable way. C88 showed
the push itself does not carry it. Here: if each character has its own consistent bias (one drifts toward painting,
another toward cartoon whatever the edit), then how a character behaved under *other* edits predicts where it goes
under this one.

## Data (fixed now)

C73 labels (`data/te_fallback_genre_alessandro.csv`, grids `fb_edits_<char>`, two seeds each): 7 characters × 11 MLP
edits; empty labels and "rotto" left out.

## Predictors (leave one cell out: target = one character × one edit)

* **EDIT:** the most frequent genre of that edit on the other six characters.
* **CHAR (primary):** for each genre, its share among the target character's labels on the *other ten edits* plus its
  share among the target edit's labels on the *other six characters*; the prediction is the genre with the highest sum
  (ties → EDIT). *(A first version, the majority among the three most similar characters, failed the synthetic
  selftest — it does not use the character's own bias — and was replaced before any real data was read.)*
* **MAJ:** most frequent genre overall, excluding the target cell.

## Rule

* **Characters deviate consistently:** CHAR − EDIT ≥ +0.10 in accuracy, and a permutation test (labels shuffled across
  characters within each edit, 1000 times, seed 9292) gives p < 0.05.
* **No consistent deviation:** CHAR − EDIT ≤ 0.02.
* Otherwise inconclusive.

**Tool rule.** Yes: a few test edits on a prompt tell how it will react to the others (a per-prompt calibration). No:
each edit's effect on a new prompt cannot be anticipated from its reaction to other edits.

Limits: 7 characters, 11 edits, one labeller, coarse genres. Script: `experiments/te_character_consistency.py`.
