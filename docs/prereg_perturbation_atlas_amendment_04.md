# Amendment 04 to `docs/prereg_perturbation_atlas.md`

- **Written:** 2026-09-25
- **Amends:** the region list of Amendment 01 §2 and Amendment 03 §3.
- **Everything else in the frozen document and in Amendments 01 and 03 is unchanged.**
- **Written before a single preset has been derived and before any render exists.**

---

## 1. What the J2 inventory showed

`data/perturbation_atlas_regions.csv` records that the eight depth-by-component regions
cover **280 of the model's 430 patched tensors**. The remaining **150 (34.88%)** belong to
no region, and their composition is not incidental:

| family | tensors | what it is |
|---|--:|---|
| `blocks.{i}.mod.lin`, `prenorm.scale`, `postnorm.scale` | **84** | modulation and normalisation, 3 per block across all 28 |
| `txtfusion.*` | **49** | the text-image fusion path |
| `first`, `last`, `tproj`, `tmlp`, `txtmlp` | 17 | input, output and small projections |

The frozen §4 said the bands cover everything "with no gaps and no overlaps". That is true
of the **blocks** and false of the **tensors**: `attn` and `mlp` do not exhaust a block.
The wording was the author's error and is corrected here.

## 2. Why two of those families cannot stay excluded

The study's second question is *which regions of the model, when perturbed, move colour the
most*. Asking it while excluding 35% of the model would be defensible if the excluded part
were arbitrary. It is not.

- **`txtfusion` is the path the prompt enters by.** Every study in this project has found
  the prompt dominating everything else, and the open question behind this whole design is
  why one edit behaves differently on different scenes. The most obvious candidate region
  for that question is the one being left out.
- **`mod.lin` and the two norm scales are the modulation path**, where timestep and
  conditioning enter. Perturbing modulation is a qualitatively different intervention from
  perturbing attention weights, not a smaller version of it.

The asymmetry this creates matters for what a null result would mean. A **positive** result
from an 11-condition design would stand. A **negative** one would not: "no region stands
out" would be indistinguishable from "the region that stands out was not measured".

## 3. Two regions added

| region | domain | tensors | pattern |
|---|---|--:|---|
| `modulation_norm` | model | **84** | `blocks.{0–27}.mod.lin`, `blocks.{0–27}.prenorm.scale`, `blocks.{0–27}.postnorm.scale` |
| `txtfusion` | model | **49** | `txtfusion.*` |

Thirteen conditions in total: the eight depth-by-component regions, `clip_only`,
`model_only`, `uniform_all`, `modulation_norm`, `txtfusion`.

Coverage after the addition: 280 + 84 + 49 = **413 of 430**, leaving 17 tensors
(`first`, `last`, `tproj`, `tmlp`, `txtmlp`) in no region. Those 17 are recorded as
`uncovered` in `data/perturbation_atlas_regions.csv` and are deliberately not made into a
region: they are a heterogeneous remainder, not a family, and a region built out of
leftovers would have no interpretation.

**Render counts:** Phase 1, one prompt: 13 x 2 draws x 3 seeds + 3 baselines = **81**.
Phase 2: **81 per prompt**.

## 4. Two properties of the design, recorded so they travel with the results

1. **The regions are not a partition.** Their tensor counts do not sum to `model_only`, and
   `uniform_all` and `model_only` include 17 tensors that no region contains. A region's
   effect is therefore a statement about that region, never a share of a whole.
2. **The regions differ greatly in size.** `attn` bands hold 49 tensors, `mlp` bands 21,
   `modulation_norm` 84, `txtfusion` 49. With the displacement matched in norm, a smaller
   region concentrates the same total push into fewer tensors and so carries larger
   per-tensor multipliers. "Perturbing `mlp`" and "perturbing in a more concentrated way"
   are entangled by construction. Every per-region result is reported beside its tensor
   count.

## 5. Disclosure

`uniform_all` (Amendment 03 §3) and these two regions were all added by the analyst after
the design was declared frozen, each before any preset existed and each with its reason
written down. That is three widenings of a frozen design in one evening. It is recorded
here rather than smoothed over, and no further region is added without the same explicit
step.

## 6. What is not changed

The scalar-only perturbation and its generation (Amendment 03 §2), the four verification
gates (Amendment 03 §4), the loss of comparability with the existing corpus (Amendment 03
§5), the four bands of seven blocks (Amendment 01 §2), and every section of the frozen
document remain in force. The hard stop at J2 remains: the full region list is seen before
a single preset is derived.
