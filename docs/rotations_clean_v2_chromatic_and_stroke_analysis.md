# Analisi Algoritmica Deterministica: Banda Cromatica e Stroke — `rotations_clean_v2`

**Autore/Script**: `experiments/analyze_chromatic_and_stroke_v2.py`  
**Data e ora**: 2026-09-22 14:42:27  
**Corpus**: 150 immagini 1024x1280 (zero HUD) generati a 9 step con angoli conservativi (5° low, 10° mid, 15° high).  

## 1. Analisi della Banda Cromatica (Spazio 24-D Lab Completo)

Lo spazio cromatico 24-D include coordinate percettive $(L^*, a^*, b^*)$ per tutti i 6 swatch dominanti più la carta e l'inchiostro:

- **Statistica di separazione direzionale $\bar{s}$ (10° mid)**: `-0.1518`
- **p-value (sign-flip esatto, n=6)**: `0.25000` (pavimento esatto `0.03125`)
- **Ipotesi confermata (s > 0, p < 0.05)**: **False**
- **$\cos(A_{B1}, A_{B6})$ medio**: `-0.0826` (i due blocchi ruotano la palette in direzioni marcatamente divergenti/ortogonali)
- **$\cos(A_{scrA}, A_{scrB})$ medio**: `-0.2344`

### Punteggi Cromatici 24-D per Cella e Risposta alla Dose

| Prompt | Seed | s (5° low) | s (10° mid) | s (15° high) | cos(B1,B6) 10° | cos(scrA,scrB) 10° |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| P01 | 2718281 | +0.4195 | -0.5429 | -0.4994 | +0.0284 | -0.5145 |
| P01 | 3141592 | -0.0763 | +0.2324 | -0.5851 | -0.2168 | +0.0157 |
| P01 | 1618033 | -0.2359 | -0.3437 | +0.2497 | -0.1350 | -0.4787 |
| P02 | 2718281 | -0.5946 | -0.0934 | -0.3912 | -0.1067 | -0.2001 |
| P02 | 3141592 | -0.1224 | -0.1682 | -0.0479 | -0.0665 | -0.2348 |
| P02 | 1618033 | +0.3744 | +0.0050 | +0.1362 | +0.0007 | +0.0058 |

### Medie delle Metriche Globali di Banda Cromatica

| Condizione | Chroma Spread | Tonal Range | Paper L* | Paper C* | Ink L* | Ink C* | Colorfulness HS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| baseline | 40.443 | 80.647 | 73.96 | 11.06 | 3.71 | 1.22 | 35.891 |
| B1_pos_mid | 42.212 | 82.694 | 76.46 | 11.54 | 3.86 | 1.41 | 38.650 |
| B1_neg_mid | 41.478 | 79.964 | 74.44 | 25.89 | 4.97 | 1.62 | 38.685 |
| B6_pos_mid | 51.548 | 73.041 | 68.81 | 38.92 | 4.46 | 5.62 | 51.026 |
| B6_neg_mid | 26.770 | 74.425 | 70.18 | 8.71 | 4.48 | 10.30 | 29.563 |
| scrA_pos_mid | 45.925 | 81.906 | 77.77 | 17.90 | 3.17 | 1.12 | 40.123 |
| scrA_neg_mid | 36.697 | 80.933 | 73.76 | 16.24 | 4.70 | 1.38 | 32.864 |
| scrB_pos_mid | 26.796 | 70.335 | 57.19 | 8.78 | 0.99 | 4.26 | 25.956 |
| scrB_neg_mid | 57.600 | 78.730 | 81.84 | 43.77 | 11.39 | 13.30 | 74.286 |

---

## 2. Analisi degli Stroke / Linework (Tratto Grafico e Modulazione)

Lo spazio 3-D dello stroke modella contemporaneamente lo spessore mediano del tratto (`stroke_width_median_px`), la sua modulazione (`stroke_width_cv`) e la densità dei bordi di china (`edge_density`):

- **Statistica di separazione direzionale $\bar{s}$ (10° mid)**: `+0.2314`
- **p-value (sign-flip esatto, n=6)**: `0.71875` (pavimento esatto `0.03125`)
- **Ipotesi confermata (s > 0, p < 0.05)**: **False**
- **$\cos(A_{B1}, A_{B6})$ medio**: `+0.4790` (forte divergenza dei gradienti di linework tra B1 e B6)
- **$\cos(A_{scrA}, A_{scrB})$ medio**: `+0.7105`

### Punteggi Stroke 3-D per Cella e Risposta alla Dose

| Prompt | Seed | s (5° low) | s (10° mid) | s (15° high) | cos(B1,B6) 10° | cos(scrA,scrB) 10° |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| P01 | 2718281 | -1.4689 | +0.0376 | +1.6599 | +0.4638 | +0.5013 |
| P01 | 3141592 | -0.8621 | +1.5340 | +1.2611 | -0.8986 | +0.6355 |
| P01 | 1618033 | +0.8901 | -0.0240 | +1.4708 | +0.7485 | +0.7245 |
| P02 | 2718281 | -0.1372 | -0.1790 | -1.1722 | +0.8175 | +0.6385 |
| P02 | 3141592 | +0.0506 | -0.0934 | +0.5984 | +0.9341 | +0.8407 |
| P02 | 1618033 | -0.0371 | +0.1133 | -0.0687 | +0.8090 | +0.9222 |

### Medie Univariate delle Feature di Stroke per Condizione

| Condizione | Stroke Width Median (px) | Stroke Width CV | Edge Density | Contour Mean Len (px) | Contour Components |
| :--- | :---: | :---: | :---: | :---: | :---: |
| baseline | 3.000 | 0.748 | 0.1352 | 57.31 | 3126.2 |
| B1_pos_mid | 2.800 | 0.773 | 0.1432 | 56.56 | 3354.2 |
| B1_neg_mid | 3.800 | 0.595 | 0.1331 | 61.28 | 2908.3 |
| B6_pos_mid | 2.000 | 0.931 | 0.1263 | 56.76 | 3003.2 |
| B6_neg_mid | 3.200 | 0.406 | 0.2091 | 32.85 | 8483.3 |
| scrA_pos_mid | 4.000 | 0.571 | 0.1334 | 62.35 | 2809.0 |
| scrA_neg_mid | 2.800 | 0.702 | 0.1443 | 54.69 | 3484.5 |
| scrB_pos_mid | 3.200 | 0.457 | 0.1290 | 61.42 | 2994.0 |
| scrB_neg_mid | 2.000 | 1.059 | 0.1179 | 55.42 | 2861.0 |

### Decomposizione Simmetrica (S) e Antisimmetrica (A) dello Stroke a 10°

| Feature | Baseline | Block_1 Antisimmetrico (A) | Block_1 Simmetrico (S) | Block_6 Antisimmetrico (A) | Block_6 Simmetrico (S) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| stroke_width_median_px | 3.000 | -0.5000 | +0.3000 | -0.6000 | -0.4000 |
| stroke_width_std_px | 2.203 | -0.0304 | -0.0085 | +0.2980 | -0.6385 |
| stroke_width_cv | 0.748 | +0.0887 | -0.0636 | +0.2628 | -0.0792 |
| edge_density | 0.135 | +0.0050 | +0.0030 | -0.0414 | +0.0325 |
| contour_mean_length_px | 57.314 | -2.3587 | +1.6086 | +11.9552 | -12.5115 |
| contour_n_components | 3126.167 | +222.9167 | +5.0833 | -2740.0833 | +2617.0833 |
