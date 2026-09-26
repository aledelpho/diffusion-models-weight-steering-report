# Prior work — is the question already answered?

- **Written:** 2026-09-26, from a web search made before spending 624 renders on the next atlas.
- **Caveat on provenance:** the analyst's own knowledge ends in May 2026. Everything below was read
  from the sources at the time of writing, not recalled; the 2026 arXiv entry in particular is
  known only through that fetch and has not been independently verified.

---

## 1. Depth specialisation in diffusion transformers — reported, and it agrees with this project

**AnyStyle** (arXiv 2607.04677) applies its style LoRA **exclusively to FLUX's later single-stream
blocks (11–38)**, on the **query, key, value and output projections of self-attention**, and states
that early blocks (1–10) encode low-level structural detail while later blocks encode higher-level
semantic and stylistic attributes.

That is the same shape as this project's own weight-space results, arrived at independently:

| this project | prior work |
|---|---|
| `cost-grows-with-depth`, r = −0.659 against block index | early = structure, late = style |
| `tail-is-rectified`, 9.1× asymmetry on block 26 | style edits are placed in the tail |
| atlas recognisability: `late_attn_d1` 95.8 %, `late_mlp_d2` 91.7 %, middle bands at chance | style LoRA restricted to late blocks |

So the depth finding is **not new**, and that is good news: it is a replication in a different
medium. The literature works in activation space or by training a LoRA; this project makes a static
50 KB weight edit at matched displacement. Agreement across two such different instruments is worth
more than either alone.

## 2. The within-block axis is finer than the one tested here, and the field points at it

AnyStyle's ablation reports that **modulating the query tensor alone outperforms key, or query and
key together**, and reads queries as carrying layout and objects while key and value leak style.
A review of the area (Lacuna, *Functional Specialization in Diffusion Transformer Layers*) collects
the same distinction from video work: Q and K sensitive to subject identity, V to motion, citing
Δ-DiT, FADE and DualReal.

**The atlas collapses all of this into one `attn` group of seven tensors per block.** The tuner does
not: `MODEL_SURGEON_MAP` exposes `ATTN_wq_query`, `ATTN_wk_key`, `ATTN_wv_value`, `ATTN_wo_out`,
`ATTN_gate_attn` and `ATTN_qknorm_scales` as separate controls, each already a widget.

## 3. The channel hypothesis runs against the grain, and cheaply

*Unpacking SDXL Turbo* (arXiv 2410.22366) trains sparse autoencoders on the transformer blocks of a
text-to-image model and finds clean per-block roles — `down.2.1` composition, `up.0.0` local detail,
`up.0.1` colour and texture, `mid.0` abstract. The relevant part for this project is **why the method
is built the way it is**: the dictionary is **overcomplete, 5120 features for 768 dimensions, a
6.67× expansion**, because features sit in superposition and are **not aligned with individual
channels**. If they were, no dictionary would be needed.

So a partition of the residual stream into 12 bands of raw channels — and the tuner's bands are cut
by **static L2 energy of the weights**, which is not even a functional criterion — is unlikely to
isolate anything the literature would call a feature. The plan in
`docs/RUNBOOK_signed_atlas_plan.md` §6 already flagged energy as a proxy; this makes the case
stronger. **It does not refute the observer's hypothesis** that functions are distributed along
depth — that part is supported. It refutes the idea that the raw channel basis is where the
distributed thing becomes localised.

## 4. What is genuinely still open

**TIDE** (arXiv 2503.07050) trains a dedicated sparse autoencoder on each of PixArt-XL's **28
layers** — the same depth as Krea-2 — and, on reading, reports feature hierarchies and a strong
**timestep** dependence, but **no analysis of how the layers differ from one another**. The obvious
systematic map of a monolithic DiT by depth × component is not in these sources.

Two gaps follow, and both are reachable with this project's instruments:

1. **Depth × sub-component in weight space.** Not `attn` against `mlp`, but `wq` against `wk`
   against `wv` against `wo`, per band. The literature's claim is specific — query alone beats
   query+key — and it has not been tested by a static weight edit at matched displacement.
2. **Timestep.** A weight edit is static, but its *effect* need not be: TIDE's central result is that
   representations change substantially between low and high t. Nothing in this project has ever
   varied the number of steps or measured where in the denoising trajectory an edit does its work.
   The sampler has been fixed at 9 steps in every single run.

## 5. Recommendation

The next atlas should be **q / k / v / o × band × sign**, not channels. It is where the literature
points, where this project's own recognisability numbers point (late attention), and where the tool
already has the widgets. The channel atlas should wait for a functional partition, not an energy one.

## Sources

- AnyStyle: A Single LoRA is Sufficient for Image-Guided Style Transfer — https://arxiv.org/html/2607.04677
- Unpacking SDXL Turbo: Interpreting Text-to-Image Models with Sparse Autoencoders — https://arxiv.org/html/2410.22366v2
- TIDE: Temporal-Aware Sparse Autoencoders for Interpretable Diffusion Transformers — https://arxiv.org/html/2503.07050
- Functional Specialization in Diffusion Transformer Layers (review) — https://lacuna.tiptreesystems.com/direction/functional-specialization-in-diffusion-transformer-layers/txn_d9b465102c724ad5a6148d6625169394
