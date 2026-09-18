# Risultati Sperimentali — Rotazioni: Block_1 vs Block_6 nello Spazio Tessitura

**Data di esecuzione**: 2026-09-18 / 2026-09-19  
**Stato**: Eseguito, verificato e congelato a fronte di [`docs/prereg_rotations_block1_vs_block6.md`](prereg_rotations_block1_vs_block6.md)  
**Displacement target appaiato**: $D_{\text{modello}} = 0.04500$ (scarto tra blocchi: $\Delta D = 0.0000006$)  
**Matrice generazioni**: 10 stili $\times$ 3 seed $\times$ 7 condizioni = **210 immagini**  
**File di calibrazione**: [`data/matched_rotation_calibration.json`](../data/matched_rotation_calibration.json)  
**File risultati**: [`data/rotations_block1_vs_block6_results.csv`](../data/rotations_block1_vs_block6_results.csv)  

---

## 1. Verdetto in Sintesi

### **Esito: CONFERMATA (SPECIFICITÀ ANATOMICA DIMOSTRATA)**

1. **Statistica Primaria Congelata (Leave-One-Out Cross-Prompt)**:
   - Vantaggio stesso-blocco medio: **$\bar{V} = +1.03860$**
   - Segni concordi su 10 stili: **10/10**
   - Test di permutazione esatta a scambio di segno (sign-flip test, $n=10$):  
     **$p = 0.00195$** (pavimento teorico esatto: $2/2^{10} = 2/1024 = \mathbf{0.00195}$).

2. **Criterio Nullo di Falsificazione (§4 Pre-registrazione: Scramble A vs Scramble B)**:
   - Vantaggio medio tra controlli a segni casuali allo stesso $D = 0.04500$: **$\bar{V}_{\text{scramble}} = +0.53230$** ($p = 0.00195$)
   - Condizione necessaria di falsificazione: $\bar{V} > \bar{V}_{\text{scramble}}$
   - Risultato falsificazione: **SUPERATO** (la specificità anatomica dei blocchi supera significativamente la perturbazione stocastica non strutturata).

3. **Coerenza Direzionale Intra-Blocco e Inter-Blocco**:
   - Coerenza interna `Block_1`: **+0.9491** (vs scramble A: +0.8908)
   - Coerenza interna `Block_6`: **+0.9578** (vs scramble B: +0.5733)
   - Coseno grezzo cross-blocco (Block_1 vs Block_6): **-0.0615**
   - Coseno disattenuato cross-blocco: **-0.06451**

4. **Quota Antisimmetrica della Risposta**:
   - `Block_1`: $\|A\| / (\|S\| + \|A\|) = \mathbf{0.54}$
   - `Block_6`: $\|A\| / (\|S\| + \|A\|) = \mathbf{0.42}$

---

## 2. Tabella Dettagliata per Prompt nello Spazio Primario (Tessitura)

Valori leave-one-out su `glcm_contrast`, `glcm_homogeneity`, `lbp_entropy`:

| Prompt ID | $V(p)$ Primario | $\cos(A_1, \bar{A}_{1,-p})$ | $\cos(A_1, \bar{A}_{6,-p})$ | $\cos(A_6, \bar{A}_{6,-p})$ | $\cos(A_6, \bar{A}_{1,-p})$ | Segno | $V_{\text{scr}}(p)$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `S01_oil` | +1.1695 | +0.9824 | -0.2136 | +0.9563 | -0.1867 | + | +0.3482 |
| `S02_linocut` | +1.0497 | +0.9883 | +0.0355 | +0.9835 | -0.1629 | + | +0.3738 |
| `S03_cyberpunk` | +1.0825 | +0.9224 | -0.2889 | +0.9877 | +0.0340 | + | +0.7851 |
| `S04_gouache` | +0.9932 | +0.9883 | +0.0443 | +0.9964 | -0.0460 | + | +0.6689 |
| `S05_pencil` | +1.0648 | +0.9923 | -0.0471 | +0.9646 | -0.1255 | + | +0.4349 |
| `S06_pastel` | +1.1225 | +0.9876 | -0.1559 | +0.9737 | -0.1278 | + | +0.6097 |
| `S07_comic` | +0.9808 | +0.9961 | -0.0833 | +0.9455 | +0.0633 | + | +0.2594 |
| `S08_papercraft` | +1.0934 | +0.9879 | -0.1431 | +0.9996 | -0.0561 | + | +0.6192 |
| `S09_fresco` | +1.1013 | +0.9970 | -0.1264 | +0.9942 | -0.0850 | + | +0.7987 |
| `S10_synthwave` | +0.7282 | +0.8808 | +0.3740 | +0.9561 | +0.0065 | + | +0.4251 |
| **Media $\pm$ Errore** | **+1.0386** | — | — | — | — | **10/10** | **+0.5323** |
| **Sign-Flip $p$-value** | **0.00195** | — | — | — | — | — | **0.00195** |
| **Pavimento teorico ($2/1024$)** | **0.00195** | — | — | — | — | — | **0.00195** |

---

## 3. Confronto tra Spazi di Misura (Spazio Primario vs Secondari)

| Spazio di Misura | Dim. | $\bar{V}$ | $p$-value | $\bar{V}_{\text{scr}}$ | Coerenza B1 | Coerenza B6 | Falsificazione OK? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Tessitura (PRIMARIO) | 3 | +1.0386 | 0.00195 | +0.5323 | +0.9491 | +0.9578 | SÌ |
| Global 23 Features (Secondario) | 23 | +0.9777 | 0.00195 | +0.4881 | +0.7723 | +0.8908 | SÌ |
| Linework (Secondario) | 3 | +1.1138 | 0.00195 | +0.1715 | +0.2787 | +0.9361 | SÌ |
| Shadow Hardness (Secondario) | 2 | +1.0754 | 0.00391 | +0.7134 | +0.9629 | +0.3993 | SÌ |
| Palette LAB/Chroma (Secondario) | 5 | +0.9561 | 0.00195 | +0.1633 | +0.5527 | +0.8994 | SÌ |

---

## 4. Verifica dei Cancelli di Accettazione della Pre-registrazione

1. [x] **Calibrazione offline verificata**: $|D_1 - D_6| \le 0.0002$ (raggiunto $0.0000006$);
2. [x] **210 task registrati correttamente nella coda ComfyUI** prima dell'elaborazione;
3. [x] **210 immagini estratte da `style_features.py` e `analyze_palette.py`** con zero errori;
4. [x] **Statistica primaria calcolata con la formula congelata al §1** (Leave-One-Out simmetrizzato);
5. [x] **$p$-value riportato con il pavimento esatto $0.00195$** ($2/1024$);
6. [x] **Criterio nullo di falsificazione contro `scramble_A` vs `scramble_B`** calcolato e verificato;
7. [x] **Risultato integrato nel report prima di ogni modifica al README**.

---
*Report autogenerato ed esportato automaticamente dalla suite sperimentale ComfyUI Pilot.*
