# Report — Damage or Style? The Multi-Image Judge on `benchmark_mappa`

- **Governed by:** [`docs/prereg_damage_or_style.md`](prereg_damage_or_style.md) (frozen before any call, Amendment 01).
- **Runbook:** [`docs/RUNBOOK_2026-09-27_damage_or_style.md`](RUNBOOK_2026-09-27_damage_or_style.md).
- **Primary Data Sources:**
  - [`data/damage_style_gate.csv`](../data/damage_style_gate.csv) (54 gate calls across all 9 baselines)
  - [`data/damage_style_report.txt`](../data/damage_style_report.txt) (analyser output)
- **Status:** **STUDY TERMINATED AT STEP 1 (GATE FAILED)**. Steps 2–4 were not executed.

---

## 1. Executive Summary & Outcome

The pre-registration established a blocking multi-image gate (§4) to test whether `qwen3.8:27b` can reliably evaluate two full-resolution images presented in the same request as distinct entities. The gate employed three perceptual probes with deterministic, unambiguous ground truth (color saturation, Gaussian blur, and Gaussian noise) applied directly to all 9 baselines across both presentation orders (`hi_first` vs `lo_first`), totaling 54 calls.

**Outcome:** The judge **FAILED** all three probes:
- **Saturation:** 11/18 correct (61.1%), 6/18 order agreement (33.3%). Thresholds: $\ge 17$ correct, $\ge 15$ agreement. **FAIL**.
- **Sharpness:** 9/18 correct (50.0%), 0/18 order agreement (0.0%). Thresholds: $\ge 17$ correct, $\ge 15$ agreement. **FAIL**.
- **Degradation:** 8/18 correct (44.4%), 0/18 order agreement (0.0%). Thresholds: $\ge 17$ correct, $\ge 15$ agreement. **FAIL**.
- **Overall first-position share:** 0.685 (37/54 answers selected "A"), falling within the wide prior bound of $[0.30, 0.70]$.

Under the pre-registered protocol (§4) and runbook (§3), a gate failure is a **terminal result**. Because the failure was not isolated to the degradation probe but was catastrophic across all perceptual tasks, **Arm B could not proceed**. The run was halted immediately without executing Step 2 (the 468-call run), Step 3 (test–retest), or Step 4 (quadrant analysis).

---

## 2. Gate Results Breakdown

All numbers in this section are extracted directly from [`data/damage_style_gate.csv`](../data/damage_style_gate.csv) and [`data/damage_style_report.txt`](../data/damage_style_report.txt):

| Probe | Manipulation | Correct Calls | Order Agreement | Target (Correct / Agree) | First-Position (A) Share | Verdict |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **saturation** | Original vs 50% Color saturation | 11 / 18 (61.1%) | 6 / 18 (33.3%) | 17 / 18 and 15 / 18 | 14 / 18 (77.8%) | **FAIL** |
| **sharpness** | Original vs Gaussian blur ($\sigma=2.0$) | 9 / 18 (50.0%) | 0 / 18 (0.0%) | 17 / 18 and 15 / 18 | 18 / 18 (100.0%) | **FAIL** |
| **degradation** | Gaussian noise $\sigma=16$ vs $\sigma=4$ | 8 / 18 (44.4%) | 0 / 18 (0.0%) | 17 / 18 and 15 / 18 | 5 / 18 (27.8%) | **FAIL** |
| **Overall** | *Pooled over 54 calls* | **28 / 54 (51.9%)** | **6 / 54 (11.1%)** | — | **37 / 54 (68.5%)** | **FAIL** |

### Perceptual Analysis of the Failure

1. **Sharpness (Complete Position Bias):**
   When asked *"Which of these two images is sharper and better in focus?"*, the model selected **"A" in 18 out of 18 calls (100.0%)**. In order `hi_first`, where the sharp unblurred image was Image A, it scored "OK" (9/9). In order `lo_first`, where the sharp image was Image B, it answered "A" anyway (0/9). This produces an order-agreement rate of **0/18 (0.0%)** and accuracy equal to coin-flipping (50.0%). The model completely ignored the severe Gaussian blur ($\sigma=2.0$).

2. **Degradation (Inability to Track Noise):**
   When asked *"Which of these two images has more visible defects, noise or artefacts?"*, the model achieved an accuracy of only 8/18 (44.4%, below random chance) and **0/18 order agreement**. In no baseline pair did the model consistently identify the noisier image ($\sigma=16$ vs $\sigma=4$) across both presentation permutations.

3. **Saturation (Partial Sensitivity, Severe Order Fragility):**
   Color saturation was the only probe where the model showed any above-chance discrimination (11/18 correct, 61.1%), but only 3 out of 9 baseline pairs (6/18) were answered consistently across orders, falling far short of the required $\ge 15/18$ threshold.

---

## 3. Protocol Decision on Arm B

The runbook noted a single contingency (§3):
> *"If only the degradation probe fails, Arm A is void and Arm B may still be run — Arm B never asks the judge to rank quality, only to match a treatment."*

Because **all three probes failed**—including the basic low-level contrasts of sharpness and saturation—the prerequisite capability of the judge to compare multi-image inputs independently of display order is entirely absent. Running Arm B under these conditions would yield uninterpretable noise dominated by position artifacts. In strict compliance with pre-registration §4 and runbook §3, Arm B was **not run**.

---

## 4. Status of Downstream Steps & Hypotheses

- **Step 2 (The 468-call run):** **Skipped** (blocked by Gate failure). No data collected in `data/damage_style_answers.csv`.
- **Step 3 (Determinism re-test):** **Skipped** (no run data to re-test).
- **Step 4 (Quadrant & Hypotheses D1–D6):**
  - **D1–D6:** Unmeasured / Voided.
  - **Quadrant Table:** Unmeasured / Voided.
- **Nulls & Position Bias of Arms A/B:** Unmeasured.

---

## 5. Limitations

1. **Instrument Boundary:**
   This failure characterizes `qwen3.8:27b` under zero-shot multi-image API inference (`/api/generate` with two native $1024 \times 1280$ images). It confirms that the model cannot serve as an automated judge for pairwise image quality or style matching at this resolution without fine-tuning, specialized prompts, or patch embeddings.
2. **Epistemic Scope:**
   Every conclusion here is strictly about **what this judge can report**, not about what the steered images *are*. The question of whether high-dose block steering produces legitimate aesthetic style or degenerative rendering damage remains open and cannot be answered by this instrument.
3. **Pre-registration Integrity:**
   No thresholds were adjusted, no prompts were modified to force a pass, and no alternative models were opportunistically substituted. The gate worked as designed: preventing hundreds of ungrounded API calls.
