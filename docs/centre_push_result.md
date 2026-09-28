# Outcome — can the centre be pushed further? The primary says no, and the reason is the grouping

**Date**: 2026-09-28 · **Design**: [`prereg_centre_push.md`](prereg_centre_push.md), committed in
`083b0a1` before any render existed · **Renders**: 295, launched by Alessandro,
`benchmark_centre_push` · **Analysis**: `experiments/analyze_centre_push.py`, the script named in
the pre-registration · **No render by the analyst.**

---

## 1. Guards — all three pass

| guard | result |
|---|---|
| **G_det** | the determinism row (`P01 Block_3 +0.200 seed 42`) reproduces `benchmark_mappa` **pixel for pixel** |
| **G1** | 295 of 295 files present |
| **G3** | **0** perturbed renders identical to their baseline — no silent no-op |

G_det is the fourth independent cross-bench determinism confirmation in this project, and G3 is the
check that `benchmark_qkvo_atlas` failed without anyone noticing for two days.
S2 (content) is dropped: the DINOv2 embedding was not available, as §5 of the pre-registration
provides for.

## 2. Primary: **not supported**

Slope β of L on ln V per arm; statistic T = mean(centres) − mean(extremes); exact null over 495
relabellings, one-sided.

> **T = +0.0534, p = 0.1899.** G_range passes — six central arms reach V ≥ 2 — so this is a null,
> not an inconclusive.

## 3. Why it fails: position does not order behaviour

The slopes, sorted:

| arm | position | β |
|---|---|--:|
| `Block_5 pos` | *centre* | **−0.2513** |
| `Block_6 neg` | end | −0.1966 |
| `Block_6 pos` | end | −0.0844 |
| `Block_3 neg` | centre | −0.0131 |
| `Block_5 neg` | centre | +0.0040 |
| `Block_2 neg` | centre | +0.0070 |
| **`Block_1 neg`** | **end** | **+0.0081** |
| `Block_3 pos` | centre | +0.0192 |
| **`Block_1 pos`** | **end** | **+0.0302** |
| `Block_4 neg` | centre | +0.0436 |
| `Block_2 pos` | centre | +0.0648 |
| `Block_4 pos` | centre | +0.0676 |

**The split is wrong in both directions.** `Block_5` sits in the centre and cedes hardest of all;
`Block_1` sits at an end and cedes less than five of the eight centrals. The same thing on the
descriptive side — share of units with L < 0.98 among those with V ≥ 1.5:

| group | share | |
|---|--:|---|
| **`Block_6`** | **93 %** (13/14) | |
| `Block_5` | 56 % | |
| `Block_3` | 44 % | |
| `Block_4` | 33 % | |
| **`Block_1`** | **9 %** (1/11) | an "extreme", second cleanest in the bench |
| `Block_2` | 0 % | |

**"The extremes break" is really "the output end breaks".** `Block_1`, the input end, does not, and
pooling it with `Block_6` is what the pre-registered contrast does. The pooled secondaries still
favour the centre — S1 56 % against 38.7 %, S4 92.6 % against 67.4 % — but both numbers are carried
by `Block_6` alone.

**Three arms cede and they are exactly the three that have a knee.** `Block_5 pos`, `Block_6 neg`
and `Block_6 pos` are the only conditions in `retro_mappa_reading_result.md` §1 whose coherence
collapses between dose 0.120 and 0.200. Different bench, new seeds, a different statistic, the same
three. Neither analysis knew about the other.

**Post hoc, and labelled as such:** reclassifying `Block_5` as an extreme gives **T = +0.1132,
p = 0.0206** over 924 relabellings. That is *not* the verdict — the pre-registered verdict is "not
supported" and stands. It is recorded because the pre-registration's own analyst prediction said
*"`Block_5 pos` si comporterà come un estremo"* before the data existed, which makes the
misclassification an anticipated flaw in the design rather than a rescue invented afterwards.

## 4. And the question that prompted the bench: yes, some of them hold at 0.500

Alessandro asked for the extreme dose specifically — *"valori molto elevati, per vedere se si
rompono di meno"*. Per arm, at dose 0.500 against dose 0.080:

| group | arm | V at 0.500 | **L at 0.500** | V at 0.080 | L at 0.080 |
|---|---|--:|--:|--:|--:|
| **`Block_4`** | **pos** | **3.28** | **1.2041** | 0.69 | 1.0017 |
| `Block_2` | pos | 1.42 | 1.0807 | 0.30 | 1.0142 |
| `Block_5` | neg | 1.34 | 1.0688 | 0.56 | 1.0037 |
| **`Block_1`** | **pos** | **3.84** | **1.0576** | 0.49 | 0.9912 |
| `Block_4` | neg | 1.29 | 1.0497 | 0.57 | 1.0201 |
| `Block_1` | neg | 2.54 | 1.0208 | 0.55 | 1.0253 |
| `Block_2` | neg | 1.43 | 0.9536 | 0.20 | 1.0123 |
| `Block_3` | neg | 1.80 | 0.9104 | 0.74 | 0.9790 |
| `Block_6` | pos | 3.82 | 0.8200 | 0.95 | 1.0198 |
| `Block_3` | pos | 2.49 | 0.7827 | 0.39 | 0.9967 |
| `Block_6` | neg | 3.95 | 0.6162 | 0.61 | 0.9732 |
| `Block_5` | pos | 5.22 | **0.4266** | 0.83 | 0.9990 |

**`Block_4 pos` at 0.500 moves the image 3.3× the seed floor with the line 20 % stronger than
baseline.** `Block_1 pos` moves 3.8× with the line still above it. At the other end, `Block_5 pos`
moves 5.2× and the drawing is gone.

The pre-registration's analyst prediction — *"at least one central arm (`Block_4`) will reach
V ≥ 2.5 with L ≥ 0.98"* — is **confirmed**: 3.28 and 1.2041. Its companion prediction, *"the
extremes at 0.500 will come out black or washed out"*, is **half wrong**: true of `Block_6`, false
of `Block_1`.

**Operationally this is the largest finding of the bench.** This project has worked at dose 0.200
for months. On `Block_4 pos` and `Block_1 pos`, **0.500 is better on both axes at once** — more
movement *and* a stronger line — and nothing in the corpus had been rendered there.

## 5. What is still owed

**The eye veto has not been run**, and the pre-registration requires it: twelve centre/extreme pairs
at matched V, 1:1 crops, blind. If Alessandro agrees with the ordering of L in fewer than 8 of 12,
the primary is reported as *"L not validated by eye"*. `analyze_centre_push.py` does not implement
it. Until it runs, every L in this document is a statistic nobody has checked against a picture —
which on 2026-09-28 was wrong three times.

## 6. Limits

Three seeds, two prompts, one drawing style; L is structure coherence and
`retro_axes_atlas_result.md` §2 shows it is near-blind on flat styles, so §3 and §4 are claims about
line-bearing work. S2 is dropped, so nothing here says whether the *content* moved, only the
surface. And the dose ladder stops at 0.500 — `Block_4 pos` is still rising at the top of it.
