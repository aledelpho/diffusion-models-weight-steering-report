# C105 result — a fixed edit carries "something similar" across subjects, in both domains; not "the same"

2026-10-20. Pre-registration `docs/prereg_te_domain_transfer.md` (1a77ff4; amendment 1 before the blind pass: match
0.10–0.45 and units of ≥ 3 subjects; amendment 2 during the blind pass, at Alessandro's request: a fourth answer
*qualcosa di simile*, scored 0.5). Calibration and renders by Antigravity (`docs/RENDERS_2026-10-20_te_domain_transfer.md`):
29 of 32 pairs reached (unreachable O4 × R09, G5 × E14, P2 × E14), hard gates 6 of 6 and reported gates 6 of 6
pixel-identical. Labels committed as downloaded (394ecfd; 42 units). Rules: `experiments/te_domain_transfer.py --rules`
→ `data/te_domain_transfer_tests.csv`.

## Verdicts (content primary)

| | within domain | mixed domains | control (different perturbations) | verdict |
|---|---|---|---|---|
| rule 1 — null | | | **0.06** (n 8) | ok: the eye rarely calls different perturbations alike |
| rule 2 — edits (E14, E26) | 0.38 (n 8) | 0.50 (n 6) | 0.06 | **transfers across domains** |
| rule 2 — random (R09, R26) | 0.56 (n 8) | 0.58 (n 6) | 0.06 | **transfers across domains** |
| style (reported) — edits | 0.19 | 0.25 | 0.00 | no transfer |
| style (reported) — random | 0.44 | 0.25 | 0.00 | partly |

Match: 28 of 29 cells within 0.10–0.45 (LN × R09 at 0.08 dropped). Test–retest: content 6 of 6, style 5 of 6.

## How strong the transfer is

The verdicts rest on *qualcosa di simile*: 23 of 36 content answers are *simile*, 3 are *stesso*, 10 *diversi*. Without
*simile* (the pre-registered binary share, reported) too few units remain to decide. So what transfers is **a partial,
recognisable kind of change, not the same change**: Alessandro's notes name it — features "exaggerated" (Z01, Z18),
"more flatness" (Z05), "highlighted" textures (Z08), "more comics" (Z23, Z29), sharper "division between elements"
(Z21) — and often with one subject out of the group (Z05, Z08, Z14, Z15, Z23, Z29, Z33). The edits pass the rule by a
small margin (within 0.38 against the null 0.06; the threshold is a gap of 0.30).

## Reading

* A fixed text-encoder perturbation — real edit or random push — gives a family resemblance across subjects, and it does
  **not** stop at the style domain: mixed groups score as high as within-domain groups. The domain specificity found on
  2026-09-25 (image-model presets) is **not** reproduced on text-encoder perturbations.
* Together with C104: per subject, a fixed perturbation changes content the same way across seeds; across subjects it
  changes it in a similar, not identical, way. An edit is a knob with a recognisable tendency, weaker than a word in the
  prompt.
* Style travels less than content; random pushes a little more than edits.

## Limits

Small groups (6–8 units); the transfer verdict depends on amendment 2's score for *simile*; two test seeds; calibration
seeds under-predicted the test-seed change (amendment 1); Alessandro had seen some of these subjects before; one
direction per perturbation.
