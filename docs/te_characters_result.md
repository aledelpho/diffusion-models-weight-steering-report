# C65 — result: text-encoder edits on seven characters, five word orders and one watercolour (2026-10-12)

Pre-registration `docs/prereg_te_characters.md` (+ amendments 1–2, eye page only). Renders 531/531, both
reproductions and the seven layer-35 nulls at max abs diff 0 (`docs/RENDERS_2026-10-11_te_characters.md`). Eye
pass committed before the measures (`docs/te_characters_eye_result.md`). Measures by Antigravity
(`data/te_characters_style_features.csv`, `te_order_style_features.csv`, `te_characters_faces.csv`); rules run by
`experiments/te_characters.py --test` → `data/te_characters_tests.csv`, `te_order_tests.csv`,
`te_watercolor_tests.csv`, `te_characters_predictions.csv`.

## Verdicts

| test | rule | value | verdict |
|---|---|---|---|
| H1 — the same edit moves different comic characters the same way | coherent (S ≥ 0.50, W ≥ 0.40) in ≥ 14 of 20 | 4 coherent, 7 incoherent, 2 unclear, 7 uninformative (13 informative) | **refuted** |
| H2 — word order disturbs a text-encoder edit more than a DiT edit | median d (TE) ≤ median d (DiT) − 0.10 and MWU p < 0.05 | d = cos_order − cos_seed: −0.05 (16 edits) vs +0.03 (43 DiT arms), p = 0.002 | **inconclusive** (direction as predicted, size 0.08 < 0.10) |
| H3 — the style family changes an edit more than the character does | median across style ≤ across character − 0.10, Wilcoxon p < 0.05 | 0.21 vs 0.19, p = 0.80 | **refuted** |
| P1 — as coherent as the DiT preset (W 0.41–0.61) | | median W 0.21 (C52: 0.51) | fails |
| P2 — less quality loss than the DiT preset | ΔBRISQUE lower and ΔCLIP-IQA higher | BRISQUE −1.52 vs +8.09; CLIP-IQA −0.001 vs −0.037 | **holds** |
| P3 — a wider spread of styles than the DiT blocks | participation ratio larger | 4.11 vs 3.49 (DiT top-20 by size) | holds (comparison favours the selected edits) |

## Reading

1. **No common direction, in the measure.** Only four edits move the seven characters the same way in the 23
   style statistics: L04 MLP−, L06 MLP+, L12 MLP+, L14 MLP+ (W 0.48–0.63). Seven edits disagree with themselves
   across the two seeds (S < 0.50) — almost all the mild ones: L08 MLP−, L09 attn+, L10 MLP−, L15 attn+, L19 attn−,
   L26 MLP+, L28 MLP+. Single text-encoder edits are not, in general, a style knob that transfers from character to
   character the way the C52 DiT preset did.
2. **The eye and the measure disagree, in a specific way.** The eye called the mild edits coherent (L10 MLP−,
   L14 attn+, L15 attn+, L19 attn−) and two of the strong MLP+ edits incoherent (L12, L14). The measure calls
   those mild edits uninformative or unclear (their change is small and not stable across seeds) and L12 / L14
   MLP+ coherent. The likely reading: the strong MLP+ edits push every picture the same way in colour, contrast
   and edge statistics while the *genre* each character lands in differs (oil, 3D, anime, photo) — the 23
   statistics see the first, the eye judges the second. The mild edits change details the eye can name (scars,
   tusks, smoke, ram horns) that the statistics do not register. This was listed as a known limit; it is now
   observed.
3. **Identity is lost almost always.** For 19 of 20 edits, at most 2 of the eligible characters keep ArcFace
   similarity above their seed-to-seed level; L19 attn− keeps 4 of 6. At dose ±1.00 these edits change who is drawn.
4. **Word order (H2).** On the elf, the same edit agrees with itself across word orders less than across seeds
   (median d −0.05), the DiT does the opposite (+0.03), and the difference is significant (p = 0.002) but smaller
   than the 0.10 fixed in advance. Median cos_order 0.50 against the DiT's 0.69. Alessandro's prediction points
   the right way; the pre-set size was not reached.
5. **Watercolour (H3).** The watercolour D1 is moved by an edit about as much as the comic D1 (median size 0.57 vs
   0.56; smaller in 12 of 20), and the direction agrees with the comic D1 about as well as another comic character
   does (0.21 vs 0.19). The style family does not, in this test, change what an edit does more than the character
   does — but both agreements are low, so "the character changes it a lot" and "the family changes it a lot" are
   both true.
6. **Quality (P2).** The measured surface cost is nil on average (BRISQUE slightly better than the baselines, CLIP-IQA
   unchanged), against a clear cost for the C52 DiT preset — the clearest difference between the two levers, and
   the one the eye also reported.

## Limits

One comic frame, two seeds, one observer; dose ±1.00 only; the 20 edits were selected on one picture where they
changed style (regression to the mean expected, and P3 favours them). H2 rests on one prompt, and its DiT reference
is single blocks at their own doses. H3 rests on one character. ArcFace is trained on photographs.

## What this changes

* The C64 phase-1 impression "the text encoder changes style cleanly" holds for **cleanliness** (P2) and for
  **range** (P3, with its caveat), not for **transfer**: a single edit at ±1.00 does not give different characters
  the same look (H1 refuted).
* Candidates, not decided: lower doses (±0.35) for the four coherent edits, to see whether coherence and identity
  improve together; a second observer on the eye sheets; combinations of mild edits.
