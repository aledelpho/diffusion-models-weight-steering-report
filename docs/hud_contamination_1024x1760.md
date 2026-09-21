# The HUD contamination — every render at 1024×1760

**Found**: 2026-09-21, as a by-product of the reproducibility audit. The audit was looking for
hand-typed fields that disagreed with the files; it found that `08-block1-vs-block6` published
`1024x1280` while its own feature tables recorded **1024×1760**. Correcting the published field
was the wrong conclusion: the right one is that 1760 is not a resolution, it is a symptom.

**What it is**: these renders were saved with a HUD strip attached to the image. 1760 − 1280 =
**480 pixels** of overlay below the picture. An earlier round had already established that a HUD
inside the frame moves the measurements. Every texture and palette feature computed on these
files was therefore computed partly on an overlay: `edge_density`, `crosshatch_entropy_mean`,
`stroke_width_cv`, `contour_n_components`, `lbp_entropy`, and every swatch the palette extractor
clustered.

**Extent**: total, on the three benches affected. Not one image of them is recorded at any other
size — there is no clean subset to fall back on.

## The 555 files

Listed image by image in [`data/hud_contaminated_images.csv`](../data/hud_contaminated_images.csv),
with the absolute path, the output folder, the bench, the prompt, the seed, the condition, the
feature tables that record it and the notebook page that rests on it.

| bench | images | output folder | notebook page |
| --- | ---: | --- | --- |
| pilot rotation sweep | 225 | 9 × `benchmark_<prompt>/` (216 under `rotations/`, 9 baselines at the root) | `04-where-in-the-model` |
| block 1 against block 6 | 210 | `rotations_block1_vs_block6/` | `08-block1-vs-block6` |
| the triangle, its own renders | 120 | `rotations_block1_vs_block6/` | none — verdict not determined |
| **distinct files** | **555** | | |

The triangle's feature tables hold 330 rows, of which **210 are the block-1-against-block-6
images themselves**: the two experiments share one output folder, and the triangle read the
earlier bench's files as part of its own corpus. That is pitfall 30 for the third time, and it
means the two cannot be re-rendered independently — the folder has to be rebuilt as a whole,
with the two runs separated.

## What rests on them

**`08-block1-vs-block6`** — the strongest confirmatory result in the notebook. Both `holds`
claims and one `ambiguous` claim are computed entirely from these features:

* `blocks-separate-by-direction-not-distance` — the +1.039 advantage, the +0.532 scramble null,
  the +0.506 paired advantage, the exact permutation floor, all five measurement spaces.
* `block1-coheres-at-matched-displacement` — the 0.949 and 0.958 coherences.
* `block1-does-not-replicate`.

**`04-where-in-the-model`** — one `ambiguous` and two `open` claims. The CLIP distances come from
the nine source reports rather than from these feature tables, but they were computed on the same
images, so the whole page is affected and not only the parts that cite the feature files.

**The triangle** is already recorded as *not determined*, for unrelated reasons. This is a second,
independent reason.

**Unaffected**: every other bench in the project renders at 1024×1280. Pages 00, 02, 03, 05, 06,
07 and 09 do not touch these files.

## What is not decided here

Nothing has been deleted and no claim's status has been changed. Both affected pages now carry a
banner saying the pixels are contaminated and that their claims are not endorsed pending a
decision, and `validate_notebook.py` refuses to pass a page that cites a contaminated feature
table without that banner.

The decision that belongs to the author:

1. Withdraw the claims now, or leave them flagged until replacement renders exist.
2. The matched-displacement calibration in `data/matched_rotation_calibration.json` is computed
   from the **weights**, not from the images, so 23.69° and 32.21° at D = 0.045 survive the
   contamination and the bench can be re-rendered against the same design.
3. The pre-registration of `08` is unaffected and still frozen: a re-render is a replication of a
   registered design, not a new experiment, provided the analysis script is not touched.
