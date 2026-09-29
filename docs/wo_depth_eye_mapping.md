# From Alessandro's words to measurements — fixed before any number is looked at

**Deposited 2026-09-29**, after his notes (`data/wo_depth_eye_notes_alessandro.md`) and **before**
any of the quantities below has been computed or inspected for these claims. The point is to stop the
analyst from choosing, afterwards, whichever feature agrees with the eye.

## Rules

- He described "i valori più negativi / più positivi": each claim is tested at the **extremes, ±0.350**,
  against the borrowed baseline of the same prompt and seed. 2 prompts × 3 seeds = **6 cells per claim**.
- A claim **agrees** in a cell when the measured change has the sign his words imply. Reported as
  k / 6, with an exact one-sided sign test (chance = 1/2), and **no correction pretending the cells
  are independent across prompts** (pitfall 17): the per-prompt split is printed alongside.
- ±0.350 is exploratory in C41; so is this whole check. It confirms or contradicts an observation;
  it confirms no pre-registered claim.
- One measure per phrase, chosen by meaning. Phrases with no honest measure are listed as such and
  **not** scored.

## The mapping

| # | slice | his words | measure (column of `wo_depth_measures.csv`, or `measure()`) | predicted sign vs baseline |
|---|---|---|---|---|
| E1 | b1, −0.350 | linee più spesse | `stroke_width_median_px` | up |
| E2 | b1, −0.350 | colori meno accentuati | `colorfulness_hs` | down |
| E3 | b1, +0.350 | linee più sottili | `stroke_width_median_px` | down |
| E4 | b1, +0.350 | colori più vibranti | `colorfulness_hs` | up |
| E5 | b1, +0.350 | tinte piatte | `color_n_effective` (fewer effective colours = flatter) | down |
| E6 | b3, −0.350 | tratti spessi | `stroke_width_median_px` | up |
| E7 | b3, −0.350 | colori piatti | `color_n_effective` | down |
| E8 | b3, +0.350 | colori più accesi | `colorfulness_hs` | up |
| E9 | b6, −0.350 | più grigio | mean saturation from `retro_texture_axes.measure()` | down |
| E10 | b6, −0.350 | più giallino | saturation-weighted mean hue, circular distance to **55°** | closer to 55° than baseline |
| E11 | b6, +0.350 | colori che si saturano | mean saturation, `measure()` | up |
| E12 | b2 | somiglianze fra il più positivo e il più negativo | cos(Δ₊, Δ₋) in 23-feature z space, per cell | **> 0** (same direction) |
| E13 | clear vs unclear | b1, b3, b6 described as two opposite poles; b2, b4 "non chiaro" | seed-mean cos(Δ₊, Δ₋) at ±0.350 per slice, both prompts | the three "clear" slices **more negative** than the two "unclear" ones |

## Not scored — no honest single measure

"effetto coriandoli" (b1 −), "figure più stilizzate / forme umane meno realistiche" (b1 −),
"anatomia più dettagliata e realistica" (b1 +), "estetica più vintage" (b3 −), "trasparenza del vetro
degli occhiali, pose più dinamiche, facce più rugose" (b3 +). These are recorded, and they are the
part of his reading no statistic in this project can currently check.
