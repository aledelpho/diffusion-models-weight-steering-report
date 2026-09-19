# Revisione indipendente — Anima Stage 1 (19/09/2026)

Rianalisi di `anima1_features_enriched.csv` (370 render) a fronte di
`docs/anima_stage1_results.md`. Stesso test dichiarato nel brief: permutazione esatta a
scambio di segno sulle medie per prompt, $n = 10$, pavimento $2/2^{10} = 0.00195$.
Nessun numero del documento originale è risultato sbagliato: i problemi sono di
correzione per molteplicità, di attribuzione e di omissione.

---

## 1. Il risultato primario regge, ed è un risultato vero

Con la correzione di Holm sulla famiglia delle 9 feature misurate, `preset` contro
`randsign` nel braccio A:

| feature | diff | $p$ | $p_{\text{Holm}}$ | |
|---|---:|---:|---:|---|
| `crosshatch_entropy_mean` | $+0.2161$ | 0.0020 | **0.0176** | sopravvive |
| `contour_mean_length_px` | $-20.235$ | 0.0020 | **0.0176** | sopravvive |
| `stroke_width_median_px` | $-0.782$ | 0.0098 | 0.068 | — |
| `glcm_homogeneity` | $-0.0343$ | 0.0215 | 0.129 | — |
| `edge_density` | $+0.0175$ | 0.0273 | 0.137 | — |
| `white_background_pct` | $+25.06$ | 0.0469 | 0.188 | — |

**Due feature sopravvivono, non cinque.** Entrambe al pavimento esatto del test, entrambe
sulla morfologia del tratto, che è esattamente l'asse dichiarato nel brief. Il criterio
primario pre-registrato — separazione dal controllo appaiato in dose con CI che esclude lo
zero — **è soddisfatto**. Questo è il risultato, ed è solido.

Il documento originale dichiara "CONFERMATO" per cinque feature senza correzione per
molteplicità. Tre di quelle cinque non sopravvivono, e una delle tre è l'ipotesi sullo
sfondo bianco.

## 2. Lo sfondo bianco: l'effetto c'è, ma non è del preset

Il documento presenta `white_background_pct` come conferma che *"il preset preserva lo
stacco su spazio negativo comics"*. Contro il baseline:

| condizione | diff vs baseline | $p$ |
|---|---:|---:|
| `preset` | $-5.59$ | **0.475** |
| `preset_nocross` | $-6.06$ | 0.440 |
| `blockshuf_neg` | $-3.37$ | 0.512 |
| `randsign` | $\mathbf{-30.66}$ | **0.0039** |

**Il preset non fa nulla allo sfondo bianco.** Solo `randsign` lo distrugge. La differenza
`preset − randsign` di $+25\%$ è reale ma è interamente attribuibile al controllo, e
descriverla come una proprietà del preset gli accredita un effetto che non ha. La
formulazione corretta è: *lo scramble dei segni distrugge la separazione figura-sfondo; le
perturbazioni strutturate la lasciano dov'era.*

Va aggiunto che `white_background_pct` non compare nel brief congelato né in
`style_features.py`: è stata aggiunta in corso d'opera. Qualunque cosa sia stata dichiarata
a voce, rispetto al protocollo scritto è **post-hoc**, e va etichettata come tale.

## 3. Quello che non ha replicato, e non è stato scritto

Su Krea-2 il risultato di §1.6 non era "il tratteggio cambia". Era che **preset e
blockshuffle spingono in direzioni opposte** lungo l'asse del tratteggio, con il segno
predetto in anticipo, e che `randsign` era assente. Era la direzionalità a rendere il
risultato più di "qualcosa si muove".

| `crosshatch_entropy_mean`, diff vs baseline | Krea-2 (16 prompt) | Anima (10 prompt) |
|---|---:|---:|
| `preset` | $\mathbf{-0.370}$ | $\mathbf{+0.292}$ |
| `blockshuffle` | $\mathbf{+0.288}$ | $\mathbf{+0.280}$ |
| `randsign` | $+0.020$ (n.s.) | $+0.076$ ($p = 0.023$) |

Su Anima le due condizioni strutturate si muovono **nello stesso verso e della stessa
quantità**. Il confronto diretto `preset` contro `blockshuf_neg` su quella feature dà
$+0.0126$, $p = 0.86$: indistinguibili.

**L'asse di tratteggio non si trasferisce.** Quello che si trasferisce è la distinzione fra
perturbazione strutturata e scramble di segno, che è una claim più debole e va scritta come
tale. Il documento originale non menziona il confronto preset-blockshuffle da nessuna parte.

Seconda differenza dello stesso tipo: **su Anima `randsign` non è inerte.** Contro il
baseline muove `glcm_contrast` ($-5.92$, 10/10, al pavimento), `lbp_entropy` ($+0.32$,
10/10, al pavimento), il tratteggio ($p = 0.023$), la lunghezza dei contorni ($p = 0.016$) e
lo sfondo bianco ($p = 0.004$). Su Krea-2 `randsign` produceva esattamente il tasso del
modello stock. L'argomento "struttura, non magnitudo" su questa architettura è quindi
*relativo*, non *assoluto*: le condizioni strutturate si separano dallo scramble, ma lo
scramble fa parecchie cose.

Correlato: **`lbp_entropy` sale in tutte e quattro le condizioni**, da $+0.32$ a $+0.42$,
tutte al pavimento, 10/10 prompt. È una componente comune a qualunque perturbazione a questa
dose: non discrimina niente e non va usata come evidenza.

## 4. La scoperta che c'era e non è stata vista

| `colorfulness_hs`, diff vs baseline | valore | $p$ | concordi |
|---|---:|---:|---:|
| `preset` | $+3.30$ | 0.697 | 4/10 |
| `preset_nocross` | $+5.38$ | 0.588 | 4/10 |
| **`blockshuf_neg`** | $\mathbf{+37.75}$ | **0.0059** | **9/10** |
| `randsign` | $+0.66$ | 0.838 | 6/10 |

E nel confronto diretto `preset` contro `blockshuf_neg`, `colorfulness_hs` è una delle due
sole feature che sopravvivono a Holm ($-34.45$, $p_{\text{Holm}} = 0.047$).

Ora si confronti con Krea-2, §1.4: *"Il preset non steera il colore"* ($\cos = -0.165$,
$p = 0.81$), e **l'unica condizione che impone un cast cromatico coerente è
`blockshuffle −`** ($\cos = +0.944$, $p < 0.0001$).

**È la stessa condizione, con la stessa specificità, su un'architettura diversa.** Nessuna
delle altre tre tocca il colore; `blockshuf_neg` lo muove del 68% sul 90% dei prompt. Questa
è la replica cross-architettura più pulita dell'intero dataset, ed è più forte del risultato
primario perché è *specifica per condizione* invece che generica. Il documento originale non
parla di colore se non per elencarlo fra i non significativi nella riga
`preset` vs `randsign` — dove in effetti non è significativo, perché nessuna delle due tocca
il colore.

## 5. La "legge di riscalatura della dose" non è una legge

Il documento propone
$\text{Dose} \propto D_{\text{backbone}} \times N_{\text{steps}} / N_{\text{ref}}$
e la dichiara "scoperta e validata" perché $9/30 = 0.30$ coincide con la dose scelta.

Tre problemi.

1. **Un solo punto.** Sono state provate tre dosi (100, 50, 30) a un solo conteggio di passi,
   e si è scelta quella che rendeva meglio. Che il rapporto scelto coincida con $9/30$ è
   un'osservazione su due numeri, non una relazione misurata. Servono almeno due conteggi di
   passi diversi con la dose di soglia trovata in entrambi.
2. **Il meccanismo proposto non è testato.** L'idea sottostante — più passi accumulano più
   effetto della perturbazione, quindi serve meno dose — è plausibile e verificabile, ma non
   è stata verificata: nessuna misura lega l'ampiezza dell'effetto al numero di passi.
3. **Incoerenza interna.** Se la legge valesse, il braccio B a 9 passi avrebbe dovuto usare
   dose **100%**, non 30%. Se ha usato gli stessi checkpoint `scaled30` del braccio A, è
   sotto-dosato di $3.3\times$ **secondo la legge stessa del documento**, e il suo fallimento
   a convergere si spiega senza tirare in ballo il regime di campionamento. La diagnosi
   contiene `solD_preset_dose100_cfg10_steps9`, cioè esattamente il punto che servirebbe: va
   guardato prima di concludere.

Finché non è risolto, il braccio B non dimostra che "un modello non distillato richiede i
suoi passi": dimostra che *quella* combinazione di dose e passi non converge.

## 6. Cosa regge, in una riga ciascuno

* **Regge**: la trasposizione gerarchica del preset produce su Anima una firma di morfologia
  del tratto che si separa dal controllo appaiato in dose, su due feature, al pavimento del
  test, con correzione per molteplicità. Criterio primario soddisfatto.
* **Regge**: la cross-attention è quasi inerte per il tratto — `preset` e `preset_nocross`
  sono indistinguibili su 8 feature su 9. L'unica eccezione, `glcm_contrast` ($+1.97$,
  $p_{\text{Holm}} = 0.018$), impedisce di dire "al 100%": un pezzo di contrasto di texture
  passa di lì.
* **Regge e vale più del resto**: `blockshuf_neg` è l'unica condizione che muove il colore,
  su entrambe le architetture.
* **Non regge**: tre delle cinque feature "confermate" non sopravvivono a Holm.
* **Non regge**: lo sfondo bianco come proprietà del preset.
* **Non regge**: la legge di riscalatura della dose.
* **Non replica**: l'asse di tratteggio, cioè la parte direzionale del risultato di Krea-2.
* **Da non usare**: `lbp_entropy`, che si muove in tutte le condizioni.

## 7. Dettaglio da correggere nei file

Nei preset `*_scaled30.json` e `*_scaled50.json` il campo `achieved_D_model` è aggiornato
correttamente ($0.013724$ e $0.022873$), ma `achieved_D_full_checkpoint` è rimasto al valore
non scalato ($0.0013898$). Chi legge quel campo per ricostruire la dose ottiene il numero
sbagliato.
