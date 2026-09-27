# Is colour bound to the concept? What the data can and cannot say

**Date**: 2026-09-27 · **Question**: Alessandro's — are colours tied to concepts, is that why they
resist being moved, and do they move *more* when the prompt declares them explicitly?
**Material**: existing data only. **No render generated.** Exploratory; nothing here changes a claim.

---

## 1. "Colour is tied to the concept" — supported, but by a different measurement

The evidence is not that colour resists moving. It is that **the colour response does not belong to
the edit**:

| trait subset | transfer across subject | permutation p |
|---|--:|--:|
| texture | **0.778** | **0.0097** |
| stroke | 0.750 | 0.0222 |
| **colour** | **0.514** | **0.233** |
| tone | 0.514 | 0.118 |

(`signature_robustness_result.md` §3.) An edit's colour displacement on one subject **does not
predict** its colour displacement on another — it sits at chance — while its texture displacement
does. Colour moves; it just moves in a way that is a property of *what is in the picture*, not of
*what was done to the weights*. That is the operational form of "bound to the concept", and it is
the strongest thing in the project on this question.

It also sharpens a published claim without contradicting it.
`edits-move-colour-in-different-directions` (page 07, `holds`) says edits differ from one another in
colour. Both are true: **colour distinguishes edits within a subject and carries nothing across
subjects.**

## 2. "We cannot move colour very much" — weak support, not established

Displacement of each trait in units of its own seed noise, prompt as the unit of analysis:

| corpus | displacement | colour < texture | mean ratio | exact sign test |
|---|---|--:|--:|--:|
| `benchmark_atlas_phase1` | D = 273 | **6 / 8 scenes** | **0.681** | p = 0.145 |
| `benchmark_qkvo_atlas` | D = 23–65 | 4 / 8 scenes | 1.024 | p = 0.637 |

At large displacement colour moves about **two thirds** as much as texture, consistently in
direction but **not significantly** with eight prompts. At small displacement there is no
difference at all.

**A caution on the strongest-looking number.** `S8_charcoal` shows the largest colour movement in
both corpora — and it is the scene whose prompt declares *monochromatic, black and white*. That is
a **denominator artefact**: its colour seed-noise is the smallest of the eight
(`colorfulness_hs` sd **0.42** against **4.21** for `S3_lowpoly`, mean colourfulness 24.9 against
56.5). Dividing by a tiny noise inflates the z. The right normaliser for "is it above noise" is the
wrong one for "how much did it move", and this is the same trap as the retracted steering fraction
(pitfall 63).

## 3. "Colour moves more when declared" — not testable on anything we have

**All eight scenes of `benchmark_qkvo_atlas` carry the identical subject text**, colours included:

> *Subject: a **yellow and blue** rally car cruising in a deep jungle, uneven street, daylight, lush
> plants, humidity, reflective ponds.*

Only the style clause differs, and five of the eight name a colour property (`soft colors`,
`flat ink colors`, `limited color palette`, `vibrant translucent`, `monochromatic`). Splitting on
that:

* style clause names colour (5 scenes): **1.30**
* style clause does not (3 scenes): **1.62**

The difference runs **opposite** to the hypothesis, the scatter is 0.59 to 2.52, and the split is
5 against 3. **This number means nothing** and is reported only so that it is not discovered later
and mistaken for evidence. The three `benchmark_mappa` prompts all declare colours too, so they
offer no contrast either.

## 4. What the outside literature says, and it converges with our own q/k result

* **ColorWave** (WACV 2026, SDXL / SD3.5-L / FLUX.1-dev) locates colour attribute binding at the
  **key projection**: it measures ⟨K, K′⟩ between the key projections of colour-word tokens and
  image features, and reports that a declared colour **dominates** — overriding it requires
  semantic proximity, and distant colours (olive, navy, yellow against "red") **fail to override**.
* **Color Bind** (2025, SD 1.4/1.5/2.1, FLUX) finds colour binding is compositionally fragile:
  61 % accuracy on a single coloured object against 26 % on a distant colour pair, with "colour
  leakage" between objects as the main failure, and five inference-time correction methods all
  **degrading** single-object performance.

The convergence with our own measurements is worth stating. If colour binding is carried by the
**key** projection, then it lives in the path this project measured as the one the sign cannot
control: `wq` / `wk` reverse with the sign in **0.067–0.120** of above-noise traits against
**0.538–0.758** for `wv` / `wo`, and move only **1.0–2.0** of 23 traits above the seed floor against
3.5–5.9. Two independent routes — a literature on attention binding, and a weight-steering bench —
land on the same projections.

And ColorWave's finding cuts **against** the second half of the hypothesis: a declared colour
*dominates*, which predicts it should be harder to move, not easier.

## 5. The experiment that would settle it, and why it is worth running

The two hypotheses make **opposite** predictions, which is the whole value of the design.

* **Alessandro's**: a declared colour is a live variable carried by the text encoder, so perturbing
  weights perturbs it → colour moves **more** in the declared variant.
* **ColorWave's**: a declared colour token binds hard through K and dominates → it moves **less**.

Design: **one subject, two prompt variants** — colours explicit (*"a yellow and blue rally car …
lush green plants"*) against colours stripped (*"a rally car … lush plants"*), everything else
identical. Crossed with a small set of edits at matched displacement, both signs, two doses, three
seeds. Roughly **96 renders plus 6 baselines**, the prediction frozen before the first one.

Primary statistic: colour-trait displacement in units of that variant's **own** colour seed noise —
measured per variant, because §2 shows exactly how that denominator can be made to lie. Both
variants must have their noise floor measured from their own baselines.

Alessandro launches renders; this is a proposal, not a plan in motion.

Sources: [ColorWave](https://arxiv.org/abs/2503.09864) · [Color Bind](https://arxiv.org/html/2508.19791)
