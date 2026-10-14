# Pre-registration C76 — when a text-encoder edit loses a colour, does the colour move or vanish?

Written 2026-10-14, **before any C76 label.** No renders: C76 uses the C74 ladder and the C75 part B2 pictures.

* Code: `experiments/te_bind_page.py` (key, schedule, page) and `experiments/te_bind_tally.py` (rules, with a
  self-test). Both are written after this document and before any label.
* Labelling page: `Text2Img\_grid_viewer\te_bind\index.html`.

## Why

C75 showed two things:

* the L06 and L14 edits cost the character traits the prompt asks for, more than random pushes of the same size;
* the skin drifts lighter.

Two readings explain this, and C75 cannot tell them apart.

* **Broken links.** The edit breaks the binding between an attribute word and its object. The attribute survives,
  but lands on the wrong part: copper on the skin instead of the hair, green on the face instead of the hood. C74
  showed one case under L28: the elf's face turns green, the colour of the hood.
* **Defaults win.** The edit amplifies what one layer writes (each matrix × (1 + d), roughly up to ×8 at full dose).
  The specific, composed content built by later layers is drowned. The attribute does not move: it vanishes, and the
  object takes the model's default.

The two readings make different predictions about a lost colour. Under broken links, the colour reappears elsewhere
more often than it does when nothing is lost. Under defaults win, it does not.

Attribute binding is a known failure of text-to-image models, measured with attributes swapped between objects
(T2I-CompBench; Magnet). Here the prompt is fixed, and the question is what an edit of the text encoder does to the
bindings already in it.

## Material

**Pictures: 312 unique pictures.**

* the 222 pictures of C75 part A: 6 originals and the C74 ladder of L06, L14 and L28 at 12 doses;
* the 72 random-push pictures of C75 part B2 (token and permuted, at 0.70, 0.85 and 1.00);
* the 18 plain portraits of B0.

**Repeats:** 4 per character, at least one original each, shown twice for test–retest.

**Who labels:** the second labeller of C75 (amendment 3 there).

* She has not seen the C75 results, and she knows nothing of the hypotheses.
* The page gives the same neutral instructions as C75 B2.
* If another person labels, the commit of the labels says so. Nothing else changes.

## Questions (fixed now)

Six colour words of the prompts, two per character, each bound to one object. They were chosen because:

* the colour is distinct;
* the object is clearly visible in a frontal portrait;
* a misplaced colour is easy to see on the body.

Each word gets two yes/no questions:

* **on:** is the colour on its object?
* **off:** does the colour appear on the body (skin, hair or eyes) where the prompt does not put it?

| id | character | prompt words | on | off |
|---|---|---|---|---|
| copper | D1 | "thick braided copper hair" | I capelli sono color rame? | Vedi del color rame sulla pelle o negli occhi? |
| navy | D1 | "a navy blue gambeson" | La giubba imbottita sotto l'armatura è blu navy? | Vedi del blu navy sulla pelle, sui capelli o negli occhi? |
| amber | E2 | "sharp amber eyes" | Gli occhi sono color ambra? | Vedi del color ambra sulla pelle o sui capelli? |
| green | E2 | "dark forest green hooded leather cowl" | Il cappuccio è verde scuro? | Vedi del verde sulla pelle, sui capelli o negli occhi? |
| burgundy | O4 | "a burgundy quilted jack" | La giacca imbottita è bordeaux? | Vedi del bordeaux o rosso scuro sulla pelle, sui capelli o negli occhi? |
| bronze | O4 | "oxidized bronze scale-mail collar" | Il colletto a scaglie è color bronzo? | Vedi del color bronzo sulla pelle, sui capelli o negli occhi? |

**Left out, and why:**

* Lips are excluded from every "off" question, because they are often reddish anyway.
* Metals that look alike are not asked against each other (steel, brass, bronze, copper on the armour): misplacement
  between them cannot be judged reliably.
* Black is excluded: it is everywhere in inked comics.

**Answers:** right arrow = yes, left arrow = no, down arrow = cannot tell, Backspace = back. It is the C75 protocol:

* one question at a time over every picture of one character;
* shuffled order with seed 7478;
* no dose, edit or seed shown;
* no reference picture.

About 1,300 answers.

## Measures

The unit is one picture × one colour word. Answers come from the first showing; "cannot tell" is left out.

**Lost.** An edited picture whose original (same character and seed) has the colour on its object ("on" = yes in
the original's labels), while the picture itself has "on" = no.

**Kept.** An edited picture with "on" = yes, for the same original condition.

Three off-target rates:

* **L_lost:** share of lost cases with "off" = yes.
* **L_kept:** the same share among kept cases.
* **L_0:** the same share among the plain pictures: the 6 originals and the 18 B0 portraits, 24 per word in all.

## Tests (thresholds fixed now)

| test | question | measure | rule |
|---|---|---|---|
| M1 | when a colour is lost under a real edit, does it move or vanish? | real-edit pictures (L06, L14, L28, every dose): L_lost against max(L_kept, L_0) | at least 10 lost cases, L_lost ≥ 0.30 and L_lost − max(L_kept, L_0) ≥ 0.20 → **the colour moves (links break)**; L_lost ≤ max(L_kept, L_0) + 0.05 → **the colour vanishes (defaults win)**; otherwise inconclusive; fewer than 10 lost cases → inconclusive |
| M2 | do real edits misplace colours more than random pushes of the same size? | off-target rate over all real-edit pictures at d = 0.70, 0.85, 1.00, against the random-push pictures (token and permuted pooled) at the same cells | difference ≥ +0.15 → **edits misplace more**; within ±0.05 → **no difference**; ≤ −0.15 → **random pushes misplace more**; otherwise inconclusive |

**Reliability gate.** Cohen's κ on the repeats, over the "on" and "off" answers given yes or no both times. If
κ < 0.60, the tests are reported but no claim built on them may be stated as "holds".

## Reported, deciding nothing

* M1 by edit, by colour word and by dose band (≤ 0.50, 0.60–0.80, ≥ 0.85).
* The off-target rate of each colour in the originals and B0: what the unedited model already does.
* The L28 control on the elf's green, the case that motivated the question.
* Agreement between the "on" answers here and the trait answers of C75 part A on the same pictures, for the four
  words that overlap: copper (`d_copper`), amber (`e_amber`), green (`e_cowl`, which also asks for leather and a
  hood) and burgundy (`o_jack`).

## What each outcome would mean

**M1 "moves":** at least part of what the edits cost is misbinding.

* The attribute survives in the conditioning, but is no longer attached to its object.
* This would fit the C68 finding that edits push small clause-sized regions of the prompt.

**M1 "vanishes":** the evidence favours "defaults win".

* The edit drowns the specific content, and the object goes back to what the model draws by default.
* Together with C75, the picture would be one of amplified generic content, not scrambled links.

**M2** says whether misplacement, if any, belongs to the edit or to any push of that size.

## Limits

* Six colour words, three characters, two seeds (eight for the plain pictures).
* Colour names are judged by eye, and similar hues blur: copper and bronze against tanned skin, amber against
  light-brown hair.
* A colour can appear on the body for reasons other than misbinding. For example, warm lighting can tint the skin
  bronze. L_0 and L_kept are there to absorb this.
* Lost cases are not chosen in advance. Their number depends on the labels; below 10, M1 is inconclusive.

## Amendment 1 (2026-10-14, before any label is kept)

While trying the page, Alessandro found two problems. Both are fixed before anyone labels.

* **Natural skin tones read as warm colours.** A tanned or flushed skin can look copper, amber or bronze, so the
  "off" questions as written would partly measure skin tone. Every "off" question now asks for a tint that a real
  person would not have ("La pelle o gli occhi hanno una tinta color rame che una persona normale non avrebbe?").
  The instructions add that a tan, a red cheek or freckles do not count.
* **The object can be gone.** For example, a photographic render with a shirt instead of armour and gambeson. A "no"
  there would count as a lost colour even when the colour is still on the garment in its place. The "on" questions
  for clothing now say "(or the garment in its place)". The instructions add the rule: judge what is in the
  object's place; "cannot tell" only if that area is cut off or covered.

**What does not change:** the measures, the rules, the key and the schedule.

**The page.** It is rebuilt with a new storage key (`te_bind_v2`), so that answers given to the first wording are not
carried over. Any answers given on the first page were a trial and are not used.

## Withdrawn (2026-10-14, before any label)

Alessandro withdrew C76 before any picture was labelled. On existing pictures the "off" questions cannot be defined
consistently: a colour named in the prompt can reach the body in ways a real person could also have (copper or bronze
skin, blue eyes from "navy"). No wording separates misbinding from natural variation. The binding question will be
asked again with renders made for it: prompts whose colours cannot belong to a body, with swapped controls. No result
of C76 exists. The key, schedule, page and tally stay in the repository as a record of the attempt.
