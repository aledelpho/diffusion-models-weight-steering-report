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
the pixels (likely below the precision at which they are used). The smallest change the bf16
matrices can take — one rounding step on every weight of one block — redraws the image slightly
almost everywhere. The hood at this seed (C54): pending Alessandro's blind labels
(`hood_test.html`, key `data/null_patch_page_key.csv`).
