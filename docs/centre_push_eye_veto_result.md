# The eye veto of `benchmark_centre_push` — run, and `L` did not survive it

**2026-09-28.** `G_eye` of [`prereg_centre_push.md`](prereg_centre_push.md) §6, **answered by
Alessandro**, plus the model-eye amendment [`prereg_centre_push_model_eye.md`](prereg_centre_push_model_eye.md)
that ran first. No render was generated: every image is a 512-px centre crop at 1:1 from a PNG
already on disk.

> The veto is closed. This document is safe to read; it was not, before the answers existed.

## 0. What was already known before this ran

Searched `docs/` and `notebook/` for the claim below, in English and in Italian, before writing a
line of it:

- **`notebook/STORY.md` §VII already says it**, in one sentence: *"An orientation statistic can read
  a regular artefact as 'more line'."* That is why `prereg_centre_push.md` §6 made the eye veto a
  gate in the first place. **The hypothesis is not new here.**
- `docs/retro_qkvo_atlas_reading_result.md` uses coherence ≥ 0.965 as evidence that renders were
  *not* collapsed — an inference this document shows to be unsafe.
- `docs/retro_axes_atlas_result.md` §2 already scoped coherence to line-bearing styles.
- Nothing in either directory contained a **named condition** on which the statistic was shown to be
  wrong, or a mechanism for the direction of the error. That is what is new.

## 1. The verdict — `L not validated by eye`

**Alessandro answered nine of the twelve pairs and agreed with the ordering of `L` in seven.
Eight were required.** The pre-registered label therefore applies to the primary of the bench, and
applying it is not a judgement call: it is the rule deposited before the bench was rendered.

| | resolved | agree with `L` | exact two-sided sign |
|---|--:|--:|--:|
| **`G_eye` — Alessandro (the verdict)** | **9 / 12** | **7** | p = 0.1797 |
| M1 — three blind model observers, majority | 5 / 12 | 4 | p = 0.375 |
| M1b — mirror control, *not scored, by the rule deposited before it ran* | 7 / 12 | 6 | p = 0.125 |

Note what the arithmetic does here. Seven of nine is not a *disagreement* with `L` — it is above
chance, and the sign test on it is p = 0.18 in `L`'s favour. The gate fails because the
pre-registration demanded 8 of 12 and three pairs were unjudgeable, two of them cross-prompt. **A
gate that can be failed by honest ties is a gate that was set too tight for a design with 8 of 12
pairs across two different scenes**, and that is a defect of the pre-registration, not of the eye.
The label stands because it was deposited; the reason it fired is recorded here so it is not
mistaken for a rout.

**The rout is elsewhere, and it is in §2.**

### The three eyes agree with each other, and the human sees more

| | |
|---|---|
| pairs both Alessandro and the blind observers resolved | **7** |
| of those, agreement | **7 / 7** |
| pairs Alessandro resolved that no blind observer could | 2 (03, 09) |
| pairs nobody could resolve | 3 (02, 05, 11) — **2 of the 3 are cross-prompt** |

The blind observers' five answers all fell on the right-hand image, so the twelve sheets were cut
again **with the halves swapped** and three fresh observers judged them, under a rule deposited
first: name the same *image* → position bias ruled out; the same *side* → discard M1 entirely.
**Five of five flipped side, zero kept side.** Then the human, judging independently, agreed with
them on every pair where both could see. Three separate looks, one answer.

### The nine answers are a consistent ordering

Treated as a tournament — *this unit is more broken than that one* — the nine judgements contain
**no cycle**. `Block_6 neg 0.200` is called broken against `Block_2 neg 0.500` and intact against
`Block_5 pos 0.350`; that is not a contradiction but a transitive rank, and it is the only unit
judged in both directions.

## 2. Both of `L`'s failures are the same condition

Alessandro disagreed with `L` on exactly two pairs, **03 and 08**. They are the same unit.

| pair | the eye calls broken | its `L` | `L` calls broken instead | its `L` |
|---|---|--:|---|--:|
| 03 | `Block_6 pos 0.080` (P01) | **1.0375** | `Block_5 pos 0.080` (P01) | 0.9927 |
| 08 | `Block_6 pos 0.080` (P01) | **1.0589** | `Block_4 pos 0.200` (P01) | 0.9483 |

`Block_6 pos 0.080` appears in two pairs. **It was called broken in both — by Alessandro, and by all
six blind observers, in both orientations of the sheets.** `L` puts it *above* its own baseline
both times. A statistic that says a render gained structure, on the one condition three independent
looks single out as damaged, is not mismeasuring the size of an effect; it has the sign wrong.

The same holds for the other unit seen twice:

| unit | seen in | the eye | `L` |
|---|---|---|--:|
| `Block_1 neg 0.500` (P02) | 01, 10 | **broken both times**, 6/6 observers and Alessandro | **1.0219 / 1.0341 — above baseline** |
| `Block_6 pos 0.080` (P01) | 03, 08 | **broken both times**, 6/6 observers and Alessandro | **1.0375 / 1.0589 — above baseline** |

And in the other direction:

| unit | `L` | what the eye said |
|---|--:|---|
| `Block_5 pos 0.350` (P02) | 0.8268 | broken — `L` and the eye agree |
| `Block_3 pos 0.350` (P02) | **0.8675** | a clean cardigan, crisp button, closed contours; **nobody called it broken**, and `L` scores it below the confetti collapse of `Block_6 pos 0.200` at 0.9319 |
| `Block_6 neg 0.200` (P02) | 0.8737 | dense fine intact hatching; ranked broken only against the cleanest unit in the set |
| `Block_4 pos 0.200` (P01) | 0.9483 | the clean side of pair 08 — `L`'s worst score among the four units nobody called damaged |

**Agreement with `L` does not improve when `L` claims more.** Small |Δ`L`| (< 0.05): 3 of 4. Middle:
2 of 2. Large (≥ 0.10): 2 of 3. The disagreements are not in the noise band; they are where `L` is
confident and inverted.

## 2b. What the eye says about the bench's actual question — post hoc

The bench asked whether the middle of the stack can be pushed further than the ends without
breaking the drawing. Every pair here is, by construction, **one central unit against one end unit
at matched V**. So the nine answers are also a sign test on that question, run on the eye instead
of on `L`:

**The end block was the broken one in 7 of the 9 pairs** (exact two-sided p = 0.1797). One of the
two exceptions is `Block_5 pos 0.350` — the arm the pre-registration's own analyst prediction named
as the central arm that would behave like an extreme.

This is **post hoc and it is not a verdict**: the primary was a slope of `L` on ln V, not this, and
reclassifying `Block_5` after seeing the data is exactly pitfall 68. Recorded because the direction
is the same as the failed primary's (`T = +0.0534`, p = 0.1899) and because the eye and the
statistic now agree on the *direction* while disagreeing on the *units* — which is the sharpest
argument yet that the right pre-registration to write next measures damage by eye, or by a repaired
axis, and not by `L`.

## 3. The mechanism — a hypothesis, not a result

This section is written by an analyst **who had already seen the key**, and it was predicted in the
amendment before the crops were cut. It generates a test; it is not evidence.

`L` appears to track **stroke coarseness and local orientedness, not structural integrity**, and the
9×9 window is the reason:

- **fine dense hatching** (1–2 px, several orientations inside one window) → λ₁ ≈ λ₂ → **low `L`**,
  on drawings that are perfectly intact;
- **coarse bold strokes** (one orientation per window) → **high `L`**;
- **a uniform speckle or confetti field** at 3–5 px is *locally* oriented everywhere, so it reads as
  structure and can push `L` **above** baseline on a render whose drawing no longer exists.

If that is right, the ordering is an artefact of window scale, and **recomputing `L` at 3×3 and 5×5
on these same 24 renders should reorder exactly these four units — at zero render cost.** That test
is registered, not run here.

## 4. What this does and does not change

- **The primary of the bench now carries its pre-registered label,** *"L not validated by eye"*, and
  is not called supported. Applying it is execution of a deposited rule, not a judgement.
- **No notebook claim changes status** — `centre_push` has no notebook page. What to do about every
  *other* document that leans on structure coherence is a decision for Alessandro, kept as **A8**.
- **It does not rescue the primary.** `T = +0.0534, p = 0.1899` failed on its own terms. The eye
  neither saves nor sinks it; it undermines the *axis* the primary was measured on.
- **It does reach further than this bench.** Every document that uses structure coherence as a
  damage or quality axis is affected, including `retro_qkvo_atlas_reading_result.md`, which argues
  from coherence ≥ 0.965 that renders were not collapsed. On the evidence above, a coherence near or
  above 1 is **not** evidence that a drawing survived.
- **What survives untouched** is `V`: displacement in style-feature space was never the disputed
  quantity, and the eye was never asked about it.

## 5. Provenance

- Selection, crops and sealed key: `experiments/centre_push_eye_veto.py --build`, key in
  `data/centre_push_veto_key.csv`, built and committed (`9f6a796`) before any observer ran.
- **Alessandro's answers**: `data/centre_push_veto_answers.csv`, scored by
  `centre_push_eye_veto.py --score` into `data/centre_push_veto_result.csv`. He judged them in
  `experiments/centre_push_eye_veto.html`, one pair at a time at 1:1 with a 4x nearest-neighbour
  loupe reading the same region of both crops; the page contains no part of the key.
- M1 answers: `data/centre_push_model_eye_answers.csv`. M1b: `data/centre_push_model_eye_mirror.csv`.
- Six observers, three per orientation, each with access only to the image folder: no repository, no
  key, no measurements, and no arithmetic of any kind — the instruction forbade computing anything,
  because a measured answer would only have reproduced `L`.
- Sheets: `benchmark_centre_push/_eye_veto/`, zoom tiles cut at 1:1 from the same crops.
- **Analyst predictions, deposited in the amendment and scored here:** *M1 agrees in 7 of 12* —
  **wrong**, 4 of 5 judged with 7 ties. *Observers disagree with each other on at least 4 pairs* —
  **wrong**, they disagreed on 2. *Where `L` is large and negative the visible difference is grain,
  not line* — **right**, and §2 names the units.
