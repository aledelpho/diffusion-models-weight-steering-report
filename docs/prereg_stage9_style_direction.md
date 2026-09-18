# Pre-registrazione — Stage 9: Dipendenza della Direzione di Steering dallo Stile Dichiarato

**Data di deposito originario**: 2026-09-18 (ore 08:55)  
**Data emendamento metodologico (Affidabilità & Disattenuazione)**: 2026-09-18 (ore 11:25, congelato mentre la coda ComfyUI è in corso: 220/300 render completati, prima di qualsiasi estrazione o analisi dei dati)  
**Stato**: Formalmente congelato  
**Corpus target**: Stage 9 (8 varianti di stile, stesso soggetto) vs Stage 5/6 (18 varianti di soggetto, stesso stile)  

---

## 1. Ipotesi Scientifica

L'intervento sui pesi (steering tramite `preset_pos`, `blockshuf_neg`, `rand_pos`) produce uno spostamento cromatico e strutturale nello spazio latente del modello.
L'ipotesi di Stage 9 è che:
> **La direzione vettoriale dello spostamento impresso dalla perturbazione dei pesi dipende dallo stile visivo dichiarato nel prompt in misura significativamente maggiore rispetto a quanto dipenda dal soggetto ritratto.**

### Termine di Confronto (Baseline Empirica Esistente):
- **Varianti di Stile (Stage 9, $N=8$)**: Prompt identici parola per parola nel soggetto (*"a yellow and blue rally car cruising in a deep jungle..."*), variati unicamente nella clausola stilistica iniziale (fotografia, acquerello, low-poly, claymation, ukiyo-e, pixel art, vetrata, carboncino).
- **Varianti di Soggetto (Stage 5 e Stage 6, $N=18$)**: Prompt che condividono la medesima clausola stilistica (*"Western comics style, bold ink outlines, hatched shadows..."*) e differiscono nel soggetto ritratto (nani, elfi, goblin, streghe, tiefling, ecc.).

Se l'ipotesi regge:
$$\bar{C}_{\text{stile}} < \bar{C}_{\text{soggetto}}$$
ovvero, il coseno direzionale medio tra le risposte dei diversi stili è inferiore al coseno direzionale medio tra le risposte dei diversi soggetti sotto la stessa perturbazione di pesi.

---

## 2. Definizione dei Quattro Spazi di Misura

Per evitare l'errore sistematico derivante da prompt che impongono vincoli cromatici intrinseci (es. *monochromatic* nel carboncino o *limited color palette* nella pixel art, che riducono artificialmente i gradi di libertà nel piano $a^*b^*$), la misura del coseno viene calcolata e riportata separatamente in quattro spazi:

1. **Spazio 1 — 24 Dimensioni Complete $(L^*, a^*, b^*)$**:
   - 8 slot cromatici (carta, inchiostro e 6 swatch estratti da `analyze_palette`).
   - Coordinate $a^*$ e $b^*$ calcolate analiticamente da croma $C$ e tinta circolare $h$ in radianti:
     $$a^* = C \cos(h), \quad b^* = C \sin(h)$$
   - *Nota metodologica*: la tinta grezza in gradi (`*_hue_deg`) non viene mai sottratta o mediata linearmente.
2. **Spazio 2 — 8 Dimensioni Solo Luminanza $(L^*)$**:
   - Estrazione dei soli canali $L^*$ degli 8 slot. Misura la redistribuzione tonale indipendentemente dal colore.
3. **Spazio 3 — 16 Dimensioni Cromatiche Pure $(a^*, b^*)$**:
   - Esclusione della componente di luminanza $L^*$. Isola la rotazione di tinta e saturazione.
4. **Spazio 4 — 5 Dimensioni Asse di Tessitura (Texture)**:
   - Feature strutturali calcolate da `style_features.py`:
     - `crosshatch_entropy_mean`
     - `edge_density`
     - `stroke_width_cv`
     - `contour_n_components`
     - `lbp_entropy`
   - *Ruolo diagnostico dirimente*: nello spazio di tessitura i vincoli cromatici del prompt non hanno influenza. Se la divergenza tra stili compare solo nel cromatico ($a^*b^*$) ma svanisce nella tessitura, l'effetto è attribuito al vincolo linguistico del prompt. Se regge anche sulla tessitura, la dipendenza stilistica dello steering è geometricamente reale.

---

## 3. Protocollo di Standardizzazione e Unità di Analisi

- **Standardizzazione Congiunta (Single Common Scale)**:
  Tutti i vettori differenza $\Delta = \vec{v}_{\text{trattamento}} - \vec{v}_{\text{baseline}}$ vengono standardizzati z-score **una sola volta** sulla distribuzione unita dei due corpora combinati ($\text{Stage 9} \cup \text{Stage 5/6}$). È severamente vietato standardizzare i corpora separatamente (evitamento della *pitfall 33*).
- **Unità di Analisi**: Livello prompt.
  Per ciascun prompt e condizione, le feature dei 5 seed standard (`[42, 777, 1337, 9999, 4242145]`) vengono mediate prima del calcolo dei coseni a coppie (evitamento della *pitfall 17*).

---

## 4. Correzione della Risoluzione della Permutazione (Emendamento 3)

Nella versione preliminare era stato erroneamente indicato un pavimento di $2/2^8 = 0.0078$, corrispondente a un test di sign-flip appaiato.
In questo disegno sperimentale a due gruppi, si permutano le **etichette di corpus** fra gli $8$ prompt di stile e i $18$ prompt di soggetto ($N_{tot} = 26$ prompt).
- Numero esatto di partizioni distinte:
  $$\binom{26}{8} = 1\,562\,275$$
- Risoluzione statistica con 20.000 estrazioni Monte Carlo:
  $$\text{risoluzione} \approx \frac{1}{20\,001} \approx 5 \times 10^{-5}$$
Il pavimento reale della significatività è due ordini di grandezza più profondo. La soglia decisionale resta fissata rigidamente ad $\alpha = 0.05$.

---

## 5. Affidabilità di Misura Split-Half (Emendamento 1)

Un coseno tra risposte è matematicamente attenuato dall'errore di misura. Se il corpus delle varianti di stile (eterogeneo: foto, pixel art, carboncino) presenta una varianza inter-seed maggiore rispetto al corpus dei soggetti (omogeneo: ritratti comic), esso risulterà meccanicamente più attenuato, producendo una coerenza apparente inferiore per puro artefatto psicometrico.

Per quantificare e isolare questo fattore:
- Per ciascun corpus, per ciascuna condizione e per ciascuno dei 4 spazi, viene calcolata l'**affidabilità split-half**:
  1. I 5 seed vengono partizionati in 2 contro 3 su tutti i $\binom{5}{2} = 10$ split possibili.
  2. Per ogni split si calcolano i due vettori di differenza dalla baseline indipendenti.
  3. Si calcola il coseno direzionale tra le due metà e si media su tutti i 10 split e su tutti i prompt del corpus: $r_{2v3}$.
  4. Si stima l'affidabilità a 5 seed tramite formula di Spearman-Brown:
     $$r_5 = \frac{2 r_{2v3}}{1 + r_{2v3}}$$
- Le metriche di affidabilità vengono tabulate e pubblicate come misura primaria di validità dello strumento.

---

## 6. Statistica Decisionale Disattenuata (Emendamento 2)

La statistica di decisione primaria dell'esperimento viene corretta per l'affidabilità di ciascun corpus:

$$\Delta \bar{C}_{\text{corretto}} = \frac{\bar{C}_{\text{soggetto}}}{r_{\text{soggetto}}} - \frac{\bar{C}_{\text{stile}}}{r_{\text{stile}}}$$

dove $r_{\text{soggetto}}$ e $r_{\text{stile}}$ sono le affidabilità a 5 seed ($r_5$) ricalcolate dinamicamente **all'interno di ciascuna iterazione di permutazione**.
Poiché sotto permutazione i 5 seed di un prompt viaggiano unitamente al prompt stesso, l'affidabilità del raggruppamento permutato è endogena e non dipende da costanti arbitrarie esterne.

### Criterio di Decisione:
- Vengono riportate sia la differenza grezza $\Delta \bar{C}$ sia la differenza corretta $\Delta \bar{C}_{\text{corretto}}$.
- **Regola di Conferma**: L'ipotesi $\bar{C}_{\text{stile}} < \bar{C}_{\text{soggetto}}$ è considerata confermata **solo se sopravvive con $p < 0.05$ sulla statistica disattenuata $\Delta \bar{C}_{\text{corretto}}$**.
- Se l'effetto è significativo solo sulla statistica grezza ma svanisce su quella disattenuata, il verdetto scientifico formale sarà: *"La minore coerenza fra stili è un artefatto di attenuazione dovuto alla maggiore varianza di misura dei prompt eterogenei"*.

---

## 7. Limiti Noti di Scambiabilità (Emendamento 4)

Si dichiara a priori che i due corpora non differiscono esclusivamente per la dimensione "stile vs soggetto". Essi differiscono anche per:
- Soggetto iconografico (un'auto da rally nella giungla per lo stile, ritratti singoli a mezzo busto per i soggetti).
- Data di render e stage sperimentale.

Il test di permutazione respinge l'ipotesi che l'etichetta di corpus sia priva di informazione; l'attribuzione causale allo stile poggia sulla coerenza del pattern attraverso i diversi spazi (specialmente lo Spazio 4 di tessitura) e sulla dose-risposta.

---

## 8. Gate di Qualità sull'Ampiezza 2.0x (Emendamento 5)

L'ampiezza 2.0x corrisponde a uno spostamento $D \approx 0.108$, situato oltre il picco nominale di saturazione della dose-risposta ($0.75 - 1.00$).
- Viene applicato a priori lo stesso gate dello Stage 8 Arm C: scostamento della media di condizione dalla media baseline su `edge_density` e `lbp_entropy` superiore a $3 \times \sigma_{\text{baseline}}$.
- Le celle che violano la soglia $3\sigma$ vengono censite e marcate come **"Fuori range di displacement utilizzabile (Degradate)"** prima di esaminare i coseni.
- Tali celle non vengono scartate a posteriori: il conteggio delle celle degradate a 2.0x costituisce di per sé una misura di stabilità geometrica del modello ad ampiezze sovra-sature.
