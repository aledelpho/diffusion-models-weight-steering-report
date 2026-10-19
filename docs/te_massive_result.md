# TEP2 result — L06's damage does not go through the massive activations

2026-10-19. Pre-registration `docs/prereg_te_massive.md` (8969b75; amendment 1, gate (c) as a 5% tolerance, approved
2026-10-18 before any main render or distance). Encodes and 25 renders by Antigravity
(`docs/RENDERS_2026-10-18_te_massive.md`); gates: plain render pixel-identical (max abs diff 0); the six file-route C1
renders within the tolerance (relative difference of distance to the plain render 0.000–0.039; the elf at 2645751 is
the largest, mean pixel difference 8.5 of 255). Rules by Claude: `experiments/te_massive.py --rules` →
`data/te_massive_tests.csv`; distances `data/te_massive_metrics.csv` (DINOv2-large, to the same-seed plain render).

## Verdict

| rule | value | verdict |
|---|---|---|
| 1 — the massive entries carry the damage | f(C2) ≤ 0.50 in **0 of 6** | not met |
| 2 — not through the massive entries | f(C2) ≥ 0.80 in **5 of 6**; f(C4) ≥ 0.80 in 5 of 6; median f(C3) **0.04** | **not through the massive entries** |

Per cell f = D(X) / D(C1): dwarf 2645751 C2 1.00, C3 0.03, C4 1.00; dwarf 3316624 0.96, 0.02, 0.97; elf 2645751 0.69,
0.05, 0.61; elf 3316624 1.41, 0.12, 0.96; half-orc 2645751 0.98, 0.08, 0.98; half-orc 3316624 1.00, 0.04, 1.09.

## What the renders show (looked at, Claude, conditions known; sheet `Text2Img/_te_shapes/TEP2_sheet.jpg`)

Restoring the 36 massive entries (C2) leaves the L06 damage in place: the comic dwarf stays a realistic photo of a woman
in a dark shirt, the half-orc stays a realistic young woman, the elf stays a pale anime girl. The massive change alone
(C3) gives back the plain picture almost unchanged. The random control (C4) looks like C1. The one cell below 0.80 is
the elf at 2645751, where the control also drops (0.61): that cell moves whenever anything is restored, and it is also
the cell where the file-route C1 differs most from the in-graph render (amendment 1).

Encoder side (reported, `data/te_massive_encoder.csv`): the 36 massive entries sit on one token; restoring them keeps
about 100% of the push length and a cosine of 0.97 with the full push; the massive change alone reproduces 0–6%.

## Reading

L06's destructiveness is not carried by the massive activations, so "leave the layers that create massive activations
alone" is not the rule behind it. The damage is in the ordinary entries of the stream after layer 6, spread over the
tokens. "Avoid early MLPs" stays an empirical map (tool rule, rule 2).

## Limits

One edit, three characters, two seeds. The mask restores the entries at the output of layer 6 only; later layers can
re-create large values. Amendment 1: the file-route conditioning is not bit-identical to the in-graph one (a ComfyUI
update between the two is a likely cause, not verified).
