# Pre-registration C112 — the subject fixed, the setting free: one picture at every seed, and an edit that picks another?

Written 2026-10-28 by Claude, **before any C112 encode or render.** Script: `experiments/te_settings.py`, committed with
this file. Renders need Alessandro's authorisation (directive `docs/directives_antigravity_te_settings.md`).

## 1. Where the hypothesis comes from

* **C111** (`docs/prereg_te_tree.md`, "Photo of a tree"): rule 1 failed. The 8 plain trees have a median pairwise DINOv2
  distance of 0.475, the highest of every prompt measured (C109 subjects 0.057–0.178). The plainest prompt varies the
  most with the seed (mostly framing, by eye — a reading after the data).
* **C111 exploratory run** (`Benchmark_te_tree_2`, not pre-registered, seen by both of us): with *"a photo of a tall
  torted tree with large leaves"* the plain tree is nearly the same at all 8 seeds; **E28 at 1.06066** moved it to a
  park lawn at 8 of 8 seeds, **P01 at 0.7071** to an ivy-covered trunk at about 6 of 8; E06, E14, P10 at 2–3 of 8;
  E05, E26, P06 near plain.
* **Refined hypothesis:** when the prompt fixes the subject and leaves the setting free, Krea-2 falls back on nearly the
  same picture at every seed; a text-encoder edit chooses another version (setting, light, form) and keeps it at every
  seed.

## 2. Design

* **Prompts (4), written by Alessandro on 2026-10-28, never rendered:** `A curved tree with large blue leaves`;
  `A short alien axe with a weird shaped blade`; `Cartoon evil helmet with black metal and a big red gemstone`;
  `A concept yellow flying car`.
* **Edits (8), doses of the exploratory run, fixed (no calibration):** E05 0.28285, E06 0.4, E14 0.4, E26 0.53033,
  **E28 1.06066**, **P01 0.7071**, P06 0.8409, P10 1.0 (E = one encoder layer's MLP; P = C109's four-layer presets at
  strength x). **Primary predictions: E28 and P01.**
* **Seeds (8):** C111's test seeds. Bench sampling. 4 × 8 × 9 = 288 renders + 4 gate renders.
* **Gate:** for each prompt, the plain picture at 2645751 through the conditioning file is pixel-identical to the one
  through the text. Otherwise stop.

## 3. Rule 1 — one picture at every seed (DINOv2, `--analyze`)

Per prompt, median pairwise distance of the 8 plain pictures **≤ 0.15** → *same picture at every seed*. **Supported if
at least 3 of the 4 prompts** pass. Reported: per prompt and edit, median distance from plain and mean cosine of the
displacements across seeds against different edits at different seeds.

## 4. Rules 0, 1b, 2 — blind (Alessandro)

Page written by the script after the renders, before any label (`occhio_C112.html`, key `data/te_settings_key.csv`,
seed 11212). Every card shows **all 8 seeds** as pairs *prima → dopo*:

* **edit cards:** plain → one edit, per prompt × edit (32);
* **null cards:** plain → a different edit at each seed (at least 6 distinct), 2 per prompt (8);
* **seed cards:** plain at a seed → plain at another seed, no edit, 1 per prompt (4);
* **4 repeats** of edit cards; order random; prompts mixed; conditions hidden. 48 cards.

Questions, as in C111 amendment 1: *amount* (molto / qualcosa / quasi niente / niente = 1 / 0.67 / 0.33 / 0);
*light* and *setting* "same kind in all pairs?" (stesso / simile / diversi = 1 / 0.5 / 0; *non si vede* excluded).
Card "same kind" score = the higher of light and setting.

0. Null cards' same-kind score **≤ 0.35**, otherwise the pass is not valid.
1b. Amount of the **E28 and P01** cards minus seed cards **≥ 0.30** → *the edits change the content more than a change
   of seed*; ≤ 0.10 → *no more*; otherwise *partly*.
2. Same kind of the **E28 and P01** cards minus null **≥ 0.30** → *the change repeats across seeds*; ≤ 0.10 → *does not
   repeat*; otherwise *partly*.

Reported: all eight edits; seed cards' same-kind score; light and setting apart (the exploratory run predicts setting
for E28); per prompt and edit; test–retest; notes. After the labels, a non-blind sheet per prompt.

## 5. Limits

One observer, who proposed the hypothesis and wrote the prompts; doses chosen on one exploratory tree, not calibrated
per prompt (an edit may barely move some prompts or break them); the "Cartoon" prompt names a style; 8 seeds; Krea-2
turbo only.
