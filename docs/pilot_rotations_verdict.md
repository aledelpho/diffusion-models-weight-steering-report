# Ri-analisi delle rotazioni dei benchmark pilota — Verdetto

**Data**: 2026-09-18  
**Ambito**: Analisi offline su dati preesistenti (9 report HTML di benchmark pilota, zero generazioni nuove).  
**Script di riferimento**:  
- Estrazione dati: [`experiments/extract_pilot_benchmarks.py`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/experiments/extract_pilot_benchmarks.py)
- Calcolo displacement Frobenius: [`experiments/compute_rotation_displacement.py`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/experiments/compute_rotation_displacement.py)
- Analisi statistica: [`experiments/analyze_pilot_rotations.py`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/experiments/analyze_pilot_rotations.py)
- Dati generati: [`data/pilot_rotations.csv`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/data/pilot_rotations.csv), [`data/pilot_macro.csv`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/data/pilot_macro.csv), [`data/pilot_rotation_displacement.csv`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/data/pilot_rotation_displacement.csv)

---

## 1. Il verdetto in sintesi

### **Esito: Effetto di Posizione (Esito 1, confermato su CLIP-Dist), condizionato a riserva metrica (Esito 3)**

L'ipotesi nulla di default — che il profilo a "U" (con **Block_1** e **Block_6** che rispondono con distanze CLIP 3–4 volte superiori ai blocchi centrali 2–5) fosse un semplice artefatto di ampiezza spettrale $D$ — **è categoricamente respinta dai dati**.

1. **Il profilo sopravvive interamente alla correzione per displacement**: regredendo la `CLIP-Dist` sul vero spostamento relativo di Frobenius ($D_{\text{blocco}}$ o $D_{\text{modello}}$), i residui medi per blocco mantengono lo stesso identico pattern:
   - `Block_1`: residuo positivo $+0.0777$ su $D_{\text{blocco}}$ ($+0.0969$ su $D_{\text{modello}}$)
   - `Block_2`: residuo negativo $-0.0689$ su $D_{\text{blocco}}$ ($-0.1017$ su $D_{\text{modello}}$)
   - `Block_3`: residuo negativo $-0.0570$ su $D_{\text{blocco}}$ ($-0.0958$ su $D_{\text{modello}}$)
   - `Block_4`: residuo negativo $-0.0672$ su $D_{\text{blocco}}$ ($-0.0906$ su $D_{\text{modello}}$)
   - `Block_5`: residuo negativo $-0.0893$ su $D_{\text{blocco}}$ ($-0.0854$ su $D_{\text{modello}}$)
   - `Block_6`: residuo positivo $+0.2047$ su $D_{\text{blocco}}$ ($+0.2764$ su $D_{\text{modello}}$)
2. **Il contrasto Estremi vs Centrali è perfetto e significativo al pavimento teorico**:
   - In **tutti e 7 i prompt indipendenti**, il contrasto sui residui (Estremi $-$ Centrali) è strettamente positivo ($7/7$, segni `[+1, +1, +1, +1, +1, +1, +1]`).
   - Test di permutazione esatta a scambio di segno (sign-flip test, $n = 7$ prompt):  
     **$p = 0.0156$** (pavimento teorico esatto: $2/2^7 = 2/128 = 0.0156$).
3. **La fisica dei tensori rafforza l'effetto anziché spiegarlo**:
   - A causa della partizione macro-blocchi sui 28 blocchi di Krea-2 ($5+5+5+5+4+4$), `Block_6` tocca solo **32 matrici 2D**, contro le **40 matrici** dei Blocchi 1–4.
   - Sull'intero modello DiT, ruotare `Block_6` di $30^\circ$ genera uno spostamento relativo $D_{\text{modello}} = 0.041988$, che è **inferiore** a quello di `Block_2` ($D_{\text{modello}} = 0.058436$).
   - Nonostante muova *meno massa spettrale* su *meno tensori*, `Block_6` induce una variazione semantica quadrupla rispetto a `Block_2` ($0.4623$ vs $0.1234$).

Tuttavia, il verdetto **non** può essere elevato a scoperta universale sull'architettura senza una pre-registrazione dedicata con metriche di tratto e palette, a causa delle note cecità di OpenCLIP ViT-B-32 documentate nel progetto.

---

## 2. Dati quantitativi verificati

### 2.1 Tabella aggregata per prompt ($n = 7$)
I 9 report contengono 7 prompt unici (i tre report di `tiefling` con seed 4242145, 1337 e 42 sono stati mediati preventivamente prima di ogni aggregazione statistica, pitfall 17).

| Blocco | −30° | −15° | +15° | +30° | Media \|angolo\| | Matrici 2D | $D_{\text{blocco}}$ (30°) | $D_{\text{modello}}$ (30°) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Block_1** | 0.5776 | 0.1355 | 0.1719 | 0.3866 | **0.3179** | 40 | 0.146978 | 0.056740 |
| Block_2 | 0.1441 | 0.1087 | 0.0928 | 0.1478 | 0.1234 | 40 | 0.125895 | 0.058436 |
| Block_3 | 0.1335 | 0.1019 | 0.0963 | 0.1366 | 0.1171 | 40 | 0.117907 | 0.053313 |
| Block_4 | 0.1188 | 0.1030 | 0.0934 | 0.1499 | 0.1163 | 40 | 0.122046 | 0.050803 |
| Block_5 | 0.1406 | 0.0769 | 0.0721 | 0.1255 | 0.1038 | 32 | 0.126233 | 0.043366 |
| **Block_6** | 0.6152 | 0.4133 | 0.2578 | 0.5632 | **0.4623** | 32 | 0.154651 | 0.041988 |

### 2.2 Regressione OLS di `CLIP-Dist` su Displacement ($n = 168$ punti appaiati)

1. **Su $D_{\text{modello}}$**:
   $$\text{CLIP-Dist} = 0.0860 + 3.1614 \cdot D_{\text{modello}}, \quad R^2 = 0.0615$$
   Il displacement complessivo sul modello spiega appena il $6.15\%$ della varianza.
2. **Su $D_{\text{blocco}}$**:
   $$\text{CLIP-Dist} = -0.0941 + 3.0242 \cdot D_{\text{blocco}}, \quad R^2 = 0.3665$$
   Il displacement locale del blocco spiega il $36.65\%$ della varianza. Il restante $63.35\%$ è dominato dalla posizione del blocco.

### 2.3 Contrasti Estremi vs Centrali per Prompt ($n = 7$)

Per ciascun prompt $p$, calcolando la differenza tra il comportamento degli estremi (`Block_1`, `Block_6`) e dei blocchi centrali (`Block_2`..`Block_5`):

| Prompt ID | $\Delta$ Grezzo | $\Delta$ Residui (su $D_{\text{modello}}$) | $\Delta$ Residui (su $D_{\text{blocco}}$) | Segno |
| :--- | :---: | :---: | :---: | :---: |
| `african_scientist` | +0.3307 | +0.3357 | +0.2675 | $+$ |
| `combat_robot` | +0.2439 | +0.2489 | +0.1807 | $+$ |
| `elf_brawler` | +0.2821 | +0.2871 | +0.2188 | $+$ |
| `flag` | +0.2600 | +0.2651 | +0.1968 | $+$ |
| `preraphaelite_altar` | +0.2858 | +0.2908 | +0.2225 | $+$ |
| `tiefling` (media 3 seed) | +0.2706 | +0.2756 | +0.2073 | $+$ |
| `troll_shaman` | +0.2519 | +0.2569 | +0.1887 | $+$ |
| **Media campionaria** | **+0.2750** | **+0.2800** | **+0.2118** | **7/7** |
| **$p$-value permutazione esatta** | **0.0156** | **0.0156** | **0.0156** | — |
| **Pavimento teorico ($2/2^7$)** | **0.0156** | **0.0156** | **0.0156** | — |

---

## 3. Lavoro D: Decomposizione di simmetria e verso di rotazione

La matematica della trasformazione è strettamente simmetrica nel formalismo Lie: ruotare di $-\theta$ o di $+\theta$ genera esattamente lo stesso displacement di Frobenius normativo ($D(-\theta) = D(+\theta)$, verificato a precisione macchina con scarto $< 10^{-6}$).

Tuttavia, la risposta empirica nella generazione delle immagini mostra una forte **antisimmetria**:

$$S = \frac{d^+ + d^-}{2}, \quad A = \frac{d^+ - d^-}{2}, \quad A_{\text{diff}} = d^+ - d^-$$

| Blocco | $S (15^\circ)$ | $A (15^\circ)$ | $S (30^\circ)$ | $A (30^\circ)$ | $A_{\text{diff}}$ medio | $p$-value permutazione | Segni prompt |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Block_1** | 0.1537 | +0.0182 | 0.4821 | −0.0955 | **−0.0773** | 0.0312 | `[-1, -1, -1, -1, -1, +1, -1]` |
| Block_2 | 0.1007 | −0.0080 | 0.1460 | +0.0018 | −0.0062 | 0.5156 | `[-1, +1, +1, -1, -1, -1, -1]` |
| Block_3 | 0.0991 | −0.0028 | 0.1350 | +0.0015 | −0.0012 | 0.8906 | `[+1, +1, +1, -1, -1, -1, -1]` |
| Block_4 | 0.0982 | −0.0048 | 0.1344 | +0.0156 | +0.0108 | 0.4531 | `[-1, -1, +1, +1, +1, +1, +1]` |
| Block_5 | 0.0745 | −0.0024 | 0.1331 | −0.0076 | −0.0100 | 0.3438 | `[+1, +1, +1, -1, -1, -1, +1]` |
| **Block_6** | 0.3355 | −0.0778 | 0.5892 | −0.0260 | **−0.1038** | **0.0156** | `[-1, -1, -1, -1, -1, -1, -1]` |
| **Globale (media 6 blocchi)** | — | — | — | — | **−0.0313** | **0.0156** | `[-1, -1, -1, -1, -1, -1, -1]` |

*(Pavimento teorico per tutti i test di permutazione: $2/2^7 = 0.0156$)*.

### Interpretazione dell'antisimmetria
1. Ruotare nel verso negativo ($-\theta$) produce una deviazione semantica sistematicamente più marcata rispetto al verso positivo ($+\theta$) in **7 prompt su 7** a livello globale ($p = 0.0156$).
2. L'effetto è concentrato specificamente nei due blocchi estremi: in `Block_6`, l'antisimmetria è unanime su tutti i 7 prompt ($A_{\text{diff}} = -0.1038, p = 0.0156$); in `Block_1`, 6 prompt su 7 sono negativi ($A_{\text{diff}} = -0.0773, p = 0.0312$). Nei blocchi centrali 2–5, $A_{\text{diff}}$ è trascurabile ($-0.001$ a $+0.010$) e privo di significatività.
3. Questo indica che lo spazio dominante dei pesi di `Block_1` e `Block_6` non è orientato isotropicamente rispetto alla traiettoria del campionamento di Krea-2: la rotazione in senso antiorario incrocia traiettorie di de-noising più caotiche rispetto alla rotazione oraria.

---

## 4. Le sei limitazioni metodologiche (da dichiarare ad alta voce)

Come richiesto dai vincoli di integrità del brief (§1 e §3), le conclusioni di questo documento sono soggette alle seguenti limitazioni strutturali e non possono essere ignorate:

1. **L'angolo non è lo spostamento**: Sebbene abbiamo verificato offline che $D$ non spiega l'effetto estremi (il quale sopravvive nei residui), confermiamo che il parametro $\theta$ in gradi non è una misura conservata di spostamento tra blocchi diversi, poiché la massa spettrale nel sottospazio di rango 16 varia da blocco a blocco.
2. **OpenCLIP ViT-B-32 è cieco alle proprietà stilistiche fini**: Il benchmark pilota ha utilizzato esclusivamente la metrica $1 - \text{cosine\_similarity}$ su OpenCLIP ViT-B-32 (risoluzione 224×224). Come dimostrato formalmente nella Sezione 4 del notebook principale, questa metrica tende a confondere o invertire le conclusioni su spessore del tratto, tratteggio (cross-hatching) e palette cromatica. L'alta sensibilità di `Block_1` e `Block_6` su CLIP riflette la composizione globale dell'immagine e la coerenza del soggetto, ma non dimostra che questi blocchi siano gli unici a governare lo stile o il tratto.
3. **Assenza di controlli a spostamento appaiato**: Nessuna delle 216 celle di rotazione ha accanto una perturbazione casuale gaussiana (matched random) allo stesso valore esatto di $D$. Di conseguenza, non possiamo stabilire se la risposta di `Block_6` sia specifica della rotazione ortogonale Lie o sia la suscettibilità generica di un blocco di uscita a qualsiasi perturbazione di ampiezza $D$.
4. **Campionamento a 6 passi invece di 9**: Tutte le immagini di questo sweep sono state prodotte a **6 passi Euler Ancestral**, mentre l'intero corpus degli Esperimenti 1 e 2 (Stage 4–12) utilizza **9 passi**. Con un campionatore ancestrale, il numero di passi altera direttamente la sequenza di iniezione del rumore stocastico a ogni step. Queste immagini non sono quindi direttamente confrontabili con i dati degli stadi successivi, nemmeno a parità di seed.
5. **Zero annotazioni umane**: Su 4.505 caselle di spunta presenti nei 9 file HTML, **zero** erano selezionate o salvate. Il benchmark pilota non contiene alcuna valutazione cieca umana.
6. **Disparità nel partizionamento dei macro-blocchi**: Poiché l'architettura Krea-2 DiT conta 28 blocchi transformer (non divisibili per 6), i blocchi sono raggruppati in $5+5+5+5+4+4$. `Block_5` e `Block_6` contengono 4 blocchi (32 matrici 2D ciascuno), mentre `Block_1`..`Block_4` ne contengono 5 (40 matrici 2D). Il fatto che `Block_6` risponda con la sensibilità più elevata nonostante abbia il 20% di matrici in meno e il minor displacement sul modello esclude che il numero di tensori sia la causa, ma sottolinea l'irregolarità della griglia di suddivisione storica.

---

## 5. Stato rispetto al progetto e pre-registrazione

In ottemperanza al cancello di accettazione 7:

> **Isolamento dell'analisi**: Nessuna di queste conclusioni è stata o sarà inserita nel `README.md` principale o in `index.html` come risultato degli Esperimenti 1 o 2. Questo sweep precede la pre-registrazione formale del progetto, utilizza parametri operativi differenti (6 passi vs 9 passi) e manca di controlli appaiati. 

Se in futuro si vorrà convalidare l'effetto di posizione topografica dei blocchi estremi, sarà necessario:
1. Registrare una nuova ipotesi pre-registrata a parte;
2. Calibrare a priori la rotazione in modo da garantire un **$D$ appaiato per costruzione** ($D = 0.0538$ costante su tutti i blocchi);
3. Introdurre il braccio di controllo matched random per ciascun blocco;
4. Misurare gli output con gli estrattori di tratto (`style_features.py`) e colore (`analyze_palette.py`) anziché affidarsi alla sola CLIP-Dist;
5. Eseguire la valutazione cieca umana secondo il protocollo di discriminazione a due alternative forzate (2AFC).
