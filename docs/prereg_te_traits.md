# Pre-registration C75 — what a text-encoder edit costs the character: prompt traits, blind, against dose and against random pushes

Written 2026-10-13, **before any C75 label, key or render.**

* **Part A** uses only the 222 existing C74 renders.
* **Part B** needs 128 new renders, which Alessandro has not yet authorised. Its rules are fixed here so that they
  cannot be chosen after Part A.
* The tally (`experiments/te_traits_tally.py`, with a self-test) is written after this document and before any
  label. It may only compute what is fixed here.

## Why

C74 found that the style of a portrait holds until d ≈ 0.70 and that no picture breaks up to full dose. What does move
early is the character. In 7 of 10 changing strips a trait was lost before the style changed, or at the same dose. The
L28 control never changes style, yet lost traits in 4 of 6 strips. Alessandro proposed taking this loss, not the
style, as the measure of what a text-encoder edit costs.

Three weaknesses of the C74 observation have to be fixed before that can be a claim:

1. **Two kinds of trait were mixed.**
   * Traits the prompt asks for: the half-orc's tusks, the dwarf's copper hair.
   * Features of the original picture that the prompt does not name: the elf's skin tone, the half-orc's grey skin
     and pointed ears.

   Losing the first kind is a failure to follow the prompt. Losing the second kind is a drift from the original.
2. **The original does not satisfy the prompt either.** At seed 2645751 the original half-orc shows no tusks; they
   appear at d = 0.40. Loss has to be measured against what the original actually shows.
3. **No control.** C72 showed that random pushes that vary per token change the genre almost as often as real edits.
   If random pushes of the same size also cost the same traits, the loss reflects how fragile some traits are, not
   what the edit does.

The traits were noted in free text, and the page was not blind. Unlike style along a ladder, whether a trait is
present can be judged on one picture alone. So it can be labelled blind.

## Existing methods this follows

Checking prompt fidelity with a list of yes/no questions derived from the prompt is the scheme of TIFA (Hu et al.,
2023), Davidsonian Scene Graph (Cho et al., 2024), GenEval (Ghosh et al., 2023) and VQAScore (Lin et al., 2024).
Those methods answer the questions with a vision-language model. Here a human answers them; the questions are fixed in
advance from the prompt's words.

An automatic scorer is not part of C75. If C75 gives a clear result, validating a vision-language model against these
labels is a separate, later test.

## The trait lists (fixed now)

Every trait comes from a phrase of the prompt and is judged as **present / absent / not visible**. The three prompts
share the frame "Western comics style, close-up portrait, frontal view … white background, simple background". Style
is left out (C74 measured it). The frame gives two common traits.

**Common to all three**

| id | trait | prompt words |
|---|---|---|
| c_frontal | close-up portrait seen from the front | "close-up portrait, frontal view" |
| c_whitebg | plain white background | "white background, simple background" |

**D1 — dwarf paladin**

Prompt: "female paladin mountain dwarf, middle-aged, resolute stern expression, thick braided copper hair pinned back,
dark brown eyes, a battle-scarred wide nose, polished steel gorget over a navy blue gambeson, high brass collar, a
vertical scar running through one eyebrow".

| id | trait |
|---|---|
| d_female | reads as a woman |
| d_dwarf | reads as a dwarf (broad, heavy features), not as an ordinary human |
| d_middleaged | middle-aged, not young |
| d_stern | stern or resolute expression |
| d_copper | copper or red hair |
| d_braids | thick braided hair, pinned back |
| d_browneyes | dark brown eyes |
| d_nose | wide nose with scars |
| d_browscar | vertical scar through one eyebrow |
| d_gorget | polished steel gorget (metal neck armour) |
| d_navy | navy blue gambeson (padded cloth) |
| d_brass | high brass collar |

**E2 — elf rogue**

Prompt: "non-binary rogue wood elf, young adult, smug lopsided smirk, undercut asymmetrical raven hair, sharp amber
eyes, prominent cheekbones, dark forest green hooded leather cowl, brass buckles, high-collared charcoal tunic, a
single dangling feather earring".

| id | trait |
|---|---|
| e_ears | pointed elf ears |
| e_androgynous | androgynous presentation, neither clearly a man nor clearly a woman |
| e_young | young adult |
| e_smirk | smug, lopsided smirk |
| e_undercut | asymmetrical undercut |
| e_black | raven, black hair |
| e_amber | amber eyes |
| e_cheeks | prominent cheekbones |
| e_cowl | dark green hooded leather cowl (hood up or down) |
| e_buckles | brass buckles |
| e_tunic | high-collared charcoal tunic |
| e_feather | a single dangling feather earring |

**O4 — half-orc fighter**

Prompt: "female fighter half-orc, young adult, fierce defiant snarl, shorn faded undercut with a tight black warrior
knot, piercing pale grey eyes, lower tusks jutting past chiseled lips, oxidized bronze scale-mail collar over a
burgundy quilted jack, fresh dirt smudges across the bridge of the nose".

| id | trait |
|---|---|
| o_female | reads as a woman |
| o_orc | reads as half-orc, not as an ordinary human (apart from the tusks) |
| o_young | young adult |
| o_snarl | fierce, defiant snarl |
| o_undercut | shorn, faded sides |
| o_knot | tight black warrior knot |
| o_greyeyes | pale grey eyes |
| o_tusks | lower tusks past the lips |
| o_scale | bronze scale-mail collar |
| o_jack | burgundy quilted jack |
| o_dirt | dirt smudges across the bridge of the nose |

That gives 14 asked traits for the dwarf, 14 for the elf and 13 for the half-orc.

**Unnamed features, judged against the original of the same character and seed**

| id | question | choices |
|---|---|---|
| skin | skin compared with the original | same / lighter / darker / another hue (green, grey, …) |
| person | the same person as the original | same / similar / another person |

A free-text note records anything new that the prompt does not ask for, such as the high oriental collar or the green
face.

## Part A — blind labels on the C74 renders

### Material

* **Pictures:** the 222 C74 pictures. That is 6 originals (3 characters × 2 seeds), 198 intermediate doses (18 strips
  × 11 doses) and 18 full-dose pictures.
* **Repeats:** 24 pictures are shown twice, for test–retest agreement. They are drawn at random with a fixed seed: 8 per
  character, at least one original among them. The second showing comes at least 60 items after the first.
* **Total:** 246 items.

### Page and key

**What each item shows:**

* Only an item number (`item 001` … `item 246`).
* Two pictures: the item and, beside it, the original of the same character and seed, labelled "riferimento".
* No edit, dose or seed is shown. The order is shuffled with a fixed seed (7475).

**What you answer per item:**

* **mancano:** buttons for the asked traits of that character plus the two common ones. You click every trait that is
  absent.
* **non si vede:** the same buttons. You click the traits that cannot be judged.
* **pelle** and **persona:** one choice each.
* A free-text note.

Any trait not clicked counts as present. An item counts as labelled when "pelle" is answered.

**The key:** `data/te_traits_key.csv` (item, file, character, seed, edit, dose, first_showing) is committed before the
page is opened. The labels are committed as downloaded (`data/te_traits_alessandro.csv`) before any count.

### Measures

For picture *i* (character *c*, seed *s*, edit *L*, dose *d*):

* **P₀(c, s):** the asked traits present in the original. "Not visible" in either picture removes that trait from
  the comparison for that picture.
* **Retention R(i)** = share of the P₀ traits still present in *i*. The originals have R = 1 by definition.
* **Fidelity F(i)** = share of all judgeable asked traits present in *i*, with no reference to the original
  (reported).
* **Additions:** traits absent in the original and present in *i*, such as the tusks at 0.40 (reported).
* **Sustained loss onset** of a strip: the lowest dose *d* such that R < 1 at *d* and at every higher dose. "Never" if
  there is none. A trait that flickers back resets the onset. This is conservative: it makes the loss look later.

Repeats use the first showing; the second is used only for agreement.

### Tests (thresholds fixed now)

| test | question | measure | rule |
|---|---|---|---|
| T1 | does retention fall with dose? | per strip, Spearman ρ between dose (12 doses, 0.10–1.00) and R; median over the 18 strips | median ρ ≤ −0.50 → **supported**; ≥ −0.20 → not supported; otherwise inconclusive |
| T2 | do traits go before style? | the 11 L06/L14 strips with a C74 style onset (`data/te_dose_alessandro.csv`, `cambia_da`, as downloaded): sustained loss onset vs style onset | onset earlier than the style in ≥ 2/3 → **traits go first**; later in ≥ 2/3 → **style goes first**; otherwise inconclusive. Ties and "never" count in the denominator, and for neither side |
| T3 | does the L28 control cost traits without changing style? | the 6 L28 strips: mean R at d = 1.00 minus mean R at d = 0.10 | ≤ −0.15 → **supported**; ≥ −0.05 → not supported; otherwise inconclusive |
| T4 | does the unnamed drift have a direction? | all edited pictures with skin ≠ "same": share "lighter" among lighter + darker | ≥ 0.80 with at least 10 changed pictures **and** lighter in the majority for at least 2 of the 3 characters → **toward lighter skin: supported**; ≤ 0.60 → not supported; fewer than 10 → inconclusive. "Another hue" is reported apart |

**Reliability gate.** On the 24 repeats, Cohen's κ over asked traits judged present or absent at both showings.

* If κ < 0.60, the tests are still reported, but no claim built on them may be stated as "holds".
* The agreement on skin and person is reported.

### Reported, deciding nothing

* R and F by edit and dose; the sustained loss onset per strip next to the C74 style onset.
* **Which traits go first,** per trait over all strips: the lowest dose at which each is lost. Prediction, not a test:
  rare or non-human traits (tusks, pointed ears, scar through the eyebrow) go before common ones (woman, black hair,
  white background). This is the reading suggested by Diffusion Lens, where rare concepts need more of the network.
* **The originals' fidelity:** how many asked traits the unedited model already misses at these two seeds.
* "Person": the share "another person" by dose and edit.
* The free-text notes on new elements.
* The C74 slip: the row L06 · half-orc · 3316624 has onset "never" but changes at 0.80. T2 uses it as downloaded,
  which leaves it out. The tally also reports T2 with that row read as 0.80.

## Part B — controls that need renders (only if authorised)

### B0 — the unedited model's own fidelity

* The three portraits, plain, at the six other seeds of the corpus (1618033, 1234567, 3141592, 2718281, 3605551,
  4123105): **18 renders.**
* **Reported:** the presence rate of every asked trait in the unedited model over 8 seeds. A trait present in fewer
  than half of the plain pictures is marked **fragile at baseline**. T1–T2 are re-reported without the fragile traits.

### B1 — random pushes of the same size

* **Material:** for L06, L14 and L28; the three characters; seeds 2645751 and 3316624; doses 0.70, 0.85 and 1.00.
* **Variants:** two random pushes from the `Krea2ConditioningPush` node (v2), each norm-matched per tap to that edit's
  real push at that dose:
  * `token`: Gaussian noise per token;
  * `permuted`: the real push with its channels permuted.
* **Renders:** 3 × 3 × 2 × 3 × 2 = **108 renders.**
* **Gate (2 renders):**
  * variant `zero` must be pixel-identical to the original;
  * variant `real` at L06 d = 0.85 must be pixel-identical to the C74 render.
* **Labelling:** blind, on a second page built the same way as Part A. It holds:
  * the 108 random-push pictures;
  * the 54 real-edit pictures at the same cells, shown again;
  * the 6 originals;
  * 12 repeats.

  Mixing the real-edit pictures into the same session keeps the comparison within one labelling session.

| test | measure | rule |
|---|---|---|
| B1 | mean R, random (token and permuted pooled) minus real, over the 54 matched cells | ≥ +0.15 → **the edit costs more traits than its size: supported**; ≤ +0.05 and ≥ −0.05 → **size alone**; ≤ −0.15 → **random pushes cost more**; otherwise inconclusive. If token and permuted fall on opposite sides of these bands, the verdict is **depends on the form of the push** (the C72 lesson) |
| B1-skin | share "lighter" among skin changes, random vs real | reported |

## What each outcome would mean

**T1 and T2 supported, B1 "edit costs more":** the first and main cost of these edits is the character.
* The edit erases what the prompt asks for before it touches the style, and more than its size alone would.
* Measuring text-encoder edits by style would then miss their main effect.

**T1 and T2 supported, B1 "size alone":** the traits are fragile to any perturbation of the conditioning.
* The edit costs them because it is large, not because of what it is.
* Rare traits would go first, under any edit.

**T2 "style goes first":** the C74 notes overstated the traits; style stays the better measure.

**T4 supported:** the drift of features the prompt does not name has a direction, toward lighter skin.
* That is a bias of the model's defaults, surfacing when the conditioning is disturbed.
* It is not a failure to follow the prompt, since the prompt names no skin tone.

## Limits

* **One labeller,** who built the edits and has seen every C74 strip. The page hides edit and dose but cannot erase
  memory. The repeats measure consistency, not bias.
* **Rows of pictures are not independent:** pictures of one strip share the character, the seed and most of the push.
  The tests are per strip or pooled over strips. The counts in T4 are pictures, which is why T4 also asks for
  agreement across characters.
* **Some traits are judgements of degree:** "middle-aged", "androgynous", "reads as a dwarf". They are kept because the
  prompt asks for them, and their agreement on the repeats is reported per trait.
* **"Click what is missing" invites misses.** An absence that is not noticed counts as present, which biases R
  upward. The repeats show how often this happens.
* **Three characters, two seeds (eight for B0), one kind of edit (MLP, three matrices).**

## Amendment 1 (2026-10-13, before any C75 label or render)

Alessandro reviewed the trait lists and asked for a faster, simpler protocol. Every change below was made before the
key was drawn and before any picture was labelled.

**Questions.**

* Every trait is now a direct yes/no question that repeats the prompt's words: "Il personaggio è femmina?"
  instead of "reads as a woman".
* The full list, in Italian (shown on the page) and English, with the prompt words behind each question, is
  `data/te_traits_questions.csv`. The trait ids and their number are unchanged: 14 for the dwarf, 14 for the elf and
  13 for the half-orc, including the 2 common ones.
* **Rule for compound questions:** answer yes only if everything the question says is true.
* **Rule for the dwarf:** a beard alone is not enough to answer no to "is female". C72 showed that the model draws
  female dwarves with beards.

**Answers.**

* Right arrow = yes, left arrow = no.
* Down arrow = "cannot tell", kept as an escape for traits that are hidden. It plays the role of "not visible" in
  the measures.
* Backspace goes back one step.

**Unnamed features as yes/no.**

* Skin becomes a chain of questions:
  1. "same colour as the reference?";
  2. if no, "lighter?";
  3. if no, "darker?"; no to both means another hue.

  The four categories of T4 are unchanged.
* Person becomes "the same person as the reference?" (yes/no). The "similar" choice is dropped.

**One question at a time (question-major).**

* The page asks one question over every picture of one character, then moves to the next question. This keeps a
  single criterion in mind and makes each picture one of 74 in a block, not a whole sheet to scan.
* **Order:** characters D1, E2, O4. Within each character, the trait questions come in a shuffled order, then skin,
  then person.
* **Pictures within a block:** shuffled; seed 7475 for everything.
* **The reference original** is shown only for skin and person. Trait questions show the picture alone, so that the
  answer is about the picture and not a comparison.
* **No item number is shown.** Picture files are renamed by item.

**Repeats.**

* The same 24 pictures (8 per character, at least one original each) are shown a second time in every block of
  their character.
* The second showing comes more than 30 positions after the first; a block has 82 positions.
* κ is computed over all trait blocks.

**Measures.**

* A strip whose retention never changes (Spearman undefined) counts as ρ = 0 in T1: no relation.
* "Cannot tell" at a dose is skipped when the sustained onset is computed.

**Files.**

* Key `data/te_traits_key_A.csv`.
* Schedule `data/te_traits_schedule_A.csv` (3,854 steps before the skin follow-ups).
* Page and key script `experiments/te_traits_page.py`.
* Tally `experiments/te_traits_tally.py`, with a self-test on a synthetic labeller.

All are committed before the page is opened.

**Part B is authorised** (Alessandro, 2026-10-13). B0 needs only 12 new renders, because seeds 3605551 and 4123105
already exist for the three portraits in `benchmark_portraits/phase_c`. With the 108 renders of B1 and the 2 gate
renders, the plan has **122 rows** (`data/te_traits_plan.csv`, `experiments/te_traits.py`).

* **Gate 1:** variant `zero` at L06 d = 0.85 must equal the plain portrait.
* **Gate 2:** variant `real` must equal the C74 render.

The Part B labelling page is built after the renders, with the same protocol. Its tally is added to
`te_traits_tally.py` before those labels, following the B1 rule fixed above.

## Amendment 2 (2026-10-13, after the Part B renders, before any Part B label)

The renders passed the gate (`docs/RENDERS_2026-10-13_te_traits.md`: both diffs 0, 122 of 122). I opened one contact
sheet to check that the files are valid pictures (`Text2Img\_grid_viewer\_c74_check\c75_b_check.jpg`). Nothing was
labelled or counted.

**The Part B page** (`Text2Img\_grid_viewer\te_traits_B\index.html`) uses the protocol of amendment 1. It has 186
pictures, 62 per character:

* the 2 originals;
* the 6 plain B0 portraits: the 4 new seeds plus 3605551 and 4123105 from `phase_c`;
* the 18 real-edit pictures at d = 0.70, 0.85 and 1.00;
* the 36 random-push pictures.

Changes from the text above:

* **Repeats.** There are 4 repeats per character (12 in all), as fixed above; at least one is an original.
* **B0 and the reference.** The B0 portraits have no reference of their own seed among the edited pictures. They are
  asked the trait questions only, not skin or person.
* **Files.** Key `data/te_traits_key_B.csv`, schedule `data/te_traits_schedule_B.csv` (3,066 steps before the skin
  follow-ups), seed 7476. The labels file is `te_traits_B_alessandro.csv`.

**Measures and rules** (`te_traits_tally.py --part B`, self-test on a synthetic labeller):

* **B1.** Retention is measured against the original as labelled in the same Part B session. The bands are
  "more" ≥ +0.15, "size" within ±0.05, "less" ≤ −0.15 and "mid" otherwise.
  * If token and permuted fall in two different bands, neither of them "mid", the verdict is "depends on the form
    of the push".
  * Otherwise the pooled difference decides.
* **B0.** Presence rate over the 8 plain pictures of each character, labelled in Part B (the 2 originals and 6
  plain). A trait with presence < 0.5 is fragile. T1 and T2 of Part A are re-reported without the fragile traits.
* **Reported in addition:** agreement across sessions on the same pictures (the originals and the real edits at
  0.70, 0.85 and 1.00, shown in both parts), as κ.

## Amendment 3 (2026-10-13, after the Part A tally, before any Part B label)

**What had happened before this amendment:**

* The Part A labels had been tallied (`docs/te_traits_result.md`). I had read the result; Alessandro had not.
* No Part B picture had been labelled.

**A second labeller.** Part B is labelled by a second person instead of Alessandro.

* She has seen none of these pictures. She does not know what the edits are, nor what the study is about.
* She is told only how to answer: a neutral instruction screen in Italian, with no mention of edits, doses or
  expectations.
* The B1 comparison (real edit vs random pushes at matched cells) is made within her labels, so the change of
  labeller does not touch it.
* The pictures shared with Part A (the originals and the real edits at the shared doses) give an **inter-rater**
  agreement in place of the cross-session one. It is reported as κ and decides nothing.

**A shorter set.** To shorten the session, the Part B page (`te_traits_B`, not labelled) is replaced by `te_traits_B2`:

* **Every one of the 18 cells at d = 1.00.**
* **One intermediate dose per cell:** 0.70 on one seed and 0.85 on the other. Which seed takes 0.70 alternates over
  the nine (character, edit) pairs (`b2_dose` in `te_traits_page.py`), so both doses meet both seeds.
  * The result is 9 cells at 0.70 and 9 at 0.85, against 18 at each before.
  * The 18 cells at 1.00 are unchanged.
* **The rest is kept:** the originals, the B0 plain portraits, 4 repeats per character, and the skin and person
  questions.
* **Size:** 132 pictures; 2,220 steps before the skin follow-ups, against 3,066.

**Why this choice, and its risk.** The choice of doses was made after I had seen the Part A result.

* It does not favour either arm of B1: real edits and random pushes keep the same cells.
* It favours d = 1.00, where Part A shows the largest loss under real edits. That gives B1 the most room to separate
  the two arms in either direction.
* Alessandro asked to keep some 0.70 and 0.85 pictures, so that the dose trend of B1 can still be described.

**Rules.**

* B1, B0 and their bands are unchanged. B1 pools every matched cell (36).
* By dose (0.70, 0.85, 1.00), the result is reported only.

**Files.**

* Key `data/te_traits_key_B2.csv`, schedule `data/te_traits_schedule_B2.csv` (seed 7477).
* Page `Text2Img\_grid_viewer\te_traits_B2\index.html`.
* Labels `te_traits_B2_rater2.csv`, committed as downloaded.
* Tally `te_traits_tally.py --part B2`, with a self-test.
