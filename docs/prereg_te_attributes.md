# Pre-registration C115 — which attributes an edit adds, moves or removes

Written 2026-10-29 by Claude, before any C115 label. Script: `experiments/te_attributes.py`. No new render: C114's 120
pictures (3 prompts × plain and 4 edits × 8 seeds). Agreed by Alessandro ("Va bene, proviamo").

## 1. Why

C114's "kept" question was too coarse. Reading the sheets (non-blind) Claude saw attributes lost (copper eyes, robot E14
and P01), moved ("clay" to a second figure; art-deco gold from the inlays to a background panel) or added (water under
the tree, big black pupils). This pass asks one question per attribute, **per picture, conditions hidden**, to see
whether that reading holds when nobody knows which edit made the picture.

## 2. Pages

One page per prompt (`occhio_C115_<prompt>.html`, key `data/te_attributes_key.csv`, seed 11515): the 40 pictures in
random order, plain and edits mixed, one picture per card at large size, 4 repeats per page (132 pictures). Answers
*sì / no / non so*.

* Robot: copper eyes? clay (not metal)? a second figure? big black pupils?
* Tree: water at the base? trunk forms a spiral or curl? red leaves? watercolour?
* Dagger: golden geometric decorations on the blade or handle? an art-deco panel or background behind it? dark
  background? upright, vertical, centred?

## 3. Predictions (from Claude's non-blind reading, fixed now) and rules

Count of *sì* over the 8 seeds, edit minus plain; a change is **confirmed** when it is ≥ 5 in the predicted direction.

| prompt | attribute | edits | direction |
|---|---|---|---|
| robot | copper eyes | E14, P01 | lost |
| robot | clay | P01 | lost |
| robot | second figure | P01 | added |
| robot | big black pupils | E06, E14, E28 | added |
| tree | water | E28 | added |
| tree | spiral trunk | E28 | added |
| dagger | art-deco panel | E06, P01 | added |
| dagger | dark background | E06, P01, E28 | added |
| dagger | upright, centred | E06, P01 | added |

1. **At least 70 % of the 16 predictions confirmed** → *the reading holds blind*; otherwise *it does not*.
2. Reported: changes ≥ 5 that were not predicted; the full table of *sì* per attribute and condition (red leaves,
   watercolour and golden inlays are expected unchanged — checks); test–retest on the repeats.

## 4. Limits

The predictions come from the same pictures (this checks the reading, it does not replicate it); Alessandro has seen
the non-blind sheets and may recognise pictures; one observer; 8 seeds per cell.
