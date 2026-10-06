# C57 — a second half-formed hood: does C56 replicate?

2026-10-06. Written **before anyone has looked at the scout renders**; Claude has not opened the
folder. Confirmatory for the predictions below; everything else descriptive.

## Scout (renders launched by Alessandro, 2026-10-06)

30 baselines of the archer prompt (`P3_archerforest`), 30 different seeds, C47 settings, no tuner,
in `Text2Img\scratch_hood_baselines`. The seeds are recorded from the file names into
`data/hood_scout_seeds.csv` when the folder is read.

1. **Base rate.** All 30 are labelled blind by Alessandro with the C54 labels (*completo (in testa)*
   / *abbassato* / *a metà* / *assente* / *non riesco a dirlo*), in random order, 6 of them shown
   twice (self-agreement ≥ 5 of 6 required). Reported: how many of 30 are *a metà* — how common
   this watershed is for this prompt.
2. **Selection rule, fixed now.** The seeds labelled *a metà* (on both showings if repeated) are
   eligible. If there are one or two, all are used. If more than two, two are drawn at random
   (numpy `default_rng(57)` over the sorted list of eligible seeds). If there are none, C57 stops
   here and reports the base rate.

## Ladder on the selected seed(s) (renders need Alessandro's authorisation)

Blocks 00, 10, 20, 23 (as in C56), both signs, doses 0.01, 0.02, 0.04, 0.08: 32 renders per seed,
plus one baseline re-render per seed as reproduction check. Labelled blind by Alessandro, same
labels, 6 repeats per seed (≥ 5 of 6).

## Predictions from C56 (decisive, per seed)

* **P1 — nothing at 0.01:** at dose 0.01 the label equals the baseline's (*a metà*) on at least 7 of
  the 8 block-sign lines.
* **P2 — negative tips early:** pushed negative, at least 2 of the 4 blocks are labelled other than
  *a metà* at a dose ≤ 0.04.
* **P3 — the sign matters:** for at least 3 of the 4 blocks, the threshold pushed positive is higher
  than pushed negative ("none within 0.08" counts as higher; equal thresholds do not count).
* **P4 — the direction decides how it falls:** among all labels that differ from *a metà*, the share
  of *completo (in testa)* is higher on the negative side than on the positive side.

Each prediction is reported as held / not held per seed; C56's pattern **replicates** on a seed if
P1–P4 all hold there. One seed failing is reported as such; the claim on page 22 stays "one ridge"
until a second seed replicates.

**Descriptive:** whether every response is a step; Spearman between threshold and the block's
content change at equal dose (`data/atlas_equal_dose_content_change.csv`), as in C56.
