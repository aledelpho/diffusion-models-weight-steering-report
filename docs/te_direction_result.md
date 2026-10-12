# C71 result — the edits do not push toward "anime" the way the text does

Analysis run 2026-10-12 on the 16 encodes of `docs/RENDERS_2026-10-12_te_direction.md`. Pre-registration:
`docs/prereg_te_direction.md`. Data:

* `data/te_direction_by_edit.csv` — the cosines, per edit;
* `data/te_direction_tests.csv` — the tests;
* `data/te_direction_norms.csv` — the sizes; exploratory, added after the tests.

## Gate

The re-encoded V1 baseline is **bit-identical** to the C67 baseline (`GATE PASS`); all 16 encodes are present.

## Tests

| test | value | verdict |
|---|---|---|
| H1 cos(push, anime direction) vs anime count (20 edits) | ρ −0.01 | not supported |
| H2 cos(push, anime − painting) vs anime count | ρ −0.00 | not supported |
| R1 cos(push, cartoon − painting) vs cartoon count (reported) | ρ 0.52 (p 0.02) | — |
| R2 cos(push, painting) vs anime count (control, reported) | ρ 0.06 | — |
| R3 similarity of the swap directions (reported) | anime~cartoon 0.79, anime~painting 0.36, cartoon~painting 0.38 | — |

The cosines between an edit's push and any style direction are all small: between −0.12 and +0.07. The three edits
that send all five orders to anime (L05, L20, L25 MLP+) have *negative* cosines with the anime direction
(−0.02, −0.06, −0.06).

## Exploratory (not preregistered)

Size of each edit's push against the size of the "comics → anime" swap, on the same taps, mean over the five orders
(`data/te_direction_norms.csv`):

* the push is **4.8 to 24 times larger** than the swap;
* this ratio vs number of images that switch genre: ρ 0.41 (p 0.08).

## What this says

* **The anime pull is not a text-like move.** An edit that ends in anime does not move the conditioning toward what
  "anime style" would write. Its push is far larger than a change of style word, and nearly orthogonal to it.
* **One explanation is compatible with most of C67–C71, but has not been tested:** the edits move the conditioning off
  the region that normal prompts occupy. The further off it goes, the less the DiT can use the text, and the more it
  falls back on its own default for "illustration", which for this model is anime.
  * This would explain why the *size* of the push predicts the change (G3d ρ 0.80) while its *direction* does not.
* **There are clear exceptions to that explanation:**
  * **L28 MLP+** has the largest push (247, ratio 24) and never leaves Western comics. It does change the rendering
    strongly (intensity 3 in all orders).
  * **L10 attention+** (126) does not switch.
  * **L12 attention+** (81) switches 4 of 5 to anime.
  * **L04 MLP−** (98, negative dose) does not switch.
  * So size alone does not decide *whether* the genre changes. It tracks *how much* the image changes.
* **Cartoon (R1, ρ 0.52) is the only sign of a direction effect.** It is reported, not tested, and cartoon counts are
  small (at most 3 per edit).

## Limits

* Pooled over positions: a direction effect located on a few tokens could be hidden.
* One wording per style.
* One labeller and one seed for the anime counts.
* The off-region explanation is a hypothesis that needs its own test. For example, the anime rate should rise with
  the distance of the conditioning from a set of ordinary prompts, at matched push size, or under random pushes of the
  same size.
