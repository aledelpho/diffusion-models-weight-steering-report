# C53 result (first observer) — block 23 against a saturation slider applied afterwards

2026-10-06. Pre-registration `docs/prereg_blk23_vs_postproc.md` (`b6035a3`); post-processed images,
sheets and key committed in `6ca29cf` before any observer; Alessandro's answers deposited in
`fb8be48` before the tally and before any measure was computed. No new render.

## Part A — blind forced choice, observer A (Alessandro; blind to side, not to the material)

`data/blk23_postproc_blind_answers_alessandro.csv`, tally `data/blk23_postproc_blind_tests_alessandro.csv`.

| | original set | mirrored set | rule | reading |
|---|---|---|---|---|
| position gate (q1) | 4 of 32 pairs same side | | ≤ 75% | pass |
| **S — adding colour:** blk23 −0.45 judged more natural | **12/16** | **11/16** | ≥ 12 on both | no difference shown (one short) |
| **D — removing colour:** blk23 +0.30 judged more natural | **1/16** | **4/16** | ≤ 4 on either | **the slider looks more natural** |
| preference (q2), S | 11/16 | 11/16 | reported | |
| preference (q2), D | 1/16 | 4/16 | reported | |

Answers are consistent cell by cell (the same choice on both versions in 28 of 32 pairs). Adding
colour, blk23 was chosen on both versions for rally, fox, still life and selfie at both seeds, the
cartoon at both, the oil painting at one; the slider on both versions for the sepia photograph at
both seeds, the archer at 4669201 and the oil painting at 4669201. Removing colour, the slider was
chosen everywhere except the cartoon (both versions at 2718281, one at 4669201) and the sepia
photograph (one version at each seed).

**Observer A's own note, given after the tally was shown to him (2026-10-06), translated:** the
archer's baseline has a hood generated "only halfway" — one of the "watershed" cases where the model
cannot finish a shape because two keywords (the hood and the long black hair) pull it different
ways. Block 23, like many imbalances, also repairs that shape. Asked which image he preferred, he was
often tempted to pick the blk23 image — which he recognised — for that detail, although the colours
and the rendering of the baseline were better.

This names a confound the pre-registration did not foresee: **block 23 changes content as well as
colour, so a forced choice between it and a slider cannot isolate colour.** Where the regenerated
image repairs or spoils a shape, that enters both questions. It also confirms that observer A was
not blind to the material: he recognised the blk23 images. Amendment 1 (below in the
pre-registration) asks observer B to judge colours only; it cannot remove the confound, only reduce it.

**Status.** Observer A is diagnostic by the pre-registration: he has seen these renders. The
primary verdict needs observer B (someone who has not seen the project). Until then: no primary
verdict.

## Part B — measures (computed after observer A answered)

`data/blk23_postproc_measures.csv` (layout r and B2 at 256×320). LPIPS and DINOv2
(`--measure --deep`) need the DINOv2 weights, which this container cannot download; they run on
Alessandro's GPU like `standard_metrics.py` and are pending.

**B1, the expected result, confirmed on layout r:** at matched chroma the slider leaves the layout
of the baseline untouched (r = 1.000) and blk23 does not (median 0.873 at −0.45, 0.854 at +0.30):
the slider is closer in 16 of 16 cells in both directions. The prediction holds as stated; it says
that block 23 is not a cleaner way to change saturation than a slider.

**B2, descriptive** (medians over 16 cells; chroma change matched: +3.9 and −3.1):

| | blk23 −0.45 | slider + | blk23 +0.30 | slider − |
|---|---|---|---|---|
| change of mean L (lightness) | −0.93 | −0.03 | +0.20 | −0.28 |
| change of std L (lightness contrast) | **+0.91** | +0.01 | **−0.57** | +0.06 |
| added share of clipped pixels | 0.000 | +0.005 | 0.000 | 0.000 |

Block 23 does not change colour alone: adding colour, it also darkens slightly and raises
lightness contrast; removing colour, it lowers contrast — the softening already noted by eye on
page 22. The slider clips a few pixels when adding colour; the model does not.

**Not interpreted:** the per-pixel measures of B2 (selectivity slope, hue shift) compare pixels
that do not correspond — block 23 regenerates the image, so a pixel is not the same point of the
scene in the two images. Their values for the model (hue shift ~15°) measure that regeneration,
not a colour transform. Recorded in the CSV, not read.

**After the test, descriptive:** quantiles of the chroma distribution (256×320), median change
over 16 cells at p25 / p50 / p75 / p95 — adding: blk23 +1.7 / +4.3 / +5.9 / +7.9, slider +1.7 /
+3.5 / +5.5 / +6.8; removing: blk23 −0.9 / −2.1 / −5.8 / −5.3, slider −0.9 / −2.4 / −4.8 / −8.2.
Removing colour, the slider takes most from the most saturated pixels; block 23 does not.

## What this lets page 22 say

* A saturation slider changes colour and nothing else; block 23 changes colour **and** regenerates
  the picture, with a change of lightness contrast in the same direction. Against the words, block
  23 is the gentler edit (unchanged); against a slider, it is not.
* To one observer who knew the material but not the side: adding colour, block 23 looked more
  natural in 11–12 of 16 cells (one short of the rule); removing colour, the slider looked more
  natural almost everywhere.
* Pending: observer B (primary), LPIPS and DINOv2.
