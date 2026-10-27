# Pre-registration C111 — "Photo of a tree": the same tree at every seed, and the same change at every seed?

Written 2026-10-27 by Claude, **before any C111 encode or render.** Script: `experiments/te_tree.py`, committed with this
file. Renders need Alessandro's authorisation (directive `docs/directives_antigravity_te_tree.md`).

## 1. Where the hypothesis comes from

Alessandro, 2026-10-27: when a prompt names a subject without describing it, Krea-2 draws nearly the same thing at every
seed; an edit of the weights then changes the environment or the light, and that change repeats at every seed. He
proposed the prompt **"Photo of a tree"**, a subject he has not seen in this project.

What was looked at before writing this: Claude assembled C109's rally renders that exist at four seeds (plain and 11
presets, `benchmark_te_light_presets`) into one sheet. Plain: nearly the same car and framing at the four seeds; P01, P06
and P10 changed the scene in a way that looked the same at the four seeds; the other presets stayed close to plain.
That look is **descriptive and generated the hypothesis**; nothing from the rally counts as a test here.

Related results already in the report: C72 (each description has its own default; random per-token pushes also switch
the genre); page 31 (an edit leaves a signature recognisable across seeds, on described portraits); C105 and C109 rule 2
(a fixed perturbation, real or random, changes content in a similar way across subjects). New here: a prompt that
leaves almost everything to the model, and a direct comparison between how much the seed varies the picture and how
much an edit moves it.

## 2. Design

* **Prompt:** `Photo of a tree` (exactly). Sampling: the bench settings (euler_ancestral, 9 steps, CFG 1, simple,
  1024×1280, negative zeroed).
* **Perturbations (10):**
  * real, one encoder layer's MLP (gate, up, down): **E05, E06, E14, E26, E28** (the layers of pages 30–31);
  * real, C109 presets **P01, P06, P10** (same four layers and signs as in C109);
  * fixed random pushes **R09, R26**: one random direction, fixed across seeds, added to that layer's MLP output
    (C105's control).
* **Calibration (C105/C109 code, unchanged):** per perturbation, target DINOv2 distance from the plain tree **0.25**
  (window 0.20–0.32, accepted 0.15–0.40), median over calibration seeds 1618033, 2718281; ladders as in C105/C109
  (edits 0.4–3.2 or 0.75–6, presets x 0.5–3.3, random as C105), up to two bisection rounds. Every perturbation is
  therefore compared at about the same size of change. Up to about 120 renders. A perturbation that does not reach
  the accepted range is left out and reported.
* **Test seeds (8):** 2645751, 3316624, 1414213, 1732050, 2236067, 3141592, 1234567, 5772156 (none used in
  calibration). Plain + every reached perturbation: up to 88 renders, plus one gate render.
* **Gate:** the plain tree at 2645751 through the conditioning file is pixel-identical (max abs diff 0) to the plain
  tree through the ordinary text path. Otherwise stop.

## 3. Rule 1 — "the same tree at every seed" (DINOv2, computed by `--analyze`)

* Median DINOv2 distance over the 28 pairs of the 8 plain trees **≤ 0.15** (the smallest accepted edit change) and
  below the median distance of the real perturbations from the plain tree at the same seed → *nearly the same picture
  at every seed*; otherwise *the seeds already vary* (the first half of the hypothesis falls).
* Reported: the same median for each C109 subject's four plain seeds (reference: is the tree more uniform than a
  described subject?); per perturbation, the median distance between its 8 seeds (does an edit narrow or widen the
  spread?); the mean cosine between the DINOv2 displacements (edit − plain) of different seeds, per perturbation,
  against the mean for different perturbations at different seeds.

## 4. Rules 2–3 — "the same change at every seed" (blind, Alessandro)

Page written by the script after the renders and `--analyze`, before any label (`occhio_C111.html`, key
`data/te_tree_key.csv`, seed 11010). Each card: four pairs *prima → dopo*, plain tree and changed tree at the same seed.

* **Matched cards:** one perturbation, seeds 1–4 or 5–8 (20 cards if all ten are reached).
* **Null cards:** four different perturbations, one per seed (4 per seed group, 8).
* **Repeats:** 4 matched cards shown again later. Order random, conditions hidden.
* **Questions:** *"Il cambiamento di luce, cielo o ora del giorno è dello stesso tipo in tutte le coppie?"* and
  *"Il cambiamento dell'albero o dell'ambiente (specie, forma, stagione, paesaggio) è dello stesso tipo in tutte le
  coppie?"*; answers *stesso tipo* / *qualcosa di simile* / *in modi diversi* / *non si vede* (1 / 0.5 / 0; *non si
  vede* excluded). Answering rule from C109 amendment 1: same kind in most pairs with some out → *qualcosa di simile*;
  *non si vede* only when no pair shows a change of that kind.
* **Card score:** the higher of the two answers (the hypothesis is "light **or** setting repeats"); a card with both
  *non si vede* is excluded. Repeats are not counted in the rules (test–retest only).

Rules, fixed now:

0. Null cards' mean score **≤ 0.35**, otherwise the pass is not valid.
2. Real cards (E05–E28, P01, P06, P10) minus null **≥ 0.30** → *the change repeats across seeds*; **≤ 0.10** → *the
   change does not repeat*; otherwise *partly*.
3. Real minus fixed random pushes **≥ 0.20** → *real edits repeat more than fixed random pushes*; otherwise *no
   difference* (C105 found random pushes transferring too; a fixed random direction may also repeat).

Reported: light and setting separately; per perturbation; *non si vede* counts; test–retest; Alessandro's notes. After
the labels, a non-blind sheet (8 seeds × plain and each perturbation) for the result page.

## 5. Limits

One prompt; one observer who proposed the hypothesis (but has not seen these images); calibration equalises the size of
the change, not its kind. If rule 1 holds, rule 2 is easier to satisfy (nearly identical starting pictures moved by
the same edit tend to end alike): the two halves are linked, and the reported spread per perturbation shows whether an
edit adds or removes variation between seeds. Krea-2 turbo is distilled; low seed variety may be a property of
distilled models and is not tested on another model here.

## Amendment 1 (2026-10-27, before any encode or render)

Asked by Alessandro before the directive was run: the claim is not that real edits beat random pushes (a fixed random
push may well repeat too); it is that **the same prompt can give versions of the tree that differ in content more than
a change of seed does, and that the changed properties stay when the seed changes.** Changes:

* **Random pushes R09 and R26 removed**, and rule 3 with them. Eight perturbations: E05, E06, E14, E26, E28, P01, P06,
  P10. Calibration up to about 100 renders; test 73 (1 gate + 8 seeds × 9).
* **Seed cards (4) added** as the control for the first half of the claim: four pairs *plain tree at one seed → plain
  tree at a seed of the other group*, no edit (two pairings per group). No extra render.
* **A third question, asked first on every card:** *"Quanto cambia il contenuto (albero, ambiente, luce) da prima a
  dopo, nell'insieme delle coppie?"* — *cambia molto / cambia qualcosa / quasi niente / niente* (1 / 0.67 / 0.33 / 0).
* **Rule 1b (blind, new):** mean "amount" of the edit cards minus that of the seed cards **≥ 0.30** → *the edits change
  the content more than a change of seed*; **≤ 0.10** → *no more than a change of seed*; otherwise *partly*.
* **Rule 1 (DINOv2) stays, with a caveat:** the edits are calibrated to move the picture by about 0.25, so "below the
  edits' distance" is partly set by the calibration. The informative part is the absolute bar (0.15) and the comparison
  with the C109 subjects. Rule 1b, by eye and on content, is the primary test of the first half.
* **Rules 0 and 2 unchanged** (null ≤ 0.35; edit cards minus null ≥ 0.30 on "same kind", the higher of light and
  setting). The seed cards' "same kind" score is reported: a change of seed is expected not to repeat.
* Cards: 16 edit, 8 null, 4 seed, 4 repeats of edit cards = 32.
