# C35 — three of the six kinds of parameter were never touched, and the tool said they were

**2026-09-28.** First reading of `benchmark_parameter_families` (144 graded renders + a 54-render
probe archive, rendered by Antigravity on Alessandro's machine). No render generated here.

## 0. What was already in the repository

Searched `docs/` and `notebook/` for every claim below, in English and in Italian, before writing it:

- **`atlas_vs_tuner_generator.md` (2026-09-26) already established the inertness of `mod.lin`,
  `prenorm.scale` and `postnorm.scale`** — 84 tensors rescaled by `model_alpha = 0.9365`, render
  byte-identical to baseline on eight prompts. It also laid out the **two candidate mechanisms** and
  said which test would separate them. That document is the prior art and it is not superseded.
- `normscales_never_applied.md` is a retraction of a re-derivation of the same thing, written this
  morning. **Its conclusion stands. One of its arguments does not — see §3.**
- `parameter_families.md` (mine, today) enumerated the six kinds but **assumed all six were
  reachable by the tool**. §4 corrects that.
- **`qknorm` inertness is nowhere.** `atlas_vs_tuner_generator.md` notes only that `qknorm` scales
  *resolve*. That they do nothing is new here.
- The removal of the three families from the bench plan exists **only in the message of commit
  `99b5ba0`** — "Rimosse famiglie inerti" — with no document, no evidence and no number attached.
  This document is that evidence.

## 1. The proof, which needs no baseline

`F_norms` (56 × `*.scale`), `F_qknorm` (56 × `*.scale`) and `F_mod` (28 × `mod.lin`) patch **disjoint
sets of tensors**. At **dose +1.000 — a multiplier of 2.0** — their renders are compared pixel by
pixel:

| | pairs | identical | max abs difference |
|---|--:|--:|--:|
| among `norms`, `qknorm`, `mod`, both prompts | **6** | **6** | **0** |

If any patch in any of the three had had an effect, the three could not coincide: the sets share no
tensor. Six identities out of six therefore prove that **none of the three did anything**, and that
their common state is the unperturbed model. Two further checks:

- `F_mod` at **+0.200** and at **+1.000** are identical as well (both prompts, max 0). Dead at every
  dose, not merely at a small one.
- `F_wo d+0.100` reproduces **bit for bit** between the probe archive and the graded bench, so the
  two folders share one workflow and the sampler is deterministic here.

The three that do move are as far apart as they could be: at +1.000, mean |Δ| of `io` against the
inert state is **120.1 / 255**, `wo` **50.0**, `proj` **32.0** (P01; P02: 141.8 / 82.2 / 44.9).

**A side effect worth keeping: the bench rendered no baseline, and the inert families are one.**
Every ratio in §2 is measured against `P01/P02_F_norms_d+1.000_seed42`, which is the untouched model.

## 1b. Where these presets actually land — they cut the model the other way round

Asked on 2026-09-29: do these apply to the whole model, or only to `Block_1`? **Neither.**

| preset | tensors | where | parameters | share of the model |
|---|--:|---|--:|--:|
| `F_wo` | 28 | `blocks.0…27.attn.wo.weight` — **one tensor in every one of the 28 blocks** | 1 056 964 608 | **8.2447 %** |
| `F_io` | 2 | `first.weight` and `last.linear.weight` — **outside the block stack**: the input projection before `blocks.0` and the output projection after `blocks.27` | 786 432 | 0.0061 % |
| `F_proj` | 1 | `txtfusion.projector.weight` — **outside the backbone**, at the end of the text-fusion pipeline that feeds text embeddings into it | 12 | 1 × 10⁻¹⁰ |

**`F_wo` spans every group**, not one: 5 tensors in `Block_1`, 5 in `Block_2`, 5 in `Block_3`, 5 in
`Block_4`, 4 in `Block_5`, 4 in `Block_6`. But it is thin at each depth — the backbone holds 364
tensors, **13 per block**, and `wo` is one of them. It is a *horizontal* slice: a single kind of
tensor taken at every depth.

**`F_io` and `F_proj` are not in the stack at all.** No block contains them, so they cannot be
placed on the `Block_1`…`Block_6` axis even in principle.

**This is the consequence that matters.** The families and the block groups are **orthogonal
decompositions of the same model**: the families cut horizontally by kind of parameter at all
depths, the groups cut vertically by depth across all kinds. So

- nothing in this bench can be attributed to a **depth** — `F_wo` breaking the line at −0.350 says
  nothing about *where* in the stack it broke;
- nothing in `benchmark_centre_push` or `benchmark_mappa` can be attributed to a **kind** — a group
  moves 13 kinds of tensor at once;
- and the two can only be crossed by a bench that holds one fixed and varies the other.

**Correction, 2026-09-29, a few hours after the paragraph above was committed.** That last line
originally read *"which no bench in this project has yet done"*. **It is false.** Asked whether
`F_wo` could be split by block, I looked in `presets/` — which I had not done before asserting the
gap — and found `Arthemy_QKVO_wo_b1_{pos,neg}` and `Arthemy_QKVO_wo_b6_{pos,neg}`, already rendered
in `benchmark_qkvo_atlas`. They are **exactly `Family_wo_d+0.100` restricted to one group**: same
key pattern, same delta 0.1, five tensors for `Block_1` and four for `Block_6`. The cross exists,
for `wo` at the two ends, on eight style prompts × three seeds, 24 cells per condition.

**And when it was split, the two ends did not behave alike** (`data/retro_qkvo_atlas_summary.csv`):

| condition | coherence ratio | band 0 (1–2 px) | displacement |
|---|--:|--:|--:|
| `wo_b1 neg` | 1.0014 | 1.0168 | 0.0814 |
| `wo_b1 pos` | 1.0047 | 0.9917 | 0.0740 |
| `wo_b6 neg` | 0.9656 | **0.9102** | 0.0972 |
| `wo_b6 pos` | 1.0284 | **1.0806** | 0.0813 |

At the front of the stack `wo` is nearly neutral in both arms; at the back it is a **strongly
antisymmetric fine-grain knob** — 9 % of the finest octave removed one way, 8 % added the other —
at comparable displacement. **So `F_wo` moving all 28 blocks together is a mixture, and the mixture
hides an antisymmetry that appears as soon as the family is cut by depth.**

What is still missing is `Block_2`…`Block_5` for `wo`, and — because the atlas uses the eight style
prompts `S1`…`S8` while the family bench uses `P01`/`P02` — **no render currently allows the whole
to be compared against the sum of its parts.** That comparison is the same question `C14` asks in
another context, and it is registered as **C41**.

> **An error found in the repository while answering this.**
> `docs/model_structures/krea2_architecture_decomposition.md` §3b lists the projector as
> `txtfusion.projector.scale`, shape **[12]**. The checkpoint it names — the same
> `krea2_turbo_bf16.safetensors`, same 430 tensors — contains **`txtfusion.projector.weight`,
> shape [1, 12]**, and no `.scale` key at all. The preset uses the real name, which is why it works.
> This is not cosmetic: **§3 below turns on that tensor being two-dimensional**, and a reader going
> by the architecture document would conclude the exact opposite. Registered as **A10**; the
> document is not edited here, because it is not mine to rewrite on one tensor.

## 2. What the three live families actually do

Seed 42, both prompts, against that derived baseline. `L` is structure coherence over the baseline.

| family | tensors | parameters | shape | at −0.350 | at +0.350 |
|---|--:|--:|---|---|---|
| **`F_wo`** attention output | 28 | 1 056 964 608 | [6144, 6144] | **the ink line is gone** — hatching dissolved into a mottled painterly surface; `L` 0.871 / 0.875 | line intact, contrast up; `L` 1.007 / 1.042 |
| **`F_io`** latent interface | 2 | 786 432 | [6144, 64], [64, 6144] | **annihilated** — coloured noise porridge, no drawing left; `L` 0.796 / 0.808 | line intact, strong colour shift toward red and blue; `L` 0.932 / 1.000 |
| **`F_proj`** the 12-parameter router | 1 | **12** | [1, 12] | clean line; `L` 1.032 / 1.020 | clean line; `L` 0.990 / 1.039 |

Three things follow.

1. **The dose is not a common currency.** ±0.350 on 1.06 billion parameters, on 786 thousand, and on
   **twelve**, are all called "dose 0.350" by the tool. Nothing in the project's dose ladders means
   the same thing across kinds, and `parameter_families.md` §3 said matched Frobenius displacement
   could not compare five kinds of six; this is the picture of that.
2. **Both destructive families destroy on the negative arm only.** `wo` and `io` are safe out to
   +0.350 and broken at −0.350 — a sign asymmetry, in agreement with Punto 7, measured here on
   parameter kind rather than on block.
3. **Twelve parameters survive ±0.350 with the drawing intact.** `F_proj` is the gentlest knob in the
   bench and the smallest by five orders of magnitude.

`L` behaves correctly on this bench — it drops exactly where the eye sees destruction. That is worth
recording next to `centre_push_eye_veto_result.md`, where it failed: **`L` catches gross collapse
and inverts on fine speckle.** Two different failure modes, and only one of them is visible here.

## 3. The signature: every dead tensor is one-dimensional

| | shape | ndim | |
|---|---|--:|---|
| `blocks.N.prenorm.scale`, `postnorm.scale` | [6144] | **1** | dead |
| `blocks.N.attn.qknorm.{q,k}norm.scale` | [128] | **1** | dead |
| `blocks.N.mod.lin` | [36864] | **1** | dead |
| `blocks.N.attn.wo.weight` | [6144, 6144] | 2 | live |
| `first.weight`, `last.linear.weight` | [6144, 64], [64, 6144] | 2 | live |
| `txtfusion.projector.weight` | **[1, 12]** | 2 | live |

Two confounds are ruled out by the table itself. **Size is not the rule:** the projector is twelve
parameters in a degenerate [1, 12] matrix and it works. **Dtype is not the rule:** the dead are all
F32 and so are `first`, `last` and the projector, which are live.

**The checkpoint has 430 tensors and 165 of them are one-dimensional.** If the rule is
dimensionality, the tool cannot reach **38 % of the model's tensors**, and every one of them is a
gain, a temperature or a modulation — the parameters that set *how much*, as opposed to *what*.

This is the mechanism proposed in `normscales_never_applied.md` this morning and **retracted the
same day**, on the grounds that the Preset Loader reported 84 of 84 matched. That ground is now
gone. The loader's log for this bench reads `Model: 56 scalar layers` for `norms`, `56` for
`qknorm`, `28` for `mod`; the source shows the counter it prints, `n_model_matched`, is incremented
when the key resolves and `add_patches` is called — **it counts registration, never effect.** The
retraction's conclusion was right for a different reason (it was already known, and
`atlas_vs_tuner_generator.md` says it better); its argument against the mechanism was wrong. Neither
the withdrawal nor this correction settles the mechanism, which remains the two branches that
document already set out.

## 4. The test that would settle it — cheap, and I have not run it

The rule "one-dimensional" and the rule "gains and modulation are ignored by the forward pass" make
the same prediction on all six families here. **One preset separates them**, because the checkpoint
contains a modulation tensor of each shape:

- `blocks.N.mod.lin` — **[36864], 1-D** — dead, shown above;
- `last.modulation.lin` — **[2, 6144], 2-D** — never tried.

Both are modulation. If the 2-D one moves the image and the 1-D ones do not, the rule is
**dimensionality** and the tool has a repairable defect. If neither moves, the rule is **function**
and the model genuinely ignores modulation. A second, tighter pair does the same job inside one
module: `first.weight` [6144, 64] is live, and `first.bias` [6144] is 1-D and untried.

Registered as **C40**. ~12 renders, two presets, one prompt, three seeds.

## 5. Limits

Seed 42 only for every ratio in §2 — the bench rendered no baseline, and the free one the inert
families provide exists at that seed alone. Two prompts, one drawing style. `L` is the axis a human
eye failed to validate today on a different bench, so §2's numbers are reported beside what the
crops show, not instead of it. And the inertness proof covers the six families **as this bench built
them**: it says nothing about the 1-D tensors those presets did not name.

## 6. Provenance

- `experiments/measure_parameter_families.py --inert --ladder` →
  `data/parameter_families_inert.csv` (30 rows), `data/parameter_families_ladder.csv` (48 cells).
- Renders: `benchmark_parameter_families/renders` (144) and `archive_d100` (54), by Antigravity.
- Loader counts: `benchmark_parameter_families/renders/tuner_logger_capture.log`.
- Shapes: `docs/model_structures/krea2_turbo_bf16_details.json`.
- Contact sheets and 1:1 crops: `benchmark_parameter_families/_sheets/`.
