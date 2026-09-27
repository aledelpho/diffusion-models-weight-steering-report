# Where the internal fights are — all six groups, dissected by depth

**Date**: 2026-09-27 · **Question**: Alessandro — are there fights in the other blocks too,
members pushing positive and negative at once? **Material**: `benchmark_profondita` / `_neg`
(28 single blocks, ±0.200) against `benchmark_mappa` (the six groups at 0.200), all on disk.
**No render.** Exploratory.

---

## 1. Method, and the gate that stops it firing on noise

Group definitions from the tuner itself (`Arthemy_Krea2_Tuner.py` line 2041): `Block_1` = 0–4,
`Block_2` = 5–9, `Block_3` = 10–14, `Block_4` = 15–19, `Block_5` = 20–23, `Block_6` = 24–27.

Two properties, both with a clean estimator: **contrast** (variance ratio) and **grain per unit of
contrast** (`r_cnorm`, the corrected statistic from `texture_estimator_audit_result.md`).

A member counts as **active** only if it agrees in **5 or 6 of its 6 cells**. A **fight** needs at
least two active members pointing opposite ways. *The first pass of this analysis had no such gate
and flagged fights everywhere — on members sitting 1 % from 1. The gate is the difference between
this being an answer and being pattern-matching.*

## 2. Answer: yes, and they are concentrated

### Contrast

| group | arm | up | down | composition of parts | the group | |
|---|---|---|---|--:|--:|---|
| `Block_1` | pos | — | `blk00` 0.797 | 0.734 | 0.788 | one active block, additive |
| **`Block_4`** | **pos** | `blk15` **1.072** | `blk17` **0.870**, `blk18` **0.889** | 0.898 | **1.102** | **fight → reversion** |
| **`Block_4`** | **neg** | `blk18` **1.085** | `blk15` 0.897, `blk16` 0.894, `blk19` | 0.822 | **1.072** | **fight → reversion** |
| `Block_5` | pos | `blk20` 1.072, `blk21` 1.105, `blk22` **1.128** | `blk23` | 1.236 | 1.122 | fight → saturation |
| **`Block_6`** | **pos** | `blk24` 1.042 | `blk25` 0.914, `blk26` **0.782** | 0.655 | **0.839** | **fight → saturation** |
| `Block_6` | neg | `blk25` 1.118 | `blk24` 0.969, `blk26` 0.950 | 1.076 | 1.090 | fight, additive |

**`Block_4` is the fight block.** Both arms, both directions, active members 7–13 % from 1 — and in
both arms **the group does the opposite of what composing its parts predicts**: the parts multiply
to 0.898 and the group lands at 1.102. That is not saturation. That is a sign reversal at the group
level, and it is the only place in the table where it happens on both arms.

### Grain per unit of contrast

| group | arm | up | down | composition | the group | |
|---|---|---|---|--:|--:|---|
| **`Block_6`** | **pos** | **`blk27` 1.156** | `blk24` 0.864, `blk25` 0.860, `blk26` **0.763** | 0.655 | **1.089** | **fight → reversion, the largest in the table** |
| `Block_6` | neg | `blk26` 1.081 | `blk24` 0.953, `blk25` 0.862, `blk27` | 0.747 | 0.782 | fight, additive |
| `Block_4` | neg | `blk17` 1.124 | `blk15` 0.943, `blk16` 0.901 | 0.935 | 0.929 | fight, additive |
| `Block_5` | neg | `blk20` 1.165 | `blk23` 0.955 | 1.062 | 1.116 | fight → super-additive |
| `Block_1` | pos | `blk01` 1.103 | `blk03` 0.964 | 1.029 | 1.091 | fight → super-additive |

**`Block_6 pos` is the most dramatic case in either table.** Three of its four blocks push grain
*down* — `blk26` by 24 % — and the fourth, `blk27`, pushes *up* by 16 %. The composition of the four
predicts **0.655**. The group delivers **1.089**. **One block overturns the other three.**

## 3. The block that overturns its group is the block Punto 7 already singled out

`punto7_attrito_e_rettificazione.md` §3, written a week ago on a different statistic:

> *"L'unica eccezione è **`blk27`**, l'ultimo blocco, che inverte il pattern in ogni sua parte: è
> più violento in negativo, ed è l'unico della coda che alza l'alta frequenza in positivo (swing
> **1.393**, il massimo dei 28…). **Merita un esperimento suo.**"*

Same block, reached by a different route. It was identified as the anomaly of the tail by its swing;
here it is the single member that reverses the sign of its whole group on grain. **Two independent
statistics nominate `blk27`, and the experiment it was said to deserve has still not been run.**

## 4. The other failure mode, which is not a fight

`Block_3` on grain, positive arm: `blk12` 1.173, `blk13` 1.091, `blk14` 1.225 — **all three
concordant**, no fight at all. Composition predicts **1.487**; the group delivers **1.124**.

**Three blocks pushing the same way waste a third of their combined effect.** That is the angle rule
(ρ = 0.939 − 0.278·cos, `regola_angolo_9_coppie.md`) appearing *inside* a group, between sub-blocks,
where it had only ever been measured between groups.

So there are two distinct ways a slider dilutes itself, and only one is a fight:

* **members opposed** — `Block_4` on contrast, `Block_6` on grain;
* **members concordant and saturating** — `Block_3` on grain, `Block_5` on contrast.

A sign mask addresses the first and would do nothing about the second.

## 5. Where this leaves the sign-mask proposal

The pre-check in `assessment_sign_correction_mask.md` failed at q/k/v/o granularity and on the 23
global descriptors. **At depth granularity and on a clean property, the opposed structure it was
looking for does exist** — in `Block_4` and `Block_6`, not in `Block_1`.

So the proposal is not dead; it was tested at the wrong granularity on the wrong property.
`Block_4` on contrast is where a mask would have something to rectify, and the rectified preset
would be: `blk15` one way, `blk17` and `blk18` the other. **Whether that beats `RANDSIGN` at matched
displacement is the experiment, and the control already exists.**

## 6. Limits

* Parts at 0.200 on one block, groups at 0.200 on four or five. The per-block gain is matched, which
  is what makes the composition question well posed, but the group's total displacement is 4–5×.
* Two prompts, six cells per member. The 5/6 gate is coarse and a member at 4/6 is simply not
  counted, which will miss real but weaker effects.
* Two properties. Nothing here says anything about the other twenty-one traits, or about anything
  localised.
* Every group value is measured at dose 0.200 only.
