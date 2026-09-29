# Render spec — `wo` cut by depth (C41)

- **For:** Alessandro, who launches every render; prepared for Antigravity to queue.
- **254 renders** total across three doses (±0.100, ±0.200, ±0.350), one pass, no stages and no gate.
- **Governed by** [`prereg_wo_depth.md`](prereg_wo_depth.md), frozen before any render exists.
- **Origin:** Alessandro's question of 2026-09-29 — *"so can `F_wo` not be split by block either?"*
  Extended to ±0.200 and ±0.350 on Alessandro's request to observe higher doses.

---

## 1. Why, in three sentences

`Family_wo_d±δ` moves the attention output projection in **all 28 blocks at once**, so what it
does cannot be placed anywhere in the stack. When that same set was split at the two ends by
`benchmark_qkvo_atlas`, the ends behaved differently — blocks 0–4 nearly neutral, blocks 24–27 a
strongly antisymmetric fine-grain knob. **The family result is a mixture**, and this bench cuts it
into its six parts across multiple doses (±0.100, ±0.200, ±0.350) and then asks whether the parts
add back up to the whole.

## 2. What is new here, and what it costs

**Nothing is being invented.** The presets split `Family_wo` across slices `b1`..`b6`.
For δ = ±0.100, four conditions (`b1`, `b6`, both signs) reuse the atlas presets unchanged.
For δ = ±0.200 and δ = ±0.350, dedicated slice presets `WO_b{1..6}_d{+,-}{0.200,0.350}.json` were generated
and matched against the full union presets `Family_wo_d{+,-}{0.200,0.350}.json`.

**Six baselines are not rendered.** `P01` and `P02` here are the same prompts as
`benchmark_centre_push` (same sha1) at the same three seeds and the same sampler settings, so its
six baselines are borrowed. **Two determinism rows pay for that**: one baseline re-rendered per
prompt. Determinism test $G_{det}$ was executed on P01 and P02 with 0 pixel difference (borrow strictly valid).

Saved: 6 renders and, more importantly, the right to compare directly against a bench already
analysed.

## 3. The queue

`data/wo_depth_plan.csv`, 254 rows:

| rows | arm | dose | what |
|--:|---|---|---|
| 1–2 | `determinism` | 0 | `P01`/`P02` baseline at seed 2718281, **no preset**, output prefix ends `_C41` |
| 3–86 | `push` | $\pm 0.100$ | 14 conditions (6 slices + union $\times$ 2 signs) × 2 prompts × 3 seeds |
| 87–170 | `push` | $\pm 0.200$ | 14 conditions (6 slices + union $\times$ 2 signs) × 2 prompts × 3 seeds |
| 171–254 | `push` | $\pm 0.350$ | 14 conditions (6 slices + union $\times$ 2 signs) × 2 prompts × 3 seeds |

The fourteen conditions:

| condition | preset file | tensors | blocks |
|---|---|--:|---|
| `slice_b1_pos` / `_neg` | `Arthemy_QKVO_wo_b1_{pos,neg}.json` | 5 | 0–4 |
| `slice_b2_pos` / `_neg` | `WO_b2_{pos,neg}.json` | 5 | 5–9 |
| `slice_b3_pos` / `_neg` | `WO_b3_{pos,neg}.json` | 5 | 10–14 |
| `slice_b4_pos` / `_neg` | `WO_b4_{pos,neg}.json` | 5 | 15–19 |
| `slice_b5_pos` / `_neg` | `WO_b5_{pos,neg}.json` | 4 | 20–23 |
| `slice_b6_pos` / `_neg` | `Arthemy_QKVO_wo_b6_{pos,neg}.json` | 4 | 24–27 |
| `union_pos` / `_neg` | `Family_wo_d{+,-}0.100.json` | 28 | 0–27 |

Every preset carries **δ = ±0.100** on `blocks.N.attn.wo.weight` and nothing else. The generator
refused to write a file until it had checked that the six slices are pairwise disjoint and that
their union is **exactly** the key set of `Family_wo_d+0.100.json`.

## 4. Settings — identical to `benchmark_centre_push`, and they must stay identical

`Real Value` · `euler_ancestral` · `simple` · **9 steps** · cfg **1.0** · denoise **1.0** ·
**1024×1280** · `ArthemyKrea2ResetPatcher` before every load.

**If any of these changes, the borrowed baselines become invalid** and the determinism rows will
catch it. Do not "improve" the sampler for this bench.

## 5. Where the output goes

`C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_wo_depth\renders`, file names exactly as
`expected_filename` in the plan.

**Keep the tuner log**, as `renders/tuner_logger_capture.log`. It is a guard, not a courtesy: the
analysis checks that each preset reported its expected matched count — 5, 5, 5, 5, 4, 4 and 28.

## 6. What this cannot answer

One dose, one kind of parameter, two prompts, one drawing style. It says nothing about `wo` at other
doses, nothing about the other twelve kinds of tensor in a block, and nothing about whether
composition holds for a *different* family. It is one clean instance of a question the project has
answered once before, on masks, and answered in the negative.

## 7. Checklist before queueing

- [ ] `presets/WO_b{2,3,4,5}_{pos,neg}.json` present — 8 files, written by
      `experiments/make_wo_depth_presets.py`
- [ ] `presets/Arthemy_QKVO_wo_b{1,6}_{pos,neg}.json` present — 4 files, already in the repository
- [ ] `presets/Family_wo_d{+,-}0.100.json` present — 2 files, already in the repository
- [ ] settings match §4 exactly
- [ ] the two determinism rows are queued **first**
- [ ] the tuner log is being captured
