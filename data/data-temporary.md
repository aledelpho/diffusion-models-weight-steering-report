# Data-Temporary: Historical Measurements from README@c843d61

> **Source**: `git show c843d61:README.md`  
> **Extraction date**: 2026-09-23  
> **Purpose**: Exact verbatim transcription of all quantitative metrics, sample sizes, effect sizes, test statistics, and fractions reported in the monolithic README across sections §1.1–§1.7, §2.8–§2.9, and the original claims ledger.

---

## 1. Global Ledger & Scope Limits (Front Matter)

### Claim: `bounded-to-one-model-one-corner`
* **Source in old README**: Lines 307–313 (under *"Not established, and it is honest to say so here"*)
* **Exact Historical Numbers & Statements**:
  * **Model**: 1 model (Krea-2 DiT, 12.8 Billion parameters).
  * **Prompt population**: Exactly **40 prompts** total.
    * **24 prompts** in Experiment 1 (18 colour-pinned + 6 colour-free).
    * **16 prompts** in Confirmation round (§1.5 / §1.6).
  * **Lexical constraint**: **40 of 40 (100%)** contain `"bold ink outlines"` and `"hatched shadows"`.
  * **Opening token**: **39 of 40 (97.5%)** open on `"Western comics style"`.
  * **Framing**: All 40 are upper-body or close-up character portraits.
  * **Sampling regime**: Fixed at 9 steps, CFG 1.0, euler_ancestral / euler sampler.

### Claim: `exploratory-sizes-are-upper-bounds`
* **Source in old README**: Lines 334–338, 483–494, 762–775
* **Exact Historical Numbers & Statements**:
  * **General rule**: Three consecutive confirmation rounds came back between **1/3 and 1/2 (33% to 50%)** of the exploratory estimate.
  * **Case 1 — Chromatic coherence (§1.5)**:
    * Exploratory within-condition coherence (18 prompts): **+0.120** (raw unstandardised: **+0.080**, p = 1e-4).
    * Confirmation within-condition coherence (16 new prompts, 560 renders): **+0.057** (difference vs between-condition: **+0.035** vs null 95th percentile **+0.007**, p = 1e-4).
    * True effect halved on independent renders; power promised ~100% at 16 prompts based on exploratory numbers, actual power was ~50%.
  * **Case 2 — Hatching axis (§1.6)**:
    * Preset exploratory $\Delta$: **-0.484** $\rightarrow$ confirmation $\Delta$: **-0.370** (76.4% of exploratory).
    * Blockshuffle exploratory $\Delta$: **+0.274** $\rightarrow$ confirmation $\Delta$: **+0.288** (held within 5%).
    * Randsign exploratory $\Delta$: **-0.187** (81/90 pairs) $\rightarrow$ confirmation $\Delta$: **+0.020** (vanished / reversed, p = 0.67, 50/80 pairs).

---

## 2. Experiment 1: Mark Style & Geometry (§1.1 – §1.3)

### Claim: `preset-moves-mark-style`
* **Source in old README**: Lines 259–260, 411–475, 478–560
* **Exact Historical Numbers & Statements**:
  * **Payload size**: **53 KB** hand-calibrated weight perturbation.
  * **Model size**: **12.8 Billion** parameters (Krea-2 DiT).
  * **Frobenius displacement**: Matched at $D = \mathbf{0.0538}$ across all conditions.
  * **Corpus size**: Sections 1.1 to 1.4 rest on **1272 renders** across **24 prompts**.
    * Stage 5 exploratory: 10 prompts × 34 renders = **340 renders**.
    * Stage 7 extensions: 14 new prompts × conditions = **600 renders** (plus controls = 1272 renders total).
  * **Separation on PC1 (stroke continuity axis, pooled $n = 24$)**:
    * Preset vs Blockshuffle: $\Delta = \mathbf{-2.532}$, 95% CI $[-3.00, -2.07]$, $d_z = \mathbf{-2.30}$, $p_{\text{Holm}} < \mathbf{0.0001}$.
    * Preset vs Randsign: $\Delta = \mathbf{-2.117}$, 95% CI $[-2.69, -1.54]$, $d_z = \mathbf{-1.55}$, $p_{\text{Holm}} < \mathbf{0.0001}$.
    * Blockshuffle vs Randsign: $\Delta = \mathbf{+0.415}$, 95% CI $[-0.37, +1.20]$, not significant (controls do not separate from each other).
  * **Stroke width (pooled $n = 24$)**:
    * Preset vs Blockshuffle: $\Delta = \mathbf{+0.238}$, $p_{\text{Holm}} = \mathbf{0.016}$.
    * Preset vs Randsign: $\Delta = \mathbf{+0.394}$, $p_{\text{Holm}} = \mathbf{0.020}$.

### Claim: `clip-blind-to-mark-style`
* **Source in old README**: Lines 266–269, 478–485
* **Exact Historical Numbers & Statements**:
  * **Standard CLIP resolution**: **224×224** downsampled from native **1024×1280** (a $4.57\times$ linear downscale, $\approx 20.8\times$ pixel area reduction).
  * **Effect**: High-frequency stroke continuity, fine line etching, and shadow transitions are smoothed out at 224×224; CLIP cosine distance showed near-zero separation between preset and baseline across 24 prompts.
  * **Morphological measurement space**: Full-frame pixel luminance, contour continuity, and ink distance transforms flip the outcome to $p_{\text{Holm}} < 0.0001$.

### Claim: `direction-not-distance`
* **Source in old README**: Lines 261–265, 411–450, 530–545
* **Exact Historical Numbers & Statements**:
  * **Displacement match**: Total Frobenius displacement matched at $D = \mathbf{0.0538}$ for Preset (+), Preset (-), Blockshuffle, and Randsign.
  * **Control indistinguishability on mark geometry**:
    * Blockshuffle vs Randsign on PC1: $\Delta = \mathbf{+0.415}$ (95% CI $[-0.37, +1.20]$, n.s.), while Preset separates by $\mathbf{-2.532}$ and $\mathbf{-2.117}$ ($p < 0.0001$).
  * **Subspace divergence**:
    * Preset channels displacement into **mark geometry and contour length** (contour length $+0.760$, fragments $-0.560$).
    * Randsign channels displacement into **broad-band texture frequency and grain** (elevated LBP entropy, flatter FFT radial slope) while leaving contour geometry indistinguishable from Blockshuffle.

### Claim: `mark-style-generalises-prompts`
* **Source in old README**: Lines 270–272, 495–530
* **Exact Historical Numbers & Statements**:
  * **Generalisation family**: **24 prompts** total.
    * 18 colour-pinned prompts (skin, hair, eyes, rim light specified in detail).
    * 6 colour-free prompts (only keyword `"colored"` retained, palette chosen freely by model).
  * **Pre-declared criterion on colour-free sub-family ($n = 6$)**: Both preset contrasts on PC1 must exclude zero.
    * Preset vs Blockshuffle: $\Delta = \mathbf{-1.958}$, 95% CI $[-2.50, -1.42]$, $d_z = \mathbf{-3.82}$.
    * Preset vs Randsign: $\Delta = \mathbf{-3.815}$, 95% CI $[-5.67, -1.96]$, $d_z = \mathbf{-2.16}$.
    * Blockshuffle vs Randsign: $\Delta = \mathbf{-1.857}$, 95% CI $[-4.03, +0.31]$, $d_z = \mathbf{-0.90}$ (includes zero).
  * **Contour geometry on colour-free family**:
    * Contour length: $\mathbf{+0.760}$, 95% CI $[+0.37, +1.15]$ vs Blockshuffle.
    * Contour fragment count: $\mathbf{-0.560}$, 95% CI $[-0.82, -0.30]$ vs Blockshuffle.
  * **Loading vector alignment (absolute cosine $|\cos|$ of PC1 loading vectors)**:
    * Pinned vs Free: $|\cos| = \mathbf{0.837}$.
    * Pinned vs Pooled: $|\cos| = \mathbf{0.990}$.
    * Free vs Pooled: $|\cos| = \mathbf{0.906}$.
    * (In contrast, PC3 failed stability: $|\cos| = 0.379$ pinned vs free).

---

## 3. Colour Specificity & Generalisation Failure (§1.4)

### Claim: `colour-does-not-generalise`
* **Source in old README**: Lines 273–275, 562–610
* **Exact Historical Numbers & Statements**:
  * **Colour-pinned prompts ($n = 18$ / pooled $n = 24$)**:
    * Effective colour count: Preset reduces count vs Blockshuffle ($\mathbf{-0.376}$, $p_{\text{Holm}} \approx \mathbf{0.001}$) and vs Randsign ($\mathbf{-0.237}$, $p_{\text{Holm}} \approx \mathbf{0.001}$).
    * Top-4 palette concentration: Preset concentrates into top-4 clusters vs Blockshuffle ($\mathbf{+0.384}$) and vs Randsign ($\mathbf{+0.234}$).
  * **Colour-free prompts ($n = 6$)**:
    * Every palette contrast contains zero; effective colour count and cluster share show zero separation from controls.
  * **Directional sharing of LAB chroma shifts across subjects ($n = 6$)**:
    * Preset (+): palette shift $1.41$ ($1.31\times$ seed floor), direction shared across prompts: $\mathbf{-0.165}$, $p = \mathbf{0.81}$ (no shared direction).
    * Preset (-): palette shift $1.81$ ($1.69\times$ seed floor), direction shared across prompts: $\mathbf{-0.013}$, $p = \mathbf{0.25}$ (no shared direction).
    * Blockshuffle (+): palette shift $1.30$ ($1.21\times$ seed floor), direction shared: $\mathbf{-0.137}$, $p = \mathbf{0.75}$.
    * **Blockshuffle (-)**: palette shift $1.82$ ($1.70\times$ seed floor), direction shared: $\mathbf{+0.944}$, $p < \mathbf{0.0001}$ (imposes a single coherent global tint across nearly all subjects; null 95th percentile is $+0.334$).
    * Randsign ($\pm$): palette shift $1.53$–$1.57$ ($\approx 1.4\times$ seed floor), direction shared: $\mathbf{+0.38}$ to $\mathbf{+0.40}$, $p = \mathbf{0.03}$–$\mathbf{0.07}$.
  * **Sign asymmetry**: Negative direction of every condition moves palette roughly $\mathbf{1.7\times}$ more than its positive counterpart.

---

## 4. Multi-Feature Sharp Operator (§1.6, §1.7, §2.8–§2.9)

### Claim: `preset-is-a-sharp-operator`
* **Source in old README**: Lines 294–298, 700–740, 805–845, 925–945
* **Exact Historical Numbers & Statements**:
  * **Five concordant effects under `preset_pos` across two unrelated corpora**:
    1. **Darkens image (mean $L^*$)**: $\Delta = \mathbf{-3.30}$, concordance in **7 of 8 prompts** and **32 of 40 images** (§1.7 rally-car corpus, 8 styles × 5 seeds).
    2. **Desaturates palette (`colorfulness_hs`)**: $\Delta = \mathbf{-3.54}$, concordance in **7 of 8 prompts** and **32 of 40 images** (§1.7).
    3. **Adds fine surface grain (`lbp_entropy`)**: $\Delta = \mathbf{+0.07}$, concordance in **8 of 8 prompts** and **40 of 40 images (100% unanimous)** (§1.7).
    4. **Runs strokes parallel (crosshatch entropy $\Delta$)**: $\Delta = \mathbf{-0.370}$, $p = \mathbf{3.05 \times 10^{-5}}$ (exact permutation floor), Holm $p = \mathbf{9.2 \times 10^{-5}}$, concordance in **16 of 16 prompts** and **80 of 80 image pairs (100% unanimous)** (§1.6 confirmation corpus, 16 prompts × 5 seeds).
    5. **Activates unasked trait (lit headlights)**: Increases lit headlights presence from **5% to 82%** (concordance: lit in **31 of 38 renders** under preset vs **10 of 35** in baseline; in brightest third of corpus, stock model is 0/13 lit while preset is **7/13 lit**) (§2.8–§2.9).
  * **Contrasting behavior under `blockshuf_neg`**:
    * Lighter, smoother, far more saturated, and extinguishes lit headlights in **39 of 39 renders (0% presence)**.

---

## 5. Structural Mechanism Unresolved (Ledger / Not Established)

### Claim: `operative-structural-property-unknown`
* **Source in old README**: Lines 339–342 (*"Not established, and it is honest to say so here"*)
* **Exact Historical Numbers & Statements**:
  * **Statement of absence**: *"Which structural property of the perturbation is the operative one. Two points — block derangement works, sign scramble does not — separate structure from magnitude, but they do not identify what about the structure does the work."*
  * **Experimental coverage**: Never measured or isolated in any run. No ablation isolating specific transformer blocks, attention heads, or singular value spectral ranges was ever executed.
  * **Status**: Pure claim of absence (*"observed, never measured / unresolved by design"*).
