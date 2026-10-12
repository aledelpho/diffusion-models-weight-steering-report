# C70 result — genre and intensity of each image (seed 3141592)

Pre-registration: `docs/prereg_te_genre.md` (amendments 1 and 2).
Labels, by Alessandro, committed as downloaded: `data/te_genre_alessandro.csv`, `data/te_genre_dose_alessandro.csv`.
Tallies: `experiments/te_genre_tally.py`, `experiments/te_genre_dose_tally.py`.
Outputs: `data/te_genre_tests.csv`, `data/te_genre_by_edit.csv`, `data/te_genre_dose_tests.csv`.

## Tests

| test | value | verdict |
|---|---|---|
| G1 switch vs style share (20 C69 images) | AUC 0.46 (7 switched, 13 not) | not supported |
| G2 switch rate vs order score | ρ 0.52 (n 20) | supported (at the threshold) |
| G3 switch rate vs conditioning size | ρ 0.73 | supported |
| G1d intensity vs style share (20 C69 images) | ρ +0.05 | not supported |
| G1d inside L06 MLP+ / L12 MLP+ (reported) | ρ −0.45 / 0.00 (n 5 each) | — |
| G2d mean intensity vs order score | ρ 0.70 | supported |
| G3d mean intensity vs conditioning size | ρ 0.80 | supported |

## Descriptive

* **The originals are all labelled Western comics.** Word order alone does not change the genre.
* **Where the switches go.** Of the 50 edited images that switch genre, 39 go to anime and 11 to cartoon. None go to
  realistic or painting.
* **No negative-dose edit switches genre.** These are L04 MLP−, L08 MLP−, L10 MLP− and L19 attention−. Their mean
  intensity is 0–0.8.
* **Most positive-dose edits switch.** The exceptions are L10 attention+, L15 attention+ and L28 MLP+.
* **Two patterns among the edits that switch:**
  * all five orders go to the same genre (L05, L20, L25 MLP+ → anime);
  * the orders scatter across genres (L06, L09, L12, L14 MLP+).
* **How the two patterns scored in the C65 B order grid.** The scattering edits scored 4–5, and include both 5s. The
  coherent ones scored 2–4 (L25 2, L20 3, L05 4).

## What this changes

* The **size of the text-encoder push predicts how much the image changes** (G3d ρ 0.80), as C67 E1 found.
* The **default style is real as a description.** When the genre changes, it goes to anime in 39 of 50 images.
* The **mechanism proposed in C69 does not hold image by image.** Less attention on the style words does not mark the
  images that leave the comic style, neither as a yes/no switch nor as an intensity. The pull toward anime has to come
  from what the conditioning *says*, not from where the image reads it.

## A labelling note

L28 MLP+ is labelled Western comics in all five orders but intensity 3 ("entirely another genre") in all five.

* Opened and compared with the original (`Text2Img\_grid_viewer\_c70_check\l28.jpg`): the images stay Western comics.
  The rendering changes a lot — cleaner and glossier, more saturated, lightning added, tighter framing.
* So intensity was in practice scored as overall change of style, within or across genre.
* This does not touch G2d and G3d, which are about change. It does make the intensity scale mix two things.
