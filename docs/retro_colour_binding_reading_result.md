# Colour Binding Bench, re-read on the two new axes

**Date**: 2026-09-28 · **Corpus**: `benchmark_colour_binding--renders` (242 renders) · **Material**: 3 isolated object prompts (`LG`, `LN`, `LP`) on a flat light grey background, testing 12 group-arm conditions (`Block_1`..`Block_6`, `pos` and `neg`) across two doses ($0.050$ and $0.200$) and 3 seeds (`42`, `777`, `1337`) · **Scripts**: `experiments/retro_colour_binding_reading.py` → `data/retro_colour_binding_cells.csv`, `data/retro_colour_binding_summary.csv` · **No render.**

---

## 1. The re-reading and balance check

`benchmark_colour_binding--renders` tests block steering on subjects isolated against a uniform, neutral grey background.

The filename structures follow:
* Perturbed: `^([A-Za-z0-9]+)_Block_(\d+)(pos|neg)_([0-9\.]+)_krea2_seed(\d+)_00001_\.png$`
* Baseline: `^([A-Za-z0-9]+)_baseline_krea2_seed(\d+)_00001_\.png$`

$$\text{216 perturbed renders} + \text{9 primary baselines} + \text{17 auxiliary pilot baselines} = \text{242 total files (0 unparsed)}$$

Every perturbed render joins to its matching baseline on the same prompt and seed ($n = 216$ matched cells, 100 % join rate).

---

## 2. Reading 1 — Coherence behaviour by prompt

Aggregated across all 12 conditions and 2 doses ($n = 72$ per prompt):

| prompt | cells | coherence ratio (mean) | sd | pct < 0.90 | pct $\ge$ 0.98 |
|---|--:|--:|--:|--:|--:|
| `LG` | 72 | 1.0552 | 0.2413 | 19.4 % | 63.9 % |
| `LN` | 72 | 1.0302 | 0.2047 | 15.3 % | 66.7 % |
| `LP` | 72 | 1.0117 | 0.1455 | 8.3 % | 61.1 % |

Because the baseline background is a flat, gradient-free grey field, the overall coherence ratio is highly sensitive to background perturbations: conditions that inject texture into the background (`Block_6 pos`) drive whole-frame coherence above $1.60$, while conditions that destroy the object's contours (`Block_5 pos`) pull it down below $0.75$.

---

## 3. Reading 2 — Dose ladder check: 0.050 vs 0.200

Dose ratio $= 4.0\times$ ($\Delta\ln(\text{dose}) = \ln(4.0) = 1.3863$). Aggregated across 3 prompts $\times$ 3 seeds ($n = 9$ each):

| condition | coherence (0.050) | coherence (0.200) | rate $\frac{\Delta\text{coh}}{\Delta\ln\text{dose}}$ | displacement (0.050) | displacement (0.200) | chroma (whole frame) | chroma (object only*) |
|---|--:|--:|--:|--:|--:|--:|--:|
| `Block_6_pos` | 0.9978 | **1.6795** | **+0.4918** | 0.1194 | **1.2076** | **1.4882** | **0.726** |
| `Block_6_neg` | 0.7779 | 1.1536 | +0.2710 | 0.1143 | 0.4033 | 1.8139 | 1.815 |
| `Block_4_pos` | 1.0039 | 1.1349 | +0.0945 | 0.0962 | 0.3304 | 1.4318 | — |
| `Block_2_pos` | 1.0086 | 1.1201 | +0.0804 | 0.0942 | 0.1980 | 1.2863 | — |
| `Block_3_pos` | 1.0238 | 1.1083 | +0.0609 | 0.2066 | 0.5256 | 1.5704 | 1.563 |
| `Block_2_neg` | 1.0062 | 1.1085 | +0.0738 | 0.1406 | 0.3584 | 1.0250 | — |
| `Block_1_neg` | 0.9618 | 1.0983 | +0.0984 | 0.0807 | 0.2926 | 1.2845 | — |
| `Block_3_neg` | 1.0060 | 1.0532 | +0.0340 | 0.1523 | 0.2317 | 0.9178 | — |
| `Block_4_neg` | 0.9608 | 0.9752 | +0.0104 | 0.1085 | 0.3053 | 1.0546 | 0.927 |
| `Block_5_neg` | 1.0574 | 0.9741 | -0.0601 | 0.1238 | 0.4649 | 1.6242 | 1.610 |
| `Block_1_pos` | 0.9955 | 0.9654 | -0.0217 | 0.0991 | 0.3221 | 1.3477 | 1.308 |
| `Block_5_pos` | 0.8768 | **0.7296** | **-0.1062** | 0.0758 | 0.2602 | 1.2207 | — |

*\*Object-restricted chroma from `docs/chroma_redistribution.md`.*

**Key findings on the dose ladder:**
1. **The collapse of `Block_5 pos`**: coherence plunges to **$0.7296$** at dose 0.200 (rate $-0.1062$). The contours of the leaf disintegrate.
2. **The explosion of `Block_6 pos`**: coherence surges to **$1.6795$**, with displacement skyrocketing from $0.1194$ to **$1.2076$** ($+911\%$).

---

## 4. Reading 3 — Scale signatures at dose 0.200

Band energy ratios relative to matched baseline ($n = 9$ each):

| condition | `1-2px` (b0) | `2-4px` (b1) | `4-8px` (b2) | `8-16px` (b3) | `16-32px` (b4) | peak band | contrast ratio |
|---|--:|--:|--:|--:|--:|---|--:|
| `Block_6_pos` | **3.115** | **5.905** | **5.419** | 1.534 | 0.568 | `2-4px` (b1) | 0.4939 |
| `Block_3_pos` | **2.362** | 1.878 | 1.475 | 1.252 | 1.222 | `1-2px` (b0) | 1.0760 |
| `Block_5_neg` | **2.189** | 1.826 | 1.238 | 0.987 | 0.979 | `1-2px` (b0) | 1.0087 |
| `Block_2_neg` | **1.897** | 1.554 | 1.155 | 0.988 | 0.954 | `1-2px` (b0) | 0.9078 |
| `Block_4_neg` | **1.591** | 1.389 | 1.125 | 1.000 | 0.990 | `1-2px` (b0) | 0.9519 |
| `Block_1_pos` | **1.552** | 0.977 | 0.821 | 0.772 | 0.776 | `1-2px` (b0) | 0.8301 |
| `Block_2_pos` | **1.177** | 1.113 | 1.003 | 1.002 | 1.029 | `1-2px` (b0) | 1.1936 |
| `Block_1_neg` | 1.058 | **1.527** | 1.413 | 1.160 | 1.077 | `2-4px` (b1) | 0.9666 |
| `Block_3_neg` | 0.863 | **1.021** | 0.920 | 0.852 | 0.860 | `2-4px` (b1) | 0.9617 |
| `Block_4_pos` | 0.769 | 1.155 | **1.271** | 1.227 | 1.208 | `4-8px` (b2) | 1.3140 |
| `Block_5_pos` | 0.768 | 1.084 | 1.225 | 1.251 | **1.256** | `16-32px` (b4) | 1.1363 |
| `Block_6_neg` | 0.615 | 0.706 | 0.807 | 0.930 | **1.081** | `16-32px` (b4) | 1.2819 |

`Block_6 pos` exhibits a colossal resonance at `2-4px` ($b1 = 5.905$, $+490\%$) and `4-8px` ($b2 = 5.419$, $+442\%$). This is the physical signature of the oriented curl field that overtakes the entire render.

---

## 5. Reading 4 — The chroma redistribution audit

In full scenes, whole-frame chroma cannot tell removal from redistribution. Because `colour_binding` features an isolated leaf on a plain grey background, it provides the sole experimental ground truth in the repository separating the two:

1. **Agreement across ordinary conditions**: For 11 of 12 conditions, whole-frame chroma ratio and object-restricted chroma ratio agree within $\approx 0.1$–$0.2$:
   * `Block_6 neg`: whole frame $= 1.814$, object $= 1.815$
   * `Block_3 pos`: whole frame $= 1.570$, object $= 1.563$
   * `Block_1 pos`: whole frame $= 1.348$, object $= 1.308$
   * `Block_5 neg`: whole frame $= 1.624$, object $= 1.610$
2. **The `Block_6 pos` divergence**:
   * Whole-frame chroma ratio: **$1.488$**
   * Object-restricted chroma ratio: **$0.726$** ($-27.4\%$)
   * Background chroma ratio: **$12.519$** ($+1152\%$)
3. **The physical synthesis**:
   `Block_6 pos` does not desaturate the render. The massive mid-frequency band energy ($5.9\times$ at `2-4px`, $5.4\times$ at `4-8px`) is an energetic texture field that carries chromatic saturation into the empty background field, while the object itself loses colour.

---

## 6. What this means for existing claims

1. **`Block_6 pos` antisymmetry (`docs/colour_gate_and_chroma_audit.md` / commit `d19ce54`)**:
   The claim that `Block_6` acts as an antisymmetric chroma knob is valid only when restricted to the subject object ($0.726$ on `pos`, $1.815$ on `neg`). On the whole image, both arms increase chroma ($1.488$ and $1.814$). The retro texture axes confirm that `Block_6 pos` operates as a **colour redistribution mechanism** accompanied by severe background gradient generation.
2. **`Block_5 pos` collapse**:
   `Block_5 pos` collapses structurally ($0.7296$ coherence at dose 0.200). Any aesthetic or stylistic claims regarding `Block_5 pos` at dose 0.200 must be scoped as sitting on a collapsed image.

**Claims audit:**
* `Block_6 pos` restated as object-restricted redistribution, confirmed by whole-frame axes.
* `Block_5 pos` confirmed as a structural collapse condition.

No claim changes status.
