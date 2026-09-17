# Pre-registration (stub) — the hatching ladder on objects, stage 8

**Locked 2026-09-17.** Written before the measuring instrument has been built and
before a single stage 8 render exists. Only the prediction and the reasons are
fixed here; the corpus and the thresholds are added when stage 7 is finished,
and that addition is dated.

## The prediction

Alessandro, by eye, ranked four conditions from the most parallel hatching to the
least:

> `blockshuffle_neg` > `preset_pos` > `preset_neg` > `blockshuffle_pos`

One ordering out of twenty-four.

## Why this needs a new instrument, and which one

The existing `crosshatch_entropy_mean` reproduces the **sign** of the effect
within every family — on 18 prompts, 90/90 image pairs for preset and 87/90 for
block-shuffle — but it cannot settle the ladder **across** families, for a
reason that is measured, not suspected:

- It correlates with how much line is on the page at all:
  `corr(edge_density, crosshatch_entropy) = +0.52`, R² = 0.27. A quarter of the
  metric is ink quantity, not orientation. Regressing that out moves the ladder
  toward the eye: `preset_neg` and `blockshuf_pos` swap into the predicted order,
  and only one adjacent pair remains inverted, separated by 0.025.
- Worse, two proxies disagree at the cross-hatched end. `contour_n_components`,
  which counts how many separate pieces the drawing breaks into, gives
  `preset_neg` **+248** against `blockshuf_pos` **+5** — the opposite verdict to
  the density-corrected entropy.

Two proxies, two answers, means neither is measuring orientation. The instrument
that measures the stated phenomenon is the **histogram of edge-gradient
orientations**: parallel hatching is unimodal, cross-hatching is bimodal with two
near-orthogonal peaks. It is built before stage 8 renders and is not tuned
afterwards.

## The one design risk, and how stage 8 avoids it

Stage 8 changes **two things at once**: a new instrument, and objects instead of
character subjects. If the ranking fails, those two changes are not separable —
it could be that the prediction is wrong, or that the instrument behaves
differently, or that hatching on objects simply is not the same phenomenon.

So stage 8 is **not** all objects. A minority of its prompts repeat the subject
genre, which makes the subject subset a within-stage replication of the stage 7
finding under the new instrument, and the object subset the actual generalisation
test. The comparison that matters then lives inside one stage, with one
instrument, instead of spanning two stages that differ in everything.

The exact split, the corpus size and the decision thresholds are set when stage 7
closes, in a dated addition below. Nothing in this section is revised.

## What would refute it

An ordering that is not the predicted one, on the object subset, with the subject
subset reproducing stage 7. That would mean the ladder is a property of how the
model hatches faces and cloth, not a property of the displacement — which is a
result worth having and would be written as such.
