# Render spec — one parameter family at a time (C35), with the matching rule frozen (C36)

- **For:** Alessandro, who launches every render; prepared for Antigravity to queue.
- **Two stages.** A **12-render gate** that can end the whole thing, then **≤ 144** renders.
- **Origin:** [`parameter_families.md`](parameter_families.md). No bench in this project has ever
  moved anything smaller than a block.

---

## 1. Why, in three sentences

The checkpoint holds 430 tensors in six functional kinds. **99.98 % of the parameters are 2-D
linear projections**, and every bench this project has run moves those. The other five kinds —
normalisation gains, q/k normalisation, modulation, biases, the latent interface — are **39 % of
the tensors and 0.018 % of the parameters**, and a scalar gain means something different on each of
them.

## 2. C36 — the matching rule, frozen here, before any data

Scaling every block normalisation gain by 10 % is a relative Frobenius displacement of
**5.3 × 10⁻⁴**, against **0.05** for a standard edit — a factor of one hundred. **Matched-displacement
controls are impossible between these families**, which is why the rule has to be written down now
and not chosen later (pitfall 68: this project has already picked a null after seeing the data
once).

> **The matched quantity is the relative gain δ, and nothing else.** Every family is driven by the
> same multiplier **1 + δ** applied identically to every tensor in it, and every family is run on
> the same δ ladder. **Frobenius displacement is recorded as an observed covariate and is explicitly
> not controlled** — it cannot be. Comparison between families is by the **shape of the δ → effect
> curve**, never by a single δ, and never by displacement.

## 3. Stage 1 — the gate, 12 renders

**Can the tool move this family at all?** Six families, δ = **+1.00** (multiplier ×2.0) for every
one of them, two prompts (`P01`, `P02`), one seed (42). Baselines exist in `benchmark_mappa`.

| id | family | kind | tensor keys | tensors | params |
|---|---|---|---|--:|--:|
| `F_wo` | attention output | 1 | `blocks.{0..27}.attn.wo.weight` | 28 | 1 056 964 608 |
| `F_mod` | modulation | 3 | `blocks.{0..27}.mod.lin` | 28 | 1 032 192 |
| `F_io` | latent interface | 5 | `first.weight`, `last.linear.weight` | 2 | 786 432 |
| `F_norms` | block norm gains | 2a | `blocks.{0..27}.{pre,post}norm.scale` | 56 | 344 064 |
| `F_qknorm` | q/k normalisation | 2b | `blocks.{0..27}.attn.qknorm.{q,k}norm.scale` | 56 | 7 168 |
| `F_proj` | the 12-parameter router | 6 | `txtfusion.projector.weight` | 1 | **12** |

**The gate criterion is a decoded-pixel hash**, not a statistic: a family passes if any of its two
renders differs from its baseline in pixel content. File bytes always differ — each PNG embeds its
own workflow — so **compare `numpy` arrays, never file hashes** (that mistake was made and caught
on 2026-09-28).

| # | prediction | confirmed if | falsified if |
|---|---|---|---|
| **G1** | `F_wo` moves | pixels differ on both prompts | identical — **stop, the pipeline is broken** |
| **G2** | `F_norms` does **not** move | pixel-identical on both | it moves — then `atlas_vs_tuner_generator.md` and its replication are both wrong, and that is the finding |
| **G3** | `F_qknorm`, `F_mod`, `F_io`, `F_proj` | recorded, **no prediction** | — |

**Read G1 and G2 first.** A family that comes back pixel-identical is not testable with this tool,
drops out of stage 2, and **that is its result**: it is a statement about the tuner, not the model
(pitfall 86's neighbourhood — a clean null from a tool that could not apply the patch).

## 4. Stage 2 — the ladder, ≤ 144 renders

Only the families that passed the gate, plus `F_wo` as the kind-1 reference whatever happens.

**δ ∈ {−1.00, −0.50, −0.10, +0.10, +0.50, +1.00}** · prompts `P01`, `P02` · seeds 42, 777, 1337.
**36 renders per family**, at most four families.

## 5. Predictions, frozen

| # | prediction | confirmed if | falsified if |
|---|---|---|---|
| **P1** | a family that moves does so **monotonically in \|δ\|** | the effect is ordered across 0.10, 0.50, 1.00 on both arms | any inversion larger than the baseline-to-baseline floor |
| **P2** | `F_qknorm` acts on **structure, not palette** — scaling q and k by 1+δ multiplies every attention logit by (1+δ)², a temperature change | \|Δ coherence\| / \|Δ chroma\| > 1 at δ = ±0.50 | < 0.5 at both signs |
| **P3** | **displacement is the wrong currency**: at equal δ, at least one family below 1 % of `F_wo`'s parameter mass produces an effect within a factor of **3** of `F_wo` | any small family reaches ⅓ of `F_wo`'s effect at the same δ | every small family stays below a tenth of `F_wo` at every δ |
| **P4** | `F_proj` (12 parameters) does either **nothing or something large** — not something small | its effect at δ = ±1.00 is below the seed floor, or above half of `F_wo`'s | it lands in between at both signs |
| **P5** | the sign asymmetry of `F_qknorm` exceeds that of `F_wo` — (1+δ)² is not symmetric in δ while a linear gain is | \|effect(+δ) − effect(−δ)\| larger for `F_qknorm` at δ = 0.50 | equal or smaller |

**P3 is the experiment.** P1, P2, P4 and P5 describe what each family does; P3 asks whether the
currency this project has been paying in — Frobenius displacement — buys anything at all outside
kind 1. If P3 falls, the block abstraction is vindicated and the small families are a curiosity. If
it holds, **every matched-displacement control in the notebook is a control over 99.98 % of the
mass and blind to the rest**, and that is a scope statement the whole project inherits.

## 6. How it is driven — preset JSON, not the 34-slot vector

The `vectors_override` addresses **block groups**. A family is not a block group, so these need
**preset files**, one per family per δ, loaded with `ArthemyKrea2PresetLoader` at
`strength_model = 1.0` after `ArthemyKrea2ResetPatcher`. `Real Value` semantics are
**multiplier = 1.0 + δ** (`Arthemy_Krea2_Tuner.py` line 1511), so the JSON carries δ directly.

Schema, copied from a working preset (`Arthemy_QKVO_wo_b6_neg.json`) — every field is required:

```json
{
  "name": "Family_qknorm_d+0.500",
  "author": "Antigravity (C35)",
  "created_at": "2026-09-28 ...",
  "version": "2.1",
  "suite_rotation_effective": true,
  "stats": { "model_patched_layers": 56, "model_granular_layers": 0,
             "clip_patched_layers": 0, "clip_granular_layers": 0,
             "chaos_recipes_count": 0, "rotation_recipes_count": 0,
             "chaos_rotation_recipes_count": 0, "channel_recipes_count": 0,
             "five_d_recipes_count": 0, "excluded_lora_tensors": 0 },
  "model_patches": { "blocks.0.attn.qknorm.qnorm.scale": 0.5, "...": 0.5 },
  "model_granular_patches": {}, "clip_patches": {}, "clip_granular_patches": {},
  "chaos_recipes": [], "rotation_recipes": [], "chaos_rotation_recipes": [],
  "channel_recipes": [], "five_d_recipes": []
}
```

**Every key must be spelled exactly as the checkpoint spells it.** The authority is
`docs/model_structures/krea2_turbo_bf16_details.json` — generate the key lists from that file, never
by hand. `stats.model_patched_layers` must equal the number of entries in `model_patches`.

## 7. Two checks that are not optional

Both come from failures paid for on 2026-09-28.

1. **Capture the tuner's logger output** for every render and keep it beside the renders. The node
   already warns when it skips a patch — `"[Arthemy Channel Scale] '<key>' ... this patch was
   skipped"` and `warn_if_quantized_skipped` — and nothing in this project has ever read it. A
   family whose patch was skipped and a family the model ignores produce the same image and are
   opposite findings. **This is the bench that cannot tell them apart without the log.**
2. **Read back `model_patched_layers` from the Preset Loader** and compare it with the count in the
   JSON. `Loaded Preset '...' | Model: N scalar layers` — if N ≠ the JSON's count, the keys did not
   resolve and the render is void.

## 8. Standing constraints

- The analyst generates no render and requests none beyond this document.
- Repository content in English; commit messages in Italian; small descriptive commits.
- Validator at **0 errors** before every commit. Every published number from a file in `data/`.
- Nothing written under `notebook/`. No claim changes status. **Do not push.**
- **Nothing in this project may shut down or close the machine**, and no watchdog may do it either.
