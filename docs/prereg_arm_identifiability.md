# Pre-registration — Is the edit *recognisable*, even when it is small?

- **Written:** 2026-09-25
- **Status at writing:** no script exists. No classification of any kind has been run on
  this project's data.
- **Corpus:** existing renders only. **No new renders are generated for this study.**
- **Relates to:** `data/arm_coherence_tests.csv`, `data/palette_tests.csv`,
  `docs/prereg_seed_stability.md`.

---

## 0. Where this question came from

On 2026-09-25 the observer (A.D.) looked at three renders of the same prompt and seed —
baseline, calibrated preset, norm-matched random control — and said that with a list of
everything that changes he could tell **which** preset had been used.

That is a different claim from every question this project has asked so far. All previous
studies measure **how far** the edit moves the output and **whether the direction repeats**.
This one asks whether the edit leaves a **recognisable signature**.

The two can come apart completely. A signal can be tiny in amplitude and perfectly
identifiable, the way a fingerprint is. `data/palette_tests.csv` records preset
displacements below the colour instrument's detection threshold; `data/arm_coherence.csv`
records cross-prompt cosines near 0.21. Neither of those rules out identifiability, because
neither measures it.

## 1. The question, stated as a test

Given the displacement of an edited render from its own baseline, at identical prompt and
seed, can the arm that produced it be predicted **on prompts never seen during fitting**,
better than chance?

## 2. Corpus and representation — frozen

**Primary: stage 7.** `data/style_features_stage7.csv` holds 24 prompts, of which **16**
carry `baseline` plus all six arms (`preset_pos`, `preset_neg`, `blockshuf_pos`,
`blockshuf_neg`, `rand_pos`, `rand_neg`) at 5 seeds each. The other 8 are baseline-only and
are excluded. **16 prompts x 5 seeds x 6 arms = 480 edited cells, 6 classes.**

**Secondary: stage 9.** Only the eight style prompts `S1`–`S8` carry `baseline` plus the six
arms used by every other stage-9 study (`preset_pos_1x`, `preset_pos_2x`,
`blockshuf_neg_1x`, `blockshuf_neg_2x`, `rand_pos_1x`, `rand_pos_2x`): **8 x 5 x 6 = 240
edited cells**. `chaos_edges_v2` exists on four I-prompts only and is **excluded** — no
prompt in stage 9 carries all seven arms. Reported separately. **The two corpora are never
pooled into one fit** — their arms are not the same objects.

Representation, per edited cell:

```
Delta(arm, P, s) = z(edited) - z(baseline)      identical prompt and seed
```

23 style features, standardised once using the mean and standard deviation of that
corpus's **baselines**, applied unchanged to every cell (pitfall 33).

## 3. Classifiers — pre-specified, not chosen after looking

**Primary: nearest centroid, cosine.** For each arm, the mean `Delta` over the training
prompts; each held-out cell is assigned to the arm whose centroid it is closest to by
cosine. **It has no hyperparameters**, which is the point: there is nothing to tune until
it works.

**Secondary: multinomial logistic regression**, L2, `C = 1.0`, `max_iter = 2000`, fixed.
No grid search, no tuning, ever. If the two classifiers disagree, both are reported and
the nearest centroid is primary.

No other classifier is fitted. If one is tried, it is reported as an unplanned exploration
and cannot support a claim.

## 4. Validation — leave one prompt out

**16 folds** on stage 7 (8 on stage 9). Each fold fits on the cells of the other prompts
and predicts the 30 held-out cells (5 seeds x 6 arms) of the remaining prompt.

**Random cross-validation is forbidden.** It would leave cells of the same prompt on both
sides of the split and inflate accuracy by leaking the scene. The claim is about
generalising to a new scene, so the fold must be a scene.

Statistic: overall accuracy over all 480 held-out predictions (240 on stage 9). Reported alongside the
6 x 6 confusion matrix and per-arm recall.

## 5. The null — permutation, never a binomial test

The 480 predictions are **not independent**: six share a prompt and a seed, thirty share a
prompt. A binomial test against `1/6` would be wrong and must not appear anywhere.

The null permutes the **arm labels within each (prompt, seed) group** — the six cells of a
group exchange labels among themselves — and then re-runs the entire leave-one-prompt-out
procedure. This destroys arm identity while preserving prompt structure, seed structure and
class balance exactly.

**1000 permutations**, `random.Random(1337)`, seed recorded in the output.

`p` = the fraction of permuted accuracies greater than or equal to the observed accuracy.
The null's mean and 95th percentile are reported next to the observed value, always.

## 6. The secondary contrast, pre-specified

The two-class question this project keeps arriving at: **`preset_pos` against `rand_pos`
alone**, same representation, same classifier, same leave-one-prompt-out, same permutation
null. Chance is 0.5.

Holm correction across the two tests (6-class and 2-class) within each corpus.

## 7. Decision rules — frozen before the first fit

- Accuracy above the null's 95th percentile at Holm-corrected `p < 0.05` -> **the arm is
  identifiable.** The observer's claim is supported: the edit leaves a decodable signature
  even where its displacement is small and its cross-prompt cosine is low. This would be
  the first positive result for arm-specific structure in this project, and it would
  **not** contradict the earlier negative results — it would show they measured a different
  thing.
- Not above -> **no decodable arm identity in this feature space.** Stated exactly that
  way. See §8: this is as much a result about the features as about the edits.
- 6-class and 2-class disagreeing, or primary and secondary classifier disagreeing ->
  `ambiguous`, both reported in full, no claim promoted.
- Primary (stage 7) and secondary (stage 9) disagreeing -> reported as the finding.

**If the classifier works**, the per-feature separation between centroids is reported as a
descriptive table — which features carry the signature. Descriptive only, no test, no
p-value. It exists so the observer can check whether what the numbers point at resembles
what his eye reports.

## 8. The limitation that has to be stated first, not last

The 23 features are **texture and colour statistics**. They do not represent objects,
regions or semantics. The observer's specific reports — "stripes appeared on the cheek",
"the shadows became geometric", "the red left the lips" — have no column among them; at
best they leave a faint trace in an aggregate.

Therefore a negative result here means "**not decodable from these 23 numbers**", never
"no signature exists". Any page citing a negative result from this study says so in the
same sentence, not in a footnote. Testing a richer representation is a separate study that
is not authorised here.

## 9. What would kill this study

- The confusion matrix shows accuracy carried by one arm only — typically the
  largest-displacement arm, which in stage 9 is `blockshuf_neg_2x`. "One arm is loud" is
  not "the arms are identifiable". If a single arm's recall exceeds the mean recall of the
  others by more than a factor of three, the result is reported as **carried by one arm**
  and no general claim is promoted.
- Accuracy varies wildly across folds, meaning a couple of prompts carry it. Per-fold
  accuracy is reported; if any single fold's contribution exceeds 40% of the total
  correct predictions above chance, the result is **fragile** and no claim is promoted.

## 10. Outputs

Script: `experiments/arm_identifiability.py`.

Data:

- `data/arm_identifiability.csv` — per fold and per arm: accuracy, recall, support.
- `data/arm_identifiability_confusion.csv` — the confusion matrices.
- `data/arm_identifiability_tests.csv` — observed accuracy, null mean, null p95,
  permutation p, Holm p, verdict, corpus and classifier named in every row.
- `data/arm_identifiability_features.csv` — the descriptive per-feature separation, written
  only if §7 returns identifiable.

No figure is registered and no page is written in the same run that produces these files.
