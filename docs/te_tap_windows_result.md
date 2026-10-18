# C87 result — how many taps, and which: tap windows and single taps of the L06 edit

2026-10-18. Pre-registration `docs/prereg_te_tap_windows.md` (975e537, before any render). Renders by Antigravity
(`docs/RENDERS_2026-10-18_te_tap_windows.md`): 156 of 156; the 18 gate renders identical to C79 (max abs diff 0,
re-checked by Claude); rule 4 passed. Rules 1–3 computed on DINOv2 and committed sealed (3b04151) before the blind
control was counted. Blind control: Alessandro, 36 sampled renders + 6 baselines, labels committed as downloaded
(6f95ee8). Scripts `experiments/te_tap_windows.py`, `te_tap_windows_page.py`, `te_tap_windows_tally.py`.

## Blind control (decides whether DINOv2 may decide)

Spearman between the DINOv2 distance to the baseline and the eye's trait loss on the 36 sampled renders: **+0.878**
(bar 0.50). **Passed**: the DINOv2 verdicts stand. Repeats: 94 pairs, 94 equal (kappa 1.00).

## Verdicts

f(X) = DINOv2 distance of the picture with the push on taps X, divided by that of the full edit, per character and
seed (6 cells).

| rule | value | verdict |
|---|---|---|
| 1 — step or slope (taps added from 2 upward) | one increment ≥ 0.40 in **5 of 6** cells, but at **different taps** (8, 4, 9, 10, 10; the same tap in at most 2) | **mixed** |
| 2 — a hub tap | mean single-tap share: t3 0.08, t4 0.21, t5 0.13, **t6 0.11**, **t7 0.23**, t8 0.13, t9 0.12, t10 0.22; no tap ≥ 0.30 | **no hub** |
| 3 — complementary windows (reported) | F(2..k−1) + B(k..11) between 0.93 and 1.27 | not read (distances are not additive; the sample has no complementary pairs) |

* **The damage jumps, but where it jumps depends on the picture.** In five cells one added tap carries 0.48–0.96 of the
  full-edit change, but it is tap 8 for the dwarf at one seed (no jump at the other), tap 4 and tap 9 for the elf at
  her two seeds, tap 10 for the half-orc at both. There is no single threshold tap.
* **No hub, and the community hub is not replicated.** Neither tap 7 (largest projector weight) nor tap 6 (L20, the
  "hub" of the krea-explorations probes) carries a large share alone.
* **Characters differ.** The elf rogue is fragile: single taps alone move her 0.3–0.65 of the full edit, and the
  window 2–4 already 0.92 at one seed. The dwarf and the half-orc barely move with any single tap (0.03–0.15) and need
  most of the taps together. Alessandro's note while labelling — "some outputs looked really very similar" — is this:
  for the dwarf and the half-orc most single-tap pictures are nearly the original.
* **Adding the last tap can reduce the change.** The window 2–10 exceeds the full edit (mean 1.17); tap 11 partly
  pulls the picture back.

## Reading

The L06 damage is built across many taps, with no tap that carries it alone; it often appears as a jump when one more
tap is added, but the tap that tips it changes with the character and the seed. That is the behaviour of a picture
crossing a boundary at a point that depends on where it starts — the watershed picture of C95–C97 — more than of a
fixed mechanism in one tap. For the tool: no single tap is a knob; the rule "do not edit the text encoder for style"
holds unless a per-prompt calibration is accepted.

## Limits

One edit (L06), three characters, two seeds; DINOv2 measures change, validated here against the eye on 36 pictures;
one labeller.
