# C79 — 12-tap isolation: result

2026-10-18. Pre-registration `docs/prereg_te_tap_isolation.md` (written by Argon; file time 10:29, first C79 render
11:26; not committed before the renders, so its precedence rests on file times only; amendment 1 by Claude before any
label). Scripts `experiments/te_tap_isolation.py`, `te_tap_isolation_page.py`, `te_tap_isolation_tally.py`
(committed with a passing selftest before it was run on the labels). Renders `Text2Img\benchmark_te_tap_isolation`,
76 of 76. Labels `data/te_tap_alessandro.csv` (Alessandro, blind, 1715 answers, committed as downloaded before any
count). Outputs `data/te_tap_tests.csv`, `data/te_tap_by_picture.csv`, `data/te_tap_isolation_metrics.csv`,
`data/te_tap_isolation_cells.csv`; `--analyze` log `docs/RENDERS_2026-10-17_te_tap_isolation.md`.

## Verdicts

| rule | value | verdict |
|---|---|---|
| **1 (primary)**: trait loss, early/mid taps vs late taps | ΔR early_mid **0.212**, ΔR late **0.066**, difference **+0.146** (threshold +0.15); early_mid loses more in **5/6** (character, edit) pairs | **inconclusive**: the direction of H2 holds in 5/6 pairs, the size misses the threshold by 0.004. No other branch is met (late < 0.10, early_mid ≥ 0.15) |
| 2: local sufficiency, L06 (taps 2–3) | ΔR local 0.014 / early_mid 0.296 = **0.05** | **needs accumulation across intermediate taps** (≤ 0.30) |
| 2: local sufficiency, L14 (tap 5 only, amendment 1) | ΔR local 0.000 / early_mid 0.128 = **0.00** | **needs accumulation across intermediate taps** |
| 3: DINOv2, Δ early−late > 0 | 15/24 cells | no unidirectional verdict (needs ≥ 18/24) |
| 3: CSD, Δ early−late < 0 | **21/24** cells | **late taps farther from the baseline** in CSD: opposite in sign to the eye's trait verdict |
| reliability gate (C75, κ ≥ 0.60) | κ **1.00** on 164 repeated trait answers (164/164 equal); skin 11/12, person 11/12 | passed |

So the pre-registered H1/H2 question is **not decided**. What the data do show:

* **Neither half reproduces the full edit, and the two halves together fall short of it** (same two seeds, where the
  full edit exists):

  | edit | ΔR local | ΔR early_mid | ΔR late | early_mid + late | ΔR full |
  |---|---|---|---|---|---|
  | L06 MLP ×2 | 0.01 | 0.31 | 0.07 | 0.37 | **0.46** |
  | L14 MLP ×2 | 0.00 | 0.12 | 0.03 | 0.16 | **0.38** |

  For L14 the two halves add up to about 40 % of the full edit's loss; for L06 to about 80 %. The full edit is
  larger than the sum of its parts: the halves interact inside `txtfusion` (the tap-attention layers mix all 12 taps
  before the projector). This is a description; the pre-registered rule for a super-additive case ("neither half
  ≥ 0.15") does not apply because L06's early_mid half alone reaches 0.30.
* **Skin and identity behave the same way.** L14 lightens the skin in 4 of 6 full-edit pictures and makes a
  different person in 6 of 6, but in **0 of 24** half-tap pictures does either happen. L06 early_mid lightens the
  skin in 6/12 and changes the person in 6/12; L06 late in 4/12 (plus 1 darker) and 1/12; L06 local in 0/12.
* **The two automatic measures split along content and style (reading, not tested).** For L06, early_mid moves the
  picture most in DINOv2 (mean distance to baseline 0.35 against late 0.14) and in VQAScore trait loss (0.094
  against 0.011); late moves it most in CSD (0.19 against 0.15), and CLIP's top genre label becomes "oil" in 7 of 12
  late pictures and in none of the early_mid ones. In C66 DINOv2 and VQAScore were validated for change and trait
  loss, CSD for word-order dispersion only, CLIP genre not at all; so this split is a lead, not a result.
* **Traits lost most often in the two halves**: `o_orc` 9, `d_gorget` 8, `o_knot` 8, `e_cheeks` 7, `d_braids` 7,
  `e_undercut` 7 (counts over 48 half-tap pictures).
* **Per pair** (ΔR early_mid / late): D1·L06 0.43 / 0.09, D1·L14 0.23 / 0.07, E2·L06 0.25 / 0.04, **E2·L14 0.05 /
  0.07** (the one pair against H2), O4·L06 0.21 / 0.10, O4·L14 0.10 / 0.03.
* The full edits, labelled again here, retain R = 0.54 (L06) and 0.62 (L14) of their baseline traits; C75 reported
  0.48 and 0.63 on the same renders with a different set of pictures around them.

## What this changes in the text-encoder story

* **"L28 is harmless because it reaches only the late taps" is not enough.** The late half of L06/L14 also does
  little (ΔR 0.07 and 0.03), so the late taps are not where these edits do their damage. That agrees with H2's
  direction, but the threshold was not met and the early/mid half alone does not reproduce the full edit either.
* **The damage needs many taps at once.** The taps right after the edited layer do nothing measurable (ΔR ≤ 0.01).
* The 1×12 projector weights (73.8 % of |w| on taps 0–8) are consistent with the early/mid direction but, as said in
  the encoder audit, they act after `txtfusion`'s own layers and do not measure tap importance by themselves.

## Gates (checked again by Claude, 2026-10-17)

| gate | reference | max abs diff |
|---|---|---|
| `gate_zero` | `benchmark_portraits/phase_c` D1 baseline, seed 2645751 | 0 |
| `gate_real` (L06) | `benchmark_te_characters` D1 `L06_mlp_p1.00` | 0 |
| `gate_all12` (L06, all 12 taps through the new `taps` path) | same | 0 |
| `gate_late_L28` (L28 restricted to taps 9–11) | `benchmark_te_characters` D1 `L28_mlp_p1.00` | 0 |

## Encoder audit (`data/te_tap_isolation_encoder_summary.csv`, `..._by_tap.csv`, `..._txtfusion_weights.csv`)

| edit | share of push energy, taps 0–8 | taps 9–11 | mean relative push, taps reached in 0–8 | taps 9–11 |
|---|---|---|---|---|
| L06 MLP ×2 | 0.24–0.25 | 0.75–0.76 | 1.15–1.18 | 0.46–0.49 |
| L14 MLP ×2 | 0.22–0.23 | 0.77–0.78 | 0.77–0.80 | 0.42–0.43 |
| L28 MLP ×2 | 0 | 1.00 | — | 1.15–1.17 |

(ranges over the three characters.) In absolute energy L06 and L14 push mostly the late taps; relative to each tap's
own size they push the early/mid taps harder.

## Limits

* One labeller (Alessandro), who had seen the C79 sheets with conditions known before labelling; κ = 1.00 on repeats
  measures consistency, not independence.
* Three characters, four seeds; the full edit exists on two seeds only.
* Retention R depends on the C75 trait list (10–14 traits per character present in the baselines).
* The pre-registration was not committed before the renders (see the header).
