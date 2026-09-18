# Scope — what this project is for

**Written 2026-09-18**, after the day that made the question answerable.

## The objective, in one sentence

> **Characterise what a small, structured, norm-matched edit to a trained diffusion backbone does to
> its output — precisely enough that the description can be stated without reference to the model it
> was measured on — and then test whether that description survives being rebuilt on an independently
> trained model.**

Three words in there are doing the work, and they are the difference between a research programme and
a collection of observations.

**Characterise**, not *validate*. A scope written as "validate whether X is true" invites looking for
X. This notebook's three most useful results — the colour signature that turned out to be subject
size, the style-direction hypothesis that failed, and the blinding that failed — all came from
measuring rather than confirming.

**Without reference to the model it was measured on.** This is the hard part and it is currently
unsolved. "The preset separates from both controls on PC1" cannot be tested on another model, because
PC1 is defined by this corpus. "A structured displacement runs strokes parallel where its sign-flipped
twin crosses them, while a sign-scrambled displacement of identical norm does neither" can be tested
anywhere. **Building the portable statement is itself a research goal**, not a write-up step.

**Rebuilt, not transferred.** See §3.

---

## 1. The ladder, and which rung we are standing on

"Is it an intrinsic property of diffusion models" collapses six different claims into one. They need
separating, because each needs its own evidence and you may only claim the rung you have tested.

| | rung | status |
| --- | --- | --- |
| 1 | This checkpoint, this sampler, this prompt register | **where all current evidence sits** |
| 2 | This checkpoint under ordinary multi-step sampling with CFG > 1 | **untested** — every render here is 9 steps at CFG 1.0 |
| 3 | Other checkpoints of the same family | untested |
| 4 | A different architecture *and* a different conditioning mechanism | designed, not run |
| 5 | Diffusion backbones in general | not reachable from one or two models |
| 6 | Deep networks with block structure, diffusion or not | the largest version, and testable outside diffusion |

Rung 4 is the first that deserves the word "cross-model", and reaching it does **not** license rung 5.
Two architectures is evidence against "an implementation detail of Krea-2". It is not evidence for
"a property of diffusion models" — that is a claim about a population, and n = 2 is not a population.

The honest form of the eventual headline is: *"this holds on two independently trained backbones that
differ in conditioning mechanism, hidden dimension and per-block capacity"* — and then let the reader
decide how far that generalises.

---

## 2. Why "intrinsic to diffusion models" is probably the wrong target

Not because it is too ambitious, but because it may name the wrong category.

What is being manipulated here is not diffusion-specific. Scaling a block's weights by α, and
permuting which block receives which profile, are operations on **a stack of transformer blocks**.
Nothing in them refers to denoising, to a noise schedule, or to a score function. If the finding is
that such operations produce coherent, direction-specific output change rather than degradation, then
the natural category is *trained deep networks with repeated block structure*, and diffusion is where
we happen to be able to see the result — because the output is an image and an image shows you
everything at once.

That possibility should stay open in the scope rather than be closed by the wording. It is also
**testable**, and more cheaply than a second diffusion model: the same norm-matched protocol on a
small language model, measuring output distribution shift instead of stroke morphology, would say
whether the phenomenon needs diffusion at all.

Conversely the finding might be narrower than diffusion — a property of *few-step distilled* models,
which is rung 2 and is the cheapest open question on the list.

**Both boundaries are unknown, and the scope should say so rather than pick one.**

---

## 3. What "cross-model" means here, and why the literature does not already answer it

Three neighbouring bodies of work, and the gap between them is where this project sits.

**`weights2weights` — Interpreting the Weight Space of Customized Diffusion Models** (Snap Research /
Berkeley). Establishes that the weight space of fine-tuned diffusion models behaves as a semantic
latent space: you can sample new models, edit attributes along linear directions, and invert an image
into weights. It is the closest published thing to "weight space has directions".

*Why it does not cover this.* It requires **a population of over 60,000 fine-tuned models** to build
the subspace, and all of it sits on one base model with LoRA variants. This project operates on **a
single checkpoint with nothing to difference against** — which is exactly the gap named in the
notebook's introduction, and it survives contact with that paper.

**THESEUS — Transporting Task Vectors across Different Architectures without Training.** Shows that
task-specific parameter updates transfer between architectures of different widths, via orthogonal
Procrustes alignment of representation spaces, and argues explicitly that *"task identity should be
defined by functional behavior rather than by parameter values"*.

*Why it matters, and why it is a different question.* A task vector is `fine-tuned − base`: it is a
learned direction, and moving it to another model is a mapping problem. **The edits here are not
vectors, they are recipes** — "scale blocks 5–9's attention by −0.045", "permute which block receives
which profile". A recipe is defined by *position in the architecture*, so on a new model it is
**re-instantiated natively**: nothing needs mapping, no Procrustes, no alignment data.

That makes the question strictly different from THESEUS's, and it makes the answer more interesting
either way. If the same recipe produces the same kind of effect on a model that shares no weights and
no training run with this one, the finding is about the **geometry that training reliably produces**,
not about a vector that happens to be portable.

And THESEUS supplies the right framing for §0's hard part: **define the thing functionally, not by
parameter values.** The cross-model test cannot be "does `preset.json` work on Anima" — the tensors do
not even have the same shapes. It has to be "does a structured displacement at matched norm produce
direction-specific output change that a sign-scrambled displacement at the same norm does not".

**Block-weighted merging and LoRA block weight** (supermerger, `sd-webui-lora-block-weight`, ComfyUI's
native merge nodes). Mature, widely used, and all of them need **at least two checkpoints** or an
adapter delta. None operates on a single checkpoint against itself. That gap was the project's
starting point and it is still open.

---

## 4. The second objective, which should be explicit rather than accidental

**Produce a usable protocol for evaluating generative-model edits without fooling yourself.**

This is not a consolation prize. As of today the notebook carries 38 documented measurement pitfalls,
nine non-negotiable rules, pre-registration with frozen hashes, and — as of this afternoon — a
**measured** blinding: a four-way forced choice showing the scorer identifying conditions at 85% and
60% against a 25% chance level, *after* randomised mirroring, hue rotation, saturation jitter and
noise.

Almost nothing in the generative-model evaluation literature does that. The field routinely reports
human preference studies with no discrimination check at all. If the scientific finding turns out
modest, **the protocol is the contribution**, and it is worth writing as such rather than leaving it
scattered across an errors log.

---

## 5. What would end the programme

Stated in advance, so that it is recognisable if it happens.

* **Rung 2 fails.** If the effects vanish under ordinary multi-step sampling with CFG > 1, this is a
  finding about few-step distilled models. Narrow, still real, and the notebook would say so.
* **The structure→effect map is model-specific.** If the same recipe produces a *different kind* of
  effect on each model, then a preset is not an instrument — it is a per-model hand calibration, which
  is what block-merging practitioners already do by eye. The practical value of the whole tuner idea
  rests on this one not happening.
* **The controls stop separating.** If a sign-scrambled displacement at matched norm ever starts
  producing the same effects as a structured one, the central "structure, not magnitude" argument
  collapses — and note that §7.2's enlargement result is currently missing exactly that control.
* **Nothing survives a measured blinding.** Today showed the blinding failing and the effect surviving
  anyway. If a future round shows effects that exist only where the scorer can identify the condition,
  the honest conclusion is that this was an elaborate way of measuring an expectation.

---

## 6. What this changes about the order of work

The scope above reorders the roadmap by one principle: **each step should buy a rung, or buy the
ability to state the claim portably.** Work that does neither waits.

1. **Get the human out of the measuring loop.** Not a rung — a precondition. Every claim currently
   passes through one pair of eyes, and today measured how leaky that is. 480 hand-drawn boxes with
   known conditions now exist as a validation set for an automatic detector.
2. **The missing sign-scrambled control on the enlargement.** Buys the portable statement: without it,
   §7.2 separates two structured edits and says nothing about structure versus magnitude, which is the
   part that has to travel to another model.
3. **Rung 2 — the sampling regime.** The cheapest rung on the ladder and the one most likely to
   invalidate everything above it. It should not stay untested while rung 4 is being prepared.
4. **Rung 4 — Anima.** Only after 2 and 3, because a negative result with the sampling regime and the
   structure control both open would be uninterpretable: three explanations, no way to choose.
5. **Rung 6, as a cheap side probe.** The same norm-matched protocol on a small language model. If a
   structured block edit produces coherent, direction-specific behavioural change there too, the
   category is not "diffusion models" and the scope should be rewritten upward.
