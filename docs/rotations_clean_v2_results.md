# Report Risultati — `rotations_clean_v2` (Angoli Conservativi 5°/10°/15°)

**Data e ora**: 2026-09-22 11:24:33  
**Cancello Phase 3**: SUPERATO (150/150 PNG a 1024x1280, zero HUD, integrità visiva verificata)  
**Unità di analisi**: 6 celle (P01/P02 x seed 2718281, 3141592, 1618033)  
**Protocollo Angoli**: Fissi simmetrici (5° low, 10° mid, 15° high) — no distorsioni o collassi su Block_6  

## 1. Risultati Nello Spazio Primario (Texture 3D: GLCM Contrast, Homogeneity, LBP Entropy)

- **Statistica primaria $\bar{s}$ (10° mid)**: `+0.8817`
- **p-value (sign-flip esatto, n=6)**: `0.03125` (pavimento `0.03125`)
- **Ipotesi confermata (s > 0, p < 0.05)**: **True** (tutte e 6 le celle strettamente positive!)
- $\cos(A_{B1}, A_{B6})$ medio: `-0.5702`
- $\cos(A_{scrA}, A_{scrB})$ medio: `+0.3115`

## 2. Spazi di Misura (Primario e Secondari)

| Spazio | Tipo | mean s (10°) | p (uncorrected) | cos(B1,B6) | cos(scrA,scrB) |
| --- | --- | ---: | ---: | ---: | ---: |
| Texture (Primary) | primary | +0.8817 | 0.03125 | -0.5702 | +0.3115 |
| Linework (Secondary) | secondary | +0.6629 | 0.09375 | +0.0423 | +0.7051 |
| Shadow (Secondary) | secondary | +0.4064 | 0.21875 | -0.9248 | -0.5184 |
| Frequency (Secondary) | secondary | -0.6667 | 0.50000 | +1.0000 | +0.3333 |
| Palette (Secondary) | secondary | +0.3187 | 0.12500 | -0.2459 | +0.0728 |

## 3. Punteggi per Cella e Risposta alla Dose (Spazio Primario Tessitura)

| Prompt | Seed | s (5° low) | s (10° mid) | s (15° high) | cos(B1,B6) 10° | cos(scrA,scrB) 10° |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| P01 | 2718281 | +1.1999 | +1.4894 | +1.5395 | -0.9879 | +0.5014 |
| P01 | 3141592 | +0.2686 | +1.5984 | +1.1535 | -0.9287 | +0.6697 |
| P01 | 1618033 | -0.5971 | +1.4669 | +1.0648 | -0.7368 | +0.7301 |
| P02 | 2718281 | -0.6400 | +0.1459 | +0.8566 | -0.1973 | -0.0514 |
| P02 | 3141592 | -1.1644 | +0.0024 | +0.4045 | -0.2597 | -0.2573 |
| P02 | 1618033 | -1.2996 | +0.5870 | +0.8216 | -0.3106 | +0.2765 |

## 4. Evidenza Visiva e Controllo Qualità

Contact sheet 3x3 disponibile in `qc_output/rotations_clean_v2/contact_sheet_3x3.png`.
