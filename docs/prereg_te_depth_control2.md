# Pre-registration C103 — deep against early text-encoder edits, matched on the change in the picture

Written 2026-10-19 by Claude, **before any C103 encode or render.** Asked by Alessandro after C102 ("Ripetiamo").

## 1. Why

C102 (`docs/te_depth_control_result.md`) matched edits on the change of the conditioning (τ). At equal τ the deep edits
(L26, L30) barely moved the pictures (median DINOv2 distance 0.04–0.06 against 0.34–0.53 for L04, L09), so their
direction could not be judged; the blind question also lacked a "not visible" answer. C103 asks the same question with
the edits matched on **how much the picture moves**.

## 2. Design

* **Same as C102:** prompts `D1_dwarf_paladin`, `S1_rally`, `C4_stilllife`, `P5_comic_panels`; test seeds 2645751,
  3316624, 2718281; MLP edits L04, L09 (early), L26, L30 (deep); random controls at L09 (R09) and L26 (R26), seed 9393;
  file route for every render; sampler as C102.
* **Calibration (seed 1618033, not used in the test).** Per prompt, a ladder of four strengths per condition:
  L04, L09 at d = 0.5, 0.75, 1.0, 1.25; L26, L30 at d = 1.5, 3, 5, 8; R09 at α = 1.5, 2.25, 3, 4; R26 at α = 6, 12, 24, 48;
  plus the plain render: 4 × 25 = 100 renders. DINOv2 distance to the plain render at each step.
* **Targets:** picture change **D₁ = 0.12** and **D₂ = 0.30** (DINOv2-large, 1 − cosine to the same-seed plain render).
  For each prompt × condition × target, the strength is interpolated (log strength, linear in D, first crossing, with
  (0, 0) as the lowest point) from the calibration ladder. A target above the ladder's largest D is **unreachable**: that
  condition is dropped at that level and reported.
* **Test:** per prompt × test seed, the plain render and the 12 matched conditions: up to 156 renders.
* **Gates:** the 12 plain test renders must be pixel-identical to C102's plain renders (same conditioning, same route).
* **Blind (Alessandro):** as C102 (48 units + 6 repeats, three seeds as plain → changed, conditions hidden, order random,
  seed 10303), one question: **"Nelle tre coppie l'immagine cambia nello stesso modo?"** with three answers: **stesso
  modo** / **in modi diversi** / **non si vede**. Page written before any label.

## 3. Rules (fixed now)

0. **Match check (gate for the reading):** for each condition × level, the realized median D over the 12 test pictures.
   A condition whose realized median D is below half its target is **not matched**; if L26 or R26 is not matched at both
   levels, rules 1–2 are reported as **not testable** (the deep edits cannot be made to move the picture with these
   strengths).
1. **Computed:** as C102. Per prompt × level (cells where both conditions exist), Δκ₀₉ = κ(L09) − κ(R09), Δκ₂₆ = κ(L26) −
   κ(R26). *Depth gives the edit a direction in the picture* if Δκ₂₆ ≥ 0.10 in ≥ 75% of cells and Δκ₀₉ < 0.10 in ≥ 75%;
   *both*, *neither*, *mixed* as C102.
2. **Blind:** s = share of "stesso modo" among the units answered "stesso modo" or "in modi diversi" (first showing only).
   Needs ≥ 4 such units for each of L09, R09, L26, R26; otherwise *not testable*. *The eye agrees* if (s(L26) − s(R26)) −
   (s(L09) − s(R09)) ≥ 0.25. **Supported** only if rules 1 and 2 agree; disagreement is reported as such.
3. **Reported:** "non si vede" per condition; κ and blind share for L04 and L30; strengths chosen and unreachable
   targets; blind test–retest.

**Tool rule.** Supported: once deep edits move the picture, they move it their own way; they are the knobs for directed
change. Not supported: at equal picture change, depth does not make an edit more directed than a random push.

## 4. Limits

One calibration seed per prompt (the chosen strength may over- or undershoot at other seeds: rule 0 checks it); DINOv2
directions not validated (hence the blind co-primary); two layers per band.

Script: `experiments/te_depth_control2.py`. Directive: `docs/directives_antigravity_te_depth_control2.md`.
