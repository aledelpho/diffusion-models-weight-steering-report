# C55 result — the active tuner is clean

2026-10-06. Pre-registration `docs/prereg_null_patch.md`; renders `docs/RENDERS_2026-10-06_null_patch.md`
(Antigravity), re-checked by Claude on the files.

| render | tuner | layers patched (log) | against the C47 baseline |
|---|---|---|---|
| N0 baseline, same session | none | — | max diff 0 (REPRO PASS) |
| **N1 null patch** — block 27 matrices ×1.0001 | active | 8 | **max diff 0 — CLEAN** |
| N2 block 27 +0.0001 (float32 scales change by 1e-4) | active | 13 | max diff 0 |
| N3 block 27 +0.004 (every bf16 weight one step) | active | 13 | 86.9% of pixels differ, mean 2.26/255, max 158 |
| N4 block 27 −0.004 | active | 13 | 88.1% of pixels differ, mean 2.12/255, max 157 |

**Verdict (decisive rule):** the active node adds nothing beyond the multiplication. Differences
between conditions in this report are the change of the weights, not the node.

**Descriptive.** A 1e-4 change of the float32 norm scales and modulation of one block does not reach
the pixels. *Corrected 2026-10-06:* not because of precision — these parameters never reach the model
at any dose (notebook page 13; a ×3 on block 23's norm scales is also pixel-identical,
`docs/inside_block23_exploration.md`). The smallest change the bf16
matrices can take — one rounding step on every weight of one block — redraws the image slightly
almost everywhere. **The hood (C54 labels), Alessandro, blind to which image was which:** *a metà* on all five
(`data/null_patch_hood_labels_alessandro.csv`; given in chat as one answer for the five, not through
the page export). One bf16 step on every weight of block 27, in either direction, redraws 87-88% of
the pixels and does **not** tip the hood. In C54 the smallest edits were blk27 +0.05 (still half)
and blk27 −0.075 (complete): the watershed needs more than the minimum displacement, somewhere
between one rounding step and a few percent.
