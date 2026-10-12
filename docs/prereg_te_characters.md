# Pre-registration C65 — do text-encoder edits move different characters the same way?

Written 2026-10-11, **before any C65 render**. Code: `experiments/te_characters.py` (plan, queue, reproduction,
count, measures, eye page, decision rules, self-test on synthetic data), committed with this document.

## Claim under test (Alessandro, 2026-10-11)

*An edit to one layer of the text encoder changes the drawing style cleanly, and it changes different
characters drawn the same way in the same direction* — the question C52 asked of a DiT preset, asked here of
single text-encoder edits.

Background: C64 phase 1 (`docs/te_pilot_phase1_result.md`), one character and one seed, found that doubling
one half of a Qwen3-VL layer often changes the style strongly with little surface cost. Whether that change is
a property of the edit or of that one picture is not known.

## Material

* **Characters, prompt frame, settings, baselines:** those of C52 (`experiments/portraits.py`): seven
  Western-comics close-up portraits (D1 dwarf paladin, E2 elf rogue, O4 half-orc fighter, G5 gnome wizard,
  H3 halfling druid, R6 dragonborn cleric, T7 tiefling bard). Seeds 2645751 and 3316624 for the edits; the
  baselines already rendered in `benchmark_portraits/phase_c` are reused (all four phase C seeds for the
  identity reference).
* **Edits, chosen by rule (no hand-picking):** every C64 phase-1 layer edit (attention q,k,v,o or MLP
  gate,up,down of one Qwen3-VL layer, dose ±1.00) that Alessandro judged a *medium* or *strong* change, with the
  overall style *changed*, and the surface *as the original* or *cleaner*. This gives 20 edits (16 at +1.00,
  4 at −1.00): L02 MLP+, L04 MLP−, L05 MLP+, L06 MLP+, L08 MLP−, L09 attn+, L09 MLP+, L10 attn+, L10 MLP−,
  L12 attn+, L12 MLP+, L14 attn+, L14 MLP+, L15 attn+, L17 MLP+, L19 attn−, L20 MLP+, L25 MLP+, L26 MLP+,
  L28 MLP+. The DiT-side text slots are excluded (they are not text-encoder edits). The selection reuses the
  C64 labels, so these are edits that changed one picture strongly by construction; the test is whether they
  do the same to others.
* **Renders, part A:** 1 reproduction (D1 baseline through this workflow, must equal the phase C baseline pixel
  for pixel) + 7 nulls (layer 35, never read, at +1.00, one per character, seed 2645751) + 20 edits × 7
  characters × 2 seeds = **288**.
* **Part B — word order** (added before any render, Alessandro: *the order of the words should change the
  text encoder's effect more visibly than the model's*). The same 20 edits on P1_elfbrawler in the five word
  orders of the DiT test (`benchmark_prompt_order`, V1 Original, V2 SubjectFirst, V3 BGFirst, V4 ActionFirst,
  V5 Inverse; seeds 3141592 and 1234567). That test's baselines are reused after one reproduction (V1, 3141592).
  **201** renders.
* **Part C — style family** (added before any render, Alessandro: *a character of the same family written as a
  realistic watercolour will change style very differently, and the text encoder will behave differently for
  the same edits*). The first calibration character, D1, with the frame `Realistic watercolor painting,
  close-up portrait, frontal view.` instead of `Western comics style, …`, same text, same two seeds; 2 baselines
  + 20 edits × 2 seeds = **42** renders. The character was fixed by position in the list, not chosen.
* **Total: 531 renders.**

## Order

1. Reproduction gate, then the renders (Antigravity, `docs/directives_antigravity_te_characters.md`).
2. **Eye first.** One sheet per edit × seed (40 sheets + 6 unannounced repeats): the seven originals above, the
   same edit on each below, anonymous id, shuffled (rng 66). Alessandro answers: do the seven change in the same
   direction (yes / partly / no); which direction (free); surface (cleaner … strong). The key
   `data/te_characters_eye_key.csv` is committed before any label; the labels are committed as downloaded,
   before any count and before anyone opens the measures.
3. Measures (Antigravity): 23 style statistics (`style_features.py`); ArcFace `buffalo_l`, BRISQUE, CLIP-IQA.
4. `--test` (Claude).

## Measures and rules (as in C52)

Style vector: the 23 statistics, each divided by its SD over the 14 edit-seed baselines. dF = edit − baseline,
per character and seed.

* **S (per edit)** — cosine of dF between the two seeds of the same character; median over the 7 characters.
* **W (per edit)** — cosine of dF between two *different* characters at the same seed; median over 21 pairs ×
  2 seeds.
* **Verdict per edit.** median S < 0.50 → *uninformative* (the edit does not agree with itself across seeds;
  pitfall 89). Otherwise median W ≥ 0.40 → *coherent*; < 0.25 → *incoherent*; else *unclear*. Thresholds are
  C52's; C52's DiT preset scored W = 0.51 on held-out characters (reference only).
* **H1 — text-encoder edits move different characters the same way.** If fewer than half the edits are
  informative: H1 *uninformative*. Otherwise: coherent in ≥ 14 of 20 → *supported*; coherent in ≤ 6 of 20 →
  *refuted*; else *inconclusive*.
* **Identity, reported, no decision.** Per edit, over characters with a detected face in all six of their
  images: how many have median ID_edit > ID_seed (ID_seed = mean ArcFace cosine between the four phase C
  baselines of that character). C64 saw strong edits drop prompt traits, so identity loss is expected for some
  edits; the count says which.
* **Eye, reported against H1, no decision:** per edit, the two sheets' answers to "same direction".
* **Cost, reported:** BRISQUE and CLIP-IQA edit − baseline per edit.

**Part B rules** (definitions of `prompt_order_feature_consistency.py`, the DiT test of 2026-10-04). Per edit:
dF in each order and seed, scaled by the SD over the 10 baselines; *cos_order* = mean cosine of dF between
different orders, same seed (20 pairs); *cos_seed* = mean cosine between the two seeds, same order (5 pairs);
*size* = mean |dF|. Only edits whose size exceeds the change made by reordering alone enter, as for the 43 DiT
arms. d = cos_order − cos_seed (how much more the order disturbs the edit than the seed does).

* **H2 — word order changes a text-encoder edit more than a DiT edit.** Median d over the text-encoder edits
  ≤ median d over the DiT arms − 0.10, with a one-sided Mann–Whitney p < 0.05 → *supported*; median d (text
  encoder) ≥ median d (DiT) → *refuted*; otherwise *inconclusive*. Fewer than 5 edits above the reordering size →
  *uninformative*. Reported alongside: median cos_order of both (DiT: 0.69).

**Part C rules.** Scale: SD of the 14 comic baselines, for both families. Per edit, *across style* = mean
cosine (over the two seeds) between dF on the watercolour D1 and dF on the comic D1; *across character* = mean
cosine between dF on the comic D1 and dF on each of the other six comic characters, same seed.

* **H3 — the style family changes what an edit does more than the character does.** Median *across style* ≤
  median *across character* − 0.10, with a one-sided Wilcoxon signed-rank p < 0.05 over the 20 edits →
  *supported*; median *across style* ≥ median *across character* → *refuted*; otherwise *inconclusive*.
  Reported alongside: the size of each edit on the watercolour against the comic D1.

**Alessandro's predictions (2026-10-11), each read as holds / fails, deciding nothing:**

* **P1** — as coherent as the DiT preset: median W over the informative edits within 0.41–0.61 (C52: 0.51).
* **P2** — less quality loss than the DiT preset: median over edits of the median BRISQUE change is lower, and of
  the CLIP-IQA change higher, than the C52 preset's on the same characters and seeds.
* **P3** — a wider spread of styles than the DiT blocks: on P1_elfbrawler (order V1, both seeds), the
  participation ratio of the 20 edits' mean dF is larger than that of the 20 largest DiT single-block arms of
  the order test. The edits were selected for changing style, so this comparison favours them; it is reported
  as such.

## Known limits

* One prompt frame and style (Western comics close-up portraits), two seeds, one observer who knows the C64
  pictures.
* The 23 statistics measure colour, contrast, edges and texture; a change of genre (e.g. "anime") that keeps
  those statistics similar can look coherent to the eye and not to W, or the reverse. Both are reported.
* Dose ±1.00 only. Nothing here says what happens at lower doses.
* Part B rests on one prompt; the DiT reference arms are single DiT blocks at their own doses, not the same
  edits. Part C rests on one character and two seeds.
* Parts B and C are measured only (no eye page); the grid viewer can show them afterwards.
* The edits were selected on one picture where they changed style; regression to the mean is expected.

## Amendment 1 (2026-10-12, after the renders, before the key was opened and before any label)

At Alessandro's request the eye page also asks, for each of the seven characters from left to right, whether it
*follows the direction* (default), *changes another way* or is *nearly unchanged*, and gives a free field for how
the exceptions change. The sheets, their order and the key are those the night run produced (the rebuilt key is
byte-identical). These answers are descriptive: they say which characters are the exceptions to an edit and how;
no rule above uses them.

## Amendment 2 (2026-10-12, before any label)

At Alessandro's request each of the seven characters on a sheet also gets a free-text field, "how it changed"
(export columns t1–t7). Same sheets, order and key. Descriptive only, like amendment 1.
