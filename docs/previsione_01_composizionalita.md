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
