# C73 result — each character has its own fallback, but the edits do not lead there

Pre-registration: `docs/prereg_te_fallback.md`. Renders: `docs/RENDERS_2026-10-13_te_fallback.md`; the gate was
pixel-identical and all 29 of 29 renders exist. Labels by Alessandro, committed as downloaded before any count:
`data/te_fallback_genre_alessandro.csv`.

Tally (committed before the labels): `experiments/te_fallback_tally.py`. Outputs:

* `data/te_fallback_tests.csv`;
* `data/te_fallback_by_char.csv`;
* `data/te_fallback_by_edit.csv` (descriptive, added after the tests).

## Labels

* **With the style clause:** all 28 with-style portraits were labelled Western comic.
* **Unlabelled pictures:** the two gnome pictures under L12 MLP doubled have no genre. The note reads "rendering 3D"
  for both, but the pre-registration counts only the genre field, so they are left out.
* **Free notes:** "rendering 3D" also appears in the notes of four pictures labelled "altro" or "realist".

## Tests

| test | value | verdict |
|---|---|---|
| H1 — distinct fallbacks among the characters that have one | elf rogue, dragonborn and tiefling → painting; half-orc → realistic; dwarf, gnome, halfling mixed (painting / realistic, two "3D") | **supported**: the fallback depends on the character |
| H2 — switched edited pictures land on the character's own fallback | 0.28 against 0.27 expected if destinations ignored the character (43 switched pictures of the four characters with a clear fallback) | **not supported** |

## Reported

* **Anime is no portrait's fallback.** Without "Western comics style", 1 of 28 portrait pictures is anime (the elf
  rogue, one seed). The elf brawler of C72 fell back to anime in 9 of 9. So the anime fallback belongs to that
  prompt, which carries anime-leaning phrases of its own (C72 block B), not to the model.
* **Destinations depend on the edit, across characters** (14 pictures per edit, `data/te_fallback_by_edit.csv`;
  described, not tested):
  * L06 MLP doubled → realistic in 11 of 14, and anime in the other 3, all of them on elves;
  * L14 → cartoon in 9 of 14;
  * L26 and L28 → still Western comic in 14 of 14;
  * L02 → still comic in 11 of 14;
  * L05 splits between anime, realistic and painting.

  L28 kept the comic on the elf brawler too (C72), so its "protection" now holds on eight characters.
* **Elves go anime.** The elf rogue switches to anime in 10 of its 12 switched pictures, although its own fallback
  is painting. The elf brawler also went anime under most edits (C70). The word "elf" itself was anime or painting
  alone (C72 block B).

## Reading

1. **There is no single fallback.** Remove the style words and each character drifts to its own genre — mostly
   painting or a realistic render — and the elf brawler to anime. The C72 result stands, but as a statement about
   that prompt.
2. **The edits do not reveal the character's fallback.** Where an edited picture lands is not where the same
   character goes without style words.
3. **Each edit has a destination of its own, modulated by the character.** L06 tends to realism, L14 to cartoon,
   L28 keeps the comic. Elves bend several edits toward anime. Edit and character together decide.

## Limits

* **The labels.**
  * One labeller, not blind, with coarse categories.
  * Alessandro notes that each label hides very different sub-styles: two pictures labelled "Western comic" can
    look nothing alike. "No switch" therefore does not mean "same style".
* **The doses.** All edits are at ±1, a layer half zeroed or doubled. At this strength part of what is labelled
  "genre" may be a loss of stylistic coherence rather than a move to another style.
* **The material.** Four seeds for the fallback, two for the edits; H2 compares switches with their own base rates.
* **The no-style prompts** keep "close-up portrait, frontal view", and the characters' own words.
