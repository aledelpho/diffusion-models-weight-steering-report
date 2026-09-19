# Coerenza di traiettoria: la filigrana del seed come misura

**Data**: 2026-09-19 · **Materiale**: 216 render già esistenti (`benchmark_mappa`, P01/P02,
6 gruppi di blocchi × 6 dosi × 3 seed). Nessuna generazione nuova.

---

## 1. L'osservazione e il meccanismo

Osservazione dell'utente: in tutte le immagini prodotte con lo **stesso seed** ricorre lo stesso
identico motivo di "sporco" sulle texture, indipendentemente dai pesi usati.

È vero e ha una causa precisa. `euler_ancestral` aggiunge rumore nuovo a ogni passo, estratto da
un generatore seminato dal seed di campionamento: la *sequenza* di tensori di rumore è una
funzione fissa del seed. Due run con lo stesso seed ricevono letteralmente gli stessi tensori,
agli stessi passi. Cambiare i pesi cambia la previsione del modello e fa divergere la
traiettoria, ma il rumore additivo resta identico, e quello degli ultimi passi non fa in tempo a
essere rimosso: resta impresso nei pixel.

**Misura di conferma.** Correlazione del residuo ad alta frequenza (immagine meno gaussiana
σ = 2) calcolata nel 40% di pixel a varianza locale più bassa:

| | r |
|---|--:|
| condizioni diverse, **stesso** seed | +0.07 … +0.39 |
| baseline, seed **diversi** | +0.003 … +0.009 |

## 2. Conseguenza metodologica: un pavimento di rumore sbagliato

`docs/mappa_krea2_primo_esito.md` concludeva che la mappa spaziale fosse vuota, sulla base di un
pavimento costruito dalle differenze fra baseline a **seed diversi**. Quel pavimento è
concettualmente errato: un cambio di seed non è rumore, è una perturbazione **massimale**
(latente iniziale del tutto diverso). A seed fisso il null è **zero**, per misura diretta
(`test_identity`, differenza massima di canale 0). Ogni differenza osservata è segnale; la
domanda corretta non è «supera il rumore» ma «è specifica e riproducibile».

Rifatta per seed invece che mediando sui seed, la mappa **non è vuota**: correlazione fra mappe
dello stesso blocco a dosi diverse 0.40–0.47, fra blocchi diversi 0.26–0.30, separazione
+0.128 … +0.165 in tutte e sei le celle (2 prompt × 3 seed), test dei segni p = 2/2⁶ = 0.031.
La firma spaziale di ciascun blocco esiste ed è **condizionata al seed**: mediare sui seed la
cancella. Vedi pitfall 55.

**Nota di contenimento**: l'errore riguarda la mappa, non la sweep di dose. Lì σ_seed non fa da
pavimento di rumore ma da unità di confronto per un'affermazione sullo *stile* («il preset
sposta lo stile meno di un re-roll del seed»), che resta un enunciato sensato. I numeri di
`anima_dosesweep_verifica.md` non sono toccati.

## 3. La filigrana come funzione obiettivo

Caso d'uso dichiarato dall'utente: **correggere un'immagine che piace, senza cambiare seed,
passi o CFG**. Per quell'obiettivo la grandezza rilevante non è quanto si sposta lo stile, ma il
rapporto fra quanto cambia ciò che si vuole cambiare e quanto si consuma l'identità
dell'immagine. L'identità è la filigrana: finché la traiettoria originale sopravvive è ancora
quella immagine; quando si dissolve si è generata un'immagine nuova, ottenibile cambiando seed.

**Coerenza di traiettoria** (correlazione HF nelle zone piatte contro il baseline dello stesso
seed), media su 2 prompt × 3 seed:

| blocco | 0.020 | 0.035 | 0.050 | 0.080 | 0.120 | 0.200 |
|---|--:|--:|--:|--:|--:|--:|
| B1 | 0.185 | 0.159 | 0.134 | 0.110 | 0.083 | **0.047** |
| B2 | 0.175 | 0.139 | 0.116 | 0.108 | 0.093 | 0.072 |
| B3 | 0.177 | 0.140 | 0.122 | 0.097 | 0.072 | 0.056 |
| B4 | 0.226 | 0.183 | 0.153 | 0.109 | 0.074 | 0.060 |
| B5 | 0.232 | 0.194 | 0.142 | 0.123 | 0.097 | 0.072 |
| **B6** | **0.260** | **0.195** | **0.180** | **0.171** | **0.165** | **0.164** |

Cambio di contenuto (differenza media delle immagini sfocate a σ = 4, ×1000) a dose 0.200:
B3 130.1, B4 129.1, B2 118.2, B1 108.2, B5 104.1, **B6 94.4**.

**B6 smette di decadere dopo dose 0.08** e si assesta a 0.164, mentre tutti gli altri scendono a
0.047–0.072, pur cambiando il contenuto quasi quanto B1 (94 contro 108).

### Controllo: B6 non sta evitando le zone di misura

Differenza media dentro le zone piatte contro le zone dettagliate, a dose 0.200:

| blocco | piatte | dettagliate | rapporto |
|---|--:|--:|--:|
| B1 | 0.1092 | 0.1776 | 0.615 |
| B2 | 0.1184 | 0.1929 | 0.614 |
| B3 | 0.1300 | 0.2032 | 0.640 |
| B4 | 0.1276 | 0.1998 | 0.639 |
| B5 | 0.0893 | 0.1884 | 0.474 |
| B6 | 0.1150 | 0.1602 | **0.718** |

B6 cambia le zone piatte quanto B1 e meno di B3, ed è il blocco **meno** selettivo sui bordi.
Non conserva la coerenza perché agisce altrove: la conserva mentre agisce lì. Sposta i valori
senza riorganizzare la traiettoria.

## 4. Ipotesi meccanicistica, falsificabile senza nuovi render

A dose bassa la coerenza cresce con la profondità (B1 0.185 → B6 0.260). Un blocco iniziale
altera la previsione e l'errore si propaga attraverso i venti e più blocchi successivi, spostando
la traiettoria; un blocco finale agisce vicino all'uscita e sposta i valori senza retroazione.

**Previsione**: la coerenza deve crescere monotonamente con l'indice del blocco. Gli slot sono
sei gruppi da quattro-cinque blocchi; il test richiede di rifare la misura **per blocco singolo**
invece che per gruppo, e i render necessari sarebbero nuovi. Con i dati attuali la monotonia è
rispettata a dose bassa salvo l'inversione B2/B3, e a dose alta solo B6 si separa nettamente.

## 5. Conseguenza operativa

Per correggere un'immagine senza perderla, la manopola non è la dose ma **quale blocco**: a
parità di spostamento del contenuto, B6 lascia 3.5× più identità residua di B1. È una
distinzione invisibile nello spazio delle feature di stile e leggibile solo nella filigrana —
che esiste perché il campionatore è `euler_ancestral`. Un campionatore non ancestrale
probabilmente non renderebbe disponibile questa misura.

---

## 7. Due fenomeni distinti: condizionato al seed e invariante al seed

Osservazione dell'utente: alcune correzioni ottenute con il tuner **persistono al cambio di
seed** — l'accensione delle alte luci, certi cambi di tratto. Se fosse tutto deviazione di
traiettoria, non dovrebbero.

Verificata misurando proprietà **globali** invece che per pixel, e chiedendo se la variazione
rispetto al baseline ha lo stesso segno in tutte e sei le celle (2 prompt × 3 seed). Dose 0.200:

| blocco | alte luci (97° pct) | ombre (3° pct) | contrasto | saturazione |
|---|--:|--:|--:|--:|
| **B1** | **−10.00** 6/6 | **+3.33** 6/6 | **−6.70** 6/6 | **−8.34** 6/6 |
| B2 | +1.17 4/6 | +0.67 3/6 | −0.43 4/6 | +2.25 4/6 |
| B3 | −0.83 4/6 | **−3.33** 6/6 | +1.72 3/6 | **+14.14** 6/6 |
| B4 | **+4.83** 6/6 | **−4.00** 6/6 | +3.61 3/6 | **+12.14** 6/6 |
| **B5** | **+7.33** 6/6 | **−2.17** 6/6 | **+3.47** 6/6 | **+17.13** 6/6 |
| B6 | −4.50 3/6 | +0.17 3/6 | **−5.88** 6/6 | **+4.09** 6/6 |

> **CORRETTO il 2026-09-19 a tarda sera, dopo il braccio negativo.** La riga sulla
> saturazione di B3 e B4 attribuiva una direzione a un effetto che non ce l'ha: con
> guadagno **negativo** B4 satura di +12.89 contro +12.14 del positivo, frazione di sterzo
> **0.03**. Non è B4 che satura, è qualunque modifica a B4 che satura. Vedi
> `docs/mappa_completa_sterzo_e_deriva.md` §2 e pitfall 57. Gli effetti di B1 e B5 sulle
> alte luci e sul contrasto sono invece sterzi veri e sopravvivono alla verifica.

**B5 espande la gamma dinamica e satura** — alte luci su, ombre giù, contrasto su, saturazione
su: quattro misure indipendenti che raccontano la stessa storia, concordi in 6/6 celle e già
presenti a dose 0.050 (+3.00, −1.33, +1.96, +5.22, tutte 6/6). **B1 fa l'opposto**: schiaccia la
gamma e desatura. Sono due manopole contrapposte sullo stesso asse tonale.

**Cautela sui confronti multipli**: 6 blocchi × 6 metriche × 2 dosi = 72 test; a p = 0.031 se ne
attenderebbero ~2.2 per caso e se ne osservano ~20, quindi il quadro complessivo è ben oltre il
caso. La singola casella a 6/6 non va però letta isolatamente, e le metriche di luminanza sono
correlate fra loro. B5 regge perché quattro metriche diverse convergono su una descrizione sola.

### La separazione che ne segue

| | cos'è | dipende dal seed? | come si misura |
|---|---|---|---|
| **firma spaziale** | *dove* si spostano i pixel | **sì** — mediare sui seed la cancella | mappe di differenza, per seed |
| **effetto sistematico** | *quale proprietà globale* si sposta | **no** — sopravvive al cambio di seed | statistiche globali, test dei segni fra celle |

Le correzioni che l'utente osserva persistere sono del secondo tipo. I due fenomeni erano
mescolati in ogni analisi precedente e vanno misurati separatamente.
