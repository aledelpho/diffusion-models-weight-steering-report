# Plan — the q/k/v/o atlas, and why it is the decisive one

- **Written:** 2026-09-26, no render made for it.
- **Replaces the recommendation of** `docs/RUNBOOK_signed_atlas_plan.md` §6 (the channel atlas),
  for the reasons in `docs/prior_work_layer_specialisation.md` §3.

---

## 0. The design exists to settle a claim that is still `open`

`position-function-or-proximity` has been open since page 04 was written: *is the position effect
about what a block does, or merely about how little network remains downstream of it?* Nothing in
this project has separated them, because every condition ever rendered varied **depth**.

`wq`, `wk`, `wv` and `wo` sit in the **same block**, at the **same distance from the output**, on the
same residual stream. Any difference between them **cannot be proximity.** This is the first design
in the project where the two accounts come apart by construction rather than by argument.

It is also where the literature points. *AnyStyle* (arXiv 2607.04677) reports that modulating the
**query alone outperforms key, or query and key together**, reading queries as layout and objects
while key and value leak style; a review collects the same split from video work (Q, K → identity;
V → motion). And this project's own strongest recognisability sits in late attention —
`late_attn_d1` at 95.8 %, `late_mlp_d2` at 91.7 %, the middle bands at chance.

## 1. The instrument

**`ArthemyKrea2ModelBlockSurgeonTuner`** — "Tier 2: High-precision **deterministic** Sub-Block
component tuning". Explicit gain per component group, per band, **no seed and no draw**. The four
projections are already separate widgets: `ATTN_wq_query`, `ATTN_wk_key`, `ATTN_wv_value`,
`ATTN_wo_out`. Negative gain gives the opposite arm, exactly antipodal in the weights.

Not the Chaos node. Randomised signs are what made the previous atlas unable to answer this.

## 2. The 18 conditions

| # | condition |
|---|---|
| 16 | {`wq`, `wk`, `wv`, `wo`} × {`Block_1 (All 0-4)`, the last band as the widget lists it} × {+, −} |
| 2 | `NORMS_block_scales` over `All Blocks (0-27)`, + and − → **declared negative control** |

Two bands, not six: the q/k/v/o contrast is the primary and depth is present only as the coarse
early/late contrast the literature and this project already agree on. One gain for every condition,
the node's own default magnitude, and the displacement **measured** afterwards:

    python experiments/measure_all_displacements.py --all --out data/preset_displacements_qkvo.csv

Corpus: the same 8 prompts and 3 seeds as the atlas on disk, whose 8 baselines are reusable —
the pipeline is byte-deterministic across a week.

    18 × 8 × 3 = 432 renders.

## 3. The statistics — frozen before the first render

Displacement, scale and features exactly as `docs/prereg_style_capacity_amendment_01.md` §2, on the
23 style features, baseline-anchored and seed-paired.

For the 8 live (projection, band) cells at the + sign, per prompt:

- **A_proj** = mean cosine between **the same projection in the two bands** (4 pairs).
  *Does a projection keep its direction as depth changes?*
- **A_band** = mean cosine between **different projections in the same band** (2 × 6 = 12 pairs).
  *Do all components at one depth do the same thing?*
- **PRIMARY: G = A_proj − A_band**, averaged over the 8 prompts.

**Null:** the 8 cells' (projection, band) labels are exchangeable. All 8! = 40 320 relabellings are
enumerated exactly, as in `docs/prereg_style_axis_tradeoff.md` §3. Two-sided on G. Floor
1/40 320 = 2.48e-05.

**Secondary, also frozen:**

- **Antisymmetry:** cos(+, −) for each of the 8 cells. Exactly antipodal in the weights by
  construction; the deviation in the image is the rectification map. `tail-is-rectified` predicts the
  late band deviates more than the early one — a directional prediction, recorded now.
- **The literature's claim:** rank the four projections by their mean distance to the other three,
  within each band. *AnyStyle* predicts `wq` separates from the rest. Recorded as a prediction made
  before the data, not as a hypothesis to fit afterwards.

## 4. Decision rules — frozen

1. **Pipeline broken** if the negative control (`NORMS_block_scales` ±) is distinguishable from the
   baseline or from itself. Nothing else in the run is read.
2. **Proximity** if G < 0 beyond the null: components at one depth act alike and a projection does
   not keep its identity across depth. Wording fixed now: *the position effect is about how much
   network remains downstream, and the component is not a control.* This closes
   `position-function-or-proximity` in favour of proximity.
3. **Function** if G > 0 beyond the null: a projection keeps its direction across depth while
   projections at one depth diverge. Wording fixed now: *what a sub-component does is a property of
   the sub-component, not of its depth* — and the four projections become four knobs.
4. **Neither** if G is inside the null. The design had the power to separate them and did not; report
   it and do not reach for a third reading.

No claim enters `notebook/` from this study without a separate, explicit decision.

## 5. What would kill it

- Two bands only. The depth axis is coarse on purpose; a projection could keep its identity between
  blocks 0–4 and 24–27 and lose it in the middle, and this design would not see that.
- One gain, so the four projections do not carry equal displacement. `wq`, `wk`, `wv`, `wo` differ in
  shape and norm, so the magnitude confound is real and lives in the analysis: every statistic is
  reported raw **and** per unit of measured displacement, as
  `output-lead-survives-dose-normalisation` requires. Cosine is scale-free, which is why the primary
  is built on cosines and not on distances.
- The existing 24 atlas presets can be projected onto the new ± axes only **approximately**: the new
  bands (0–4, 24–27) overlap the old quarters (0–6, 21–27) without matching them. Any such projection
  is descriptive and is labelled so.
- Three seeds, eight prompts sharing one subject. As in every study on this corpus.

## 6. On whether the agreement with FLUX is a cross-architecture result

It is convergent evidence and it is worth having. It is **not** yet a cross-architecture law, for
three reasons that belong in any write-up:

1. **FLUX and Krea-2 are the same family.** Both are monolithic diffusion transformers. The genuinely
   different architecture is the UNet, and there *Unpacking SDXL Turbo* finds **cleaner, more
   separated** per-block roles (`down.2.1` composition, `up.0.1` colour and texture) — which supports
   the observer's original intuition that UNets carry more distinct block roles than DiTs do. Two
   families, two behaviours; Krea-2 sits with FLUX.
2. **The agreement is on direction, not on magnitude.** No one has compared numbers. *AnyStyle*
   reports a design choice and an ablation ranking; this project reports r = −0.659 and a 9.1×
   asymmetry. "We agree on the sign" is the honest phrasing.
3. **And the shared finding has a mundane explanation that is exactly the open claim.** "Later layers
   do finer and more stylistic things" follows from having less network downstream to absorb a
   perturbation, with no appeal to function at all. Until `position-function-or-proximity` is closed,
   the cross-architecture agreement may be an agreement about **depth in a stack** rather than about
   style. Which is why this experiment, and not another depth sweep, is the one to run.
