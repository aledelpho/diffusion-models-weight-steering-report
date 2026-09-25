# Pre-registration — The ordering of how far each arm leaves the base model's repertoire

- **Written:** 2026-09-25, after `data/mountain_reachability_tests.csv` (commit `f781cb7`).
- **Status:** a **registered prediction**, not a test that can be run today. See §1.
- **Relates to:** `docs/prereg_mountain_reachability.md` + Amendment 01.

---

## 0. The observation this comes from, stated plainly

R1 in the frozen mountain pre-registration is a threshold on a descriptive fraction:
`frac_above_p95`, the share of an arm's renders whose `d_out` sits above the 95th
percentile of the baselines' own `d_out` band. **It carries no statistical test** — no
null, no permutation, no p-value — and that is a property of how it was written, not of
how it was run.

Across the two corpora already measured:

| arm | stage 9 | stage 7 |
|---|--:|--:|
| preset | 0.400 | 0.175 |
| block-shuffle | 0.475 | 0.2875 |
| random scramble | 0.625 | 0.300 |

Two things are visible, and only one of them is interesting.

**Not interesting:** stage 7's `preset_pos` falls under the pre-registered 0.25 line and so
"R1 holds" for it. The whole stage-7 distribution is 0.19 to 0.33 lower than stage 9's, so
the preset crossed the threshold because the corpus moved, not because the arm behaves
differently. That verdict is a threshold artefact and no claim rests on it.

**Interesting:** the **ordering** `preset < block-shuffle < random scramble` holds in both
corpora, across two different arm sets (`preset_pos` vs `preset_pos_1x`, and so on) and two
different prompt sets. If it is real, it says the calibrated preset is the edit that leaves
the base model's repertoire *least*, and the random perturbation the one that leaves it
*most* — the first ordering in this project that would distinguish a structured edit from a
random one.

## 1. Why this is a prediction and not a test

**Both corpora have already been looked at.** The ordering was found in them. Testing it
there would be fitting the hypothesis to the data that produced it, which is the failure
this project has already caught in itself twice (`data/shared_axis_diagnostics.csv`, and
the quarantine of stage 9 in `docs/prereg_seed_stability.md`).

A third corpus was sought and does not exist. `data/style_features_stage8.csv` holds 29
prompts, but only **five** (`B1`–`B4`, `P0`) carry `baseline`, `preset_pos`,
`blockshuf_neg` and `rand_pos` together — below the 12-prompt gate of Amendment 01 §2.

So this document does not authorise a confirmatory test today. It freezes the prediction,
the statistic and the decision rule **now**, so that the first adequate corpus to exist can
judge them.

## 2. The prediction — frozen

For the fraction `frac_above_p95(arm, prompt)`, with the prompt as the unit:

```
frac(preset)  <  frac(block-shuffle)  <  frac(random scramble)
```

**Primary contrast:** `preset` minus `random scramble`, expected **negative**.
**Secondary:** `preset` minus `block-shuffle`, and `block-shuffle` minus `random scramble`,
both expected negative.

Test: exact sign-flip permutation over prompts, two-sided, Holm across the three contrasts.

`frac_above_p95` is computed per prompt, against that corpus's own baseline `d_out` band,
with the standardisation rule of Amendment 01 §7 — from that corpus's baselines only.

## 3. Where it will be judged

**Confirmatory:** the first corpus holding at least **12 prompts** with `baseline`, a
preset arm, a block-shuffle arm and a random-scramble arm, that is not stage 7 and not
stage 9. No such corpus exists on 2026-09-25.

**Pre-committed but underpowered first look:** the six prompts `S7_01`–`S7_06` of Block D-B,
whose renders **do not exist at the time of writing**. Six prompts give a sign-flip floor of
`2/2^6 = 0.031`, and after Holm across three contrasts `0.094` — so **significance is not
reachable there even with a perfect result**, and the six-prompt outcome is reported as
descriptive whatever it shows. Its only value, and it is a real one, is that the direction
was committed to before the images existed.

## 4. Decision rules — frozen

On the confirmatory corpus:

- Primary contrast negative at Holm-corrected `p < 0.05` -> **the ordering holds**: the
  calibrated preset leaves the base model's repertoire less than a random perturbation
  does. This would be the first arm-specific distinction between a structured edit and a
  random one in this project.
- Primary not significant -> **the ordering is not supported.** The appearance of it in
  stage 7 and stage 9 is then attributed to the two corpora sharing whatever produced it,
  and it is reported that way.
- Primary significant in the **opposite** direction -> reported as such, prominently.
- Secondaries disagreeing with the primary -> `ambiguous`, all three reported, no claim.

## 5. What would kill this

- No corpus of 12 or more adequate prompts is ever produced: the prediction stays
  registered and untested, and the observed ordering stays descriptive, permanently
  labelled as such wherever it is quoted.
- `frac_above_p95` turns out to depend on the size of the base cloud `B` more than on the
  arm. This is checkable and must be checked first: recompute `frac_above_p95` on stage 7
  with `B` subsampled to the size of stage 9's, and report whether the ordering survives.
  If the fractions move by more than the gaps between the arms, the statistic is measuring
  the cloud and not the edit, and this study ends there.
- The confirmatory corpus's arms are not the same objects as stage 7's and stage 9's — they
  never exactly are. The result is reported with its arm set named, and it is never pooled
  with the other two.

## 6. Outputs

Script: `experiments/r1_ordering.py`, written only when a corpus exists to run it on.

Data: `data/r1_ordering.csv` and `data/r1_ordering_tests.csv`, each row naming its corpus,
its arm set, and whether it is confirmatory or descriptive.

Until then this document stands alone, and the ordering is quoted nowhere as anything but a
descriptive observation replicated across two corpora and not tested.
