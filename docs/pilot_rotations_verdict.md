# Ri-analisi delle rotazioni dei benchmark pilota — Verdetto

**Data**: 2026-09-18  
**Ambito**: Analisi offline su dati preesistenti (9 report HTML di benchmark pilota, zero generazioni nuove).  
**Script di riferimento**:  
- Estrazione dati: [`experiments/extract_pilot_benchmarks.py`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/experiments/extract_pilot_benchmarks.py)
- Calcolo displacement Frobenius: [`experiments/compute_rotation_displacement.py`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/experiments/compute_rotation_displacement.py)
- Analisi statistica: [`experiments/analyze_pilot_rotations.py`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/experiments/analyze_pilot_rotations.py)
- Dati generati: [`data/pilot_rotations.csv`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/data/pilot_rotations.csv), [`data/pilot_macro.csv`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/data/pilot_macro.csv), [`data/pilot_rotation_displacement.csv`](file:///C:/Users/aless/Desktop/diffusion-models-weight-steering-report/data/pilot_rotation_displacement.csv)

---

> ⚠️ **Questo verdetto è stato rivisto la sera del 2026-09-18.** Le sezioni 1–5 restano come
> scritte, perché i loro conti sono corretti e sono stati riprodotti in modo indipendente. La loro
> **lettura** però è cambiata su tre punti, e un quarto risultato che i dati contenevano già è stato
> aggiunto. **Leggere l'emendamento in fondo prima di citare qualsiasi cosa da qui.** In breve: non è
> un profilo a U ma un effetto `Block_6`; `Block_1` non replica sullo sweep di ampiezza; i test di
> antisimmetria per blocco non sopravvivono a Holm; e la correzione per $D$ non era un ostacolo
> superato perché non poteva fallire. **E il 2026-09-18 a notte è stato aggiunto un secondo
> emendamento**, dopo che le 216 immagini sono state rimisurate con le feature di tratto e
> palette: la direzione del cambiamento **sembra** dipendere dal blocco e non solo l'ampiezza,
> ma l'affermazione non è sostenibile con sette prompt. Il verdetto operativo è l'ultimo.

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


---

# Emendamento — 2026-09-18, sera

**Aggiunto dopo un controllo indipendente** (`experiments/analyze_pilot_rotations_followup.py`,
output in `data/pilot_rotations_followup.csv`). L'aritmetica della sezione sopra è stata riprodotta e
**torna in ogni cifra**: residui $+0.0777$ e $+0.2047$, contrasto $+0.2118$ sui residui e $+0.2750$ sui
valori grezzi, $p = 0.0156$ con sette segni concordi. Niente di quanto segue corregge un conto.

Quello che segue corregge una **lettura**, su tre punti, e ne aggiunge uno che i dati contenevano
già.

## A. Non è un profilo a U. È un effetto Block_6

Il contrasto pre-registrato fonde `Block_1` e `Block_6` in un'unica categoria "estremi". Quella
categoria è stata scritta quando l'unica cosa nota era la media di `CLIP-Dist`. Scomposta, i due
blocchi hanno firme **diverse**, e la differenza è visibile in tre modi indipendenti.

**1. Lo sweep di ampiezza li separa.** `extract_pilot_benchmarks.py` ha estratto 216 celle di
ampiezza (`Block_N ±1.0/±2.0`) sugli stessi 7 prompt, e l'analisi non le ha usate. Sono una
perturbazione di tipo completamente diverso — un riscalamento, non una rotazione. Se il profilo per
blocco è una proprietà della **posizione**, deve ricomparire lì.

| famiglia | dose | bersaglio | Δ vs centrali | $p$ | prompt concordi |
| --- | --- | --- | --- | --- | --- |
| rotazione | 15° | `Block_1` | $+0.0606$ | **0.0156** | 7/7 |
| rotazione | 15° | `Block_6` | $+0.2424$ | **0.0156** | 7/7 |
| rotazione | 30° | `Block_1` | $+0.3450$ | **0.0156** | 7/7 |
| rotazione | 30° | `Block_6` | $+0.4520$ | **0.0156** | 7/7 |
| ampiezza | ×1 | `Block_1` | $+0.0033$ | 0.2188 | 6/7 |
| ampiezza | ×1 | `Block_6` | $+0.0132$ | 0.2500 | 5/7 |
| ampiezza | ×2 | `Block_1` | $+0.0291$ | 0.0938 | 5/7 |
| ampiezza | ×2 | **`Block_6`** | $\boldsymbol{+0.1011}$ | **0.0156** | **7/7** |

`Block_6` replica. `Block_1` **non replica**: nello sweep di ampiezza è indistinguibile dai blocchi
centrali, a entrambe le dosi.

**2. La forma della dose-risposta li separa.**

| blocco | rotazione 15°→30° | ampiezza ×1→×2 |
| --- | --- | --- |
| `Block_1` | **×3.14** | ×1.72 |
| `Block_2` | ×1.45 | ×1.27 |
| `Block_3` | ×1.36 | ×1.34 |
| `Block_4` | ×1.37 | ×1.32 |
| `Block_5` | ×1.79 | ×1.73 |
| `Block_6` | ×1.76 | ×2.37 |

`Block_6` cresce come gli altri, partendo da un livello più alto: è un **guadagno**. `Block_1` cresce
più del doppio degli altri partendo da un livello quasi normale: è una **non-linearità a grande
angolo**.

**3. La variabilità fra seed li separa.** Nell'unico prompt che ha più di un seed (`tiefling`, 3
seed), `Block_1` ha la deviazione standard fra seed più alta di tutti i blocchi ($0.0467$, contro una
mediana di $0.0224$). Oltre a essere alto a 30°, è anche il più instabile — coerente con una rottura,
non con una risposta stabile.

**Conclusione di questa sezione.** Il risultato pre-registrato resta come scritto: era congelato,
passa, e si riporta. Ma la scomposizione post-hoc dice che passa **sulle spalle di `Block_6`**, e che
`Block_1` in quel contrasto è un passeggero. La formulazione corretta è **effetto `Block_6`**, con
`Block_1` come anomalia separata e di natura diversa, da verificare a parte.

## B. Il residuo su $D$ non era un ostacolo superato: era un ostacolo assente

La sezione sopra presenta "il profilo sopravvive alla correzione per displacement" come la prova che
respinge l'ipotesi di ampiezza. La direzione dei dati rende quel test incapace di fallire per
`Block_6`:

- la pendenza della regressione è **positiva** ($+3.16$ su $d_{\text{modello}}$);
- `Block_6` ha il $d_{\text{modello}}$ **più basso dei sei** ($0.04199$ contro $0.05844$ di
  `Block_2`);
- quindi la regressione gli predice il valore più basso, e ogni eccesso osservato finisce nel residuo
  **amplificato**, non attenuato.

Il fatto grezzo è più forte del residuo e non ha bisogno di regressioni: **`Block_6` muove il modello
il 28% in meno di `Block_2` e cambia l'immagine 3.7 volte di più.** Va riportato così.

C'è anche un'osservazione che la regressione nasconde e che conta: **fra i soli blocchi centrali
(2–5), l'ordinamento di `CLIP-Dist` è spiegato per intero dal displacement** — Spearman
$\rho = +1.000$. Il displacement non è un confondente da rimuovere ovunque: nel centro del modello è
*la* variabile. Sono i due estremi a uscire dalla relazione. Questo è un risultato più informativo di
"i residui restano positivi", ed è quello che va pubblicato.

*(Registrato come pitfall 41: residualizzare su una covariata che ordina i gruppi al contrario.)*

## C. L'antisimmetria: esplorativa, e non è la decomposizione dell'Esperimento 1

Due correzioni.

**Confronti multipli.** I sei test di antisimmetria per blocco **non erano nel brief**. Con Holm sulla
famiglia di sei, nessuno sopravvive:

| blocco | $A$ | $p$ grezzo | $p$ Holm(6) |
| --- | --- | --- | --- |
| `Block_6` | $-0.1038$ | 0.0156 | 0.0938 |
| `Block_1` | $-0.0773$ | 0.0312 | 0.1562 |
| `Block_2`…`Block_5` | $[-0.010, +0.011]$ | 0.34 – 0.89 | 1.0000 |

Vanno riportati come **descrittivi**. L'antisimmetria globale era invece pre-registrata e resta a
$p = 0.0156$ — ma è concentrata nei due blocchi anomali e vicina a zero negli altri quattro, quindi
non è una proprietà generale delle rotazioni: è un'altra faccia della stessa anomalia.

**Categoria sbagliata.** `CLIP-Dist` è una **distanza senza segno** dal baseline.
$A = d(+\theta) - d(-\theta)$ dice "un verso sposta più dell'altro", non "i due versi vanno in
direzioni opposte". La decomposizione $S$/$A$ dell'Esperimento 1 opera su **proiezioni con segno**, ed
esiste proprio perché una distanza senza segno non può osservare un compromesso — è il **pitfall 2** di
questo stesso progetto. Chiamarle la stessa decomposizione è un errore di categoria.

## D. Il pavimento, detto come lo dice il resto del notebook

Ogni test riportato sopra restituisce $p = 0.0156$, che è **esattamente** $2/2^7$. Con sette prompt
tutti concordi il test non può restituire altro. Non è un valore forte né debole: è **saturo**. Il
disegno ha un bit di risoluzione per test — "tutti e sette dalla stessa parte" oppure no — e non
distingue un effetto enorme da uno appena consistente. È la stessa situazione strutturale di §1.3 e
§2.8 del notebook, e va scritta accanto a ogni $p$.

Una cosa che invece dà la scala, e che il disegno permette: nell'unico prompt con tre seed, la
deviazione standard fra seed è $0.0224$, mentre lo scarto `Block_6` − centrali è $0.3472$. **Circa
quindici volte il rumore di seed.** Questo sì che separa "enorme" da "appena consistente", e non
dipende dal pavimento.

## E. L'alternativa che nessuno ha escluso: prossimità all'uscita

`Block_6` sono i blocchi DiT **24–27**, gli ultimi quattro dei ventotto. `Block_1` sono i blocchi
**0–4**, i primi cinque. Una perturbazione applicata vicino all'uscita attraversa meno strati a valle
che possano assorbirla, e i gruppi adiacenti all'ingresso e all'uscita si comportano diversamente dal
centro in quasi ogni transformer. Questo produrrebbe esattamente il profilo osservato **senza alcuna
specializzazione funzionale**.

I dati non separano le due spiegazioni, e non possono, perché `CLIP-Dist` misura **quanto** l'immagine
è cambiata e non **che cosa** è cambiato. Tutto questo sweep può stabilire che alcune posizioni sono
più sensibili. Non può stabilire che posizioni diverse steerino verso cose diverse — che è l'unica
versione della claim che avrebbe conseguenze per il progetto.

Il fatto che il profilo **non** sia monotono nella profondità (i centrali 2→5 *scendono*: $0.1234$,
$0.1171$, $0.1163$, $0.1038$, e quella discesa segue il displacement con $\rho = +1.000$) esclude la
versione più banale — "più sei in fondo, più sposti" — ma non esclude "i due capi sono speciali", che
è una regolarità nota e non una scoperta su questo modello.

## Verdetto rivisto

**Esito 1 limitato a `Block_6`, con riserva metrica (Esito 3) e meccanismo indeterminato.**

Esiste una posizione, `Block_6`, in cui lo stesso tipo di perturbazione produce un cambiamento
d'immagine sproporzionato rispetto allo spostamento che induce nei pesi, e lo fa in due famiglie di
perturbazione indipendenti, in tutti e sette i prompt, con un'ampiezza di circa quindici volte il
rumore di seed. Questo **non** è un artefatto di ampiezza: è l'opposto, perché `Block_6` è il blocco
che sposta meno.

Non è invece stabilito: che `Block_1` condivida il fenomeno (non replica); che la sensibilità di
`Block_6` rifletta una specializzazione funzionale anziché la sua posizione vicino all'uscita (non
distinguibile con una distanza senza segno); che qualcosa di tutto ciò valga fuori da
`CLIP-Dist`, da 6 passi di campionamento e da un solo seed per cella.

**Il prossimo test è economico e decisivo**: le immagini esistono ancora. Rimisurare quelle 216 celle
con `style_features.py` e `analyze_palette.py` — le metriche di tratto e palette del progetto — e
chiedere non "quanto è cambiato" ma "**in che direzione**". Se la direzione differisce per blocco, la
posizione porta informazione. Se cambia solo l'ampiezza, `Block_6` è semplicemente il punto in cui il
modello è più fragile, che è un fatto utile di ingegneria e non una scoperta di interpretabilità.

## Cosa resta fuori dal notebook

Nulla di questo entra in Esperimento 1, 2 o 3. Lo sweep precede ogni pre-registrazione, usa un
campionamento a 6 passi invece di 9, ha un solo seed per cella tranne un prompt, e la sua unica
metrica è dichiarata cieca al §4 del notebook. Nel README e in `index.html` compare come sezione
esplicitamente esplorativa e senza numero di esperimento.


---

# Secondo emendamento — 2026-09-18, notte: la direzione

**Il test che il primo emendamento indicava come "economico e decisivo" è stato fatto.** Le 216
rotazioni e le 9 baseline sono state rimisurate con `style_features.py` e `analyze_palette.py`
(`data/pilot_rotations_style_features.csv`, `data/pilot_rotations_palette_features.csv`, 225 righe
ciascuno). Questa sezione riporta l'analisi indipendente di quei dati
(`experiments/analyze_pilot_rotation_directions.py`), che arriva a una conclusione diversa da
`data/pilot_rotations_directions.csv`.

## A. La decomposizione che prima era impossibile, e che qui cambia tutto

`CLIP-Dist` è una distanza senza segno: poteva dire *quanto* l'immagine si era mossa e mai *verso
dove*. Le feature di tratto e palette hanno un segno, quindi per la prima volta su questo sweep si
applica la decomposizione dell'Esperimento 1:

$$S = \frac{\Delta(+\theta) + \Delta(-\theta)}{2}, \qquad A = \frac{\Delta(+\theta) - \Delta(-\theta)}{2}$$

$S$ è la parte comune ai due versi di rotazione — "quanto". $A$ è la parte che cambia segno con il
verso — "dove".

**`measure_pilot_rotation_directions.py` non fa questa separazione.** Alla riga 226 raggruppa per
`["prompt_id", "block"]` e media sui quattro angoli, fondendo $-30$, $-15$, $+15$, $+30$ in un unico
vettore. Se la risposta è antisimmetrica, quella media **la cancella**. E lo è, in modo sostanziale:

| blocco | $\|S\|$ | $\|A\|$ | quota antisimmetrica |
| --- | --- | --- | --- |
| `Block_1` | 3.862 | 1.908 | 0.33 |
| `Block_2` | 1.122 | 0.512 | 0.31 |
| `Block_3` | 1.495 | 0.453 | 0.23 |
| `Block_4` | 1.196 | 0.602 | 0.33 |
| `Block_5` | 1.351 | 1.774 | **0.57** |
| **`Block_6`** | 5.647 | **6.124** | **0.52** |

*(spazio tessitura, 30°, unità = prompt, standardizzazione unica sulle 225 righe)*

Per `Block_6` la componente antisimmetrica è **la metà più grande delle due**. Mediando sui versi si
è buttata via la parte maggiore del suo segnale, ed è per questo che la matrice dei coseni in
`pilot_rotations_directions.csv` mostra `Block_6` a 0.37–0.66 dagli altri: stava confrontando dei
residui.

Nota che vale per tutto il resto del progetto: **$A$ è invariante alla convenzione di centratura.**
Sottrarre una costante a tutti i delta si cancella in $(\Delta^+ - \Delta^-)/2$. È esattamente la
convenzione che ha affondato lo stage 9 (pitfall 37, segno ribaltato in 11 celle su 18). La sola
statistica a prova di convenzione in tutta quest'area è anche quella che porta il risultato.

## B. I blocchi centrali non hanno una direzione. Ma la ragione potrebbe essere banale

Coerenza fra prompt diversi dentro lo stesso blocco (componente $A$, tessitura, 30°):

| blocco | coerenza interna | ampiezza $\|A\|$ |
| --- | --- | --- |
| `Block_6` | **+0.901** | 6.124 |
| `Block_1` | **+0.650** | 1.908 |
| `Block_5` | +0.438 | 1.774 |
| `Block_4` | +0.155 | 0.602 |
| `Block_2` | −0.024 | 0.512 |
| `Block_3` | −0.010 | 0.453 |

Sembra il risultato: due blocchi hanno una direzione riproducibile, i centrali non ne hanno nessuna.
**E invece è, per metà, una frase sul rapporto segnale/rumore.** Le due colonne sono ordinate quasi
identicamente:

$$\rho(\text{ampiezza}, \text{coerenza}) = +0.943 \ (A), \qquad +1.000 \ (S)$$

Se ogni blocco si muove in una direzione con un rumore di misura simile, quello che si muove dieci
volte tanto avrà automaticamente un coseno molto migliore. "`Block_6` ha una direzione e i centrali
no" è compatibile con "`Block_6` è l'unico che supera il pavimento di rumore". È il **pitfall 36** di
questo progetto — una graduatoria di coerenze misurate con precisioni diverse — sotto un'altra forma.

## C. Il test che aggira il problema, e che dà una risposta

Se il confronto fra un blocco ben misurato e uno mal misurato non è un confronto, allora si
confrontano **solo i blocchi ben misurati fra loro**. Tre superano una coerenza di 0.25 nello spazio
tessitura a 30°: `Block_1`, `Block_5`, `Block_6`.

Test appaiato, unità = prompt: *il vettore di un prompt sotto il blocco X somiglia agli altri prompt
sotto X più di quanto somigli agli altri prompt sotto Y?* Nessuno dei due blocchi è svantaggiato dal
rumore, perché entrambi sono misurati bene.

| confronto | vantaggio stesso-blocco | $p$ | prompt concordi |
| --- | --- | --- | --- |
| `Block_1` vs `Block_6` | **+0.689** | 0.0156 | **7/7** |
| `Block_1` vs `Block_5` | **+0.545** | 0.0156 | **7/7** |
| `Block_5` vs `Block_6` | +0.232 | 0.0469 | 6/7 |

E i coseni grezzi contro il tetto di affidabilità di ciascuna coppia:

| coppia | coseno osservato | tetto $\sqrt{c_1 c_2}$ |
| --- | --- | --- |
| `Block_6` – `Block_1` | +0.146 | +0.766 |
| `Block_6` – `Block_5` | +0.466 | +0.628 |
| `Block_1` – `Block_5` | +0.329 | +0.534 |

**`Block_1` e `Block_6` hanno entrambi una direzione riproducibile e concordano fra loro a 0.146
contro un tetto di 0.766.** Due posti del modello, misurati bene tutti e due, che spingono in
direzioni quasi ortogonali. Questo non è spiegabile con l'ampiezza.

Lo spazio palette dice la stessa cosa più debolmente (`Block_1` vs `Block_6`: $+0.337$, 7/7,
$p = 0.0156$; coseno $+0.403$ contro un tetto di $+0.603$), coerentemente con il fatto — già noto in
questo progetto — che i prompt vincolano il colore e lasciano meno gradi di libertà.

## D. Perché questo resta un'ipotesi e non un risultato

Con $n = 7$ il pavimento della permutazione esatta è $2/2^7 = 0.0156$. Ne segue una cosa aritmetica
che vale la pena scrivere una volta per tutte: **Holm può reggere al massimo tre test nella stessa
famiglia**, perché $0.0156 \times 3 = 0.0469 < 0.05$ ma $0.0156 \times 4 = 0.0625 > 0.05$.

Qui i confronti sono tre nello spazio tessitura e uno nella palette.

- Se tessitura e palette sono **due famiglie separate** — come le dichiara la pre-registrazione dello
  stage 9, che definisce quattro spazi di misura distinti — i tre confronti di tessitura passano Holm
  a esattamente $0.0469$. Sul filo.
- Se sono **una famiglia sola**, sono quattro e non passa niente.

**La famiglia non è mai stata dichiarata.** Il risultato sta esattamente sul confine che quella
dichiarazione avrebbe deciso, e la dichiarazione non c'è. Aggiungici che tutto questo è post-hoc, su
un corpus con un solo seed per cella, a 6 passi di campionamento invece di 9, senza controllo casuale
appaiato in $D$, e la conclusione corretta è: **un'ipotesi ben definita, non un risultato citabile.**

## Verdetto rivisto, secondo giro

**La direzione sembra dipendere dal blocco, non solo l'ampiezza — e il disegno non può sostenere
l'affermazione.**

Quello che è cambiato rispetto al primo emendamento: non è più vero che questo sweep può stabilire
solo una *sensibilità*. La decomposizione antisimmetrica, che nessuno aveva fatto, mostra che i
blocchi ben misurati spingono in direzioni diverse fra loro, e lo fa con effetti grandi e unanimi sui
sette prompt. Ma la moltiplicità e l'assenza di una famiglia dichiarata lo lasciano sul confine.

Resta non stabilito, come nel primo emendamento, se la specialità dei due capi sia una
specializzazione funzionale o la loro vicinanza all'ingresso e all'uscita.

## L'esperimento successivo, adesso completamente specificato

Non serve più esplorare: serve **un** test, dichiarato prima.

> **Primaria, unica.** Nello spazio tessitura, sulla componente antisimmetrica
> $A = (\Delta(+\theta) - \Delta(-\theta))/2$, il vantaggio stesso-blocco fra `Block_1` e `Block_6`
> è positivo. Permutazione esatta a scambio di segno sui prompt, $\alpha = 0.05$.

Con le condizioni che questo corpus non aveva:

- **almeno 10 prompt**, così il pavimento scende a $2/2^{10} = 0.00195$ e la famiglia può ospitare 25
  test invece di 3;
- **almeno 3 seed per cella**, perché qui ce n'è uno e il rumore di seed è stimabile su un solo prompt;
- **displacement appaiato per costruzione** fra i due blocchi, invece di misurato a posteriori;
- **campionamento a 9 passi**, lo stesso del resto del progetto, così il risultato è confrontabile;
- **un controllo casuale allo stesso $D$**, che qui non esiste da nessuna parte;
- la famiglia di test **dichiarata per intero** prima di guardare, e i quattro spazi di misura tenuti
  separati come nella pre-registrazione dello stage 9.

Se quel test passa, "dove spingi decide *cosa* ottieni" diventa una frase con dei dati dietro, e la
metafora del canale smette di essere una figura retorica. Se non passa, `Block_6` è il punto in cui
il modello è più fragile e nient'altro — che è comunque un fatto utile e va scritto.
