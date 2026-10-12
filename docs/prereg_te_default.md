# Pre-registration C72 — the model's own defaults: no style words, one word at a time, and random pushes

Written 2026-10-12, **before any C72 render.** Renders authorised by Alessandro on 2026-10-12.

* Code: `experiments/te_default.py`.
* Node: `tools/comfyui_krea2_condpush` (`Krea2ConditioningPush`).
* Plan: `data/te_default_plan.csv`, 280 renders. Folder `Text2Img\benchmark_te_default`.

## Why

C69–C71 found that text-encoder edits send the elf to anime in 39 of 50 genre switches, and that neither less
attention on the style words nor a push resembling "anime style" explains it. Three readings remain, and this
experiment separates them:

1. **Default style.** With no working style words, Krea-2 draws anime. This is Alessandro's remark that there is no
   picture "without style", and nobody has looked at that picture yet.
2. **Word priors.** Each word carries its own typical picture. For example, "dwarf" suggests a bearded man, and
   "uniform" a military anime uniform. An edit that loosens the links between words lets those priors surface.
3. **Size alone.** Any push of the conditioning as large as an edit's, in any direction, sends the picture to the
   same place.

The third is the review's priority control. The ridge reading (results page 22) predicts the same for the word
orders: a large push carries the picture near a boundary, and a small difference decides the side.

## Material

| block | what | renders |
|---|---|---|
| gate | V1, seed 3141592: zero push; real push of L05, L06, L28 MLP doubled rebuilt on the plain conditioning | 4 |
| A | the elf in five orders **without** "realistic western comics style", "bold ink outlines", "hatched shadows" (seeds 3141592, 1234567); the **empty prompt** (seeds 3141592, 1234567, 1618033, 2718281) | 14 |
| C | random pushes added to the plain conditioning, no weight edited: three variants × L05, L06, L28 MLP doubled × five orders × two seeds | 90 |
| B | each of the 36 clauses of the elf prompt alone, plus "dwarf", "female dwarf", "female paladin mountain dwarf", "elf", "female elf", "uniform", "brawler"; four seeds | 172 |

**Block C variants.** The real push P = edit − baseline comes from the full C67 and C68 encodes. Every variant has
the same norm as P on each of the 12 taps, and zero on the taps the edit does not reach.

* **permuted** — P with its 2560 channels shuffled by one fixed permutation. It keeps P's structure over tokens and
  its few very large channels, but moves them, so the direction is random.
* **shared** — one random unit vector per tap, added to every token. It mimics the fact that the real push is mostly
  common to the whole prompt (C67).
* **token** — independent Gaussian noise for every token.

Noise seed 7, the same in every order and image seed, so each variant acts like one fixed "edit". The three edits
are:

* L05: all five orders go to anime;
* L06: the orders scatter across genres;
* L28: the largest push, and the genre stays Western comic.

Sampling as in C65: euler_ancestral, 9 steps, cfg 1.0, simple, 1024×1280.

## Gate (before any label)

* **Zero push** must be pixel-identical to the existing plain render of V1 at seed 3141592.
* **Real push** of each of the three edits, added to the plain conditioning, must reproduce the edit's existing
  render closely. The mean absolute pixel difference to that render must be ≤ 0.25 × the difference between the plain
  render and the edit's render. The rebuilt push is exact up to the float16 storage of C67 and C68; the threshold
  allows for that rounding.

If the gate fails, nothing below is labelled.

## Labels (after the renders, before any count)

Alessandro labels each picture on a grid page built after the renders, with the C70 genres:

* the C70 genres: Western comic, anime, cartoon, realistic, painting, other;
* plus **broken**, for no recognisable character or a destroyed picture.

The grid also includes the real edit renders of L05, L06 and L28 at seed 1234567 (C65 B), which C70 did not label.
For block B he also notes, where a person appears, apparent gender and beard.

The CSV is committed as downloaded before any count. The page shows the condition names, so the labelling is not
blind (limit).

## Tests (thresholds fixed now)

| test | measure | rule |
|---|---|---|
| A1 default style | the 10 no-style elf pictures | ≥ 7 anime → default anime **supported**; ≤ 3 → **not supported**; otherwise inconclusive |
| C1 size alone (primary) | R = genre-switch rate of the **permuted** pushes ÷ switch rate of the real edits, same 30 order × seed × edit cells | R ≥ 0.5 → size alone suffices **supported**; R ≤ 0.2 → the direction matters; otherwise inconclusive |
| C2 / C3 | the same for **shared** and **token** | same rule, secondary |

**A switch** means a genre different from the plain render of the same order and seed, labelled in the same pass. A
**broken** picture counts as no switch, and broken pictures are reported apart.

## Reported, deciding nothing

* The genre of the empty prompt (4 pictures).
* Among switched pictures in block C, the share that is anime.
* Block B, per word, the genre and the person: in particular whether "dwarf" alone gives a bearded man in at least
  3 of 4 seeds and whether "female dwarf" ever does, and what "uniform" draws.
* Whether the C1 rate differs between L05, L06 and L28.

## Limits

* **One labeller**, not blind to the condition.
* **One prompt family**, two seeds for blocks A and C.
* **One wording** for "no style": dropping the clauses also shortens the prompt.
* **The empty prompt may fail** to encode with Krea-2's template; if so it is reported missing.
* **Block C rests on one noise seed** per variant. Its pushes are matched in size and coarse structure, not in
  whatever else makes the real pushes special.
* **The ridge reading** predicts a gradual rise of switches with dose. That needs intermediate doses across orders
  and seeds, which this plan does not include.
