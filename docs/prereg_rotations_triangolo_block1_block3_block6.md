# Pre-registrazione — Il triangolo Block_1 / Block_3 / Block_6

**Data di congelamento**: 2026-09-21  
**Stato**: Congelata e pronta per l'esecuzione.  
**Scopo**: Rispondere alla domanda lasciata aperta da [`docs/rotations_block1_vs_block6_results.md`](rotations_block1_vs_block6_results.md) §2:
*la separazione direzionale osservata riflette una reale specializzazione funzionale o la pura prossimità topografica ai confini della rete (uscita verso il VAE)?*  
Un confronto a due soli estremi non può distinguerle. Se un **terzo blocco, genuinamente centrale**, manifesta una direzione propria, coerente e separabile da entrambe le altre due rispetto al proprio nullo stocastico, l'ipotesi di una pura anomalia di confine perde consistenza. Se invece il centro risulta "piatto" (nessun vantaggio stesso-blocco contro il rumore scramble appaiato né rispetto a Block_1 né a Block_6), l'ipotesi di un effetto legato ai soli confini si rafforza in modo decisivo.

---

### Perché Block_3 e perché l'esclusione motivata di Block_5

Dalla mappa strutturale dei pesi (`docs/model_structures/krea2_architecture_decomposition.md`):
* `Block_1` = Layout_Geometry (strati 0–4, ingresso)
* `Block_2` = Global_Composition (strati 5–9)
* `Block_3` = Subject_Identity (strati 10–14, baricentro all'indice 12)
* `Block_4` = Material_Substance (strati 15–19, baricentro all'indice 17)
* `Block_5` = Art_Style_Medium (strati 20–23)
* `Block_6` = Lighting_Sharpness (strati 24–27, uscita DiT)

Il centro geometrico dei 28 blocchi transformer di Krea-2 è all'indice 13.5: `Block_3` (baricentro a 12) è il blocco più vicino al centro reale.

> **Esclusione empirica di Block_5**: Il pilota informale del 18/09 aveva testato `Block_5`, ma `Block_5` è adiacente a `Block_6`. La decomposizione di simmetria eseguita nel secondo emendamento del verdetto (`docs/pilot_rotations_verdict.md` §A) ha dimostrato che `Block_5` possiede una quota antisimmetrica pari a **0.57**, persino superiore a quella di `Block_6` (**0.52**). Questo dato numerico conferma che `Block_5` è funzionalmente agganciato e contaminato dalla dinamica terminale di `Block_6`. `Block_3` è l'unico candidato centrale topograficamente e funzionalmente non contaminato.

> **Nota metodologica sui dati pilota di Block_3**: Nel file storico `data/pilot_rotations.csv`, il gruppo `Block_3` contiene 90 righe invece di 36, poiché 54 derivano da famiglie di rotazione disomogenee (`structural_rot_y`, `tensor_rot_x`, $\pm 20^\circ$). Nessuna stima o valore a priori deve essere estratto da quel file per `Block_3`. Il presente esperimento genera l'intero braccio sperimentale di `Block_3` ex-novo, a parità di campionatore e displacement.

---

## 1. Ipotesi Primarie Riscritte contro il Nullo Appaiato (Anti-Scramble)

Nello spazio primario **Tessitura** (`glcm_contrast`, `glcm_homogeneity`, `lbp_entropy`, z-standardizzate per stile), con la formula Leave-One-Out cross-prompt congelata in `docs/prereg_rotations_block1_vs_block6.md` §1:

$$V_{b,b'}(p) = \tfrac{1}{2}\Big[\big(\cos(A_b(p), \bar A_{b,-p}) - \cos(A_b(p), \bar A_{b',-p})\big) + \big(\cos(A_{b'}(p), \bar A_{b',-p}) - \cos(A_{b'}(p), \bar A_{b,-p})\big)\Big]$$

### Perché il confronto contro zero è metodologicamente non valido (Pitfall 63)
In `Block_1 vs Block_6`, il controllo nullo formato da due perturbazioni stocastiche indipendenti allo stesso $D = 0.04500$ ha registrato un vantaggio medio intrinseco di $\bar{V}_{\text{scramble}} = \mathbf{+0.5323}$ ($p = 0.00195$). Poiché qualsiasi matrice di pesi fissa genera un'auto-somiglianza strutturale non nulla tra prompt, il vero pavimento non è 0, ma $\approx +0.5$. Dichiarare l'ipotesi primaria come "$\bar{V} > 0$" significherebbe farla passare quasi per costruzione (**Pitfall 63: ogni statistica derivata richiede il proprio nullo empirico**).

### Definizione formale delle Ipotesi Primarie
Le due ipotesi primarie sono definite come **contrasti appaiati rispetto allo scramble corrispondente ad ancoraggio incrociato**:

$$\Delta \bar{V}_{1,3} = \frac{1}{10} \sum_{p=1}^{10} \Big( V_{1,3}(p) - V_{\text{scr}(1,3)}(p) \Big) > 0$$

$$\Delta \bar{V}_{3,6} = \frac{1}{10} \sum_{p=1}^{10} \Big( V_{3,6}(p) - V_{\text{scr}(3,6)}(p) \Big) > 0$$

dove:
* $V_{\text{scr}(1,3)}(p)$ è il vantaggio calcolato tra `scramble_A` (ancorato su Block_1) e `scramble_C` (ancorato su Block_3).
* $V_{\text{scr}(3,6)}(p)$ è il vantaggio calcolato tra `scramble_C` (ancorato su Block_3) e `scramble_A` (o `scramble_B`, ancorato su Block_1).

**Procedura di Test**:
* Test di permutazione esatta a scambio di segno (sign-flip test a due code) sui 10 delta appaiati $\Delta V(p) = V(p) - V_{\text{scr}}(p)$.
* Pavimento teorico esatto: $2 / 2^{10} = 2 / 1024 = \mathbf{0.00195}$.
* Correzione per molteplicità: procedura sequenziale di Holm a $\alpha = 0.05$ sulla famiglia dei 2 test primari.

*(Il valore $\bar{V}_{1,6} = +1.0386$ contro $\bar{V}_{\text{scr}(1,6)} = +0.5323$, $\Delta \bar{V}_{1,6} = +0.5063$, $p=0.00195$, è già congelato e viene utilizzato come termine di paragone).*

---

## 2. Criterio di Decisione con Margine di Equivalenza Dichiarato

Per evitare il **Pitfall 61** (regole decisionali basate su soglie qualitative post-hoc o più strette del rumore di stima), fissiamo a priori il **margine di equivalenza**:

$$\Delta_{\text{equiv}} = \mathbf{0.25}$$

**Giustificazione statistica**: Derivato direttamente dalla dispersione empirica cross-stile osservata in `Block_1 vs Block_6` ($\text{SD} \approx 0.12$, intervallo $[+0.73, +1.17]$). Il margine di $0.25$ corrisponde a circa due deviazioni standard di variabilità campionaria tra regimi stilistici ($\sim 2 \times \text{SD}$).

### Tavola di Decidibilità a 4 Vie

| Pattern Osservato | Condizioni Matematiche | Interpretazione Teorica |
|---|---|---|
| **1. Centro Piatto / Prossimità ai Confini** | $\Delta \bar{V}_{1,3} \le 0$ **oppure** $\Delta \bar{V}_{3,6} \le 0$ *(almeno uno dei due non supera significativamente il rumore di scramble)* | L'effetto è legato unicamente all'ingresso e all'uscita della rete (strati terminali). Nessuna specializzazione funzionale distribuita. |
| **2. Gradiente Continuo di Profondità** | $\Delta \bar{V}_{1,3} > 0$ **e** $\Delta \bar{V}_{3,6} > 0$, con $|\bar{V}_{1,3} - \bar{V}_{3,6}| \le 0.25$ **e** $\bar{V}_{1,6} - \max(\bar{V}_{1,3}, \bar{V}_{3,6}) > 0.25$ | Il vantaggio scala monotonamente con la distanza topografica tra blocchi lungo la profondità del DiT. |
| **3. Specializzazione Discreta Idiosincratica** | $\Delta \bar{V}_{1,3} > 0$ **e** $\Delta \bar{V}_{3,6} > 0$, con $|\bar{V}_{1,3} - \bar{V}_{1,6}| \le 0.25$ **e** $|\bar{V}_{3,6} - \bar{V}_{1,6}| \le 0.25$ | Più di due direzioni ortogonali autonome. Il centro possiede una propria traiettoria stilistica forte e distinguibile tanto quanto gli estremi. |
| **4. Asimmetria di Propagazione** | Uno solo supera il nullo scramble, **oppure** $|\bar{V}_{1,3} - \bar{V}_{3,6}| > 0.25$ | La dinamica di uno dei due confini (ingresso o uscita) penetra nel centro molto più profondamente dell'altra. |

---

## 3. Matrice dei Dati e Adozione dell'Opzione (a)

### Riuso delle 210 immagini esistenti (Zero spreco computazionale)
Le 210 immagini generate per `Block_1 vs Block_6` (10 stili $\times$ 3 seed $\times$ 7 condizioni) rimangono identiche e vengono riutilizzate al 100%:
* `baseline` (30 img)
* `Block_1_pos` (+23.69°, 30 img)
* `Block_1_neg` (-23.69°, 30 img)
* `Block_6_pos` (+32.21°, 30 img)
* `Block_6_neg` (-32.21°, 30 img)
* `scramble_A` (Rademacher seed 20260919 su Block_1, 30 img)
* `scramble_B` (Rademacher seed 20260920 su Block_1, 30 img)

### Adozione formale dell'Opzione (a): 120 Nuove Generazioni
Rifiutata l'opzione (b) (che avrebbe introdotto un'asimmetria di nullo non controllata), si generano 4 condizioni nuove su `Block_3` a parità esatta di parametri (10 stili $\times$ 3 seed = 120 immagini):
1. `Block_3_pos` ($\theta_3 = +25.24^\circ$, 30 immagini)
2. `Block_3_neg` ($\theta_3 = -25.24^\circ$, 30 immagini)
3. `scramble_C` (Rademacher seed 20260922 su 40 tensori 2D di Block_3, 30 immagini)
4. `scramble_D` (Rademacher seed 20260923 su 40 tensori 2D di Block_3, 30 immagini)

**I tre pavimenti nulli ottenuti**:
1. $\bar{V}_{\text{scr}}(1,1) = \bar{V}_{A,B}$ (nullo omologo Block_1: $+0.5323$)
2. $\bar{V}_{\text{scr}}(3,3) = \bar{V}_{C,D}$ (nullo omologo Block_3)
3. $\bar{V}_{\text{scr}}(1,3) = \bar{V}_{A,C}$ (nullo incrociato Block_1 vs Block_3, nullo esatto per $V_{1,3}$ e $V_{3,6}$)

---

## 4. Calibrazione Offline Congelata ($D_{\text{modello}} = 0.04500$)

Eseguita su `krea2_turbo_bf16.safetensors` tramite [`experiments/calibrate_block3.py`](file:///c:/Users/aless/Desktop/comfyui-pilot/experiments/calibrate_block3.py) e salvata in [`matched_rotation_calibration.json`](file:///c:/Users/aless/Desktop/comfyui-pilot/matched_rotation_calibration.json):

* **Norma complessiva modello**: $\|W_{\text{modello}}\|_F = 5009.4475$
* **Target $D_{\text{modello}}$ prefissato**: $0.045001$
* **Block_1 (All 0–4)**: $\theta_1 = 23.69^\circ \rightarrow D = 0.045002$ (40 tensori 2D, $\|\Delta W\| = 225.4332$)
* **Block_3 (All 10–14)**: $\theta_3 = \mathbf{25.24^\circ} \rightarrow D = \mathbf{0.045006}$ (40 tensori 2D, $\|\Delta W\| = 225.4548$)
* **Block_6 (All 24–27)**: $\theta_6 = 32.21^\circ \rightarrow D = 0.045001$ (32 tensori 2D, $\|\Delta W\| = 225.4305$)

**Verifica della tolleranza inter-blocco**:
* $|D_3 - D_1| = |0.045006 - 0.045002| = \mathbf{0.000004} \le 0.0002$
* $|D_3 - D_6| = |0.045006 - 0.045001| = \mathbf{0.000005} \le 0.0002$
* **Cancello di tolleranza superato al 100%** (scarto $< 5 \times 10^{-6}$).

---

## 5. Cancelli di Accettazione

1. [x] **Calibrazione offline verificata**: $|D_3 - D_1| \le 0.0002$ e $|D_3 - D_6| \le 0.0002$ ($\Delta D = 0.000005$).
2. [x] **Decisione metodologica (a) adottata**: 120 generazioni nuove deliberate per garantire il nullo cross-anchored.
3. [x] **Definizione dei primari corretta contro il nullo scramble**: $\Delta \bar{V} > 0$ su test sign-flip appaiato (Pitfall 63 evitato).
4. [x] **Margine di equivalenza pre-dichiarato**: $\Delta_{\text{equiv}} = 0.25$ (Pitfall 61 evitato).
5. [ ] **120 nuove immagini generate** e verificate nella coda ComfyUI a 9 passi `euler_ancestral`.
6. [ ] **Estrazione feature di Tessitura** (`glcm_contrast`, `glcm_homogeneity`, `lbp_entropy`) eseguita e verificata con contact sheet visivo QC.
7. [ ] **Calcolo di $\Delta \bar{V}_{1,3}$ e $\Delta \bar{V}_{3,6}$** con pavimento teorico $p = 0.00195$.
8. [ ] **Applicazione letterale dell'albero decisionale a 4 vie** del §2.
9. [ ] **Integrazione del report in `docs/rotations_triangolo_block1_block3_block6_results.md`** prima di qualsiasi modifica al README.


---

## Nota di stato — 2026-09-21: congelata CON DEVIAZIONI

Il documento e' stato rispettato nel disegno — opzione (a), scramble cross-anchored, margine di
equivalenza dichiarato, displacement appaiato a $D = 0.04500$ — e ha **tre buchi di specifica**
che sono emersi solo in fase di lettura. Sono registrati qui perche' la prossima versione li
chiuda prima di renderizzare, non dopo.

1. **Non dice quale coppia cross sia «il pavimento».** Le quattro coppie `A`-`C`, `A`-`D`,
   `B`-`C`, `B`-`D` sono nulli scambiabili per costruzione, e la scelta fra loro decideva il
   verdetto da sola: la coppia usata vale −0.0396 e la media delle quattro +0.5630. La regola
   di aggregazione dei nulli va fissata qui, insieme alla statistica. Pitfall 68.

2. **Non prevede nessuno scramble ancorato su `Block_6`.** `A` e `B` stanno su `Block_1`, `C` e
   `D` su `Block_3`, quindi il lato `Block_3`-vs-`Block_6` non ha un nullo proprio e non e'
   misurabile con questo corpus. Servono `scramble_E`/`scramble_F` su `Block_6`, 60 immagini.
   Pitfall 69.

3. **Il margine di equivalenza $\Delta_{\text{equiv}} = 0.25$ non era calibrato.** E' stato
   fissato in conversazione senza derivarlo dalla dispersione dei dieci stili del banco
   `Block_1` vs `Block_6`, che era gia' disponibile. La diramazione che ne dipendeva e' stata
   decisa da 0.2737 contro 0.25 — un margine di 0.0237 su una differenza con p = 0.0586.
   Pitfall 61.

Esito dopo la revisione: `docs/rotations_triangolo_block1_block3_block6_results.md` §1-bis.
Il verdetto e' **non determinato**, non «4. Asimmetria di Propagazione».
