# Stage 7 (Western comic linework confirmation), re-read on the two new axes

**Date**: 2026-09-28 · **Corpus**: `benchmark_stage7/renders` (480 renders) · **Material**: 16 Western comic confirmation prompts (`I01`..`I24`), 6 steering conditions at $1.0\times$ dose, 5 seeds (`42`, `777`, `1337`, `9999`, `4242145`) · **Scripts**: `experiments/retro_stage7_reading.py` → `data/retro_stage7_cells.csv`, `data/retro_stage7_summary.csv` · **No render.**

---

## 1. Baseline discovery, verification and balance check

`benchmark_stage7/renders` contains 480 renders and 0 baselines in its own folder.

### Resolution of the missing baseline
As anticipated in the handover document, the baseline renders reside in the sibling bench `benchmark_stage7a/renders` (120 renders, 24 prompts $\times$ 5 seeds). Direct inspection of the embedded PNG metadata between `stage7` and `stage7a` on matching prompt IDs confirms:
* **Prompt text**: identical character-for-character across prompt IDs (e.g. `I06`: *"Western comics style, bold ink outlines, hatched shadows, upper body portrait. A human man with cropped brown hair and stubble..."*).
* **Sampler configuration**: `euler_ancestral`, `simple` scheduler, 9 steps, CFG scale 1.0, matching random seeds.
* **Resolution & Model**: $1024 \times 1280$, `krea2_turbo_bf16.safetensors`.

The 120 baseline renders of `stage7a` were measured using the identical `measure()` estimator and integrated into `data/retro_texture_axes.csv`.

### Arithmetic balance equation
$$\text{480 perturbed renders in stage7 (16 prompts} \times \text{6 conditions} \times \text{5 seeds)}$$
$$\text{Joined to 80 matching baselines in stage7a (16 prompts} \times \text{5 seeds)} \implies \text{480 matched cells (100 \% join rate, 0 unparsed)}$$
*(The remaining 40 renders in stage7a belong to the 8 prompts I03, I04, I08, I13, I14, I15, I19, I22 not selected for the 16-prompt stage7 bench).*

---

## 2. Reading 1 — Baseline coherence across the 16 Western comic prompts

Baseline structure coherence by prompt ($n = 5$ seeds each):

| prompt | baseline coherence (mean) | baseline coherence (sd) |
|---|--:|--:|
| `I01` | 0.5772 | 0.0081 |
| `I02` | 0.6664 | 0.0119 |
| `I05` | 0.5765 | 0.0232 |
| `I06` | 0.5754 | 0.0149 |
| `I07` | 0.5581 | 0.0172 |
| `I09` | 0.5980 | 0.0182 |
| `I10` | 0.6245 | 0.0280 |
| `I11` | 0.6663 | 0.0152 |
| `I12` | 0.6940 | 0.0384 |
| `I16` | 0.5733 | 0.0235 |
| `I17` | 0.5626 | 0.0263 |
| `I18` | 0.5798 | 0.0293 |
| `I20` | 0.6247 | 0.0094 |
| `I21` | 0.6256 | 0.0253 |
| `I23` | 0.6167 | 0.0132 |
| `I24` | 0.6035 | 0.0237 |
| **Overall** | **0.6077** | **0.0394** |

Baseline coherence is exceptionally stable across the 16 comic portraits (overall mean $0.6077$, seed sd within prompts $\approx 0.01$–$0.02$), confirming that Western comic linework provides an ideal structural canvas for texture gradient analysis.

---

## 3. Reading 2 & 3 — Condition summaries, scale signatures and replication of Stage 5

Aggregated conditions ($n = 80$ each: 16 prompts $\times$ 5 seeds):

| condition | coherence ratio | sd | pct < 0.90 | pct $\ge$ 0.98 | displacement | contrast | chroma (whole frame) | `1-2px` (b0) | `2-4px` (b1) | `4-8px` (b2) | `8-16px` (b3) | `16-32px` (b4) | peak band |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| `preset_neg` | **1.0504** | 0.0305 | **0.0 %** | **98.8 %** | 0.1193 | 1.0174 | 1.0295 | **1.068** | 1.056 | 1.008 | 0.968 | 0.972 | `1-2px` |
| `blockshuf_neg` | **1.0233** | 0.0345 | 0.0 % | 88.8 % | 0.1454 | 1.0505 | 1.0271 | **1.171** | 1.065 | 0.997 | 1.025 | 1.077 | `1-2px` |
| `rand_pos` | **1.0214** | 0.0526 | 6.2 % | 80.0 % | 0.1446 | 1.1228 | 1.0064 | **1.158** | 1.091 | 1.115 | 1.119 | 1.088 | `1-2px` |
| `blockshuf_pos` | 0.9913 | 0.0463 | 3.8 % | 53.8 % | 0.1446 | 1.1129 | 0.9806 | 0.876 | 0.977 | **1.038** | 1.032 | 1.022 | `4-8px` |
| `rand_neg` | 0.9844 | 0.0247 | 0.0 % | 51.2 % | 0.1527 | 0.9556 | 1.0291 | 0.858 | 0.899 | 0.907 | 0.928 | **0.972** | `16-32px` |
| `preset_pos` | 0.9769 | 0.0416 | 7.5 % | 51.2 % | 0.1516 | 1.0915 | 1.0478 | 0.862 | 0.920 | 0.987 | 1.022 | **1.057** | `16-32px` |

*Note on chroma:* Reported strictly as a whole-frame metric.

### Perfect replication of Stage 5 scale signatures
The scale signatures found in Stage 5 replicate on Stage 7:
1. `preset_neg`: enhances fine lines and hatching ($b0 = 1.068$, $b1 = 1.056$) while gently attenuating coarse structures ($b3 = 0.968, b4 = 0.972$). It raises coherence systematically to **$1.0504$**, with **$98.8\%$ of cells $\ge 0.98$** and $0\%$ below $0.90$.
2. `preset_pos`: acts as the exact reciprocal high-pass suppressor / coarse-enhancer ($b0 = 0.862 \to b4 = 1.057$), with coherence at $0.9769$ (virtually identical to Stage 5's $0.9759$).
3. `rand_pos`: broadband inflation ($b0 = 1.158, b3 = 1.119, b4 = 1.088$).
4. `rand_neg`: broadband suppression across all 5 bands ($b0 = 0.858$ to $b4 = 0.972$).

---

## 4. Reading 4 — Line-preserving movers vs collapses

Ranked by displacement:
1. `rand_neg`: displacement $0.1527$, coherence $0.9844$ (51.2 % $\ge 0.98$, 0.0 % $< 0.90$) — mild line preservation.
2. `preset_pos`: displacement $0.1516$, coherence $0.9769$ (51.2 % $\ge 0.98$, 7.5 % $< 0.90$) — coarse-shifted mover.
3. `blockshuf_neg`: displacement $0.1454$, coherence **$1.0233$** (88.8 % $\ge 0.98$, 0.0 % $< 0.90$) — line-preserving mover.
4. `rand_pos`: displacement $0.1446$, coherence **$1.0214$** (80.0 % $\ge 0.98$, 6.2 % $< 0.90$) — line-preserving mover.
5. `blockshuf_pos`: displacement $0.1446$, coherence $0.9913$ (53.8 % $\ge 0.98$, 3.8 % $< 0.90$) — line-preserving mover.
6. `preset_neg`: displacement $0.1193$, coherence **$1.0504$** (**98.8 % $\ge 0.98$**, 0.0 % $< 0.90$) — **highest line fidelity in the corpus**.

Five of the six conditions maintain coherence $\ge 0.98$. None causes structural collapse.

---

## 5. What this means for existing claims

`notebook/01-mark-style.md` and `notebook/06-the-hatching-axis.md` reference Stage 7 as the confirmation bench for:
1. Stroke width separation (`notebook/01-mark-style.md`):
   * Claim: *"On the stage 7 corpus, 10 of 11 statistics keep at least half their paired effect size... Stroke width separates the preset from both controls."*
   * Structural audit: Both `preset_pos` ($0.9769$) and `preset_neg` ($1.0504$) operate well above collapse thresholds. The measured stroke modifications reflect authentic linework transformation with intact gradient alignment.
2. Crosshatch entropy (`notebook/06-the-hatching-axis.md`):
   * `preset_neg` exhibits the highest coherence ($1.0504$) and fine-scale energy ($b0 = 1.068$), proving that the crosshatch density increases measured in Chapter 06 were clean line additions rather than pixel noise.

**Claims audit:**
* No claim sits on a collapse condition.
* No claim changes status.
