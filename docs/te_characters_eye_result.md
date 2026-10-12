# C65 — the eye pass (2026-10-12), before any measure

Descriptive; no decision rule of `docs/prereg_te_characters.md` uses these answers. Key
`data/te_characters_eye_key.csv` (committed before labels), labels `data/te_characters_eye_alessandro.csv`
(committed as downloaded, before counting and before the measures were computed), table
`data/te_characters_eye_joined.csv`, code `experiments/te_characters_eye_tally.py`.

**Change of meaning of one question, stated by Alessandro when he sent the labels.** The surface never broke,
so he used the "surface" scale (as / slight / medium / strong) for how far the picture stops following the
prompt — e.g. a coloured background where a white one was asked is *strong* degradation. In this pass that column
reads as **prompt-following loss**, not surface damage.

## Numbers

40 sheets (20 edits × 2 seeds) + 6 repeats. Six first showings have no answer to "same direction" (their
free texts are kept); one of them (L08 MLP−, 3316624) is answered on its repeat (*yes*).

* Repeats with both showings answered: 3; same answer on 2 (*partly → yes* on L15 attn+).
* Same direction on the 34 answered sheets: yes 9, partly 15, no 10. On the 14 edits answered on both seeds,
  the answer is the same on 10.
* No character was ever judged *nearly unchanged*.
* "Changes another way" by character (of 34): E2 elf 16, T7 tiefling 15, H3 halfling 13, G5 gnome 11, R6
  dragonborn 10, D1 dwarf 8, O4 half-orc 8.

| group (both seeds) | edits | same direction | prompt-following loss |
|---|---|---|---|
| coherent and mild | L08 MLP−, L10 MLP−, L14 attn+, L15 attn+, L19 attn−, L28 MLP+ | yes / partly | none |
| partly coherent | L02 MLP+, L04 MLP−, L06 MLP+, L10 attn+, L12 attn+, L25 MLP+, L26 MLP+ | partly | none to strong |
| no common direction | L05 MLP+, L09 MLP+, L12 MLP+, L17 MLP+; L14 MLP+, L20 MLP+ and L09 attn+ *partly* on one seed | no | medium / strong |

## What the notes say

* **The edits that keep a common direction are the mild ones.** Where all seven follow, the notes say the style
  stays comic, "a bit more American comic", "little changes"; where the change is a genre jump (oil painting,
  3D render, anime, photograph) the seven characters go to different genres and the prompt is lost (character
  replaced, gender changed, three figures instead of one).
* **The exceptions are not random characters.** The elf rogue and the tiefling bard are the most frequent
  exceptions; across the strong MLP+ edits, the halfling and the gnome tend to turn into oil painting or 3D
  render while the others stay drawn.
* **Several mild edits make the prompt's own details more literal.** L15 attn+ on both seeds: fresh scars on the
  dwarf (prompt: "battle-scarred", "a vertical scar"), a tusk on the half-orc ("lower tusks"), a real dragon face
  on the dragonborn ("blunt draconic snout"). L25 MLP+ on both seeds: dragon face, smoke at the tiefling's mouth
  ("faint smoke curling from one nostril"). L10 MLP− on both seeds: the half-orc's tusk. The tiefling's horns
  become ram horns under six edits ("short curling horns" read another way).

## Against Alessandro's predictions (by eye only; the measured tests come with `--test`)

* *As coherent as the DiT preset*: by eye, only for the mild edits; the strong MLP+ edits split the characters.
* *Less quality loss*: by eye the surface never broke — consistent with P2, which is decided on BRISQUE/CLIP-IQA.
* *Wider range of styles*: the notes name photograph, oil painting, 3D render, anime, Saturday-morning cartoon,
  cubist portrait, Victorian painting — wide, but across characters within one edit, not as a controllable
  direction.
