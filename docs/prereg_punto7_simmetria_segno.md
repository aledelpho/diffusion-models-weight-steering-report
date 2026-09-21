# Pre-registrazione — Punto 7: simmetria di segno sui 28 blocchi singoli

**Data di deposito**: 2026-09-20, ore 14:5x (Europe/Rome)
**Stato**: congelato PRIMA che esista un solo render di `benchmark_profondita_neg/`
**Corpus target**: 28 blocchi × 2 prompt (P01, P02) × 3 seed (42, 777, 1337) a dose −0.200

---

## 0. Dichiarazione dello stato di informazione — questa previsione NON è cieca

Chi scrive conosce già, al momento del deposito:

* **r⁺ in pixel per tutti e 28 i blocchi singoli** a +0.200 (da `benchmark_profondita/`);
* **r⁺ e r⁻ in pixel per tutti e 6 i macro-blocchi** a ±0.200;
* **r⁺ e r⁻ nel latente per tutti e 6 i macro-blocchi** e per le famiglie di B6.

Non conosce **nessun dato a −0.200 su blocco singolo**: è esattamente e solo quello
che il Punto 7 produrrà.

Le previsioni qui sotto sono quindi **estrapolazioni dal livello macro al livello
singolo**, non intuizioni a scatola chiusa. Il valore del deposito sta nel fatto che
l'estrapolazione può fallire in modi precisi e dichiarati in anticipo, non nel fatto
che l'autore fosse all'oscuro.

---

## 1. Definizione operativa della misura — fissata, non negoziabile dopo i dati

Per ogni immagine, **energia ad alta frequenza in pixel**:

```
g  = cvtColor(imread(file), COLOR_BGR2GRAY).astype(float32)
HF = std( g − GaussianBlur(g, ksize=(0,0), sigmaX=1.5) )
```

Per ogni blocco *b* e ogni cella *(prompt, seed)*:

```
r⁺(b, cella) = HF(blk_b pos 0.200) / HF(baseline, stessa cella)
r⁻(b, cella) = HF(blk_b neg 0.200) / HF(baseline, stessa cella)
```

Aggregazione sulle 6 celle **in spazio logaritmico** (media geometrica). Poi:

```
c(b) = sqrt( r⁺ · r⁻ )      MODO COMUNE   — effetto indipendente dal segno
s(b) = r⁺ / r⁻              SWING         — risposta a manopola
m(b) = r⁺ · r⁻              SPECULARITÀ   — vale 1 se r⁻ = 1/r⁺
```

**Baseline**: `benchmark_latenti_b6/renders/{P01,P02}_baseline_lat_krea2_seed{42,777,1337}`.
**Rumore di riferimento**: la deviazione relativa dell'HF del baseline fra seed vale
0.27% su P01 e 2.03% su P02, σ tipico **1.15%**. Soglia **3σ: |log| > 0.034**, cioè
rapporto fuori da **[0.966, 1.035]**.

Nessuna esclusione di blocchi o celle. Se una cella manca, il blocco è riportato ma
escluso dai conteggi, e l'esclusione va dichiarata.

**Ampiezza estetica** (per P7): vettore di 4 feature Lab — media L, dev L, croma media,
HF — differenza rispetto al baseline della stessa cella, ciascuna divisa per la propria
deviazione fra seed, poi norma L2 della media sulle 6 celle. Identica alla funzione già
usata il 20/09.

---

## 2. Quello che è già noto e che la previsione usa come àncora

Macro-blocchi, **in pixel**, dose ±0.200:

| | r⁺ | r⁻ | modo comune *c* | swing *s* | specularità *m* |
|---|---|---|---|---|---|
| B1 (0–4) | 0.859 | 1.094 | 0.969 | 0.785 | 0.940 |
| B2 (5–9) | 1.000 | 0.972 | 0.986 | 1.028 | 0.972 |
| B3 (10–14) | 1.077 | 0.970 | 1.022 | 1.111 | 1.045 |
| B4 (15–19) | 0.864 | 1.043 | 0.950 | 0.828 | 0.902 |
| B5 (20–23) | 0.862 | 1.016 | 0.936 | 0.848 | 0.875 |
| B6 (24–27) | 0.989 | 0.787 | 0.883 | 1.256 | 0.779 |

Due letture che guidano le previsioni:

1. **Il modo comune è quasi ovunque < 1**: media 0.958. Qualunque perturbazione, in
   qualunque verso, tende a *togliere* texture fine. Sembra un **costo**, non una leva.
2. **La specularità non regge**: *m* va da 0.779 a 1.045; solo B2 e B3 sono entro ±3%.
   La bidirezionalità speculare che la motivazione del Punto 7 dà per «accertata su B6»
   è, in pixel, proprio dove regge peggio (m = 0.779).
3. **Banda**: nel latente B6 ha swing 2.00, in pixel 1.256; e il modo comune latente di
   B6 è 0.987 contro 0.883 in pixel. B6 sposta energia dalla scala fine a quella media.
   Il Punto 7 salva **solo render**, quindi misura la banda fine: gli effetti attesi
   sono più deboli di quelli visti nel latente.

r⁺ noti per i 28 singoli (pixel): blk00 0.843 · blk01 1.039 · blk02 0.979 · blk03 0.968 ·
blk04 0.987 · blk05 1.018 · blk06 1.008 · blk07 1.011 · blk08 0.969 · blk09 0.975 ·
blk10 1.000 · blk11 0.957 · blk12 1.028 · blk13 1.016 · blk14 1.057 · blk15 1.044 ·
blk16 1.068 · blk17 0.908 · blk18 0.902 · blk19 0.960 · blk20 0.981 · blk21 1.024 ·
blk22 0.942 · blk23 0.864 · blk24 0.949 · blk25 0.862 · blk26 0.817 · blk27 1.086.

---

## 3. Previsioni — otto, tutte falsificabili

### P1 — Il modo comune è un costo di qualità, non una manopola
La media di *c(b)* sui 28 blocchi sarà **< 1**, e cadrà nell'intervallo **[0.94, 0.99]**.
Almeno **18 blocchi su 28** avranno *c* < 1.
*Fallisce se*: media ≥ 1, o meno di 14 blocchi sotto 1.

### P2 — La specularità non regge nemmeno sui singoli
La media di |log *m*| sui 28 blocchi sarà **> 0.03**, e **meno di 10 blocchi su 28**
avranno *m* dentro [0.97, 1.03].
*Fallisce se*: 14 o più blocchi sono entro ±3% da *m* = 1.

### P3 — blk00 è una manopola invertita
`blk00` ha r⁺ = 0.843. Previsione: **r⁻ > 1.00**, quindi swing **< 0.85**.
*Fallisce se*: r⁻ ≤ 1.00.
Ancora: B1 macro ha swing 0.785 in pixel e 0.739 nel latente, e dentro B1 solo blk00
si discosta da 1 (gli altri quattro stanno fra 0.968 e 1.039).

### P4 — La coda perde texture fine in entrambe le direzioni
`blk23`, `blk25` e `blk26` avranno tutti e tre modo comune **c < 0.96**.
*Fallisce se*: anche uno solo dei tre ha c ≥ 0.96.

### P5 — Gli swing forti sono pochi
**Al più 8 blocchi su 28** avranno |log *s*| > 0.10 (swing fuori da [0.905, 1.105]).
*Fallisce se*: 12 o più blocchi superano quella soglia.

### P6 — Nessun singolo raggiunge lo swing latente di B6
**Nessun blocco** avrà swing in pixel > 1.5.
*Fallisce se*: anche un solo blocco supera 1.5.

### P7 — L'asimmetria di ampiezza agli estremi si ripete in negativo
L'ampiezza estetica a −0.200 di `blk00`, e di **almeno 3 fra blk23…blk27**, sarà
**≥ 3×** la mediana dell'ampiezza di blk01…blk15.
*Fallisce se*: blk00 sta sotto 3×, oppure meno di 2 dei blocchi 23–27 la superano.

### P8 — Il costo cresce con la profondità *(la più rischiosa)*
Il modo comune *c(b)* correlerà **negativamente** con l'indice di blocco sui 28:
**r < −0.30**.
*Fallisce se*: r ≥ −0.10, o se il segno si inverte.
Ancora: sui 6 macro-gruppi la stessa correlazione vale **r = −0.74**; ma il profilo
macro non è monotono dall'inizio (B3 ha il *c* più alto), quindi l'estrapolazione ai
singoli è genuinamente a rischio. È la previsione che mi aspetto possa cadere.

---

## 4. Esito che falsificherebbe l'inquadramento complessivo

Se **P1 e P2 cadessero insieme** — modo comune centrato su 1 *e* specularità entro ±3%
sulla maggioranza dei blocchi — allora la lettura «ogni perturbazione costa texture
fine, e la bidirezionalità speculare è l'eccezione» sarebbe sbagliata, e la motivazione
originale del Punto 7 («la funzione di ogni blocco è bidirezionale e speculare») sarebbe
quella giusta. Sarebbe un risultato negativo pulito e andrebbe scritto come tale.

## 5. Cosa NON viene predetto, e resta esplorativo

* Il verso dello swing dei blocchi centrali (5–19) preso uno per uno.
* Qualunque affermazione sul *modo di rottura* oltre al clipping e alla perdita di HF.
* Il confronto fra prodotto dei singoli e macro corrispondente: sul braccio positivo
  il prodotto sovrastima il macro in 4 gruppi su 6, ma non ho una previsione ferma sul
  braccio negativo e non ne invento una adesso.
* Qualunque lettura in spazio latente: il Punto 7 non salva latenti.

---

*Deposito effettuato a generazione del Punto 7 non ancora avviata (il Punto 6 era al
50% circa). Lo script di verifica va scritto DOPO il deposito e DEVE implementare
letteralmente il §1.*

---

# EMENDAMENTO — 2026-09-20, ~16:40, PRIMA dei dati

**Verificato al momento della scrittura**: `benchmark_profondita_neg/renders/` contiene
**0 file**. Il Punto 7 non è partito. L'emendamento riguarda solo la **calibrazione del
rumore**; le previsioni sostantive P1, P3, P4, P6, P7, P8 non cambiano.

## Motivo

Il §1 fissava σ = 1.15% sull'HF, stimato su **3 semi** dei baseline P01/P02. Il
benchmark `benchmark_stage1_gate` (collegato dopo il deposito) contiene **20 baseline
per prompt su 3 prompt**, e dà σ = **3.26%** (P2), **4.93%** (P3), **5.20%** (P1).

Una deviazione campionaria su n = 3 ha 2 gradi di libertà: può sbagliare di un fattore
2–3 in entrambe le direzioni. La stima originale era quindi inaffidabile, e i tre nuovi
valori — pur venendo da prompt diversi — concordano su un ordine di grandezza superiore.

**Non** è una misura diretta del σ di P01/P02, che il progetto non possiede: con soli
3 baseline per prompt non è misurabile. Vedi §Raccomandazione.

## Calibrazione rivista — da riportare ACCANTO a quella congelata, non al suo posto

Adottando σ = **4%** per cella (punto medio dei tre valori misurati), e propagando sulla
media geometrica di 6 celle:

| quantità | σ propagato | soglia 3σ |
|---|---|---|
| log r⁺ o log r⁻ (media su 6 celle) | 0.0163 | 0.049 |
| log *c* = (log r⁺ + log r⁻)/2 | 0.0115 | **0.035** |
| log *s* = log r⁺ − log r⁻ | 0.0231 | **0.069** |
| log *m* = log r⁺ + log r⁻ | 0.0231 | **0.069** |

Nota non ovvia e utile: **il modo comune ha rumore inferiore allo swing** (fattore 2),
perché la media di due misure cancella, mentre la differenza somma. La decomposizione
del §2 del documento di analisi è quindi *meglio* condizionata del rapporto originale,
non peggio.

## Effetto sulle otto previsioni

* **P1, P3, P4, P6, P7, P8 — invariate.** Nessuna usava la soglia σ. P4 (`c` < 0.96)
  resta a ≈ 3.5σ rivisti, P5 (|log *s*| > 0.10) a ≈ 4.3σ: entrambe restano sensate.
* **P2 — mal calibrata, e va detto ora.** La banda ±3% su *m* corrisponde a |log *m*| =
  0.030, cioè **1.3σ** con la calibrazione rivista. Il rumore da solo spingerebbe la
  maggior parte dei blocchi fuori dalla banda, quindi P2 come scritta è **sbilanciata
  verso la conferma**: passerebbe quasi comunque. Non ha valore probatorio.

  **P2 rivista**, congelata adesso e da riportare accanto all'originale:
  banda a 3σ, *m* ∈ [0.933, 1.071]. Previsione: **almeno 12 blocchi su 28 saranno
  DENTRO** la banda — cioè compatibili con la specularità entro il rumore — mentre la
  violazione si concentrerà nei blocchi con effetto rilevabile (|log *c*| > 0.035).
  La tesi diventa: *la specularità cade dove c'è segnale, non dappertutto*.
  Si noti che la direzione della previsione è **invertita** rispetto all'originale: con
  la banda giusta mi aspetto più blocchi speculari, non meno. È una conseguenza della
  ricalibrazione, non di un ripensamento sul modello, e nessun dato del Punto 7 esiste.

## Raccomandazione operativa (fuori dalla pre-registrazione)

Generare **15 semi di baseline aggiuntivi per P01 e per P02** — 30 immagini, ~15 minuti.
Darebbe al progetto il proprio pavimento di rumore misurato su 190 coppie invece che su
3, e diventerebbe il riferimento per ogni soglia futura. È l'azione col miglior rapporto
valore/costo attualmente disponibile.
