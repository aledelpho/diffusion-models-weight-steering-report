# C115 result — which attributes an edit adds, moves or removes (blind, per picture)

Pre-registration: `docs/prereg_te_attributes.md` (+ clarifications given during labelling). C114's 120 pictures, one
per card, conditions hidden. Labels by Alessandro, committed as downloaded before any count:
`data/te_attributes_labels_U1_redtree.csv`, `_U2_dagger.csv`, `_U3_robot.csv`; key `data/te_attributes_key.csv`;
tests `data/te_attributes_tests.csv`.

## Rules

| rule | value | verdict |
|---|---|---|
| 1 — predictions confirmed (≥ 5 of 8 seeds in the predicted direction; bar 70 %) | **15 of 16** | **the reading holds blind** |
| 2 — changes ≥ 5 not predicted | none | — |

Test–retest: 48 of 48 answers identical on the 12 repeated pictures.

## "Sì" out of 8 seeds

| prompt · attribute | plain | E06 0.8 | E14 0.8 | E28 1.06 | P01 1.75 |
|---|---|---|---|---|---|
| robot · copper eyes | 8 | 8 | **0** | 8 | **0** |
| robot · clay | 8 | 8 | 8 | 8 | **0** |
| robot · second figure | 0 | 0 | 0 | 0 | **8** |
| robot · big black pupils | 0 | **7** | **8** | **8** | 3 |
| tree · water at the base | 0 | 0 | 0 | **6** | 0 |
| tree · spiral / curl | 0 | 0 | 0 | 3 | 1 |
| tree · red leaves (control) | 8 | 8 | 8 | 8 | 8 |
| tree · watercolour (control) | 8 | 8 | 8 | 8 | 8 |
| dagger · golden decorations on the dagger (control) | 8 | 8 | 8 | 8 | 4 |
| dagger · art-deco panel behind | 0 | **8** | 1 | 4 | **8** |
| dagger · dark background | 0 | **8** | 0 | **5** | **7** |
| dagger · upright, centred | 2 | **8** | 3 | 3 | **7** |

The only prediction not confirmed: E28's spiral trunk (3 of 8).

## Reading

1. **Attributes change as discrete, nameable events that repeat at almost every seed.** An edit does not blur a picture;
   it switches particular attributes on or off: copper eyes 8 → 0 (E14, P01), clay 8 → 0 and a second figure 0 → 8
   (P01), big black pupils 0 → 7–8 (E06, E14, E28), water 0 → 6 (E28), an art-deco panel 0 → 8 (E06, P01).
2. **Three kinds of change, by edit:**
   * **adds without removing** — E28 (pupils, water, a darker background) and E06 on the robot (pupils): every
     stated attribute kept;
   * **replaces a stated attribute** — E14 on the robot (copper eyes → black pupils, 8 of 8);
   * **moves a stated attribute elsewhere** — P01 on the robot ("clay" leaves the robot for a second figure),
     E06 and P01 on the dagger (art-deco gold onto a background panel; the dagger's own decorations drop to 4 of 8
     with P01).
3. **Controls held:** red leaves and watercolour 8 of 8 everywhere.
4. **The same edit does different things on different subjects** (E06: pupils on the robot, a deco panel on the dagger,
   nothing countable on the tree), consistent with C104–C114: the effect is per edit × subject.

## Limits

The predictions came from the same pictures (C114 sheets, non-blind): this shows the reading is not driven by knowing
the condition, it does not replicate it on new pictures. Alessandro had seen those sheets; one observer; 8 seeds;
answers to the robot pupils question before the clarification may have counted the small figure (P01 3 of 8).
