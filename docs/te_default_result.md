# C72 result — the model's own defaults, words alone, and random pushes

Pre-registration: `docs/prereg_te_default.md` (+ amendments 1-2). Labels by Alessandro, committed as downloaded
before any count:

* `data/te_default_genre_alessandro.csv`;
* `data/te_words_alessandro.csv`.

Tally: `experiments/te_default_tally.py`, committed before the labels. Outputs:

* `data/te_default_tests.csv`;
* `data/te_default_cells.csv`;
* `data/te_words_table.csv`.

## Renders and gate

280 of 280 renders exist; the empty prompt encoded without error. The amended gate passed: the zero push and the three
real pushes are pixel-identical (max abs diff 0) to the plain render and to the edits' existing renders. Antigravity
did not write the `RENDERS` paste-back; Claude re-ran `--gate` and `--count` from the same script and reports their
output here.

## Labels

* **Missing labels.** Three are missing, and the images exist:
  * order 5 of the original at seed 1234567;
  * order 5 of the no-style elf at seed 1234567;
  * the whole "dwarf" row of block B (and three genres of "close-up on gauntlet").

  By the pre-registration, missing labels are left out. Order 5 at seed 1234567 therefore drops out of every
  switch count (27 cells instead of 30).
* **Repeat agreement.** The 20 images already labelled in C70 — the originals and L05, L06, L28 at seed 3141592 —
  received the same genre in 20 of 20.

## Tests

| test | value | verdict |
|---|---|---|
| A1 — the elf without style words | anime in 9 of 9 labelled (one unlabelled) | **default anime supported** (bar 7 of 10; holds even if the missing one is not anime) |
| C1 — permuted pushes | switch rate 0.41 (11/27) against 0.52 (14/27) for the real edits, R = 0.79 | size alone suffices (bar 0.5) |
| C2 — shared pushes | 0/27, R = 0 | the direction matters (bar 0.2) |
| C3 — token pushes | 0.37 (10/27), R = 0.71 | size alone suffices |
| joint reading (amendment 2) | C1 and C3 against C2 | **depends on the form of the push** |

## Reported

* **Empty prompt:** anime, realistic, anime, painting. Without any text the model has no single default. The anime
  default appears when a character is described without a style.
* **Where the random pushes land:** of the 21 random pushes that switched genre, 15 went to anime and 6 to cartoon.
  None was broken.
* **Per edit, out of 9 labelled cells:**

| edit | real | permuted | shared | token |
|---|---|---|---|---|
| L05 MLP doubled | 9 switch (all anime) | 0 | 0 | 1 |
| L06 MLP doubled | 5 | 2 | 0 | 2 |
| L28 MLP doubled (largest push) | 0 | 9 | 0 | 7 |

* **Words alone (block B), 4 seeds each:**
  * "uniform" → an anime girl in a school uniform in 4 of 4;
  * "female dwarf" → a woman **with a beard** in 4 of 4;
  * "female paladin mountain dwarf" → a bearded woman in 4 of 4;
  * "realistic western comics style" → bearded cowboys in comic panels in 4 of 4 ("western" read as the American West);
  * "dynamic" → anime in 4 of 4;
  * "female antlered elf brawler" → anime in 3 of 4;
  * "wide reckless grin" → anime in 3 of 4;
  * phrases without a person mostly → realistic (78 of 165 labelled single-word pictures are realistic);
  * "dwarf" alone was not labelled.

## Reading

1. **The anime default is real and specific.** Take the style words away and the elf is drawn as anime in every
   labelled case. The empty prompt is not anime, so this is not the model's global default. It is what this
   character description becomes when nothing names a style: the elf, the grin, the dynamism are each anime-leaning on
   their own (block B). The three style words were holding the picture in Western comics. This confirms Alessandro's
   remark: there is no picture "without style", and here the fallback is anime.
2. **Random pushes of the same size also reach the default, but only if they vary from token to token.**
   * A random vector added equally to every token (shared) did nothing to the genre, in 30 of 30 pictures.
   * Random pushes with per-token structure (permuted, token) switched the genre about as often as the real edits,
     and mostly to anime.
   * So "any push of this size goes to anime" holds only for pushes that differ between tokens. A uniform shift of
     the same size is harmless. The real pushes are mostly per-token (the shared part is 21-57%,
     `data/te_massive_channels.csv`).
3. **The real edits are not random pushes: their direction matters, edit by edit.**
   * L28 has the largest push. Random pushes of its size switch 16 of 18 pictures, yet the real L28 edit keeps every
     picture a Western comic.
   * L05 sends all 9 cells to anime, while random pushes of its size almost never switch (1 of 18).
   * So the real L05 direction leads to anime at a size where chance does not, and the real L28 direction protects
     the comic at a size where chance would leave it.
   * Neither edit is explained by size alone.
4. **The word priors predict what surfaces.**
   * "female dwarf" is drawn with a beard on its own; the beard Alessandro saw on the dwarf under edits is the
     model's prior for "dwarf", not something the edit created.
   * "uniform" alone is an anime school uniform (the L05 pictures show a military one).

## Limits

* One labeller, not blind; one prompt family; two seeds for blocks A and C; one noise seed per variant.
* Block B is descriptive, with four seeds per phrase.
* A shared push may be partly absorbed by normalisation inside the image model's text path. This is untested, and
  it would explain C2 without saying anything about genre.
* The "dwarf" prior check of the pre-registration could not be read: the row was not labelled.
