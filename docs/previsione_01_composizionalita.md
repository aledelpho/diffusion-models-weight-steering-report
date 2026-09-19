# Previsione 01 — Gli effetti tonali dei blocchi si sommano

**Scritta il 2026-09-19, ore 22:30 (Europe/Rome), PRIMA di generare le immagini che la testano.**
Questa è la prima previsione del progetto formulata prima del dato, non dopo.

---

## 1. Da dove viene

Su Krea-2, misurando proprietà globali dell'immagine e chiedendo che la variazione rispetto al
baseline abbia lo **stesso segno in tutte e sei le celle** (2 prompt sonda × 3 seed), a dose
0.200 emergono effetti sistematici e invarianti al seed (`docs/coerenza_traiettoria.md` §7):

| blocco | alte luci (97° pct) | ombre (3° pct) | contrasto | saturazione |
|---|--:|--:|--:|--:|
| B1 | −10.00 ± 5.44 | +3.33 ± 2.58 | −6.70 ± 1.16 | −8.34 ± 3.11 |
| B4 | +4.83 ± 3.06 | −4.00 ± 1.55 | +3.61 ± 4.82 | +12.14 ± 6.68 |
| B5 | +7.33 ± 5.05 | −2.17 ± 0.75 | +3.47 ± 1.44 | +17.13 ± 5.68 |

(± è la deviazione standard fra le sei celle, non l'errore della media.)

B1 e B5 hanno segno opposto su tutte e quattro le grandezze: sembrano due manopole contrapposte
sullo stesso asse tonale. B4 e B5 hanno segno concorde su tre su quattro.

**Questo è un risultato esplorativo.** È stato trovato guardando i dati, non predetto. Non
dimostra niente e non deve essere presentato come dimostrazione.

## 2. L'ipotesi

**I guadagni scalari applicati a gruppi di blocchi distinti si compongono in modo additivo negli
effetti tonali globali**: applicandone due insieme, lo spostamento risultante è la somma dei
due spostamenti singoli, entro l'incertezza.

Se regge, i preset smettono di essere oggetti da tarare a mano e diventano **progettabili**: si
sceglie l'effetto voluto e si risolve per i guadagni. È questa la conseguenza che rende
l'ipotesi degna di un test, non il fatto in sé.

## 3. Le previsioni numeriche

Condizioni: Krea-2, dose 0.200 su ciascun blocco coinvolto, prompt sonda `P01` e `P02`, seed
42 / 777 / 1337. Baseline già esistenti in `benchmark_mappa`. **12 immagini nuove in tutto.**

Somma delle medie osservate; incertezza propagata in quadratura dalle DS fra celle.

| combinazione | alte luci | ombre | contrasto | saturazione |
|---|--:|--:|--:|--:|
| **B5 + B1** (opposti) | **−2.67 ± 7.42** | **+1.17 ± 2.69** | **−3.23 ± 1.85** | **+8.79 ± 6.48** |
| **B5 + B4** (concordi) | **+12.17 ± 5.90** | **−6.17 ± 1.72** | **+7.09 ± 5.03** | **+29.26 ± 8.77** |

### Cosa conta come conferma

La previsione è **confermata** se, per ciascuna delle due combinazioni, la media osservata sulle
sei celle cade entro ±1 DS propagata dalla previsione su **almeno 3 delle 4 grandezze**.

### Cosa conta come smentita, e cosa significherebbe

Due modi di fallire, opposti, e il test li distingue:

* **Sotto-additività** (l'osservato è sistematicamente più piccolo della somma, nello stesso
  verso): gli effetti saturano. Esisterebbe un tetto, e i preset non sarebbero sommabili oltre
  una certa intensità. Il segnale più netto sarebbe la saturazione di `B5 + B4`, prevista a
  +29.26: se esce intorno a +18–20 è sotto-additività, non rumore.
* **Cancellazione oltre il previsto** su `B5 + B1` (per esempio contrasto ≈ 0 invece di −3.23):
  i due blocchi non sarebbero manopole indipendenti sullo stesso asse ma la stessa manopola con
  segno diverso, e sommandoli si annullerebbero invece di comporsi.

Il numero più discriminante è il **contrasto di `B5 + B1`, previsto −3.23 ± 1.85**. Zero è a
1.75 DS dalla previsione: se esce ≈ 0 l'ipotesi è in difficoltà seria; se esce ≈ −3 è la
previsione più stretta del set ed è rispettata.

## 4. Limiti dichiarati prima del test

* Le previsioni poggiano su medie di **sei celle** con DS grandi (fino a 6.7). Sono intervalli
  larghi e il test è di conseguenza poco severo. Una conferma qui è una conferma debole: dice
  che l'additività non è violata in modo grossolano, non che è esatta.
* I prompt sono gli **stessi** `P01`/`P02` su cui gli effetti singoli sono stati misurati. Non
  è una replica su materiale indipendente: è un test di composizione sullo stesso materiale.
  Il corpus sigillato `data/prompts_sealed_krea2.json` (12 scene, generate meccanicamente con
  seme 20260919, impronta `fca56e49138f0480…`) esiste apposta per la replica indipendente **se
  e solo se** questo test passa.
* Il test è su Krea-2. Nulla di quanto ne esce è portabile ad Anima senza rimisurare: su Anima
  il preset non si separa nemmeno dai controlli a norma appaiata
  (`docs/anima_dosesweep_verifica.md` §4).

## 5. Registrazione

Le due tabelle del §3 sono definitive. Qualunque modifica successiva a questo documento va
fatta in aggiunta, con la data, senza riscrivere le previsioni.

---

# ESITO — aggiunto il 2026-09-19, ore 23:30, dopo la generazione

Le previsioni del §3 **non sono state modificate**. Quanto segue è aggiunto in coda.

12 immagini in `benchmark_composizione`, impostazioni identiche alla mappa, baseline e
condizioni singole riusati da `benchmark_mappa`.

## Risultato

| combinazione | grandezze entro 1 DS | esito |
|---|:--:|---|
| **B5 + B1** (opposti) | **4/4** | **CONFERMATA** |
| **B5 + B4** (concordi) | **0/4** | **SMENTITA** |

### B5 + B1 — confermata

| grandezza | previsto | osservato | scarto in DS |
|---|--:|--:|--:|
| alte luci | −2.67 ± 7.42 | −5.33 | −0.36 |
| ombre | +1.17 ± 2.69 | +0.50 | −0.25 |
| **contrasto** | **−3.23 ± 1.85** | **−3.02** | **+0.11** |
| saturazione | +8.79 ± 6.48 | +14.17 | +0.83 |

Il numero dichiarato come discriminante — il contrasto, previsto −3.23, con lo zero a 1.75 DS —
è uscito **−3.02**, e negativo in **tutte e sei le celle** (−1.85, −2.26, −2.90, −3.11, −3.21,
−4.81). Lo zero è escluso. Per questa coppia gli effetti si sommano.

### B5 + B4 — smentita, e non per saturazione

| grandezza | previsto | osservato | B5 solo | B4 solo | baseline |
|---|--:|--:|--:|--:|--:|
| alte luci | +12.17 | **−0.17** | +7.33 | +4.83 | 198.50 |
| contrasto | +7.09 | **−0.51** | +3.47 | +3.61 | 61.77 |
| saturazione | +29.26 | **+11.63** | +17.13 | +12.14 | 69.27 |

La combinazione non sta fra la somma e il singolo: sulle alte luci e sul contrasto è **sotto
entrambi i singoli**, e torna al baseline. Due modifiche che separatamente alzano le alte luci,
insieme non le alzano affatto.

Confronto appaiato sulle sei celle, test dei segni esatto:

| | differenza | p |
|---|--:|--:|
| B5B4 − B5, alte luci | −7.50 | **0.031** |
| B5B4 − B4, alte luci | −5.00 | **0.031** |
| B5B4 − B4, contrasto | −4.12 | **0.031** |
| B5B4 − B5, contrasto | −3.98 | 0.156 |
| B5B4 − B5, saturazione | −5.50 | 0.188 |

## Spiegazioni alternative, esaminate ed escluse

**Tetto della metrica.** `fari` ha baseline 198.50 su un massimo di 255: la previsione +12.17
richiedeva 210.67, con 56 punti di margine. Nessun tetto. Idem per contrasto e saturazione.

**Errore di disegno riconosciuto**: la previsione su `ombre` era **fisicamente irrealizzabile**.
Baseline 4.83, previsione −6.17, cioè −1.34 su una grandezza che non può scendere sotto 0; `B4`
da solo era già a 0.83. Quella grandezza andava esclusa *a priori* e non è stata controllata
prima di committare la previsione. Vedi pitfall 56. La conclusione non cambia: le altre tre
hanno margine abbondante e sono smentite tutte e tre.

**Normalizzazione del nodo fra slot attivi.** Se accendere due slot dimezzasse ciascuno,
anche `B5B1` sarebbe stato dimezzato e il contrasto sarebbe uscito ≈ −1.6 invece di −3.23.
È uscito −3.02. Esclusa.

**Riorganizzazione della scena.** Se la doppia modifica avesse spostato l'immagine altrove, le
statistiche globali confronterebbero scene diverse. È vero **il contrario**: `B5B4` ha la
coerenza di traiettoria **più alta** di tutte le condizioni misurate (0.098 contro 0.072 di
`B5` e 0.060 di `B4`), con p = 0.031 su entrambi i confronti appaiati. E le immagini sono
visibilmente la stessa scena, stessa posa, stessa composizione. Esclusa.

## La dissociazione

| coppia | effetti tonali | coerenza di traiettoria |
|---|---|---|
| **B5 + B1** (tonalmente opposti) | si **sommano** come previsto | **0.039** — la più bassa misurata, p = 0.031 vs `B5` |
| **B5 + B4** (tonalmente concordi) | si **annullano** | **0.098** — la più alta misurata, p = 0.031 vs entrambi |

La coppia che si somma nel tono è quella che disturba di più la traiettoria; la coppia che si
annulla nel tono è quella che la conserva di più. La relazione è inversa in entrambe le
direzioni e su tutti e quattro i confronti appaiati.

**Non c'è un meccanismo proposto per questo, e non se ne inventa uno adesso.** Il fatto è
registrato come tale.

## Cosa cambia nella linea di ricerca

L'ipotesi che i preset siano **progettabili** — si sceglie l'effetto, si risolve per i guadagni
— sopravvive solo in forma condizionata: vale per modifiche che si oppongono sull'asse tonale,
non per modifiche che concordano. Una procedura di progetto che assumesse additività generale
produrrebbe preset sistematicamente più deboli del previsto, e nel caso peggiore nulli.

Questo è il motivo per cui il test valeva dodici immagini. Costruire sopra l'additività senza
averla misurata avrebbe prodotto mesi di taratura a mano per compensare un effetto che non
c'era.

**Il corpus sigillato `data/prompts_sealed_krea2.json` resta chiuso.** La condizione per
aprirlo era che questa previsione passasse; è passata a metà, e metà non basta. Serve prima
capire la regola che distingue le coppie che si sommano da quelle che si annullano — e quella
va cercata sull'esplorativo, non sul sigillato.
