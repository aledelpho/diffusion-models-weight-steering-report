# Audit metodologico — cosa è sbagliato e cosa manca

**Data**: 2026-09-20 · **Domanda**: «Ho sbagliato qualche metodologia o dimenticato di eseguire
test importanti?» · Tutto quanto segue è verificato sui dati esistenti, non ricordato.

---

## 1. L'errore più grave, scoperto oggi: si misura in un regime dominato dal danno

Tutte le conclusioni di stamattina — la matrice dei coseni fra blocchi, i confini naturali
(2, 7, 12, 17, 26), la regola dell'angolo — sono calcolate a **dose 0.200**. Non era mai stato
verificato che quel regime fosse informativo.

**Quota dello spostamento che giace sull'asse comune** (la grana, che spiega il 78.1% di tutto):

| blocco | dose 0.050 | dose 0.120 | dose 0.200 |
|---|--:|--:|--:|
| B1 | 41% | 28% | 22% |
| B2 | 43% | 31% | 46% |
| B3 | 18% | 26% | **84%** |
| B4 | 30% | 76% | **73%** |
| B5 | 19% | 35% | 28% |
| B6 | 73% | 98% | **99%** |

A dose 0.200 tre blocchi su sei sono al 73% o più di pura grana. `B6` è al **99%**: la sua
"direzione" a quella dose è l'asse del danno e nient'altro.

**Le direzioni ruotano con la dose.** Coseno fra la direzione dello stesso blocco a dosi diverse:

| blocco | 0.05 ↔ 0.12 | 0.12 ↔ 0.20 | 0.05 ↔ 0.20 |
|---|--:|--:|--:|
| B1 | 0.93 | 0.91 | 0.73 |
| **B2** | **0.13** | 0.68 | **0.30** |
| B3 | 0.67 | 0.61 | 0.48 |
| B4 | 0.58 | 0.94 | 0.50 |
| B5 | 0.94 | 0.95 | 0.91 |
| B6 | 0.84 | 0.98 | 0.71 |

E la **matrice** dei coseni fra blocchi correla solo **r = +0.42** fra dose 0.05 e 0.20. Tolto
l'asse comune, scende a **+0.04**: le relazioni fra blocchi a dose bassa e a dose alta sono
*scorrelate*, e la parvenza di stabilità era portata dalla grana condivisa.

**Conseguenza**: «i confini naturali sono 2, 7, 12, 17, 26» e «B4 e B5 puntano nella stessa
direzione (+0.77)» sono enunciati **sul regime a dose 0.200**, dove metà dei blocchi stanno
soprattutto producendo grana. Non sono falsi, sono più stretti di come li ho scritti, e vanno
replicati a dose bassa prima di costruirci sopra.

## 2. Errori di metodo, verificati

**Sweep a un segno solo.** Per gran parte del progetto si è misurato solo il guadagno positivo.
Ha prodotto un'affermazione direzionale sbagliata («B3 e B4 saturano»), smascherata solo
generando il braccio negativo: la frazione di sterzo di B4 sulla saturazione è **0.03**. Pitfall
57. **La sweep di dose su Anima è ancora a un segno solo**, quindi ogni affermazione direzionale
tratta da lì è nella stessa condizione.

**La suddivisione in gruppi non è mai stata validata.** Misurata sui 28 blocchi singoli, quella
in uso sta al 31° percentile fra le partizioni contigue, e nove permutazioni delle stesse
dimensioni fanno meglio. Non invalida le misure — ogni esperimento ha misurato l'insieme di
tensori che ha manipolato — ma il linguaggio "anatomico" del notebook non è sostenuto.

**Nessun calcolo di potenza prima di spendere il budget di render.** Il pilota su Anima girava al
**34%** di potenza, e la regola dell'angolo è stata formulata su **4 punti** con pavimento
di significatività a 0.083. In entrambi i casi la potenza è stata calcolata *dopo*. Cinque minuti
di conto prima avrebbero cambiato entrambi i disegni.

**Il cancello di collasso è una soglia assoluta ereditata da Krea-2.** Su Anima scatta in
funzione di quanto tratto aveva il prompt in partenza, non di quanto ne ha perso: a dose 50 tutti
e sette i prompt avevano perso il 32–74% del tratto e il cancello ne segnalava due. Pitfall 51.

**Le metriche non sono validate contro casi sintetici.** È stato fatto una volta sola (la mappa
di differenza, che falliva il proprio test sintetico e fu corretta). Negli altri casi le metriche
si sono rivelate misurare altro solo per caso: `edge_density` catturava l'inquadratura, la
correlazione della filigrana è invariante di scala, quattro scalari tonali non distinguevano
saturazione da antagonismo.

## 3. Test mancanti, in ordine di importanza

**a. Determinismo fra sessioni — 1 immagine, mai fatto.**
`benchmark_profondita` è stato generato il 20 settembre alle 00:57 e **riusa i baseline del 19
settembre sera** (16:38–16:41). Fra i due c'è stato almeno un riavvio. Se la pipeline non è
riproducibile fra sessioni, ogni spostamento misurato lì contiene una deriva di sessione, e
l'analisi dei gruppi di stamattina poggia su quel confronto.
*Test*: rigenerare oggi `P01_baseline_krea2_seed42` con lo stesso workflow e confrontare i
**pixel decodificati** con quello archiviato. Differenza massima 0 → il riuso dei baseline fra
giorni è lecito. Diversa da 0 → ogni confronto fra cartelle generate in giorni diversi va
rifatto con baseline propri.
*Nota*: la cartella `benchmark_mappa` è invece pulita — tutte e 519 le immagini sono state
generate in una sessione continua fra le 15:17 e le 21:08 del 19 settembre.

**b. Replica del raggruppamento a dose bassa — 168 immagini.**
I 28 blocchi singoli esistono solo a 0.200. Vanno rifatti a **0.050**, dove la quota di grana
scende dal 73–99% al 18–43%. Senza questo, i confini naturali restano una proprietà del regime
degradato.

**c. Braccio negativo su Anima.**
Ogni affermazione direzionale su Anima poggia su un solo segno, ed è l'errore che su Krea-2 ha
già prodotto una conclusione sbagliata.

**d. Il percorso del testo non è mai entrato in nessun esperimento.**
Il tuner ha un nodo per il text encoder (`ArthemyKrea2CLIPBlockSurgeonTuner`, 60 layer
indirizzabili) e `Text_Fusion` compare nella mappa solo a ±0.05, due condizioni su 48. Tutto il
corpo di risultati riguarda il DiT. Se lo steering dei pesi funziona anche sul percorso del
testo, è una famiglia di risultati intera che non è stata nemmeno guardata; se non funziona, è
un contrasto che rafforza le conclusioni sul DiT. In entrambi i casi è informativo e non è mai
stato provato.

**e. Sensibilità della standardizzazione.**
Lo spazio a 23 feature è standardizzato su **6 baseline**. Sei campioni per stimare media e
deviazione standard di 23 grandezze è poco, e tutte le distanze e i coseni ne dipendono. Va
verificato che i risultati non cambino usando una standardizzazione diversa (per esempio sui
baseline di tutti i prompt disponibili).

## 4. Cosa è stato fatto bene, per contrasto

Non per bilanciare, ma perché sono scelte che cambiano il valore dell'insieme e che in gran parte
del lavoro amatoriale su questo tema mancano.

* **Controlli a norma appaiata fin dall'inizio** (`blockshuffle`, `randsign`, e i due `scramble`
  a $D$ identico). È la decisione singola più importante di tutto il disegno: senza, nessuna
  delle conclusioni sarebbe distinguibile da "una perturbazione qualsiasi fa qualcosa".
* **Il prompt come unità di analisi**, con test di permutazione esatti e correzione di Holm,
  invece di trattare le immagini come indipendenti.
* **Entrambi i segni sulla mappa**, che è ciò che ha reso visibile la distinzione fra sterzo e
  deriva — e ha smascherato un errore proprio.
* **$D$ appaiata fra condizioni** nell'esperimento sulle rotazioni ($\Delta D = 6\times10^{-7}$).
* **Il registro degli errori stesso**, che è il motivo per cui questo audit può essere scritto:
  ogni passo falso è documentato e datato invece che riscritto.
* **L'osservazione della filigrana è arrivata guardando le immagini**, non da una metrica. Nessuna
  delle misure in uso l'avrebbe trovata, ed è diventata la grandezza più utile del progetto.
