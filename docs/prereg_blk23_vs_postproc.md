# C53 pre-registration — block 23 against a saturation slider applied afterwards

2026-10-06. Written before any outcome measure of this comparison was computed and before any
observer saw a sheet. No new render: every image is a C47 render (`benchmark_blk23_colorful`, 128
images, 8 prompts × 2 seeds) or a post-processed copy of a C47 baseline.

## Why

Page 22 compares block 23 with the words "colorful" / "muted colors" in the prompt. A reader
asked for the comparison that matters in practice: the baseline image with its saturation raised or
lowered in post-production. The page's scope note already says the project does not compete with
post-production, but the comparison was never shown.

## What is expected, stated before

A saturation slider changes only colour; block 23 makes the model generate a different image. At
the same chroma gain the slider will therefore leave the rest of the picture closer to the baseline
than block 23 — on layout r, LPIPS and DINOv2 — almost by construction. This is written down so that
it cannot be presented later as a finding against or for the block: the claim "block 23 disturbs the
picture less than the words" stays true, and **"block 23 is a cleaner way to add saturation than a
slider" is expected to be false**.

The open question is the other way round: **does block 23 give something a slider does not?** A
colour change made by the model may be distributed differently (selective rather than uniform,
with hue and lighting following), and may look less like a filter. That is a perceptual question.

## Material

* **Cells:** the 16 prompt-seed cells of C47.
* **Post-processing, two methods**, applied to the full-resolution baseline:
  * **PP-slider (primary):** `PIL.ImageEnhance.Color(img).enhance(f)` — interpolation with the
    grey image, the usual "saturation" slider of image editors.
  * **PP-chroma (secondary):** CIELAB a\* and b\* multiplied by k, L unchanged, back to sRGB with
    clipping.
* **Matching:** for every blk23 rung (−0.45, −0.30, −0.15, +0.15, +0.30) and for each wording, f
  (or k) is found by bisection so that the post-processed image has the same mean-chroma change
  from the baseline as the blk23 / wording image, on the C47 metric (CIELAB at 64×80), within
  0.05. A target the method cannot reach is recorded as unreachable. The matching table
  (`data/blk23_postproc_match.csv`) contains only the targets and the factors, no outcome measure.

## Part A — blind forced choice (decisive)

* **Sheets:** for each cell, blk23 at −0.45 against PP-slider matched to it (direction S,
  saturating), and blk23 at +0.30 against PP-slider matched to it (direction D, desaturating):
  32 pairs; each shown twice with the sides swapped (original and mirrored set) = 64 sheets, random
  ids, shuffled order. Key committed before any observer answers (`data/blk23_postproc_blind_key.csv`).
* **Questions:** q1 "In which of the two images do the colours look more natural, as if the
  picture had been made that way?" (LEFT/RIGHT, decisive). q2 "Which of the two do you prefer?"
  (LEFT/RIGHT, reported, not decisive). The sheets carry no label; nothing on the page says what
  the two images are.
* **Observers.** Observer A: Alessandro — first, as the eye pass. He is blind to the side but has
  seen the C47 renders, so his answers are declared **not blind to the material** and are
  diagnostic. Observer B (primary, if available): an observer who has not seen the project — his
  partner, as in C52 — with Alessandro out of the room. If no observer B answers, Part A has no
  primary verdict and says so.
* **Position gate** (per observer): the same side named on both versions of a pair in at most 75%
  of the 32 pairs; otherwise that observer is void.
* **Rules, per direction (16 pairs), on q1, observer B:**
  * **H1 (S)** blk23 judged more natural in ≥ 12 of 16 on **both** sets → *block 23 has a perceptual
    advantage over the slider when adding colour*. Chosen in ≤ 4 of 16 on either set → *the slider
    looks more natural*. Otherwise → *no difference shown*.
  * **H2 (D)** the same for removing colour.
  (12 of 16 is p = 0.038 one-sided under chance.)

## Part B — measures, computed only after observer A has answered (descriptive)

* **B1, the expected result:** at matched chroma, PP-slider against blk23, distance from the
  baseline on layout r, LPIPS and DINOv2, per cell and rung. Declared prediction: the slider is
  closer on all three in at least 14 of 16 cells at −0.45. If the prediction fails, that is
  reported as a surprise to be explained, not as a win for the block.
* **B2, what the block does beyond saturation** (descriptive, no thresholds): LPIPS between blk23
  and its matched PP image; selectivity of the gain (slope of the per-pixel chroma ratio against
  baseline chroma; a slider has slope ≈ 0 in ratio terms); mean absolute hue shift on pixels with
  chroma > 10; lightness change (mean L, std L); share of clipped pixels (any channel at 0 or 255)
  added relative to the baseline.
* Both PP methods are reported; PP-slider is the one that enters Part A.

## What changes on page 22, whatever the outcome

A section "Against a slider in post-production" with the side-by-side figure (base, slider, blk23,
words; in both directions), the B1 numbers and the Part A verdict. The claim about the words is
not touched. Any change to a claim's status is Alessandro's decision.

## Code

`experiments/blk23_vs_postproc.py`: `--build` (post-processed images and matching table),
`--sheets` (blind sheets and key), `--page` (blind page), `--tally` (Part A), `--measure` (Part B).
Committed with this document, before `--sheets` is shown to anyone.

## Amendment 1 — 2026-10-06, after observer A, before observer B

Observer A reported (see `docs/blk23_postproc_result.md`) that block 23 sometimes repairs a shape
the baseline left half-formed, and that this drew his choice. The comparison therefore mixes colour
with content. For observer B only, the page opens with one sentence before the first sheet:
"Le due immagini possono differire anche in piccoli dettagli o forme: ignora queste differenze e
giudica solo i colori." The sheets, their order, the questions and the rules are unchanged.
The verdict of Part A will be reported together with this confound whatever it is; it cannot be read
as a judgement on colour alone. Page: `blind_pp/test_B.html`, built by `--page --observer-b`.
