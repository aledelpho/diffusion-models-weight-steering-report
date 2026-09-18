# Pre-registrazione — Stage 9: Dipendenza della Direzione di Steering dallo Stile Dichiarato

**Data di deposito**: 2026-09-18  
**Stato**: Congelato prima dell'esecuzione dei render e dell'analisi  
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

## 4. Test Statistico e Regola di Decisione

### Statistica Test:
$$\Delta \bar{C} = \bar{C}_{\text{soggetto}} - \bar{C}_{\text{stile}}$$
dove $\bar{C}$ indica il coseno medio calcolato su tutte le coppie distinte di prompt ($i \neq j$):
$$\bar{C} = \frac{2}{N(N-1)} \sum_{i < j} \frac{\Delta_i \cdot \Delta_j}{\|\Delta_i\|_2 \|\Delta_j\|_2}$$

### Distribuzione Nulla e Significatività:
- Il test è di permutazione unidirezionale esatta / Monte Carlo (20.000 iterazioni) scambiando le etichette di corpus (*stile* vs *soggetto*) tra i prompt.
- Pavimento teorico della permutazione su 8 prompt: $2 / 2^8 = 0.0078$.
- Soglia di significatività fissata a:
  $$\alpha = 0.05$$

### Criteri di Accettazione e Validità:
1. **Conferma Piena**: $\bar{C}_{\text{stile}} < \bar{C}_{\text{soggetto}}$ con $p < 0.05$ **sia** nello Spazio 1 (24-D) **sia** nello Spazio 4 (Tessitura).
2. **Artefatto da Vincolo Cromatico**: $p < 0.05$ nello Spazio 3 ($a^*b^*$) ma $p \ge 0.05$ nello Spazio 4 (Tessitura).
3. **Analisi Dose-Risposta (Verifica Ampiezza 1.0 vs 2.0)**:
   - Il test viene condotto separatamente per l'ampiezza 1.0 e 2.0.
   - Se la divergenza tra stili esiste a 1.0 e si preserva a 2.0, l'effetto è strutturale.
   - Se compare esclusivamente ad ampiezza 2.0 (dove $D \approx 0.108$ supera la saturazione del modello), l'effetto è un manufatto dell'over-steering.
