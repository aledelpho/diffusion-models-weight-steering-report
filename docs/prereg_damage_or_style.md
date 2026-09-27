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

**Superseded by Amendment 01**: all 9 baselines × 3 probes × 2 orders = **54 calls**.

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

---

## Amendment 01 — two defects in the design, found before any call was made

**Deposited**: 2026-09-27, before the gate ran. Nothing had been measured.

### A. The gate silently dropped an image

`judge_pairs_gate.py` took `sorted(baselines)[:8]`. There are **nine** baselines in this corpus
(3 prompts × 3 seeds) and the slice discarded `P02_baseline_seed777` for no reason other than the
number 8 appearing in §4. An unjustified exclusion, however small, is the beginning of a
selection effect.

**Fixed**: the gate uses **all nine** baselines — 9 × 3 probes × 2 orders = **54 calls** — and the
thresholds are stated as proportions, **≥ 0.889 correct** and **≥ 0.778 order-agreeing** per probe,
which at n = 9 means **16/18 and 14/18**. Both are **stricter** than the 14/16 and 12/16 first
deposited (0.875 and 0.750); the amendment does not loosen a criterion.

### B. The determinism re-test never touched Arm B

§5 specified "the first 16 items of each arm" and the runbook implemented it as
`sorted(item_ids)[:16]`. Item ids begin with `A|` and `B|`, so sorting puts **all sixteen in Arm A**
and Arm B would never have been re-tested. Arm B is the arm the study exists for.

**Fixed**: `experiments/judge_damage_style_retest.py` takes **8 items from each arm**, both orders,
**32 calls**, snapshots the first run to `data/damage_style_answers_run1.csv` before re-running, and
prints the test–retest rate against the frozen 0.95 threshold.

### C. The call budget, restated

| arm | items | × orders | calls |
|---|--:|--:|--:|
| gate | 27 | 2 | **54** |
| A — damage | 144 | 2 | **288** |
| A null — baseline vs baseline, different seed | 6 | 2 | **12** |
| B — style identity | 72 | 2 | **144** |
| B null — reference with two non-matching candidates | 12 | 2 | **24** |
| determinism re-test — 8 items per arm | 16 | 2 | **32** |
| | | | **554** |

The §5 table said 548 and is superseded by this one. The item counts were verified against the
renders on disk: 234 run items, **zero missing files**.

---

## Amendment 02 — the gate failed, what the failure actually says, and the instrument that replaces it

**Deposited**: 2026-09-27, after the gate and **before any statistic of the replacement was
computed.** No result of the replacement has been seen.

### A. The gate result, independently recomputed from `data/damage_style_gate.csv`

| probe | correct | order-agreeing | A-share | verdict |
|---|--:|--:|--:|---|
| saturation | 11/18 | 6/18 | **0.778** | FAIL |
| sharpness | 9/18 | **0/18** | **1.000** | FAIL |
| degradation | 8/18 | **0/18** | **0.278** | FAIL |
| **pooled** | 28/54 | 6/54 | **0.685** | — |

The report in `report_damage_or_style.md` reproduces exactly. No threshold was moved, no prompt
reworded, no model substituted, and Arm B was correctly **not** run, because the contingency in the
runbook covered a failure of the degradation probe alone and all three failed.

### B. The failure has a mechanism, and it is not "the judge is noisy"

On `sharpness` the judge answered **"A" in 18 calls out of 18**, against a Gaussian blur of σ = 2.
Correct 9/9 when the sharp image was first, 0/9 when it was second. On `degradation` it answered
"B" in 13 of 18. **It emits a fixed letter per question and does not consult the pixels.**

Accuracy alone would have hidden this: 9/18 on `sharpness` reads as "chance". It is not chance.
Under guessing, both orders of a pair agree correctly about a quarter of the time, so ~4–5 of 18;
observed **0 of 18** on two probes, with P(0 of 9 pairs) = 0.75⁹ = 0.075 each and 0.0056 jointly.
**Zero order agreement is below chance and is the signature of a constant answer.** The
order-agreement criterion is what separated "noisy" from "not looking", and it is the part of the
gate that earned its place.

### C. A defect in the gate's own third criterion — pitfall candidate 74

The pooled first-position share is **0.685, inside the [0.30, 0.70] bound: on that criterion the
gate PASSES.** It passes because the three per-probe biases point in different directions — 1.000,
0.778, 0.278 — and cancel when averaged.

**A position-bias guard pooled over questions with different position preferences is not a guard.**
Had §4 relied on the pooled share alone, a judge answering with a constant letter would have been
certified. Only the per-probe criteria caught it.

This generalises beyond the gate: guard **G1** in `judge_damage_style_run.py` computes the A-share
pooled per *arm*. Each arm here happens to carry one question, so G1 is correct — **by luck, not by
design.** Any future arm with more than one question form must compute it per question.

**Pitfall candidate 74**: *a distributional guard averaged over heterogeneous questions can be
satisfied by the cancellation of opposite pathologies. Compute it per question, and keep a
consistency criterion (order agreement) alongside the accuracy criterion, because accuracy alone
reads a constant answer as chance.*

### D. What is voided, and what is not

* **Voided**: multi-image judging with `qwen3.8:27b` over `/api/generate` at native resolution.
  Arm A and Arm B as specified in §5 are unreachable with this instrument.
* **Not voided**: the single-image gate of 2026-09-26 (`data/capability_judge_gate.csv`, 7/8 scenes,
  polarity agreement 0.016). That judge passed, on one image, and nothing here contradicts it. The
  boundary is exact: **this judge sees one image.**

### E. The replacement for Arm B, and why the frozen prediction carries over unchanged

Arm B asks whether a block edit is a **transferable treatment**: does the same edit applied to a
different prompt and seed produce a recognisably related image, against a foil matched in ‖D‖?
That is a 2-alternative forced choice with chance 0.50 — and **it does not need a judge.** In the
23-trait space it is a nearest-neighbour decision:

```
for each (block b, dose d, sign s, seed sigma):
    reference = feature vector of (b,d,s) on P01, seed sigma
    target    = feature vector of (b,d,s) on P02, seed sigma
    foil      = feature vector of (b',d,s) on P02, seed sigma,  b' the magnitude-matched block
    hit  iff  cos(reference - mean_P01, target - mean_P02) > cos(reference - mean_P01, foil - mean_P02)
```

Each arm is centred on its own prompt's baseline mean, so content is removed and only the
displacement direction is compared. Standardisation from **baselines only** (pitfall 33). Chance
remains exactly **0.50**, the foils are the same magnitude-matched ones the runner computes, and the
unit of analysis is the seed within prompt pair.

**Therefore prediction D3 carries over verbatim**: confirmed if pooled > 0.60 with ≥ 5/6 blocks
above 0.50; falsified if pooled ≤ 0.55. The instrument changed because the gate forced it, not
because a result was seen — **none has been.** The exact sign test over the 12 block × dose cells
is retained.

Cost: **zero renders, zero judge calls.** `experiments/style_features.py` extracts the 23 traits
from the 519 existing PNGs.

### F. What cannot be replaced

**Arm A cannot.** "Has visible rendering defects" is a perceptual judgement and there is no feature
that means it. The project's nearest proxy is the loss of high-frequency energy against the
same-seed baseline (`punto7_attrito_e_rettificazione.md` §1), and that measures **loss of fine
texture, not the appearance of being broken** — a coherent flat style loses fine texture too, which
is exactly the confusion this study existed to resolve.

So the damage half stays open. It would need either a judge that addresses two images — the
composite-canvas variant, where both images are pasted into one labelled canvas and the problem
becomes single-image, re-gated with these same three probes at 54 calls — or a human. Neither is
assumed here, and neither is run without Alessandro.
