# Pre-registration — Does the edit move the palette's *position*, or only its shape?

- **Written:** 2026-09-25
- **Status at writing:** no measurement has been run. No script exists yet.
- **Corpus:** existing renders only. **No new renders are generated for this study.**
- **Supersedes:** nothing.
- **Relates to:** `docs/prereg_shared_axis.md`, `experiments/arm_coherence.py`,
  `data/arm_coherence_tests.csv`.

---

## 0. Honesty note, written before any number exists

This study was proposed by the project's observer (A.D.) after looking at renders he
had already seen many times. He reports, in his own words, that in some images "it is
obvious that the colour is changing" and that a given preset "is influencing the images
it digests heavily and coherently" — an impression that the published measurements do
not support.

That makes this study **post-hoc in spirit**. The images are not new and both the
observer and the analyst have already formed expectations about them. The only thing
standing between that and a result shaped to fit the expectation is this document:
every threshold, statistic, control and decision rule below is fixed *before* any
measurement is taken. If this study is ever written into the notebook, this paragraph
goes into the page with it.

---

## 1. The gap this study targets

The 23-feature style vector already contains four colour features:

| feature | what it measures |
|---|---|
| `color_n_effective` | how many colours are effectively present |
| `color_top4_cluster_share` | how concentrated the palette is |
| `color_cluster_entropy_norm` | how evenly the palette is spread |
| `colorfulness_hs` | Hasler & Süsstrunk colourfulness |

Three of these appear among the eight largest loadings of both axis definitions in
`data/shared_axis_loadings.csv`, so the edits demonstrably move them.

**All four are scalar summaries of the palette's *shape*. None of them encodes *where*
the palette sits in colour space.** An edit that rotates an image from warm orange to
cold blue while preserving the number of clusters, their concentration and the overall
colourfulness registers as approximately zero change on every one of them.

That is a specific, testable blind spot, and it matches the observer's specific report.
This study asks whether anything lives in it.

## 2. Two questions, deliberately kept apart

The observer's proposal contains two different questions. Merging them would make the
result uninterpretable, so they are measured separately and reported separately.

- **Track A — direction.** Does the edit displace the palette's *position* in colour
  space in a consistent direction across seeds and across prompts?
- **Track B — recurrence.** Do images sharing an arm end up with *the same swatches*
  more than images sharing a seed or a prompt?

Track A is comparable, by construction, with every coherence number already published.
Track B is the observer's original proposal in its pure form and has no published
counterpart.

## 3. Extraction — frozen

**Input.** The stage-9 style corpus, exactly the cells used by
`experiments/shared_axis.py`: prompts S1–S8, five seeds each, `baseline` plus the six
arms (`preset_pos_1x`, `preset_pos_2x`, `blockshuf_neg_1x`, `blockshuf_neg_2x`,
`rand_pos_1x`, `rand_pos_2x`). 40 cells per arm, 40 baselines.

**Decoding.** Each render is read at full resolution and converted to 8-bit sRGB. No
resizing, no cropping, no dithering anywhere in the pipeline.

**Colour space.** sRGB -> linear RGB -> CIE XYZ (D65) -> CIELAB. The implementation is
`skimage.color.rgb2lab` if `scikit-image` is importable; otherwise an explicit
conversion in the script. Whichever is used is recorded in the output.

**Quantisation (Track B only).** Median cut, `N = 15` colours, via
`PIL.Image.quantize(colors=15, method=Image.Quantize.MEDIANCUT, kmeans=0,
dither=Image.Dither.NONE)`. Each palette entry carries a weight equal to its pixel
fraction; weights sum to 1.

**No merging step.** The original proposal included collapsing near-identical swatches
into an average. It is deliberately dropped: the transport distance in §4 already
handles near-duplicates, and a merge threshold would add a free parameter with no
principled value. Fewer free parameters means fewer places to tune towards a hoped-for
answer without noticing.

## 4. Representations and statistics — frozen

### Track A: the 9-dimensional position vector

Computed over **all pixels**, not over the quantised palette (so Track A does not
depend on `N`):

```
v = (mean L*, mean a*, mean b*,
     sd L*,   sd a*,   sd b*,
     corr(L*,a*), corr(L*,b*), corr(a*,b*))
```

Each of the nine components is standardised using the **mean and standard deviation of
the stage-9 baselines only**, computed once over all baselines and applied unchanged to
every cell — the same convention as `experiments/arm_coherence.py`. One
standardisation, not one per arm and not one per prompt (pitfall 33).

`Delta(arm, prompt, seed) = z(edited) - z(baseline)` at identical prompt and seed.

Statistics, all three identical in form to `arm_coherence.py` so the numbers are
directly comparable with `data/arm_coherence.csv`:

1. `||Delta||`, reported as a multiple of the seed-change null.
2. Mean cosine between `Delta` of different seeds within the same prompt.
3. Mean cosine between per-prompt mean `Delta` across different prompts.

Plus, for comparability with Block B, the split-half statistic `S` over the same 35
four-versus-four prompt splits used in `experiments/shared_axis.py`, with the
**sign-randomised** null of `docs/prereg_shared_axis.md` §3.

### Track B: palette distance

Ground metric between two Lab swatches: **CIEDE2000**.

Distance between two palettes: the exact earth mover's distance over the 15x15 cost
matrix, with the pixel-fraction weights as supplies and demands. Solved as a linear
program (`scipy.optimize.linprog`, method `highs`) or `ot.emd2` if POT is available.
The solver actually used is recorded in the output. The problem is 15x15; no
approximation is permitted.

Write this distance `D_pal`.

For each prompt `P` and each arm `A`:

- `W(A,P)` = mean `D_pal` over all pairs of cells in arm `A` at prompt `P` with
  different seeds — *within-arm* distance.
- `B(P)` = mean `D_pal` over all pairs of cells at prompt `P` and the **same** seed but
  **different** arms — *between-arm* distance.
- `R(A,P) = B(P) - W(A,P)`. Positive means palettes cluster by arm rather than by seed.

### Tests — frozen

**The unit is the prompt** (eight of them). Seeds are repeated measures within a
prompt, not independent observations (pitfall 17).

- Exact sign-flip permutation over the eight prompts. Floor `2/2^8 = 0.0078125`.
- Holm correction across the arms tested, within each track.
- **The primary contrast in both tracks is `preset` minus `scramble` (`rand_pos`), not
  `preset` minus zero.** That an edit beats "no edit" is already known and is not what
  is in dispute. What is in dispute is whether a structured edit beats a random one.

## 5. Instrument check — mandatory, runs first, has a stop

No arm result may be computed until all four of these have been run and recorded. This
is §00 of the notebook applied to this study's own instrument.

1. **Determinism.** Quantise the same file twice. The palettes must be byte-identical.
   Not identical -> **STOP**, the pipeline is nondeterministic and nothing downstream
   means anything.
2. **Zero on identity.** The two pixel-identical seed-42 baselines must give
   `D_pal = 0.0` exactly and nine-dimensional vectors equal under float equality.
   Not zero -> **STOP**.
3. **The floor.** `D_pal` and `||Delta||` between two baselines of the same prompt at
   different seeds. This is the noise floor of colour space. It is reported *before*
   any arm number, and every arm result is expressed as a multiple of it. Without it
   the word "large" has no meaning.
4. **Positive control.** Take a baseline, rotate its hue by a known +10 degrees, and
   run both tracks on the result. Track A's `a*`/`b*` means must move and Track B's
   `D_pal` must exceed the floor of check 3. If a deliberate, visible hue rotation does
   not register, the instrument is blind and no negative result from it is
   interpretable -> **STOP**.

## 6. Controls reused, not reinvented

Non-negotiable, because the point of the study is comparability with what is already
published:

- the same six arms, the same eight prompts, the same five seeds;
- the same scramble arm as the control;
- the same exact sign-flip permutation and the same Holm correction;
- the same seed-change null construction;
- the same standardisation convention.

A new metric that has never been calibrated against these controls cannot be compared
with `+0.143` from `data/arm_coherence_tests.csv`, and a number that cannot be compared
cannot overturn anything.

## 7. Decision rules — frozen before the first measurement

**Track A**

- `preset` separates from `scramble` on cross-prompt coherence at Holm-corrected
  `p < 0.05` -> **the 23-feature instrument was blind to colour direction.** The
  existing conclusions that rest on it are flagged for revision. They are *flagged*,
  not changed: a published status is never changed inside the run that found the
  reason to change it.
- No separation -> colour direction adds nothing the existing features did not already
  carry. The observer's impression is then attributed to seed-fixed coherence, which
  the random control shares.

**Track B**

- `R(preset,P) - R(scramble,P)` positive beyond the permutation null at Holm-corrected
  `p < 0.05` -> palette recurrence is real and arm-specific.
- Otherwise -> swatch recurrence is a property of holding the seed fixed, not of the
  preset.

**Disagreement.** If the two tracks point in opposite directions, the verdict is
`ambiguous`, both are reported in full, and no claim is promoted. A disagreement
between two honest measurements is a result, not a problem to be resolved by choosing
the nicer one.

**The all-negative outcome is a result.** If neither track separates anything, that is
written up at the same length and with the same prominence as a positive one would
have been, and it closes the question of whether the observer's eye is tracking
arm structure or seed structure.

## 8. Free parameters, declared

| parameter | value | chosen by |
|---|---|---|
| palette size `N` | 15 | the observer, before any result existed |
| quantisation | median cut | standard (Heckbert 1982), deterministic |
| ground metric | CIEDE2000 | perceptual standard |
| merge threshold | none | deliberately removed, see §3 |

**Sensitivity.** Track B is re-run at `N = 8` and `N = 24`. The primary remains
`N = 15`. All three are reported. **If the verdict changes with `N`, the verdict is
`ambiguous`** — a finding that depends on the palette size is a finding about the
palette size.

## 9. Pitfalls this design is built against

- **17** — seeds are repeated measures. The unit of the test is the prompt.
- **33** — one standardisation, computed on baselines, applied to everything.
- **36** — attenuation. Aggregated split-half coherence and pairwise cross-prompt
  cosine are different quantities and are never quoted as if interchangeable.
- **30** — this study writes to its own output folder, shared with no other experiment.
- **40** — every number in any page that cites this study is read from a file in
  `data/`, never typed.

## 10. What would kill this study

- The positive control in §5.4 fails: the instrument cannot see a hue rotation, so
  nothing it says about colour means anything.
- The floor in §5.3 is of the same order as the arm displacements: colour space is too
  noisy at this corpus size to answer the question, and the honest outcome is
  "underpowered", not "no effect".
- The verdict flips between `N = 8`, `15` and `24`.
- Track A and Track B disagree.

Any of these, and no claim is promoted to the notebook.

## 11. Outputs

Scripts:

- `experiments/measure_palette.py` — extraction, both representations, per-render rows.
- `experiments/palette_coherence.py` — statistics, tests, verdicts.

Data:

- `data/palette_instrument_check.csv` — §5, written first.
- `data/palette_position.csv` — Track A, per cell.
- `data/palette_recurrence.csv` — Track B, per arm and prompt.
- `data/palette_tests.csv` — the contrasts, p-values, Holm-corrected p-values,
  verdicts, and the `N` sensitivity rows.

No figure is registered and no page is written in the same run that produces these
files.
