# Pre-registration C113 — does a stronger push let the edit's direction dominate the seed?

Written 2026-10-28 by Claude, **before any C113 encode or render.** Script: `experiments/te_dose2.py`, committed with this
file. Proposed by Alessandro after C112 ("se fosse solo questione di calibrazione? ... forse semplicemente non sono
abbastanza spinti"); renders authorised by him ("OK") on 2026-10-28.

## 1. Why

C112: the change of E28 (d 1.06) repeated across seeds; the other edits, mostly at d 0.28–0.53, repeated less, and no
edit changed the picture more than a change of seed. C74 found that encoder edits leave the style alone below d 0.70
and change it between 0.70 and 1.00 without breaking pictures — so most C112 doses were under that threshold. Against:
in C111 the same edits near d 0.8 were not more consistent across seeds, widened the seed spread and inserted
unrelated content; the DiT preset of the README peaks at strength 0.75–1.00 and falls beyond. Two outcomes are open:
past the threshold the direction dominates and repeats, or the picture changes more but differently per seed and
then breaks.

## 2. Design

* **Prompts:** two of C112's — `A curved tree with large blue leaves` (plain seeds vary, DINOv2 0.383) and
  `Cartoon evil helmet with black metal and a big red gemstone` (plain seeds nearly the same, 0.056).
* **Ladders (level 1 = C112's dose, reused):** E06 and E14 (one layer's MLP) d = 0.4, 0.8, 1.2, 1.6; E28 d = 1.06,
  1.59, 2.12, 2.65; P01 strength x = 0.71, 1.41, 2.12, 2.83 (per-layer ±0.21 to ±0.85).
* **Seeds:** C112's 8. Plain pictures and level 1 reused from `benchmark_te_settings`; levels 2–4 new:
  2 × 4 × 3 × 8 = 192 renders + 2 gate renders (plain re-rendered here, pixel-identical to C112's, else stop).

## 3. Blind page (Alessandro), written by the script after the renders, before any label

C112 amendment-2 format: two rows of 8, PRIMA above, DOPO below, same column = same seed (`occhio_C113.html`, key
`data/te_dose2_key.csv`, seed 11313). Cards: one per prompt × edit × level (32, levels in random order); null cards,
DOPO a different edit/level at each seed (4); seed cards, DOPO the plain picture at another seed (4); 4 repeats; 44.

Questions: 1 *amount* (molto / un po' / quasi niente / niente = 1 / 0.67 / 0.33 / 0); 2 *same way* (sì, tutte / la
maggior parte / no, ognuna a modo suo / non è cambiato nulla = 1 / 0.5 / 0 / excluded); 3 **broken** — "In quante
immagini DOPO c'è qualcosa di rotto, deformato o estraneo al prompt?" nessuna / una o due / circa metà / quasi tutte.
A level is **unbroken** when the answer is *nessuna* or *una o due*.

## 4. Rules (fixed now). A cell is prompt × edit (8 cells)

0. Null cards' *same way* ≤ 0.35, otherwise rules 1 is not testable.
1. **Primary:** *same way* at the highest unbroken level (2–4) minus at level 1 **≥ 0.5** (one step). Supported if in
   **at least 5 of 8 cells** → *a stronger push makes the change repeat more*.
2. At the highest unbroken level, *amount* ≥ the seed cards' *amount* for that prompt, in **at least 5 of 8 cells** →
   *the edit changes the picture as much as a change of seed*.
3. DINOv2: mean cosine of the displacements across seeds at the highest unbroken level minus at level 1 **≥ 0.10**, in
   **at least 5 of 8 cells** (computed by `--analyze`, applied with the labels).

Reported: per cell the first broken level, the curve of *same way* and *amount* over the levels, DINOv2 distance from
plain and its ratio to the plain seed spread, test–retest, notes.

## 5. Limits

One observer who proposed the hypothesis and has seen C112's level-1 pictures (in the non-blind sheets); one card per
level per cell (single answers, coarse scale); two prompts; doses beyond C74's range; Krea-2 turbo only.

## Amendment 1 (2026-10-28, before any label)

Alessandro, before starting: since this is a calibration, what matters most is *how far* each edit went, not how many
pictures broke. Question 3 is replaced:

* *drift* — "Quanto si sono allontanate dal prompt le immagini DOPO, nell'insieme?" per niente (è ancora ciò che il
  prompt chiede) / poco (qualche dettaglio fuori posto) / molto (si riconosce a fatica) / del tutto (non è più ciò che il
  prompt chiede, o è rotta).
* A level is **unbroken** when *drift* is *per niente* or *poco*. Rules 0–3 and their bars are otherwise unchanged.
* Reported in addition: the drift curve over the four levels per cell (the calibration the tool needs).

Same cards, same order (key regenerated identical); storage key `c113_labels_v2`.

## Amendment 2 (2026-10-28, before any label was exported)

Alessandro, on the first cards (one was a null card mixing edits and levels, several of them broken): the blind pass
does not serve a calibration; he asked for a non-blind sheet of every picture to mark, per edit, which doses can go
higher and which must come down. **The blind pass is abandoned; no label from it exists or is used.** Rules 0–2 are
not applied. C113 becomes a descriptive calibration:

* sheets `Text2Img/_claude_scratch/C113_<prompt>.jpg` (plain + 4 edits × 4 levels × 8 seeds, labelled);
* Alessandro's marks per edit and level (usable / too strong / broken), committed as given;
* DINOv2 (`data/te_dose2_dino.csv`) reported next to the marks, with the caveat that consistency across seeds can rise
  because the picture leaves the prompt the same way at every seed (seen on the sheets before the marks).

The blind confirmation of the chosen doses moves to C114, on prompts Alessandro has not seen.
