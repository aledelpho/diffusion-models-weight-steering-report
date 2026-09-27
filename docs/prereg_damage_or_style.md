# Pre-registration — is a hard block edit damage, or is it a style?

**Deposited**: 2026-09-27, before any call of this study was made.
**Corpus**: `benchmark_mappa/renders`, 519 renders already on disk. **No render is generated.**
**Judge**: `qwen3.8:27b` over Ollama, the model already gated in `data/capability_judge_gate.csv`.

---

## 1. The question, and why the existing measurements cannot answer it

Every statistic this project has applied to `benchmark_mappa` measures **how far** the image moved.
None measures **where it landed**. At dose 0.200 a block edit moves the image 83–101 % of the
distance between two renders of the same prompt at different seeds
(`assessment_per_block_dose_calibration.md` §3). The analyst read that as a ceiling. Alessandro's
objection, which the repository had already recorded in `coerenza_traiettoria.md` §2, is that a seed
distance is a **ruler, not a verdict**: an edit that lands far away may have landed on a coherent
new style, and that is a success, not a failure.

`‖D‖` is blind to the difference. This study is the instrument that is not.

## 2. The two hypotheses make opposite predictions

**Damage is idiosyncratic. A style is reproducible.**

If pushing `Block_3` hard produces a *style*, then the same push applied to a **different prompt and
a different seed** should carry a recognisable family resemblance — the same treatment on different
content. If it produces *damage*, two such images are merely broken, each in its own way, and no
resemblance survives the change of content.

So the study has two arms, and the second is the one that decides.

* **Arm A — damage.** Baseline against perturbed, same prompt, same seed, forced choice, both
  orders. Which of the two has visible rendering defects?
* **Arm B — style identity.** A reference image, and two candidates rendered from a **different
  prompt and seed**: one carries the same block/dose/sign as the reference, the other a
  **different block matched in ‖D‖ at that dose**. Which candidate shares the reference's
  treatment? Chance is 50 %.

The foil in Arm B is matched in displacement magnitude on purpose. Without that, Arm B would merely
re-measure Arm A: the judge would pick whichever candidate is *equally broken* rather than
*treated the same way*. With it, Arm B asks about identity, not amount.

### The reading, fixed now

| | matching at chance | matching above chance |
|---|---|---|
| **damage high** | pure damage | **a style that costs quality** |
| **damage low** | nothing happened | **a clean style** |

## 3. Form of the questions — no absolute rating, ever

`prereg_capability_judge_amendment_02.md` §5 established, after 920 wasted calls, that this judge
has no resolution for absolute judgements and must be asked **forced choice at matched prompt and
seed, both orders**. Every question here is forced choice. No confidence, no rating, no threshold is
requested of the judge at any point.

Both orders are always run. A cell counts only when the two orders **agree**; disagreements are the
position-bias measure and are counted and discarded, never broken by a tie-rule.

## 4. The multi-image gate — new, and blocking

Every prior judge call in this project sent **one** image. Both arms here send two or three. Whether
this judge addresses several images as several is unknown and must not be assumed.

The gate uses manipulations with **certain ground truth**, applied by the runner to copies of the
baselines (image processing, not rendering):

| probe | manipulation | question |
|---|---|---|
| **saturation** | one copy at 50 % saturation | which is more colourful? |
| **sharpness** | one copy Gaussian-blurred σ = 2 | which is sharper? |
| **degradation** | two copies with Gaussian noise σ = 4 and σ = 16 | which has more visible defects? |

8 baselines × 3 probes × 2 orders = **48 calls**.

**Gate criteria, frozen**: on each probe separately, ≥ **14 of 16** correct, and the two orders
agreeing on ≥ **12 of 16**; and the overall share of first-position answers inside
**[0.30, 0.70]**.

**If the gate fails, that is the result.** Do not reword, do not swap model, do not lower a
threshold, do not resize an image. Write it up and stop. The third probe is the closest to the real
task and a failure there specifically means the judge cannot rank degradation at all, which voids
Arm A but not necessarily Arm B; the runbook says what to do in that case.

## 5. Design and size

Doses **0.050** and **0.200** only — one where the earlier work found the cost to be nil, one at the
top of the sweep. Blocks `Block_1` … `Block_6`, both signs, prompts `P01` and `P02`, seeds 42, 777,
1337.

| arm | items | × orders | calls |
|---|--:|--:|--:|
| gate | 24 | 2 | **48** |
| A — damage | 144 | 2 | **288** |
| B — style identity | 72 | 2 | **144** |
| A null — baseline vs baseline, different seed | 6 | 2 | **12** |
| B null — reference with two non-matching candidates | 12 | 2 | **24** |
| determinism re-run — first 16 items of each arm | 32 | 1 | **32** |
| | | | **548** |

`A01` is excluded: its negative arm exists only at 0.050.

## 6. Early guards — the rule that cost 920 calls

`prereg_capability_judge_amendment_02.md` §6: *every judge study runs its distributional guards on a
small pre-flight subset before the full sweep.* Enforced in the runner, not left to the analysis:

* **G1** — after the first **32** calls of each arm, the share of "A" answers must be inside
  **[0.25, 0.75]**. Outside it, that arm **halts** and records why.
* **G2** — after the first **32** calls of each arm, the share of unparseable answers must be
  **< 0.10**. Otherwise halt.
* **G3** — Arm A's null must be run **before** Arm A's items, not after. If the baseline-vs-baseline
  null does not sit inside **[0.30, 0.70]**, Arm A halts: a judge that calls one of two identical-in-
  expectation baselines defective cannot measure degradation.
* **G4** — determinism. The re-run of the first 16 items must reproduce them exactly. Test-retest
  was 1.000 on the previous study; anything below **0.95** invalidates the run.

A halted arm is a **result**, written up as such. The other arm continues.

## 7. Predictions, frozen before any call

| # | prediction | confirmed if | falsified if |
|---|---|---|---|
| **D1** | hard edits are visibly defective | Arm A, dose 0.200, perturbed chosen as defective in **> 0.75** of order-agreeing cells | **< 0.55** |
| **D2** | damage grows with dose | share at 0.200 > share at 0.050 in ≥ **5/6** blocks | ≤ 3/6 |
| **D3** | **a block edit is a transferable treatment** | Arm B pooled **> 0.60**, and ≥ **5/6** blocks above 0.50 | pooled ≤ **0.55** |
| **D4** | Arm B is not Arm A in disguise | \|ρ\| between damage share and matching share over the 12 block×dose cells **< 0.60** | ρ > **0.80** → Arm B discarded |
| **D5** | `Block_6` is the extreme on both | `Block_6` ranks first or second on damage **and** on matching | in the lower half on both |
| **D6** | the negative arm is the safer side on the tail (Punto 7 §3) | `Block_6` matching higher for `neg` than `pos` at 0.200 | the reverse, by more than 0.10 |

**D3 is the prediction this study exists for.** The analyst expects it to be **confirmed but
modestly** — between 0.60 and 0.75 — because the trait analysis shows block edits moving style
descriptors 1.5–6.7× the seed noise, which is a real signature but not a dramatic one.

**D4 is the prediction most likely to fail**, and its failure voids Arm B rather than teaching
anything: if the magnitude-matched foil did not do its job, the judge is answering "which is more
broken" in both arms.

## 8. What this study may not do

* It may not change the status of any published claim. If a result bears on one, the report says so
  and stops.
* It generates no render and requests none.
* It writes nothing under `notebook/`.
* The judge's answers are data about the judge as much as about the images. Any statement of the
  form "the images *are* a style" is a statement about what this judge, gated this way, reports —
  and is written that way.
