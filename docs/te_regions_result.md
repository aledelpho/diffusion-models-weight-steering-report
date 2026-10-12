# C68 — result: how large are the regions of the prompt a text-encoder edit pushes alike? (2026-10-12)

Pre-registration `docs/prereg_te_regions.md` (all 12 taps, revised before any encode). 241 encodes, no images; gate
PASS (repeat identical; agreement with C67 within 0.000324 against a limit of 0.000977; `docs/RENDERS_2026-10-12_te_regions.md`).
Code `experiments/te_regions.py --analyze`; data `data/te_regions_size*.csv`, `te_regions_curves*.csv`,
`te_regions_size_by_tap.csv`, `te_regions_tests*.csv`. Residual = change minus its mean over the prompt (the shared
push of C67 removed).

## The answer: about three tokens

**The half-life of the residual similarity is 3 tokens** (median over the 20 edits; range 2–5). Two tokens next to
each other are pushed in related directions; four or five tokens apart the relation has halved. A clause of these
prompts is about 6 tokens, a sentence about 25, so a region is **about half a clause — a word with its neighbour,
"bold ink", "pale antlers"**, not a sentence.

**By depth** (each tap an edit reaches; `te_regions_size_by_tap.csv`):

| tap (layer) | 5 | 8 | 11 | 14 | 17 | 20 | 23 | 26 | 29 | 32 | 35 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| half-life (tokens) | 4.5* | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 3 | 3 | 4 |
| same-clause minus cross-clause | −0.02* | 0.00 | 0.02 | 0.03 | 0.04 | 0.04 | 0.04 | 0.04 | 0.04 | 0.03 | 0.01 |

\* only the L02 and L04 edits reach tap 5 (24 edit-prompts).

The regions grow a little with depth (2 → 3 → 4 tokens) and the punctuation starts to matter in the middle of the
encoder (from layer 11, strongest at 20–26), fading at the last tap.

## Tests

| test | value | rule | verdict |
|---|---|---|---|
| H1 — inside one prompt, clauses are pushed less alike than the whole prompt is across orders | 20/20 edits; clause agreement 0.54 against 0.97–0.99 | ≥ 16/20 | **supported** |
| H2 — at equal distance, tokens of one clause are pushed more alike than across clauses | 18/20 edits, sign test p = 0.0002 | ≥ 15/20, p < 0.05 | **supported** |
| H3 — the word-order dependence lives in the clause residuals | ρ = −0.37 (p 0.11); sentence −0.42, word −0.40 | ρ ≥ 0.50 | **not supported** (sign opposite) |
| H4a — frame residual agreement across characters vs "same direction" | ρ = 0.12 | ρ ≥ 0.40 | not supported |
| H4b — exceptions from the frame residual | AUC 0.53 | ≥ 0.70 | not supported |

The last-three-taps comparison gives the same picture (H1 20/20, H2 18/20, H3 ρ −0.38, H4b AUC 0.58).

## Reading

1. **The regions are real and small.** Beyond the shared push, each edit pushes small groups of 2–4 tokens in their
   own directions, with boundaries that follow the commas — the encoder's own segmentation of the prompt.
2. **But they do not carry Alessandro's divergence.** The regional pattern is as stable across word orders as the
   shared push was (C67), and the edits the eye rated most order-dependent have, if anything, the *more* consistent
   regional pattern (H3 negative, as E2 was). Nor do the frame residuals pick out the characters that break the
   common direction (H4).
3. **Where that leaves the question.** Three measurements of the text encoder's output — size (C67 E1, which works),
   direction of the whole (C67 amendment 2), direction by region (C68) — say the same thing: the encoder gives the DiT
   a push that depends on the edit, not on the prompt. The genre the picture ends in depends on the prompt. The
   divergence is made **in the DiT**, from where the unedited conditioning puts it. The negative signs of E2 and H3
   are consistent with a strength effect: the strongest edits push the most stereotyped pattern and also move the
   picture furthest, where small differences of starting point decide the genre.

## Limits

One observer's labels; 20 edits; punctuation-based units. The half-life is a property of the residual after
removing the prompt mean, so a region effect spread over the whole prompt is, by construction, not counted.

## Next (not decided)

Look where the push is turned into a picture: the DiT's attention from image regions to these 2–4-token groups, with
and without the edit, on two word orders that the eye saw diverge — the "watershed" read at the level where it
happens.
