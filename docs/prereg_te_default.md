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

## Amendment 1 (2026-10-12, after the gate failed, before any render of blocks A, B, C)

**The gate failed** (`python te_default.py --gate`, run by Antigravity):

* zero push: max abs diff 0;
* real push L05: ratio 0.186;
* real push L06: ratio 0.372;
* real push L28: ratio 0.278;
* the bar was ≤ 0.25 for all three.

Antigravity stopped as instructed.

**What the renders show.** Claude opened the four gate renders next to the existing renders
(`Text2Img\_grid_viewer\_c70_check\c72_gate.jpg`). The three rebuilt pushes give the same genre and composition as the
real edits; L05 and L28 are nearly indistinguishable from them. On L06 the details are redrawn: the head turns, and
an ear and a mark over the eye appear.

**Cause.** The push was rebuilt from the C67/C68 encodes, which are stored in float16, so it carried rounding of about
2⁻¹¹ relative. The sampler (euler_ancestral) redraws unstable details under any small change of input, as results
page 22 documents for the weights. The node adds the push correctly; the threshold of 0.25 was a guess, made without
knowing how much a rounding-size change moves this sampler. Noted, not used: L06, the edit whose word orders scatter
across genres, was the most sensitive to this tiny difference.

**Change.**

* **The node (version 2)** measures the push live, inside each workflow. It encodes the prompt twice — plain CLIP,
  and the same CLIP under the edit's ArthemyKrea2CLIPTuner patch — in the conditioning's own precision. The
  variants are otherwise unchanged.
* **"real" now passes the edited conditioning through untouched**, so the gate can be strict.
* **New gate:** the zero push must be pixel-identical to the plain render, and **each real push must be
  pixel-identical to the edit's existing render** (max abs diff 0). This also checks that the tuner node does not
  alter the plain CLIP that feeds the other encode.
* **The four version-1 gate renders** stay in the folder, unused; the new gate rows are named `..._v2`.
* Tests, thresholds, material and the noise seed are unchanged. Blocks A, B and C had not been rendered.

## Amendment 2 (2026-10-12, after the renders were queued, before any label)

Written after a literature search on massive activations (Sun et al. 2024, arXiv 2402.17762). Qwen3-VL-4B's hidden
states have a few channels far larger than the rest. In the C67 baseline of V1 at the last tap, channels 4 and 0
average 84.7 times the median channel (`data/te_massive_channels.csv`, `experiments/te_massive_channels.py`,
exploratory).

The real pushes touch these channels first, but are not dominated by them. Over the 20 C65 edits at the last tap:

* the two large channels carry 2–14% of the push energy;
* the push's own ten largest channels carry 5–19%;
* the component shared by all tokens carries 21–57%.

**Consequence for block C.** The **permuted** variant moves the push's components from the large channels into
ordinary ones. That is a perturbation no real edit produces, so it could change the picture for a reason other than
the size of the push. The **shared** and **token** variants do not have this property. Therefore:

* C1 (permuted) is reported together with C2 (shared) and C3 (token), never alone;
* if C1 and C2/C3 disagree, the result is read as **"depends on the form of the push"**, not as support for either
  reading.

The rules and thresholds are unchanged. This amendment was written while the renders were running and before any C72
image was looked at or labelled.
