# Figure brief — Experiment 6 (attribute emergence)

> Work order for the figure rebuild. Supersedes the figure list in
> [`asset_pipeline.md`](asset_pipeline.md) §5, which was written before anyone had looked at
> the rendered result.

## Why the current figures have to be rebuilt

`effect_A1_vs_A5`, `conjunction_A1_vs_E3` and `matched_control_A1_vs_A7` are 3300 px wide with
20 columns: 165 px per thumbnail in the file, but GitHub renders README images at about 880 px,
so each portrait lands at **44 px**. A barnacle cluster is 5–8% of face width — two or three
pixels. The three figures that carry the finding currently show the reader nothing.

The two that work, `dose_response_strip` (110 px per panel) and `placement_crops` (146 px),
are exactly the ones with few columns and a tight crop. That is the whole diagnosis.

## The geometric fact that constrains the fix

The clusters do **not** sit in a fixed place. Measured on four A1 positives at 480×600:

| seed | cluster position (fraction of frame width) |
|---|---|
| 1337 | x ≈ 0.05–0.20, far left cheek |
| 9999 | x ≈ 0.42–0.48, centre cheek, small and sparse |
| 101 | x ≈ 0.66–0.70, temple beside the ear |
| 205 | x ≈ 0.78–0.85, cheek, large |

The head pose changes with the seed, so the attribute moves with it. **One fixed crop box cannot
capture all twenty**, which is also why two panels of the current `placement_crops` look empty:
seeds 9999 and 101 both have clusters, the crop simply missed them.

So the crop has to vary per image — and the moment it does, it becomes a choice that could be
used to flatter the result. The rule below makes that choice auditable instead of forbidding it.

## The fix: split each comparison into two figures

Trying to make 20 portraits legible in one strip is the wrong goal. A contact sheet's job is to
prove nothing was left out; a detail figure's job is to show what the difference looks like.
Making one image do both is what produced an image that does neither.

### A. Census sheet — completeness

* All seeds, **2 rows of 10 per condition** (so 4 rows for a two-condition comparison).
* Crop: **centre square**, identical for every image — from 480×600 take y ∈ [60, 540]. No
  per-image variation here; this sheet is about coverage, not legibility.
* Seed number above every column, condition label and score on every row band.
* Caption states its job: *every seed, in the same order, none omitted.*
* **Linked from the README, not embedded** — it is a reference, not a reading figure.

### B. Detail figure — evidence

* **The first six seeds of the canonical ordering: 1337, 42, 4242145, 777, 9999, 101.** Fixed in
  advance, not chosen for clarity. In A1 all six are positive; in A5, A7 and E3 all six are
  negative — so the figure reads as six-for-six against zero-for-six without anyone picking.
* Two rows: condition above, condition below, same seed in the same column.
* Crop: **per image, tight on the face region carrying the attribute**, roughly a 240×240 window
  of the 480×600 frame, upscaled.
* **Every crop box is written to `data/figure_crops.json`** as
  `{figure: {set_id: {seed: [x, y, w, h]}}}` in source-pixel coordinates. That turns a subjective
  framing into a published one: anyone can re-cut the same crops, or check that the negative row
  was not framed to hide something.
* Embedded in the README — this is the figure a reader actually looks at.

## Deliverables

| file | contents |
|---|---|
| `census_A1_vs_A5.webp` | 20 seeds, blockshuffle 19/20 vs stock 1/20 |
| `detail_A1_vs_A5.webp` | first 6 seeds, paired |
| `census_A1_vs_A7.webp` | 20 seeds, blockshuffle vs randsign at identical D |
| `detail_A1_vs_A7.webp` | first 6 seeds, paired |
| `census_A1_vs_E3.webp` | 20 seeds, full prompt vs temple-ridges phrase removed |
| `detail_A1_vs_E3.webp` | first 6 seeds, paired |
| `dose_response_strip.webp` | **keep**, relabel `Forza` → `Strength`, and make the caption say the score is the set's while the panel is one seed |
| `placement_crops.webp` | **keep**, re-cut seeds 9999 and 101 with the published crop boxes so no panel is empty |
| `data/figure_crops.json` | every per-image crop box used in a detail figure |

## Composition rules, unchanged from before

Seeds always in the same order and always labelled. No seed omitted from a census row. Row labels
carry the condition and its score (`A1 · blockshuffle · 19/20`) so a reader can count along and
check. All labels in English.

## Checks before commit

* Every detail figure's seed list is exactly `[1337, 42, 4242145, 777, 9999, 101]`.
* Every crop box in `figure_crops.json` is inside the source frame and non-degenerate.
* No panel of `placement_crops` or of any detail figure is empty where the data says positive.
* Each census sheet has exactly as many panels as its row label claims.
* `assets/` still under 60 MB.
