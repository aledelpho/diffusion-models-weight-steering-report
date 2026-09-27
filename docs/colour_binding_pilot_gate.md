# Stage 1 pilot — the gate passes, and the prior is not what the design assumed

**Date**: 2026-09-27 · **Governed by**:
[`RENDERS_2026-09-27_colour_object_pilot.md`](RENDERS_2026-09-27_colour_object_pilot.md) §2, whose
four criteria were fixed before the renders existed.
**Material**: 15 renders in `benchmark_colour_binding/renders`, launched by Alessandro.

---

## 1. Result — all four criteria pass

Mean hue of the leaf region (background removed as low-saturation bright pixels; hue averaged as a
circular mean weighted by saturation):

| prompt | hue per seed (42, 777, 1337, 9999, 4242145) | mean | band |
|---|---|--:|---|
| **LP** *a single purple leaf* | 311.7 · 308.8 · 313.5 · 299.5 · 311.3 | **308.9°** | violet / magenta |
| **LG** *a single green leaf* | 88.1 · 87.7 · 87.7 · 87.2 · 87.2 | **87.6°** | green |
| **LN** *a single leaf* | 34.8 · 34.2 · 38.2 · 37.1 · 34.3 | **35.7°** | **orange-brown** |

| gate | criterion | observed | |
|---|---|---|---|
| **G1** | `LP` in the violet band, ≥ 4/5 | **5/5** | PASS |
| **G2** | `LG` in the green band, ≥ 4/5 | **5/5** | PASS |
| **G3** | no overlap between `LP` and `LG` | `LP` [299.5, 313.5], `LG` [87.2, 88.1] — **211° apart** | PASS |
| **G4** | leaf present and intact in all 15 | 15/15 | PASS |

`LG` is astonishingly tight: 0.9° of spread across five seeds. The seed noise on this statistic is
negligible, which is exactly what a binding test needs.

**Stage 2 is licensed.** No substitution was needed and the declared purple→blue fallback is not
used.

## 2. The finding the pilot was not looking for, and it changes the design

**The model's own prior for an unqualified leaf is orange-brown, 35.7°. It is not green.**

The runbook's reading table assumed green was the prior and that a broken binding would show as
*purple → green*. That assumption is wrong, and the pilot caught it before 78 renders were spent on
a mis-specified outcome.

Three poles, cleanly separated, and the distances are asymmetric:

| | hue | distance from the prior |
|---|--:|--:|
| prior, `LN` | 35.7° | — |
| `LG`, declared green | 87.6° | **51.8°** |
| `LP`, declared purple | 308.9° | **86.8°** |

Purple is the harder binding, by a factor of 1.7 in hue distance. That is what the design wanted.

### Amendment to the reading table

`LN` is no longer descriptive. It is **the third pole and the target of reversion**, and the reading
becomes:

| outcome | `LP` goes | `LG` goes | reading |
|---|---|---|---|
| **reversion to the prior** | toward **35°** (brown) | toward **35°** (brown) | the declaration stopped being honoured — the binding broke |
| generic rotation | shifts | shifts by the same signed amount | colour drift, not binding |
| **selective reversion** | toward 35° | **stays at 88°** | the *uncommon* binding broke and the common one held — the strongest possible result |
| object collapse | stops being a leaf | stops being a leaf | the object path was hit |

**"Selective reversion" is the row that did not exist before the pilot**, and it is now the outcome
worth hoping for: it would show the edit is not moving colour in general but releasing a binding in
proportion to how unusual it is.

`LN` should therefore be **carried into Stage 2** as a third arm, not left out. That adds
6 blocks × 2 signs × 3 seeds = **36 renders plus 3 baselines**, taking Stage 2 from 78 to **117**.
Alessandro decides whether to spend them; the study is interpretable without them, and stronger
with.

## 3. A defect to fix before Stage 2

`experiments/evaluate_colour_object_gate.py` reported **"15 of 15 renders missing on disk"** while
all fifteen were present and readable at the connected path. The gate above was computed
independently. The path handling must be fixed before it is trusted to gate anything, and the fix
verified against these fifteen files, whose verdict is now known.

A gate that cannot find the files it is gating would have failed the study for the wrong reason.
