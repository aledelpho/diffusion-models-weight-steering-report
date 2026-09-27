# Render spec — colour/object dissociation, feasibility pilot

- **For:** Alessandro, who launches every render. **The analyst generates none.**
- **Governed by:** [`assessment_colour_object_dissociation.md`](assessment_colour_object_dissociation.md).
- **Stage 1 is a gate.** Stage 2 is not launched unless Stage 1 passes, and Stage 1 is **15 renders**.

---

## 0. Why there is a gate at all

`edit-adds-and-removes-unasked-traits` (page 02, `ambiguous`) had its pre-registered confirmation
killed by one sentence: *"9 of its 10 prompts never light a headlight in any condition."* The corpus
was chosen without checking that the attribute had room to move. **That is the only way this study
can fail cheaply, so it is checked first.**

If Krea-2 already renders *a purple leaf* as green without any perturbation, the design is at floor
and nothing downstream can be measured. Fifteen renders decide it.

## 1. Settings — identical to every bench in this project

| | |
|---|---|
| model | `krea2_turbo_bf16.safetensors` |
| CLIP | `qwen3vl_4b_bf16.safetensors` |
| sampler | `euler_ancestral` |
| scheduler | `simple` |
| steps | **9** |
| CFG | **1.0** |
| denoise | 1.0 |
| resolution | **1024 × 1280** |
| tuner | **absent, or every gain at zero** for Stage 1 |

Do not change any of these. Comparability with the existing corpora depends on them, and
`node-is-identity-at-zero` and `deterministic-across-sessions` are the two claims that make the
whole notebook measurable.

## 2. Stage 1 — the pilot. 15 renders.

Three prompts × five seeds. **Seeds: 42, 777, 1337, 9999, 4242145** — the five this project has used
throughout.

The template is deliberately bare: one object, plain ground, no style clause. A binding lives on an
object, and the aggregate descriptors this project uses average over the whole frame — which is
exactly why they could not see it (`assessment_colour_object_dissociation.md` §3). The object must
fill the frame and have nothing to compete with.

**`LP` — the uncommon binding**
```
a single purple leaf centred on a plain light grey background, macro photograph, sharp focus, even studio lighting, no other objects
```

**`LG` — the prior, and the control that makes the whole study work**
```
a single green leaf centred on a plain light grey background, macro photograph, sharp focus, even studio lighting, no other objects
```

**`LN` — no colour named, to find out what the prior actually is**
```
a single leaf centred on a plain light grey background, macro photograph, sharp focus, even studio lighting, no other objects
```

**Filenames**: `LP_baseline_seed42_00001_.png`, `LG_baseline_seed42_00001_.png`,
`LN_baseline_seed42_00001_.png`, and so on. Folder: `benchmark_colour_binding\renders`.

### The gate, fixed now — read before looking at the images

| # | criterion | pass |
|---|---|---|
| **G1** | `LP` renders a leaf whose dominant hue is in the violet/purple band | **≥ 4 of 5 seeds** |
| **G2** | `LG` renders a leaf whose dominant hue is in the green band | **≥ 4 of 5 seeds** |
| **G3** | the `LP` and `LG` hue distributions do **not overlap** across the five seeds | no overlap |
| **G4** | a leaf is present and intact in all 15 | 15/15 |
| **—** | `LN` is descriptive: it records what the model's own prior is, and is not gated | — |

**If G1 fails, the study stops and that is the result.** Do not swap purple for a colour the model
finds easier until it passes — that is choosing the corpus to fit the hypothesis, which is the error
that made the headlight confirmation worthless. Report the failure and stop.

If G1 fails, one substitution is allowed **once**, declared in advance here: replace purple with
**blue**, re-run the same 15, and if blue also fails, stop for good.

## 3. Stage 2 — the sweep. 78 renders, only if Stage 1 passed.

Same settings, same seeds — **3 seeds only**: 42, 777, 1337.

| factor | levels | n |
|---|---|--:|
| prompt | `LP`, `LG` | 2 |
| block group | `Block_1` … `Block_6` | 6 |
| sign | `pos`, `neg` | 2 |
| dose | **0.050** | 1 |
| seed | 42, 777, 1337 | 3 |
| | **perturbed** | **72** |
| baselines | `LP`, `LG` × 3 seeds | **6** |
| | **total** | **78** |

Dose 0.050 and not 0.200: at 0.200 the image has already moved 83–101 % of the way to a different
seed (`assessment_per_block_dose_calibration.md` §3), and an object that has collapsed cannot show
a colour reversion. A second dose is added later if the first shows anything.

**Filenames**: `LP_Block_3pos_0.050_krea2_seed42_00001_.png`, matching the `benchmark_mappa`
convention exactly, so the existing analysis scripts read it without modification.

## 4. What will be measured, so that the renders are not wasted

Three outcomes, and only the first is what the study is looking for. The **`LG` control is what
separates them** — without it, "the purple went green" and "every hue rotated" are one measurement.

| outcome | `LP` | `LG` | reading |
|---|---|---|---|
| **reversion** | goes green | stays green | **the binding broke, the object survived** |
| generic rotation | shifts hue | shifts by the same amount | colour drift, not binding |
| object collapse | stops being a leaf | stops being a leaf | the object path was hit |

Per render: the hue of the object region against the two poles, plus an object-integrity measure so
that a collapse is never scored as a reversion. A block that produces reversion without collapse,
beside a block that produces collapse without reversion, **is** the watershed — and it is a
dissociation, which is what the outside literature says to look for instead of sensitivity
(arXiv 2608.03842, ρ = −0.72 to −0.88 between sensitivity and causality).

**The numeric predictions are frozen after Stage 1 passes and before Stage 2 is launched**, in a
pre-registration written then. They are not written now, because the pilot may show that the two
poles sit closer together than assumed and the thresholds have to be set from the measured
separation rather than guessed.

## 5. Standing constraints

- The analyst generates no render and requests none beyond this document.
- Nothing is written under `notebook/`.
- No claim status changes on this result.
- `python experiments/validate_notebook.py` at 0 errors before every commit; commit messages in
  Italian; everything entering the repository in English; **do not push**.
