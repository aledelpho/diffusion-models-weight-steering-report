# C75 result — what a text-encoder edit costs the character (blind labels; part A on the C74 ladder, part B2 against random pushes)

* **Pre-registration:** `docs/prereg_te_traits.md` (amendments 1–4).
* **Labels:** mine, blind to edit and dose, one question at a time, committed as downloaded
  (`data/te_traits_alessandro.csv`, 3,938 answers, none missing).
* **Tally:** `experiments/te_traits_tally.py`, outputs `data/te_traits_tests.csv` and `data/te_traits_by_picture.csv`.
* **Exploratory checks:** `experiments/te_traits_explore.py`, output `data/te_traits_explore.csv`.
* **Part B2** (random pushes of the same size, plain portraits at eight seeds) was labelled by a second person who had
  seen none of the pictures and did not know what the study is about. See [Part B2](#part-b2--the-control-with-random-pushes)
  at the end.

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
* **It belongs to the edit, not to the size of the push.** Part B2, labelled by someone else, finds random pushes of
  the same size costing far fewer traits, and almost never changing the skin.
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

## Part B2 — the control with random pushes

* **Labels:** a second labeller, blind, neutral instructions, committed as downloaded (`data/te_traits_B2_rater2.csv`,
  2,245 answers, none missing).
* **Tally:** `te_traits_tally.py --part B2`, output `data/te_traits_B2_tests.csv`.
* **Exploratory breakdowns:** `experiments/te_traits_explore_B2.py`, output `data/te_traits_B2_explore.csv`.

| test | value | rule | verdict |
|---|---|---|---|
| B1 random minus real retention, 36 matched cells | pooled +0.18; token +0.20; permuted +0.17 | ≥ +0.15, both variants in the same band | **the edit costs more traits than its size** |
| Reliability, her repeats | κ 0.98 on 162 pairs | ≥ 0.60 | passed |
| Agreement with me on the shared pictures (reported) | κ 0.83 on 566 pairs; 0.85 without e_androgynous | — | — |

### By edit and dose (reported)

Retention against the original, her labels.

| | real | token | permuted |
|---|---|---|---|
| L06, d = 1.00 (6 cells) | 0.48 | 0.89 | 0.87 |
| L14, d = 1.00 (6 cells) | 0.63 | 0.95 | 0.94 |
| L28, d = 1.00 (6 cells) | 0.97 | 0.92 | 0.83 |
| all, d = 0.85 (9 cells) | 0.80 | 0.97 | 0.94 |
| all, d = 0.70 (9 cells) | 0.82 | 0.97 | 0.97 |

* **L06 and L14:** random pushes of the same size keep about nine traits in ten, while the real edit keeps half to two
  thirds.
* **L28 goes the other way:** its real edit keeps 0.97, and its permuted random push costs more (0.83). This matches
  C72, where L28's random pushes switched the genre and the real edit did not.
* **What "edit costs more" means here.** The pooled verdict is carried by L06 and L14. The finding is that **each edit's
  direction decides what it costs**, not that every edit costs more than noise.
* **At 0.70 and 0.85** the gap is already there for L06 and L14: real 0.69–0.78 against random 0.93–1.00.

### Skin (reported)

Among pictures whose skin changed:

* **real edits:** lighter in 14 of 14;
* **token random pushes:** lighter in 2 of 3;
* **permuted random pushes:** lighter in 3 of 3.

Random pushes rarely change the skin at all. The drift toward lighter skin found in part A belongs to the real edits
L06 and L14.

On the 36 edited pictures we both labelled:

* we agree on skin in 29;
* both of us say "lighter" for 12 of them.

### What the unedited model draws (B0, eight seeds)

* **Five asked traits are never drawn at any seed, by her labels:**
  * the dwarf's scarred wide nose and eyebrow scar;
  * the half-orc's tusks, dirt smudges and snarl.
* **These are fragile at baseline.** Without them, T1 (median ρ −0.89) and T2 (11 of 11) are unchanged.
* **The fragile traits are not what the edits remove.** They were never there to lose.

### Agreement between the two labellers

The lowest agreement is on:

* "reads as a dwarf" (8 of 14);
* the dwarf's stern expression (9 of 14);
* the dwarf's braids (9 of 14);
* the half-orc's youth (9 of 14).

She answered "reads as a dwarf" yes on every plain portrait; I answered no on the originals. Most other traits agree
in 13 or 14 of 14.

## What C75 changes, all together

* **The first and largest cost of the L06 and L14 text-encoder edits is the character the prompt asks for.**
  * Traits fall with dose and go before the style.
  * Random pushes of the same size cost about a fifth as much.
  * This was found by two labellers, one of whom knew nothing of the study.
* **The drift of what the prompt does not name has a direction, lighter skin, and it comes with the edit.** Random
  pushes of the same size almost never change the skin.
* **Not every edit does this.** L28 keeps the character better than random pushes of its size. Like the destination
  of the genre switch (C72, C73), the cost depends on the edit's direction.
* **The unedited model already misses some traits at every seed:** tusks, scars, the snarl. A text-encoder edit
  cannot be blamed for those, and they are excluded by the B0 check without changing any verdict.

## Limits of part B2

* **A short set:** 1.00 for every cell, but 9 cells each at 0.70 and 0.85 (amendment 3), chosen after I had seen part
  A.
* **Two questions were reworded for her** (amendment 4), so the agreement on androgyny and person is not comparable.
* **Two labellers, three characters, two seeds, one kind of edit.**
