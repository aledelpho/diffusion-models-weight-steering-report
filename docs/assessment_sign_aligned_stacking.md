# Assessment — finding the sign inversions and driving them together

**Date**: 2026-09-27 · **Proposal**: Alessandro — find every sign inversion at sub-block or tensor
level, then control them together, growing positive and negative in one direction or the other.
**Assessment**: analyst, from existing measurements. **No render.** Nothing here changes a claim.

---

## 1. The project has measured this twice, and the answer is the opposite of the intuition

**Previsione 01** (deposited 2026-09-19 **before** the renders, 12 images):

| combination | quantities within 1 SD of the additive prediction | verdict |
|---|:--:|---|
| **`B5 + B1`** — **opposite** signs on tone | **4/4** | **CONFIRMED, they add** |
| **`B5 + B4`** — **concordant** signs | **0/4** | **REFUTED, they do not add** |

**The angle rule**, nine pairs, `regola_angolo_9_coppie.md`:

ρ = ‖Δ(A+B)‖ / ‖Δ(A) + Δ(B)‖ — 1.00 means two edits add exactly, below 1 means they waste each
other.

| | ρ | cos(A,B) |
|---|--:|--:|
| `B1+B4` | **1.167** | −0.14 |
| `B2+B6` | 1.007 | −0.43 |
| `B5+B6` | 0.980 | +0.16 |
| `B5+B1` | 0.929 | −0.34 |
| `B1+B2` | 0.864 | +0.56 |
| `B3+B5` | 0.794 | +0.20 |
| `B3+B6` | 0.740 | +0.80 |
| `B5+B4` | 0.687 | +0.77 |
| `B4+B6` | 0.662 | +0.64 |

**ρ = 0.939 − 0.278·cos**, Pearson r = −0.791, p = 0.011. The slope was estimated on four pairs at
−0.282 and on nine at **−0.278** — it moved by 0.004 when five independent pairs were added.

> **Edits that point in different directions add. Edits that point in the same direction saturate
> and waste each other, up to a third of the combined displacement.**

Taken naively, that refutes the proposal: *"align them all on the property and push"* is the
concordant case, which is the one that failed 0/4 and sits at the saturating end of the line.

## 2. But the naive reading conflates two different alignments, and the distinction saves the idea

`cos(A, B)` in the angle rule is the cosine between the **whole displacement vectors** in the
23-feature space. The proposal aligns the units on **one target property**.

Those are not the same thing. Two edits can have `cos(Δ_A, Δ_B) = −0.3` overall — mostly doing
different things — while **both pushing contrast the same way**. Combined, they sit in the
*additive* end of the rule, and their contrast contributions add.

So the design criterion is not "pick the units that agree on the property". It is:

> **Pick units that push the target property the same way and are otherwise as different as
> possible. Maximise the target component; minimise the overall cosine.**

That is the opposite of what "align everything" suggests, it is derivable from two measured
results, and it is testable.

`B5 + B1` is the existence proof already in hand: opposite on tone, and 4/4 additive.

## 3. What makes tensor-level feasible at all

Measuring every unit's signed effect directly is out of reach. 430 patched model tensors × 2 signs
× 6 cells = **5 160 renders**.

**The angle rule is what removes that cost.** If ρ is predictable from the singles, you never render
the combinations — you measure each unit once and *compute* which stack maximises the target. The
rule is the thing that turns an enumeration into a design problem.

Sizing a first signed map, at the granularity the project already has working — and, per pitfall
candidate 71, enumerating **the tuner's own exposed controls** and not the checkpoint hierarchy:

| granularity | units | renders (2 signs × 2 prompts × 3 seeds) |
|---|--:|--:|
| 4 projections × 6 bands | 24 | **288** |
| attention only, 4 × 6 | 24 | 288 |
| + MLP up/down/gate × 6 | 42 | 504 |
| every patched tensor | 430 | 5 160 |

**288 renders buys the signed map at q/k/v/o granularity**, which is the granularity where this
project has already shown a real functional split (`wv`/`wo` carry the control, `wq`/`wk` do not).

## 4. The load-bearing caveat, and it decides the order of work

`regola_angolo_9_coppie.md` §5 declares it itself:

> all nine pairs are at **dose 0.200**, a regime where half the blocks lie **73–99 %** along the
> common degradation axis, and where the cosines between blocks correlate only **r = +0.42** with
> the cosines at dose 0.050.

**The law is established between displacements in a degraded regime.** Whether it is a property of
composition or an interaction between two contributions of grain is undecided, and the low-dose
replication is already queued (`BRIEF_20sett_coda_lunga.md` point 6).

And today's measurements sharpen the worry rather than easing it: image motion goes as **dose^0.19**,
and **45 %** of a block edit's effect is a global mode identical for every block and every sign
(`sign_decomposition_result.md` §3). A saturating response and a shared common axis are two names
for the same suspicion — that ρ < 1 at high cosine is the common mode saturating, not composition
failing.

**Therefore the order is:**

1. **Replicate the angle rule at low dose.** The whole proposal rests on it, it is cheap, and the
   pairs already exist at 0.200 to compare against. Without this, a 288-render signed map is built
   on a law measured only where everything is already degraded.
2. **Then** the signed map at q/k/v/o granularity, 288 renders.
3. **Then** solve for the stack: maximise the target component, minimise the overall cosine, and
   render only the predicted optimum plus its controls.

## 5. One more thing worth measuring, and it is free

`B1+B4` gives **ρ = 1.167 ± 0.058** — **2.9 standard errors above 1**. Two edits together move the
image **more** than the sum of their separate effects. Nothing predicted it, it is one point, and it
is the only pair at slightly negative cosine among the nine.

If super-additivity is systematic near cos ≈ −0.2, the straight line is the chord of a curve, and
**the optimum stack is not the one the linear rule would choose**. That single point is the most
interesting number in the composition work and it needs one more pair between cos −0.2 and 0.0
before anything can be said.
