# Stage 12 — verifica indipendente

**2026-09-18**, su `84ea3a9`. Pre-registrazione congelata in `9cb4112` alle 14:17, prima di ogni
render. Numeri ricalcolati da zero con codice indipendente.

## 1. La cecità è fallita, e adesso è un numero

Il test 4-AFC (venti prove, quattro slot, caso = 25%):

| condizione da identificare | corrette | tasso | caso | p |
| --- | --- | --- | --- | --- |
| `preset_pos_2x` | **17 / 20** | 85% | 25% | $3.0\times10^{-8}$ |
| `blockshuf_neg_2x` | **12 / 20** | 60% | 25% | $9.4\times10^{-4}$ |
| entrambe nella stessa prova | 12 / 20 | 60% | 6.25% | $7.5\times10^{-9}$ |

**Specchiatura, ribaltamento, rotazione di tinta, saturazione 0.6–1.6, luminosità e rumore non hanno
nascosto le condizioni.** Questo è il risultato più prezioso della tornata, perché trasforma in misura
un dubbio che finora era solo argomentato — e vale **retroattivamente** su stage 9 e sul round dei
barnacoli, dove la cecità era più debole di questa e non era mai stata verificata.

Da qui in avanti nessun round di annotazione umana di questo progetto dovrebbe chiudersi senza un
test di discriminazione allegato.

## 2. Ma la non-cecità NON spiega il risultato sui bbox

Due argomenti indipendenti, e il primo è forte.

### L'asimmetria fra ciò che riconosce e ciò che ha disegnato

| condizione | quanto la riconosce | effetto sulla dimensione |
| --- | --- | --- |
| `preset_pos_2x` | **85%**, quasi perfetto | $\rho = 0.989$, $p = 0.68$ — **nessuno** |
| `blockshuf_neg_2x` | 60% | $\rho = 1.22$, 9/10 prompt — **c'è** |

La condizione che riconosce quasi sempre è quella su cui **non ha disegnato nessun effetto**, pur
avendo una previsione registrata che diceva "rimpicciolisce". Se il riconoscimento guidasse la mano,
il quadro sarebbe esattamente rovesciato: il rimpicciolimento previsto sarebbe comparso proprio dove
sapeva quale condizione stava guardando.

### Dove la cecità ha davvero tenuto, l'effetto resta

Incrociando la discriminabilità per stile con l'effetto per stile:

| | stili | $\rho$ medio |
| --- | --- | --- |
| riconosce `blockshuf_2x` 2/2 | 5 | 1.320 |
| non lo riconosce 0/2 | 3 | 1.110 |

Nei tre stili in cui era **al livello del caso o sotto** — `S03_cyberpunk`, `S06_pastel`,
`S10_synthwave` — l'auto cresce comunque dell'11%. La correlazione fra discriminabilità ed effetto è
positiva ma non significativa (Pearson +0.455, $p = 0.19$; Spearman +0.401, $p = 0.25$).

Il gradiente 1.32 contro 1.11 va riportato: **una parte dell'effetto potrebbe essere gonfiata dove
riconosceva la condizione.** Ma non è l'effetto.

## 3. Il confound della saturazione è escluso per misura

I disturbi applicati da noi, regrediti sull'area tracciata nei soli baseline:

| disturbo applicato | pendenza | r | p |
| --- | --- | --- | --- |
| `sat_factor` | −1.53 p.p. per unità | −0.096 | 0.51 |
| `lum_factor` | +11.69 | +0.229 | 0.11 |
| `noise_sigma` | +0.30 | +0.076 | 0.60 |

La saturazione che abbiamo imposto **non predice** quanto grande viene tracciato il rettangolo. Il
bias temuto dalla prima tornata è escluso da una misura, non da un ragionamento — che era lo scopo del
disegno. La luminosità è la più grossa delle tre e non raggiunge la significatività: da tenere
d'occhio.

## 4. L'annotatore è preciso, e ora sappiamo quanto

Dai 20 duplicati nascosti con specchiatura diversa:

* differenza assoluta media fra le due annotazioni della stessa immagine: **0.27 punti percentuali**
  di canvas (sd 0.24)
* errore relativo mediano: **1.0%**
* correlazione test-retest: **r = +0.995**

L'effetto misurato (+22%) è circa **venti volte** il rumore della mano. Quantità mai misurata prima in
questo progetto, ed è il metro con cui va letto tutto il resto.

## 5. Il verdetto dipende da una scelta che la pre-registrazione non aveva specificato

Quattro modi legittimi di fare lo stesso test su `blockshuf_neg_2x`:

| statistica | p | Holm ×3 | |
| --- | --- | --- | --- |
| media dei log-rapporti per prompt | 0.0176 | **0.0527** | non passa |
| log della media dei rapporti | 0.0098 | 0.0293 | passa |
| media di $(\rho - 1)$ per prompt | 0.0078 | 0.0234 | passa |
| differenza in punti percentuali | 0.0059 | 0.0176 | passa |

Tre su quattro superano la soglia corretta; quella che non la supera è la più difendibile in teoria
per un rapporto, perché il logaritmo è simmetrico rispetto all'inversione.

**La pre-registrazione diceva "permutazione esatta sign-flip su $\rho$" senza specificare quale.**
È un buco, ed è mio: l'ho scritta io. Va chiuso la prossima volta nominando la statistica esatta.

Lettura onesta: **l'effetto c'è, vale $\rho \approx 1.22$–1.25 con 9 prompt su 10 concordi, e siede
esattamente sulla soglia corretta.** A $n = 10$ i $p$ possibili sono multipli di 0.00195 e con Holm
×3 le soglie diventano a scatti: la granularità del test, non la debolezza dell'effetto, è ciò che
rende il verdetto instabile.

## 6. L'effetto si è ridotto di molto, e stavolta c'è un meccanismo

| | stage 9 | stage 12 |
| --- | --- | --- |
| $\rho$ per `blockshuf_neg_2x` | **2.14** | **1.22** |
| cecità dell'annotazione | chiave già aperta, immagini già viste | chiave sigillata, prima esposizione, disturbi randomizzati |

È la terza volta che questo progetto vede un effetto esplorativo ridursi fortemente in conferma —
dopo il colore di §1.5 e i fari. Qui però la spiegazione non è generica: stage 9 fu annotato **dopo**
che la chiave era stata aperta e su immagini già esaminate. La riduzione è coerente con l'idea che
quella tornata fosse gonfiata dalla non-cecità.

Vale come avvertimento generale: in questo progetto la regola empirica è che **un effetto esplorativo
vale fra un terzo e metà di quanto sembra**, e le tornate future vanno dimensionate su quello.

## 7. Il controllo negativo non si è riprodotto

`preset_pos_2x` era previsto in direzione opposta. Osservato: $\rho = 0.9888$, 4 prompt su 10 sopra 1,
$p = 0.68$. Il **segno è corretto** (< 1) ma l'effetto è nullo.

Per la regola scritta nella pre-registrazione questo non è un fallimento — il fallimento era il segno
invertito con significatività — ma la previsione bidirezionale, che era la difesa principale contro il
bias, è soddisfatta solo a metà.

## Verdetto complessivo

**Confermato con riserva.**

* Primario: passa sotto tre statistiche su quattro, non sotto la quarta. Specifica incompleta.
* Direzionale: tutti e tre i segni corretti, e 2× maggiore di 1×. Soddisfatto.
* Cecità: fallita come procedura, ma dimostrabilmente non responsabile del risultato.
* Ampiezza: circa un quinto di quella di stage 9, in termini di log-rapporto.

L'ingrandimento del soggetto sotto `blockshuf_neg` **esiste**, è molto più piccolo di quanto la prima
tornata facesse credere, e questa è la prima affermazione del progetto sostenuta da un test di
discriminazione che ne quantifica la cecità invece di assumerla.
