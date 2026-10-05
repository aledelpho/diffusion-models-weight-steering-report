# Knobs inside the weights: single-block scaling in Krea-2 — results

> **Scope.** Everything here is about one model, Krea-2 (28 single-stream transformer blocks),
> edited without training by multiplying the weights of single blocks. It is an investigation
> into whether controllable "knobs" exist inside the weights, not a tool that competes with
> post-production. The exploratory lab notebook that led here is in [`../notebook/`](../notebook/)
> and stays the record of every test run; this folder holds only the results that were
> confirmed, or that the report needs in order to be honest about what was not.

## How to read the table below

The four words mean what they mean in the exploratory notebook: **Holds** passed a criterion
fixed before the data; **Ambiguous** was tested and does not decide; **Overturned** was tested
and failed; **Open** was not tested. Every row links to the page that makes the claim, and every
page shows its pre-registration, its data and its reservations.

## What holds and what does not

<!-- CLAIMS:BEGIN -->

| | What | What it rests on |
|---|---|---|
| **Holds** | [Scaling block 23 alone moves the saturation of a Krea-2 picture in one direction, monotonically with the dose and roughly in proportion to it.](22-saturation-knob.md#direction-and-proportion) | Pre-registered. Chroma falls strictly from -0.45 to +0.30 in 15 of 16 prompt-seed cells (threshold 14); doubling the dose from -0.15 to -0.30 multiplies the gain by 1.76 (window 1.6-2.4). On every older render with a blk23 arm, 83 of 83 move chroma the expected way. |
| **Holds** | [Where blk23 reaches the same saturation gain as adding "colorful, vivid highly saturated colors" to the prompt, it leaves the rest of the picture closer to the original than the words do.](22-saturation-knob.md#against-the-words) | Pre-registered on layout r: 6 of 7 scorable cells, median +0.08. Confirmed afterwards with standard metrics: LPIPS 7 of 7, DINOv2 6 of 7. The comparison is possible in 7 of 16 cells only: in the other 9 the words add more saturation than blk23 at its strongest tested dose. |

<!-- CLAIMS:END -->

## Pages

| page | question |
|---|---|
| [22 · One block that turns saturation up and down](22-saturation-knob.md) | Is there a knob that does one thing everywhere? |

Pages in preparation: method and instrument (20), a map of the 28 blocks (21), presets for a
prompt family (23), wording against content (24), standard metrics (25), what did not work (26),
other kinds of edit (appendix A). Structure and sources: `docs/report_outline.md`.
