# C79 — 12-tap isolation: interim result (renders, gates, encoder audit, first look)

2026-10-17. Pre-registration `docs/prereg_te_tap_isolation.md` (written by Argon; file time 10:29, first C79 render
11:26; the file was not committed before the renders, so its precedence rests on file times only). Script
`experiments/te_tap_isolation.py`. Renders `Text2Img\benchmark_te_tap_isolation`, 76 of 76 present.

**What is decided and what is not.** The pre-registered **primary rule is on blind human trait labels** (section C:
trait retention and skin, 108 items). No label exists yet, so **H1 / H2 / joint is not decided**. The automatic
distances of `--analyze` (DINOv2, CSD, VQAScore) only feed the concordance rule (rule 3) and need the GPU (they were
not run: the Linux shell has no torch).

## Gates (checked again by Claude, 2026-10-17)

| gate | reference | max abs diff |
|---|---|---|
| `gate_zero` | `benchmark_portraits/phase_c` D1 baseline, seed 2645751 | 0 |
| `gate_real` (L06) | `benchmark_te_characters` D1 `L06_mlp_p1.00` | 0 |
| `gate_all12` (L06, all 12 taps through the new `taps` path) | same | 0 |
| `gate_late_L28` (L28 restricted to taps 9–11) | `benchmark_te_characters` D1 `L28_mlp_p1.00` | 0 |

The tap-restricted push reproduces the full edit exactly when all 12 taps are kept, and L28's push is entirely in
taps 9–11. The partition `early_mid + late = full` holds by construction.

## Encoder audit (`data/te_tap_isolation_encoder_summary.csv`, `..._by_tap.csv`, `..._txtfusion_weights.csv`)

| edit | share of push energy, taps 0–8 | taps 9–11 | mean relative push, taps reached in 0–8 | taps 9–11 |
|---|---|---|---|---|
| L06 MLP ×2 | 0.24–0.25 | 0.75–0.76 | 1.15–1.18 | 0.46–0.49 |
| L14 MLP ×2 | 0.22–0.23 | 0.77–0.78 | 0.77–0.80 | 0.42–0.43 |
| L28 MLP ×2 | 0 | 1.00 | — | 1.15–1.17 |

(ranges over the three characters.) In absolute energy L06 and L14 push mostly the late taps, because late taps
are large; relative to each tap's own size they push the early/mid taps harder. `txtfusion.projector.weight` is a
1×12 mix: |w| on taps 0–8 is 73.8 % of the total, with the largest single weight on tap 7 (L23, −1.44) and a small
one on tap 11 (L35, +0.11). The projector acts after `txtfusion`'s own layers, so its weights alone do not say how
much each tap matters.

## First look at the 72 renders (Claude, by eye, conditions known — not a test)

Sheets: `Text2Img\_post_cards\_view\c79\L{06,14}_{D1,E2,O4}.jpg` (columns: baseline, full edit at the two seeds where
it exists, taps_local, taps_early_mid, taps_late; rows: the 4 seeds).

* **`taps_local` does almost nothing**: in all 24 cells the picture is the baseline with small differences. The two
  taps right after the edited layer are not enough.
* **Neither half reproduces the full edit.** L06 in full turns the dwarf and the half-orc into photographs and the
  elf into anime; no half-tap picture becomes a photograph. L14 in full turns the dwarf into a dark-haired man and
  the half-orc into a light-skinned human; the halves stay close to the original character.
* **Both halves change the character, in different ways.**
  * L06 `early_mid`: the dwarf grows a full red beard at two seeds (the model's own "dwarf" prior, as in C72) and
    loses her armour at the other two; the elf gains a hood; the half-orc becomes a human woman. Style stays comic.
  * L06 `late`: the dwarf's steel gorget turns brass at all four seeds; the elf's skin is lighter; the half-orc
    becomes a lighter, painted, half-realistic woman, the only drift toward the full edit's realism.
  * L14 `early_mid` and `late`: small changes (braids, a hood on the elf in `late`, tusks appearing on the half-orc
    in `late`).
* If labels confirm this, the reading would be the pre-registered **joint / super-additive** case: the effect needs
  both groups of taps together.

## To do

1. `--analyze` on the Windows GPU (directive below) — concordance rule 3 and the metric file.
2. The blind labelling of section C (108 items, C75 questions), which decides the primary rule.
