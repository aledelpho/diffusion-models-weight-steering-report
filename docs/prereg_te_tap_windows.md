# Pre-registration C87 — how many taps, and which: cumulative tap windows and single taps of the L06 edit

Written 2026-10-18 by Claude, **before any C87 render and before any C87 measure.** Absorbs roadmap item TAP1
(replicating the public single-tap probes). Follows C79 (`docs/te_tap_isolation_result.md`).

## 1. Why

C79 found that the damage of `L06_mlp_p1.00` (layer 6 MLP of Qwen3-VL-4B doubled) does not travel through the two
taps right after the layer (trait loss 0.014 against 0.296), that the early/middle taps cost more than the late ones
in 5 of 6 pairs but by +0.146 (bar +0.15, inconclusive), and that the two halves together fall short of the full
edit (0.37 against 0.46 on the same seeds). Three questions follow:

* **Q1 — step or slope.** As more taps carry the push, does the damage grow gradually, or does it jump when one
  particular tap is added?
* **Q2 — a hub tap.** Is there one tap that alone carries a large share of the damage? Two candidates are named in
  advance: **tap 7 (L23)**, which has the largest weight in `txtfusion.projector` (−1.44,
  `data/te_tap_isolation_txtfusion_weights.csv`), and **tap 6 (L20)**, the "hub" layer of the community probes
  (krea-explorations, one seed, not replicated).
* **Q3 — interaction.** Do complementary windows add up to the full edit, or does the damage need taps together?

**Tool rule.** If a few taps carry the effect (Q1 step or Q2 hub), those taps are a candidate knob for a style tool.
If the damage needs nearly all taps, the rule is: do not edit the text encoder for style.

## 2. Design (156 renders)

* **Edit:** `L06_mlp_p1.00` only (`layers.6.mlp.{gate,up,down}_proj.weight` × 2). L14 is left for later.
* **Characters (3):** `D1_dwarf_paladin`, `E2_elf_rogue`, `O4_halforc_fighter` (C74/C75/C79 prompts, unchanged).
* **Seeds (2):** `2645751`, `3316624`, where the full edit and the C79 renders already exist.
* **Mechanism:** `Krea2ConditioningPush`, `variant="taps"`, exactly as in C79: P = C_edit − C_base, added only on the
  listed taps. L06 reaches taps 2–11; taps 0–1 carry no push and are never listed.
* **Conditions (26 per character × seed):**
  * **Forward windows** F_k = taps 2..k, k = 2…10 (9). F_11 is the full edit (exists).
  * **Backward windows** B_k = taps k..11, k = 3…11 (9). B_2 is the full edit.
  * **Single taps** S_k = tap k alone, k = 3…10 (8). S_2 = F_2 and S_11 = B_11 are not repeated.
* **Count:** 26 × 3 × 2 = **156 renders**. Plain baselines (`benchmark_portraits/phase_c`) and full edits
  (`benchmark_te_characters`) are reused.

### Gates (part of the 156, checked before any measure)

Three conditions coincide with C79 renders at the same seeds and must be **pixel-identical** (max abs diff 0):
F_3 = C79 `taps_local` ("2,3"), F_8 = C79 `taps_early_mid` (taps 2–8 carry the push in both), B_9 = C79 `taps_late`
("9,10,11"). 18 pairs. Any difference > 0 stops the analysis.

## 3. Measures

**Primary: DINOv2-large distance to the same-seed baseline** (1 − cos), D(X), and its share of the full edit,
f(X) = D(X) / D(full), per (character, seed) "cell" (6 cells).

Why DINOv2 and not VQAScore. The roadmap proposed VQAScore, validated in C66 for trait loss (AUC 0.885). Checked on
C79's 72 tap-restricted pictures against Alessandro's blind trait loss (computed 2026-10-18, before this design was
fixed), VQAScore tracks the eye poorly (Spearman 0.31; AUC 0.60 for any loss), DINOv2 well (Spearman 0.70; AUC 0.86
for any loss, 0.91 for a loss ≥ 0.2; 0.96 for "a different person"). CSD 0.63, pixel RMS 0.45. That check was made on
the same kind of picture C87 produces, but it is post hoc: hence the blind control below.

**Blind control (decides whether the primary measure may be used).** A random sample of 36 of the 156 renders
(RNG seed 8787, stratified: 12 forward, 12 backward, 12 single), plus the 6 baselines and 6 repeats, labelled blind by
Alessandro with C79's page and C75's positive questions. Rule: **Spearman between D(X) and the eye's trait loss
1 − R on the 36 ≥ 0.50.** If it fails, no C87 verdict is drawn from DINOv2; the primary rules are recomputed on the
eye's trait loss after labelling all 156 (a second, larger labelling round, decided then).

Reported, deciding nothing: CSD and VQAScore distances, skin and person on the blind sample.

## 4. Decision rules (fixed now)

Increments along the forward windows, per cell: Δ_k = f(F_k) − f(F_{k−1}), k = 3…11, with f(F_2) as the first value
and f(F_11) = 1.

1. **Q1 — step or slope.**
   * **Step:** in ≥ 4 of 6 cells one single increment Δ_k ≥ 0.40, **and** the same k in ≥ 3 of those cells.
   * **Gradual:** in ≥ 4 of 6 cells no increment exceeds 0.25.
   * Otherwise: mixed.
2. **Q2 — hub tap.** For each single tap k = 3…10, f(S_k) per cell.
   * **Tap 7 is a hub:** f(S_7) is the largest single-tap share in ≥ 4 of 6 cells **and** mean f(S_7) ≥ 0.30.
   * **Tap 6 is a hub:** same rule for tap 6.
   * **No hub:** no single tap has mean f(S_k) ≥ 0.30.
   * Otherwise (a hub other than 6 or 7, or a share ≥ 0.30 without the 4-of-6 lead): reported, no verdict.
3. **Q3 — interaction (reported with a direction, not a verdict on size).** For k = 3…11, the complementary pair
   F_{k−1} + B_k covers all taps once. Report, per cell and k, s_k = f(F_{k−1}) + f(B_k). DINOv2 distances are not
   additive, so s_k < 1 is read as "the halves together fall short" only if it holds for **the eye** too on the blind
   sample (complementary pairs drawn into it where possible).
4. **Concordance with C79.** The gate renders give C79's three conditions again; their D(X) must reproduce
   `data/te_tap_isolation_metrics.csv` to the third decimal (same images, same code).

## 5. Labelling and order

* Key, sample and schedule are written and committed before any label; labels are committed as downloaded before any
  count (as C75/C79).
* The tally script is written and committed, with a selftest, before it is run on the labels.
* Renders are made by Antigravity from a directive; the plan (`data/te_tap_windows_plan.csv`) and the queue script are
  committed before the first render. **This pre-registration is committed before the plan.**

## 6. Limits known in advance

* One edit (L06), three characters, two seeds: six curves.
* DINOv2 measures how much the picture changed, not which traits were lost; the blind control checks that the two go
  together here, but only on 36 pictures.
* The tap push is the conditioning difference of the full edit. Restricting it to some taps is not the same as
  editing the encoder so that only those taps change: the encoder's own later layers are bypassed.
