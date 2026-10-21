# Pre-registration C108 — does the gender word steer L06 beyond the elf rogue, in short prompts, and inside one picture?

Written 2026-10-21 by Claude, **before any C108 render.** Asked by Alessandro after C107 ("sono curioso di fare
quell'esperimento, ma proverei anche a vedere cosa succede con meno parole, e mettendo tutte e quattro le descrizioni
nella stessa immagine ... per vedere se i cambiamenti sono simili"). Renders authorised by him the same day.

## 1. Why

C107 (`docs/te_species_result.md`): on the elf rogue's description, under L06 MLP doubled, "non-binary" sends the picture
to anime in 6 of 8, "female" in 0 of 8 (rule +0.75), while elf against human makes no difference (+0.00). One
description, one observer. Three open questions: (A) does "non-binary" pull toward anime on other characters; (B) does
the split hold when the gender and species words are a large part of a short prompt; (C) inside one picture with the
four descriptions in four panels, do the panels split the same way, and do they change alike?

## 2. Design (96 renders, folder `benchmark_te_gender`, plan `data/te_gender_plan.csv`)

Every prompt plain and with L06 MLP doubled (`layers.6.mlp.{gate,up,down}_proj.weight` +1.00, ArthemyKrea2CLIPTuner,
Real Value, in-graph), at the C52 phase-C seeds 2645751, 3316624, 3605551, 4123105. Sampler as always.

* **Block A — other characters (48).** The C52/C65 portraits D1 dwarf ("female paladin mountain dwarf"), O4 half-orc
  ("female fighter half-orc") and T7 tiefling ("male bard tiefling"), each as written (*orig*) and with the gender
  word replaced by "non-binary" (*nb*), nothing else changed.
* **Block B — short prompts (32).** "Western comics style, portrait of a {non-binary | female} {elf | human}." (SEN,
  SEF, SHN, SHF).
* **Block C — one page, four panels (16).** A comic-page prompt in the form of C100's `P5_comic_panels`, "Western comics
  style. Comic book page layout, single image divided into four equal rectangular panels by thick bold black borders,
  a close-up portrait in each panel. Panel 1 (Top Left): … Panel 4 (Bottom Right): …", with C107's four long
  descriptions (EN, EF, HN, HF, without the white-background clause) in two orders: O1 EN, EF, HN, HF; O2 reversed.
* **Gates (stop on failure):** D1 as written, plain and L06, at 2645751, pixel-identical to `benchmark_portraits/phase_c`
  and `benchmark_te_characters`.

## 3. Blind labels (Alessandro), pages written after the renders, before any label

* **Single pictures (A and B mixed, 80 + 6 repeats):** one at a time, random order, nothing shown about prompt, word or
  condition. *Genere:* fumetto occidentale / anime / realistico / pittura / cartoon / altro.
* **Pages (C, 16 + 2 repeats):** one page at a time. *"L'immagine ha quattro pannelli separati?"* sì / no; then the genre
  of each panel, by position (top left, top right, bottom left, bottom right).
* **Pairs (C, 8, after the pages):** plain and L06 page at the same seed and order, side by side (which is which not
  said). *"Nei quattro pannelli il cambiamento è dello stesso tipo?"* stesso / qualcosa di simile / diversi.

## 4. Rules (fixed now; first showings only)

0. A prompt whose plain pictures are not Western comic in at least 3 of 4 is excluded from its rule (reported). A page
   without four separate panels is excluded from block C.
A. **Other characters:** pooled over the kept characters, anime share under L06 with "non-binary" minus with the original
   word **≥ 0.40**, and positive in at least 2 of 3 characters → *non-binary pulls toward anime on other characters*;
   otherwise *not shown on other characters*.
B. **Short prompts**, as C107: anime elf − human ≥ 0.50 → *the species decides*; anime non-binary − female ≥ 0.50 →
   *the gender word decides*.
C. **Inside one picture:** over the L06 panels of the kept pages (panel ↔ description by its position in the prompt),
   anime share of the non-binary panels minus the female panels **≥ 0.50** → *the same split inside one picture*;
   otherwise *no split inside one picture*.
Reported: per-character and per-variant tallies; elf − human in panels; L06 pages with one genre in all four panels;
the pairs' mean (stesso 1, simile 0.5, diversi 0); test–retest. Script `experiments/te_gender.py --rules` →
`data/te_gender_tests.csv`, tested on synthetic labels by `--selftest`.

## 5. Limits

One edit, four seeds, one observer who knows the hypothesis. Panels may not follow the order of the prompt (rule C
assumes they do; Alessandro's genre per position is kept as given, and a page whose panels visibly do not match the
descriptions is reported). A "non-binary" dwarf or tiefling may also change the character's look, not only its genre;
the rule counts genre only.
