# Pre-registration — Does the edit change how much the output wobbles between seeds?

- **Written:** 2026-09-25
- **Status at writing:** no script exists. No statistic of this kind has been computed on
  stage 7, which is the primary corpus below.
- **Corpus:** existing renders only. **No new renders are generated for this study.**
- **Relates to:** `docs/prereg_palette_position.md` + Amendment 01,
  `experiments/arm_coherence.py`, `data/palette_instrument_check.csv`.

---

## 0. Where this hypothesis came from, and why that matters

On 2026-09-25 the project's observer (A.D.) asked, in his own words, whether moving the
weights might be "ruining some parts and amplifying others", sometimes "injecting noise,
because the signal passes through parts we altered".

Immediately afterwards the analyst **looked at existing numbers** — the `W_within_arm`
column of `data/palette_recurrence.csv` against the per-prompt baseline floor in
`data/palette_instrument_check.csv` — and noticed, on a handful of stage-9 prompts, that
the preset arms appeared *less* dispersed across seeds than the baselines while
`blockshuf_neg_1x` appeared *more* dispersed on S3.

**That look happened.** The hypothesis is therefore not blind with respect to stage 9,
and no confirmatory test may be run there. Anything computed on stage 9 for this question
is a description of the data that generated the hypothesis.

This document resolves that by moving the confirmatory test to a corpus that has never
been examined for this question.

## 1. The question

For a given prompt, does applying an edit change **how far apart the outputs of different
seeds land**?

- Dispersion goes **up**: the edit injects variability — the observer's "injecting noise".
- Dispersion goes **down**: the edit constrains the output — it makes the model answer
  the same prompt more consistently whatever the seed.
- Dispersion unchanged: the edit moves the output without changing its spread.

All three are substantive answers. The third is the null and it is reported as a result.

This is a different question from everything measured so far. Every previous study
measured **where** the edit moves the output. This one measures **how much the output
stops or starts moving on its own**.

## 2. Corpora, in order

| role | corpus | prompts | seeds | conditions |
|---|---|--:|--:|---|
| **primary, confirmatory** | `data/style_features_stage7.csv` | **24** | 5 | baseline + 6 arms |
| secondary | stage 7, palette/CIELAB space | 24 | 5 | baseline + 6 arms |
| **exploratory only** | stage 9 style prompts S1–S8 | 8 | 5 | baseline + 6 arms |

Stage 7 is fully balanced: every (condition, prompt) cell holds exactly five seeds.

The secondary requires extending `experiments/measure_palette.py` to the stage-7 renders.
That is a re-measurement of existing images; **no render is generated**.

Stage 9 results are reported in a clearly separated section headed **"the data that
generated the hypothesis"** and carry no p-value, no verdict and no claim.

## 3. The statistic — frozen

For a condition `c` (a baseline or an arm) and a prompt `P`, **seed dispersion** is the
mean distance between the outputs of that condition at that prompt over all
`C(5,2) = 10` seed pairs:

```
V(c, P) = mean over seed pairs (s_i, s_j) of  dist( x(c,P,s_i), x(c,P,s_j) )
```

Two distances, giving two spaces, reported separately and never pooled:

- **Style space.** The 23 style features, standardised once using the mean and standard
  deviation of the **stage-7 baselines**, applied unchanged to every cell (pitfall 33).
  `dist` is the Euclidean distance between standardised vectors.
- **Palette space.** `D_pal`, the CIEDE2000 earth mover's distance of
  `docs/prereg_palette_position.md` §3–§4, `N = 15`.

The contrast, per arm and prompt:

```
R(arm, P) = V(arm, P) - V(baseline, P)
```

`R > 0` means the edit increases seed-to-seed wobble. `R < 0` means it reduces it.

A ratio `V(arm,P) / V(baseline,P)` is reported alongside for readability. **The test is
run on the difference**, not the ratio; the ratio is unstable when the denominator is
small and it is descriptive only.

## 4. Tests — frozen

- **The unit is the prompt**: 24 in the primary. Seeds are inside `V`, never counted as
  observations (pitfall 17).
- Exact sign-flip permutation over prompts. Floor `2/2^24 = 1.192e-07`.
- **Holm across the six arms**, within each space, separately.
- Two-sided. This study has no preferred direction: an edit that stabilises and an edit
  that destabilises are equally interesting and the write-up treats them as such.

**Secondary contrast, pre-specified:** `R(preset) - R(scramble)`, paired by prompt, same
test. This asks whether a *structured* edit changes dispersion differently from a random
one — the question every other study in this project has ended up asking.

## 5. Instrument conditions carried over

- **Palette space only:** Amendment 01 §5 applies unchanged. Before any p-value is
  interpreted, `|R|` is compared with the detection threshold established for that
  corpus. An arm whose `|R|` falls below the threshold is reported **uninterpretable**,
  whatever the test says. The stage-7 threshold is established by re-running the
  Amendment 01 §2–§3 procedure on stage-7 baselines; the stage-9 threshold does not
  transfer and must not be reused.
- **Style space:** no equivalent threshold exists, so none is invented here. Instead the
  floor is `V(baseline, P)` itself, which is measured for every prompt, and every `R` is
  reported as a fraction of it.

## 6. Decision rules — frozen before the first measurement

Per space, per arm:

- `R` significantly **positive** at Holm-corrected `p < 0.05` -> **the edit injects
  variability.** The observer's "injecting noise" reading is supported for that arm.
- `R` significantly **negative** -> **the edit stabilises the output across seeds.** This
  would be a new and separately interesting result: it would mean part of what reads as
  a preset's "coherence" is the model answering more consistently, not the preset
  carrying a style.
- Not significant -> the edit moves the output without changing its spread.

**If the two spaces disagree for the same arm**, the verdict for that arm is `ambiguous`,
both are reported in full, and no claim is promoted.

**If the primary (stage 7) and the exploratory (stage 9) disagree, the primary wins** and
the disagreement is reported. Stage 9 generated the hypothesis; it cannot also judge it.

## 7. What would kill this study

- The stage-7 palette detection threshold turns out to exceed the observed `|R|` values
  for every arm: the palette half is then uninterpretable and only the style space
  speaks.
- `V(baseline, P)` varies so much between prompts that the paired difference is dominated
  by one or two prompts. This is checked before the test: report the per-prompt `R` and
  state whether any single prompt carries more than 40% of the mean. If one does, the
  result is reported as **fragile** and no claim is promoted.
- Stage 7 and stage 9 disagree in sign.

## 8. Pitfalls this design is built against

- **17** — seeds are repeated measures; they live inside `V`, the prompt is the unit.
- **33** — one standardisation, from stage-7 baselines, applied to everything.
- **30** — this study writes only to its own output files.
- **40** — every number quoted anywhere comes from a file in `data/`.
- The specific failure this document exists to prevent: **testing a hypothesis on the
  same data that suggested it.** That is why stage 7 is primary and stage 9 is
  quarantined.

## 9. Outputs

Scripts:

- `experiments/seed_stability.py` — computes `V`, `R`, the tests and the verdicts.
- an extension of `experiments/measure_palette.py` to stage-7 renders (no new renders).

Data:

- `data/seed_stability.csv` — `V` and `R` per condition, prompt and space.
- `data/seed_stability_tests.csv` — contrasts, p-values, Holm-corrected p-values,
  interpretability flags and verdicts, with the corpus named in every row.
- `data/palette_instrument_check_stage7.csv` — the stage-7 floor distribution and
  detection threshold, written **before** any stage-7 palette contrast is computed.

No figure is registered and no page is written in the same run that produces these files.
