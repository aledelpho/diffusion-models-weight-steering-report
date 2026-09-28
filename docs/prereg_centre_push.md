# Pre-registration — can the centre be pushed further without breaking the drawing?

- **Deposited:** 2026-09-28, before any render of this bench existed.
- **Status:** frozen. Amendments go at the bottom, dated, never in the body.
- **Renders:** 295, listed in `data/centre_push_plan.csv` and queued by
  `experiments/queue_centre_push.py`. Alessandro launches them; nothing here launches a render.
- **Analysis:** `experiments/analyze_centre_push.py`, committed with this document, before any data.
- **Parent:** [`groove_or_hole_result.md`](groove_or_hole_result.md) §4, the post-hoc position pattern.

---

## 0. What is already known

This study exists because of an exploratory reading of existing data, and the reader should see it.

On `benchmark_mappa` and `benchmark_profondita`, pooled, the line coherence `L` falls with visibility
`V` at a slope of **−0.037 per unit of ln V** for the end groups, against **−0.005** for the central
ones. At `V` between 1.5 and 2.5, the ends read `L` 0.945 and the centre 0.992. Visible end units were
mostly holes (14 of 16 in M); central ones about half.

**The weakness of that reading is the reason this study renders.** It was found after the fact, on
two prompts, and on the same three seeds (42, 777, 1337) that every earlier bench used. **This study
uses three seeds never used on these arms**: 2718281, 3141592 and 1618033. Every primary number comes
from renders that do not exist yet.

## 1. The claim

Alessandro, 2026-09-28 at 17:43, verbatim:

> Perdonami, volevo dire che il centro si può muovere molto di più senza rovinare l'immagine ma
> cambiando di più il contenuto, perché si tira dietro meno noise o artefatti.

*Translation.* What I meant is that the centre can be moved much further without ruining the image,
changing the content more instead, because it drags less noise or artefacts along with it.

It contains three claims, which are tested in this order of weight:
1. **at equal visibility, the centre keeps the drawing better than the ends** (primary);
2. **it drags fewer artefacts along**, in the sense of staying closer to what the model already does
   (S4);
3. **it changes the content more** (S2, if a content measure can be computed).

## 2. Design

| factor | levels |
|---|---|
| group | `Block_1` … `Block_6` (ends = 1 and 6; centre = 2 to 5) |
| sign | positive, negative |
| dose | 0.080, 0.200, **0.350, 0.500** |
| prompt | P01, P02: the same text as `benchmark_mappa`, byte for byte, read from its renders |
| seed | 2718281, 3141592, 1618033 |

That makes 288 perturbed renders, 6 baselines and 1 determinism row: **295 in all**.

- **Drive:** the group input of `ArthemyKrea2ModelTuner`, `Real Value` mode, empty
  `vectors_override`, exactly as `benchmark_mappa` was driven (verified from its PNG graph).
- **Baselines:** the tuner node is absent, not set to zero.
- **Sampler:** `euler_ancestral` / `simple`, 9 steps, CFG 1.0, 1024×1280.
- **Output:** `benchmark_centre_push/renders`.

**Why 0.350 and 0.500.** Up to 0.200, only three central units ever passed `V = 2.5`. The claim is
that the centre *can be moved much further*. That cannot be tested at doses where it never moves
far. The two new doses take the centre into the range where the ends are known to break. The ends
at 0.350 and 0.500 are expected to be destroyed, and that is their job: they populate the high-`V`
end of their own curve.

## 3. Measures

All reused unchanged:
- `V`: the visibility of `prereg_groove_or_hole.md` §3.2. The consistent part of the edit over
  seeds, in units of the seed noise of the same prompt text in the base cloud.
- `L`: structure coherence, edit over same-seed baseline, computed with `measure()` of
  `experiments/retro_texture_axes.py`.
- `Δout`: distance from the base model's repertoire, as in `prereg_groove_or_hole.md` §3.1.

The unit is **(group, sign, dose, prompt)**, averaged over the three seeds: 96 units.

**Content (S2 only).** The cosine distance between DINOv2 ViT-S/14 CLS embeddings (`timm`
`vit_small_patch14_dinov2.lvd142m`) of the edit and its same-seed baseline. It is divided by the
median of the same distance between this bench's baselines of the same prompt at different seeds.
It is a semantic distance: it moves when *what* is in the picture moves, and much less with texture.

## 4. Decision rules — frozen

**Primary.** For each of the 12 group-arms, the OLS slope β of `L` on `ln V` over its 8 units (2
prompts × 4 doses). The statistic is

`T = mean β(8 central arms) − mean β(4 end arms)`.

The claim predicts **T > 0**: the centre's line falls more slowly with visibility. The null is exact
over all C(12,4) = 495 ways of labelling 4 arms as "ends", with a one-sided p because the direction
is predicted.

| verdict | condition |
|---|---|
| **supported** | T > 0, p ≤ 0.05, and G_range passes |
| **not supported** | G_range passes, and T ≤ 0 or p > 0.05 |
| **inconclusive** | G_range fails: the centre was not pushed far enough to test the claim |

**Secondary, descriptive, no p-values:**
- **S1:** among units with `V ≥ 1.5`, the share with `L < 0.98`. The claim predicts centre < ends.
- **S2, content:** in bins of `V` (1–1.5, 1.5–2.5, ≥ 2.5), the median content shift. The claim
  predicts centre > ends at matched V.
- **S4, artefacts:** among visible units (`V ≥ 1`), the share of holes (`Δout > 0`). The claim
  predicts centre < ends.
- **S3, `Block_5 pos`**, the known exception, which collapsed at 0.200 on the old seeds: its β is
  reported beside the other central arms and named.

## 5. Guards — run before any statistic

- **G_det:** the determinism row (P01, `Block_3` +0.200, seed 42) must reproduce the existing
  `benchmark_mappa` render **pixel for pixel**. If it does not, stop: the pipeline has changed since
  that bench.
- **G1:** every one of the 295 renders is present. Its embedded graph matches its plan row (prompt
  hash, seed, steps, size, and group gain). Baselines carry no tuner node.
- **G3:** no perturbed render may be pixel-identical to its baseline (an edit that never arrived).
- **G_range**, part of the primary rule: at least 3 of the 8 central group-arms reach a mean `V ≥ 2`
  over the two prompts at some dose.
- **G_content:** if DINOv2 cannot be computed on the analysis machine, S2 is dropped and recorded.
  No other content measure is substituted after the fact.

## 6. The eye

`L` has already been seen to rate a regular artefact as "more line" (`STORY.md` §VII), so it is
checked before the primary is reported.

**G_eye.** Twelve pairs, each a central and an end unit with the closest `V` in the range 1.5–3,
shown at **1:1 crops** (a 512-px centre crop), unlabelled, in random order. Alessandro marks which
of the two is more broken, or "neither".

If his answer agrees with the ordering of `L` in **fewer than 8 of the 12 pairs** (ties excluded),
the primary is reported as **"L not validated by eye"** next to its number, and is not called
supported.

## 7. Predictions — deposited now

- **Alessandro:** §1, verbatim.
- **Analyst:**
  - T > 0 with p ≤ 0.05: probability about **0.55**.
  - The exploratory slopes will shrink on new seeds, as every exploratory estimate in this project
    has done.
  - `Block_5 pos` will behave like an end arm, with the steepest central β.
  - The ends at 0.500 will be black or washed out.
  - At least one central arm, most likely `Block_4` in one sign, will reach `V ≥ 2.5` with
    `L ≥ 0.98`.
  - S2 (the content claim): no firm expectation, probability 0.4 that the centre exceeds the ends in
    both of the upper bins.

## 8. What this cannot settle

- **Two prompts, one comic register.** `L` only discriminates on line-bearing styles, so this is a
  claim about drawings with a line.
- **"Content" means what a DINOv2 embedding sees.** That is not the same as what a person would call
  the content. A content change that DINOv2 misses reads here as no change.
- **The four doses are coarse.** A central arm that holds at 0.350 and breaks just above it is
  reported as holding.
- **Group sliders only.** A central *single block* that behaves differently from its group is not
  tested here.

## 9. Outputs

- `data/centre_push_measures.csv`: per render; 23 features, coherence and the DINOv2 embedding.
- `data/centre_push_guards.csv`.
- `data/centre_push_units.csv`: 96 units.
- `data/centre_push_tests.csv`.
- `docs/centre_push_result.md`.
