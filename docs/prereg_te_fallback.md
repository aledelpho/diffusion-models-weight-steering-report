# Pre-registration C73 — does every character fall back to its own genre?

Written 2026-10-13, **before any C73 render or label.** Renders authorised by Alessandro on 2026-10-13.

* Code: `experiments/te_fallback.py` (plan, queue, gate, count), `experiments/te_fallback_tally.py` (rules, with a
  self-test).
* Labelling page: `grid_viewer.py --set te_fallback`.
* Plan: `data/te_fallback_plan.csv` (29 renders).

## Question

C72 showed that the elf, with her style words removed, is drawn as anime (9 of 9). The same text-encoder edit (L06
MLP doubled) that sends the elf toward anime or cartoon turns the dwarf and the gnome into photographs (results page
30, F30.12). Two questions follow:

1. **H1.** Does each character have its own fallback, the genre it takes when nothing names a style?
2. **H2.** Do strong edits send each character toward its own fallback?

## Material

* **New renders (28 + 1 gate).** The seven C65 characters (dwarf paladin, elf rogue, half-orc fighter, gnome wizard,
  halfling druid, dragonborn cleric, tiefling bard), each with the clause "Western comics style" removed.
  * The C52 frame becomes "close-up portrait, frontal view."; nothing else changes.
  * Seeds: the four C52 phase-C seeds (2645751, 3316624, 3605551, 4123105).
  * Plain model and plain encoder; sampling as in C52 and C65.
* **Existing renders.**
  * The C52 baselines with the style clause, at the same four seeds.
  * The C65 pictures of the eleven **MLP-doubled** edits (L02, L05, L06, L09, L12, L14, L17, L20, L25, L26, L28) on
    the seven characters at the two C65 seeds.

## Gate

The C52 baseline of the dwarf at seed 2645751, rendered again, must be pixel-identical to the existing file.

## Labels

Alessandro labels one genre per picture on one page (Western comic, anime, cartoon, realistic, painting, other,
broken):

* the 28 with-style baselines;
* the 28 no-style pictures;
* the 154 edited pictures.

The page is not blind (limit). The CSV is committed as downloaded, before any count.

## Rules (fixed now; `te_fallback_tally.py`)

**Definitions.**

* **Fallback of a character:** the genre given to at least 3 of its 4 no-style pictures. Otherwise "mixed".
  Broken pictures do not count.
* **Switch:** an edited picture whose genre differs from the with-style baseline of the same character and seed.
  Broken pictures are not switches.

**Tests.**

| test | measure | rule |
|---|---|---|
| H1 | distinct fallbacks among the characters that have one | ≥ 2 → **supported** (the fallback depends on the character); exactly 1 → **not supported** (one fallback for all); none → inconclusive |
| H2 | among switched pictures of characters with a clear fallback, the share that lands on that character's fallback, against the share expected if destinations ignored the character (each genre's overall share among all switches) | match − expected ≥ 0.20 **and** match ≥ 0.5 → **supported**; difference ≤ 0.05 → **not supported**; otherwise inconclusive |

## Reported

* Each character's with-style genres, no-style genres and edit switches.
* Whether anime is a fallback, and for how many characters.
* The elf of C72 (anime) next to the seven.

## Limits

* **The labeller.** One labeller who knows the condition and has seen many of these pictures.
* **Seeds.** Four seeds for the fallback, two for the edits.
* **One cut.** Removing "Western comics style" removes one phrase among several. The portraits keep "close-up
  portrait, frontal view", and the characters' own words carry style too, as C72 block B showed.
* **H2 is a coarse test.** The share expected under independence uses the same switches it is compared with.
