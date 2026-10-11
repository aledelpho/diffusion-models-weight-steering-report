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
* **Renders:** 1 reproduction (D1 baseline through this workflow, must equal the phase C baseline pixel for
  pixel) + 7 nulls (layer 35, never read, at +1.00, one per character, seed 2645751) + 20 edits × 7 characters
  × 2 seeds = **288**.

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

## Known limits

* One prompt frame and style (Western comics close-up portraits), two seeds, one observer who knows the C64
  pictures.
* The 23 statistics measure colour, contrast, edges and texture; a change of genre (e.g. "anime") that keeps
  those statistics similar can look coherent to the eye and not to W, or the reverse. Both are reported.
* Dose ±1.00 only. Nothing here says what happens at lower doses.
* The edits were selected on one picture where they changed style; regression to the mean is expected.
