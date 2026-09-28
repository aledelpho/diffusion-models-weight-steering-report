# Withdrawn as a finding — this was already known, and better

> **Correction, same day, 2026-09-28 (later).** The withdrawal below stands: this *was* already
> known, and [`atlas_vs_tuner_generator.md`](atlas_vs_tuner_generator.md) says it better. But one of
> its arguments was wrong. It dismissed the proposed mechanism because *"the Preset Loader reports
> 84/84 matched"*. `benchmark_parameter_families` shows that counter is worthless: the loader prints
> `n_model_matched`, which the source increments when a key resolves and `add_patches` is called —
> **it counts registration, not effect**. At a multiplier of 2.0, three families patching disjoint
> 1-D tensor sets produce pixel-identical renders while the loader reports 56, 56 and 28 layers
> matched. See [`parameter_families_first_result.md`](parameter_families_first_result.md) §3. The
> mechanism is still unsettled; it is no longer refuted by that argument.

**Date**: 2026-09-28 · **Status**: **rewritten the same day, after Alessandro asked "had we not
already noticed this?"** The answer is yes.

---

## 1. What this document claimed, and why it should not have

Verifying Antigravity's re-reading of `benchmark_qkvo_atlas`, the `normscales_all_pos` and
`normscales_all_neg` conditions returned exactly 1.0000 on every measured quantity. I checked the
preset (56 layers at `prenorm.scale` / `postnorm.scale` = 0.1), compared decoded pixels against the
baselines (**18 of 18 identical, maximum difference 0**), and wrote it up as a new finding with a
proposed mechanism.

**It is in the repository since 2026-09-26**, in
[`atlas_vs_tuner_generator.md`](atlas_vs_tuner_generator.md), whose own commit message ends
*"NORMS_block_scales e' ancora esposto in interfaccia"*. That document establishes more than this
one did:

* the same effect on a different corpus — 84 parameters (`mod.lin`, `prenorm.scale`,
  `postnorm.scale`, all 28 blocks) rescaled by `model_alpha = 0.9365`, render **byte-identical to
  the baseline on all eight prompts**. *"Not small: zero."*
* the tuner's own source comment, which documents `mod.lin` as **already known to be inert** and
  records that the control was removed from the node for exactly this symptom;
* that the removal's stated diagnosis is wrong — the keys do exist in the checkpoint;
* that **the displacement accounting of the whole project is unaffected**, which is the question
  that actually mattered and which I never asked;
* two candidate mechanisms, and a decisive test that separates them.

## 2. And my proposed mechanism is probably wrong

I suggested the channel-scale adapter's `weight.ndim < 2` guard silently skips 1-D norm tensors.
The earlier document has the Preset Loader's own report:

> `Loaded Preset 'Arthemy_Atlas_modulation_norm_draw1' | Model: 84 scalar layers, 0 granular
> layers (x1.00)`

**84 of 84 matched; nothing was skipped.** The scalar patch path is not the channel-scale adapter I
read, so the guard I quoted is not the code that runs here. The two live hypotheses remain the ones
already written down on 26/09:

1. **the forward pass does not read these parameters** — a non-affine norm taking its whole scale
   from the modulation path would leave `prenorm.scale` in the checkpoint as an unused weight;
2. **ComfyUI never materialises a scalar patch on a parameter not named `.weight`** — registered by
   `add_patches`, hence the count of 84, but never walked by `calculate_weight`.

The decisive test was specified there and **has never been run**: bake the patched model with the
tuner's own Saver, which materialises every patched weight, and compare the baked
`blocks.0.prenorm.scale` against the original checkpoint. Different → hypothesis 1, and *these
parameters are inert to rescaling*, which is a real statement about the architecture. Identical →
hypothesis 2, and it is a tool limitation the tuner should refuse rather than report as 84 patched
layers. **It is now register item C34**, where it should have been put two days ago.

## 3. What survives from this document

Two things, and they are replication and arithmetic, not discovery.

* **A second corpus.** The 26/09 result is on the atlas's `modulation_norm` conditions, 8 prompts.
  This is the q/k/v/o bench's `normscales` conditions: **18 of 18 renders checked have pixel content
  identical to their baseline, maximum absolute difference 0**, across three styles, three seeds and
  both arms. Same phenomenon, second corpus, independent measurement.
* **A count.** 48 renders of `benchmark_qkvo_atlas` (2 conditions × 8 styles × 3 seeds) are
  duplicates of baselines that exist in `benchmark_atlas_phase1`.

The operational consequences are unchanged and worth keeping: **"no effect" from this tuner is not
evidence of no effect until the patch is shown to have reached the weights**, and the tuner's own
warnings go to a log no bench script captures (register **C33**).

## 4. The process failure, which is the part worth keeping

**This is the third time in one day that I re-derived something already in this repository.** The
sign decomposition on pixels had been retracted a week earlier; the specialisation table had been
demolished on 23/09; and this. Pitfall candidate 73 says a novelty check run in one language is not
a novelty check — but here **the check was not run at all**. I ran it only when asked, and the very
first grep returned the right document as its first hit. Writing took an hour; the check took
eleven seconds.

Drafted defect **87**: *a novelty check performed after publication is not a novelty check.* The
rule it earns is narrow and mechanical, which is the only kind that survives:

> **Before writing any document that reports a finding, grep `docs/` and `notebook/` for the
> phenomenon's key terms in both English and Italian, and record in the document what the search
> returned — including "nothing".** A stated negative is auditable; an unstated one is an
> assumption.

Defect **86** as originally drafted is withdrawn along with the finding: the phenomenon is real, it
is simply not new, and its correct entry is the one already in `errors_log.md`'s neighbourhood via
`atlas_vs_tuner_generator.md`.

**Credit unchanged:** Antigravity put the zero in its table instead of smoothing it away, which is
what made the check possible at all.
