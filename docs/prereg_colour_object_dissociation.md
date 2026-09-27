# Pre-registration: Colour/Object Dissociation Sweep (Stage 2)

- **Date:** 2026-09-27
- **Governed by:** `docs/assessment_colour_object_dissociation.md` and `docs/RENDERS_2026-09-27_colour_object_pilot.md`.
- **Written and committed:** after Stage 1 feasibility gate passed (4/4) and **before any Stage 2 render is generated**.

---

## 1. Stage 1 Baseline Empirical Poles

From the 15 verified pilot renders in `data/colour_object_pilot_measurements.csv`:

| Pole | Condition | Measured Hue Range | Mean Hue | Standard Deviation |
|---|---|---|---:|---:|
| **Purple Pole** | `LP` (uncommon binding) | $[300.33^\circ, 314.23^\circ]$ | **$309.80^\circ$** | $5.53^\circ$ |
| **Green Pole** | `LG` (prior control) | $[87.61^\circ, 88.40^\circ]$ | **$88.00^\circ$** | $0.34^\circ$ |
| **Neutral Prior** | `LN` (unspecified) | $[34.39^\circ, 37.83^\circ]$ | **$36.01^\circ$** | $1.67^\circ$ |

The measured separation between the purple and green poles is **$138.2^\circ$** (circular distance), with zero overlap across seeds.

---

## 2. Frozen Operational Definitions for Stage 2

For each macro block $B \in \{\text{Block\_1}, \dots, \text{Block\_6}\}$, sign $s \in \{\text{pos}, \text{neg}\}$ at dose $0.050$:

### A. Object Integrity Gate
A render is **intact** if the segmented object occupies at least 3.0% of the frame area (`fg_share >= 0.030`) and exhibits non-zero chromatic structure (`mean_sat >= 0.15`).
- If an object fails this condition in $\ge 2$ of 3 seeds for either prompt, that cell is classified as **`object_collapse`**.

### B. Reversion (Breaking the Binding)
A block perturbation achieves **`reversion`** if and only if:
1. **Object remains intact** on both `LP` and `LG` across all 3 seeds.
2. **`LG` stays green**: mean hue of `LG` remains within $[65.0^\circ, 120.0^\circ]$ on $\ge 2$ of 3 seeds (shift $|\Delta H_{LG}| < 25^\circ$).
3. **`LP` shifts toward green**: mean hue of `LP` moves into the green band $[65.0^\circ, 165.0^\circ]$ or exhibits a shift toward the green pole $\Delta H_{LP \to \text{green}} \ge 70.0^\circ$ on $\ge 2$ of 3 seeds.

### C. Generic Hue Rotation
A block perturbation is classified as **`generic_rotation`** if:
1. Both `LP` and `LG` remain intact.
2. `LP` and `LG` shift by comparable amounts in the same angular direction:
   $$|\Delta H_{LP} - \Delta H_{LG}| < 30.0^\circ \quad \text{and} \quad \text{sign}(\Delta H_{LP}) = \text{sign}(\Delta H_{LG})$$
   demonstrating global chromatic drift rather than selective binding decoupling.

### D. Ineffective / Preserved Binding
If neither reversion, generic rotation, nor object collapse occurs, and both `LP` and `LG` remain within $20^\circ$ of their respective baseline poles, the cell is classified as **`unperturbed_binding`**.

---

## 3. Decision Matrix and Stopping Rule

- **Decisive finding (Dissociation)**: Observed if at least one block produces **`reversion`** without collapse, while other blocks produce **`object_collapse`** without reversion.
- **Negative finding**: If all blocks either produce generic rotation or unperturbed binding, the hypothesis that macro blocks selectively house colour-object binding at dose 0.050 is refuted for this architecture.
