# C62 — a noise measure that agrees with the eye: pre-registration

2026-10-11. Written before any candidate measure was computed on either set. No renders. Asked for by
Alessandro. Motivation: three automatic measures failed against the eye on the noise that matters (C58:
Immerkær; C59: page 05's HF and a band-pass), and every noise statement of results page 29 rests on one
observer. A measure that reproduces his blind labels would make later tests cheaper and less dependent on him.

## Labels (already committed, blind)

* **Development set — C59** (`data/split_atlas_eye_tally_alessandro.csv`, key `data/split_atlas_eye_key.csv`):
  168 sheets at seed 2718281, each the same edit on three prompts. Each image of a sheet takes the sheet's
  label; sheets marked "non in tutti e tre" are left out. **Positive** = noise class (`chiazze`, `grana`,
  `collasso`, `retino`) at medium or stronger (≥ 2). Negatives include clean sheets and sheets with only
  structural artefacts.
* **Test set — C60** (`data/comic_form_eye_tally_alessandro.csv`): the 180 edited images, each with its own
  blind damage label; **positive** = damage ≥ medium. Baseline images are not scored (their ratio to
  themselves is trivially zero). 88 positives, 92 negatives. Never used before this document for any
  measure in the candidate list below except M1, whose C60 value has not been computed.

Only medium and stronger counts, because "slight" did not reproduce in either eye pass.

## Candidates (fixed now; every one is edit against its own baseline, same prompt and seed)

gray = luminance 0-255, float. Flat mask = pixels of the **baseline** whose Sobel gradient magnitude, blurred
with σ = 4, is below the baseline's own 30th percentile (where a drawing or a photo has no edges: skies,
walls, skin). DoG(s) = GaussianBlur(gray, s) − GaussianBlur(gray, 2s). All blurs OpenCV, ksize (0,0).

| id | measure | score |
|---|---|---|
| M1 | page 05 HF = std(gray − blur 1.5), whole image | \|log ratio\| (the comparator) |
| M2 | band = std(blur 2 − blur 8), whole image | \|log ratio\| |
| M3 | Immerkær σ (C58), whole image | log ratio |
| M4 | HF inside the flat mask | log ratio |
| M5 | band inside the flat mask | log ratio |
| M6 | max over s ∈ {1, 2, 4, 8} of the log ratio of std(DoG(s)) inside the flat mask | as is |
| M7 | colour high-pass inside the flat mask: std(x − blur 2) for CIELAB a* and b*, mean of the two | log ratio |
| M8 | max(M5, M6, M7) | as is |

## Selection (development set only)

The candidate with the highest AUC on the development set is **the chosen measure**; ties within 0.005 go to
the lower id. Its threshold is the one maximising Youden's J on the development set. Both are written to
`data/noise_metric_dev.csv` and committed **before** the test set is scored.

## Predictions on the test set

* **T1:** the chosen measure has AUC ≥ 0.85 on C60, and the lower end of its 95% bootstrap interval (2000
  resamples of images, seed 62) is ≥ 0.75.
* **T2:** it beats M1 on C60: the 95% bootstrap interval of the paired AUC difference lies above 0.
* **T3:** at the development threshold, sensitivity and specificity on C60 are both ≥ 0.75.

All three hold → the measure is adopted as the project's noise detector for illustration prompts, with its
limits (one observer's labels, illustration-heavy, ±0.35 edits). Any failure → reported, nothing adopted.
Every candidate's test AUC is reported, descriptively.

## Known weaknesses, written now

* The two sets share an observer: the measure can at best reproduce Alessandro's eye, not "noise" in general.
* C59 labels are per sheet (three prompts), C60 per image: development labels are noisier than test labels.
* C60 contains edits that change a lot without damage (the FORM set): a measure of change rather than
  noise should fail T1/T2 there — that is the point of using it as the test set.

Code: `experiments/noise_metric.py` (`--dev`, then `--test`).
