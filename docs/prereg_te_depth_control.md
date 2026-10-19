# Pre-registration C102 — is a deep text-encoder edit more controllable than an early one, at the same push?

Written 2026-10-19 by Claude, **before any C102 encode or render.** Asked by Alessandro after C101 ("facciamo il prossimo
passo naturale"). Renders: 156 (4 prompts × 3 seeds × 13 conditions), with a blind pass by Alessandro.

## 1. Why

C101 (`docs/te_shapes_layers_result.md`): in the conditioning, an MLP edit in the first third of the encoder bends exactly
like a random push of the same size injected at the same place (edit − control +1°, layers 0–11), while from the middle on
the edit is straighter than chance (−16°, layers 24–34). C100: the curve is the edit's, not the prompt's. Reading: early
edits carry no direction of their own beyond what the network imposes; deep edits do. Untested: whether this shows **in
the pictures**. If it does, a deep edit changes the picture "the same way" across seeds and a random push at the same
place does not; an early edit and its random push behave alike.

## 2. Design

* **Prompts (4, from C100):** `D1_dwarf_paladin` (comic portrait), `S1_rally` (photo), `C4_stilllife` (cartoon still
  life), `P5_comic_panels` (comic page). Texts from their plans.
* **Seeds (3):** 2645751, 3316624, 2718281. Sampler as every Krea-2 run here: euler_ancestral, simple, 9 steps, cfg 1,
  1024 × 1280.
* **Edits (MLP, ×(1+d)):** early **L04**, **L09** (C101: edit not straighter than its control); deep **L26**, **L30**
  (C101: edit straighter by 9° and 32°).
* **Random controls:** at **L09** and **L26**: per-token random unit directions (seed 9393) added to that layer's MLP
  output, scaled by α × the per-token norm of the unedited MLP output.
* **Matched push.** The push is the relative change of the whole conditioning, τ = ‖c − c₀‖ / ‖c₀‖ (Frobenius, all
  tokens, all 12 taps). Two levels per prompt, anchored on the edit we know: **τ₁ = τ of L06 MLP at d = 0.5** and
  **τ₂ = τ of L06 MLP at d = 1.0**, on that prompt. For every edit the dose d (and for every control the scale α) is found
  by bisection so that τ is within 1% of the target; a target not reachable with d ≤ 6 (α ≤ 20) is recorded and dropped.
  The encoder is seed-free: one conditioning per prompt × condition × level, used for all three seeds.
* **Route:** every picture, including the plain one, is rendered from a saved conditioning with the node variant `file`
  (TEP2), so all conditions share one route.
* **Conditions per prompt × seed (13):** plain C0; L04, L09, L26, L30 at τ₁ and τ₂; control L09 and control L26 at τ₁ and
  τ₂.
* **Gates:** the plain file-route render must be pixel-identical to the existing in-graph baseline where one exists: dwarf
  at 2645751 (`benchmark_portraits/phase_c`), rally at 2718281 (`benchmark_single_blocks_atlas/renders`), still life at
  2718281 (`benchmark_single_blocks_styles/renders`). Any failure stops the run.

## 3. Measures

* **Direction consistency (computed, primary).** DINOv2-large vectors (as C87); for each picture the change
  Δ = v(X) − v(C0, same prompt and seed). For each prompt × condition × level, **κ = mean pairwise cosine of Δ over the
  three seeds** (3 pairs). An edit "has a direction in the picture" if it changes the three seeds the same way.
* **How far the picture moves (reported).** D = 1 − cos(v(X), v(C0)).
* **Blind (Alessandro, primary together with κ).** One unit per prompt × condition × level (48 units): the three seeds
  side by side, each as plain → changed. Question, positive: **"Nelle tre coppie l'immagine cambia nello stesso modo?"**
  — sì / in parte / no (scored 1 / 0.5 / 0). Order random (seed 10202), conditions hidden, 6 units repeated for
  test–retest. The page is written after the renders, before any label.

## 4. Rules (fixed now)

Per prompt × level (8 cells), Δκ₀₉ = κ(L09) − κ(control L09) and Δκ₂₆ = κ(L26) − κ(control L26).

1. **Depth gives the edit a direction in the picture (computed):** Δκ₂₆ ≥ 0.10 in ≥ 6 of 8 cells **and** Δκ₀₉ < 0.10 in
   ≥ 6 of 8. *Both have a direction:* both ≥ 0.10 in ≥ 6 of 8. *Neither:* both < 0.10 in ≥ 6 of 8. Otherwise *mixed*.
2. **The eye agrees (blind):** with blind score s (mean over the 8 cells), (s(L26) − s(control L26)) − (s(L09) −
   s(control L09)) ≥ 0.25. Rule 1 counts as **supported** only if rule 2 agrees; if they disagree, the result is reported
   as disagreement.
3. **Reported:** κ for L04 and L30 (no own control: compared with the control of their band); D at equal push, deep (mean
   of L26, L30) against early (mean of L04, L09), share of prompt × seed × level where deep moves less; the doses found;
   blind test–retest on the 6 repeats.

**Tool rule.** Supported: deep MLP edits are the knobs that carry a direction, early ones act like structured noise; a
style or character tool should draw its edits from the second half of the encoder. Neither or both: depth does not
decide controllability in the picture, and C101's difference stays a property of the conditioning only.

## 5. Limits

One edit type (MLP); two layers per band; three seeds (κ from 3 pairs); DINOv2 change vectors are not validated as a
measure of "the same change" (C87 validated DINOv2 distances, not directions), hence the blind co-primary. The
file-route conditioning is not bit-identical to the in-graph one for edited encodes (TEP2 amendment 1); every condition
here uses the file route.

Script: `experiments/te_depth_control.py`. Directive: `docs/directives_antigravity_te_depth_control.md`.
