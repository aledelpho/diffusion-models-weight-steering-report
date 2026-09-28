# `Block_6 pos` does not desaturate — it moves the colour off the object

**Date**: 2026-09-28 · **Found by**: comparing the whole-frame chroma in
`data/retro_texture_axes.csv` with the object-restricted chroma in `data/colour_chroma_audit.csv`,
which the corpus-wide re-measurement made possible · **No render.**

---

## 1. The discrepancy

The same condition, the same corpus, two ways of averaging saturation:

| condition | chroma, whole frame | chroma, object only |
|---|--:|--:|
| `Block_1 pos` | 1.348 | 1.308 |
| `Block_3 pos` | 1.570 | 1.563 |
| `Block_5 neg` | 1.624 | 1.610 |
| `Block_6 neg` | 1.814 | 1.815 |
| **`Block_6 pos`** | **1.488** | **0.726** |

Eleven of twelve group-arm conditions agree between the two within about 0.2. **`Block_6 pos`
disagrees by a factor of two and in direction.**

## 2. What it is

Splitting the frame into the object and everything outside it, on the leaf corpus at dose 0.200:

| condition | chroma on the object | chroma on the **background** |
|---|--:|--:|
| **`Block_6 pos`** | **0.726** | **12.519** |
| `Block_6 neg` | 1.815 | 1.692 |
| `Block_4 neg` | 0.927 | 1.335 |

**`Block_6 pos` multiplies the background's chroma by twelve and a half while taking 27 % off the
object's.** The background of that corpus is a plain light grey by construction, so this is colour
appearing where there was none — and the object losing it at the same time.

It is not a saturation knob. It is a **redistribution**: colour leaves the content and arrives in
the empty field around it.

`Block_6 neg` is the ordinary case — object and background both rise, together (1.815 and 1.692).
`Block_4 neg` is a mild version of the same redistribution as `Block_6 pos`.

## 3. Why this ties three separate readings together

* **The band signature.** `Block_6 pos` adds energy peaking at 4–8 px
  (`retro_mappa_reading_result.md` §3). That texture is the curl field seen at 1:1 in
  `style_damage_frontier.md` §7, and it covers the whole frame — including the parts that had
  nothing in them. The chroma it carries is what raises the background by ×12.5.
* **The coherence collapse at 0.200.** The same field is what drives `Block_6 pos` from 1.009 at
  dose 0.120 to 0.927 at 0.200 (`retro_mappa_reading_result.md` §1). The knee and the
  redistribution are the same event.
* **The taxonomy.** What Alessandro called "very strong grain" on the positive arm is energy added
  at 4–8 px carrying chroma into empty regions. Two observations, one mechanism.

## 4. What it scopes

`colour_gate_and_chroma_audit.md` §6 reported `Block_3` and `Block_6` as **antisymmetric chroma
knobs**, 18 of 18 cells each, p = 1e-5. That measurement is object-restricted, and it stands as
measured. **But its name was wrong for one of the two arms**: on the whole frame `Block_6` reads
1.488 / 1.814 — both arms up, no antisymmetry at all. The antisymmetry is a property of the
*object's* chroma, not of the image's, and for `Block_6 pos` the object loses what the background
gains.

The claim is therefore restated, not withdrawn: **`Block_6` moves object chroma antisymmetrically,
and on the positive arm it does so by moving the colour out of the object rather than by removing
it.** `Block_3` is unaffected — its two measures agree to 0.007.

That distinction cannot be made on a corpus without an isolated object, which is every other bench
in this project. **Any chroma reading taken on a full scene is a whole-frame reading and cannot
tell removal from redistribution.**

## 5. Limits

One corpus, one dose, one arm carrying the effect. The background of the leaf bench is a flat grey
by construction, which is what makes a ×12.5 possible and also what makes it unrepresentative: a
scene with a busy background has no empty field for colour to arrive in. Whether the same
redistribution happens there is untested, and it is the thing to ask the comic prompts — which
needs an object mask on a full scene, which this project does not have.
