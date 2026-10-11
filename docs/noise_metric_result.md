# C62 — a noise measure that agrees with the eye: result

2026-10-11. Pre-registration `docs/prereg_noise_metric.md` (`3340c60`). Development choice committed before
the test set was scored (`602d055`). No renders. Code `experiments/noise_metric.py`; data
`data/noise_metric_dev.csv`, `data/noise_metric_dev_scores.csv`, `data/noise_metric_test_scores.csv`.

## Verdicts, as written

| | value | verdict |
|---|---|---|
| chosen on C59 (444 images, 75 positive) | **M1**, page 05's HF as \|log ratio\|, AUC 0.808 (M2 0.805; M3-M8 0.38-0.48) | — |
| **T1** AUC ≥ 0.85, lower bound ≥ 0.75 on C60 (180 edits, 88 positive) | 0.794 [0.727, 0.856] | **fails** |
| **T2** beats M1 | the chosen measure *is* M1: difference 0 | **fails** (by construction) |
| **T3** sensitivity and specificity ≥ 0.75 at the dev threshold 0.067 | 0.795 and 0.630 | **fails** |

Nothing is adopted. The best automatic stand-in for the eye remains what it was: the size of the
fine-texture change, which finds about four of five damaged images but also flags a third of the clean ones —
it measures change, not damage.

## What went wrong with the new candidates (descriptive)

* **The flat-region measures (M4-M8) were built on a mask that does not follow the picture.** The mask is the
  baseline's flat areas; the edits redraw the picture, so the same pixels hold new content in the edit. Their
  log ratios sit around +1.5 to +2.4 for clean and damaged images alike (median M4 2.22 on clean FORM edits,
  2.39 on damaged ones): they measure that the content moved. The C60 observation that damage sits in flat
  areas still stands; a mask taken from each image itself, or from both, was not in the list and would have
  to be pre-registered anew.
* **Immerkær's σ (M3) runs the wrong way, and not stably.** Signed as written, it scores 0.375 on C59 and
  0.148 on C60: damaged images have *less* fine pixel-scale variation than their baselines (median log ratio
  −0.22 on damaged SURFACE edits). The eye's "noise" here is coarse mottling that replaces fine detail. Read
  the other way it would score 0.63 and 0.85 — too unstable between the sets, and chosen after the fact, to
  be anything but a lead.
* **The colour high-pass (M7)** is the only flat-region measure above 0.5 on C60 (0.612), and below it on C59.

## What this changes

Nothing in the claims. It confirms the reservation of results page 29: the noise statements rest on the eye,
and no measure in the project replaces it yet. The two leads worth a new pre-registration, if wanted: the
inverted Immerkær ratio (coarse noise replaces fine detail) and a flat mask computed on the edit as well as on
the baseline.
