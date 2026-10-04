# Pre-registration C49 — is a preset coherent inside a prompt family?

Written 2026-10-04, before any render. Code: `experiments/prompt_family.py` (plan, queue,
repro, count), `experiments/analyze_prompt_family.py` (scoring),
`experiments/build_prompt_family_eye_page.py` (eye page). Exploratory basis:
`style_vs_subject_exploration.md`.

## Claim under test (Alessandro, 2026-10-04)

*"Once a prompt style is set, editing the weights gives a coherent style across the
generations made inside that family; build presets for the prompt styles you use most to
shape your own aesthetic — the price is a little more noise."*

Phase 1 (this run) tests coherence and measures the cost. "You can always clean it up
later" is **phase 2**, not tested here.

## Design

- **Families** (style prefix): `F1cartoon` "Cartoon style illustration.", `F2oil` "Oil
  painting.", `F3photo` "Photograph.".
- **Subjects** (6): blacksmith, rally, fox, still life (the C1–C4 texts of
  single_blocks_styles without their prefix), fisherman, lighthouse (new). Prompt = prefix +
  space + subject text.
- **Seeds**: 5772156, 1414213 (new to the project).
- **Arms** (doses = Alessandro's calibrated styles doses): blk16 +0.30, blk20 +0.45,
  blk23 −0.30, blk26 +0.15, blk27 −0.25; **control** blk09 +0.45 (a middle block, expected not
  to be family-coherent); **combo** = blk16 +0.20, blk20 +0.30, blk23 −0.20, blk27 −0.10 (an
  example preset; Alessandro may replace it before launch, with a commit to this file).
- 3 × 6 × 2 × 8 = 288 renders + 1 REPRO (C3_fox baseline, seed 2718281, must equal the
  existing file).

## Measures

Per image the 23 style features; per arm dF = feature change against its own baseline,
each feature divided by its SD over the 36 baselines.

- **W** (within family): mean cosine of dF between different subjects of the same family,
  same seed.
- **B** (between families): mean cosine between prompts of different families, same seed.
  Both W and B compare different subjects, so W − B isolates the family.
- **S** (seed floor): cosine between the two seeds of the same prompt.
- **Cost** (descriptive): share of images where the arm raises high-frequency share, edge
  density, LBP entropy, GLCM contrast.

## Decision rules (tested arms: the five single blocks + combo; control reported separately)

- **H1 — the family matters:** W > B on ≥ 5 of 6 arms and median (W − B) ≥ 0.10 →
  supported; W > B on ≤ 3, or median gap < 0.05 → refuted; otherwise inconclusive.
- **H2 — coherence is usable:** median W ≥ 0.40 → supported; < 0.25 → refuted; otherwise
  inconclusive. (Exploratory value on the cartoon family, late blocks: 0.38.)
- **H3 — middle blocks are not family-coherent:** control blk09 + 0.45 has W below the median
  W of the tested arms.

## The eye (before any number)

For each arm × family, the six subjects × two seeds, base beside preset. Questions: does the
preset give these six pictures a common, recognisable look (yes / partly / no)? Is the cost
acceptable (yes / partly / no)? If eye and rules disagree, the disagreement is reported.

## Known limits

Three families, six subjects, two seeds. The combo is one example, not an optimised preset.
"Coherent" here means the same *direction of change*, not identical results.

## Amendment 1 (2026-10-04, before any render)

At Alessandro's request four **Style-band** arms are added, at his calibrated doses:
blk03 +0.40 ("natural light, three-dimensional lighting"), blk06 +0.45 ("more colour, more
stylised"), blk13 −0.45 ("organic, cute, tidy"), blk17 +0.40 ("subject synthesis, more
generic"). Renders: 3 × 6 × 2 × 12 = 432 + 1 REPRO = **433**. H1–H3 are unchanged (same
tested arms, same control). New:

- **H4 — the Style band is less family-coherent than the late blocks** (Claude's prediction,
  from the exploration: middle blocks ≈ 0.10 against late ≈ 0.38 within the cartoon family).
  Median W of the four Style arms < median W of the tested arms − 0.10 → supported; ≥ the
  tested median → refuted; otherwise inconclusive. W > B for each Style arm is reported.
