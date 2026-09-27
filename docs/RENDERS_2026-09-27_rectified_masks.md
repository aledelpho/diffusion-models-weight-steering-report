# Render spec — rectified sign masks on Block_4 and Block_6

- **For:** Alessandro, who launches every render. **The analyst generates none.**
- **Origin:** [`internal_fights_by_group.md`](internal_fights_by_group.md) found the opposed
  structure; the antisymmetry pre-check below says which members a mask can actually use.
- **72 renders.** Every condition earns its place; nothing is included "for completeness".

---

## 1. The pre-check, and the design consequence it forces

A sign mask only works if flipping a member's gain **flips its contribution**. Checked on
`benchmark_profondita`, 6 cells per member:

**`Block_4`, contrast:**

| block | pos | cells>1 | neg | cells>1 | usable? |
|---|--:|--:|--:|--:|---|
| **`blk15`** | **1.072** | 5/6 | **0.897** | 0/6 | **yes** |
| `blk16` | 1.035 | 4/6 | 0.894 | 0/6 | weak |
| `blk17` | 0.870 | 1/6 | 1.038 | 4/6 | weak |
| **`blk18`** | **0.889** | 0/6 | **1.085** | 6/6 | **yes** |
| `blk19` | 1.046 | 3/6 | 0.911 | 0/6 | weak |

**`Block_6`, grain:**

| block | pos | cells>1 | neg | cells>1 | usable? |
|---|--:|--:|--:|--:|---|
| `blk24` | 0.864 | 0/6 | 0.953 | 0/6 | **no — both arms lower grain** |
| `blk25` | 0.860 | 0/6 | 0.862 | 0/6 | **no — both arms lower grain** |
| **`blk26`** | **0.763** | 0/6 | **1.081** | 6/6 | **yes** |
| **`blk27`** | **1.156** | 6/6 | **0.841** | 0/6 | **yes** |

> **`blk24` and `blk25` are rectified at the single-block level: they lower grain whichever way you
> push them.** A sign mask cannot use them, because there is no sign to flip. They must be
> **switched off**, not flipped.

**So a mask is not only signs. It is signs *plus a selection*** — and both masks come out as
two-block presets rather than five- or four-block ones. That was not anticipated and it changes what
is being compared: the mask's Frobenius displacement is far smaller than the group's.

## 2. The two masks

| preset | blocks | all members push |
|---|---|---|
| **`B4_mask`** | `blk15` at **+d**, `blk18` at **−d**, others 0 | contrast **up** |
| **`B6_mask`** | `blk27` at **+d**, `blk26` at **−d**, others 0 | grain **up** |

And the control that matters is not a random mask — with two blocks, "random" has four outcomes and
two of them *are* the mask. The sharp control is the **anti-mask**: the same two blocks, the same
|d|, the same displacement, **both at the same sign** — which is exactly what the group slider does
to them.

| preset | blocks |
|---|---|
| `B4_anti` | `blk15` at **+d**, `blk18` at **+d** |
| `B6_anti` | `blk27` at **+d**, `blk26` at **+d** |

**Mask against anti-mask differs only in one relative sign, at identical displacement.** No other
control in this project is that clean.

## 3. Is the combined arm worth it? Yes, for a reason that is not "more of the same"

`B4_mask` targets **contrast**. `B6_mask` targets **grain**. They are two different axes, so the
combination is not a bigger knob — it is a test of **selectivity**:

> Does `B4_mask + B6_mask` move contrast like `B4_mask` **and** grain like `B6_mask`, independently
> — or does it collapse into the common mode that carries 45 % of every edit?

That is the most valuable question in the design, and neither single arm can ask it.

It also pays a second time. The angle rule, ρ = 0.939 − 0.278·cos
(`regola_angolo_9_coppie.md`), predicts the combination from the singles. Measuring it adds a point
to that rule **from material that was not used to build it, at sub-block granularity**, where it has
only ever been measured between whole groups. That is queued work (**C12** in the register) obtained
for free.

## 4. The design — 72 renders

Dose **d = 0.200** per block, to match the corpus the members were measured on. Prompts `P01`,
`P02`; seeds **42, 777, 1337**. Baselines already exist in `benchmark_mappa`.

| condition | signs | cells | renders |
|---|--:|--:|--:|
| `B4_mask` | 2 | 6 | 12 |
| `B4_anti` | 2 | 6 | 12 |
| `B6_mask` | 2 | 6 | 12 |
| `B6_anti` | 2 | 6 | 12 |
| `B4B6_mask` | 2 | 6 | 12 |
| `B4B6_anti` | 2 | 6 | 12 |
| | | | **72** |

Already on disk and **not** to be re-rendered: `Block_4 ±` and `Block_6 ±` at 0.200
(`benchmark_mappa`), every single block at ±0.200 (`benchmark_profondita`), the baselines.

Folder `benchmark_rectified_masks\renders`; filenames `B4_mask_pos_seed42_00001_.png` and so on.
Settings identical to every bench: `euler_ancestral`, `simple`, 9 steps, CFG 1.0, 1024 × 1280.

## 5. Predictions, frozen before the renders

Derived by composing the measured singles — nothing is fitted here.

| # | condition | statistic | predicted | confirmed if | falsified if |
|---|---|---|--:|---|---|
| **M1** | `B4_mask` pos | contrast | 1.072 × 1.085 = **1.163** | > 1.08 | < 1.02 |
| **M2** | `B4_anti` pos | contrast | 1.072 × 0.889 = **0.953** | < 1.00 | > 1.06 |
| **M3** | `B6_mask` pos | grain | 1.156 × 1.081 = **1.250** | > 1.12 | < 1.03 |
| **M4** | `B6_anti` pos | grain | 1.156 × 0.763 = **0.882** | < 0.95 | > 1.02 |
| **M5** | the mask beats the anti-mask | separation | **0.21** on contrast, **0.37** on grain | both gaps > 0.08 | either gap < 0 |
| **M6** | selectivity | `B4B6_mask` moves contrast like `B4_mask` **and** grain like `B6_mask`, each within 0.10 | both | either outside 0.20 |

**M5 is the experiment.** M1–M4 are the arithmetic it rests on; if they fail, additivity at
sub-block level fails and M5 means nothing whatever it says.

**M6 is the one worth hoping for.** If it holds, the tuner has two independent axes built from four
blocks. If it fails, the common mode swallows both and the register's §F changes.

## 6. Standing constraints

- The analyst generates no render and requests none beyond this document.
- Nothing written under `notebook/`. No claim status changes.
- Validator at 0 errors before every commit; commit messages in Italian; repository content in
  English; **do not push**.
