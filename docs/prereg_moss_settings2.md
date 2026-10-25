# Pre-registration MOSS-S2 — S2 again at doses that move the picture; turbo at 10 steps, euler and euler_ancestral

Written 2026-10-25 by Claude, **before any render.** MOSS-S (`docs/moss_settings_result.md`) could not decide S2: at
d ≤ 0.30 the edits moved pictures by 0.001–0.036, below what a ranking can resolve. Alessandro agreed to work in turbo
with confirmations fixed in advance, raised the turbo to 10 steps (he checked the quality) and asked to try it with
euler_ancestral.

## Design (72 renders, about 1 h 30 min)

* **Settings:** R50 (euler, 50, CFG 3), E25 (euler, 25, CFG 3), **T10** (DMD2 LoRA, euler, 10 steps, CFG 1), **T10A** (DMD2
  LoRA, euler_ancestral, 10 steps, CFG 1). Simple scheduler, shift 5, 1024 × 1280, SFT bf16, tuner v4.
* **Cells:** dwarf and rally at 2645751; plain, and the four MOSS-S edits (DiT MLP down 6 and 20, TE MLP down 6 and 27) at
  **d = 1.0 and 2.0** (16 edit cells per setting).

## Rules (fixed now)

* **Power (reported first):** median R50 edit distance; if below 0.03 the test is again uninformative and no setting is
  chosen from it.
* **S2 per setting (E25, T10, T10A):** Spearman with R50 over the 16 cells ≥ 0.80 and median ratio 0.5–2.
* **Use:** T10 or T10A (the one passing; if both, the one Alessandro prefers on the sheet; if neither, still the working
  setting for sweeps, labelled "turbo", with every reported result confirmed) for the MOSS experiments. **Confirmations**
  on E25 if E25 passes S2, otherwise on R50. Each MOSS pre-registration names its confirmation cells (10–15 %) before
  any render, and a confirmation counts when Alessandro, blind, sees the same kind of change.

## Limits

One seed, two prompts, four edits; DINOv2 distance only.
