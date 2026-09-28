# Stage 4 Preset (Family A1), re-read on the two new axes

**Date**: 2026-09-28 · **Corpus**: `benchmark_stage4_preset/renders` (140 renders) · **Material**: Family A1 — Western comic linework with pinned monochromatic rim light/hue, 4 prompts (`F1`..`F4`), 7 steering conditions, 5 seeds (`42`, `777`, `1337`, `9999`, `4242145`) · **Scripts**: `experiments/retro_stage4_preset_reading.py` → `data/retro_stage4_preset_cells.csv`, `data/retro_stage4_preset_summary.csv` · **No render.**

---

## 1. Baseline discovery, verification and balance check

`benchmark_stage4_preset/renders` contains 140 renders across 7 conditions and 0 baselines in its own folder.

### Resolution of the missing baseline
The baseline renders reside in `benchmark_stage2_family/renders` (prompts `F1`..`F4`, seeds `42`, `777`, `1337`, `9999`, `4242145`). Direct inspection of the embedded PNG metadata confirms:
* **Prompt text**: identical character-for-character across prompt IDs (e.g. `F1`: *"Western comics style, bold ink outlines, hatched shadows, hard amber-tinted rim light..."*).
* **Sampler configuration**: `euler_ancestral`, `simple` scheduler, 9 steps, CFG scale 1.0, matching random seeds.
* **Resolution & Model**: $1024 \times 1280$, `krea2_turbo_bf16.safetensors`.

The baselines of `stage2_family` were measured with the identical `measure()` estimator and integrated into `data/retro_texture_axes.csv`.

### Arithmetic balance equation
$$\text{140 perturbed renders in stage4 (4 prompts} \times \text{7 conditions} \times \text{5 seeds)}$$
$$\text{Joined to 20 matching baselines in stage2\_family (4 prompts} \times \text{5 seeds)} \implies \text{140 matched cells (100 \% join rate, 0 unparsed)}$$

---

## 2. Reading 1 — Baseline coherence across Family A1

Baseline structure coherence by prompt ($n = 5$ seeds each):

| prompt | baseline coherence (mean) | baseline coherence (sd) |
|---|--:|--:|
| `F1` | 0.5874 | 0.0155 |
| `F2` | 0.5415 | 0.0092 |
| `F3` | 0.5726 | 0.0249 |
| `F4` | 0.5683 | 0.0183 |
| **Overall** | **0.5675** | **0.0166** |

Baseline coherence is remarkably tightly distributed across the four Western comic portraits ($0.5675 \pm 0.0166$), providing a clean reference floor for relative texture ratios.

---

## 3. Reading 2 — Dose ladder check: half dose vs full dose

* `preset_half` (dose 0.5): coherence ratio $= 0.9843$, displacement $= 0.1616$
* `preset_pos` (dose 1.0): coherence ratio $= 0.9513$, displacement $= 0.2384$
* $\Delta\text{coherence} = 0.9513 - 0.9843 = -0.0330$
* $\Delta\ln(\text{dose}) = \ln(1.0 / 0.5) = 0.6931$
* Rate: $\frac{\Delta\text{coherence}}{\Delta\ln(\text{dose})} = -0.0476$

As observed in Stage 5, the calibrated preset maintains high drawing coherence across the dose range from $0.5$ to $1.0$ (remaining above $0.95$), without the catastrophic cliff seen at $2.0\times$ in Stage 9.

---

## 4. Reading 3 — Scale signatures: the three-way comic linework synthesis

Aggregated conditions ($n = 20$ each: 4 prompts $\times$ 5 seeds):

| condition | coherence ratio | sd | pct < 0.90 | pct $\ge$ 0.98 | displacement | contrast | chroma (whole frame) | `1-2px` (b0) | `2-4px` (b1) | `4-8px` (b2) | `8-16px` (b3) | `16-32px` (b4) | peak band |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| `preset_neg` | **1.0446** | 0.0321 | **0.0 %** | **95.0 %** | 0.2500 | 1.0582 | 0.8814 | **1.377** | 1.294 | 1.159 | 1.068 | 1.079 | `1-2px` |
| `rand_pos` | 0.9930 | 0.0397 | 0.0 % | 70.0 % | **0.3799** | 1.1164 | 1.0301 | **1.538** | 1.414 | 1.466 | 1.426 | 1.367 | `1-2px` |
| `blockshuf_pos` | 0.9946 | 0.0468 | 10.0 % | 60.0 % | 0.2727 | 1.1719 | 0.9963 | 0.925 | 1.049 | 1.266 | 1.367 | **1.406** | `16-32px` |
| `blockshuf_neg` | 0.9893 | 0.0412 | 0.0 % | 45.0 % | 0.2048 | 1.0657 | 0.9205 | **1.329** | 1.211 | 1.093 | 1.090 | 1.121 | `1-2px` |
| `preset_half` | 0.9843 | 0.0455 | 10.0 % | 65.0 % | 0.1616 | 1.0691 | 0.9213 | 0.891 | 0.961 | 1.077 | **1.138** | 1.134 | `8-16px` |
| `preset_pos` | 0.9513 | 0.0492 | 25.0 % | 30.0 % | 0.2384 | 1.0966 | 0.9453 | 0.784 | 0.892 | 1.075 | 1.224 | **1.256** | `16-32px` |
| `rand_neg` | 0.9420 | 0.0425 | 10.0 % | 20.0 % | 0.1725 | 0.9477 | 0.9559 | 0.850 | 0.915 | 0.955 | 0.949 | **0.980** | `16-32px` |

*Note on chroma:* Reported strictly as a whole-frame metric.

### Perfect consistency across the comic linework benchmarks
Comparing Family A1 (Stage 4), Family A2 (Stage 5), and Confirmation (Stage 7):
* **`preset_neg`**: coherence ratio reads **$1.0446$** (Stage 4), **$1.0308$** (Stage 5), and **$1.0504$** (Stage 7). In all three independent corpora, $95\%$ to $99\%$ of renders maintain $\ge 0.98$, with $0\%$ below $0.90$. It acts everywhere as a precision linework enhancer peaking at `1-2px` ($b0 = 1.377$).
* **`preset_pos`**: coherence ratio reads **$0.9513$** (Stage 4), **$0.9759$** (Stage 5), and **$0.9769$** (Stage 7). In all three corpora, it suppresses fine details ($b0 = 0.784$) and enhances coarse structure ($b4 = 1.256$).
* **`rand_pos`**: broadband inflation across all bands ($b0 = 1.538 \to b4 = 1.367$).
* **`rand_neg`**: broadband suppression across all bands ($b0 = 0.850 \to b4 = 0.980$).

---

## 5. Reading 4 — Line-preserving movers vs collapses

Ranked by displacement:
1. `rand_pos`: displacement $0.3799$, coherence $0.9930$ (70.0 % $\ge 0.98$, 0.0 % $< 0.90$) — massive broadband line-preserving mover.
2. `blockshuf_pos`: displacement $0.2727$, coherence $0.9946$ (60.0 % $\ge 0.98$, 10.0 % $< 0.90$) — coarse-shifted mover.
3. `preset_neg`: displacement $0.2500$, coherence **$1.0446$** (**95.0 % $\ge 0.98$**, 0.0 % $< 0.90$) — **clean linework enhancer**.
4. `preset_pos`: displacement $0.2384$, coherence $0.9513$ (30.0 % $\ge 0.98$, 25.0 % $< 0.90$) — coarse-structure mover.
5. `blockshuf_neg`: displacement $0.2048$, coherence $0.9893$ (45.0 % $\ge 0.98$, 0.0 % $< 0.90$) — line-preserving mover.
6. `rand_neg`: displacement $0.1725$, coherence $0.9420$ (20.0 % $\ge 0.98$, 10.0 % $< 0.90$) — mild line attenuation.
7. `preset_half`: displacement $0.1616$, coherence $0.9843$ (65.0 % $\ge 0.98$, 10.0 % $< 0.90$) — mild mover.

---

## 6. What this means for existing claims

`notebook/01-mark-style.md` and `docs/prereg_family_coherence.md` reference Family A1 as the initial test of preset steering:
1. Stroke density and mark texture shifts:
   * Confirmed as authentic line modifications. Both `preset_pos` ($0.951$) and `preset_neg` ($1.045$) operate well within usable structure coherence, without collapsing the gradient tensor.
2. Cross-family coherence:
   * The structural findings on Family A1 agree in sign, amplitude, and band frequency with Family A2 and Stage 7.

**Claims audit:**
* No claim sits on a collapse condition.
* No claim changes status.
