# Pre-registration C114 — the dose windows of C113, blind, on unseen prompts

Written 2026-10-28 by Claude, **before any C114 encode or render.** Script: `experiments/te_unseen.py`. Alessandro asked
for prompts built on the structure of his examples (subject + colour + style) and **not shown to him** before the
blind page; he should not read this file until then.

## 1. Why

C113 (descriptive, non-blind) found one usable dose per edit, identical on two prompts, at which DINOv2 put the edit's
change above the plain seed spread with a direction shared across seeds. C114 checks that blind, on prompts nobody
has seen rendered, and adds the question C113 could not ask: do the edits at those doses respect what the prompt
states explicitly (subject, colour, style)?

## 2. Design

* **Prompts (3), written by Claude:** `A twisted tree with long red leaves and a curled trunk, watercolor painting`;
  `A ceremonial dagger in art deco style with golden geometric inlays`; `A small green robot with round copper eyes,
  clay figurine`.
* **Edits at C113's doses, fixed:** E06 0.8, E14 0.8, E28 1.06066, P01 1.75 (inside C113's bracket 1.41–2.12, not
  rendered before).
* **Seeds:** C111–C113's 8. Plain + 4 edits: 3 × 8 × 5 = 120 renders + 3 gate renders (plain through the conditioning
  file = plain through the text, pixel for pixel).

## 3. Blind page (`occhio_C114.html`, key `data/te_unseen_key.csv`, seed 11414)

C112 amendment-2 format (PRIMA above, DOPO below, same column = same seed); each card's title shows the prompt.
Cards: one per prompt × edit (12); null, each DOPO a different edit (every edit twice), 2 per prompt (6); seed, DOPO
the plain picture at another seed, 1 per prompt (3); 3 repeats; 24 cards.
Questions: 1 *amount* (C112); 2 *same way* (C112); 3 *kept* — "Il soggetto, il colore e lo stile scritti nel prompt ci
sono ancora nella riga DOPO?" sì, in tutte / nella maggior parte / solo in poche / in nessuna (1 / 0.67 / 0.33 / 0).

## 4. Rules (fixed now)

0. Null cards' *same way* ≤ 0.35, otherwise rule 1 is not testable.
1. **Primary:** *same way* of the edit cards minus null **≥ 0.30** → *the change repeats across seeds on unseen
   prompts*; ≤ 0.10 → *does not repeat*; otherwise *partly*.
2. *kept* "all" or "most" in **at least 9 of 12** edit cards → *the window doses respect the prompt*; otherwise *the
   edits override the prompt*.
3. DINOv2 (`--analyze`, applied with the labels): median distance from plain ≥ the plain seed spread in **at least 9 of
   12** cells → *the edit moves the picture at least as much as a change of seed*.

Reported: amount for edit / null / seed cards (C112's seed cards were all "molto", so amount is not ruled); per cell
answers; DINOv2 consistency; test–retest; notes.

## 5. Limits

One observer; prompts by Claude in the style of his examples; P01's dose interpolated; three prompts; Krea-2 turbo
only. A "kept" judgement needs the prompt on the card, so the observer reads the prompts at labelling time.
