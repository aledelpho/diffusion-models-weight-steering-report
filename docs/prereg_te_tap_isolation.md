# Pre-registration C79 — 12-tap isolation: does an early/mid text-encoder edit act through the early/mid taps (`L02–L26`) or through the intra-LLM cascade into the late taps (`L29–L35`)?

Written 2026-10-17, **before any C79 render or label.**

* Code: `experiments/te_tap_isolation.py` (`--plan`, `--encoder`, `--queue`, `--gate`, `--count`, `--selftest`).
* Directive: `docs/directives_antigravity_te_tap_isolation.md` (76 renders: 4 gate + 72 main).
* Node: `Krea2ConditioningPush` (`tools/comfyui_krea2_condpush`, `variant="taps"`).

---

## 1. Why this experiment is needed

In `results/30-the-text-encoder.md` (`C67`–`C75`), three facts stand in tension:

1. **The conditioning interface is multi-tap:** `Krea-2` does not read only the final layer of `Qwen3-VL-4B`. It extracts **12 intermediate hidden-state taps** at layers `TAPS = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]` (indices `0..11`, each passed through the final `RMSNorm`) and fuses them inside `txtfusion` / `txtmlp`.
2. **A causal paradox across depth (`C72`, `C74`, `C75`):**
   * Doubling **`L28 MLP` (`L28_mlp_p1.00`)** produces the **largest conditioning displacement** on the taps it reaches (`0.869` relative change), yet **never switches the comic genre (`0/6` strips in C74)** and **preserves character traits (`0.97` retention in C75)**.
   * Doubling **`L06 MLP` (`L06_mlp_p1.00`)** (`0.548` relative change) or **`L14 MLP` (`L14_mlp_p1.00`)** (`0.592` relative change) produces a **smaller** conditioning displacement, yet **switches the genre** (`L06` $\to$ 3D/photo, `L14` $\to$ cartoon), **erases asked character traits (`0.48` and `0.63` retention in C75)**, and **lightens dark/non-human skin (`52/53` cases in C75)**.
3. **Exact tap geometry:**
   * Layer 28 sits between **Tap 8 (`L26`)** and **Tap 9 (`L29`)**. Therefore, `L28_mlp_p1.00` modifies **only Taps `9, 10, 11` (`L29, L32, L35`)**; its push on Taps `0..8` (`L02..L26`) is identically zero.
   * By contrast, `L06_mlp_p1.00` modifies **Taps `2..8` (`L08..L26`) AND Taps `9..11` (`L29..L35`)**, and `L14_mlp_p1.00` modifies **Taps `4..8` (`L14..L26`) AND Taps `9..11` (`L29..L35`)**.

This leaves two competing mechanistic hypotheses that cannot be separated without isolating the taps:

* **H1 — Intra-LLM Cascade into the Late Taps (`taps_late` = `9,10,11` drives the effect):**
  Perturbing `L06` or `L14` corrupts self-attention routing and feature assembly inside subsequent LLM layers (`L07`–`L35`), so by the time the signal reaches the late taps (`L29, L32, L35`), specific trait bindings are already lost. Under `H1`, injecting `L06`/`L14`'s push **only into Taps `9, 10, 11`** (holding Taps `0..8` at clean baseline) reproduces the trait loss and style switch, even though those are the exact same 3 tap slots where `L28_mlp_p1.00` is harmless.
* **H2 — Direct Multi-Tap Reading by `txtfusion` (`taps_early_mid` = `0..8` drives the effect):**
  `Krea-2`'s `txtfusion` reads character traits and style heavily from the early/mid taps (`L08..L26`, Taps `2..8`) and gives little weight to Taps `9, 10, 11` (`L29..L35`). Under `H2`, `L28_mlp_p1.00` is harmless simply because it only reaches Taps `9, 10, 11`; consequently, restricting `L06`/`L14`'s push to **Taps `0..8`** (`taps_early_mid`) reproduces the trait loss and style switch, whereas restricting `L06`/`L14`'s push to **Taps `9, 10, 11`** (`taps_late`) leaves the portrait nearly intact (like `L28`).

---

## 2. Experimental design (76 renders)

### Material
* **Characters (`3`):** the three C74/C75 portrait prompts (`D1_dwarf_paladin`, `E2_elf_rogue`, `O4_halforc_fighter`).
* **Seeds (`4`):** `2645751`, `3316624` (the two C74/C75 main seeds, where full-edit renders already exist in `benchmark_te_dose`) plus `3605551`, `4123105` (two held-out seeds whose plain baselines already exist in `benchmark_portraits/phase_c`).
* **Edits (`2`):** `L06_mlp_p1.00` (`layers.6.mlp.{gate,up,down}_proj.weight` at `+1.00`) and `L14_mlp_p1.00` (`layers.14.mlp.{gate,up,down}_proj.weight` at `+1.00`).
* **Tap-isolation conditions (`3` per edit):** Let $P = C_{\text{edit}} - C_{\text{base}}$ be the live conditioning difference across the 12 taps (`0..11`):
  1. **`taps_local`** (the 2 taps immediately following the edited layer):
     * For `L06_mlp_p1.00`: `taps = "2,3"` (`L08, L11`).
     * For `L14_mlp_p1.00`: `taps = "4,5"` (`L14, L17`).
  2. **`taps_early_mid`** (all taps strictly before `L28`):
     * `taps = "0,1,2,3,4,5,6,7,8"` (`L02..L26`; for `L06` this is active on `2..8`, for `L14` on `4..8`).
  3. **`taps_late`** (only the 3 taps after `L28`, i.e. the exact tap support of `L28_mlp_p1.00`):
     * `taps = "9,10,11"` (`L29, L32, L35`).

Notice the **exact algebraic partition**:
$$P_{\text{taps\_early\_mid}} + P_{\text{taps\_late}} = P_{\text{real}}$$
Every token and channel of the full perturbation belongs to either `taps_early_mid` (`0..8`) or `taps_late` (`9..11`), with zero overlap.

* **Main render count:** $3 \text{ characters} \times 4 \text{ seeds} \times 2 \text{ edits} \times 3 \text{ tap conditions} = \mathbf{72\text{ renders}}$.

### Bit-exact reproduction & partition gates (`4` renders, `block = "gate"`)
All four gate renders are run on `D1_dwarf_paladin`, seed `2645751`, before queuing the 72 main renders:
1. **`gate_zero`** (`variant="zero"`): must be pixel-identical (`max abs diff = 0`) to `benchmark_portraits/phase_c/D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png`.
2. **`gate_real_L06`** (`variant="real"`, `L06_mlp_p1.00`): must be pixel-identical (`max abs diff = 0`) to `benchmark_te_dose/D1_dwarf_paladin_L06_mlp_p1.00_krea2_seed2645751_00001_.png`.
3. **`gate_all12_L06`** (`variant="taps"`, `taps="0,1,2,3,4,5,6,7,8,9,10,11"`, `L06_mlp_p1.00`): exercises the new `variant="taps"` code path across all 12 taps; must be pixel-identical (`max abs diff = 0`) to the same C74 `L06_mlp_p1.00` render.
4. **`gate_late_L28`** (`variant="taps"`, `taps="9,10,11"`, `L28_mlp_p1.00`): restricts `L28_mlp_p1.00` to Taps `9, 10, 11`; must be pixel-identical (`max abs diff = 0`) to `benchmark_te_dose/D1_dwarf_paladin_L28_mlp_p1.00_krea2_seed2645751_00001_.png`, proving that `L28` has zero effect on Taps `0..8`.

If any of the four gate renders has `max abs diff > 0`, execution stops immediately.

---

## 3. Pre-registered encoder-side & image-side measures and decision rules

### A. Encoder-side partition audit (0 renders, `--encoder`)
Computed from the C67/C68 `.npz` files (or direct encoder pass) across the 3 characters (`D1`, `E2`, `O4`) plus `txtfusion.projector.weight` (`[1, 12]` or per-tap block norms in `krea2_turbo_bf16.safetensors`):
* For `L06_mlp_p1.00`, `L14_mlp_p1.00`, and `L28_mlp_p1.00`, report the exact Frobenius norm $\|P_{\text{tap}}\|_F$ and relative norm $\|P_{\text{tap}}\|_F / \|B_{\text{tap}}\|_F$ at each of the 12 taps, and the share of energy in `taps_local`, `taps_early_mid` (`0..8`), and `taps_late` (`9..11`).
* Inspect `txtfusion` weights in `krea2_turbo_bf16.safetensors` to measure the linear norm / gain assigned by Krea-2's adapter to each of the 12 tap slots (`0..11`).

### B. Image-side automatic distance partition (`--analyze`, on seeds `2645751` and `3316624` where full edits exist, and across all 4 seeds against baseline)
For each `(character, seed, edit)` cell, let $D_{\text{base}}(X)$ be the perceptual distance (`1 - cos` in DINOv2-large and CSD-ViT-L, plus pixel RMS / LPIPS) between condition $X$ and the plain `baseline`, and $D_{\text{real}}(X)$ be the distance between condition $X$ and the full edit (`real` from `benchmark_te_dose` on seeds `2645751` and `3316624`).

Define the **Late-vs-Early Dominance Index** per cell:
$$\Delta_{\text{early-late}} = D_{\text{base}}(\text{taps\_early\_mid}) - D_{\text{base}}(\text{taps\_late})$$
and the **Full-Edit Proximity Index** on seeds `2645751` and `3316624`:
$$\Pi_{\text{early-late}} = D_{\text{real}}(\text{taps\_late}) - D_{\text{real}}(\text{taps\_early\_mid})$$
(positive when `taps_early_mid` is closer to the full edit `real` than `taps_late` is).

### C. Blind human trait & skin-tone test (same protocol as C75 Amendment 1/4)
On the 72 C79 renders + 12 plain baselines + 12 full-edit C74 renders + 12 repeats (108 items total, shuffled blind):
* Measure **Trait Retention $R$** (share of baseline-present traits retained) and **Skin Lightening rate**.
* Let $\Delta R_{\text{early\_mid}} = 1 - \overline{R}(\text{taps\_early\_mid})$ and $\Delta R_{\text{late}} = 1 - \overline{R}(\text{taps\_late})$ be the mean trait loss induced by the two complementary tap subsets.

### Decision rules (fixed now)
1. **Primary rule (H2 vs H1 on Trait Loss):**
   * **H2 supported (`early/mid taps` drive the trait loss):** $\Delta R_{\text{early\_mid}} - \Delta R_{\text{late}} \ge +0.15$ **and** `taps_early_mid` loses more traits than `taps_late` in at least `5 of 6` `(character, edit)` pairs.
   * **H1 supported (`late-tap cascade` drives the trait loss):** $\Delta R_{\text{late}} - \Delta R_{\text{early\_mid}} \ge +0.15$ **and** `taps_late` loses more traits than `taps_early_mid` in at least `5 of 6` `(character, edit)` pairs.
   * **Joint / Distributed across both tap groups:** $|\Delta R_{\text{early\_mid}} - \Delta R_{\text{late}}| < 0.15$, with both causing $\ge 0.10$ trait loss, or neither causing $\ge 0.15$ trait loss alone (super-additive interaction requiring all taps together).
2. **Secondary rule (Local 2-Tap Sufficiency, `taps_local` vs `taps_early_mid`):**
   * If $\Delta R_{\text{local}} / \Delta R_{\text{early\_mid}} \ge 0.70$, the two taps immediately following the edited layer are sufficient to cause the majority of the early/mid damage.
   * If $\le 0.30$, the damage requires accumulation across multiple intermediate taps (`L08..L26`).
3. **Concordance with automatic distances (`DINOv2-large` and `CSD-ViT-L`):**
   * Report the sign agreement of $\Delta_{\text{early-late}}$ and $\Pi_{\text{early-late}}$ across all 24 `(character, seed, edit)` cells (`>= 18/24` required for a unidirectional automatic verdict).

---

## Amendment 1 — 2026-10-18, by Claude, after the renders and before any label

**What the taps are.** The design above says each tap is a layer's output "passed through the final `RMSNorm`".
ComfyUI's Krea-2 encoder (and its review in other codebases) captures each tap **at the start of layer k, before
layer k runs, without normalisation**: tap "L14" is the residual stream entering layer 14, i.e. the output of layers
0–13. Each tap is normalised later, inside `txtfusion`'s layerwise blocks. Argon reported this on 2026-10-17 after
reading the source; the encoder audit agrees.

**Consequences for the design.**

* **L14's `taps_local` is one tap, not two.** With taps read before the layer, an edit to layer 14 first appears in
  tap 5 (L17). The push of `L14_mlp_p1.00` on tap 4 is exactly 0 (`data/te_tap_isolation_encoder_by_tap.csv`), so
  `taps_local = "4,5"` acts on tap 5 only. For L06, `taps_local = "2,3"` (L08, L11) is correct.
* **The `early_mid` / `late` partition is unchanged**: L06 and L14 reach taps 2–8 / 5–8 and 9–11; L28 reaches only
  taps 9–11 (gate 4, max abs diff 0). The rules are unchanged.
* **The secondary rule (local sufficiency) is reported separately for L06 and L14**, with L14's "local" read as one
  tap.

**The primary rule needs the blind labels of section C.** The automatic distances (`--analyze`) feed rule 3 only.

**Record.** This pre-registration was not committed before the renders (file time 10:29, first render 11:26); its
precedence rests on file times.

## Labelling page — 2026-10-18, before any label

`experiments/te_tap_isolation_page.py`, key `data/te_tap_key.csv`, order `data/te_tap_schedule.csv` (RNG seed 7979).
96 pictures (72 C79, 12 baselines, 12 full edits) + 4 repeats per character (one of them a baseline) = 108 showings,
as section C asks. Questions: the C75 asked and common traits of `data/te_traits_questions.csv` (all worded in the
positive), skin against the same-seed baseline (same / lighter / darker), same person. One question at a time over
all pictures of a character; condition, edit and seed never shown. A repeat returns at least 12 pictures after its
first showing (C75 used 30, impossible with 32 pictures per character). Labeller: Alessandro. Retention R and the
rules of section C are computed exactly as in C75's tally.
