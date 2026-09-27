# Pre-registration: Colour/Object Dissociation Sweep (Stage 2)

- **Date:** 2026-09-27
- **Governed by:** `docs/assessment_colour_object_dissociation.md` and `docs/RENDERS_2026-09-27_colour_object_pilot.md`.
- **Amended before sweep execution:** Inclusion of `LN` as third arm (117 renders total).
- **Written and committed:** after Stage 1 feasibility gate passed (4/4) and **before Stage 2 sweep completion**.

---

## 1. Stage 1 Baseline Empirical Poles

From the 15 verified pilot renders in `data/colour_object_pilot_measurements.csv`:

| Pole | Condition | Measured Hue Range | Mean Hue | Standard Deviation |
|---|---|---|---:|---:|
| **Purple Pole** | `LP` (uncommon binding) | $[300.33^\circ, 314.23^\circ]$ | **$309.80^\circ$** | $5.53^\circ$ |
| **Green Pole** | `LG` (prior control) | $[87.61^\circ, 88.40^\circ]$ | **$88.00^\circ$** | $0.34^\circ$ |
| **Natural Prior** | `LN` (unspecified) | $[34.39^\circ, 37.83^\circ]$ | **$36.01^\circ$** | $1.67^\circ$ |

The measured separation between the purple and green poles is **$138.2^\circ$** (circular distance), with zero overlap across seeds.
The natural unconstrained prior sits at **$36.0^\circ$** (warm autumnal ochre/brown).

---

## 2. Experimental Design (3 Arms, 117 Renders)

- **Prompts (3)**:
  - `LP`: *"a single purple leaf centered..."* (uncommon binding)
  - `LG`: *"a single green leaf centered..."* (prior control)
  - `LN`: *"a single leaf centered..."* (unspecified natural prior)
- **Macro Blocks (6)**: `Block_1` through `Block_6`
- **Signs (2)**: `pos` (+0.050), `neg` (-0.050)
- **Dose**: 0.050
- **Seeds (3)**: 42, 777, 1337
- **Counts**:
  - Perturbed: 12 conditions (6 blocks x 2 signs) x 3 prompts x 3 seeds = **108 renders**
  - Baselines: 3 prompts x 3 seeds = **9 renders**
  - Total: **117 renders**

---

## 3. Frozen Operational Definitions for Stage 2

For each macro block $B \in \{\text{Block\_1}, \dots, \text{Block\_6}\}$, sign $s \in \{\text{pos}, \text{neg}\}$ at dose $0.050$:

### A. Object Integrity Gate
A render is **intact** if the segmented object occupies at least 3.0% of the frame area (`fg_share >= 0.030`) and exhibits non-zero chromatic structure (`mean_sat >= 0.15`).
- If an object fails this condition in $\ge 2$ of 3 seeds for any prompt, that cell is classified as **`object_collapse`**.

### B. Reversion (Breaking the Binding)
A block perturbation achieves **`reversion`** if and only if:
1. **Object remains intact** on `LP`, `LG`, and `LN` across all 3 seeds.
2. **`LG` stays green**: mean hue of `LG` remains within $[65.0^\circ, 120.0^\circ]$ on $\ge 2$ of 3 seeds (shift $|\Delta H_{LG}| < 25^\circ$).
3. **`LP` shifts toward green or natural prior**:
   - *Semantic Reversion (toward green control)*: mean hue of `LP` moves into $[65.0^\circ, 165.0^\circ]$ or exhibits $|\Delta H_{LP \to \text{green}}| \le 50.0^\circ$ on $\ge 2$ of 3 seeds.
   - *Default Reversion (toward natural prior)*: mean hue of `LP` shifts into the autumnal band $[20.0^\circ, 55.0^\circ]$ alongside `LN`.

### C. Generic Hue Rotation
A block perturbation is classified as **`generic_rotation`** if:
1. All three prompts remain intact.
2. `LP`, `LG`, and `LN` shift by comparable amounts in the same angular direction:
   $$|\Delta H_{LP} - \Delta H_{LG}| < 30.0^\circ \quad \text{and} \quad |\Delta H_{LP} - \Delta H_{LN}| < 30.0^\circ$$
   demonstrating global chromatic drift rather than selective binding decoupling.

### D. Ineffective / Preserved Binding
If neither reversion, generic rotation, nor object collapse occurs, and all three arms remain within $20^\circ$ of their respective baseline poles, the cell is classified as **`unperturbed_binding`**.

---

## 4. Decision Matrix and Stopping Rule

- **Decisive finding (Dissociation)**: Observed if at least one block produces **`reversion`** without collapse, while other blocks produce **`object_collapse`** without reversion.
- **Role of the Third Arm (`LN`)**: Differentiates whether a broken binding falls back to the **canonical concept** (green leaf, $88^\circ$) or the **training distribution centroid** (autumnal leaf, $36^\circ$).
