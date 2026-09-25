# Amendment 02 to `docs/prereg_family_coherence.md` — the verdict is withdrawn

- **Written:** 2026-09-25, **after** the pre-registered script was run.
- **Nature:** this amendment **removes** a result. It adds no claim and relaxes no rule.
  Everything below was found by a post-hoc decomposition whose only purpose was to check
  whether the pre-registered statistic measures what its name says. It does not.

---

## 1. What the frozen script produced

`experiments/family_coherence.py`, run unmodified against the pre-registration frozen at
commit `35de33e`, wrote `data/family_coherence_tests.csv` and applied §7 mechanically. For
`preset_pos`, 23 features, 48 prompts:

- W = 0.453497, Bt = 0.281647, **G = 0.171849**, permutation p = 1.0e-04 (floor), Holm 3.0e-04
- reliability ceiling rel = 0.755174, W/rel = 0.600
- bootstrap 95 % interval for W = [0.377728, 0.527168], excludes 0
- Guard R1 (run gap inside A1) = −0.004188, p = 0.4756 — the render run explains nothing
- Guard R2 (cross-run pairs only) G = 0.175974, p = 1.0e-04
- machine verdict: **`holds_and_specific`**

That verdict is **not** to be read as a result. Two reasons, in increasing order of severity.

## 2. The verdict rests on the fourth decimal of an arbitrary constant

Rule 4 of §7 requires G(preset_pos) ≥ 2 × G(rand_pos):

    G(preset_pos) = 0.171849
    2 × G(rand_pos) = 2 × 0.085783 = 0.171566
    margin = 0.000283, i.e. 0.16 % of the threshold

On the 44-prompt robustness set the margin is 0.016126. The 2× factor was fixed in advance
precisely so that it could not be chosen afterwards; that protects against one failure mode
and not against this one. A verdict that changes at the fourth decimal of a number chosen by
hand is not evidence of anything.

## 3. The partition is misspecified — G does not measure what it is named

`experiments/family_coherence_decomposition.py` breaks G into the mean cosine of every
family pair (`data/family_coherence_by_family_pair.csv`). For `preset_pos`:

| pair | kind | n | mean cosine |
|---|---|---|---|
| A1–A1 | within | 153 | +0.4563 |
| A2–A2 | within | 15 | +0.5075 |
| B–B | within | 120 | +0.4920 |
| A1–A2 | between | 108 | +0.4495 |
| A1–B | between | 288 | +0.4249 |
| A2–B | between | 96 | +0.4798 |
| A1–C | between | 144 | **+0.0159** |
| A2–C | between | 48 | **−0.0093** |
| B–C | between | 128 | **+0.0772** |
| C–C | within | 28 | +0.2442 |

Among A1, A2 and B — all of them "Western comics style, bold ink outlines, hatched shadows" —
within-family and between-family are the same number. A2–B (between) exceeds A1–A1 (within).
The entire gap comes from family **C**, whose cosine with every other family is near zero.

C is also not a family. Its eight prompts are eight *different* rendering styles sharing one
subject, which is why its own within-family cosine is only 0.244. In the partition C behaves
as eight singleton families wrongly grouped together.

So G measures **"comics corpus versus the stage9 corpus"**, not "same family versus different
family". And for that contrast family is perfectly collinear with render run — every C prompt
was rendered in `stage9_20260918_085644` and no other family was. Guard R1 tests the run
inside A1 and therefore cannot see this; Guard R2 removes same-run pairs but leaves the
A-versus-C contrast entirely intact, so neither guard was ever able to catch it.

## 4. Restricted to comparable prompts, the sign of rule 4 reverses

`data/family_coherence_restricted.csv`, over the 40 prompts of A1 ∪ A2 ∪ B only
(288 within-family pairs, 492 between-family pairs):

| arm | W | Bt | G |
|---|---|---|---|
| `preset_pos` | 0.473849 | 0.441011 | **0.032838** |
| `rand_pos` | 0.409280 | 0.360349 | **0.048931** |
| `blockshuf_neg` | 0.376562 | 0.355871 | 0.020692 |

Between prompts that can be compared at all, the norm-matched random control shows a
**larger** family gap than the calibrated preset. Rule 4 is not merely missed, it points the
other way.

## 5. Consequence, recorded now

- The `verdict_preset_pos` column of `data/family_coherence_tests.csv` is **void**. It is
  left in the file because deleting a computed output would hide what the frozen rules
  produced; this amendment is its label.
- **No claim is published.** `notebook/` is untouched, no page changes, no claim changes
  status, no figure is registered.
- The following are kept as **description only**, each with the confound that prevents it
  from being a result:
  - within the comics domain the preset's direction transfers at cosine ≈ 0.47 against a
    split-half reliability ceiling of 0.755 — about 63 % of the reproducible direction —
    and it transfers as well between the three comics sub-families as inside them;
  - the random control at the same displacement transfers at ≈ 0.41 in the same set, so the
    transfer is not a property of the calibrated preset;
  - across the comics/stage9 boundary the preset's cosine falls to ≈ 0.02 while the random
    control's stays at ≈ 0.19; this is the most interesting number in the study and it is
    **confounded with render run**, so it is not a finding.
- What a corrected study needs, stated here so that it is not invented later: a domain
  contrast whose two sides are **not** one render run each, i.e. prompts of at least two
  distinct style domains rendered inside the same run, with the existing six arms. That is a
  render request, and it belongs to the observer, not to this document.
