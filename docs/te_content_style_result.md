# C104 result — each fixed random push changes the content its own way; the embeddings do not see it

2026-10-19. Pre-registration `docs/prereg_te_content_style.md` (e5a5765). No new renders (C103's). Labels committed as
downloaded (dbe1a47; 55 units, two questions); CSD vectors by Antigravity committed before the rules. Rules by Claude:
`experiments/te_content_style.py --rules` → `data/te_content_style_tests.csv`.

## Verdicts

| rule | layer 9 | layer 26 |
|---|---|---|
| 1 — content is the network's (blind B content ≥ 0.60 and DINOv2 r ≥ 0.50) | blind **0.00** (n 9); DINOv2 r 1.61 → **disagreement** | blind **0.25** (n 12); r 0.87 → **disagreement** |
| 2 — style is the perturbation's own (blind B style ≤ 0.30 and CSD r ≤ 0.25) | blind 0.56; CSD r 0.75 → **not supported** | blind 0.25; CSD r 0.84 → **disagreement** |
| 3 — content from the network, rendering from the perturbation | **not supported** | **not supported** |
| 4 — A units, random pushes, same change across seeds (reported) | content **1.00** (n 5), style 0.67 (n 6) | content **0.92** (n 12), style 0.50 (n 12) |

Test–retest 6 of 6 on both questions; *non si vede* 2 (content), 0 (style). Edits (A units): content 1.00 at both layers.

## Reading

**Claude's reading of C103 is rejected.** By eye, three different random pushes at the same layer do **not** change the
content the same way (0.00 and 0.25), while one fixed random push changes the content the same way across seeds (1.00 and
0.92). That is Alessandro's hypothesis in its strong form — *every fixed perturbation, random or not, has a content
direction of its own, consistent across seeds and different from the others* — supported by the eye at both layers.

**The embedding measures disagree with the eye, and an exploratory check says they cannot be trusted for this
question.** Per unit, the mean cosine between change vectors (κ for A units, ρ for B units) against Alessandro's answer
(*stesso* against *diversi*): DINOv2 for content AUC **0.64** (n 28 and 19), CSD for style AUC **0.36** (below chance).
The cosine between DINOv2 or CSD change vectors does not track "the same change" as the eye sees it; it likely carries a
component shared by any change (more realistic, more detailed), which makes different perturbations look alike. C102's
and C103's computed rules rested on that measure, so their computed halves are withdrawn as evidence of shared
direction; the blind halves stand.

## What follows

* Random edits are legitimate knobs: each one, once fixed, produces its own change, reproducible across seeds.
* Depth (L09 against L26) did not change this answer.
* For "same change" questions, the measure is the eye; a computed proxy needs validating against it first.

## Limits

21 B units; Alessandro had seen the pictures in C103 (the result went against the hypothesis that was put to him);
three random directions per layer; R09a under-matched; the AUC check is exploratory, computed after the rules.
