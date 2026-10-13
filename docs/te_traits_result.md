# C75 result, part A — what a text-encoder edit costs the character (blind labels on the C74 ladder)

* **Pre-registration:** `docs/prereg_te_traits.md` (amendments 1 and 2).
* **Labels:** mine, blind to edit and dose, one question at a time, committed as downloaded
  (`data/te_traits_alessandro.csv`, 3,938 answers, none missing).
* **Tally:** `experiments/te_traits_tally.py`, outputs `data/te_traits_tests.csv` and `data/te_traits_by_picture.csv`.
* **Exploratory checks:** `experiments/te_traits_explore.py`, output `data/te_traits_explore.csv`.
* **Part B is not labelled yet.** The control with random pushes of the same size, which decides whether these costs
  belong to the edit or to any push of that size, is still open.

## Tests

| test | value | rule | verdict |
|---|---|---|---|
| T1 retention falls with dose | median Spearman −0.89 over 18 strips | ≤ −0.50 | **supported** |
| T2 traits lost before the style changes (L06, L14) | traits first in 11 of 11 strips | ≥ 2/3 | **traits go first** |
| T3 the L28 control costs traits without changing style | mean R at 1.00 minus at 0.10 = −0.07 | ≤ −0.15 | inconclusive |
| T4 unnamed drift toward lighter skin | lighter in 52 of 53 skin changes (0.98); lighter majority for 2 of 3 characters | ≥ 0.80 and ≥ 2 characters | **supported** |
| Reliability gate | Cohen κ 0.93 on 325 repeat pairs | ≥ 0.60 | passed |

* On the repeats, skin and person agree in 23 of 24 each.
* The trait disagreements are on the dwarf's eyebrow scar (3) and stern expression (2), and on single answers for
  six other traits.

## Retention by dose

Retention R is the share of the traits present in the original that are still present.

| edit | 0.10 | 0.40 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|
| L06 MLP | 1.00 | 0.96 | 0.83 | 0.76 | 0.70 | 0.65 | 0.52 |
| L14 MLP | 0.97 | 0.94 | 0.84 | 0.77 | 0.77 | 0.66 | 0.63 |
| L28 MLP | 1.00 | 0.97 | 0.97 | 0.96 | 0.96 | 0.95 | 0.93 |

* Under L06 and L14 the character loses about a sixth of its traits by d = 0.60. This is before any strip changes
  style (C74: none below 0.70). By full dose it has lost a third to a half.
* L28, which never changes style, loses almost nothing (0.93 at full dose). C74's free notes said that L28 lost traits
  in 4 of 6 strips. Blind, that is true only for the half-orc's orc features (from 0.60–0.70 on both seeds) and for
  single traits at full dose.

## What T2 rests on, and a stricter check

**Why T2 leans toward the traits by construction.** T2 compares two instruments:

* the C74 style onset, one judgement per picture, side by side and not blind;
* the trait onset, the first dose from which at least one of 11–14 blind yes/no answers stays lost.

A criterion built on many answers detects smaller events, so it is expected to fire earlier.

**The stricter check (exploratory).** I recomputed the onset as the first dose from which R stays ≤ 0.85, i.e. about
two traits lost:

* traits first in 8 of 11 strips;
* style first in 1 (the dwarf under L14 at seed 3316624);
* ties in 2.

That still clears the 2/3 bar. The ordering survives a less sensitive criterion, but with a smaller margin.

## What is lost

**The pre-registered prediction about rare traits does not hold as stated.**

* **The elf's pointed ears are never lost.** The half-orc's tusks cannot be lost: the originals do not have them.
* **The first traits to go are expressions and judgements of degree:**
  * the elf's smirk (median first loss 0.25);
  * androgynous presentation (0.33);
  * the dwarf's middle age (0.55).
* **Then the race and the costume:**
  * the half-orc stops reading as a half-orc (0.60), losing her warrior knot (0.60), undercut and scale collar (0.65);
  * the dwarf loses her braids (0.70) and her armour (gorget, gambeson, brass collar; 0.75–0.90).

**At full dose:**

* **L06:** the dwarf loses her armour and braids, the elf their amber eyes, smirk, undercut, cheekbones and youth, and
  the half-orc her knot, undercut, collar, jack, youth and orc features.
* **L14:** the dwarf loses her copper hair and is no longer read as female at either seed; the elf loses androgyny,
  cheekbones and tunic; the half-orc loses her knot, undercut, collar, youth and orc features.

## Skin and person

**Skin.**

* Every change of skin tone but one goes lighter: the half-orc 33, the elf 19, one darker for the elf under L06.
* The dwarf's skin never changes.
* Under L28 the elf's skin takes "another hue" 11 times (the green face of C74).
* The prompts name no skin tone, so this is a drift from the original picture, not a failure to follow the prompt.
  Its direction is one-sided.

**Person.** "Not the same person as the reference" holds for:

* 50 of 72 edited pictures under L06;
* 42 of 72 under L14;
* 30 of 72 under L28.

Even the control edit changes who is drawn in four pictures of ten, while keeping most of the listed traits.

## The originals do not satisfy their prompts

Fidelity F is the share of asked traits present, on the unedited pictures:

* **Elf:** 1.00 at both seeds.
* **Half-orc:** 0.77 at both seeds. No tusks, no dirt smudges, no snarl.
* **Dwarf:** 0.71 and 0.64. Not read as a dwarf rather than a human woman, no scarred wide nose, no eyebrow scar, not
  stern, and at one seed not brown-eyed.

The model leaves out the same traits at both seeds. Part B's eight plain seeds will say whether these are fragile at
baseline.

## What this changes

* **The first cost of these text-encoder edits is the character, not the style.**
  * Under L06 and L14, traits fall steadily with dose (T1).
  * They start to go well before the style moves (T2), and this survives a stricter criterion.
  * C74's free-text impression holds blind, with high agreement between repeats.
* **The drift of what the prompt does not name has a direction: lighter skin**, in 52 of 53 changes (T4).
  * This matches what audits of text-to-image models report about their defaults (Luccioni et al. 2023, "Stable
    Bias"; Bianchi et al. 2023).
  * Here it appears as what is left when the conditioning is weakened.
* **Not yet shown: that this belongs to the edit.** Part B compares the same doses with random pushes of the same size.
  If those cost the same traits and the same skin, the right reading is that these traits are fragile to any push,
  not that these edits target them.
* **T3 is inconclusive.** The control edit costs few listed traits. The C74 claim that L28 "loses traits in 4 of 6
  strips" is mostly the half-orc's race and the elf's green face.

## Limits

* **One labeller,** who built the edits and had seen every C74 strip. Blindness to dose and edit reduces, but does
  not remove, memory.
* **Three characters and two seeds.** The pictures of one strip are not independent.
* **Some traits are judgements of degree.** Smirk, androgyny, age and "reads as a dwarf" are among the earliest losses
  and among the less repeatable answers (the dwarf's scar and sternness).
* **T2 compares a blind multi-item measure with a non-blind single judgement.** See the stricter check above.
* **"Click what is missing" was replaced by explicit yes/no for every trait** (amendment 1). So unnoticed absences
  are not counted as present by default.
