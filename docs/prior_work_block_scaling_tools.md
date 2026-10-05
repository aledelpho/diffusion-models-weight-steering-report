# Prior art — two ComfyUI tools that already scale single blocks, and what they cost this project's novelty claim

**2026-10-05.** Written after Alessandro pointed at `cubiq/Block_Patcher_ComfyUI` and the
`FluxBlocksBuster` node. Read from source, not from the project pages that describe them: the
summaries on node-index sites were treated as untrusted, and every mechanical statement below was
checked against the code, including ComfyUI's own `add_patches` / `calculate_weight` in the copy
installed on Alessandro's machine (`comfy/model_patcher.py`, `comfy/lora.py`).

**Why this document exists.** Pitfall 87: search before claiming novelty. This project has been
describing its edit as something the literature does not do. For the *mechanism*, that is now
false, and two published claims in the repository had to be corrected (§5).

---

## 1. What the two tools are

| | `FluxBlocksBuster+` | `Block_Patcher_ComfyUI` |
|---|---|---|
| where | node in `cubiq/ComfyUI_essentials`, file `conditioning.py` | standalone repo `cubiq/Block_Patcher_ComfyUI` |
| kind | a **model node**: model in, patched model out | a **sampler**: renders one image per line and plots the value on it |
| input | one multiline box, `## i = v` for the 19 double blocks, `# i = v` for the 38 single blocks, all 1.0 by default | one `regex=weight` per line, iterated |
| author's framing | — | "(very) advanced and (very) experimental … change the blocks weights of Flux models and check the difference each value makes" |
| model | Flux only ("Support other models than Flux" is still an open TODO) | Flux only |

Both are by the same author. `ComfyUI_essentials` has been in "maintenance only" mode since
2025-04-14 by its own README.

**Dates, from the git history** (both repositories cloned on 2026-10-05):

| | first commit | last commit |
|---|---|---|
| `FluxBlocksBuster` (first appearance in `ComfyUI_essentials`, `git log -S`) | **2024-09-07** (`b581fab`) | — |
| `Block_Patcher_ComfyUI` | **2024-09-20** (`508b893`) | 2024-09-22 |
| Arthemy Live Model & CLIP Tuner, Civitai article 25091 (Alessandro) | **2026-01-18** | — |

So cubiq's two tools precede the Arthemy tuner by about sixteen months.

**Independent development.** Alessandro reports (personal communication with the author, Matt3o /
cubiq, October 2026) that neither knew of the other's work: the two tools and the Arthemy tuner
were arrived at independently. This is recorded as stated; a reader cannot verify it from the
repository. It changes the attribution — convergence, not derivation — and not the priority, which
is a matter of publication date. They are Flux-only; the
Arthemy tuner was first published for SDXL, Illustrious and NAI (U-Net, with named functional
areas and a CLIP tuner), and later ported to Krea-2. Whether an equivalent base-weight block scaler
for SDXL U-Nets existed before January 2026 has not been checked.

## 2. The mechanism is the same as ours — verified line by line

`FluxBlocksBuster`, for every state-dict key matching the block's regex:

```python
if value != 1.0 and re.search(block, k):
    m.add_patches({k: (None,)}, 0.0, value)
```

`Block_Patcher_ComfyUI` uses the identical call on the keys its regex matches.

In the installed ComfyUI, `add_patches(patches, strength_patch, strength_model)` stores
`(strength_patch, payload, strength_model, …)`, and `comfy/lora.py:calculate_weight` does:

```python
if strength_model != 1.0:
    weight *= strength_model          # line 471-472
...
if patch_type == "diff":
    ...
    if strength != 0.0:               # line 500 — false here, so the None payload is never read
```

So `add_patches({k: (None,)}, 0.0, value)` is exactly **`W := W × value`**, and the `None` is a
placeholder that is never dereferenced because `strength_patch` is 0.

**The Arthemy Krea-2 tuner does the same thing by the same route.** `Arthemy_Krea2_Tuner.py`:
`soft_target_weight(delta, "Real Value")` returns `1.0 + delta` (line 1510-1511); the patch is built
as a scalar `(1.0 + strength,)` (line 2172) and committed as
`_commit(formatted, s_patch=0.0, s_model=scalar_mult)` (line 1329) — the same ComfyUI call, with a
2-byte dummy tensor in place of cubiq's `None`.

**Conclusion: the edit this project studies is not a new operation.** Per-block multiplicative
scaling of base weights, training-free, through `add_patches`, was publicly available for Flux
before this project started.

## 3. Where the tools differ from each other and from ours

- **Which tensors.** `FluxBlocksBuster` targets, per block,
  `(img|txt)_(mod|attn|mlp)\.(lin|qkv|proj|0|2)\.(weight|bias)` for double blocks and
  `(linear[12]|modulation\.lin)\.(weight|bias)` for single blocks — so it scales **modulation
  layers and biases** as well, and leaves the layer norms alone. Krea-2 has **no biases in its
  blocks** (13 tensors per block: 8 2-D weights, 4 norm scales, 1 modulation —
  `docs/model_structures/krea2_turbo_bf16_details.json`), so that part of the difference is
  architecture, not intent. On Krea-2 the modulation family was measured inert
  (`parameter_families_first_result.md`); on Flux it is inside cubiq's regex and presumably is not.
- **Granularity.** `Block_Patcher_ComfyUI`'s regex is **finer than our 34-slot vector**: it can
  address `img_` against `txt_`, `attn` against `mlp`, one tensor at a time. Our tuner reaches that
  granularity only through `granular_json` / the Surgeon node, which this project has not used.
- **Sweeping.** `Block_Patcher_ComfyUI` iterates the list, renders one image per line and prints the
  parameters onto the images with a `Plot Block Params` node. That is, in substance, the
  single-block atlas of [notebook page 12](../notebook/12-single-blocks.md) — as a tool, built two
  years earlier, for a different model.
- **What is claimed.** Neither tool publishes a finding. There is no map, no dose calibration, no
  measurement, no claim about what any block does; the README's own instruction is to experiment at
  a fixed seed and look. `FluxBlocksBuster`'s index page states the same: "deliberately a probing
  tool, not a preset system."

## 4. What this leaves as this project's own

The mechanism is not ours. What is not in either tool, and is what the report should claim:

1. **A measured per-block map** of one model, from ~5,000 renders, with doses calibrated per block
   and a sensitivity map of where artefacts start (notebook page 12, results page 21).
2. **Pre-registered confirmation** of specific claims — the saturation knob (results page 22),
   presets coherent inside a prompt family (page 23), robustness to how the prompt is written
   (page 24) — each with its decision rule and scoring code committed before the renders, a
   pixel-identical reproduction check, and an eye pass deposited before the numbers.
3. **The negative results and retractions** (results page 26, notebook page 13), including three
   kinds of parameter that the tool reports as patched and that never reach the model.
4. **A different architecture**: Krea-2's 28 single-stream blocks against Flux's 19 double + 38
   single.

Stated plainly: **we did not invent the knob; we measured one.** That is a smaller claim than the
repository was making, and a safer one.

## 5. Corrections made to published text (2026-10-05)

- `results/README.md`, related work: the sentence "The difference here is that the base weights
  themselves are scaled: nothing is learned, and the knob is a block, not a learned direction" was
  the differentiator against Concept Sliders / weights2weights / LoRA Block Weight. It does not
  separate this work from cubiq's tools, which scale base weights per block. Rewritten, and both
  tools added as references [17] and [18].
- `notebook/STORY.md`, opening: "Static per-tensor edits like these have barely been studied. The
  nearest prior work trains LoRAs or steers activations" — false as written. Rewritten.

## 6. What this audit did not do

- It did not run either tool: neither is installed here, and Flux is not on this machine. Every
  statement above is about source code, not behaviour observed.
- It did not search for other tools of the same kind. `sd-webui-lora-block-weight` (reference 8)
  weights a *LoRA* per block and is a different operation; whether an equivalent base-weight block
  scaler exists for SD1.5/SDXL was not checked, and probably should be before publication.
