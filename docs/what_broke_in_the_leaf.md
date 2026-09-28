# What broke between the leaf and its colour

**Date**: 2026-09-28 · **Question**: Alessandro — did we break the link between the leaf and its
colour, and are they perhaps not "joined" precisely because the colour is intrinsic to the object?
· **Material**: `benchmark_leaf_collapse` and the Stage 2b sweep, all on disk · **Scripts**:
`experiments/leaf_collapse_scope.py`, `experiments/prior_colour_bleed.py` →
`data/leaf_collapse_scope.csv`, `data/prior_colour_bleed.csv` · **No render.**

---

## 1. Three facts, and they point the same way

**(a) Only the undeclared probe ever collapses.** In the Stage 2b sweep, over 36 cells each
(6 blocks × 2 arms × 3 seeds), the lowest chroma ratio reached by a *declared* colour is:

| probe | lowest of 36 | second lowest |
|---|--:|--:|
| `LP` purple declared | 0.648 | 0.653 |
| `LG` green declared | 0.658 | 0.693 |
| **`LN` nothing declared** | **0.040** | 0.783 |

Under the very same edit and the very same seed that produced the achromatic leaf —
`Block_4 neg`, seed 1337 — the **purple** leaf comes back at **1.063** and the **green** one at
**0.871**. Same weights, same noise, same sentence frame; the only difference is whether the colour
was named. **Naming it makes it immune.**

**(b) The collapse is the object's, not the frame's.** Arm A, chroma inside the object and outside
it, each against that seed's own baseline (`data/leaf_collapse_scope.csv`):

| | collapsed seeds | the others | exact p |
|---|--:|--:|--:|
| **object** | **0.050** | 0.999 | **0.00001** |
| background | 0.882 | 1.102 | 0.131 |

The leaf loses 95 % of its chroma; the background keeps its tint. *Stated with its limit*: the
background is a plain light grey by construction and its absolute chroma is 0.003–0.006, so that
test has little power and its job is only to rule out a gross frame-wide desaturation, which it
does.

**(c) It produces no colour, not a different one.** This is the fact that decides the reading.
Breaking a *binding* between two representations should leave the object with the wrong colour —
a random hue, or the prior. It does not: chroma goes to 0.04, and the hue becomes undefined. And
when whole blocks were swept, no block in either arm released a declared purple leaf toward its
prior either — 6 of 36 cells moved toward it, mean distance 84.5° → 93.2°
(`colour_gate_and_chroma_audit.md` §8).

## 2. The reading these support

**There appear to be two routes by which the leaf gets a colour, and only one of them is fragile.**

* **Declared** — the colour is in the text conditioning. It survives every edit measured, in both
  arms, at every block, on both an ordinary colour and an unusual one.
* **Undeclared** — the colour has to be *inferred from the object*, because nothing said it. That
  inference is a step, it happens somewhere in the trajectory, and it is what a `Block_4` negative
  edit can knock out — not always, about 45 % of seeds, and when it fails nothing takes its place.

So, to answer the question as it was asked: **we did not break a link between two things that were
joined.** What the evidence fits is that the leaf's colour, when unstated, is not a separate thing
bound to the object at all — it is produced *by* the object, and the edit can stop it being
produced. The leaf survives because the leaf was asked for; the colour does not because it was
never asked for, only implied.

That is close to Alessandro's formulation — "not joined, because the colour is intrinsic to the
object" — with one correction: intrinsic does not mean inseparable. It means there is no separate
handle to grab. The colour is downstream of the object, and what fails is the step that produces
it, not a connection between two stored things.

## 3. What this is not, and the limit that matters most

**One prompt, one subject, one block, one arm, one dose.** Five near-synonymous rewordings of the
leaf prompt never produce it, in 15 cells.

The four other subjects are a different matter, and the claim made here on 2026-09-28 was withdrawn
the same day. Mushroom, tomato, pinecone and banana were chosen for having a *strong* colour prior —
and for all four, not naming the colour gives the same picture as naming the prototypical one
(0.9° to 9.9° apart, against **52.2°** for the leaf). There was no free inference in them to break,
so this section's own mechanism predicts no collapse there. **Arm C did not test generality; it
tested a population that cannot show the effect** (`looking_at_the_leaf_corpus.md` §1). Whether the
two routes exist beyond this prompt is open, and the subjects that would decide it are the ones with
an *ambiguous* prior.

## 4. A negative of my own, recorded because it was my impression

Looking at `PCU` (a purple pinecone) seed 777 before and after, the purple looked intact while
**brown had appeared in the crevices** — the object's own colour seeming to leak back. If that were
real it would support §2 nicely from the other direction.

It does not survive counting. `experiments/prior_colour_bleed.py` defines, for each subject, a
prototypical and a declared hue band from that subject's *own* baselines, and counts the share of
the object in each, before and after:

| subject | prototypical share | declared share |
|---|--:|--:|
| mushroom | +0.040 | −0.077 |
| tomato | **−0.112** | −0.118 |
| pinecone | +0.070 | −0.202 |
| banana | −0.001 | +0.004 |

**The prototypical share rises in 5 of 12 cells — a coin flip, p = 1.00.** The declared share falls
in 9 of 12, p = 0.146, which is not significant either. Two subjects show the pattern and two show
the opposite.

The impression came from one image, and one image is one cell. Twice today an impression from
looking has met a count: the first time the impression was right and the statistic was wrong, this
time the impression was mine and the count says no. **The lesson is not that the eye beats the
number or the reverse — it is that a single cell is a single cell, whichever faculty read it.**
