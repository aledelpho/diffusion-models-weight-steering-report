# Passing an eye over the 102 renders nobody had opened

**Date**: 2026-09-28 · **Prompted by**: Alessandro — "pass an eye over them" · **Material**: arms
A, B and C of `benchmark_leaf_collapse`, measured two documents ago and never looked at ·
**Method**: contact sheets at `benchmark_leaf_collapse\_contact_sheets`, then measurement of
whatever the sheets suggested · **Scripts**: `experiments/prior_ambiguity.py` →
`data/prior_ambiguity.csv` · **No render.**

---

## 1. The finding: arm C tested subjects that could not show the effect

`leaf_collapse_and_blk16_result.md` §3 read arm C as a clean falsification — four other subjects,
36 cells, not one collapse, therefore **leaf-specific**. The contact sheet for the mushroom says
something the numbers did not: **the undeclared row and the prototypical-declared row are the same
picture.** Brown mushroom when told "brown", brown mushroom when told nothing.

Measured — circular hue distance between the undeclared baseline and the prototypical-declared
baseline, pooled over three seeds:

| subject | undeclared vs prototypical-declared | prior |
|---|--:|---|
| pinecone | **0.9°** | unambiguous |
| banana | 1.4° | unambiguous |
| mushroom | 3.1° | unambiguous |
| tomato | 9.9° | unambiguous |
| **leaf** | **52.2°** | **ambiguous** |

**For all four subjects of arm C, not naming the colour is the same as naming it.** There is no
inference left to fail. The mechanism proposed in `what_broke_in_the_leaf.md` §2 — that what breaks
is the step where an object is *given* a colour it was never told — predicts exactly nothing to
break in those cells, which is what happened.

**So L4 is not a clean falsification.** The subjects were chosen for having a *strong* colour prior,
on the reasoning that a weak prior would leave nothing to measure. That reasoning was backwards:
a strong prior is precisely what removes the free inference the effect needs. Alessandro's own
suggestion when the arm was designed — *"flowers? mushrooms?"* — contained the right answer, and the
flower was rejected for the one property that made it the correct subject.

This does not rescue the collapse as a general mechanism. It says the test that was supposed to
decide it has not been run. The right population is subjects whose colour is genuinely undetermined
in the prior — a flower, a car, a shirt, a bird, a stone, a butterfly — and the measurement above is
the **screening criterion** for choosing them: render the undeclared and prototypical-declared
baselines first, keep the subjects above about 30°, and only then spend renders on the edit.

## 2. Arm B: my visual impression did not survive counting either

The five rewordings visibly produce different scenes — one has shallow depth of field, one a pinkish
background, the leaves sit at different scales and angles, and they read as more vividly autumnal
than arm A's. That suggested the rewordings had changed the object, which would have made L3's
falsification meaningless.

Two colour statistics say no:

| | baseline chroma | hue dispersion inside the leaf |
|---|--:|--:|
| arm A | 0.5031 | 14.5° |
| arm B | 0.4736 | 16.8° |

**Neither separates them.** The scenes differ in framing, not in the leaf's colour. So L3 stands
better than feared: the wordings did not move the object's colour, and the collapse still vanished.
It is still not a single-variable change — framing moved — but the variable the mechanism cares
about did not.

That is the second impression today, and the first one of mine, to meet a count and lose.

## 3. Arm A: the quiet seeds drift toward green

The eleven seeds that keep their colour do not keep it unchanged. Signed circular hue shift,
perturbed against the same seed's baseline, positive meaning toward green:

```
-10.4  -4.5  +0.7  +1.2  +1.5  +3.3  +17.9  +19.3  +24.3  +32.0  +33.8
```

**Nine of eleven move toward green, mean +10.8°, exact sign test p = 0.065.** Not significant, and
recorded as such — but it suggests the edit pushes the leaf *away from brown*, and that the collapse
may be the far end of that same push rather than a separate event. The two quiet cells nearest the
collapse threshold (chroma 0.518 and 0.602) sit at +17.9° and +24.3°, in the upper half of the
drift — while two cells with the largest drift keep their chroma entirely, so drift and collapse are
not one axis. It is a lead, and **C23's dose ladder will separate them**: if the collapse is the end
of a continuum, the intermediate doses will show cells partway along it.

## 4. What changes

* **L4 is downgraded from "falsified — leaf-specific" to "not tested".** Both
  `leaf_collapse_and_blk16_result.md` §3 and `what_broke_in_the_leaf.md` §3 are amended to say so.
* New register item: rerun arm C on **ambiguous-prior** subjects, screened with
  `experiments/prior_ambiguity.py` before any edit is rendered.
* Drafted defect **82**: choosing the test population by the property that makes the effect
  *impossible*. Four subjects were picked for a strong colour prior in order to test a mechanism
  that needs a weak one, and the resulting null was read as a falsification.
* L3 stands, with its framing caveat stated.
