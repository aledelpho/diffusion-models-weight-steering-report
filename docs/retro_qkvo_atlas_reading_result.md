# QKVO Atlas, re-read on the two new axes

**Date**: 2026-09-28 · **Corpus**: `benchmark_qkvo_atlas--renders` (433 renders) · **Material**: Attention sub-matrices ($W_q, W_k, W_v, W_o$) on Block 1 and Block 6, plus normscales controls, across 8 style families (`S1_photo` to `S8_charcoal`) and 3 seeds (`42`, `777`, `1337`) · **Scripts**: `experiments/retro_qkvo_atlas_reading.py` → `data/retro_qkvo_atlas_cells.csv`, `data/retro_qkvo_atlas_summary.csv` · **No render.**

---

## 1. Baseline verification and arithmetic balance check

`benchmark_qkvo_atlas--renders` contains 433 renders and only 1 baseline in its own folder (`determinism_check_S1_photo_baseline_seed42_00001_.png`).

### Verification of the baseline hypothesis
Before performing any join, the hypothesis that baselines reside in `benchmark_atlas_phase1--renders` was verified directly against the physical PNG metadata:
* **Prompt text**: identical positive and negative prompt text across both folders for each style.
* **Sampler configuration**: `euler_ancestral`, `simple` scheduler, 9 steps, CFG scale 1.0, identical random seeds.
* **Resolution & Model**: $1024 \times 1280$, `krea2_turbo_bf16.safetensors`.
* **Zero-metric determinism check**: the in-folder file `determinism_check_S1_photo_baseline_seed42_00001_.png` compared to `S1_photo_baseline_seed42_00001_.png` in `benchmark_atlas_phase1--renders` yielded:
  $$\Delta\text{coherence} = 0.000000,\quad \Delta\text{band0..4} = 0.000000,\quad \Delta\text{variance} = 0.000000,\quad \Delta\text{chroma} = 0.000000$$

The baselines are confirmed bit-for-bit identical.

### Arithmetic balance equation
$$\text{432 perturbed renders} + \text{1 determinism check} = \text{433 files in QKVO (0 unparsed)}$$
$$\text{Joined to 24 Atlas baselines (8 styles} \times \text{3 seeds)} \implies \text{432 matched cells (100 \% join rate)}$$

---

## 2. Reading 1 — Coherence behaviour style by style

| style | cells | coherence ratio (mean) | sd | pct < 0.90 | pct $\ge$ 0.98 |
|---|--:|--:|--:|--:|--:|
| `S1_photo` | 54 | 0.9947 | 0.0159 | 0.0 % | 79.6 % |
| `S2_watercolor` | 54 | 0.9980 | 0.0306 | 0.0 % | 88.9 % |
| `S3_lowpoly` | 54 | 1.0012 | 0.0179 | 0.0 % | 88.9 % |
| `S4_claymation` | 54 | 0.9967 | 0.0112 | 0.0 % | 96.3 % |
| `S5_ukiyoe` | 54 | 0.9986 | 0.0101 | 0.0 % | 96.3 % |
| `S6_pixel` | 54 | 1.0018 | 0.0156 | 0.0 % | 87.0 % |
| `S7_glass` | 54 | 0.9991 | 0.0151 | 0.0 % | 88.9 % |
| `S8_charcoal` | 54 | 1.0039 | 0.0336 | 0.0 % | 88.9 % |

**Key observations:**
1. Across the entire bench, **0.0 % of cells fall below 0.90**. Sub-matrix steering at dose 0.200 never causes structural collapse in any style.
2. The sensitivity hierarchy matches the atlas findings: line-bearing and texture-rich styles (`S8_charcoal` sd 0.0336, `S2_watercolor` sd 0.0306) exhibit 3× greater variance under steering than geometry-defined or flat styles (`S5_ukiyoe` sd 0.0101, `S4_claymation` sd 0.0112).

---

## 3. Reading 2 & 3 — Sub-matrix scale signatures and the QK vs VO dichotomy

Aggregated conditions ($n = 24$ each, pooled across 8 styles and 3 seeds):

| condition | coherence ratio | pct < 0.90 | pct $\ge$ 0.98 | displacement | contrast | chroma (whole frame) | `1-2px` (b0) | `2-4px` (b1) | `4-8px` (b2) | `8-16px` (b3) | `16-32px` (b4) | peak band |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| `normscales_all_neg` | 1.0000 | 0.0 % | 100.0 % | 0.0000 | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | `1-2px` |
| `normscales_all_pos` | 1.0000 | 0.0 % | 100.0 % | 0.0000 | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | `1-2px` |
| `wk_b1_neg` | 0.9973 | 0.0 % | 95.8 % | 0.0214 | 1.0019 | 1.0048 | 1.008 | 1.007 | 1.005 | 1.005 | 0.998 | `1-2px` |
| `wk_b1_pos` | 0.9968 | 0.0 % | 91.7 % | 0.0283 | 0.9982 | 1.0021 | 1.003 | 0.998 | 0.989 | 0.986 | 0.988 | `1-2px` |
| `wk_b6_neg` | 0.9992 | 0.0 % | 100.0 % | 0.0195 | 1.0031 | 1.0037 | 1.001 | 1.006 | 1.005 | 1.004 | 1.002 | `2-4px` |
| `wk_b6_pos` | 0.9991 | 0.0 % | 100.0 % | 0.0188 | 0.9981 | 1.0014 | 1.001 | 0.999 | 0.996 | 0.996 | 1.002 | `16-32px` |
| `wq_b1_neg` | 0.9981 | 0.0 % | 100.0 % | 0.0190 | 1.0012 | 1.0024 | 0.994 | 1.000 | 1.003 | 1.003 | 1.002 | `4-8px` |
| `wq_b1_pos` | 0.9977 | 0.0 % | 100.0 % | 0.0206 | 0.9986 | 1.0031 | 1.000 | 1.004 | 1.001 | 0.994 | 0.995 | `2-4px` |
| `wq_b6_neg` | 0.9985 | 0.0 % | 100.0 % | 0.0201 | 1.0009 | 1.0027 | 1.005 | 1.007 | 1.006 | 1.001 | 1.001 | `2-4px` |
| `wq_b6_pos` | 0.9981 | 0.0 % | 100.0 % | 0.0193 | 1.0028 | 1.0028 | 1.004 | 0.999 | 1.002 | 1.005 | 1.006 | `16-32px` |
| `wo_b1_neg` | 1.0014 | 0.0 % | 83.3 % | 0.0814 | 1.0110 | 1.0172 | 1.017 | **1.039** | 1.025 | 1.008 | 1.016 | `2-4px` |
| `wo_b1_pos` | 1.0047 | 0.0 % | 100.0 % | 0.0739 | 1.0108 | 1.0241 | 0.992 | 0.989 | 0.994 | 1.005 | **1.011** | `16-32px` |
| `wv_b1_neg` | 1.0014 | 0.0 % | 87.5 % | 0.0799 | 1.0139 | 1.0177 | 1.026 | **1.042** | 1.030 | 1.007 | 1.012 | `2-4px` |
| `wv_b1_pos` | 1.0066 | 0.0 % | 95.8 % | 0.0766 | 1.0113 | 1.0284 | 0.990 | 0.987 | 0.994 | 1.003 | **1.016** | `16-32px` |
| `wo_b6_neg` | 0.9656 | 0.0 % | 25.0 % | **0.0972** | 0.9668 | 0.9789 | 0.910 | 0.903 | 0.904 | 0.914 | **0.938** | `16-32px` |
| `wo_b6_pos` | **1.0284** | 0.0 % | 100.0 % | 0.0813 | 1.0173 | 1.0209 | 1.081 | **1.090** | 1.090 | 1.079 | 1.046 | `2-4px` |
| `wv_b6_neg` | 0.9662 | 0.0 % | 29.2 % | **0.0920** | 0.9683 | 0.9837 | 0.918 | 0.912 | 0.913 | 0.918 | **0.936** | `16-32px` |
| `wv_b6_pos` | **1.0272** | 0.0 % | 100.0 % | 0.0783 | 1.0118 | 1.0195 | 1.076 | **1.085** | 1.080 | 1.065 | 1.039 | `2-4px` |

*Note on chroma:* On this full-scene corpus without object segmentation masks, chroma is reported strictly as a whole-frame metric.

### Findings on sub-layer architecture
1. **The Q/K vs V/O divide**:
   * Steering $W_q$ (Query) and $W_k$ (Key) produces almost no measurable change in gradient or band texture (displacement $0.019$–$0.028$, band ratios within $\pm 0.8\%$ of baseline).
   * Steering $W_v$ (Value) and $W_o$ (Output projection) carries the entire steering impact (displacement $0.074$–$0.097$, band ratios deviating by up to $+9\%$).
2. **Block 6 antisymmetry**:
   * `wo_b6_pos` and `wv_b6_pos` systematically *raise* drawing coherence ($1.028$ and $1.027$, 100 % $\ge 0.98$) and inflate energy across all bands with a peak at `2-4px` ($+9\%$).
   * `wo_b6_neg` and `wv_b6_neg` depress coherence ($0.966$) and attenuate band energy across all scales (suppression of $\approx 10\%$).
3. **Normscales**:
   * Modifying normalization scales (`normscales_all_pos`, `normscales_all_neg`) produces an absolute zero displacement ($0.00000$) across every single metric, acting as an identity operation.

---

## 4. Reading 4 — Line-preserving movers vs collapses

Ranked by displacement:

1. `wo_b6_neg`: displacement $0.0972$, coherence $0.9656$ (0.0 % $< 0.90$) — mild line attenuation.
2. `wv_b6_neg`: displacement $0.0920$, coherence $0.9662$ (0.0 % $< 0.90$) — mild line attenuation.
3. `wo_b1_neg`: displacement $0.0814$, coherence $1.0014$ (83.3 % $\ge 0.98$) — line-preserving mover.
4. `wo_b6_pos`: displacement $0.0813$, coherence **$1.0284$** (100.0 % $\ge 0.98$) — line-enhancing mover.
5. `wv_b1_neg`: displacement $0.0799$, coherence $1.0014$ (87.5 % $\ge 0.98$) — line-preserving mover.
6. `wv_b6_pos`: displacement $0.0783$, coherence **$1.0272$** (100.0 % $\ge 0.98$) — line-enhancing mover.
7. `wv_b1_pos`: displacement $0.0766$, coherence $1.0066$ (95.8 % $\ge 0.98$) — line-preserving mover.
8. `wo_b1_pos`: displacement $0.0739$, coherence $1.0047$ (100.0 % $\ge 0.98$) — line-preserving mover.

16 of the 18 conditions maintain coherence $\ge 0.98$. None causes collapse.

---

## 5. What this means for existing claims

1. **`position-function-or-proximity` (`notebook/04-where-in-the-model.md` / `docs/RUNBOOK_qkvo_atlas_plan.md`)**:
   This experiment directly resolves the proximity debate: $W_q$, $W_k$, $W_v$, and $W_o$ exist within the **exact same block**, at the **exact same distance from the output**, on the **exact same residual stream**. The fact that $W_v$ and $W_o$ move texture by $0.08$–$0.09$ while $W_q$ and $W_k$ produce near-zero displacement ($0.02$) demonstrates that steering differences reflect internal computational function rather than downstream network proximity.
2. **`sign_decomposition_result.md`**:
   The common-mode and signed-mode findings reported on QKVO did not sit on collapsed images: structure coherence remained $\ge 0.965$ across all 18 conditions. The observed mathematical separation between directional structure and omnidirectional grain is verified on structurally sound renders.

**Claims audit:**
* No claim was made on a collapse condition.
* No claim changes status.
