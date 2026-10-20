# Pre-registration C107 — is it the subject that decides where L06 sends the style?

Written 2026-10-20 by Claude, **before any C107 render.** Asked by Alessandro after looking at the TEP2 sheet: under
L06 MLP doubled the dwarf and the half-orc become photographs while the elf rogue becomes anime — is it the subject?
Would a female human ranger go the same way as the others? Renders authorised by Alessandro the same day.

## 1. Why

C73 (`data/te_fallback_genre_alessandro.csv`): under L06 MLP doubled, seven portraits at two seeds are realistic in 11 of
14 pictures and anime in 3 — the elf rogue 2 of 2, the tiefling 1 of 2. C73 H2 ruled out that a strong edit sends each
character to its own no-style fallback (0.28 against 0.27); the elf rogue's fallback is painting, not anime. C72 block
B: "elf" alone draws anime in 2 of 4 seeds, "female antlered elf brawler" in 3 of 4. Observation on the TEP2 sheet
(Claude, not tested): the dwarf and the half-orc lose their fantasy traits and become generic human women, drawn as
photographs; the elf keeps her pointed ears and becomes anime. Two candidate causes are mixed in the elf's prompt: the
**species** word ("wood elf") and the **gender** word ("non-binary"), both plausibly tied to anime in the model's data.

## 2. Design

* **Prompt:** the E2 elf rogue of C52/C65, frame "Western comics style, close-up portrait, frontal view.", with only the
  subject phrase "non-binary rogue wood elf" changed (everything else identical, checked by `--selftest`):
  * **EN** non-binary rogue wood elf (the original) · **EF** female rogue wood elf
  * **HN** non-binary rogue human · **HF** female rogue human
  * **RF** female ranger human (Alessandro's case; reported, not in the 2 × 2)
* **Conditions:** plain encoder; L06 MLP doubled (`layers.6.mlp.{gate,up,down}_proj.weight` at +1.00, ArthemyKrea2CLIPTuner,
  Real Value), in-graph as C65.
* **Seeds (4):** the C52 phase-C seeds 2645751, 3316624, 3605551, 4123105. Sampler as every Krea-2 run here.
* **Renders:** 5 × 2 × 4 = **40**, folder `benchmark_te_species`, plan `data/te_species_plan.csv`.
* **Gates (stop on failure):** EN plain at 2645751 pixel-identical to `benchmark_portraits/phase_c`; EN L06 at 2645751
  pixel-identical to `benchmark_te_characters` (C65).

## 3. Blind labels (Alessandro)

A page written after the renders, before any label: the 40 pictures one at a time, in random order, nothing about
prompt or condition shown, 6 repeated for test–retest. Two questions per picture:

* **Genere:** fumetto occidentale / anime / realistico / pittura / cartoon / altro (C70–C73's labels).
* **Orecchie:** "Il personaggio ha le orecchie a punta?" sì / no.

## 4. Rules (fixed now)

First showings only. A variant whose plain pictures are not Western comic in at least 3 of 4 is excluded from rules 1–2
(rule 0, reported). On the L06 pictures of EN, EF, HN, HF:

1. **Species:** share of anime among the elf prompts (EN, EF) minus among the human prompts (HN, HF) **≥ 0.50** →
   *the species decides*; otherwise *not the species alone*.
2. **Gender word:** share of anime among non-binary (EN, HN) minus female (EF, HF) **≥ 0.50** → *the gender word
   decides*; otherwise *not the gender word alone*.
3. **Reported:** realistic share human minus elf; the genre tally of every variant under L06, RF included; the 2 × 2
   table.
4. **Reported, Claude's prediction:** RF under L06 is realistic in at least 3 of 4 pictures.
5. **Reported, the traits reading:** among L06 pictures, anime and realistic shares by species and by "pointed ears"
   (yes / no). The reading "the destination follows what survives" predicts anime with ears kept, realistic with ears
   lost, whatever the prompt.
6. **Reported:** test–retest on the 6 repeats.

Both rules met: both words push toward anime. Neither: the destination is not decided by either word alone (the 2 × 2
table and rule 5 say what else). Script: `experiments/te_species.py --rules` → `data/te_species_tests.csv`, tested on
synthetic labels by `--selftest`.

## 5. Limits

One character's description, four seeds, one edit, one observer who knows the hypothesis (he proposed it). n = 8 per side
of each rule: a difference of 0.50 is 4 pictures. "Human" and "elf" also change what the model draws for ears, which
is what rule 5 looks at; it cannot separate cause from consequence.
