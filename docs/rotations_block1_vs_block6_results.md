# Risultati Sperimentali — Rotazioni: Block_1 vs Block_6 nello Spazio Tessitura

**Data di esecuzione**: 2026-09-18 / 2026-09-19  
**Stato**: Eseguito e verificato a fronte di [`docs/prereg_rotations_block1_vs_block6.md`](prereg_rotations_block1_vs_block6.md)  
**Displacement target appaiato**: $D_{\text{modello}} = 0.04500$ (scarto residuo tra blocchi: $\Delta D = 0.0000006$)  
**Matrice generazioni**: 10 stili $\times$ 3 seed $\times$ 7 condizioni = **210 immagini**  
**File di calibrazione**: [`data/matched_rotation_calibration.json`](../data/matched_rotation_calibration.json)  
**Dataset dei risultati**: [`data/rotations_block1_vs_block6_results.csv`](../data/rotations_block1_vs_block6_results.csv), [`data/rotations_block1_vs_block6_prompt_scores.csv`](../data/rotations_block1_vs_block6_prompt_scores.csv)  
**Contact Sheet QC (WebP)**: [`qc_output/rotations_block1_vs_block6/`](../qc_output/rotations_block1_vs_block6/)  
**Ricette di Riproducibilità**: [`qc_output/rotations_block1_vs_block6/RECIPES.md`](../qc_output/rotations_block1_vs_block6/RECIPES.md)  

---

## 1. Verdetto in Sintesi

### **Esito: SEPARABILITÀ DIREZIONALE CONFERMATA TRA GLI ESTREMI**
*(Specificità funzionale anatomica non dimostrata: l'esperimento non separa la specializzazione di ruolo dalla pura prossimità topografica all'uscita della rete, né include i blocchi intermedi)*

1. **Statistica Primaria Congelata (Leave-One-Out Cross-Prompt)**:
   - Nello spazio di misura primario **Tessitura** (`glcm_contrast`, `glcm_homogeneity`, `lbp_entropy`), a parità di spostamento normativo di Frobenius ($D = 0.04500$):
     $$\bar{V} = \mathbf{+1.0386}$$
   - **Concordanza di segno**: **10 / 10** regimi stilistici indipendenti mostrano un vantaggio stesso-blocco strettamente positivo ($V(p) > 0$).
   - **Test di permutazione esatta a scambio di segno** (sign-flip test a due code su $2^{10} = 1024$ permutazioni, $n=10$):  
     $$\mathbf{p = 0.00195} \quad (\text{pavimento teorico esatto: } 2/1024 = 0.001953)$$

2. **Criterio Nullo di Falsificazione (§4 Pre-registrazione: Scramble A vs Scramble B)**:
   - Il vantaggio medio tra due perturbazioni ortogonali stocastiche indipendenti allo stesso $D = 0.04500$ è:
     $$\bar{V}_{\text{scramble}} = \mathbf{+0.5323} \quad (p = 0.00195)$$
   - Poiché $\mathbf{\bar{V} > \bar{V}_{\text{scramble}}}$ ($+1.0386 > +0.5323$, $\Delta V = +0.5063$), l'ipotesi nulla che la separazione osservata sia un banale effetto di disturbo casuale tra due matrici arbitrarie è **respinta**. La risposta di `Block_1` e `Block_6` possiede una coerenza interna che eccede di quasi il doppio la perturbazione stocastica.

3. **Coerenza Direzionale Intra-Blocco e Inter-Blocco (Spazio Tessitura)**:
   - Coerenza interna `Block_1` (media coseni cross-prompt): **$+0.9491$**
   - Coerenza interna `Block_6` (media coseni cross-prompt): **$+0.9578$**
   - Coseno cross-blocco grezzo ($\cos(\bar{A}_1, \bar{A}_6)$): **$-0.0615$**
   - Coseno cross-blocco disattenuato ($\cos / \sqrt{\text{coh}_1 \times \text{coh}_6}$): **$-0.0645$**  
   *(Nello spazio di micro-grana, l'ortogonalità tra le traiettorie di Block_1 e Block_6 è quasi perfetta).*

4. **Quota Antisimmetrica della Risposta**:
   - `Block_1`: $\|A\| / (\|S\| + \|A\|) = \mathbf{0.54}$
   - `Block_6`: $\|A\| / (\|S\| + \|A\|) = \mathbf{0.42}$

---

## 2. Riserve Metodologiche e Limiti Epistemici

> **Aggiornamento 2026-09-21.** La domanda di questa sezione — se la separazione direzionale sia
> specializzazione funzionale o pura prossimita' ai confini della rete — era stata affidata
> all'esperimento del triangolo `Block_1`/`Block_3`/`Block_6`. Quell'esperimento **non la
> chiude**: il lato `Block_3`-vs-`Block_6`, che e' il lato che avrebbe deciso, non ha un nullo
> ancorato su `Block_6` e non e' misurato; il lato `Block_1`-vs-`Block_3` non si separa dal
> nullo sotto la regola di aggregazione dichiarata. Vedi
> [`rotations_triangolo_block1_block3_block6_results.md`](rotations_triangolo_block1_block3_block6_results.md)
> §1-bis. **La domanda resta aperta.**


Nonostante la significatività statistica al pavimento teorico ($p = 0.00195$), i risultati **non consentono di affermare una specializzazione funzionale dell'architettura**, per tre ragioni strutturali:

1. **Confondimento tra Specializzazione Funzionale e Prossimità all'Uscita**:
   - `Block_6` raggruppa gli ultimi blocchi del DiT (strati 24–27), posizionati immediatamente a ridosso dell'uscita e della proiezione finale verso il VAE.
   - `Block_1` raggruppa i blocchi di testa (strati 0–4).
   - Qualsiasi disturbo applicato agli strati terminali agisce su rappresentazioni che hanno già completato la convergenza globale e influenza direttamente i dettagli ad alta frequenza dell'immagine. Pertanto, la divergenza direzionale tra `Block_1` e `Block_6` è **compatibile sia con una reale segregazione qualitativa di compiti sia con un banale effetto di profondità/uscita**.

2. **Assenza dei Blocchi Centrali nel Disegno**:
   - Questo esperimento ha testato esclusivamente la coppia di estremi `Block_1` vs `Block_6`.
   - Non sappiamo se i blocchi centrali (`Block_2`, `Block_3`, `Block_4`, `Block_5`) occupino posizioni intermedie lungo un gradiente continuo di profondità, o se manifestino direzioni autonome. Senza testare i blocchi centrali allo stesso $D$ calibrato, la topografia resta incompleta.

3. **Instabilità della Disattenuazione nelle Famiglie Secondarie (Pitfall 36)**:
   - Nello spazio primario di Tessitura, entrambe le coerenze interne sono stabili e superiori a $0.94$, rendendo la disattenuazione di Spearman affidabile (variazione trascurabile da $-0.0615$ a $-0.0645$).
   - Nelle famiglie secondarie (Linework e Shadow Hardness), una delle coerenze scende sotto $0.40$. In questo regime di bassa affidabilità, dividere per la radice del prodotto amplifica esponenzialmente il rumore di campionamento. **In tali famiglie fanno fede unicamente i valori grezzi**.

---

## 3. Tabella Dettagliata per Prompt nello Spazio Primario (Tessitura)

Valori calcolati con la formula Leave-One-Out registrata su `glcm_contrast`, `glcm_homogeneity`, `lbp_entropy`:

| Prompt ID | Stile | $V(p)$ Primario | $\cos(A_1, \bar{A}_{1,-p})$ | $\cos(A_1, \bar{A}_{6,-p})$ | $\cos(A_6, \bar{A}_{6,-p})$ | $\cos(A_6, \bar{A}_{1,-p})$ | Segno | $V_{\text{scr}}(p)$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `S01_oil` | Oil Painting | +1.1695 | +0.9824 | -0.2136 | +0.9563 | -0.1867 | + | +0.3482 |
| `S02_linocut` | Linocut Print | +1.0497 | +0.9883 | +0.0355 | +0.9835 | -0.1629 | + | +0.3738 |
| `S03_cyberpunk` | Neon Cyberpunk | +1.0825 | +0.9224 | -0.2889 | +0.9877 | +0.0340 | + | +0.7851 |
| `S04_gouache` | Gouache | +0.9932 | +0.9883 | +0.0443 | +0.9964 | -0.0460 | + | +0.6689 |
| `S05_pencil` | Graphite Pencil | +1.0648 | +0.9923 | -0.0471 | +0.9646 | -0.1255 | + | +0.4349 |
| `S06_pastel` | Soft Pastel | +1.1225 | +0.9876 | -0.1559 | +0.9737 | -0.1278 | + | +0.6097 |
| `S07_comic` | Western Comic | +0.9808 | +0.9961 | -0.0833 | +0.9455 | +0.0633 | + | +0.2594 |
| `S08_papercraft` | Cut Paper Craft | +1.0934 | +0.9879 | -0.1431 | +0.9996 | -0.0561 | + | +0.6192 |
| `S09_fresco` | Renaissance Fresco | +1.1013 | +0.9970 | -0.1264 | +0.9942 | -0.0850 | + | +0.7987 |
| `S10_synthwave` | Retro Synthwave | +0.7282 | +0.8808 | +0.3740 | +0.9561 | +0.0065 | + | +0.4251 |
| **Media campionaria** | — | **+1.0386** | — | — | — | — | **10/10** | **+0.5323** |
| **Sign-Flip $p$-value** | — | **0.00195** | — | — | — | — | — | **0.00195** |
| **Pavimento teorico** | — | **0.00195** | — | — | — | — | — | **0.00195** |

---

## 4. Confronto tra Spazi di Misura (Grezzo vs Disattenuato)

Nelle famiglie secondarie, il confronto tra coseno grezzo e disattenuato mostra chiaramente l'effetto del denominatore a bassa coerenza:

| Spazio di Misura | Dim. | $\bar{V}$ | $p$-value | $\bar{V}_{\text{scr}}$ | Coerenza B1 | Coerenza B6 | Coseno B1-B6 (Grezzo) | Coseno B1-B6 (Disattenuato) | Affidabilità Disattenuata |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tessitura (PRIMARIO)** | 3 | **+1.0386** | **0.00195** | +0.5323 | +0.9491 | +0.9578 | **-0.0615** | **-0.0645** | **ALTA** (entrambe $> 0.94$) |
| **Global 23 Features** | 23 | +0.9777 | 0.00195 | +0.4881 | +0.7723 | +0.8908 | -0.0780 | -0.0940 | MEDIA |
| **Linework** | 3 | +1.1138 | 0.00195 | +0.1715 | +0.2787 | +0.9361 | **-0.4499** | *-0.8809* | **NON ATTENDIBILE** (B1 < 0.30) |
| **Shadow Hardness** | 2 | +1.0754 | 0.00391 | +0.7134 | +0.9629 | +0.3993 | **-0.4343** | *-0.7004* | **NON ATTENDIBILE** (B6 < 0.40) |
| **Palette LAB/Chroma** | 5 | +0.9561 | 0.00195 | +0.1633 | +0.5527 | +0.8994 | -0.1382 | -0.1961 | BASSA (B1 ~ 0.55) |

> **Nota metodologica**: Nelle righe Linework e Shadow Hardness il salto da $-0.45$ a $-0.88$ e da $-0.43$ a $-0.70$ è un artefatto matematico della divisione per radici di coerenza vicine a zero, non un segnale biologico/architetturale. Solo il valore grezzo è interpretabile.

---

## 5. Trasparenza sulla Sequenza Temporale dei Commit (Audit Locale Git)

In assenza di polling esterno via API GitHub durante la sessione interattiva, la sequenza cronologica oggettiva è verificabile direttamente dal log dei commit locali di `diffusion-models-weight-steering-report`:

```text
28529bf | 2026-09-19 01:29:15 +0200 | feat(report): block 1 vs block 6 rotation results and null falsification
64e219d | 2026-09-18 23:10:13 +0200 | prereg: freeze protocol for Block_1 vs Block_6 texture rotation experiment
```

1. **Commit `64e219d` (2026-09-18 23:10:13 +0200)**:  
   Congelamento del protocollo `docs/prereg_rotations_block1_vs_block6.md` e della calibrazione $D = 0.04500$ prima di qualsiasi generazione.
2. **Commit `28529bf` (2026-09-19 01:29:15 +0200)**:  
   Commit successivo, avvenuto 2 ore e 19 minuti dopo, contenente le 210 righe estratte dai render terminati, i CSV delle feature e la prima stesura del report.

---

## 6. Verifica dei Cancelli di Accettazione

1. [x] **Calibrazione offline verificata**: $|D_1 - D_6| \le 0.0002$ (misurato $\Delta D = 0.0000006$);
2. [x] **210 task registrati correttamente nella coda ComfyUI** prima dell'elaborazione;
3. [x] **210 immagini estratte da `style_features.py` e `analyze_palette.py`** con zero errori;
4. [x] **Statistica primaria calcolata con la formula congelata al §1** (Leave-One-Out simmetrizzato);
5. [x] **$p$-value riportato con il pavimento esatto $0.00195$** ($2/1024$);
6. [x] **Criterio nullo di falsificazione contro `scramble_A` vs `scramble_B`** calcolato e verificato ($\bar{V} > \bar{V}_{\text{scr}}$);
7. [x] **Riserve metodologiche su uscita, blocchi centrali e disattenuazione integrate nel documento**.
