# Stage 9 (Style Direction & Amplitude Ladder), re-read on the two new axes

**Date**: 2026-09-28 · **Corpus**: `benchmark_stage9/renders` (300 renders) · **Material**: 8 style families (`S1_photo` .. `S8_charcoal`) testing 3 steering conditions across two amplitudes ($1.0\times$ and $2.0\times$) across 5 seeds, plus 20 renders of `chaos_edges_v2` on 4 $I$-prompts · **Scripts**: `experiments/retro_stage9_reading.py` → `data/retro_stage9_cells.csv`, `data/retro_stage9_summary.csv` · **No render.**

---

## 1. Baseline verification and the Pitfall 69 resolution

Stage 9 contains 300 renders partitioned into two distinct subsets:
1. **Part 1 (Style variants, $S1$ to $S8$)**: 280 renders.
   * 40 baselines: 8 styles $\times$ 5 seeds (`42`, `777`, `1337`, `9999`, `4242145`).
   * 240 perturbed renders: 8 styles $\times$ 6 conditions $\times$ 5 seeds (`preset_pos_1x`, `preset_pos_2x`, `blockshuf_neg_1x`, `blockshuf_neg_2x`, `rand_pos_1x`, `rand_pos_2x`).
   * PNG metadata inspection confirms the baseline prompts and sampler settings match the perturbed renders identically.
2. **Part 2 (Chaos Edges V2, $I06$, $I07$, $I20$, $I24$)**: 20 renders (4 prompts $\times$ 5 seeds).
   * **Pitfall 69 inspection**: It was hypothesized that their baselines lived in `benchmark_stage7a/renders`. Direct PNG metadata extraction revealed that prompt texts differ completely:
     * `I06` in `stage7a`: *"A human man with cropped brown hair and stubble. armor made of steel, He wears a chainmail coif..."*
     * `I06` in `stage9`: *"A lithe female elf ranger, sharp cheekbones, long silver hair braided with green vines, piercing amber eyes... teal rim light..."*
   * Following the strict protocol of [`HANDOVER_2026-09-28_retro_axes.md`](HANDOVER_2026-09-28_retro_axes.md), **these files have no matching baseline in the project**. Their ratio columns are strictly left empty in `data/retro_stage9_cells.csv`.

### Arithmetic balance equation
$$\text{240 matched S-perturbed} + \text{40 S-baselines} + \text{20 un-baselined I-renders} = \text{300 total files in stage9 (0 unparsed)}$$

---

## 2. Reading 1 — Coherence behaviour across the 8 style families

Aggregated across all 6 conditions ($n = 30$ per style):

| style | cells | coherence ratio (mean) | sd | pct < 0.90 | pct $\ge$ 0.98 |
|---|--:|--:|--:|--:|--:|
| `S1_photo` | 30 | 1.0102 | 0.1338 | 16.7 % | 53.3 % |
| `S2_watercolor` | 30 | 0.9362 | 0.1190 | **36.7 %** | 43.3 % |
| `S3_lowpoly` | 30 | 0.9636 | 0.0789 | 20.0 % | 43.3 % |
| `S4_claymation` | 30 | 0.9846 | 0.0568 | 16.7 % | 56.7 % |
| `S5_ukiyoe` | 30 | 0.9564 | 0.0695 | 16.7 % | 46.7 % |
| `S6_pixel` | 30 | **1.0144** | 0.0638 | 10.0 % | **80.0 %** |
| `S7_glass` | 30 | 0.9884 | 0.1089 | 16.7 % | 56.7 % |
| `S8_charcoal` | 30 | **0.8979** | 0.1969 | **33.3 %** | 56.7 % |

The style sensitivity pattern discovered on the atlas is replicated here:
* Line-bearing and medium-sensitive styles (`S8_charcoal` mean $0.8979$, `S2_watercolor` mean $0.9362$) exhibit severe structural vulnerability, with more than a third of renders dropping below $0.90$.
* `S6_pixel` and `S4_claymation` exhibit low variance and high stability ($80\%$ of pixel renders maintain $\ge 0.98$).

---

## 3. Reading 2 — The catastrophic cliff of the double-dose ladder

Aggregated conditions ($n = 40$ each, pooled across 8 styles and 5 seeds):

| condition | coherence ratio | sd | pct < 0.90 | pct $\ge$ 0.98 | displacement | contrast | chroma (whole frame) | `1-2px` (b0) | `2-4px` (b1) | `4-8px` (b2) | `8-16px` (b3) | `16-32px` (b4) | peak band |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| `blockshuf_neg_1x` | 1.0260 | 0.0782 | 5.0 % | **82.5 %** | 0.1919 | 1.1177 | 1.0680 | 1.119 | 1.084 | 1.091 | 1.151 | **1.220** | `16-32px` |
| `blockshuf_neg_2x` | **1.0422** | 0.0894 | 10.0 % | 75.0 % | 0.4724 | 1.5270 | 1.3054 | 1.362 | 1.277 | 1.350 | 1.615 | **1.922** | `16-32px` |
| `preset_pos_1x` | 0.9199 | 0.0912 | 25.0 % | 25.0 % | 0.2608 | 0.9759 | 1.0904 | 0.834 | 0.701 | 0.767 | 0.883 | **0.979** | `16-32px` |
| `preset_pos_2x` | **0.8046** | 0.1171 | **82.5 %** | **0.0 %** | 0.5483 | 0.9554 | 1.1614 | 0.715 | 0.458 | 0.535 | 0.718 | **0.892** | `16-32px` |
| `rand_pos_1x` | 0.9991 | 0.0463 | 2.5 % | 67.5 % | 0.1668 | 0.9928 | 0.9842 | **1.085** | 0.953 | 0.948 | 0.977 | 1.009 | `1-2px` |
| `rand_pos_2x` | 1.0220 | 0.0543 | **0.0 %** | 77.5 % | 0.2430 | 1.1269 | 1.1026 | 1.199 | 0.925 | 1.016 | 1.120 | **1.222** | `16-32px` |

*Note on chroma:* Reported strictly as a whole-frame metric.

### Rate of coherence loss per unit of log-dose:
$$\Delta\ln(\text{dose}) = \ln(2.0 / 1.0) = 0.6931$$

* **`preset_pos` ($1.0 \to 2.0$)**:
  * Coherence drops from $0.9199$ to **$0.8046$** ($\Delta\text{coherence} = -0.1153$).
  * Rate: $\frac{\Delta\text{coherence}}{\Delta\ln(\text{dose})} = \mathbf{-0.1663}$.
  * The fraction of cells below $0.90$ surges from $25.0\%$ to **$82.5\%$**; exactly **$0.0\%$** of cells maintain $\ge 0.98$.
  * **Conclusion**: Doubling the preset dose drives the model over a catastrophic cliff across all styles.
* **`blockshuf_neg` ($1.0 \to 2.0$)**:
  * Coherence moves from $1.0260$ to $1.0422$ ($\Delta\text{coherence} = +0.0162$, rate $= +0.0234$).
  * Displacement grows from $0.1919$ to $0.4724$, and contrast increases by $+52.7\%$. The line is preserved and intensified.
* **`rand_pos` ($1.0 \to 2.0$)**:
  * Coherence moves from $0.9991$ to $1.0220$ ($\Delta\text{coherence} = +0.0229$, rate $= +0.0331$), with $0\%$ below $0.90$.

---

## 4. Reading 3 — Scale signatures

* **`preset_pos_2x`**: severe hollowing out of fine and medium detail.
  * Band 1 (`2-4px`) energy drops to **$0.458$** ($-54.2\%$).
  * Band 2 (`4-8px`) drops to **$0.535$** ($-46.5\%$).
  * Coarse bands remain relatively intact ($b4 = 0.892$). This massive mid-scale hole is the physical mechanism of the structural collapse: strokes lose internal continuity and erode into amorphous patches.
* **`blockshuf_neg_2x`**: massive coarse-scale energy inflation.
  * Band 4 (`16-32px`) surges to **$1.922$** ($+92.2\%$), with Band 3 at $1.615$. High-contrast macro forms dominate the frame without eroding fine contour coherence ($b0 = 1.362$).

---

## 5. Reading 4 — Line-preserving movers vs collapses

Ranked by displacement:
1. `preset_pos_2x`: displacement $0.5483$, coherence $0.8046$ (**82.5 % $< 0.90$**, 0 % $\ge 0.98$) — **catastrophic collapse**.
2. `blockshuf_neg_2x`: displacement $0.4724$, coherence **$1.0422$** (75.0 % $\ge 0.98$) — **massive line-preserving mover**.
3. `preset_pos_1x`: displacement $0.2608$, coherence $0.9199$ (25.0 % $< 0.90$) — partial line degradation.
4. `rand_pos_2x`: displacement $0.2430$, coherence **$1.0220$** (77.5 % $\ge 0.98$) — clean line-preserving mover.
5. `blockshuf_neg_1x`: displacement $0.1919$, coherence **$1.0260$** (82.5 % $\ge 0.98$) — line-preserving mover.
6. `rand_pos_1x`: displacement $0.1668$, coherence $0.9991$ (67.5 % $\ge 0.98$) — line-preserving mover.

---

## 6. What this means for existing claims

`notebook/09-style-direction.md` contains the claim:
* `double-dose-arm-is-degraded` (Status: `holds`):
  *"The only amplitude that produced significant cells sits outside the quality range declared for it in advance, in three quarters of its cells... 18 cells of 24 at the double amplitude fall outside it on edge density or on texture entropy."*

**New analytical verification**:
The retro-reading on the structure tensor coherence axis provides the exact physical validation for this claim:
* At double dose ($2.0\times$), `preset_pos_2x` suffers an $82.5\%$ collapse rate (coherence $< 0.90$), with a mean coherence of $0.8046$ and a rate of degradation of $-0.1663 / \Delta\log(\text{dose})$.
* In contrast, the control arms (`blockshuf_neg_2x` and `rand_pos_2x`) at double dose retain coherence $> 1.02$.
* The original claim that the double-dose arm was degraded is not an artifact of edge-density heuristics: it is a genuine physical collapse of gradient coherence.

**Claims audit:**
* `double-dose-arm-is-degraded`: verified with structural gradient mathematics.
* `style-does-not-steer-direction`: consistent with findings; $1\times$ preset dose was already causing mild degradation ($25\%$ below $0.90$) on non-comic styles.

No claim changes status.
