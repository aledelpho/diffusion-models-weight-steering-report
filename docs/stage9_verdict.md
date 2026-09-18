# Stage 9 — verdetto sotto i criteri ripristinati

**Data**: 2026-09-18. Analisi eseguita una volta sola (commit `e5f755a`), emendamento metodologico
congelato prima (`bd784ca`, ore 11:23, con 220/300 render in coda e nessuna estrazione fatta).
I criteri di accettazione applicati qui sono quelli depositati alle 08:55 in `35de7d8` e ripristinati
dall'emendamento 6.

## Verdetto

**L'ipotesi non è confermata. All'ampiezza utilizzabile è rovesciata.**

| criterio | esito |
| --- | --- |
| 1 · Conferma piena (Spazio 1 **e** Spazio 4) | **non soddisfatto** — lo Spazio 4 non è mai significativo, a nessuna ampiezza |
| 2 · Artefatto da vincolo cromatico (Spazio 3 sì, Spazio 4 no) | **soddisfatto** a 2.0x per `preset_pos` ($p = 0.0167$) e `rand_pos` ($p = 0.0004$) |
| 3 · Dose-risposta (solo a 2.0 ⇒ over-steering) | **soddisfatto** — a 1.0x nessuna cella è significativa |

I criteri 2 e 3 sono entrambi clausole di artefatto, e scattano tutte e due.

## Il rovesciamento a 1.0x

A 1.0x la coerenza *fra stili diversi* è **maggiore** di quella *fra soggetti diversi* — il contrario
di quanto previsto:

| Spazio, condizione | $\bar{C}_{\text{stile}}$ | $\bar{C}_{\text{sogg}}$ | $\Delta$ | $p$ |
| --- | --- | --- | --- | --- |
| 1 · 24-D, `preset_pos` | 0.1284 | 0.0244 | **−0.1040** | 0.9914 |
| 2 · L\*, `preset_pos` | 0.3538 | 0.0936 | **−0.2602** | 0.9978 |
| 4 · tessitura, `preset_pos` | 0.4770 | 0.1497 | **−0.3273** | 0.9848 |
| 4 · tessitura, `blockshuf_neg` | 0.3857 | 0.2844 | **−0.1013** | 0.7887 |

Il rovesciamento è robusto alla convenzione di standardizzazione: ricalcolato senza centratura dà
$\Delta = -0.1874$ sulla prima riga, contro $-0.1040$ con centratura. Entrambi negativi.

## Perché le cinque celle `CONFIRMED` a 2.0x non reggono

Quattro ragioni, ciascuna sufficiente da sola.

**1 · Cambiano segno senza centratura.** Ricalcolate dividendo solo per $\sigma$ senza sottrarre
$\mu_{\text{congiunta}}$, tutte e cinque si rovesciano (`data/stage9_centering_sensitivity.csv`):

| cella | $\Delta$ centrato | $\Delta$ non centrato |
| --- | --- | --- |
| `preset_pos_2x` · 24-D | +0.1172 | **−0.1747** |
| `rand_pos_2x` · 24-D | +0.0876 | **−0.0305** |
| `blockshuf_neg_2x` · L\* | +0.1265 | **−0.1849** |
| `preset_pos_2x` · a\*b\* | +0.2112 | **−0.1225** |
| `rand_pos_2x` · a\*b\* | +0.1453 | **−0.0411** |

**2 · Il braccio è fuori range.** 18 celle su 24 a 2.0x sono `DEGRADED` dal gate dell'emendamento 5,
una a $z = 131.7$ su `lbp_entropy`.

**3 · Il confronto è confuso con l'ampiezza.** Non esiste un corpus soggetti a 2.0x: quelle righe
confrontano stile a $D \approx 0.108$ contro soggetto a $D \approx 0.0538$.

**4 · La disattenuazione le fabbrica.** Su `preset_pos` 24-D il $p$ grezzo è 0.4290 e il disattenuato
0.0279. Il corpus di confronto è il più rumoroso ($r_5 = 0.32$ contro 0.68), quindi dividere per il
suo $r$ gonfia $\bar{C}_{\text{soggetto}}$. Vedi emendamento 6.2.

**La colonna `decision` di `data/stage9_coherence_results.csv` è superata** e va letta contro questa
tabella: implementa la regola piatta per cella dell'emendamento 2, non i criteri 1-3.

## Cosa il rovesciamento significa, e cosa non significa

Non è evidenza che lo stile dichiarato sia irrilevante per la direzione di steering, e leggerlo così
sarebbe un errore simmetrico a quello che si voleva evitare.

Gli otto prompt di stile sono **otto varianti di una sola scena** (la stessa auto da rally nella
stessa giungla); i diciotto di soggetto sono diciotto scene diverse. Condividere la scena è
esattamente ciò che alza la coerenza misurata. Il disegno non separa *condividere la scena* da
*variare lo stile* — è il limite di scambiabilità dichiarato a priori nell'emendamento 4, e qui morde
per intero. L'affidabilità lo conferma dall'altro lato: $r_5$ del corpus di stile è più alto proprio
perché la scena condivisa rende i seed più simili fra loro.

La lettura difendibile è quindi: **a parità di scena, la direzione impressa dalla perturbazione è
notevolmente stabile attraverso stili dichiarati molto diversi** — fotografia, acquerello, pixel art,
carboncino. È un'osservazione, non un risultato registrato, e il disegno incrociato la metterebbe
alla prova.

## Cosa resta utilizzabile di stage 9

* I 280 render a 1.0x e 2.0x, con prompt hashati e protocollo documentato. Sono dati buoni.
* Il censimento delle celle degradate a 2.0x, che l'emendamento 5 dichiara essere di per sé una
  misura di stabilità geometrica oltre saturazione: **18 su 24**, con `blockshuf_neg` la condizione
  che degrada più spesso e più violentemente.
* L'affidabilità split-half pubblicata per entrambi i corpora, che è la prima misura di validità
  dello strumento cromatico mai prodotta in questo progetto.
* Il fatto che $r_5$ dipenda fortemente da quanto i prompt di un corpus condividono la scena: è un
  vincolo di disegno che riguarda ogni confronto fra corpora fatto finora, §1.5 compreso.
