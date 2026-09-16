# Asset layout, batch figures and the repository weight

> **Status**: specification + work order. Sections 1–4 are the convention this repository
> follows from now on. Section 6 is the work still to be done.

## 1. The problem, in numbers

| | files | size |
|---|---|---|
| `assets/images/` — 1024×1280 PNG originals | 370 | **498 MB** |
| `assets/preview/` — 480×600 WebP | 370 | 18.7 MB |
| `assets/hero/` — GIFs and strips | — | 8.0 MB |
| **A full clone today** | | **≈ 536 MB** |

Nothing in the notebook or the viewer ever displays a PNG: every figure, every preview and
every GIF is built from the WebP. The 498 MB is carried so that a reader *could* inspect an
original — which is worth preserving, but not at 14× the weight of everything else combined.

**Target: a clone under 40 MB**, with the originals one click away instead of in the clone.

## 2. What stays in the repository

WebP only, at **480×600, quality 82** — the size already in use, which is legible at the scale
every figure in the notebook uses it. Plus the composed figures, plus one ComfyUI graph per
experiment.

```
assets/
  hero/                                   figures used at the top of README.md
  01_steering/                            the D-matched experiment (§2–§4)
    workflow_baseline.json
    workflow_preset.json
    _figures/
    baseline/G1_seatouched_teal_30de058455/{seed}.webp
    preset/G1_seatouched_teal_30de058455/{seed}.webp
    ...
  02_attribute_emergence/                 the barnacle experiment (§5)
    workflow_blockshuffle.json
    workflow_baseline.json
    workflow_randsign.json
    _figures/
    A1_blockshuffle_full_prompt/{seed}.webp
    A5_baseline_full_prompt/{seed}.webp
    A7_randsign_full_prompt/{seed}.webp
    E3_no_temple_ridges/{seed}.webp
    ...
```

Two rules behind the naming:

* **The folder name carries the set id from the data tables.** A reader who sees `A7` in §5.1 finds
  `A7_randsign_full_prompt/` without a lookup. The `set_id` column of
  [`../data/attribute_emergence.csv`](../data/attribute_emergence.csv) is the index.
* **The `prompt_sha1` stays in the path** for the steering experiment, alongside the readable id
  and tag. That hash is how "the prompt was never edited" is enforced — renaming the folder to
  something friendlier must not cost the proof. `G1_seatouched_teal_30de058455` gives both.

## 3. What leaves the repository

The 1024×1280 PNGs move to a **GitHub Release asset**, one zip per experiment. Release assets do
not count toward repository size and allow up to 2 GB per file, which is the mechanism GitHub
provides for exactly this. The README links to them from §7 so nothing becomes unreachable.

## 4. The ComfyUI graph travels with the images

Every render already carries its generation graph in a PNG `tEXt` chunk, and all 370 are published
as [`../data/comfy_graphs.json`](../data/comfy_graphs.json). But a reader who opens one experiment's
folder should not have to go find a 739 KB index: **each experiment folder carries the graphs that
produced it**, one per weight configuration, pretty-printed and loadable by dragging into ComfyUI.

Across all renders there are only three topologies (see [`workflow/`](workflow/)), so this costs a
few KB per experiment.

## 5. The figures §5 needs

In priority order. Every one of them uses the same 20 seeds, so they read as paired comparisons and
not as cherry-picked examples — that is the whole point of building them.

1. **`effect_A1_vs_A5.webp`** — two rows of 20 thumbnails, blockshuffle above, stock model below,
   seeds in the same order and labelled. This is the 19/20 against 1/20 in one image.
2. **`conjunction_A1_vs_E3.webp`** — the same layout, blockshuffle with the full prompt above and
   blockshuffle with only the temple-ridges phrase removed below. One phrase of difference, 19/20
   against 1/20. **This is the figure that explains the finding**, and it is the one to build first
   if only one gets built.
3. **`matched_control_A1_vs_A7.webp`** — blockshuffle above, randsign below. Identical Frobenius
   displacement, and the bottom row is indistinguishable from the stock model. This is the figure
   that answers "you just added noise of a certain size".
4. **`dose_response_strip.webp`** — one seed (1337 is present at every strength) across
   0.25 / 0.50 / 0.75 / 1.00 / 1.25 / 1.50 / 1.75 / 2.00, labelled with the count at each point.
5. **`placement_crops.webp`** — tight crops of the ear and cheekbone region from six positive
   renders, showing that the clusters land on the **cheekbone and temple**, not on the earlobe the
   prompt names. §5.5 makes this claim in prose and currently has nothing to show for it.

Composition rules so the figures stay honest: seeds always in the same order and always labelled;
no seed omitted from a row; the row label states the condition and its score (`A1 · blockshuffle ·
19/20`), so a reader counts along and checks.

## 6. Work order

1. Re-encode every `assets/images/**/*.png` to WebP 480×600 q82 into the new layout. The existing
   `assets/preview/` tree is already this encoding — reuse it rather than re-encoding, and only
   generate what is missing.
2. Build the batch figures of §5 for `02_attribute_emergence/_figures/`.
3. Write the ComfyUI graphs into each experiment folder.
4. Zip the PNG originals per experiment and attach them to a GitHub Release; add the links to §7.
5. Delete `assets/images/` from the working tree and commit.
6. **Squash and force-push.** This is the step that actually reclaims the space, and without it the
   first five change nothing: a blob stays in the pack as long as any commit reaches it. This
   repository has already been squashed to a single commit once, so the operation is known-safe
   here — but it rewrites history, so it happens once, deliberately, after steps 1–5 are verified.

## 7. Checks before the commit

* Every `image_file` in `data/attribute_emergence.csv` resolves to a file under the new layout
  (with the `.png` → `.webp` substitution). A missing file is an error, not a warning.
* Every experiment folder contains at least one `workflow_*.json` that parses.
* Every figure in `_figures/` has as many thumbnails as its row label claims.
* `assets/` totals under 40 MB.
