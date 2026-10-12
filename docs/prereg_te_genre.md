# Pre-registration C70 — the genre of each image, and whether attention on the style words predicts the switch

Written 2026-10-12, **before any label is given.** No renders. Labelling page: `Text2Img\_grid_viewer\te_genre.html`
(`experiments/grid_viewer.py --set te_genre`). The tally script is written after the labels arrive. It may only
compute what is fixed here.

## Why

C69 found that one strong edit (L06 MLP+) halves the share of text attention that goes to the style clauses, while the
other (L12 MLP+) raises it. Both send the five word orders to different genres. Alessandro's hypothesis is that
weakening the style words lets a default style (anime, a dataset prior) or a stereotype take over. The C69
preregistered test (P5) compared edits, not images. It could not say whether the images that actually changed genre
are the ones with less attention on the style words. That needs the genre of each image.

## Material and labels

* **Images:** the 210 images of C65 B: 2 seeds (3141592, 1234567) × 21 rows (originals + 20 text-encoder edits at
  ±1.00) × 5 word orders.
* **Who labels:** Alessandro, one genre per image, on the page.
* **Genres:**
  * `fumetto`: Western comics;
  * `anime`: anime or manga;
  * `cartoon`;
  * `realist`: realistic or semi-realistic, photo, 3D;
  * `pittura`: watercolour, oil, digital painting;
  * `altro`.
* **What the page shows:** only the images and their difference from the original of the same column. No attention
  values, sizes or scores.
* **Handling the file:** the CSV is committed as downloaded (`data/te_genre_alessandro.csv`) before any count.

**Switch:** an edited image switches genre when its label differs from the label of the original of the same order
and seed. Images without a label are left out; the counts below say how many.

## Tests (thresholds fixed now)

| test | measure | rule |
|---|---|---|
| G1 | **image-level P5.** The 20 edited images of C69 (seed 3141592; L06 MLP+, L12 MLP+, L10 MLP−, L19 attn−, 5 orders each): style share of that image (`data/te_bridge_style.csv`, `per_order_style_share`) in switched vs non-switched images | AUC (lower share → switch) ≥ 0.70 → supported; ≤ 0.50 → not supported; if either group has fewer than 3 images → inconclusive |
| G2 | the 20 edits: switch rate (10 images, both seeds) vs the C65 B order score (`score_1_5`, seed 3141592) | Spearman ρ ≥ 0.50 → supported |
| G3 | the 20 edits: switch rate vs the size of the conditioning change on the order prompts (`data/te_order_tests.csv`, `size`) | Spearman ρ ≥ 0.50 → supported |

## Reported, deciding nothing

* For each edit, the genres of its 10 images.
* The share of `anime` among the switched images.
* Whether the originals already differ in genre between orders, i.e. whether word order alone changes the genre.
* G1 again, inside each of the two strong edits separately.

## Limits

* One labeller, who knows the edits by name (the row label shows the edit) and has already seen these images. The
  page does not hide the condition.
* The genre boundaries are fuzzy, especially comics vs cartoon and anime vs cartoon.
* G1 rests on 20 images, and the style share comes from a single seed.
* Within an edit, the five images share most of the push. So G1 partly compares edits again; the within-edit report
  is there to show this.

## Amendment 1 (2026-10-12, after the labels arrived, before any count)

Alessandro labelled seed 3141592 only (105 images); seed 1234567 is empty. G2 and G3 therefore use the switch rate
over the **5** images of seed 3141592 per edit instead of 10. The rate can only take the values 0, 0.2, … 1, so ties
are many; the rules are unchanged. G1 is unaffected (it was seed 3141592 only). The tally script
(`experiments/te_genre_tally.py`) is written after this amendment.

## Amendment 2 (2026-10-12, after G1-G3 were counted, before any intensity label)

Alessandro pointed out that a binary "switched / not switched" may hide what happens, and asked for an intensity per
image. Second labelling pass, seed 3141592, 105 images (`Text2Img\_grid_viewer\te_genre_dose.html`, CSV
`data/te_genre_dose_alessandro.csv`, committed as downloaded). For each image, how far its style moves from the
original of the same column:

* 0 = same style;
* 1 = slight drift;
* 2 = clearly another style, with traces of the original;
* 3 = entirely another genre.

The page shows the genre labels already given. G1–G3 above stand as counted (`data/te_genre_tests.csv`). The new
tests are:

| test | measure | rule |
|---|---|---|
| G1d | the 20 C69 images: style share vs intensity | Spearman ρ ≤ −0.40 → supported |
| G2d | the 20 edits: mean intensity (5 images) vs order score 1–5 | ρ ≥ 0.50 → supported |
| G3d | the 20 edits: mean intensity vs conditioning size | ρ ≥ 0.50 → supported |

Reported: G1d inside L06 MLP+ and inside L12 MLP+ (5 images each, no rule).

Limit: Alessandro gives these labels after the binary G1 result was reported to him; the per-image style shares
were not shown.
