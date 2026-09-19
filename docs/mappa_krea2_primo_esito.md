# Mappa esplorativa dei blocchi su Krea-2 — primo esito: la mappa spaziale è vuota

**Data**: 2026-09-19 · **Materiale**: 328 render in `benchmark_mappa/renders`, di cui 271 sui
prompt sonda `P01`/`P02` e 45 su `A01` (vedi §4) · **Stato**: generazione ancora in corso.

---

## 1. Cosa è stato misurato

48 condizioni (sei gruppi di blocchi × sei dosi in guadagno più il negativo a 0.050, più
`Text_Fusion`, `Time_Embed`, `Projection` a ±0.050), tre seed, due prompt sonda
multi-contenuto. Per ogni condizione: mappa di differenza per pixel contro il baseline dello
stesso seed, confrontata con un pavimento di rumore costruito **con lo stesso estimatore** dai
soli baseline a seed diversi, soglia al 99° percentile.

## 2. Esito: nessun segnale sopra il rumore di seed

**Area sopra il pavimento: 0.0% per ogni blocco a ogni dose.** Il pavimento non è marginalmente
superiore al segnale, lo domina:

| quantità | valore |
|---|--:|
| differenza mediana fra due baseline a seed diversi | **0.1874** |
| soglia al 99° percentile del null | 0.4016 |
| \|diff\| massimo raggiunto da un blocco (`Block_3`, guadagno 0.200) | 0.1562 |

Nessun blocco, a nessuna dose provata, sposta i pixel quanto li sposta il cambio di seed.

La causa è il campionatore. `euler_ancestral` inietta rumore nuovo a ogni passo: due render
dello stesso prompt e dello stesso seed condividono l'inizializzazione ma non la traiettoria,
e la riorganizzazione casuale che ne segue è più grande dell'effetto di una perturbazione dei
pesi a questi guadagni. **La domanda "quali pixel cambiano di più" non è rispondibile da questi
dati**, e non lo diventerà aggiungendo immagini: il pavimento cresce insieme al segnale.

Il rimedio è un campionatore **deterministico** (`euler`, `dpmpp_2m`), dove il seed fissa la
traiettoria e l'unica differenza residua è la modifica dei pesi. Prima di impegnare un budget
di render in un disegno spaziale, il pavimento di seed e l'effetto atteso vanno misurati su
una manciata di immagini e confrontati. Vedi pitfall 53.

## 3. Cosa resta utilizzabile: la classifica scalare

Il \|diff\| medio è monotono nella dose e ordina i gruppi in modo non banale:

| slot | 0.020 | 0.035 | 0.050 | 0.080 | 0.120 | 0.200 |
|---|--:|--:|--:|--:|--:|--:|
| `Block_1` | 0.0654 | 0.0757 | 0.0874 | 0.0958 | 0.1099 | 0.1425 |
| `Block_2` | 0.0732 | 0.0965 | 0.1061 | 0.1141 | 0.1263 | 0.1460 |
| `Block_3` | 0.0710 | 0.0854 | 0.0941 | 0.1092 | 0.1317 | **0.1562** |
| `Block_4` | 0.0583 | 0.0682 | 0.0786 | 0.1005 | 0.1281 | 0.1551 |
| `Block_5` | 0.0601 | 0.0743 | 0.0871 | 0.0973 | 0.1118 | 0.1337 |
| `Block_6` | **0.0483** | **0.0622** | **0.0727** | **0.0856** | **0.0999** | **0.1286** |

Due osservazioni, entrambe da trattare come indizi e non come risultati:

* **`Block_6` è ultimo a tutte e sei le dosi.** È l'unico ordinamento stabile della tabella.
* **C'è un incrocio.** A guadagno basso l'ordine è B2 > B3 > B1 > B5 > B4 > B6; a guadagno alto
  diventa B3 > B4 > B2 > B1 > B5 > B6. I blocchi iniziali saturano, quelli centrali accelerano.

**Avvertenza che invalida la lettura ingenua**: le dosi sono espresse in *guadagno*, non in $D$.
I sei gruppi contengono un numero diverso di tensori con norme diverse, quindi lo stesso
guadagno produce spostamenti di Frobenius diversi. La tabella è una sensibilità **per unità di
guadagno**, che è la grandezza che l'utente manipola nel tuner ed è quindi utile di per sé, ma
**non** è una classifica di sensibilità per unità di spostamento dei pesi. Per ottenere quella
serve riscalare ciascun gruppo al medesimo $D$ e rigenerare.

## 4. Nota sui 45 render `A01`

Le prime 45 immagini della cartella sono state generate sul prompt `A01` del corpus nativo
Anima invece che sulle sonde `P01`/`P02`. La causa è un identificativo rimasto non aggiornato
nella sezione "pilota" di `BRIEF_mappa_esplorativa.md` dopo che la mappa era stata spostata sui
prompt sonda: errore di redazione del brief, non di esecuzione. Il brief è stato corretto. I 45
render restano validi come materiale descrittivo ma non entrano nella mappa, che è appaiata sui
baseline delle sonde.
