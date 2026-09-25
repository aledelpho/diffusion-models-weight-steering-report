# Pre-registration — Does colour carry a fingerprint of its own?

- **Written:** 2026-09-25, after `data/arm_identifiability_tests.csv` (commit `c648299`).
- **Corpus:** existing renders only. **No new renders are generated for this study.**
- **Relates to:** `docs/prereg_arm_identifiability.md`,
  `docs/prereg_palette_position.md` + Amendment 01.

---

## 0. What is already known, including the part that argues against this study

Block H established that the arm that produced an edited render is decodable from the 23
style features, on prompts never seen during fitting: 96.9% for `preset_pos` against
`rand_pos` with a scale-invariant nearest-centroid classifier, replicated on stage 9. Every
arm, including both random ones, is recognised well above chance.

Two facts from that run bear directly on this one, and one of them is unfavourable:

- The eight features with the largest separation between centroids are **all texture and
  edge statistics**. No colour feature appears among them.
- Block F found the preset's palette displacement to be **below the instrument's detection
  threshold** (+30 degrees of hue), so its colour tests were recorded as uninterpretable.

So the prior evidence points *against* colour carrying an independent signature. That is
stated here deliberately: a positive result obtained after writing down the evidence against
it is worth more, not less.

**What has never been asked:** whether colour *alone* decodes the arm. Block F asked whether
the colour displacement is **large** — a magnitude question, answered no. This asks whether
it is **consistent** — a different question, and the one that today's result shows can come
out positive where the magnitude question came out negative. A shift far too small to clear
a noise floor can still be perfectly repeatable, and a classifier reads repeatability, not
size.

**Blindness:** the primary corpus (stage 7) and the secondary (stage 9) were both used by
Block H. No third corpus with the required arms exists. The colour-only question has not
been run on either, and no colour feature value has been inspected. This is declared rather
than claimed away.

## 1. The observer's report this is aimed at

The observer (A.D.) reports specific, regional colour changes: the red leaving a figure's
lips, a cheek acquiring stripes, shadows turning toward one hue while highlights do not, one
preset tending toward the monochromatic.

Every colour measurement in this project so far is a **whole-image aggregate**. A change
confined to the shadows, or to one region, is averaged away by construction. §3 exists
because of that.

## 2. Feature sets — frozen

**Set T (texture), the comparison baseline.** The 19 style features that are not colour.

**Set C1 (colour, global).** The four existing colour features: `color_n_effective`,
`color_top4_cluster_share`, `color_cluster_entropy_norm`, `colorfulness_hs`.

**Set C2 (colour, global + position).** C1 plus the nine CIELAB moment features of
`docs/prereg_palette_position.md` §4 — mean and standard deviation of `L*`, `a*`, `b*`, and
the three correlations. These exist for stage 9 in `data/palette_position.csv` and must be
computed for stage 7; that is a re-measurement of existing renders, **no render is
generated**.

**Set C3 (colour, global + position + regional).** C2 plus the regional features of §3.

All sets use `Delta = z(edited) - z(baseline)` at identical prompt and seed, standardised
once from that corpus's baselines and applied unchanged to every cell (pitfall 33), exactly
as in Block H.

## 3. The regional colour measurement — frozen

Three luminance bands, defined on the **baseline** image's `L*` terciles and applied
unchanged to the edited image, so that a region which darkens moves band and that movement
is itself recorded.

Per band: mean `L*`, mean `a*`, mean `b*`, and the fraction of the image's pixels in it.
**3 bands x 4 numbers = 12 features.**

Free parameter: the number of bands, fixed at **3**. Sensitivity at **5**, reported; if the
verdict changes between 3 and 5 bands, the verdict is `ambiguous`.

## 4. Classifiers, validation and null — inherited unchanged from Block H

Nearest centroid by cosine (primary, scale-invariant) and multinomial logistic regression
with `C = 1.0`, no tuning (secondary). Leave **one prompt** out: 16 folds on stage 7, 8 on
stage 9. The null permutes arm labels within each (prompt, seed) group and re-runs the whole
procedure, 1000 times, `random.Random(1337)`. **No binomial test anywhere.**

Reusing Block H's machinery unchanged is what makes the colour and texture numbers
comparable. Any change to it invalidates the comparison.

## 5. The tests — pre-specified, in order

**Primary.** Set **C2**, `preset_pos` against `rand_pos`, nearest centroid, stage 7.
Chance 0.5.

**Secondary, Holm-corrected together with the primary:**

1. Set C2, 6-class, stage 7.
2. Set C3, 2-class, stage 7 — does the regional information add to the global?
3. Set C1, 2-class, stage 7 — do the four original features alone carry anything?

**The question that decides what this study means**, reported alongside and not
Holm-corrected because it is a comparison of accuracies rather than a test against a null:

> **Does colour add anything to texture?** Accuracy of set T against accuracy of
> T + C3, on the identical folds. If adding every colour feature to the texture set does not
> raise accuracy, colour carries no information the texture features did not already carry,
> whatever colour-only scores on its own.

That last point matters: colour features can decode the arm merely by correlating with
texture ones — colourfulness with edge density, for instance. Colour-only beating chance is
necessary but not sufficient.

**Replication:** everything above on stage 9, reported separately, never pooled.

## 6. Decision rules — frozen before the first fit

- **Primary above the null's 95th percentile at Holm-corrected `p < 0.05`, and T + C3 more
  accurate than T alone** -> **colour carries an independent fingerprint.** Block F's
  negative is then correctly re-read as a statement about magnitude, not about colour, and
  the instrument's blind spot is a threshold, not the colour channel.
- **Primary significant but T + C3 no better than T** -> colour is decodable but carries
  nothing of its own; it rides on texture. Reported in exactly those words.
- **Primary not significant** -> colour does not decode the arm at this corpus size, and the
  observer's colour reports are not captured by any colour measurement available. That would
  make the forced-choice test of §8 the only remaining route, and it is reported as such.
- **C3 significant where C2 is not** -> the signal is regional and global aggregates destroy
  it. This is the outcome §3 was built to be able to detect.
- **Stage 7 and stage 9 disagreeing** -> reported as the finding, no claim promoted.

## 7. The §9 guards of Block H apply unchanged

Before any verdict: if one arm's recall exceeds three times the mean of the others, the
result is **carried by one arm**; if one fold carries more than 40% of the above-chance
correct predictions, it is **fragile**. Either one, and no claim is promoted.

## 8. What this study cannot do

It cannot tell us whether what a classifier decodes from colour is what a person sees. The
observer's reports are regional and semantic — a mouth, a cheek, a shadow on a face — and
§3 approximates that with luminance bands, which is a crude stand-in for a region a person
would name.

Closing that gap needs the observer's own labels: blind pairs, same prompt and seed, judged
"same hand" or "different hands", then asking which feature set predicts those judgements.
That study is **not authorised here** and needs its own pre-registration, written before any
label is collected. This one exists partly to aim it: it should be pointed at whatever
colour is left unexplained after §5 and §6, not at everything.

## 9. Outputs

Script: `experiments/colour_identifiability.py`, plus an extension of
`experiments/measure_palette.py` to produce the stage-7 CIELAB moments and the regional
features of §3.

Data:

- `data/colour_features_regional.csv` — the §3 measurements, per render.
- `data/colour_identifiability.csv` — per fold, per arm, per feature set.
- `data/colour_identifiability_tests.csv` — observed accuracy, null mean, null p95,
  permutation p, Holm p, the T versus T + C3 comparison, guard flags and verdicts, with the
  corpus, the feature set and the classifier named in every row.

No figure is registered and no page is written in the same run that produces these files.
