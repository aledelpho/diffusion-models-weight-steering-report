# Block 6 nel latente: la manopola c'è, ed è la VAE a nasconderne metà

**Data**: 2026-09-20 · **Materiale**: `benchmark_latenti_b6` — 18 render **più i 18 latenti
corrispondenti**, salvati prima della decodifica. 3 condizioni × 2 prompt × 3 seed.
Latente `[16, 160, 128]`, modalità del tuner `Real Value`, 9 passi, CFG 1.0, `euler_ancestral`.

---

## 1. La domanda

L'utente aveva proposto, guardando le immagini: *«Può essere che gestisca una manopola che mette
a fuoco i pixel in preparazione all'estrazione finale da parte del VAE?»*

Le misure sui pixel (`docs/block6_e_struttura_gruppi.md`) avevano dato una risposta ambigua. Il
**negativo** sfocava in modo netto (alta frequenza 0.79×, luminanza −9.0). Il **positivo** non
aumentava affatto l'alta frequenza (0.99×): la ridistribuiva soltanto. E poiché l'effetto **non si
invertiva col segno** (p = 0.156, l'unico blocco a fallire quel test), la conclusione era che
`Block_6` non fosse una manopola di fuoco.

Quella conclusione era **sbagliata**, e lo si vede solo guardando prima della VAE.

## 2. Nel latente l'effetto è pulito e bidirezionale

Misure per canale sui 16 canali del latente, poi mediate; 6 celle prompt × seed; test dei segni
esatto.

| | energia ad alta frequenza | uniformità spaziale (CV) | media |
|---|--:|--:|--:|
| baseline | 1.000× | 0.203 | — |
| **B6 pos** | **1.404×** (p = 0.031) | **0.092** (−0.111, p = 0.031) | −0.0117 (p = 0.22) |
| **B6 neg** | **0.695×** (p = 0.031) | 0.230 (+0.027, p = 0.062) | +0.0033 (p = 0.88) |

1.404 e 0.695 sono quasi esattamente reciproci (1/1.404 = 0.712). **Nel latente `Block_6` è una
manopola di dettaglio simmetrica**: il segno inverte l'effetto in modo pulito.

## 3. Il confronto che decide

| | nel **latente** | nei **pixel** |
|---|--:|--:|
| B6 pos, alta frequenza | **1.404×** | 0.99× |
| B6 neg, alta frequenza | **0.695×** | 0.79× |
| il segno inverte l'effetto? | **sì, nettamente** | **no** (p = 0.156) |

**La metà negativa attraversa la VAE, la metà positiva no.** Il decodificatore lascia passare la
perdita di dettaglio e **assorbe l'aggiunta**: l'alta frequenza in più che `Block_6` scrive nel
latente non diventa alta frequenza nell'immagine.

Quello che sopravvive del braccio positivo è la **redistribuzione**: il CV dell'alta frequenza
scende già nel latente da 0.203 a 0.092, e nei pixel si ritrova attenuato (0.440 → 0.341).
L'uniformazione è un fatto del latente, non un effetto della decodifica.

## 4. La tesi dell'utente, riformulata

*Sì, `Block_6` è una manopola di messa a fuoco, e lo è nello spazio dove il modello lavora.* Non è
però una manopola «in preparazione» alla VAE nel senso di assecondarla: è una manopola che la VAE
**taglia da un lato**. Il tetto non è del modello, è del decodificatore.

Una conseguenza pratica: chi volesse usare `Block_6` per aggiungere dettaglio sta spingendo contro
un limite che sta a valle dei pesi, e nessuna dose lo supererà. Per **togliere** dettaglio invece
funziona, e il braccio negativo è quello che nei pixel si comporta come descritto.

**E una conseguenza sulla luminanza**: il calo di −9.0 su 255 del braccio negativo **non** è uno
spostamento di media nel latente (+0.0033, p = 0.88). Non è un offset che attraversa la
decodifica: emerge dal decodificare un latente più povero di alta frequenza. È coerente con la
descrizione data a occhio — «una fusione di moltiplicazione» — e non con una semplice sottrazione.

## 5. Lezione di metodo

Ogni misura di questo progetto, fino a oggi, è stata fatta **dopo la VAE**. Il caso di
`Block_6` mostra che è una misura composta — «cosa fa l'edit» convoluto con «cosa il
decodificatore lascia passare» — e che le due cose possono cancellarsi fino a far sembrare
assente un effetto che c'è. Vedi pitfall 62.

Il rimedio non è rifare tutto nel latente: il pixel è ciò che l'utente guarda, e un effetto che
la VAE assorbe è, per il caso d'uso, assente davvero. Il rimedio è **misurare in entrambi gli
spazi quando si vuole attribuire un meccanismo**, e riservare l'affermazione «il blocco X non fa
Y» al caso in cui anche il latente lo confermi.
