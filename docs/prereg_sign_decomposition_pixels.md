# Pre-registration — pixel-level decomposition of the signed block map

**Deposited**: 2026-09-26, before any of the statistics below was computed.
**Corpus**: `benchmark_mappa/renders`, already on disk, 519 PNG. **No new renders.**
**Author of the predictions**: analyst (Claude). **Observer predictions**: none recorded for this
analysis; the visual observations in `observer_predictions_atlas_phase1.md` concern a different
bench.

---

## 1. The gap this closes

The project has asked the sign question once, in
[`punto7_attrito_e_rettificazione.md`](punto7_attrito_e_rettificazione.md), on a different corpus
(`benchmark_profondita` / `benchmark_profondita_neg`, 28 single blocks) and at **one dose per sign**
(±0.200). Two limits are stated in that document and are the reason for this pre-registration:

1. §1 reports that at `D = 0.050` the common mode costs nothing, and concludes: *"Non è una tassa
   fissa: è una soglia, e dove cada non è ancora misurato."* The dose has never been swept on both
   arms.
2. §5 tests mirroring as `r⁻ = 1/r⁺`, a ratio between **two scalar** high-frequency numbers. A block
   can satisfy that ratio while moving the image in an entirely unrelated direction. The
   directional test has never been run.

Neither the sign comparison nor any other measurement in this project has so far been made on the
**pixels** of a positive/negative pair. All of it has been made on summary features.

## 2. Material and design

Sampler `euler_ancestral`, 9 steps, CFG 1.0, scheduler `simple`, 1024×1280 RGB.

Same-seed determinism on this exact bench is already on record in `data/bench_checks.csv`
(`determinism_across_sessions`, P01 seed 42, `benchmark_determinismo` vs `benchmark_mappa` across a
ComfyUI restart, max channel difference **0**). This is what makes a pixel difference against the
same-seed baseline a pure weight effect with no sampler term. The analysis depends on that row; if
it were wrong, everything here falls.

**Primary (balanced) design**: 6 block groups (`Block_1` … `Block_6`) × 6 doses
(0.020, 0.035, 0.050, 0.080, 0.120, 0.200) × 2 signs × 2 prompts (`P01`, `P02`) × 3 seeds
(42, 777, 1337) = **432 images**, plus 6 baselines.

**Excluded from the primary**: prompt `A01`, whose negative arm exists only at 0.050 (unbalanced);
used only in a secondary check at that dose for `Block_1` / `Block_6`.

**Secondary**: `Projection`, `Text_Fusion`, `Time_Embed` at ±0.050 only.

## 3. Statistics, frozen

Images to float32 in [0,1], all three channels, flattened. For one cell = (prompt, seed):

```
Dplus  = I(block, +d) - I(baseline)
Dminus = I(block, -d) - I(baseline)
c = (Dplus + Dminus)/2      # common mode: the part that does not depend on the sign
m = (Dplus - Dminus)/2      # signed mode: the part that reverses with the sign
a = cos(Dplus, Dminus)
F = ||c||^2 / (||c||^2 + ||m||^2)       # PRIMARY: sign-blind share of the energy
rho_mag = ||Dplus|| / ||Dminus||
```

`F` is the primary statistic and is reported instead of `a` because it does not assume
`||Dplus|| = ||Dminus||`; when the two norms are equal, `F = (1+a)/2` exactly.

Interpretation, fixed now: `F → 0` means the block is a **linear knob** (plus does a thing, minus
undoes it). `F → 1` means the block is **rectified** (either sign does the same thing). `F` is the
fraction of the image change that carries no control.

High-frequency share, fixed 3×3 Laplacian `[[0,-1,0],[-1,4,-1],[0,-1,0]]` per channel:
`HF(x) = ||lap(x)||^2 / ||x||^2`.

**Different-block reference**, built from the data, same dose and same sign, all 15 unordered pairs
b≠b′: `cos(Dplus_b, Dplus_b')`. This is the "two unrelated perturbations" level and is **not** zero,
because every perturbation shares a common mode; it is the correct thing to compare the same-block
cosine against.

**Unit of analysis and inference.** There are only **two prompts**, so no prompt-level p-value is
claimed (pitfall 17). The unit is the cell (prompt × seed), 6 cells. Each effect is reported as the
mean over cells **and** as the number of cells in the predicted direction; the criterion is
unanimity, 6/6. The exact two-sided sign-test floor on 6 cells is 2/2⁶ = **0.03125**, and no p-value
below that can be produced by this design.

## 4. Predictions, frozen before computing

| # | prediction | confirmed if | falsified if |
|---|---|---|---|
| **P1** | first order dominates at the smallest dose | mean `F` over the 6 groups at dose 0.020 **< 0.25** | **> 0.40** |
| **P2** | the sign-blind share grows with dose | Spearman ρ(dose, `F`) > 0 in ≥ 5/6 groups **and** pooled ρ **> +0.50** | pooled ρ < +0.20, or < 4/6 groups positive |
| **P3** | at the dose Punto 7 called costless, control still dominates | mean `F` at dose 0.050 **< 0.30** | **> 0.45** |
| **P4** | rectification is a tail property (Punto 7 §3) | `Block_6` has the **highest** mean `F` over doses, and `Block_1` is in the lower half | `Block_6` ranks 4th or worse |
| **P5** | the positive arm moves the image more (Punto 7 §3) | `‖Dplus‖ > ‖Dminus‖` at dose 0.200 in ≥ 5/6 groups | ≤ 3/6 |
| **P6** | antisymmetry is a same-block property | at dose 0.020, mean different-block cosine minus mean same-block `a` **> +0.30** | gap < 0 |
| **P7** | the sign-blind part is the high-frequency part (Punto 7 §1, the VAE story) | `HF(c) > HF(m)` at dose 0.200 in ≥ 5/6 groups | ≤ 3/6 |

Anything between the two columns is reported as **grey**, not argued either way.

**P4 is the prediction most likely to fail, and its failure is the informative one.** `Block_6` here
is a macro-group, not the blocks 23–27 that Punto 7 found rectified; if the grouping dilutes the
tail, P4 fails for a reason that is about the grouping and not about the model.

## 5. Guards, checked before any statistic is read

* **G1** — all 6 baselines present; any missing → abort, nothing reported.
* **G2** — every image 1024×1280 RGB; any mismatch → abort.
* **G3** — `‖Dplus‖ > 0` and `‖Dminus‖ > 0` for every cell. An exact zero is a **dead slot**
  (`mod.lin` / norm-scale precedent, pitfall candidate 70), not noise: zeros are listed by name and
  excluded, never averaged in.
* **G4** — the different-block reference of §3 must be computable for all 6 doses, else P6 is
  dropped rather than approximated.

## 6. What this analysis may not do

* It may not change the status of any published claim. Punto 7 §3 and §5 are the claims in contact
  with it; if the result disagrees with them, the disagreement is reported and the decision is
  Alessandro's.
* It produces no new renders and requests none.
* `c` and `m` are images and will be written out as viewable maps. Any statement made from **looking**
  at them is descriptive and labelled as such, never as a result.
