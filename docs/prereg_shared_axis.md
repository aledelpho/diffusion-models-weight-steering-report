# Pre-registration — the axis every edit shares

**Deposited** 2026-09-24, before the statistics below were computed **on the corpus they will be
computed on**. Read §6 first: an earlier, post-hoc version of this analysis exists and this
document is what turns it into something testable.
**Status** frozen. Amendments at the bottom, dated, never in the body.
**Runs** locally. Renders nothing.

---

## 1. What this is for

`data/arm_coherence_tests.csv` established something deflationary: at a fixed seed every arm of
the bench moves the batch along one direction, **and so does the norm-matched random scramble**,
with no structured arm separating from it. Holding the seed fixed is enough.

The obvious next question is whether the arms share more than that — whether there is a single
direction that *every* edit drags the image along, regardless of which edit it is. If there is,
it has a name in this project already: the **cost**, the common mode of page 05, the thing that
happens whichever way you push. And it has a name in the tool's own announcement: the
contamination that ruins quality, the spoil thrown up by digging.

The question that matters is what is left when you take it out. An edit whose whole cross-scene
consistency *is* the shared degradation is eroding the mountain. An edit that keeps a direction
of its own after the degradation is removed is digging a canal.

---

## 2. Defining the axis — out of sample, frozen here

The axis must not be fitted on the corpus it is then used to judge. Two definitions, both fixed
now, the first primary.

**Primary — estimated on stage 7, applied to stage 9.**

1. In the 23 numeric style features of `experiments/style_features.py`, standardise **once** on
   the stage-7 baselines (`data/style_features_stage7.csv`, condition `baseline`).
2. For every cell of every stage-7 arm (`preset_pos`, `preset_neg`, `blockshuf_pos`,
   `blockshuf_neg`, `rand_pos`, `rand_neg`), take the paired difference from the baseline at the
   same prompt and seed.
3. `u` = the mean of all those difference vectors, unit-normalised.

`u` is then applied to the stage-9 corpus, which shares no prompt with stage 7 and was not used
to estimate it.

**Secondary — leave-one-arm-out, within stage 9.** For each stage-9 arm, `u_-a` = the mean
difference vector of the *other five* arms, unit-normalised, and the arm is judged against that.
No arm contributes to the axis it is measured against.

The two definitions answer different objections. The primary is genuinely out of sample but
assumes the per-feature scales of the two corpora are comparable, because each is standardised on
its own baselines. The secondary has no such assumption but stays inside one bench. **If the two
disagree, the analysis is reported as undecided and neither is published as a result.**

---

## 3. The measure

For an arm `a` with per-cell difference vectors `D_a`:

```
share(a)   = mean over cells of |<d, u>| / ||d||        how much of the edit lies on the axis
strip(d)   = d - <d, u> u                               the edit with the shared axis removed
S(a)       = split-half cosine of the mean direction:
             split the 8 style prompts 4 against 4, mean D on each half, cosine between them,
             averaged over all 35 distinct splits
S_strip(a) = the same on strip(D_a)
```

**Null.** The same split-half statistic on the differences between two baselines at different
seeds of the same prompt, **with the sign of each difference randomised**, 200 draws, reporting
the mean and the 95th percentile. The randomisation is not decoration: with a fixed pair ordering
the null scores 0.61 and looks identical to the arms, which is an artefact of the ordering and
not a property of the model. Any run that reports a null above 0.40 without sign randomisation
has the bug and must stop.

---

## 4. What counts as what — written before looking

Per arm, in both axis definitions:

| outcome | criterion |
|---|---|
| **keeps a direction of its own** | `S_strip(a)` above the 95th percentile of the stripped null |
| **its consistency was the shared axis** | `S(a)` above that percentile, `S_strip(a)` below it |
| **no cross-scene direction either way** | both below |

And the comparison that carries the claim:

> **The preset separates from the controls on this measure** if, in *both* axis definitions,
> `S_strip(preset_pos_2x)` is above the null band while `S_strip(rand_pos_2x)` is below it.

**Declared in advance.** I expect: the preset keeps its direction at both amplitudes and loses
almost nothing by the stripping; the scramble and the block derangement at **double** amplitude
lose most of theirs, with the scramble falling below the null; at **single** amplitude all three
keep something. I also expect `share(a)` to be lowest for the scramble at single amplitude. If
the preset loses its direction when the axis is stripped, the honest reading is that the
calibration buys magnitude and not kind, and the tool's central claim needs rewriting.

---

## 5. Traps

* **Circularity** — handled by §2; it is the entire reason this document exists.
* **Attenuation** — a direction estimated at twice the amplitude is estimated better, so raising
  the dose raises every cosine for measurement reasons alone. This is why the comparison that
  carries the claim is *between arms at the same amplitude*, never between amplitudes.
* **The null's ordering artefact** — §3.
* **Dimension bookkeeping** — stripping removes one dimension, so the null must be stripped the
  same way before the percentiles are read. Comparing a stripped arm to an unstripped null is the
  easy way to invent a result.
* **Standardisation** — once per corpus, on that corpus's baselines (pitfall 33).
* **Unmatched displacement** — the stage-9 arms are not displacement-matched (page 09). `share`
  and `S` are scale-free; `||D||` is reported as descriptive only.

---

## 6. The honest history of this analysis

An earlier version was run on 2026-09-24 with the axis defined as the mean over **all six
stage-9 arms** — that is, fitted on the same data it judged, after the data had been seen. It
returned: preset unchanged by the stripping (0.599 to 0.600 and 0.716 to 0.719), block
derangement at double amplitude 0.666 to 0.440, scramble at double amplitude 0.655 to 0.410 and
below the null. Those numbers are the reason this pre-registration exists and they are **not**
evidence for it. If the frozen version returns the same picture, the picture is worth something.
If it does not, the earlier run was the analysis finding what it was looking for, which is the
failure mode this whole notebook is built against.

---

## 7. Output contract

`experiments/shared_axis.py`, no rendering, writes:

* `data/shared_axis.csv` — one row per (arm, axis_definition): `share`, `S`, `S_strip`,
  `null_mean`, `null_p95`, `null_mean_stripped`, `null_p95_stripped`, `verdict` taken verbatim
  from the table in §4, `n_cells`, `n_prompts`
* `data/shared_axis_loadings.csv` — the 23 components of `u` in both definitions, so a reader can
  see *what* the shared axis is made of rather than taking "degradation" on trust

The second file is the one that will teach us something. If `u` loads on edge density, texture
entropy and the high-frequency band, it is the loss of fine texture that page 05 already measured
from the other side, and two independent roads have met.

---

## Amendments

*(none yet)*
