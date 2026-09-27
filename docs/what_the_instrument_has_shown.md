# What this instrument has shown, and what it has not

**Date**: 2026-09-27 · **Sources**: `notebook/*.md` front matter (43 claims),
`data/claim_map.csv`, `docs/errors_log.md` (69 rows), and the documents named below.
Counted from the files, not from memory.

---

## 1. The scoreboard

| status | claims |
|---|--:|
| **holds** | **15** |
| **ambiguous** | 6 |
| **overturned** | 4 |
| **open** — stated, never tested | **18** |
| total | **43** |

Plus **69** logged pitfalls, each with a mechanism and a fix.

The ratio is the first honest fact: **about a third of what this project has claimed survives, and
nearly half has never been tested.** Four claims were killed by their own pre-registrations.

## 2. What holds, and the two piles are not equally interesting

### Pile A — the bench. Five claims, and they are the reason anything else is measurable.

* `node-is-identity-at-zero` — the tuner at zero gain renders bit-for-bit identically to no tuner.
* `deterministic-across-sessions` — a render reproduces exactly across a restart, so measurements
  weeks apart are comparable. Every pixel comparison in this project stands on this row.
* `roundtrip-does-not-return` — an edit and its exact inverse restore the weights and **do not**
  restore the image. A floor stricter than the seed floor.
* `cliplult-is-a-dead-arm` — one text-encoder arm is exactly inert at every dose while its sibling
  moves the image at every dose.
* `noise-floor-measured` — seed-to-seed texture noise under 2 % on the two calibration prompts,
  from 18 seeds each.

These are claims about the **instrument**, not about the model. They are solid, and a report that
only contained them would still be worth publishing, because most work of this kind never
establishes them.

### Pile B — the model. Ten claims, of unequal weight.

The strongest, by a distance:

* **`subject-enlargement-replicates`** — a block-derangement edit makes the subject occupy more of
  the frame, growth increases with dose, and it **replicated on a ten-style corpus that did not
  exist when the prediction was frozen**. Out-of-sample replication of a frozen prediction is the
  highest standard anything here has met.
* **`blocks-separate-by-direction-not-distance`** — two block groups pushed exactly the same
  distance move the image in directions that can be told apart, and separate further than two
  arbitrary perturbations of that size. This is the claim the whole enterprise rests on: **there is
  structure, and it is not a function of how far you pushed.**

Then the per-block asymmetries, mutually consistent and each from a frozen prediction:

* `cost-grows-with-depth` — any push costs fine texture, either direction, and the cost concentrates
  near the output.
* `first-block-is-an-inverted-knob` — block 0 pushed positive smooths, pushed negative etches.
* `tail-is-rectified` — on the last blocks the negative direction is the safe side.
* `block1-coheres-at-matched-displacement`, `edits-move-colour-in-different-directions`,
  `hatching-axis-holds-under-derangement`.

And two about method rather than model, both useful:

* `blinding-is-a-measurement-and-it-failed` — hashed filenames do not blind an expert observer to a
  visible signature, measurable on twenty trials.
* `double-dose-arm-is-degraded` — the only amplitude that produced significant cells sits outside
  its own declared quality range in three quarters of them.

## 3. What was debunked

### Four claims overturned by their own pre-registrations

* `mirror-response-is-the-rule` — **falsified**: mirroring is the rule, not the exception;
  17 of 28 blocks are compatible with a perfectly mirrored response.
* `extremes-are-violent-both-ways` — **falsified**: the tail is rectified, up to a factor nine
  between the two directions on `blk26`.
* `randsign-hatching-did-not-replicate` — an exploratory effect that died on a fresh corpus.
* `style-does-not-steer-direction` — **the prediction that the declared style drives the direction
  of the displacement more than the subject does was not supported.**

### Verdicts the project withdrew from itself

* **Family coherence** — `holds_and_specific` withdrawn: it rested on a 0.000283 margin and on one
  family being an outlier group (`prereg_family_coherence_amendment_02.md`).
* **Domain specificity** — the coherence is real but the verdict on record is
  `holds_provisionally_not_specific_to_calibration` (`data/domain_specificity_tests.csv`): the
  effect is **not** specific to the calibrated preset. A random sign scramble at matched
  displacement does much of the same work.
* **The spatial map** — `mappa_krea2_primo_esito.md` §2, retracted the same day: the noise floor was
  built from different-seed baselines, which is a maximal perturbation, not noise.
* **Steering fraction at the pixel level** — `mappa_completa_sterzo_e_deriva.md`, retracted as
  pitfall 63: 0.40 is the floor of the statistic, not a result.
* **The same measurement, re-derived on 2026-09-26 and retracted again**
  (`sign_decomposition_retraction.md`), this time with a pre-registered threshold **below the
  estimator's floor**.
* **`modulation_norm`** — a region that never existed, 48 renders spent and a false positive
  carried, because the atlas enumerated the checkpoint instead of the tool (pitfall candidate 71).
* **The analyst's sealed prediction H** — that the CLIP half of every preset is near-inert.
  Falsified: `clip_only` moves the pixels as far as `model_only`
  (`where_the_stroke_shift_lives.md`).

## 4. The one thing added on 2026-09-26 that survived its own retraction

**The routing path and the value path behave differently, by three independent statistics.**

| | `wq` / `wk` | `wv` / `wo` |
|---|--:|--:|
| traits that reverse with the sign (chance 0.50) | **0.067 – 0.120** | **0.538 – 0.758** |
| traits above the seed noise, per pair | 1.0 – 2.0 / 23 | 3.5 – 5.9 / 23 |
| steering fraction (null 0.400) | **0.359 – 0.369** | **0.411 – 0.434** |

Gap **+0.060 against a floor variation of 0.015**, complete separation of the eight cells, 8/8
scenes. **`q` and `k` are close to unusable as signed controls**; the control lives in the value
path. This is the only genuinely new result of that day and it needs the replication on a middle
band, on a band never used to find it, before it is more than that.

## 5. What the instrument is, stated plainly

**It is not a knob.** Image motion goes as dose^0.19 — six times the dose buys 1.39 times the
effect — and at the smallest dose ever tested the image has already moved 50–62 % of the distance to
a different seed. There is no small-perturbation regime anywhere in the tested range, and `F` does
not depend on dose, so lowering it is not obviously a way out.

**It is a source of reproducible, discriminable directions.** Different edits go different ways,
those ways can be told apart above a matched-displacement null, and at least one of them —
subject enlargement — replicates out of sample on a frozen prediction.

**It is not selective in the way the project set out to show.** The direction does not follow the
declared style (`style-does-not-steer-direction`, overturned), the coherence is not specific to the
calibrated preset (`holds_provisionally_not_specific_to_calibration`), and a matched random scramble
does much of the same work.

**And nobody has yet asked whether far is bad.** Every statistic measures how far the image moved;
none measures where it landed. `prereg_damage_or_style.md` is the first instrument that can tell a
ruined image from a restyled one, and it has not been run.

## 6. The output that may outlast the claims

`docs/errors_log.md` holds **69** entries, each a mechanism and a fix: a floor mistaken for a
result; a null built from a maximal perturbation; a product of two measures; a sweep enumerated from
the architecture instead of from the tool; a judge with a ceiling found after 920 calls instead of
32; a quantised estimator reported to three decimals; a pre-registration whose confirm region lay
outside the estimator's range; a novelty check run in the wrong language.

Fifteen surviving claims describe one checkpoint. The error log describes **how measurement on
generative models goes wrong**, and that transfers. On present evidence it is the most valuable
thing the project has produced.
