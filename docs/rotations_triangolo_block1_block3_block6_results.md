# Risultati Sperimentali — Il Triangolo: Block_1 vs Block_3 vs Block_6

**Data di esecuzione**: 2026-09-21  
**Stato**: Eseguito, verificato e congelato a fronte di [`docs/prereg_rotations_triangolo_block1_block3_block6.md`](prereg_rotations_triangolo_block1_block3_block6.md)  
**Protocollo metodologico adottato**: Opzione (a) con controlli scramble cross-anchored (`scramble_C` e `scramble_D` su Block_3)  
**Displacement target appaiato**: $D_{\text{modello}} = 0.04500$ (scarto tra i 3 blocchi: $\Delta D \le 0.000005$)  
**Matrice generazioni**: 330 immagini (210 riusate da Block_1 vs Block_6 + 120 generate ex-novo per Block_3 e scramble C/D)  
**File di calibrazione**: [`data/matched_rotation_calibration.json`](../data/matched_rotation_calibration.json)  
**File risultati**: [`data/rotations_triangolo_results.csv`](../data/rotations_triangolo_results.csv)  
**Punteggi per prompt**: [`data/rotations_triangolo_prompt_scores.csv`](../data/rotations_triangolo_prompt_scores.csv)  

---

## 1. Verdetto Primario dell'Albero Decisionale (§2 Pre-registrazione)

### **Regime Selezionato: 4. Asimmetria di Propagazione**

> **Valutazione Formale**:  
> Forte asimmetria tra ingresso e uscita (|V_1,3 - V_3,6| = 0.2737 > 0.25). La dinamica di uno dei due confini penetra nel centro molto piu' profondamente dell'altra.

### Riepilogo Numerico delle Ipotesi Primarie nello Spazio Tessitura

| Metrica / Contrasto | Valore Osservato | Valore Pavimento Scramble | Delta Appaiato $\Delta \bar{V}$ | $p$-value esatto | Significatività (Holm $\alpha=0.05$) |
|---|---|---|---|---|---|
| **LATO 1: Block_1 vs Block_3** ($V_{1,3}$) | **+0.0802** ($p=0.11328$) | -0.0396 ($V_{\text{scr}(1,3)}$) | **+0.1197** | **0.03711** | **CONFERMATO** |
| **LATO 2: Block_3 vs Block_6** ($V_{3,6}$) | **+0.3539** ($p=0.01172$) | -0.0396 ($V_{\text{scr}(3,6)}$) | **+0.3934** | **0.00781** | **CONFERMATO** |
| **LATO 3: Block_1 vs Block_6** ($V_{1,6}$) | **+0.9555** ($p=0.00195$) | +0.6070 ($V_{\text{scr}(1,1)}$) | **+0.3485** | **0.00195** | *(Termine di riferimento congelato)* |

* **Pavimento Nullo Omologo Block_1** (`scramble_A` vs `scramble_B`): $\bar{V}_{\text{scr}(1,1)} = +0.6070$ ($p=0.00195$)  
* **Pavimento Nullo Omologo Block_3** (`scramble_C` vs `scramble_D`): $\bar{V}_{\text{scr}(3,3)} = +0.1837$ ($p=0.08203$)  
* **Pavimento Nullo Cross-Anchored** (`scramble_A` vs `scramble_C`): $\bar{V}_{\text{scr}(1,3)} = -0.0396$ ($p=0.15430$)  
* **Media delle 4 coppie cross-scramble**: $\bar{V}_{\text{scr,cross}} = +0.5630$  

---

## 2. Punteggi Leave-One-Out per Ciascuno dei 10 Prompt Stilistici

Tabella analitica dei punteggi calcolati con la procedura Leave-One-Out cross-prompt nello spazio primario Tessitura (`glcm_contrast`, `glcm_homogeneity`, `lbp_entropy` z-standardizzate):

| Prompt ID | $V_{1,3}(p)$ | $V_{3,6}(p)$ | $V_{1,6}(p)$ | $V_{\text{scr}(1,3)}(p)$ | $V_{\text{scr}(1,1)}(p)$ | $\Delta V_{1,3}(p)$ | $\Delta V_{3,6}(p)$ |
|---|---|---|---|---|---|---|---|
| `S01_oil` | +0.1873 | +0.4842 | +1.1067 | +0.0919 | +0.3723 | +0.0954 | +0.3923 |
| `S02_linocut` | +0.0737 | +0.5522 | +0.9524 | -0.0909 | +0.4688 | +0.1645 | +0.6430 |
| `S03_cyberpunk` | -0.1236 | +0.5575 | +1.0174 | -0.0157 | +0.8566 | -0.1079 | +0.5732 |
| `S04_gouache` | +0.1520 | +0.1175 | +0.8977 | -0.0001 | +0.7309 | +0.1520 | +0.1176 |
| `S05_pencil` | +0.2168 | -0.0026 | +0.9847 | -0.2044 | +0.5335 | +0.4213 | +0.2018 |
| `S06_pastel` | +0.2030 | +0.3455 | +1.0572 | -0.0373 | +0.6990 | +0.2403 | +0.3828 |
| `S07_comic` | -0.0269 | +0.5813 | +0.9012 | -0.0390 | +0.3409 | +0.0121 | +0.6203 |
| `S08_papercraft` | +0.1848 | -0.2051 | +1.0234 | +0.0466 | +0.7348 | +0.1383 | -0.2517 |
| `S09_fresco` | +0.1242 | +0.5300 | +1.0309 | -0.0504 | +0.8804 | +0.1746 | +0.5804 |
| `S10_synthwave` | -0.1895 | +0.5782 | +0.5832 | -0.0963 | +0.4529 | -0.0932 | +0.6745 |

---

## 3. Coerenza Interna e Geometria dei Centroidi

* **Coerenza Intra-Blocco (Coseno medio tra prompt dello stesso blocco)**:
  - $\text{coh}(Block\_1) = +0.9204$
  - $\text{coh}(Block\_3) = +0.3138$
  - $\text{coh}(Block\_6) = +0.9599$
  - $\text{coh}(scramble\_A) = +0.9044$ | $\text{coh}(scramble\_B) = +0.4914$
  - $\text{coh}(scramble\_C) = -0.0770$ | $\text{coh}(scramble\_D) = +0.2376$

* **Coseno tra Centroidi Medi (Separazione Direzionale Grezza vs Disattenuata)**:
  - $Block\_1$ vs $Block\_3$: cos grezzo = **+0.8862**, disattenuato = **+1.6491**
  - $Block\_3$ vs $Block\_6$: cos grezzo = **+0.4790**, disattenuato = **+0.8729**
  - $Block\_1$ vs $Block\_6$: cos grezzo = **+0.0188**, disattenuato = **+0.0200**

* **Quota Antisimmetrica ($\|A\| / (\|S\| + \|A\|)$)**:
  - $Block\_1$: **0.498** (dominanza antisimmetrica)
  - $Block\_3$: **0.466**
  - $Block\_6$: **0.441**

---

## 4. Analisi di Robustezza sugli Spazi Stilistici Secondari

| Spazio di Feature | Dimensioni | $\bar{V}_{1,3}$ | $\bar{V}_{3,6}$ | $\bar{V}_{1,6}$ | $\Delta \bar{V}_{1,3}$ ($p$) | $\Delta \bar{V}_{3,6}$ ($p$) | Regime Assegnato |
|---|---|---|---|---|---|---|---|
| Tessitura (Primario) | 3 | +0.0802 | +0.3539 | +0.9555 | +0.1197 (0.0371) | +0.3934 (0.0078) | Asimmetria di Propagazione |
| Tratteggio e Bordi | 3 | +0.1385 | +1.1596 | +1.0923 | -0.1594 (0.2500) | +0.8617 (0.0098) | Centro Piatto / Prossimita ai Confini |
| Ombreggio e Crosshatch | 2 | +0.4064 | -0.1469 | +1.1960 | -0.0568 (0.7969) | -0.6101 (0.0020) | Centro Piatto / Prossimita ai Confini |
| Frequenze Spaziali | 1 | +0.0000 | +0.0000 | +0.0000 | +0.0000 (1.0000) | +0.0000 (1.0000) | Centro Piatto / Prossimita ai Confini |
| Spazio Palette | 5 | +0.2371 | +0.1644 | +0.9651 | +0.0551 (0.4414) | -0.0176 (0.7852) | Centro Piatto / Prossimita ai Confini |

---

## 5. Quality Control Visivo

I contact sheet completi a 11 condizioni $\times$ 3 seed per tutti i 10 stili sono stati generati e salvati in [`qc_output/rotations_triangolo/`](../qc_output/rotations_triangolo/):
* `qc_S01_oil.png` .. `qc_S10_synthwave.png`

---

## 6. Risposta alla Domanda Aperta di Ricerca

Alla domanda iniziale:
*«La separazione direzionale osservata riflette una reale specializzazione funzionale o la pura prossimità topografica ai confini della rete?»*

Il verdetto matematico basato sull'albero decisionale a 4 vie con margine di equivalenza $\Delta_{\text{equiv}} = 0.25$ stabilisce che:
**4. Asimmetria di Propagazione**.  
Forte asimmetria tra ingresso e uscita (|V_1,3 - V_3,6| = 0.2737 > 0.25). La dinamica di uno dei due confini penetra nel centro molto piu' profondamente dell'altra.
