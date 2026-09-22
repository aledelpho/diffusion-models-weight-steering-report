# Studio Comparativo Multi-Step — `rotations_clean_v1` (9 vs 7 vs 5 Passi)

**Data e ora**: 2026-09-22 04:50:21  
**Cancello Phase 3**: SUPERATO SU TUTTE LE SERIE (3 x 150 = 450 PNG a 1024x1280, zero HUD)  
**Unità di analisi**: 6 celle per serie (P01/P02 x seed 2718281, 3141592, 1618033)  

## 1. Sintesi Spazio Primario (Tessitura 3D: GLCM Contrast, Homogeneity, LBP Entropy)

| Passi di Campionamento | mean s (D=0.045) | p-value (sign-flip, n=6) | Pavimento | Ipotesi Supportata | cos(B1,B6) | cos(scrA,scrB) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **9 passi** | `-0.8568` | `0.03125` | `0.03125` | **False** | `+0.1704` | `-0.6864` |
| **7 passi** | `-0.7906` | `0.06250` | `0.03125` | **False** | `+0.3288` | `-0.4618` |
| **5 passi** | `-0.7191` | `0.03125` | `0.03125` | **False** | `+0.5167` | `-0.2024` |

## 2. Punteggi per Cella nello Spazio Primario attraverso le Tre Serie

| Passi | Prompt | Seed | s (D=0.030) | s (D=0.045) | s (D=0.060) | cos(B1,B6) | cos(scrA,scrB) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 9 | P01 | 2718281 | +1.3035 | -0.7418 | +0.7542 | -0.0990 | -0.8409 |
| 9 | P01 | 3141592 | +0.8024 | -1.1160 | +0.1329 | +0.2547 | -0.8613 |
| 9 | P01 | 1618033 | +1.0674 | -0.7723 | +0.2852 | +0.0287 | -0.7436 |
| 9 | P02 | 2718281 | +0.8315 | -0.9750 | +0.0138 | +0.2397 | -0.7353 |
| 9 | P02 | 3141592 | +0.5812 | -0.8883 | -0.0177 | +0.2662 | -0.6221 |
| 9 | P02 | 1618033 | +0.5863 | -0.6474 | -0.0574 | +0.3321 | -0.3153 |
| 7 | P01 | 2718281 | +1.3418 | +0.2000 | +0.1745 | +0.2537 | +0.4537 |
| 7 | P01 | 3141592 | +0.9271 | -1.0846 | -0.1905 | +0.2431 | -0.8415 |
| 7 | P01 | 1618033 | +1.1902 | -1.2659 | +0.6125 | +0.4060 | -0.8599 |
| 7 | P02 | 2718281 | +1.0533 | -0.8377 | +0.2915 | +0.2762 | -0.5615 |
| 7 | P02 | 3141592 | +1.0158 | -0.7943 | +0.0777 | +0.3133 | -0.4810 |
| 7 | P02 | 1618033 | +0.6494 | -0.9609 | +0.0127 | +0.4806 | -0.4803 |
| 5 | P01 | 2718281 | +0.5120 | -0.2761 | +0.1043 | +0.5787 | +0.3026 |
| 5 | P01 | 3141592 | +0.5386 | -0.4695 | -0.0075 | +0.6936 | +0.2240 |
| 5 | P01 | 1618033 | +1.2632 | -0.2794 | +0.5119 | +0.2494 | -0.0300 |
| 5 | P02 | 2718281 | +0.7054 | -1.1758 | -0.0057 | +0.5994 | -0.5764 |
| 5 | P02 | 3141592 | +1.1546 | -1.0319 | -0.3399 | +0.4334 | -0.5985 |
| 5 | P02 | 1618033 | +0.4347 | -1.0820 | +0.5262 | +0.5458 | -0.5362 |

## 3. Matrice Completa degli Spazi di Misura (Primario e Secondari)

| Passi | Spazio | Tipo | mean s | p (uncorrected) | cos(B1,B6) | cos(scrA,scrB) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| 9 | Texture (Primary) | primary | -0.8568 | 0.03125 | +0.1704 | -0.6864 |
| 9 | Linework (Secondary) | secondary | -0.6838 | 0.06250 | +0.7533 | +0.0695 |
| 9 | Shadow (Secondary) | secondary | -0.1170 | 0.87500 | +0.0330 | -0.0840 |
| 9 | Frequency (Secondary) | secondary | -1.3333 | 0.12500 | +0.3333 | -1.0000 |
| 9 | Palette (Secondary) | secondary | -0.5188 | 0.03125 | +0.3427 | -0.1761 |
| 7 | Texture (Primary) | primary | -0.7906 | 0.06250 | +0.3288 | -0.4618 |
| 7 | Linework (Secondary) | secondary | -0.4489 | 0.15625 | +0.1750 | -0.2739 |
| 7 | Shadow (Secondary) | secondary | -0.8171 | 0.12500 | +0.7093 | -0.1077 |
| 7 | Frequency (Secondary) | secondary | -1.0000 | 0.25000 | +0.0000 | -1.0000 |
| 7 | Palette (Secondary) | secondary | -0.2976 | 0.09375 | +0.4076 | +0.1100 |
| 5 | Texture (Primary) | primary | -0.7191 | 0.03125 | +0.5167 | -0.2024 |
| 5 | Linework (Secondary) | secondary | -0.5508 | 0.31250 | +0.4124 | -0.1384 |
| 5 | Shadow (Secondary) | secondary | -0.6627 | 0.06250 | +0.9622 | +0.2996 |
| 5 | Frequency (Secondary) | secondary | -0.6667 | 0.50000 | -0.3333 | -1.0000 |
| 5 | Palette (Secondary) | secondary | -0.3446 | 0.21875 | +0.4006 | +0.0560 |

## 4. Contact Sheet e Ispezione Visiva

- **9 Passi**: `qc_output/rotations_clean_v1/contact_sheet_3x3.png`
- **7 Passi**: `qc_output/rotations_clean_v1_steps7/contact_sheet_3x3.png`
- **5 Passi**: `qc_output/rotations_clean_v1_steps5/contact_sheet_3x3.png`
