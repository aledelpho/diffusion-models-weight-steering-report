# C74 result — a dose ladder for three text-encoder edits

Pre-registration: `docs/prereg_te_dose.md` (amendments 1 and 2).
Labels: mine, committed as downloaded before any count (`data/te_dose_alessandro.csv`).
Tally: `experiments/te_dose_tally.py`, output `data/te_dose_tests.csv`.
Renders: `docs/RENDERS_2026-10-13_te_dose.md` (gate PASS, 199/199).

The ladder has twelve doses per strip: 0.10, 0.25, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00. There are 18
strips (3 edits × 3 characters × 2 seeds). H1–H3 use the 12 strips of L06 and L14. They count only the strips whose style
changes at some dose: 11 of 12.

## Tests

| test | value | verdict |
|---|---|---|
| H1 gradual vs step | gradual in 8 of 11 = 0.73 | gradual (bar 0.6) |
| H2 intermediate doses move toward the d = 1.00 picture | yes in 10 of 11 = 0.91 | supported (bar 0.7) |
| H3 style change before loss of coherence | style first in 11 of 11 | style moves before coherence breaks |

## What the tests hide

* **H1 is pooled across two edits that behave differently.**
  * L14 is gradual in 6 of 6.
  * L06 is a step in 4 of 5 (5 of 6 with the slip below).
  * The pooled "gradual" verdict comes from L14. The per-edit split was not preregistered as a test, so it is reported
    here as a description.
* **H3 is met in the simplest way.** I marked coherence as lost in none of the 18 strips, up to and including d = 1.00
  (17 "never", 1 blank). Under the amendment 2 definition, none of these pictures reads as broken. So the genre
  switches at d = 1.00 that C70–C73 counted are not a loss of coherence.
* **A labelling slip.** In the strip L06 · half-orc · 3316624 the onset is "never", but the same row says "step" and
  "toward 1.00: yes". The note is the same as for the other seed.
  * I opened the strip next to the other seed (`Text2Img\_grid_viewer\_c74_check\o4_l06.jpg`). The picture goes
    from comic to photographic at 0.80, as on seed 2645751.
  * The CSV stays as downloaded, and the row is out of H1–H3 because its onset is "never".
  * With the onset read as 0.80, H1 is 8 of 12 = 0.67 (gradual) and H2 is 11 of 12 = 0.92 (supported). No verdict
    changes.

## Descriptive

**The style holds until late.**

* No strip changes style below d = 0.70.
* L06 changes at 0.80 in four strips and at 0.85 in one.
* L14 changes at 0.70, 0.80, 0.95, 0.95, 1.00 and 1.00.
* L28 (the control) never changes style, as in C73.

**Seeds agree; characters differ.**

* The two seeds of a character and edit change within one or two steps of each other.
* Under L14 the dwarf changes at 0.70–0.80. The elf and the half-orc change at 0.95–1.00.

**Destinations match C73.**

* L06 goes to photographic or realistic for the dwarf and the half-orc.
* For the elf rogue, L06 passes through a painted look at 0.80–0.85 and then reaches anime by 1.00. These are the L06
  anime cases C73 already found on this character.
* L14 drifts toward cartoon.

**Prompt attributes often go first** (amendment 2, reported only).

* In L06 and L14, attributes are lost before the style changes in 5 of 10 strips, at the same dose in 2, and after in 3.
* In L28, which never changes style, attributes are lost in 4 of 6 strips.
* What goes:
  * hair colour (dwarf, half-orc; L14);
  * the elf rogue's dark skin (L14, from 0.80 and 1.00). The prompt names no skin tone ("non-binary rogue wood
    elf"), so this is a drift from the original picture, not a lost prompt trait;
  * the half-orc's tusks, ears and skin;
  * clothing:
    * the half-orc fighter gets a garment I described as a kimono (L06 from 0.70, L28 from 0.90);
    * in the opened strip it is a high mandarin-style collar with frog fastenings;
  * the elf's face turns green, then olive (L28).
* **In the opened L06 half-orc strip** (both seeds):
  * the tusks are gone by 0.60–0.70;
  * the pointed ears and grey-brown skin give way to a lighter-skinned human woman by 0.70;
  * all of this happens while the picture is still drawn as a comic.
  * The edit changes who is drawn before it changes how.
* **Composition is stable along the ladder.** I wrote "linear composition" on all 18 strips: pose and framing move
  smoothly from one dose to the next, even where the style jumps.
  * The one exception: the elf rogue's hood under L06, which goes up between 0.70 and 0.80.
  * This was not a preregistered question.

## What this changes

* **The d = ±1 edits of C64–C73 were large, but they did not break the pictures.** What changed at d = 1.00 was style
  and content, not coherence. This answers the first doubt that led to C74.
* **"Gradual or step" depends on the edit.**
  * L06 switches rendering mode (comic to photo) in one step around 0.80.
  * L14 slides toward cartoon.
  * The ridge reading of page 22 fits L06, not L14.
* **The style is robust to most of the dose range.** Nothing moves below 0.70. By the (1 + d)³ estimate that is an MLP
  output already several times larger than the original. This is an estimate, not a measurement.
* **Identity moves before style.**
  * Race markers, skin tone, hair colour and clothing change before, or without, any change of genre.
  * Some are asked by the prompt (the half-orc's tusks, the dwarf's copper hair); others are choices of the original
    picture the prompt does not name (skin tone, pointed ears). My notes did not separate the two.
  * At seed 2645751 the original half-orc already shows no tusks: the baseline itself does not satisfy every trait.
  * The direction is toward a lighter-skinned, more generic human.
  * This fits the stereotype hypothesis behind C70: weakening part of the encoding lets defaults take over.
  * The default here is in the character, not only in the style.
  * It rests on three characters and my free-text notes. It is a lead, not a result.

## Limits

* One labeller, not blind (doses visible), who had seen the d = 1.00 renders before.
* Three characters, two seeds, one edit type.
* The attribute question decides nothing and was answered in free terms (which attribute was not fixed in advance).
* One row has an internal inconsistency (above). It does not change any verdict.
