# C64 phase 1 — text-encoder layers at dose ±1.00, read by eye (2026-10-11)

Exploratory pilot, one prompt (P1_elfbrawler), one seed (1618033). Plan and amendments: `docs/plan_te_pilot.md`.
Edits scale Qwen3-VL-4B weights by ×(1+d) through ArthemyKrea2CLIPTuner: d = −1.00 sets the half (attention
q,k,v,o or MLP gate,up,down) of one layer to zero, d = +1.00 doubles it. Phase 1 shows only these two doses
(152 renders) plus six checks, blind, shuffled, with 10 repeats. One observer (Alessandro). Questions: how much
the render changed (none / slight / medium / strong / text), overall style (unchanged / changed, with a free
note), gauntlet arm (same / other / ambiguous), surface (cleaner … strong).

Data: key `data/te_pilot_eye_key_phase1.csv` (committed before labels), labels
`data/te_pilot_eye_alessandro_phase1.csv` (committed as downloaded, before counting), tables
`data/te_pilot_phase1_joined.csv`, `_repeats.csv`, `_summary.csv`. Code: `experiments/te_pilot_phase1_tally.py`.
Five renders carry answers imported from the earlier full page (column `imported`).

## Gates

* **Checks.** Layer 35 at +1.00 (never read by Krea-2): *none*, "identical pixel by pixel". Visual tower at
  +1.00: *none*. L02 MLP at +1.00 (expected active): *strong*. q+k only at L05/L17/L29: *slight* / *none* /
  *slight*, consistent with the ~10/255 pixel floor found earlier.
* **Self-agreement on the 10 repeats.** Change: 7/10 exact, 10/10 within one step. Arm: 10/10. Surface: 9/10.
  Style: 7/10 — the least stable question; style counts below carry that noise.

## What the eye saw (140 layer edits)

1. **Doubling a half changes far more than removing it.** Strong changes: 40 of 70 at +1.00 against 4 of 70 at
   −1.00 (Fisher p ≈ 2e-11). Style judged changed: 36/70 at +1.00, 9/70 at −1.00. Zeroing one half of one
   layer leaves the picture recognisably the same in most layers (53/70 *slight*); the exception is layer 0,
   where zeroing either half turns the picture into text (2/2, as in the first look).
2. **At +1.00 the MLP is the stronger half.** MLP+: 28/35 strong, almost every layer from L02 to L31. Attention+:
   12/35 strong, concentrated in L05–L22; from L24 on, attention+ is mostly *slight* (9/11).
3. **The style changes are real style changes, not damage.** Surface was judged *as the original* or *slight*
   in 125/140 and *cleaner* in 7; *medium* or *strong* in 8. The notes describe shifts of genre (anime, chibi,
   1990s cartoon, children's illustration, Franco-Belgian or "Adam Warren" comics, painted sketch) more often
   than noise. This is unlike the DiT blocks, where large edits mostly cost surface.
4. **Content goes with style.** At strong change the notes often list lost prompt traits (antlers, fur,
   pauldron, eyepatch, tan skin, gauntlet) and a moved camera; several renders keep every trait and change only
   the drawing (L20, L29 and L31 MLP+: "tutto coincide", "gli attributi ci sono tutti", "rispetto assoluto del prompt").
5. **The six DiT-side text slots** (txtfusion, txtmlp) at ±1.00: 11/12 strong, 10/12 style changed, both signs.
   One slot scales the whole adapter, so this is not comparable layer for layer.

## Under-specified choices flip

The prompt fixes neither the gauntlet arm nor the eye under the patch. Both flip often:

* **Arm:** other arm in 50/138, ambiguous ("hands merged", gauntlet between them) in 18/138 (two text renders
  excluded). Ambiguous arms were rarer at strong change (3/44) than at slight or no change (12/74); the
  difference is not significant (Fisher p ≈ 0.16).
* **Late attention, exploratory:** ambiguous arms gather where attention of layers 24–34 is edited, either
  sign: 8/22, against 10/118 elsewhere (Fisher p ≈ 0.002). This band was picked after looking at the table, so
  the p-value is descriptive, not a test. These are also the edits that change the picture least (18/22
  *slight*), which fits Alessandro's reading: a small push near the boundary between two poses lands between
  them.
* **Eyepatch side:** the notes mention the patch on the other eye in 58/140 renders (a lower bound: the notes
  are free text, not a question). It does not travel with the arm: patch moved in 35/70 renders with the same
  arm and 17/50 with the other arm.

## Limits

One prompt, one seed, one observer; two doses. "None" and "slight" are relative: several *none* renders note a
moved patch or lowered arm. The ±0.35 and ±0.10 renders are not yet labelled, so nothing here says where in dose
a change starts. A different seed could put the pose or patch on the other side of the boundary.

## Next

* Grid viewer `te_pilot.html` (`experiments/grid_viewer.py --set te_pilot`) is now open to use: unblinding no
  longer affects phase 1.
* Candidate follow-ups, not decided: phase 2 on ±0.35 for the layers marked strong here; the late-attention
  ambiguous-arm band on new seeds as a pre-registered test; the eyepatch side as a second binary choice.
