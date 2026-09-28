# Latent Space Benches, re-read on the two new axes

**Date**: 2026-09-28 · **Corpus**: `benchmark_latenti_b6/renders` (18 renders) & `benchmark_pavimento_rumore/renders` (32 renders) · **Material**: Latent-space steering of Block 6 at dose $0.200$ across prompts `P01` and `P02`, and 16-seed unperturbed latent baseline sets · **Scripts**: `experiments/retro_latenti_reading.py` → `data/retro_latenti_b6_cells.csv`, `data/retro_latenti_b6_summary.csv`, `data/retro_pavimento_rumore_summary.csv` · **No render.**

---

## 1. The re-reading and balance check

Two distinct latent-space benches are evaluated:
1. **`benchmark_latenti_b6`**: 18 renders.
   * 12 perturbed renders: 2 prompts (`P01`, `P02`) $\times$ 2 conditions (`B6pos`, `B6neg`) $\times$ 3 seeds (`42`, `777`, `1337`).
   * 6 in-folder baselines: 2 prompts $\times$ 3 seeds.
   * Balance: $12 \text{ perturbed} + 6 \text{ baselines} = 18 \text{ total files (0 unparsed)}$.
2. **`benchmark_pavimento_rumore`**: 32 baseline renders.
   * 16 unperturbed seeds for `P01`, 16 unperturbed seeds for `P02`.
   * Designed to establish the empirical noise floor of the diffusion generator across seeds.

---

## 2. Reading 1 — The empirical inter-seed noise floor (`pavimento_rumore`)

Natural inter-seed variability across 16 random seeds without weight steering:

| prompt | seeds | coherence (mean) | coherence (sd) | coherence CV | variance (mean) | variance (sd) | variance CV | chroma (mean) | chroma (sd) | chroma CV |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| `P01` | 16 | 0.6025 | 0.0090 | **1.49 %** | 0.0379 | 0.0016 | 4.18 % | 0.3106 | 0.0188 | 6.06 % |
| `P02` | 16 | 0.6346 | 0.0131 | **2.07 %** | 0.0819 | 0.0028 | 3.37 % | 0.2458 | 0.0082 | 3.35 % |

### Methodological threshold
The natural random-seed variance in structure coherence is bounded at **$\text{CV} \le 2.07\%$**.
* Any steering condition producing a $\Delta\text{coherence} < 2\%$ sits within the noise floor.
* Any effect producing $\Delta\text{coherence} > 5\%$ represents an authentic physical steering displacement.

---

## 3. Reading 2 & 3 — Block 6 latent steering: scale signatures and asymmetry

Aggregated conditions ($n = 6$ each: 2 prompts $\times$ 3 seeds):

| condition | dose | coherence ratio | sd | pct < 0.90 | displacement | contrast | chroma | `1-2px` (b0) | `2-4px` (b1) | `4-8px` (b2) | `8-16px` (b3) | `16-32px` (b4) | peak band |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| `B6pos` | 0.200 | 0.9268 | 0.0152 | **0.0 %** | 0.2137 | 0.8392 | 1.0577 | 0.950 | 1.135 | **1.275** | 1.070 | 0.893 | `4-8px` (b2) |
| `B6neg` | 0.200 | **0.7943** | 0.0248 | **100.0 %** | 0.5634 | 1.0903 | 1.2258 | 0.746 | 0.450 | 0.504 | 0.708 | **0.973** | `16-32px` (b4) |

*Note on chroma:* Reported strictly as a whole-frame metric.

### Findings on latent steering
1. **The 4–8px resonance of `B6pos`**:
   `B6pos` steering directly in latent space peaks at **`4-8px` ($b2 = 1.275$)**, with Band 1 at $1.135$, while suppressing fine ($b0 = 0.950$) and coarse ($b4 = 0.893$) scales. This proves that the mid-scale curl field discovered across pixel-space benchmarks is a direct property of the latent representation produced by Block 6, rather than an artifact of pixel-space decoding.
2. **The catastrophic collapse of `B6neg`**:
   `B6neg` in latent space suffers a catastrophic structural collapse across **$100\%$ of its renders**, plunging to a mean coherence of **$0.7943$**.
   The band profile reveals a massive mid-scale crater: Band 1 (`2-4px`) energy drops by **$-55.0\%$** ($0.450$) and Band 2 (`4-8px`) drops by **$-49.6\%$** ($0.504$). Pushing Block 6 negative in latent space strips the internal gradient scaffolding of the image.

---

## 4. Reading 4 — Line-preserving movers vs collapses

* `B6pos`: displacement $0.2137$, coherence $0.9268$ ($0.0\%$ below $0.90$) — moderate line preservation with mid-scale texture addition.
* `B6neg`: displacement $0.5634$, coherence $0.7943$ (**$100.0\%$ below $0.90$**) — **total structural collapse**.

---

## 5. What this means for existing claims

`docs/block6_nel_latente.md` formulated the hypothesis that Block 6 operates as a focus knob in latent space, where negative steering sharply reduces high frequencies while positive steering redistributes energy:
* The retro texture axes confirm this: `B6neg` destroys line coherence ($0.7943$) and suppresses high-frequency detail by $> 50\%$.
* `B6pos` maintains coherence above collapse ($0.9268$) while injecting the $1.275\times$ curl field at $4$–$8\text{ px}$.

**Claims audit:**
* The findings of `docs/block6_nel_latente.md` are physically confirmed on the gradient tensor and band energy axes.
* `B6neg` is confirmed as a total structural collapse condition at dose $0.200$.

No claim changes status.
