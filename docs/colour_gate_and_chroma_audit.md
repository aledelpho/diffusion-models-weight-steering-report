# The intactness gate measures saturation — and what the sweep says once it does not

**Date**: 2026-09-28 · **Trigger**: Alessandro picked one image out of the leaf corpus as "the most
interesting of all: unexpected black and white" · **Material**: the 117 renders of the Stage 2b
colour sweep at dose 0.200, already on disk · **Script**: `experiments/colour_chroma_audit.py` →
`data/colour_chroma_audit.csv`, `data/colour_chroma_audit_summary.csv`,
`data/colour_chroma_audit_tests.csv` · **No render.**

---

## 1. The image, and where it went

Identified by perceptual hash against the corpus, exact match:
**`LN_Block_4neg_0.200_krea2_seed1337`** — the *undeclared-colour* leaf prompt, `Block_4` negative,
dose 0.200. The leaf is fully drawn, veins and all, and completely achromatic.

Its row in `data/colour_object_sweep_measurements.csv`:

```
mean_sat = 0.1028    fg_share = 0.0    object_intact = False
```

**The analysis filed it as a destroyed object and dropped it.** The object is not destroyed. The
colour is.

## 2. Why the gate had to do that

From `experiments/evaluate_colour_object_sweep.py`:

```python
fg_mask = (sat > 0.15) & (val > 0.08) & (val < 0.98)
object_intact = (fg_share >= 0.030) and (mean_sat >= 0.15)
```

**The foreground is defined by saturation.** An achromatic object therefore has no foreground by
construction, hence no `fg_share`, hence no object. The criterion is named for objects and measures
chroma.

Two consequences, and the second is worse than the first:

1. **The one outcome the experiment was looking for is the one outcome the gate cannot represent.**
   A colour/object dissociation *is* an object that survives while its colour does not. The gate
   classifies that as breakage.
2. **`mean_sat` in that file is censored.** It is the mean saturation over pixels selected for being
   saturated. It cannot go low, and it cannot be used to detect desaturation.

This is the same family as the audit of 23/09, where a structureless scramble scored as the most
chromatically specialised object in the corpus: a statistic whose name describes one thing and whose
arithmetic measures another. It is a **drafted pitfall candidate**, not a numbered one — the log
stands at 69 and nine candidates are already queued under register item A1.

## 3. Re-measured with a foreground that is blind to colour

`experiments/colour_chroma_audit.py` replaces the foreground with a **value-based** one: background
value taken from the border ring, foreground = every pixel departing from it by more than 0.06.
It then reports, for all 117 renders, the region's size, its overlap (IoU) with the same
prompt-and-seed baseline — a structural, colour-free test of whether the object is still there —
its uncensored mean chroma, and a chroma-weighted hue.

On the image in question:

| | foreground share | chroma |
|---|--:|--:|
| `LN` baseline, seed 1337 | 0.0845 | **0.5167** |
| `LN_Block_4neg_0.200`, seed 1337 | 0.0814 | **0.0204** |

**IoU with its baseline 0.936.** The object is in the same place and the same size; 96 % of its
colour is gone. That is a dissociation, and the gate saw a broken image.

## 4. And now the deflation: it is one cell out of 108

| probe | n | mean chroma ratio | min | cells with chroma < 50 % | mean IoU | **object kept and bleached** |
|---|--:|--:|--:|--:|--:|--:|
| `LP` (purple declared) | 36 | 1.210 | 0.385 | 3 | 0.861 | **0** |
| `LG` (green declared) | 36 | 1.110 | 0.298 | 3 | 0.821 | **0** |
| `LN` (nothing declared) | 36 | 1.229 | 0.040 | 4 | 0.835 | **1** |

Criterion: IoU ≥ 0.70 and chroma below half the baseline's.

**Perturbation does not desaturate on average — it saturates**, by 11–23 %. Across 108 cells exactly
one shows the object kept and the colour gone, and it is the one Alessandro spotted. The other cells
that lose chroma also lose the object.

So the gate flaw is real and must be fixed, and the phenomenon it hid is **a singleton**. It is a
lead worth a pre-registration of its own; it is not evidence of a systematic colour/object
dissociation, and the pre-registered verdict of Stage 2b is not disturbed by it — that prediction
was about hue rotation and it fell on hue rotation.

## 5. What the re-measurement does change: the declared/undeclared reading gets sharper

Measured again on the colour-free foreground, cells whose hue is undefined (chroma below 20 % of
baseline) excluded:

| probe | n | mean hue shift | max |
|---|--:|--:|--:|
| `LG` — green, the prototypical colour, declared | 36 | **4.7°** | 24.4° |
| `LP` — purple, an unusual colour, declared | 36 | **9.3°** | 32.0° |
| `LN` — nothing declared | 35 | **24.7°** | 56.2° |

The ordering **`LG` < `LP` < `LN`** replicates the published reading (25.2 / 8.7 / 4.6) under an
independent foreground definition, and slightly strengthens it.

Tested with the tool's condition as the unit — block × sign, 12 of them, seeds pooled, per pitfall
17 — and an exact two-sided sign test:

| comparison | conditions | p |
|---|--:|--:|
| `LN` moves more than `LG` | **10/12** | **0.039** |
| `LN` moves more than `LP` | 8/12 | 0.388 |

**The asymmetry is between undeclared and *prototypically* declared, not between undeclared and
declared.** Purple — a colour the model rarely sees on a leaf — sits in the middle and is not
significantly more pinned than saying nothing at all. That is closer to Alessandro's original
conjecture than the earlier reading was: what pins a colour is not the fact of declaring it but how
strongly the colour is already bound to the object.

**Caveat, stated plainly:** this analysis was chosen after seeing the images and is not
pre-registered. `LG` < `LP` < `LN` is a hypothesis now, with a p of 0.039 on one of its two arms and
a single object. It needs a second object, a second prototypical/unusual colour pair, and a
pre-registration, before it is anything more.

## 6. Actions

* `evaluate_colour_object_sweep.py` and `evaluate_colour_object_gate.py` must not gate anything else
  until the foreground is value-based. Register item.
* Pitfall candidate drafted (A1): *a "structure intact" criterion built out of the same quantity the
  experiment is trying to move cannot see the experiment succeed.*
* Register item: pre-register `LG` < `LP` < `LN` on a second object before citing it.
* No published claim changes status here.
