# Pre-registration C105 — does a fixed edit carry the same change across subjects, within and across style domains?

Written 2026-10-20 by Claude, **before any C105 encode or render.** Asked by Alessandro to close the circle opened by
C104 ("vorrei chiudere il cerchio"), with a better calibration than C103's.

## 1. Why

C104 (`docs/te_content_style_result.md`): a fixed perturbation of the text encoder — a real edit or a random push —
changes the **content** the same way across seeds of one prompt, and different perturbations change it differently.
Across prompts the earlier evidence says the change does not carry like a word of the prompt does: structured edits of
the image model kept their direction within a style domain and lost it across domains (2026-09-25, replication
pending, on DiT presets); in C103 the same random push aged the paladin and turned the teapot into a kettle. C105 tests
it on text-encoder perturbations, by eye, with a control for "same by chance".

## 2. Design

* **Subjects (8, two domains):** Western-comics portraits `D1_dwarf_paladin`, `E2_elf_rogue`, `O4_halforc_fighter`,
  `G5_gnome_wizard`; other styles `S1_rally` (photo), `C4_stilllife` (cartoon), `P2_lotuscanoe` (dreamlike), `LN` (macro
  photo). Texts from their plans.
* **Perturbations (4), text encoder, MLP:** edits ×(1+d) at **L14** (E14) and **L26** (E26); random pushes at **L09**
  (R09) and **L26** (R26) (per-token random unit directions, seed 9393, scaled by α × the per-token norm of the unedited
  MLP output). One fixed direction each, as C104 requires.
* **Matched picture change, calibrated per subject × perturbation.** Target DINOv2 distance **D = 0.25**, window
  **0.20–0.32**, median over **two calibration seeds** (1618033, 2718281; not used in the test).
  * Round 0, geometric ladder: E14 d = 0.4, 0.8, 1.6, 3.2; E26 d = 0.75, 1.5, 3, 6; R09 α = 1.5, 2.5, 4, 6; R26 α = 4, 7, 12, 20.
  * Rounds 1–2, automatic bisection (geometric midpoint) inside the bracket around the target, for every pair not yet in
    the window.
  * After round 2: the tested strength whose median D is closest to 0.25 is used if it lies in 0.15–0.40 (flagged when
    outside the window); otherwise the pair is **unreachable** and dropped.
  * About 300–400 calibration renders, run by one command that encodes, queues, waits, measures and decides.
* **Test seeds (2):** 2645751, 3316624. Per subject × seed: plain + 4 perturbations = up to 80 renders.
* **Gates:** plain test renders pixel-identical to existing plain renders for D1 (`benchmark_portraits/phase_c`), S1 and
  C4 (`benchmark_te_depth_control`), both seeds (6 checks, stop on failure); E2, O4, G5 against `phase_c` reported.
* **Blind (Alessandro).** Each unit shows four subjects as plain → changed, two questions with *stesso modo* / *in modi
  diversi* / *non si vede*:
  * **Contenuto:** "Il tipo di cambiamento del contenuto (soggetti, forme, oggetti, età, materiali) è lo stesso nelle
    quattro coppie?"
  * **Stile:** "Il tipo di cambiamento dello stile (resa, tecnica, colori, tratto) è lo stesso nelle quattro coppie?"

  Unit kinds, per perturbation × test seed: **WC** (the four comics), **WO** (the four others), **X1** (D1, E2, S1, C4),
  **X2** (O4, G5, P2, LN): 32 units. **Controls N:** the same four-subject sets, each subject with a *different*
  perturbation (rotation by seed): 8 units. 6 repeats; order random (seed 10505); conditions hidden. Page written
  before any label.

## 3. Rules (fixed now), content primary, style reported the same way

s = share of *stesso modo* among answers *stesso* or *diversi*, first showings. Edits = E14 + E26, random = R09 + R26.

0. **Match:** a subject × perturbation whose realized median D over the two test seeds lies outside 0.15–0.40 is not
   matched; units containing it are dropped (reported).
1. **Null:** s(N, content) ≤ 0.35. Above: the eye calls different perturbations "the same" too often (a generic change,
   such as "more realistic"), and rule 2 is **not testable**.
2. **Transfer, per type (edits, random)**, with within = WC + WO and mixed = X1 + X2 (≥ 6 answered units per group):
   * *no transfer*: s(within) − s(N) < 0.30;
   * *domain-specific*: s(within) − s(N) ≥ 0.30 and s(within) − s(mixed) ≥ 0.30;
   * *transfers across domains*: s(within) − s(N) ≥ 0.30, s(mixed) − s(N) ≥ 0.30 and s(within) − s(mixed) < 0.30;
   * otherwise *partly*.
3. **Reported:** the same for style; per perturbation; *non si vede*; test–retest; strengths, rounds and unreachable
   pairs; realized D.

**Tool rule.** Transfers: a fixed edit is a portable style knob, like a word. Domain-specific: an edit has to be chosen
per family of subjects. No transfer: an edit is a knob for one subject (C104), not a style.

## 4. Limits

Two seeds per subject; one direction per perturbation; small blind groups (8 units per type and group); the 2026-09-25
result was on image-model presets, so this tests the text encoder, not an exact replication; Alessandro has seen some
of these subjects before.

Script: `experiments/te_domain_transfer.py`. Directive: `docs/directives_antigravity_te_domain_transfer.md`.
