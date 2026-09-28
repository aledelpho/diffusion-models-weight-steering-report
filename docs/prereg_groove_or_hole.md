# Pre-registration — a groove or a hole? Targeted presets and the model's repertoire

- **Deposited:** 2026-09-28, before any statistic below was computed on any of the four benches.
- **Status:** frozen. Amendments go at the bottom, dated, never in the body.
- **Renders:** none in Stage A. Stage B (§8) renders only if Stage A produces a candidate.
- **Parent:** [`prereg_mountain_reachability.md`](prereg_mountain_reachability.md) and its
  [amendment 01](prereg_mountain_reachability_amendment_01.md). The measure, the base cloud and the
  standardisation are reused **unchanged**.

---

## 0. What is already known, and what is not

This is written by an analyst who has already seen part of the material. The reader should know
which part.

**Seen before writing:**
- the structure coherence of every group-arm-dose of `benchmark_mappa` (`retro_mappa_reading_result.md`),
  including the knee at 0.200;
- the `blk16` ladder's style and coherence (`leaf_collapse_and_blk16_result.md`);
- the per-block transfer accuracy at each dose (`transfer_test_result.md`);
- the parent study's result: **for three broad presets, R2 refuted** — every arm moved the output
  *away* from the base model's repertoire (`data/mountain_reachability_tests.csv`).

**Not seen, and not computed by anyone:** `d_out`, `Δout` or the visibility ratio `V` (§3) for any
targeted unit — any group, single block, or q/k/v/o projection. The primary quantity of this study is
unobserved.

The coherence gate (§3.3) therefore uses numbers the analyst has seen. It is a gate, not a test, and
it is stated here so it cannot be tuned afterwards.

## 1. The claim being tested

Alessandro, 2026-09-28, answering the parent study's refutation (translated from Italian):

> When presets are that broad, yes. But when they become more targeted they can actually "carve a
> groove", or at least I believe so. For the changes to show, though, they have to be pushed hard
> enough to be visible. Often it takes very "wide" changes to move the output at all.

The parent study tested three **broad** presets, each touching hundreds of tensors. It says nothing
about targeted ones. Two readings make opposite predictions:

- **Groove.** A targeted preset, pushed far enough to be visible but not past the point where the
  drawing breaks, moves the output **toward** what the base model already produces for other
  prompts. The look was on the mountain; the edit re-routed the water.
- **Hole.** Wherever a targeted preset is visible, it moves the output **away** from everything the
  base model produces, and further with dose, as the broad presets did.

The claim contains a dose condition, and the design has to respect it: a groove is only a groove at a
dose where the change is visible and the picture is intact. This study asks whether such a
**window** exists, and for which units.

## 2. Material — four benches, no renders

| bench | units | doses | prompts × seeds | baselines |
|---|---|---|---|---|
| **M** `benchmark_mappa` | 6 groups × 2 signs | 0.020, 0.035, 0.050, 0.080, 0.120, 0.200 | P01, P02 × 42, 777, 1337 | in folder |
| **K** `benchmark_blk16_ladder` | `blk16`, 2 signs | 6 doses | 2 prompts × 3 seeds | from M, verified by G1 |
| **D** `benchmark_profondita` + `_neg` | 28 single blocks × 2 signs | 0.200 | P01, P02 × 3 seeds | from M, verified by G1 |
| **Q** `benchmark_qkvo_atlas` | `wq`/`wk`/`wv`/`wo` × bands b1, b6 × 2 signs = 16 | one | 8 scenes × 3 seeds | from `benchmark_atlas_phase1`, verified by G1 |

`A01` (bench M) is excluded: it carries only `Block_1` and `Block_6` and has no counterpart in the
other benches. The `Text_Fusion`, `Time_Embed` and `Projection` rows of M are excluded, because they
have one dose. The `normscales` rows of Q are excluded as a known dead edit (§5 G3 would exclude
them anyway).

Features: the 23 style features of `experiments/style_features.py`, **unmodified**. Benches K and D
do not yet have them and are extracted with that script before anything else is computed.

## 3. The measure — fixed

### 3.1 Distance from the repertoire (reused from the parent)

- **Space and standardisation:** exactly as the parent §2. The 23 features, z-scored **once** on the
  base cloud `B`.
- **Base cloud `B`:** the parent's, **frozen** at the 409 rows of
  `data/mountain_base_features_style.csv`, 52 prompts. No render from this study enters `B`.
- `d_out(x)` = the minimum Euclidean distance from `x` to any member of `B` whose **prompt text**
  differs from `x`'s. The match is by the SHA-1 of the prompt text, not by prompt id. Prompt ids
  collide in this repository: `S7` is two different prompts
  (`prereg_family_coherence_amendment_01.md`).
- Per cell (condition `c`, prompt `p`, seed `s`):
  **`Δout(c,p,s) = d_out(edit) − d_out(baseline at p,s)`**.
  Negative means toward the repertoire (groove), positive means away (hole).

### 3.2 Visibility

`V(c,p) = ‖ mean over seeds of (z_edit − z_baseline) ‖ / N(p)`

`N(p)` is the median, over all pairs of seeds, of `‖z_b(p,s) − z_b(p,s')‖` for baselines of the same
prompt in `B`.

In words: the part of the edit that is consistent across seeds, measured in units of a change of
seed. **Visible iff `V ≥ 1.0`**: the consistent part of the edit is at least as large as what a new
seed does.

This is a statistical proxy for "visible", not a perceptual one. §6 G_eye is the perceptual check.

### 3.3 Line kept

`L(c,p)` = the mean over seeds of the structure-coherence ratio, edit over same-seed baseline, from
`data/retro_texture_axes.csv` (the corrected estimator of `estimator_precision_defect.md`).
**Line kept iff `L ≥ 0.98`.**

Coherence only discriminates on line-bearing styles (`retro_axes_atlas_result.md` §2). In bench Q
the gate is therefore evaluated on `S1_photo`, `S2_watercolor` and `S8_charcoal` only, and applied
to the condition as a whole. Coherence has also been seen to rate a known artefact as "more line"
(`STORY.md` §VII). That is why §6 G_eye exists.

## 4. Decision rules — frozen before the first distance

### 4.1 Benches M, K, D — a screen, two prompts

With two prompts there is no inference across prompts. Seeds are repeated measures. Stage A on
these benches is a **screen**, labelled as such in every output row.

A condition-dose `(c, d)` is a **groove candidate** iff all four hold:
1. `V ≥ 1.0` on **both** prompts;
2. `L ≥ 0.98` on **both** prompts;
3. `Δout < 0` in **all 6** cells (exact sign test, two-sided p = 0.031, reported, not corrected:
   this is a screen);
4. the mean `Δout` is negative on each prompt separately.

It is a **hole** iff conditions 1 holds and `Δout > 0` in all 6 cells. It is **undecided** otherwise.
Cells that fail condition 1 are **invisible** and are counted but not classified.

**Dose curve (M and K, descriptive).** For each unit, Spearman ρ between dose and the mean `Δout`.
The hole signature is ρ > 0 with the top-dose `Δout` > 0. It is reported, not tested.

### 4.2 Bench Q — confirmatory, eight scenes

Unit: the scene, with its three seeds averaged first. For each of the 16 conditions, an exact
sign-flip over 8 scenes (floor 2/2⁸ = 0.0078), two-sided, Holm-corrected across the 16.

A condition is a **confirmed groove** iff all three hold:
- the mean `Δout` < 0 at Holm p < 0.05;
- the median `V` over the 8 scenes ≥ 1.0;
- `L ≥ 0.98` on the three line-bearing scenes.

It is a **confirmed hole** iff the mean `Δout` > 0 at Holm p < 0.05 with the median `V` ≥ 1.0.

### 4.3 The verdict on the claim

| outcome | condition |
|---|---|
| **supported** | at least one confirmed groove in Q, **or** at least one screen candidate that is confirmed in Stage B (§8) and passes G_eye |
| **screen only** | candidates in M, K or D, none confirmed yet. Stage B is licensed; no claim is made |
| **not supported** | no candidate anywhere, **and** at least half of all visible cells, pooled over the four benches, are holes |
| **undecided** | none of the above |

**A null here is informative only for the units tested.** It would not show that *no* targeted preset
can carve a groove. It would show that none of these 12 group-arms, 2 `blk16` arms, 56 single-block
arms or 16 projections does, at these doses. The report must say so in that sentence.

## 5. Guards — they run before any statistic, and each can stop the study

- **G0 — pipeline control.** Before touching the four benches, the script must reproduce the
  parent's stage-7 R2 row for `preset_pos` (mean Δ 0.501902, Holm 0.002441) to four decimals. If it
  does not, stop: the measure is not the parent's measure.
- **G1 — baseline identity** (pitfall 69). Every perturbed cell's baseline must match on prompt text,
  seed, sampler, scheduler, steps, CFG and resolution, read from the PNG metadata. One mismatch
  aborts that bench.
- **G2 — prompt matching.** Every prompt in K, D and Q must resolve to a prompt text by SHA-1. An id
  with two texts aborts.
- **G3 — edits that never arrived.** Any perturbed render with pixels identical to its baseline
  (maximum channel difference 0) is flagged `dead` and excluded. A condition with more than 10% dead
  cells is excluded whole and reported.
- **G4 — cloud coverage.** For each tested prompt, at least 40 other prompts must remain in `B` after
  the exclusion of its own. If fewer remain, stop.

## 6. The eye, as a gate and not as a judge

**G_eye.** Every condition that passes §4 as a groove, in any bench, is shown to Alessandro before it
is reported as one. He sees it at **1:1 crops**, never downsampled (pitfall 78), mixed with an equal
number of hole and invisible conditions from the same bench, with filenames hashed and without
knowing how many grooves there are.

For each crop he answers one question: *is this a picture the untouched model could plausibly have
produced for some prompt, or does it carry an artefact?* A groove that he marks as an artefact is
reported as **"groove by the statistic, artefact by eye"**. It does not count toward §4.3.

Blinding is already known to fail for visible signatures (page 03). G_eye is therefore a veto, not a
confirmation: it can only remove a groove.

## 7. Predictions — deposited before the first distance

**Alessandro.** Deposited verbatim on 2026-09-28 at 17:14, before the script ran. Original Italian
first, then an English translation. The operational reading is in amendment 02.

> Dipende cosa intendi per solco:
> Io credo che ogni preset sia una manopola che muove milioni di manopole e, di conseguenza, è
> difficile comprendere "cosa" si sia spostato, dato che alcune di esse si muovono in direzioni
> opposte o hanno effetti complementari.
> Credo però che si possano trovare o isolare delle aree che hanno degli effetti diversi che cambiano
> il modo in cui vengono interpretati i prompt, non attraverso ciò che si scrive, ma attraverso i
> collegamenti impliciti tra le parole (nelle sezioni più centrali) e nel modo in cui viene
> sviluppata l'immagine attraverso una black box che facciamo fatica a comprendere.
> Penso che i blocchi iniziali e finali spesso creino artefatti visivi, grana, pixel "sciolti" o
> fuori fuoco, mentre quelli più centrali siano in grado di muovere molto più l'immagine, trovare
> stili diversi o rappresentazioni differenti di quello stesso prompt, su una scala non lineare, ma
> coerente tra seed diversi.
> Credo che siamo lontani dall'avere un controllo su ciò che realmente accade, ma possiamo già usarlo
> per fare uno steering del modello, in modo coerente e riproducibile a parità di famiglie di prompt
> (se calibriamo cosa succede in aree legate allo stile "Comics" stiamo ricalibrando il modello su
> quel prompt, di conseguenza non è sicuro che si avrà qualità altrove, anzi, è probabile che i pesi
> tendano a rovinare ciò che non si stava guardando).

*Translation.* It depends on what you mean by a groove. I believe every preset is one knob that moves
millions of knobs, so it is hard to understand *what* has moved: some of them move in opposite
directions or have complementary effects. I believe, though, that areas can be found or isolated
that have different effects and change how prompts are interpreted. They act not through what is
written, but through the implicit links between words (in the central sections) and through the way
the image is developed inside a black box we struggle to understand. I think the first and last
blocks often create visual artefacts, grain, "loose" or out-of-focus pixels. The central ones can
move the image much more and find different styles or different representations of the same prompt,
on a scale that is not linear but is coherent across seeds. I believe we are far from controlling
what really happens, but we can already use it to steer the model coherently and reproducibly
within a family of prompts. If we calibrate what happens in areas linked to the "Comics" style, we
are recalibrating the model on that prompt, so there is no guarantee of quality elsewhere. On the
contrary, the weights probably tend to spoil whatever was not being looked at.

**Analyst.** I expect the hole reading to dominate.
- In bench M, wherever `V ≥ 1`, I expect `Δout > 0`, rising with dose (ρ > 0) for at least 9 of the
  12 group-arms.
- I expect groove candidates, if any, only among units that keep or raise coherence without a knee:
  `Block_5 neg`, `blk16 pos` at 0.080–0.120, `Block_4` in either sign.
- In Q I expect no confirmed groove.
- I put the probability of the verdict "supported" at about 0.3.

The reason: roughly four fifths of any displacement lies on a shared grain axis
(`e_tutto_scrambling.md`, an upper bound), and grain is exactly what the base cloud does not contain.

## 8. Stage B — confirmation with renders, only if Stage A produces candidates

- **Which:** at most **3** screen candidates, ranked by the mean `Δout`, most negative first. Each
  keeps its dose and sign from Stage A.
- **Where:** 8 new prompts, none of them in `B`: 4 comic portraits and 4 other line-bearing styles
  (pen, ink wash, etching, charcoal). Three seeds. Each candidate plus its baseline:
  8 × 3 × (k + 1) renders, at most 96. `B` is **not** extended with the new baselines.
- **Rule:** the §4.2 rules with Holm across the candidates, then G_eye.
- A candidate that fails Stage B is reported as a screen artefact, with its Stage A numbers beside it.

## 9. Outputs

- `experiments/groove_or_hole.py`, committed **before** it is run;
- `data/groove_cells.csv`, one row per cell with `Δout`, `V`, `L`, `dead` and bench;
- `data/groove_by_condition.csv`;
- `data/groove_tests.csv`, the verdicts, with `stage` = `screen` / `confirmatory`;
- `docs/groove_or_hole_result.md`.

## 10. What this cannot settle

- **The repertoire is the base cloud.** That is 52 prompts, mostly comic portraits and eight
  renderings of one rally car. "Toward the repertoire" means toward *this* sample of what the model
  does, not toward everything it can do. A groove toward a look the model produces only for prompts
  outside the cloud would read here as a hole.
- **23 global features.** A look that differs only locally, or only in colour placement, may not
  register.
- **Visibility is a proxy.** `V ≥ 1` is "as large as a change of seed", not "a person would call it a
  new style". G_eye covers the second half only for grooves.
- **Doses** are the ones already rendered. A window narrower than their spacing can be missed.
