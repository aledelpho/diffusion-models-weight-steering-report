# Stage 2 — no dissociation, and the reason the verdict does not name

**Date**: 2026-09-27 · **Material**: 117 measurements over 134 renders in
`benchmark_colour_binding`, launched by Alessandro, measured by Antigravity.
**Governed by**: [`RENDERS_2026-09-27_colour_object_pilot.md`](RENDERS_2026-09-27_colour_object_pilot.md)
and the amended reading table in
[`colour_binding_pilot_gate.md`](colour_binding_pilot_gate.md) §2.
**Data**: `data/colour_object_sweep_measurements.csv`, `data/colour_object_sweep_verdict.csv`.
**Independently recomputed** from the images with the pilot's own estimator; every hue agrees with
the recorded measurement to within **0.3°**, and the three baselines reproduce the pilot exactly.

---

## 1. The verdict stands: no dissociation at dose 0.050

**117 of 117 objects intact.** No condition produced reversion, generic rotation or collapse. The
three pre-registered outcomes did not occur.

How far each declared colour travelled toward the prior at 35.7°:

| arm | distance to the prior | largest shift | fraction of the way |
|---|--:|--:|--:|
| **`LP`** purple, declared | 83.8° | 11.8° | **14.1 %** |
| **`LG`** green, declared | 52.3° | 1.3° | **2.6 %** |

Nothing came close to breaking.

## 2. What the verdict table does not say

The classification column is keyed to whichever arm moved, so a row where `LP` moved 0.5° and `LN`
moved 15.7° is labelled *"partial chromatic shift — asymmetric shift without full reversion"*. True,
but it reads as a statement about the binding when it is a statement about the arm that has none.

Sorted by arm instead of by condition, the pattern is the finding:

| arm | conditions shifting hue by more than 5° | largest shifts |
|---|--:|---|
| `LG` — green, **declared** | **0 / 12** | 1.3, 1.3, 1.3, 1.2 |
| `LP` — purple, **declared** | **3 / 12** | 11.8, 6.3, 5.7, 3.9 |
| **`LN` — nothing declared** | **6 / 12** | **33.2, 31.0, 15.9, 15.7** |

> **The colour the prompt declares is pinned. The colour the model chooses for itself moves — by up
> to 33°, out of orange-brown and into yellow-green.**

`LN` moves more than `LP` in **9 of 12** conditions and more than `LG` in **9 of 12**,
sign test **p = 0.073** each. **Consistent, not established** — twelve conditions cannot reach 0.05
at 9/12.

## 3. The denominator objection, raised and dismissed

The obvious complaint is that `LG` barely moves because `LG` is simply a stable render. It does not
survive the numbers:

| arm | seed noise | largest shift | ratio |
|---|--:|--:|--:|
| `LG` | 0.14° | 1.3° | 9.5 |
| `LP` | 2.41° | 11.8° | 4.9 |
| **`LN`** | **1.74°** | **33.2°** | **19.0** |

**`LN` has *lower* seed noise than `LP` and moves three times further.** Mobility is not tracking
stability, so the declared/undeclared difference is not a noise artefact.

*(On the noise-normalised scale the picture is weaker — `LN` mean |z| 5.00 against 1.96 for the
declared arms, but only 7/12 conditions, p = 0.387, because `LG`'s 0.14° noise inflates its z. The
raw-degree scale is the one argued from here, because "did the binding loosen" is a question about
how far the colour actually went, not about how many noise units. Both are reported so the choice
is visible.)*

## 4. Where this sits against the other colour results

This is the measurement that [`colour_and_concept.md`](colour_and_concept.md) §5 said was missing.
That document's §3 found declared-versus-undeclared **not testable** on the existing corpora, and
`declared_colour_result.md` tested it on six matched pairs and found **nothing** — 3/3, p = 1.000.

The two are not in conflict, and the difference is exactly the one `colour_and_concept.md` §5
declared out of scope:

* the morning study varied a **rim-light** colour and measured **global** colour descriptors;
* this varies the colour **of the object** and measures the hue **of that object**.

**A colour attached to a thing behaves differently from a colour attached to the light.** The
morning null was a true null for what it measured.

And the direction here is **ColorWave's**, not the one Alessandro predicted: a declared colour token
binds hard and resists. His hypothesis was that a declared colour, being a live variable, would move
*more*. On this bench it moves *less*, in 18 of 24 arm-condition comparisons.

## 5. The design stopped short, and the data says so

Dose **0.050** was chosen because at 0.200 an object that has collapsed cannot show a colour
reversion (`RENDERS_2026-09-27_colour_object_pilot.md` §3).

**117 of 117 objects came back intact.** The caution was not needed: there was headroom everywhere,
and the sweep never approached the regime where a binding could plausibly break. `LP` moved 14 % of
the way to the prior at the dose chosen to be safe.

**A second sweep at 0.120 and 0.200 is now justified by data rather than guessed**, and it is the
same 78 renders per dose. The object-integrity measure that made 0.050 look prudent is the same one
that can be watched to know when to stop.

## 6. Limits

* One subject, one style, one dose. Three seeds.
* The declared colour is an **object** colour here and a **lighting** colour in the morning study;
  neither generalises to the other.
* `LN` has no binding to break, so its motion is free drift, not reversion. The comparison is
  "pinned versus free", which is the right contrast for this question but is not the same as
  observing a binding break.
* Sign tests at 9/12 give p = 0.073. Nothing here clears 0.05.
