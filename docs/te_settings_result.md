# C112 result — subject fixed, setting free: one picture at every seed, and an edit that keeps its change?

Pre-registration: `docs/prereg_te_settings.md` (+ amendments 1–2, before any label). Renders:
`docs/RENDERS_2026-10-28_te_settings.md` (292 of 292, four gates pixel-identical). Labels by Alessandro, committed as
downloaded before any count: `data/te_settings_labels.csv`; key `data/te_settings_key.csv`; tests
`data/te_settings_dino_tests.csv`, `data/te_settings_tests.csv`.

## Rules

| rule | value | verdict |
|---|---|---|
| 1 — plain pictures the same at every seed (DINOv2 ≤ 0.15, ≥ 3 of 4 prompts) | helmet 0.056, axe 0.094, flying car 0.277, blue tree 0.383 → 2 of 4 | **not supported** |
| 0 — null cards called "same way" | 0.00 (n 8) | ok |
| 1b — amount, E28 + P01 cards against seed cards | 0.79 (n 8) against 1.00 (n 4) | **no more than a change of seed** |
| 2 — same way, E28 + P01 cards against null | 0.56 (n 8) against 0.00 | **the change repeats across seeds** |

## Reported

* **By edit (same way, mean of the four prompts):** E28 0.75 (blue tree 1.0, axe 1.0, helmet 0.5, car 0.5; "molto" in
  3 of 4); P01 0.38; all eight edits 0.38 (n 32); seed cards 0.00 (n 4).
* **DINOv2, agreeing with the eye:** E28 has the largest distance from plain and the most shared displacement direction
  across seeds on all four prompts (mean cosine 0.31, 0.23, 0.36, 0.14 against nulls of −0.02 to 0.04); the other
  edits stay between −0.04 and 0.27.
* **Notes:** E14 on the blue tree "foglie più grandi, colori più vibranti, lievemente più pittorico"; E06 on the car
  solves "flying" with turbines in most pictures; E26 on the axe "meno alieno". All four seed cards were recognised as
  the plain pictures reshuffled.
* **Test–retest:** amount 4 of 4, same way 2 of 4.
* **Eye against DINOv2 on the plain pictures:** the helmets are DINOv2-nearly identical (0.056) yet the seed card was
  "changed a lot": by eye (sheets), the helmet is the same object while the background colour changes from seed to seed
  (red, cream, white, purple). DINOv2 weighs the object; the observer weighs the whole picture.

## Reading

1. **The second half of the hypothesis holds, carried mainly by E28.** An encoder edit can impose a change that is
   recognisably the same at every seed (on the blue tree and the axe at all 8 seeds, by eye and by DINOv2 direction).
   This replicates page 31's "an edit leaves a signature across seeds" on new, undescribed subjects, and the exploratory
   tree's E28 at its pre-registered dose.
2. **The first half does not hold.** Even where the plain object is the same at every seed, the seed still changes the
   picture as much as or more than these edits do (background, pose, details), and two of four prompts vary a lot by
   DINOv2 as well. Across C111 and C112, the trees vary most with the seed.
3. **So the edit is not a "seed of the concept"** that replaces the seed's variety with another version. It is a
   **consistent modifier on top of it**: the seed keeps choosing composition and background, the edit adds the same
   change to whatever the seed drew. For the tool this is the useful property: a preset predictable across seeds.

## Limits

One observer who proposed the hypothesis and wrote the prompts; seed cards recognised; two amendments to the page
before labelling; doses fixed from one exploratory tree; 8 seeds; four cards per primary edit; test–retest on "same
way" only 2 of 4; Krea-2 turbo only.
