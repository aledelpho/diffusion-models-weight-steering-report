# Pre-registration C74 — a dose ladder: does the style move gradually, and when does coherence break?

Written 2026-10-13, **before any C74 render or label.** Renders authorised by Alessandro on 2026-10-13.

* Code: `experiments/te_dose.py` (plan, queue, gate, count) and `experiments/te_dose_tally.py` (rules, with a
  self-test).
* Labelling page: `grid_viewer.py --set te_dose`.
* Plan: `data/te_dose_plan.csv`, 73 renders.

## Why

Every text-encoder result so far (C64–C73) was made at d = ±1. Alessandro raised two doubts about that:

* the dose may be so strong that part of what we called a change of genre is a loss of stylistic coherence;
* genre labels hide very different sub-styles.

Two further points bear on the design:

* **The real size of these edits.** The edit scales the three matrices of an MLP (gate, up, down) by 1 + d each.
  Where the gate's activation is in its linear range, the MLP's output then grows roughly like (1 + d)³:
  * about ×1.3 at d = 0.10;
  * ×2.0 at 0.25;
  * ×3.4 at 0.50;
  * ×5.4 at 0.75;
  * up to ×8 at 1.00.

  This is an upper estimate from the arithmetic of the layer, not a measurement. "Doubling" an MLP was therefore far
  stronger than the word suggests.
* **The ridge reading** (results page 22) predicts a step, not a gradual shift. It also predicts that the step comes
  at different doses for different seeds.

## Material

* **Edits.** Three MLP edits whose destination is clear across characters (C73):
  * L06 → realistic;
  * L14 → cartoon;
  * L28 → stays Western comic (the control).
* **Doses.** d = 0.10, 0.25, 0.50, 0.75 are new; d = 1.00 is the existing C65 render.
* **Characters.** Three portraits: dwarf paladin, elf rogue, half-orc fighter.
* **Seeds.** The two C65 seeds, 2645751 and 3316624.
* **Renders.** 72 new renders, plus 1 gate render.

## Gate

L06 at d = 1.00 on the dwarf at seed 2645751, rendered again, must be pixel-identical to the C65 render.

## Labels — comparative, not genre

The page shows 18 strips (edit × character × seed): the original and the five doses side by side. For each strip
Alessandro answers four questions:

| question | choices |
|---|---|
| from which dose does the style differ from the original | 0.10 / 0.25 / 0.50 / 0.75 / 1.00 / never |
| how does it change | gradual / step / none |
| do the intermediate doses move toward the d = 1.00 picture | yes / no / unclear / none |
| from which dose does the picture lose stylistic coherence (mixed styles, broken rendering, artefacts) | 0.10 / … / 1.00 / never |

The page is not blind: doses are visible, since the question is about the ladder itself. The CSV is committed as
downloaded, before any count.

## Rules (fixed now; `te_dose_tally.py`)

All three tests use the strips of L06 and L14 (12 strips) whose style changes at some dose.

| test | measure | rule |
|---|---|---|
| H1 | share answered "gradual" (among gradual / step) | ≥ 0.6 → **gradual**; ≤ 0.3 → **step-like** (ridge reading); otherwise inconclusive |
| H2 | share answered "yes" (among yes / no / unclear) | ≥ 0.7 → **supported**; ≤ 0.4 → not supported; otherwise inconclusive |
| H3 | strips where the style changes at a lower dose than coherence is lost (or coherence is never lost), against strips where coherence is lost at or before the style change | ≥ 2/3 the first → **style moves before coherence breaks**; ≥ 2/3 the second → **the change is mainly a loss of coherence**; otherwise inconclusive |

## Reported

* L28 (control): onsets and coherence.
* The distribution of onset doses per edit.
* Whether the two seeds of the same character and edit change at the same dose.

## Limits

* One labeller, not blind.
* Three characters and two seeds.
* One edit type (MLP, all three matrices).
* The doses are equal steps of d, not of effect.
* The (1 + d)³ figure is an estimate, not a measurement.

## Amendment 1 (2026-10-13, while the first renders were running, before any C74 label)

At Alessandro's request I added more intermediate doses, mostly at the high end, where the jump to the d = 1.00
picture happens. The new doses are 0.40, 0.60, 0.70, 0.80, 0.85, 0.90 and 0.95, rendered for every strip.

* **Renders.** 7 new doses × 18 strips = **126 more renders**. The plan now has 199 rows; the new rows are appended,
  so the original rows keep their order.
* **The ladder per strip.** The original plus twelve doses: 0.10, 0.25, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85,
  0.90, 0.95, 1.00.
* **Questions.** The same four, with the same twelve doses offered as answers.
* **Rules.** H1–H3 and their thresholds are unchanged. The tally orders the doses by their value
  (`te_dose_tally.py`, self-test updated).
* **What had happened before this amendment.** The gate passed (max abs diff 0) and 62 of the first 73 renders
  existed. None had been labelled or looked at for this test.
