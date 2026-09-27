# Assessment: can a weight edit break the binding between a colour and an object?

**Date**: 2026-09-27 · **Proposal**: Alessandro — use an uncommon colour/object pairing (a purple
leaf) to find whether colour and object live in separable places, starting from strong block-level
perturbations and narrowing. **Assessment**: analyst, from existing data and documents.
**No render generated.** Exploratory; no claim status changes.

---

## 1. The idea is not debunked. It has the project's strongest unclaimed evidence

Two claims on notebook page 02, both `ambiguous`, are this mechanism:

**`permutation-adds-a-neglected-attribute`** — *"A block permutation makes an attribute the prompt
names and the model normally drops appear in almost every render, while a sign scramble carrying the
identical displacement does nothing at all."*
Evidence on record: **19/20** against **1/20** for the stock model on the same prompt and seeds, and
**1/20** for the norm-matched scramble at D = 0.0538.

That is precisely the proposed mechanism, already observed: **a weight edit restored a binding the
model was dropping**, and a structureless perturbation of identical size did not. It is `ambiguous`
for one reason only — it was exploratory and no threshold was fixed in advance.

**`edit-adds-and-removes-unasked-traits`** — lit headlights **10/35** at baseline, **31/38** under
one edit, **0/39** under another. Bidirectional control of a specific semantic attribute. Its
pre-registered confirmation failed for a reason that must not be repeated: *"9 of its 10 prompts
never light a headlight in any condition"* — **the replication corpus was chosen without checking
that the attribute had room to move.** A floor, not a refutation.

## 2. What *has* been debunked is step 1

The proposal starts by using **strong block-level perturbations to find where the biggest changes
are**. Three results say that criterion selects the wrong thing.

* **"Strong" is already saturated.** Image motion goes as dose^0.19, and at the smallest dose ever
  tested the image has moved 50–62 % of the distance to a different seed
  (`assessment_per_block_dose_calibration.md` §2–3). There is no headroom to turn up.
* **Sensitivity is anti-correlated with causality**, ρ = −0.72 to −0.88 on a five-model panel
  (arXiv 2608.03842). Where representations diverge most is not where the computation lives.
* **And this project has its own demonstration, which is the decisive one.** The audit of
  2026-09-23 re-ran `all_blocks_specialization_report.md` with the null the original omitted:

  | | chroma | shape | log2(C/S) | cells with log2 > 0 |
  |---|--:|--:|--:|--:|
  | B1 | 0.875 | 1.144 | −0.39 | 2/6 |
  | B6 | 2.058 | 2.666 | −0.37 | 1/6 |
  | **scrB** — *no structure*, D matched to B6 | **3.442** | 2.191 | **+0.65** | **6/6** |

  **A structureless scramble is classified as the most chroma-specialised thing in the corpus, and
  more consistently than any real block.** The classification measures how far the image moved, not
  what the block does. With the dimensionality correction (chroma on 5 features, shape on 4, log2
  biased +0.16) **B2 drops from "chromatic" to "mixed"**.

  *The analyst read `B2 = chroma-dominant` off that table an hour ago and began building on it. The
  audit was in the repository. Fifth time today.*

## 3. Where a watershed would have to be found, and what today's data says

Per-block transfer across subjects, by trait family, from `data/signature_robustness.csv`
(all seven conditions, 42 items per cell, chance 0.50):

| block | all 23 | colour | texture | stroke | tone |
|---|--:|--:|--:|--:|--:|
| `Block_1` | 0.905 | 0.631 | **1.000** | **1.000** | 0.595 |
| `Block_2` | **0.476** | 0.393 | 0.631 | **0.274** | 0.607 |
| `Block_3` | 0.631 | 0.512 | 0.571 | 0.738 | 0.548 |
| `Block_4` | 0.619 | 0.357 | 0.821 | 0.679 | 0.464 |
| `Block_5` | 0.679 | 0.607 | 0.631 | 0.845 | 0.452 |
| `Block_6` | **1.000** | 0.595 | **1.000** | **1.000** | 0.762 |

`Block_2`'s failure is **not** a colour failure — its worst column is **stroke, 0.274, well below
chance**. No block shows a colour column that transfers. **There is no colour/shape watershed
visible in this table**, and the one the old report claimed is the one the audit killed.

That is not evidence against the proposal. It is evidence that **the aggregate style descriptors
cannot see it**: they average over the whole frame, and a binding lives on one object.

## 4. The design that would work, and the control that makes it work

The measurement must be **on the object, and against its own prior**.

* **Two prompts, matched**: *a purple leaf* (uncommon binding) and *a green leaf* (the prior),
  everything else identical.
* Under an edit, three outcomes, and only the first is what the proposal is looking for:

| outcome | purple leaf | green leaf | reading |
|---|---|---|---|
| **reversion** | goes green | stays green | **the binding broke, the object survived** |
| generic rotation | shifts hue | shifts hue by the same amount | colour drift, not binding |
| object collapse | stops being a leaf | stops being a leaf | the object path was hit |

**The green-leaf control is the whole experiment.** Without it, "the purple went green" and "every
hue rotated" are the same measurement, and the project has already published a retraction for
exactly that class of error.

* Statistic: hue of the object region against the two poles (declared colour, prior colour), plus an
  object-integrity measure so collapse is not scored as reversion. Per block, both signs, several
  seeds. A block that produces reversion without collapse, beside a block that produces collapse
  without reversion, **is** the watershed — and it is a dissociation, which is what
  arXiv 2608.03842 says to look for instead of sensitivity.

## 5. The step that must come first, and it is small

**A feasibility pilot, before any sweep**: does Krea-2 render *a purple leaf* as purple at baseline,
across seeds? If it already reverts to green unperturbed, the design is at floor and dies exactly
as the headlight confirmation died. Roughly **10 renders**, and it either licenses the study or
saves it.

The same pilot should confirm the green-leaf control renders green, and that the two are
distinguishable by the chosen statistic before any edit is applied.

Alessandro launches renders. This is an assessment, not a plan in motion.
