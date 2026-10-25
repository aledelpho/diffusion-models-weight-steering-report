# MOSS2 result — the MOSS bench: reproducible and clean; light doses barely move MOSS; the turbo confirms 4 of 6 edits

2026-10-25. Pre-registration `docs/prereg_moss_bench.md` (amendments 1-3). Renders by Antigravity
(`docs/RENDERS_2026-10-25_moss_bench.md`): 84 + 6. Setting T10 (DMD2 LoRA, euler, 10 steps, CFG 1, about 22 s);
confirmations at R50 (euler, 50 steps, CFG 3, about 166 s). Values: `data/moss_bench_tests.csv`,
`data/moss_bench_metrics.csv`; confirmation key and labels `data/moss_confirm2_key.csv`, `data/moss_confirm2_labels.csv`.

## Verification

| check | value | verdict |
|---|---|---|
| V1 the dwarf rendered twice, no cache | max pixel difference 0 | **PASS** |
| V2 DiT layer 41 x 1.0001 (dwarf, rally) | max 0, max 0 | **PASS** |
| V2r TE layer 31 MLP x 1.0001 (reported) | 76 % and 96 % of pixels change, DINOv2 0.002 and 0.010 | — |

## Seed floor (T10, median DINOv2 distance between four seeds)

Lotus canoe 0.056, comic page 0.075, dwarf 0.098, leaf 0.155, still life 0.249, rally 0.335: the floor depends strongly
on the prompt, so every MOSS threshold must be set per prompt.

## Dose ladder (T10, distance to the plain picture, dwarf / rally)

At d = 0.10 and 0.30 almost every edit stays below 0.04, under every floor but the canoe's. At d = 1 and 2 effects are
clear: DiT layer 20 on the rally 0.23 at d = 1; TE layer 27 0.12 / 0.16 at d = 2; DiT layer 35 on the dwarf 0.38 at d = 2.
Deep DiT blocks and TE layer 27 act most.

## Confirmation at R50 (blind, amendment 3: d = 2; rule fixed before the labels)

Matched cards 0.50 (n 6), control cards 0.17 (n 6): **not confirmed** as a whole (bar 0.67). Per edit: DiT 6 (similar),
DiT 35 (same), TE 6 (similar), TE 27 (same) **confirmed**; DiT 20 and TE 15 (different) **not**. The controls show the
eye separates different edits (0.17). Repeats 2 of 3 identical (DiT 6 changed from similar to different).

## Reading

* The pipeline is sound: deterministic, and the tuner adds nothing at null doses.
* MOSS is little sensitive per layer: Alessandro's ±0.10 per layer is invisible on MOSS; working doses are around 1-2
  per layer, or several layers together.
* The turbo reproduces the kind of change of the reference for 4 of 6 edits, not for all: turbo results are working
  results, and each must be confirmed at R50 before it is reported as a property of MOSS. DiT 20 and TE 15 are the
  first cases where turbo and reference diverge.

## Limits

One prompt for the confirmations, one seed, one observer who knew the setup; at d = 1 the change was too small to judge
(amendment 3).
