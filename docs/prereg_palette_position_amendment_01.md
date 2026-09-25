# Amendment 01 to `docs/prereg_palette_position.md`

- **Written:** 2026-09-25
- **Amends:** §5.3 and §5.4 of `docs/prereg_palette_position.md` (committed `a9c8341`).
- **Everything else in that document is unchanged and remains in force.**

## 0. Why this is an amendment and not a rescue

At the time of writing, `experiments/measure_palette.py` has run §5 and produced
`data/palette_instrument_check.csv` and `data/palette_position.csv`. The latter holds
**per-cell measurements only**: 240 rows of `Delta` vectors, one per arm/prompt/seed.

**No test, no contrast, no p-value, no verdict and no arm-versus-arm comparison has been
computed.** `data/palette_tests.csv` and `data/palette_recurrence.csv` do not exist.
Nothing is yet known about whether any arm separates from any other.

That is the only condition under which a pre-registration may be amended, and it is the
reason this is a separate, dated document committed on its own rather than a silent edit
to the frozen one.

## 1. What went wrong

§5.3 specified the noise floor as **a single number from a single pair of baselines**
(prompt S1, seeds 42 and 777). §5.4 then required only that the positive control
"exceed the floor of check 3".

Two point estimates compared with no margin and no distribution is not a test. The run
satisfied it exactly as written:

| quantity | value |
|---|--:|
| noise floor, one pair (S1 seed 42 vs seed 777) | 2.595891 |
| positive control, +10 degree hue rotation | 2.627692 |
| margin | **+1.2%** |

The script recorded PASS, correctly, against the rule as drafted. But a margin of 1.2%
over a floor estimated from a single pair does not show that the instrument can see a
hue rotation. It shows that **a 10 degree hue rotation sits at the noise floor**:
rotating an image's hue by 10 degrees moves its palette about as far as generating a
different image with a different seed.

Two readings remain open and they are not distinguishable from what has been measured:

1. The instrument is nearly blind to hue at this corpus size.
2. A 10 degree rotation is simply a small perturbation in CIELAB — the recorded shift was
   `|Delta a*| = 1.4647`, `|Delta b*| = 0.1066`, near the just-noticeable difference — and
   the instrument would see a larger one perfectly well.

Proceeding to F4 without separating these two would mean computing arm statistics on an
instrument of unknown sensitivity. Under §10 of the frozen document, a negative result
from a blind instrument is not a negative result, so that path produces nothing usable
either way.

## 2. §5.3 replaced — the floor is a distribution

The noise floor is estimated over **every within-prompt pair of baseline seeds across all
eight style prompts**: 8 prompts x C(5,2) = **80 pairs**.

Report, for both `D_pal` and `||Delta||`: mean, standard deviation, median, **95th
percentile** and maximum. Write every row to `data/palette_instrument_check.csv`.

From this point on, **the reference quantity is the floor's 95th percentile**, not its
mean and not a single pair. Every later number in this study is expressed as a multiple
of it.

## 3. §5.4 replaced — the positive control becomes a sensitivity curve

The control is run at **four hue rotations: +10, +30, +90 and +180 degrees**, applied to
**at least eight baselines, one per prompt**, and averaged per angle. Record the mean
`D_pal`, the mean `|Delta a*|` and `|Delta b*|`, and the ratio to the floor's 95th
percentile, for each angle.

**PASS requires the +180 degree rotation to exceed the floor's 95th percentile by a
factor of at least 1.5.** A deliberate hue inversion that cannot clear the noise of a
seed change by half again is not a detectable signal.

**Record the smallest angle that clears the floor's 95th percentile.** That number is the
**detection threshold of this instrument**, it is written into
`data/palette_instrument_check.csv`, and it is quoted in any page that ever cites this
study. An instrument whose threshold is unknown cannot support a claim.

## 4. New stop condition

If +180 degrees does not clear `p95 x 1.5`:

- Block F **ends here**.
- No arm statistic, contrast or verdict is computed.
- The recorded outcome is **"instrument insufficient at this corpus size"** — explicitly
  not "no colour effect". The distinction is the whole point of §00 of the notebook and
  it must not be blurred in the write-up.

## 5. New condition carried forward into F4

When the arms are eventually measured, their `D_pal` displacements are compared against
the detection threshold from §3 **before** any p-value is interpreted. If an arm's
displacement falls below the detection threshold, that arm is reported as
**uninterpretable**, whatever its p-value says. A significant test on a quantity the
instrument cannot resolve is a significant test on noise.

## 6. What is not changed

Extraction (§3), the two representations and their statistics (§4), the controls reused
(§6), the decision rules (§7), the free parameters and the `N = 8 / 15 / 24` sensitivity
(§8), the pitfalls (§9) and the outputs (§11) are unchanged and remain binding. In
particular §7 still stands: an all-negative outcome, if it is ever reached with a
demonstrably sensitive instrument, is a publishable result and is written up as one.
