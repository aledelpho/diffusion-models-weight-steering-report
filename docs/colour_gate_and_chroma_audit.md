# The intactness gate measures saturation — and what the sweep says once it does not

**Date**: 2026-09-28 · **Trigger**: Alessandro picked one image out of the leaf corpus as "the most
interesting of all: unexpected black and white" · **Material**: the 117 renders of the Stage 2b
colour sweep at dose 0.200, already on disk · **Script**: `experiments/colour_chroma_audit.py` →
`data/colour_chroma_audit.csv`, `data/colour_chroma_audit_summary.csv`,
`data/colour_chroma_audit_tests.csv` · **No render.**

> **Sections 4–8 supersede the first version of this document, committed the same day in `9eef1ad`.
> Its foreground detector was defeated by grain (§7) and its per-probe figures were wrong.** The
> conclusions did not reverse; the numbers moved and one finding appeared that the broken detector
> had buried.

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
arithmetic measures another.

## 3. Re-measured with a foreground that is blind to colour

The replacement foreground is **value-based**: background value from the border ring, foreground =
departure from it by more than 0.06, after an 8× low-pass and reduced to its largest connected
component (the low-pass is not optional — see §7). It is blind to chroma, so it can see an object
that has lost its colour. Reported per render: region size, IoU with the same prompt-and-seed
baseline (a structural, colour-free test that the object is still there), uncensored mean chroma,
and a chroma-weighted hue.

On the image in question:

| | foreground share | chroma |
|---|--:|--:|
| `LN` baseline, seed 1337 | 0.0850 | **0.5071** |
| `LN_Block_4neg_0.200`, seed 1337 | 0.0821 | **0.0200** |

**IoU with its baseline 0.936.** Same place, same size; 96 % of the colour gone. That is a
dissociation, and the gate saw a broken image.

## 4. And it is one cell out of 108

| probe | n | mean chroma ratio | min | cells below 50 % | mean IoU | cells IoU < 0.5 | **kept and bleached** |
|---|--:|--:|--:|--:|--:|--:|--:|
| `LP` (purple declared) | 36 | 1.231 | 0.648 | 0 | 0.898 | 0 | **0** |
| `LG` (green declared) | 36 | 1.140 | 0.658 | 0 | 0.861 | 0 | **0** |
| `LN` (nothing declared) | 36 | 1.268 | 0.040 | 1 | 0.884 | 0 | **1** |

With the repaired detector the isolation is sharper than the first version reported: **every object
in the corpus survives** (no IoU below 0.5) and **exactly one cell in 108 loses its colour**, the
one Alessandro spotted, at 4 % of baseline chroma while the next lowest is 65 %.

Within its own condition it does not replicate: `LN`/`Block_4 neg` gives chroma ×1.652 on seed 42,
×0.898 on seed 777, ×0.040 on seed 1337. **Nor is seed 1337 globally fragile** — its mean chroma
ratio over all 36 of its cells is 1.135 against 1.308 and 1.195 for the other two seeds. So the
event is neither a property of the condition nor a property of the seed as such. With n = 1 a
seed × condition interaction cannot be told apart from a one-off, and that is a cheap render to
settle (§9).

## 5. The declared/undeclared reading gets sharper, and changes shape

Cells whose hue is undefined (chroma below 20 % of baseline) excluded:

| probe | n | mean hue shift | max |
|---|--:|--:|--:|
| `LG` — green, the prototypical colour, declared | 36 | **4.1°** | 14.8° |
| `LP` — purple, an unusual colour, declared | 36 | **9.4°** | 32.0° |
| `LN` — nothing declared | 35 | **24.9°** | 56.4° |

The ordering **`LG` < `LP` < `LN`** replicates the published reading (25.2 / 8.7 / 4.6) under an
independent foreground definition. Tested with the tool's condition as the unit — block × sign,
12 of them, seeds pooled, per pitfall 17 — and an exact two-sided sign test:

| comparison | conditions | p |
|---|--:|--:|
| `LN` moves more than `LG` | **10/12** | **0.039** |
| `LN` moves more than `LP` | 8/12 | 0.388 |

**The asymmetry is between undeclared and *prototypically* declared, not between undeclared and
declared.** Purple sits in the middle and is not significantly more pinned than saying nothing.
What pins a colour is not the act of declaring it but how strongly that colour is already bound to
that object.

Post hoc, and stated as such: one object, one unusual colour, p = 0.039 on one of two arms.

## 6. What the broken detector had buried: hue is pinned, **chroma is not**

Nothing pre-registered looked at saturation. Per block, over all 18 cells (3 probes × 3 seeds ×
2 arms), counting cells that fall on the consistent side of 1 for their arm:

| block | pos | neg | consistent cells | p |
|---|--:|--:|--:|--:|
| `Block_1` | ×1.308 | ×1.067 | 12/18 | 0.238 |
| `Block_2` | ×1.083 | ×1.184 | 12/18 | 0.238 |
| **`Block_3`** | **×1.563** | **×0.931** | **18/18** | **0.00001** |
| `Block_4` | ×1.193 | ×0.927 | 14/18 | 0.031 |
| `Block_5` | ×1.145 | ×1.610 | 12/18 | 0.238 |
| **`Block_6`** | **×0.726** | **×1.815** | **18/18** | **0.00001** |

**`Block_3` and `Block_6` are antisymmetric saturation knobs.** Every one of their 36 cells moves
the way its arm says, across three prompts, three seeds and two declared colours plus none, with
the object intact throughout (mean IoU 0.89 and 0.92). `Block_6` spans ×0.73 to ×1.82 — a factor of
2.5 between its arms. Bonferroni over the six blocks leaves both at p < 1e-4.

Blocks 1, 2 and 5 raise chroma in *both* directions: they are not knobs on this axis, they are
damage.

Set against §5, the separation is the point:

> **mean hue shift 12.7°, mean chroma change 28 %.** Hue barely moves and is pinned hardest where
> the colour is prototypical. Chroma moves a lot, moves *antisymmetrically*, and has two blocks
> that steer it cleanly.

The project has been asking "why can't we move colour". The answer appears to be that **"colour"
was being read as hue**. Also post hoc — but unlike §5 it is a direction prediction, 18/18 twice,
and it costs one cheap replication to pre-register.

## 7. The detector in §3 had the same defect it was written to expose

The first version of this document thresholded value **per pixel**, with no low-pass. On
`Block_6 pos` — the grain block — grain floods the background with value deviation: the measured
foreground went from 0.10 to **0.30** of the frame, swallowing grey noise, and the chroma computed
inside it collapsed to 0.407 with IoU 0.26–0.55. Read literally that said "`Block_6 pos`
desaturates by 60 % and destroys the object". Both were artefacts of the mask. With the low-pass
and largest-component step the same condition reads ×0.726 with IoU 0.860 — a real effect, less
than half as large, on an object that is fine.

**A colour-blind foreground is not enough; it must also be texture-blind.** Written here in full
because it was committed, in `9eef1ad`, in a document criticising a foreground detector for
measuring the thing it was supposed to control for. Drafted defect, register §E.

## 8. Alessandro's actual hypothesis, tested — and it fails at this granularity

The conjecture was not that colour can be moved. It was: *"purple leaf" is a crossing the model
rarely saw, so "leaf" and "change of colour" may sit in separate places, and there may be a
dividing line to find.*

That has a sharp consequence. **If an edit cuts the binding that holds "purple" onto "leaf", the
leaf should fall back to its prior** — the colour the model gives it when nothing is declared,
which is measured here as the `LN` baseline of the same seed, 36.4° (orange-brown), not green.
Purple sits 84.5° away from it. There is room to move either way.

Over all 36 `LP` cells:

| | |
|---|--:|
| cells that move **toward** the prior | **6/36** |
| conditions (block × sign) that mostly move toward the prior | **1/12** |
| mean distance from the prior, baseline → perturbed | 84.5° → **93.2°** |

**Not one block, in either direction, releases the purple leaf toward its default colour. Thirty of
thirty-six cells move further away.** Whatever a whole-block edit at dose 0.200 does, it is not
cutting a colour-to-object binding — if anything it entrenches the declared colour while degrading
everything around it.

This is a negative result on the mechanism, not on the idea, and it is the negative result
Alessandro's own plan expected from the coarse pass: *"strong block-level perturbations first, to
identify which area to work in, then narrow the field."* The coarse pass is now done and it says
**no block is the area**. The next step is the one his plan already named — finer granularity — and
the literature says where to point it: ColorWave (arXiv 2503.09864) localises colour-attribute
binding at the **key projection**, and this project already has a q/k/v/o apparatus
(`benchmark_qkvo_atlas`) that has never been pointed at colour.

## 9. Actions

* `evaluate_colour_object_sweep.py` and `evaluate_colour_object_gate.py` must not gate anything else
  until the foreground is value-based **and** low-passed. Register item.
* Two drafted defects (register §E): *a "structure intact" criterion built out of the same quantity
  the experiment is trying to move cannot see the experiment succeed*; and *a foreground threshold
  without a low-pass measures texture, not shape.*
* **C15** — pre-register `LG` < `LP` < `LN` on a second object and colour pair.
* **C16** — the achromatic singleton: same condition, ~20 seeds, to separate a seed × condition
  interaction from a one-off. Cheap and decisive.
* **C17** — pre-register the chroma antisymmetry of `Block_3` and `Block_6` on a second object.
* **C18** — colour binding at q/k/v/o granularity, key projection first, per §8.
* No published claim changes status here.
