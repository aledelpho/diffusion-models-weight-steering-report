# The eye veto of `benchmark_centre_push` — what six blind observers and one sighted one saw

> **STOP — if you have not yet filled in `data/centre_push_veto_answers.csv`, close this file.**
> §2 names the units and the pairs. Reading it destroys your own blindness, and `G_eye` — the only
> veto that counts — needs a human who has not been told the answer. Twelve looks, then come back.

**2026-09-28.** Governed by [`prereg_centre_push.md`](prereg_centre_push.md) §6 and its amendment
[`prereg_centre_push_model_eye.md`](prereg_centre_push_model_eye.md). No render was generated: every
image here is a 512-px centre crop at 1:1 from a PNG already on disk.

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

## 1. The verdict

**`L` is not validated by eye. The threshold cannot be reached — not because the eye disagreed, but
because the eye could not see a difference at all in 7 of the 12 pairs.**

| | pairs resolved | agree with `L` | exact two-sided sign |
|---|--:|--:|--:|
| **M1** — three blind observers, majority vote (**the result**) | **5 / 12** | **4** | p = 0.375 |
| M1b — mirror control, *not scored by the rule deposited before it ran* | 7 / 12 | 6 | p = 0.125 |

Eight of twelve agreements were required. With seven pairs tied, eight is arithmetically
unreachable. **`G_eye` as written by Alessandro is still owed and is unaffected by this**: a human
eye is the point of that gate, and three instances of one model are not three observers.

### The mirror control

All five M1 answers fell on the right-hand image. Since side was randomised, a right-hand habit and
a real perception of damage produce the same table, so the twelve sheets were cut again **with the
halves swapped** and three fresh observers judged them. The rule was deposited first:

> The mirrored majority names the **same image** → position bias ruled out, M1 stands. The **same
> side** → M1 is discarded in full.

**Five of five flipped side. Zero kept side.** The observers were looking at the pictures.

## 2. Where `L` and the eye part company — the four named cases

`L` is structure coherence, (λ₁−λ₂)/(λ₁+λ₂) of the gradient structure tensor over a 9×9 window,
as a ratio to the untouched baseline. Above 1 means *more* oriented structure than the original.

| unit | `L` | what is in the picture |
|---|--:|---|
| `Block_1 neg 0.500` (P02) | **1.0219 / 1.0341** | smeared, every contour doubled with a rainbow fringe, knit reduced to confetti. **Six observers out of six called it broken. `L` puts it above baseline.** |
| `Block_6 pos 0.080` (P01) | **1.0589** | the flat fills are peppered with isolated black flecks and a dense micro-stipple; `L` ranks it as *less* broken than the clean `Block_4 pos 0.200` at 0.9483, and **the eye ranks it the other way, 6/6** |
| `Block_3 pos 0.350` (P02) | **0.8675** | a clean cardigan, crisp button, closed contours, fine regular hatching. Nobody called it broken. `L` scores it **below** the confetti catastrophe of `Block_6 pos 0.200` at 0.9319. |
| `Block_6 neg 0.200` (P02) | **0.8737** | dense fine intact hatching. `L`'s second-worst score in the set, on a drawing no observer called damaged. |

The single scored disagreement, pair 08, is the second row: `L` says the clean `Block_4 pos 0.200`
is the broken one and the flecked `Block_6 pos 0.080` is the sound one. All six observers, in both
orientations, said the opposite.

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

- **No claim status has been changed.** The analyst does not change one alone. What the bench's
  primary should now say is a decision for Alessandro, recorded as **A8**.
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
- M1 answers: `data/centre_push_model_eye_answers.csv`. M1b: `data/centre_push_model_eye_mirror.csv`.
- Six observers, three per orientation, each with access only to the image folder: no repository, no
  key, no measurements, and no arithmetic of any kind — the instruction forbade computing anything,
  because a measured answer would only have reproduced `L`.
- Sheets: `benchmark_centre_push/_eye_veto/`, zoom tiles cut at 1:1 from the same crops.
- **Analyst predictions, deposited in the amendment and scored here:** *M1 agrees in 7 of 12* —
  **wrong**, 4 of 5 judged with 7 ties. *Observers disagree with each other on at least 4 pairs* —
  **wrong**, they disagreed on 2. *Where `L` is large and negative the visible difference is grain,
  not line* — **right**, and §2 names the units.
