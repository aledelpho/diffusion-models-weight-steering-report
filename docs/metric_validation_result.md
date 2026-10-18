# Result C66 — Which automatic measures reproduce the eye on text-encoder edits?

Date: 2026-10-17
Pre-registration: `docs/prereg_metric_validation.md`
Data: `data/metric_val_images.csv` (657 rows), `data/metric_val_emb.npz` (CSD `657×768`, DINOv2 `657×1024`), `data/metric_val_genre.csv` (657 rows), `data/metric_val_vqa.csv` (153 rows), `data/metric_val_tests.csv` (9 rows)
Script: `experiments/metric_validation.py`

## 1. Pre-registered calibration tests (`data/metric_val_tests.csv`)

| Test | Measure | n | Value | Rule for *validated* | Verdict |
|---|---|---:|---|---|---|
| **T1** | Per sheet, median cosine between the 7 characters' CSD change vectors vs "same direction" (`yes` / `partly` / `no`) | 34 | `ρ = -0.482` (`p = 0.0039`), `AUC(yes vs no) = 0.056` | `ρ ≥ 0.40` and `AUC ≥ 0.75` | **not validated** |
| **T2** | Per character, cosine of its CSD change with the mean change of the other six vs `follows` / `another way` | 157+81 | `AUC = 0.383` | `AUC ≥ 0.70` | **not validated** |
| **T3 (CSD)** | Per edit, CSD dispersion across the 5 word orders (minus originals) vs 1–5 scores | 20 | `ρ = 0.844` (`p = 0.0`) | `ρ ≥ 0.60` | **validated** |
| **T3 (DINOv2)** | Per edit, DINOv2 dispersion across the 5 word orders vs 1–5 scores | 20 | `ρ = 0.898` (`p = 0.0`) | reported | **reported** |
| **T4** | CSD distance to baseline, style `changed` vs `unchanged` (elf) | 55+97 | `AUC(CSD) = 0.796`, `AUC(DINOv2) = 0.815` | `AUC(CSD) ≥ 0.70` and `> AUC(DINOv2)` | **not validated** |
| **T5** | DINOv2 distance to baseline vs how much it changed (`none` … `strong`, elf) | 150 | `ρ = 0.661` (`p = 0.0`, `ρ_CSD = 0.654`) | `ρ ≥ 0.50` | **validated** |
| **T6** | CLIP ViT-L/14 zero-shot top-1 genre vs genre named in the notes | 145 | `accuracy = 0.593`, `majority = 0.317` | `accuracy ≥ 0.60` and `≥ majority + 0.15 (0.467)` | **not validated** |
| **T7** | `1 - VQAScore` (`clip-flant5-xl`) of the trait, lost vs not (elf) | 78 | `pooled AUC = 0.885` | `pooled AUC ≥ 0.80` | **validated** |
| **D** | CSD discrimination gap: mean cosine within the same named genre minus across genres | 145 | `gap = +0.2070` | reported | **reported** |

### T7 breakdown by trait (`data/metric_val_tests.csv`)

| Trait | Question (`clip-flant5-xl`) | Positives (`n`) | Within-trait AUC |
|---|---|---:|---:|
| `elf` | `"pointed elf ears"` | 4 | `1.000` |
| `fur` | `"a fur collar"` | 11 | `0.995` |
| `antlers` | `"a small pair of pale antlers"` | 17 | `0.985` |
| `pauldron` | `"a gold wood-textured pauldron"` | 14 | `0.885` |
| `tan` | `"tan sun-kissed skin"` | 7 | `0.830` |
| `eyepatch` | `"an eyepatch over one eye"` | 14 | `0.824` |
| `gauntlet` | `"a heavy silver gauntlet"` | 11 | `0.686` |
| **Pooled** | — | **78** | **`0.885`** |

## 2. What is validated and what is not

1. **Validated (3 of 7 rules):**
   - **Word-order dispersion (`T3`):** Both `CSD-ViT-L` (`ρ = 0.844`) and `DINOv2-large` (`ρ = 0.898`) reproduce the 1–5 visual dispersion scores across the five word orders (`threshold ≥ 0.60`).
   - **Magnitude of change from baseline (`T5`):** `DINOv2-large` cosine distance (`ρ = 0.661`, `threshold ≥ 0.50`; `CSD-ViT-L` `ρ = 0.654`) tracks the ordinal change labels (`none` to `strong`) on the 150 C64 phase-1 renders.
   - **Character trait loss (`T7`):** `VQAScore` (`clip-flant5-xl`) achieves a pooled within-trait AUC of **`0.885`** (`threshold ≥ 0.80`), with `AUC ≥ 0.824` on six of the seven traits (`elf 1.000`, `fur 0.995`, `antlers 0.985`, `pauldron 0.885`, `tan 0.830`, `eyepatch 0.824`; `gauntlet 0.686`).
2. **Not validated (4 of 7 rules):**
   - **Cross-character direction coherence (`T1`, `T2`):** Just as the 23 style features in C65 disagreed with the eye (`page 30`), `CSD-ViT-L` change-vector coherence across the 7 characters correlates negatively with the eye's "same direction" label (`ρ = -0.482`, `AUC = 0.056`; `T2 AUC = 0.383`). A possible reading, not tested: edits that keep all 7 characters in the comic genre have small change vectors in idiosyncratic directions (low CSD cosine), while strong edits (`L06`, `L12`) apply a large shared shift in CSD space even when the characters land in different genres.
   - **Style vs content discriminant validity (`T4`):** `CSD-ViT-L` separates style `changed` from `unchanged` well (`AUC = 0.796 ≥ 0.70`), but fails the discriminant requirement `AUC(CSD) > AUC(DINOv2)` (`0.796 < 0.815`). A likely reason, not tested here: text-encoder edits that change style also change the character (`C75`), which DINOv2 sees.
   - **Zero-shot CLIP genre (`T6`):** `CLIP ViT-L/14` reaches `0.593` accuracy on the 145 single-genre notes, comfortably above `majority + 0.15 = 0.467` but `0.007` below the `0.600` bar (`86/145`, 1 image short of `87/145 = 0.600`). By the pre-registered rule, it is not validated.
