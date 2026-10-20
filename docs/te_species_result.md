# C107 result — under L06 it is the gender word, not the species, that decides where the style goes

2026-10-20. Pre-registration `docs/prereg_te_species.md` (aa4d5f7, before any render). Renders by Antigravity
(`docs/RENDERS_2026-10-20_te_species.md`): 40, gates 2 of 2 pixel-identical (the original plain and L06 renders).
Blind key and page committed after the renders, before any label (242eedd); Alessandro's labels committed as
downloaded (ba23ae3; 46 pictures, 6 repeats). Rules: `experiments/te_species.py --rules` → `data/te_species_tests.csv`.

## Verdicts

| rule | value | verdict |
|---|---|---|
| 0 — plain pictures Western comic | 4 of 4 for every variant | all kept |
| **1 — species** (anime elf − human, L06) | 0.38 (n 8) − 0.38 (n 8) = **+0.00** | **not the species alone** |
| **2 — gender word** (anime non-binary − female, L06) | 0.75 (n 8) − 0.00 (n 8) = **+0.75** | **the gender word decides** |
| 3 — realistic, human − elf (reported) | 0.12 − 0.00 = +0.12 | — |
| 4 — Claude's prediction: the female human ranger realistic in ≥ 3 of 4 | realistic 1 of 4 (painting 3) | **not met** |
| 5 — the traits reading (reported) | elf prompts keep the pointed ears in 7 of 8 L06 pictures and go to painting (EF 4 of 4) or anime (EN); human prompts lose no ears and go anime (HN 3 of 4) | **not supported** |
| 6 — test–retest | 5 of 6 identical (the one change: EN L06 anime → cartoon) | — |

Tally under L06: EN anime 3, cartoon 1 · EF painting 4 · HN anime 3, painting 1 · HF painting 3, realistic 1 ·
RF painting 3, realistic 1.

## What the pictures show (looked at, Claude, after the rules, conditions known; sheet `scratch/c107_sheet.jpg`, not committed)

Plain, all five variants are the same Western-comic rogue: undercut, amber eyes, smirk, hooded cowl; the elf variants
have pointed ears, the human ones do not. Under L06 every variant becomes the **same kind of person**: younger, lighter
skin, a soft face, shoulder-length dark hair, the green hood and the feather earring kept, the smirk and the undercut
gone. What separates them is the rendering: the non-binary variants get large eyes and flat cel shading (anime), the
female ones a painterly, almost photographic face. Alessandro's note says the same: several pictures come close to
realistic, but the stroke is mostly painting.

## Reading

* The species word does not decide the destination; the gender word does, on this description: "non-binary" sends
  L06's pictures to anime in 6 of 8, "female" in 0 of 8 (exploratory Fisher test on the 2 × 2, two-sided p ≈ 0.007).
* Claude's reading from the TEP2 sheet — the destination follows what survives (pointed ears kept → anime) — is **not
  supported**: the female elf keeps her ears every time and is painted; the non-binary human has no pointed ears and is
  anime. Alessandro's worry about a survival bias was justified: the reading was built on the one character that stood
  out, and on a trait that is itself an effect of the edit.
* The female variants land where this description falls back without its style words (painting, C73: 3 of 4); the
  non-binary word adds a pull toward anime. Exploratory, not tested.
* The content change is shared by all variants (who is drawn); the gender word changes how it is rendered. This
  fits C104–C106: one edit, one recognisable change, with the prompt deciding the details.

## Limits

One description, four seeds, one edit, one observer who knew both hypotheses. The boundary between "painting" and
"realistic" is soft (Alessandro's note); C73's "realistic" for the dwarf and the half-orc may sit on the same boundary.
The EN L06 picture at seed 2645751, pixel-identical to C73's, was labelled anime there and cartoon here. Whether
"non-binary" pulls toward anime on other characters, or in short prompts, is untested.
