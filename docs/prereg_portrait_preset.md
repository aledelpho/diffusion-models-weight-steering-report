# Pre-registration C52 — does a preset calibrated by eye on four characters carry over to three others, and keep who they are?

Written 2026-10-05, **before any portrait was rendered and before the preset exists.** Phase A
(the calibration atlas) is exploratory; this document fixes, in advance, how phase C will judge the
preset Alessandro builds from it. Code: `experiments/portraits.py` (phase A plan, queue, repro,
count); the phase C plan and `experiments/analyze_portrait_preset.py` will be written and committed,
tested on synthetic data, **before any phase C render**, and must implement exactly the rules below.

## Claim under test (Alessandro, 2026-10-05)

*Looking at what each block does to portraits of a few characters, I can calibrate a preset that
gives other characters drawn the same way the same look, without turning them into someone else.*

Two parts: **transfer** (the same change on characters not seen during calibration) and
**identity** (the character stays the same person).

## Material

Prompt frame, fixed: `Western comics style, close-up portrait, frontal view.` + character text +
`white background, simple background.` Texts in `experiments/portraits.py`.

| set | characters | used for |
|---|---|---|
| calibration | D1 dwarf paladin, E2 elf rogue, O4 half-orc fighter, G5 gnome wizard | phase A atlas (seeds 2236067, 1732050) and phase C |
| held out | H3 halfling druid, R6 dragonborn cleric, T7 tiefling bard | **phase C only** — never rendered before the preset is frozen |

The held-out texts are frozen as committed with this document (T7: "jellow" corrected to "yellow"
before any render).

## The three phases

- **A — atlas (exploratory).** 4 characters × 2 seeds × (baseline + 28 blocks × 2 signs at the v4
  doses) + 1 reproduction row = 457 renders. Alessandro reads it on `benchmark_portraits/presets.html`.
- **B — freeze.** Alessandro writes the preset as a 34-slot `vectors_override` (any number of single
  blocks, any signed doses). It is committed as `presets/portrait_preset_alessandro.json`, with his
  description of the intended look in one or two sentences, **before** phase C is planned. Once
  committed it is not changed; a second preset is a new pre-registration.
- **C — test.** 7 characters × 4 new seeds (2645751, 3316624, 3605551, 4123105) × {baseline, preset}
  = 56 renders + 1 reproduction row. The first row is queued alone and must reproduce an existing
  phase A baseline pixel for pixel before the rest runs.

## The eye, first

Before any number of phase C is computed, Alessandro answers on an eye page (base beside preset, all
seeds), and the answers are committed to `data/portrait_preset_eye_alessandro.csv`:

1. per held-out character: *does the preset give it the look you calibrated?* yes / partly / no;
2. per held-out character: *is it still the same character?* yes / partly / no;
3. per character: *is the cost (noise, artefacts, deformation) acceptable?* yes / partly / no.

Declared, not blind: he built the preset and knows which image carries it (results page 20).

## Measures

**Look (style features).** The 23 statistics of `experiments/style_features.py`, each divided by its
SD over the 28 phase C baselines. dF = preset − baseline, per character and seed.

- **W_held** — mean cosine of dF between two *different* held-out characters at the same seed
  (3 pairs × 4 seeds = 12 values; the median is reported).
- **W_cal** — the same among the four calibration characters (6 pairs × 4 seeds = 24).
- **S** — cosine of dF between two seeds of the *same* character (6 seed pairs × 7 characters = 42):
  how much the preset agrees with itself.

**Identity (face embedding).** InsightFace `buffalo_l` (ArcFace recognition model), detection size
640×640, largest detected face, L2-normalised embedding; cosine similarity.

- **ID_edit(c, s)** = cos(baseline, preset) for character c at seed s.
- **ID_seed(c)** = mean cos between baselines of c at different seeds (6 pairs): how much the same
  prompt already changes the face from one seed to the next.
- **Detection gate.** A character enters the identity test only if a face is detected in all 8 of
  its phase C images. A character that fails the gate is judged by eye only, and the failure is
  reported (expected for R6, whose face is not human).

## Decision rules

**Gate G_S (pitfall 89).** If median S < 0.50, the preset does not agree with itself across seeds,
and H1–H2 are reported as *uninformative*, not as refuted.

- **H1 — the look transfers.** median W_held ≥ 0.40 → supported; < 0.25 → refuted; otherwise
  inconclusive. (Same threshold as C49 H2.)
- **H2 — no worse than on the calibration characters.** median W_held ≥ median W_cal − 0.15 →
  supported; < median W_cal − 0.30 → refuted; otherwise inconclusive.
- **H3 — identity holds.** Over the held-out characters that pass the detection gate:
  supported if, for every one, median_s ID_edit > ID_seed **and** the median of ID_edit over them is
  ≥ 0.50; refuted if median_s ID_edit ≤ ID_seed for at least half of them; otherwise inconclusive.
  If no held-out character passes the gate, H3 is *untestable* and reported as such.
- Reported alongside, not decisive: the same three numbers on the calibration characters; the eye
  answers against each rule; the standard quality metrics of C50 (BRISQUE, CLIP-IQA) per character.

## Known limits

- One preset, built by one person who also judges it.
- Three held-out characters; W_held rests on 3 pairs per seed.
- ArcFace is trained on photographs of human faces; on comic drawings its similarities are lower and
  less reliable, which is why its rule is relative to ID_seed and why the eye is asked first.
- One style (Western comics, white background). Nothing here says the preset works in another style.

## Amendment 1 (2026-10-05) — a blind forced choice, added after the measurements existed and before anyone read them

**Timing, stated exactly.** Written after Antigravity computed `data/portrait_preset_style_features.csv`
and `data/portrait_preset_faces.csv` (step 4 of the directive), and before `--test` was run. Neither the
analyst nor Alessandro has opened either file or seen any W, S or ID value. Alessandro's eye pass is
committed (`c285253`, all "yes"). The reason for the amendment is that pass: the rater built the
preset and, by his own account, could not stop seeing the pattern he had calibrated. The new test
does not use the measured files at all, so its outcome cannot have been shaped by them.

**Material.** The 28 phase C pairs (7 characters × 4 seeds), baseline and preset side by side at the
same size, left/right assigned at random (`numpy.random.default_rng(52)`), one sheet per pair. The key
is written to `data/portrait_preset_blind_key.csv` and committed **before** any observer is run. A
second set of sheets with every pair mirrored is the position control.

**Observers.** Model observers, as in the centre-push eye veto: each is a fresh model instance that
receives only one sheet and the questions below, never the repository, the preset, the description
of the hypothesis or which side is which. Three observers per sheet on the original set (M), three
on the mirrored set (M').

**Questions, verbatim.**
1. "Which of the two portraits looks more like an American comic leaning toward animation — flatter
   colours and cleaner lines? Answer LEFT or RIGHT."
2. "Do the two portraits show the same character (the same person, even if drawn differently)? Answer
   YES or NO."

**Rules.** Per sheet, the majority of three.

- **Position gate.** If, on the mirrored set, the majority names the same *side* as on the original
  set in more than 75% of pairs, the observers are reading position, not content: H4 and H5 are void.
- **H4 — the look is visible to someone who was not told what to look for.** On the 12 held-out pairs,
  the preset is chosen in ≥ 9 of 12 on the original set **and** on the mirrored set → supported; in ≤ 6
  of 12 on either → refuted; otherwise inconclusive. Exact one-sided binomial p against 1/2 reported.
- **H5 — the character is kept.** "YES" in ≥ 9 of the 12 held-out pairs on both sets → supported; ≤ 6
  of 12 on either → refuted; otherwise inconclusive.
- Calibration pairs (16) are reported alongside and decide nothing.
- Human observers who have not seen the project may answer the same sheets later; their answers are
  reported, not scored, unless a further amendment registers them first.

**Code.** `experiments/portrait_preset_blind.py` (sheets, key, tally), committed with this amendment.
