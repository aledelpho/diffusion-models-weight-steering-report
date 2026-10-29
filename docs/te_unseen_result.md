# C114 result — C113's dose windows, blind, on three unseen prompts

Pre-registration: `docs/prereg_te_unseen.md`. Renders: `docs/RENDERS_2026-10-28_te_unseen.md` (123 of 123, three
gates pixel-identical). Labels by Alessandro, committed as downloaded before any count: `data/te_unseen_labels.csv`;
key `data/te_unseen_key.csv`; tests `data/te_unseen_tests.csv`; DINOv2 `data/te_unseen_dino.csv`.

## Rules

| rule | value | verdict |
|---|---|---|
| 0 — null cards called "same way" | 0.00 (n 6) | ok |
| 1 — same way, edit cards against null (primary) | 0.75 (n 12) against 0.00 | **the change repeats across seeds on unseen prompts** |
| 2 — subject, colour and style kept (all or most), edit cards | 12 of 12 | **the window doses respect the prompt** (see the caveat) |
| 3 — DINOv2: distance from plain ≥ plain seed spread | 11 of 12 cells (ratio 0.69–2.69) | **supported** |

## Reported

* **Per cell (same way):** "sì, tutte" in 8 of 12, "la maggior parte" in 2 (tree P01, robot E06), "ognuna a modo suo"
  in 2 (dagger E14, dagger E28). DINOv2 agrees on dagger E14 (ratio 0.69, consistency 0.03, the only cell under the
  seed spread); dagger E28 is above the seed spread (1.33) but with low consistency (0.21).
* **Amount:** edit 0.89, null 0.94, seed 1.00 — by eye, a change of seed still looks as large as an edit (as in C112),
  while DINOv2 puts 11 of 12 edits above the seed spread. The eye weighs the whole picture; DINOv2 the object.
* **Plain seed spread:** 0.046 (tree), 0.137 (dagger), 0.078 (robot): the detailed prompts vary little with the seed.
* **Kept:** "in tutte" on every card, edit, null and seed alike, so the question did not discriminate. On the sheet,
  P01 at 1.75 on the robot draws a metal robot next to a separate small clay figure in all 8 seeds — Alessandro's note
  ("clay figure viene visto come un altro elemento separato dal robot") — i.e. the edit reinterprets the style word
  while every word is still somewhere in the picture. Rule 2 passes on its wording; it does not show that style words
  are untouched.
* **Notes:** E28 on the tree brings water into many versions; E28 on the robot "grossi occhi neri, più cute"; E06 on
  the tree a warmer, yellower tone; tree E14 "si potrebbe alzare o abbassare un po'". All three seed cards and most
  null cards were recognised ("risultati di edit diversi").
* **Test–retest:** 3 of 3 on all three questions.

## Reading

1. **Confirmed blind on prompts nobody had seen:** at C113's doses (E06 0.8, E14 0.8, E28 1.06, P01 1.75) an encoder edit
   leaves a change that is the same at every seed in 10 of 12 prompt × edit cells, and by DINOv2 moves the picture
   more than a change of seed in 11 of 12. This is what C112 lacked at half the doses.
2. **The windows transfer:** chosen on a blue tree and a helmet, they held on a watercolour tree, an art-deco dagger and
   a clay robot without breaking any picture.
3. **Not every edit on every subject:** E14 on the dagger does not repeat; the effect is per edit × subject, as in
   C104–C109.
4. **Style words can be reinterpreted rather than dropped** (P01 on the robot); the "kept" question was too coarse to
   catch it.

## Limits

One observer, who proposed the hypothesis and recognised the control cards; prompts written by Claude; three prompts,
8 seeds, one card per cell; the "kept" question at ceiling; Krea-2 turbo only.

## Addendum (2026-10-29, Claude's non-blind reading of the robot sheet, after the rules)

* **E14 0.8** gives the strongest and most uniform change: a lighter lime green, a rounded helmet-like head with a cream
  face window and black eyes, green antennae; **the copper eyes are gone at all 8 seeds** — a stated attribute
  overridden, which the "kept" answer ("in tutte") did not record. DINOv2: ratio 2.47, consistency 0.60, the highest
  on this prompt.
* **P01 1.75** turns the clay robot into a glossy, detailed metal robot with glowing yellow-green eyes in a
  photographic indoor scene, and places a separate small clay figure beside it at most seeds: "clay" and "copper" are
  reassigned, not kept.
* **E06 0.8** simplifies the robot (smoother body, fewer panels, black pupils inside the copper rims): same robot, less
  detail; the most variable of the four between seeds ("la maggior parte").
* **E28 1.06** is the lightest: same robot, colour and material, larger glossy black pupils inside the copper rims, a
  slightly rounder, "cuter" head — the only edit that keeps every stated attribute (DINOv2 ratio 1.00, at the seed
  spread).
* So on this prompt the strength of the repeated change and the respect of the prompt pull in opposite directions:
  the two edits that change most uniformly (E14, P01) are the two that override stated attributes.

## Correction of three labels (2026-10-29, after the rules; reported, the as-labelled file is unchanged)

Alessandro, after the addendum: on the robot he had judged "kept" on the general description and missed the copper
eyes; E14 and P01 lose them at every seed. Corrections in `data/te_unseen_labels_corrections.csv` (W23, W10 and its
repeat W21: *in tutte* → *in nessuna*). With them, rule 2 is **10 of 12** (bar 9) — still above the bar on its wording,
kept 0.83 for edit cards against 1.00 for null and seed. The bar was set for a question that turned out too coarse; the
honest reading is that **two of the four edits override a stated attribute on one of three prompts**.

## Claude's non-blind reading of the tree and the dagger (2026-10-29)

* **Tree** (plain: the same weeping watercolour tree at every seed). E06: denser, darker red canopy filling the frame,
  more stranded trunk — same tree, heavier. E14: barely different from plain (Alessandro's "si potrebbe alzare").
  E28: the trunk's curl drawn literally as a spiral, a dome-shaped canopy and **a pond of blue water at the base** at
  most seeds — every stated attribute kept, something added. P01: a compact, symmetric weeping dome on a clean white
  ground at 6 of 8 seeds, seeds 1 and 8 close to plain ("la maggior parte"). No attribute lost on this prompt.
* **Dagger** (plain: one dagger in product-photo light on grey, varying angle; the art-deco inlays are faint). E06 and
  P01: at every seed the dagger stands upright and centred on **a black-and-gold art-deco panel** (sunbursts,
  geometric frames) — "art deco golden geometric" moves from the inlays onto the background, as "clay" moved off the
  robot; the blade itself is plainer. E14: mostly plain-like, one seed with an art-deco panel, one with two crossed
  blades — "ognuna a modo suo" fits. E28: dark backgrounds, more engraving on the blade, close crops and partial deco
  patterns, varying from seed to seed — the darkening repeats, the composition does not.
* **Across the three prompts:** the edits that change most uniformly (E06, P01; E14 on the robot) tend to **move a
  stated attribute to another place** in the picture (background, a second figure) or replace it; E28 adds something
  (water, bigger eyes, engraving) while keeping what is written. This pattern is read after the data and is not
  tested.
