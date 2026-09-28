# How many kinds of thing are in this model, and which of them a gain cannot address

**Date**: 2026-09-28 · **Question**: Alessandro — *"how many families of elements are there inside
a model? Maybe we are thinking too broadly, and there are simply structures that should not be
touched."* · **Material**: `docs/model_structures/krea2_turbo_bf16_details.json`, the checkpoint's
own tensor listing · **No render, no measurement** — this is arithmetic on the inventory.

**Novelty check** (per the rule drafted the same day): grepped `docs/`, `notebook/` and
`experiments/` for `qknorm`, `first.weight`, `last.linear`, `projector` in both languages.
`krea2_architecture_decomposition.md` maps the architecture and proposes five *subdivision
strategies for control*; `atlas_vs_tuner_generator.md` notes in passing that "14 of 49 tensors are
`qknorm` scales" inside the atlas's `*_attn` conditions; `prior_work_layer_specialisation.md` notes
that `ATTN_qknorm_scales` is already a widget. **Nothing asks which families a scalar gain is a
meaningful operation on, and no bench has ever moved one of the small families alone.**

---

## 1. Fifty-five families by name, six by kind

430 tensors, 12 820 073 036 parameters, 55 distinct name patterns. Grouped by what the tensor *is*:

| functional kind | tensors | parameters | share |
|---|--:|--:|--:|
| **1 — 2-D linear projections** (attn `wq/wk/wv/wo/gate`, mlp `up/gate/down`, `tproj`, `tmlp`, `txtmlp`, txtfusion) | 261 | 12 817 793 024 | **99.9822 %** |
| 2a — normalisation gains (`prenorm.scale`, `postnorm.scale`, `last.norm.scale`, …) | 66 | 373 248 | 0.0029 % |
| 2b — **q/k normalisation** (`attn.qknorm.{q,k}norm.scale`) | 64 | 8 192 | 0.0001 % |
| 3 — modulation / conditioning (`mod.lin`, `last.modulation.lin`) | 29 | 1 044 480 | 0.0081 % |
| 4 — biases | 7 | 67 648 | 0.0005 % |
| 5 — the latent interface (`first.weight` 6144×64, `last.linear.weight` 64×6144) | 2 | 786 432 | 0.0061 % |
| 6 — a 12-parameter router (`txtfusion.projector.weight`, shape [1, 12]) | 1 | 12 | 0.0000 % |

**By mass the model is one kind of thing.** By count it is not: **169 of 430 tensors — 39 % — are
not linear projections**, and together they hold **0.0178 %** of the parameters.

## 2. Where a gain stops being a gain

Multiplying a 2-D weight matrix by α is a well-defined operation: it scales a linear map. For the
other kinds it is a different operation each time, and two are worth naming.

**`qknorm` is a temperature control, not a gain.** Queries and keys are normalised and rescaled by
their own learned vectors before the dot product. Scaling *both* by α multiplies every attention
logit by **α²** — which sharpens or flattens the softmax across the whole model. It is not a
perturbation of what attention computes; it is a change of how decisive attention is.
**8 192 parameters**, 0.000064 % of the model, 64 tensors.

**The latent interface is a global gain.** `first.weight` (6144 × 64) and `last.linear.weight`
(64 × 6144) are the only points where the 64-channel latent meets the 6144-channel feature stream.
Scaling either multiplies the whole image's signal, at 786 432 parameters.

**And a twelve-parameter tensor.** `txtfusion.projector.weight` has shape [1, 12]. Whatever it
decides, it decides with twelve numbers, and "a small edit" is not a meaningful category there.

## 3. The consequence that matters most: matched displacement cannot see five kinds out of six

This project's central control is **matched Frobenius displacement** — comparing a structured edit
against a scramble that moves the weights exactly as far. The standard working edit is
D ≈ 0.05.

Scale **every** normalisation gain in all 28 blocks by 10 %:

> 364 544 parameters, 0.00284 % of the model. **Relative Frobenius displacement ≈ 5.3 × 10⁻⁴** —
> about **one hundredth** of a standard edit.

For `qknorm` alone it is 8 192 parameters and the displacement is a further order down.

**So a temperature change and a 5 % scale on the MLPs cannot be put on the same axis.** They differ
by two orders of magnitude in displacement and by an unknown amount in effect. Every conclusion this
project has drawn of the form *"at matched displacement, X beats Y"* is a conclusion about **kind 1
only** — which is 99.98 % of the mass and 61 % of the tensors, and is not the whole model.

That is not a retraction: those conclusions were drawn on benches that move kind-1 tensors, and they
stand for what they measured. It is a statement of scope that nothing in the notebook currently
carries.

## 4. What this says about "is the price always noise?"

The block abstraction the tuner exposes applies **one α to kinds 1, 2, 3 and 4 at once**. A "block"
is not a homogeneous object: it is eight 2-D matrices plus two normalisation vectors plus a
modulation vector, and the same α means four different things across them.

That is a concrete mechanism for damage that is neither "the model is fragile" nor "the tool injects
noise": **a single gain is being applied across families where it is four different operations.**
Two facts already in the repository fit it, and neither was read this way:

* the four **dead arms** — `MOD`, `NORMS`, `clipLULT`, `CLIP:Final_Projection` — are exactly kinds
  2 and 3, where the gain does nothing at all;
* at matched displacement a random sign-flip moves the image **1.68×** more than coherent scaling,
  read at the time as downstream normalisations cancelling the coherent component. Kinds 2a and 2b
  *are* those normalisations, and they are the part no edit has ever moved on purpose.

It also fits the observation that prompted this: `B4_mask` (2 blocks) holds the line better than
`Block_4` (5 blocks) on the positive arm — 1.0166 against 0.9785 — while on the negative arm the
order reverses (0.9722 against 1.0016). **Breadth is not the variable**: mean coherence by number of
blocks touched runs 0.990 (1 block), 0.938 (2), 0.909 (4), **0.998 (5)**. Which blocks, and which
families inside them, is what moves.

## 5. The experiment this earns

**Move one family at a time.** Never done: no bench in this project has ever isolated a family
smaller than a block. The candidates, in order of leverage per parameter:

1. **`qknorm` alone**, ± a range of α, all 28 blocks. 8 192 parameters. If attention temperature is
   a usable axis it is the cheapest control in the model by four orders of magnitude, and it has
   been riding inside every `*_attn` atlas condition unexamined.
2. **`first` / `last` alone** — the latent interface, 786 432 parameters.
3. **`mod.lin` alone at a large α** — declared a dead arm at the gains tried; a dead arm is only
   dead at the amplitude tested.
4. **kind 1 with kinds 2–4 held fixed**, which is what a "block" edit has never been.

**The design note that makes it hard, and must be written into the pre-registration:** these
families *cannot be Frobenius-matched* to a kind-1 edit, because their displacement is ~100× smaller
at any reasonable α. The matching has to be on something else — equal effect size on a declared
statistic, or a per-family relative scale — and choosing that rule **after** seeing the data is
pitfall 68, which this project has already paid for once.

Register items **C35** (family isolation bench) and **C36** (a matching rule for families that
displacement cannot compare).

## 6. Limits

This is the checkpoint's inventory and the architecture's semantics, not a measurement. Which
families *matter* is exactly what §5 proposes to find out; nothing here shows that `qknorm` does
anything. The kind assignment is mine, from tensor names and shapes, and a name is not a proof of
function — `mod.lin` at 36 864 × 1 is a strong hint but not a reading of the forward pass.
