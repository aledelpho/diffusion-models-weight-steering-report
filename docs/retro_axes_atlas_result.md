# The whole corpus, re-read on the two new axes — and the atlas answers C20 for free

**Date**: 2026-09-28 · **Prompted by**: Alessandro — *"now that you have added those two columns
we can re-analyse the map and the atlas at zero cost"* · **Material**: every render this project
has ever made, already on disk · **Scripts**: `experiments/retro_texture_axes.py` →
`data/retro_texture_axes.csv`, `experiments/retro_atlas_reading.py` →
`data/retro_atlas_cells.csv`, `data/retro_atlas_summary.csv` · **No render.**

---

## 1. The re-measurement

Both axes added on 2026-09-28 are functions of a single image: **structure coherence** (do the
gradients still agree locally — is what is left still a drawing?) and **energy at each scale of
detail** (what size is the texture that changed?). Neither needs a baseline to be computed, so
every render already on disk can be re-scored for the cost of reading it.

**3 735 renders, fifteen benches, ten minutes, no GPU.**

| bench | renders | | bench | renders |
|---|--:|---|---|--:|
| `atlas_phase1` | 649 | | `profondita_neg` | 168 |
| `mappa` | 519 | | `leaf_collapse` | 142 |
| `stage7` | 480 | | `stage4_preset` | 140 |
| `qkvo_atlas` | 433 | | `blk16_ladder` | 72 |
| `stage5` | 300 | | `rectified_masks` | 72 |
| `stage9` | 300 | | `pavimento_rumore` | 32 |
| `colour_binding` | 242 | | `latenti_b6` | 18 |
| `profondita` | 168 | | **total** | **3 735** |

Absolute values only. Ratios need a baseline and every bench names its baselines differently, so
the joins live in per-bench analyses on top of this file. This document does one of them.

## 2. `C20` is answered, and the answer is a qualified no

Register item **C20** asked whether structure coherence means anything outside comic linework, and
budgeted renders for it. It did not need them: `benchmark_atlas_phase1` already carries **eight
style families** — photo, watercolour, lowpoly, claymation, ukiyo-e, pixel, glass, charcoal — each
with its own baseline, 78 perturbed cells apiece.

| style | baseline coherence | ratio mean | ratio spread | cells below 0.90 |
|---|--:|--:|--:|--:|
| `S1_photo` | 0.544 | 0.960 | **0.091** | **27 %** |
| `S2_watercolor` | 0.529 | 0.979 | **0.102** | **24 %** |
| `S8_charcoal` | 0.548 | 0.963 | **0.099** | **31 %** |
| `S7_glass` | 0.702 | 0.981 | 0.054 | 9 % |
| `S5_ukiyoe` | 0.607 | 0.990 | 0.056 | 1 % |
| `S3_lowpoly` | 0.644 | 1.001 | 0.042 | 1 % |
| `S4_claymation` | 0.659 | 0.983 | 0.040 | 1 % |
| `S6_pixel` | 0.524 | 1.003 | 0.038 | 1 % |

**The axis discriminates on three styles and is nearly flat on four.** On photo, watercolour and
charcoal it moves — a quarter to a third of all perturbed cells fall below 0.90 — and on lowpoly,
claymation, ukiyo-e and pixel almost nothing does, with a spread half as wide.

Two readings are possible and this corpus cannot separate them: either those four styles are
genuinely harder to break, or the statistic cannot see how they break. The second is the one to
assume, because it is the failure this axis was invented to expose in the first place: **a picture
made of flat polygons or of a pixel grid has little oriented line to lose, so an orientation
statistic has little to report.** Pixel art has the lowest baseline coherence of the eight (0.524)
and the smallest spread (0.038), which is exactly what a floor looks like.

**So the axis is not universal, and every structural claim made with it belongs to line-bearing
styles.** That is a narrower licence than the one this project was operating under this afternoon,
and it comes from the eight styles that were already rendered.

## 3. What the atlas looks like on the new axes

Ranked by coherence, pooled over seeds, 208 style × condition pairs:

**The conditions that move the image and lose the drawing** are `uniform_all` and `model_only` —
the two broadest edits in the atlas — and they do it on photo, watercolour and charcoal
(coherence 0.787 to 0.836). `late_attn` and `early_mlp` on charcoal join them.

**The conditions that move most while keeping the line** are headed by one name, in six of the
eight styles:

| style | condition | displacement | coherence |
|---|---|--:|--:|
| `S8_charcoal` | `early_attn_draw2` | **0.917** | **1.236** |
| `S1_photo` | `late_mlp_draw2` | 0.767 | 1.113 |
| `S2_watercolor` | `late_mlp_draw2` | 0.755 | 1.177 |
| `S4_claymation` | `late_mlp_draw2` | 0.712 | 1.040 |
| `S5_ukiyoe` | `early_attn_draw2` | 0.649 | 1.207 |
| `S8_charcoal` | `late_mlp_draw2` | 0.644 | 1.092 |
| `S3_lowpoly` | `late_mlp_draw2` | 0.624 | 1.136 |
| `S7_glass` | `late_mlp_draw2` | 0.603 | 1.087 |

**`late_mlp` is the atlas's `blk16`**: it moves the picture as far as anything in the corpus and
*raises* the orientation of the drawing while doing it, in six styles out of eight. 128 of the 208
pairs keep the line at 0.98 or above, so this is a property of a specific condition and not of the
atlas in general.

This is not a claim yet — it is exploratory, post hoc, and read off a corpus whose own
pre-registration asked different questions. It is, however, the first thing in this project that
puts the `blk16` result on more than one drawing style, and it cost no renders.

## 4. What this changes

* **`C20` is answered**, not fully and not the way it was expected: coherence is usable on
  line-bearing styles and near-blind on flat ones. The register item is closed with that caveat
  rather than spending 96 renders on it.
* **Every structural claim made on 2026-09-28 now carries a scope**: line-bearing styles. The
  comic-line bench that produced them is the best case for the statistic, not a typical one.
* **`late_mlp` earns a pre-registration** on the same footing `blk16` has. Two independent corpora,
  different granularities, same shape of result.
* The remaining benches — `qkvo_atlas`, `stage4_preset`, `stage5`, `stage7`, `stage9`,
  `pavimento_rumore`, `latenti_b6`, 1 653 renders — are measured and not yet joined to their
  baselines. That work is handed over in
  [`HANDOVER_2026-09-28_retro_axes.md`](HANDOVER_2026-09-28_retro_axes.md).

## 5. Limits

The universal table is absolute values; every ratio in §2 and §3 depends on the atlas's own
baseline convention being read correctly, which is checked only by the parse succeeding on 624 of
649 files (the 25 left out are the baselines themselves and the determinism check). The
displacement used for ranking here is the root-mean-square of the log band ratios — a new summary,
chosen for this table, not one with a history in the project. And the two readings of §2 cannot be
separated by this corpus.
