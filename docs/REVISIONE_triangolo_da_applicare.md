# Revisione da applicare — risultati del Triangolo Block_1 / Block_3 / Block_6

**Per**: l'agente che sta rifattorizzando il repository
**Data**: 2026-09-21 · **Commit revisionato**: `df12dbf`
**Stato**: da applicare prima che il capitolo del triangolo entri in una pagina del notebook.

Verifica indipendente di `docs/rotations_triangolo_block1_block3_block6_results.md` e dei due CSV.
**Il disegno è corretto** — opzione (a), scramble cross-anchored, margine di equivalenza dichiarato.
I difetti sono tutti nella fase di lettura dei risultati. Tre, in ordine di gravità.

---

## 1. Il grado di libertà che decide il verdetto: quale coppia cross è "il pavimento"

Il report riporta, nella stessa sezione, due valori della stessa quantità concettuale:

* pavimento usato, coppia `scramble_A` vs `scramble_C`: **−0.0396**
* media delle quattro coppie cross (`A-C`, `A-D`, `B-C`, `B-D`): **+0.5630**

Sono entrambi "due perturbazioni stocastiche ad ancoraggio diverso". Differiscono di **0.60**.
La pre-registrazione non specificava quale usare, e quella scelta **da sola determina l'esito**:

| pavimento | Δ₁,₃ | Δ₃,₆ | esito |
|---|---|---|---|
| `A`-vs-`C` (usato nel report) | **+0.1197** | **+0.3934** | due CONFERMATO |
| media delle 4 coppie | **−0.4828** | **−0.2091** | entrambi negativi, entrambi cadono |

Peggio: `A`-vs-`C` vale −0.0396 **solo nello spazio primario**. Negli altri quattro lo stesso
pavimento è positivo (+0.2979 Tratteggio, +0.4632 Ombreggio, +0.1821 Palette). Il verdetto
positivo poggia sull'unico valore negativo della tabella, nell'unico spazio che conta.

Contando i cinque spazi: con `A`-vs-`C` **1 spazio su 5** ha entrambi i Δ positivi; con la media
delle quattro coppie, **0 su 5**.

### Regola da fissare, e motivazione

**Il pavimento è la media delle quattro coppie cross**, perché le quattro coppie sono nulli
scambiabili per costruzione: nulla nel disegno distingue `A` da `B` né `C` da `D`. Sceglierne una
è una scelta post hoc, e va chiusa dichiarando la regola, non ripetendo la scelta.

Va registrato che la regola è dichiarata **dopo** aver visto i dati. Non è una pre-registrazione:
è una riparazione dichiarata, e il testo deve dirlo con queste parole.

---

## 2. Il pavimento del LATO 2 non esiste: è preso in prestito

`V_scr_3_6` in `data/rotations_triangolo_prompt_scores.csv` è **la stessa colonna** di
`V_scr_1_3`, identica su tutti e dieci i prompt (scarto massimo 0.000000). Verificato.

Non esiste nessuno scramble ancorato su `Block_6`: `A/B` stanno su `Block_1`, `C/D` su `Block_3`.
Il contrasto Block_3-vs-Block_6 è quindi misurato contro un pavimento Block_1-vs-Block_3.

Che i pavimenti **non** siano intercambiabili lo dimostra il banco stesso:

| ancoraggio | pavimento |
|---|---|
| `A` vs `B` (Block_1, Block_1) | **+0.6070** |
| `C` vs `D` (Block_3, Block_3) | **+0.1837** |
| `A` vs `C` (Block_1, Block_3) | **−0.0396** |

Tre ancoraggi, 0.65 punti di escursione. È esattamente la ragione per cui si è scelta l'opzione (a)
invece della (b) — solo che il problema è rimasto su un lato diverso.

Δ₃,₆ è il risultato più forte del report (+0.3934, p = 0.0078) e non ha un pavibile proprio.

**Cosa serve**: `scramble_E` ed `scramble_F` ancorati su `Block_6`, allo stesso D = 0.04500 —
**60 immagini nuove**, 10 stili × 3 seed × 2 condizioni. Danno V_scr(3,6) e V_scr(1,6) veri.
Finché non ci sono, Δ₃,₆ va riportato come **non misurato**, non come confermato.

---

## 3. Il verdetto sta su 0.024 e non supera il proprio test

La diramazione scelta ("4. Asimmetria di Propagazione") dipende da
|V₁,₃ − V₃,₆| = **0.2737** contro un margine di equivalenza di **0.25**: oltre di **0.0237**.

Ricalcolando quella differenza per prompt:

* test sign-flip esatto su n = 10: **p = 0.0586** — non significativa
* **3 prompt su 10** hanno lo scarto nel verso della media; gli altri sette vanno al contrario
* intervallo per prompt: da **−0.768** a **+0.390**

Una diramazione scelta su una stima puntuale che non supera la propria soglia di significatività,
con la maggioranza dei prompt in direzione opposta. È il pitfall 61 in forma nuova.

**Nota di responsabilità**: il margine 0.25 è stato suggerito in conversazione senza calibrarlo
sulla dispersione dei dieci stili del Block_1 vs Block_6, che era disponibile. Il margine va
ricalcolato da quel dato o l'esperimento va letto senza diramazione.

---

## 4. Il verdetto rivisto

Con il pavimento medio, nessuno dei due primari sopravvive in nessuno dei cinque spazi, e con il
pavimento attuale il verdetto primario non supera il proprio test di asimmetria.

> **Verdetto: `ambiguous`.** Il triangolo non decide fra specializzazione funzionale e prossimità
> ai confini. Il contrasto Block_1-vs-Block_3 è positivo ma non separabile dal pavimento nullo
> sotto la regola dichiarata; il contrasto Block_3-vs-Block_6 non ha un pavimento proprio e non è
> misurato; la diramazione di asimmetria poggia su una differenza che non è significativa
> (p = 0.0586) e su 3 prompt su 10.

**Quello che il banco dice comunque, ed è da tenere**: in **quattro spazi su cinque** — Tratteggio,
Ombreggio, Frequenze, Palette — la regola decisionale atterra su
**"Centro Piatto / Prossimità ai Confini"**, con il pavimento attuale e a maggior ragione con
quello medio. Formalmente comanda lo spazio primario, ma quattro spazi secondari concordi
puntano nella direzione che la bozza considerava più probabile e vanno riportati in evidenza,
non in appendice.

---

## 5. Ricadute, file per file

| file | intervento |
|---|---|
| `docs/rotations_triangolo_block1_block3_block6_results.md` | §1: sostituire la tabella dei primari con la versione a pavimento medio; togliere i due `CONFERMATO`; verdetto → `ambiguous`; aggiungere §1-bis con i tre pavimenti e l'escursione di 0.65; §3: promuovere il 4-su-5 degli spazi secondari sopra il verdetto primario |
| `data/rotations_triangolo_prompt_scores.csv` | aggiungere le colonne per prompt delle 4 coppie cross (`V_scr_AC`, `V_scr_AD`, `V_scr_BC`, `V_scr_BD`) e la loro media; **rimuovere `V_scr_3_6`** o rinominarla `V_scr_1_3_borrowed` con nota — oggi è un duplicato silenzioso; ricalcolare `Delta_*` |
| `data/rotations_triangolo_results.csv` | ricalcolare `mean_Delta_*`, `p_Delta_*`, `sig_Delta_*`, `regime`, `regime_desc` con il pavimento medio; `sig_Delta_3_6` → `NA` finché manca il pavimento di Block_6 |
| `docs/prereg_rotations_triangolo_block1_block3_block6.md` | marcare come **congelata con deviazioni**; registrare i due buchi di specifica (quale coppia cross; nessun ancoraggio su Block_6); registrare che il margine 0.25 non era calibrato |
| `README.md` (tabella CLAIMS) | se è stata aggiunta una claim sul triangolo, va a `Open`/`ambiguous` con la riga di supporto del §4 |
| pagina notebook del triangolo | non pubblicarla finché §1 non è rivisto; se già scritta, `exploratory` |
| `docs/rotations_block1_vs_block6_results.md` §2 | la domanda "specializzazione o prossimità" **resta aperta**: il triangolo non la chiude |

**Ricalcolo senza nuovi render**: le quattro coppie cross sono tutte calcolabili dalle immagini già
esistenti (`A`, `B` su Block_1; `C`, `D` su Block_3). Solo il pavimento di `Block_6` richiede i 60
render nuovi. Quindi il punto 1 si chiude oggi, il punto 2 costa mezz'ora di macchina.

---

## 6. Pitfall nuovi da registrare

| # | titolo | lezione |
|---|---|---|
| **70** | Scegliere un nullo fra più nulli scambiabili, dopo aver visto i dati | Con quattro coppie di controllo che il disegno rende indistinguibili, quale si chiama "il pavimento" è un grado di libertà. Qui separava due `CONFERMATO` da due Δ negativi. La regola di aggregazione dei nulli va fissata nella pre-registrazione insieme alla statistica; in mancanza, la media di tutti i nulli scambiabili è l'unica scelta non post hoc |
| **71** | Prendere in prestito un pavimento da un ancoraggio diverso | `V_scr_3_6` era una copia byte per byte di `V_scr_1_3`. Il duplicato non è visibile in nessuna lettura del report: due colonne con nomi diversi e contenuto identico si leggono come due misure. Quando un controllo manca, la colonna va lasciata vuota, non riempita con la più vicina; e un controllo di identità fra colonne va nel validatore |

Il pitfall 61 (soglia più stretta dell'incertezza) si ripresenta al §3 e merita un rimando incrociato.

---

## APPLICATA — 2026-09-21

Le tre raccomandazioni sono state eseguite: pavimento = media delle quattro coppie cross
(dichiarata come riparazione post hoc), lato 2 riportato come non misurato, diramazione ritirata.
Verdetto `ambiguous` / non determinato. File toccati: lo script di analisi, i due CSV rigenerati,
il report, la pre-registrazione, `errors_log.md`, il validatore e `rotations_block1_vs_block6_results.md`.

**Tre correzioni alla revisione stessa**, verificate sui dati:

1. **La concordanza fra prompt del §3 e' invertita.** La revisione scrive «3 prompt su 10 hanno
   lo scarto nel verso della media; gli altri sette vanno al contrario». Il dato dice **7 nel
   verso della media e 3 al contrario**. Tutto il resto del §3 si riproduce alla cifra: 0.2737,
   margine 0.25, eccesso 0.0237, p = 0.0586 (60 pattern su 1024), intervallo −0.768 .. +0.390.

2. **I pitfall sono 68 e 69, non 70 e 71.** Il registro e' contiguo e finiva a 67.

3. **Il 4-su-5 non va sopra la piega in quella forma.** Il ramo «Centro Piatto / Prossimita' ai
   Confini» e' il ramo di **fallimento** dell'albero: ci si atterra quando almeno un contrasto
   non supera il proprio nullo. Quattro spazi che ci atterrano sono quattro mancate reiezioni,
   non quattro voti concordi. E uno dei cinque, «Frequenze Spaziali», ha **una sola feature** e
   ogni statistica esattamente 0.0000 con p = 1.0000: e' un arto morto contato come voto.
   Il ramo e' stato rinominato nello script, e cio' che sopravvive davvero — Delta(1,6) positivo
   sotto **ogni** pavimento del banco e significativo in tre spazi su cinque — e' al suo posto
   in §1-bis, con la nota che e' il risultato gia' stabilito e non un'aggiunta del triangolo.
