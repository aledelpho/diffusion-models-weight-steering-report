# Bounding box — verifica indipendente, e una correzione che ne discende

**2026-09-18**, su `68c0875`. Numeri riprodotti da zero con codice indipendente.

## Riproduzione: esatta

| condizione | Δ area (punti percentuali di canvas) | prompt concordi | p esatto |
| --- | --- | --- | --- |
| `preset_pos_1x` | −0.86 | 1/8 | 0.0391 |
| `preset_pos_2x` | −1.67 | 2/8 | 0.0469 |
| **`blockshuf_neg_1x`** | **+4.06** | **8/8** | **0.0078** |
| **`blockshuf_neg_2x`** | **+15.06** | **8/8** | **0.0078** |
| `rand_pos_1x` | −0.22 | 2/8 | 0.4062 |
| `rand_pos_2x` | +2.44 | 7/8 | 0.0234 |

`p = 0.0078` è il pavimento esatto a 8 prompt ($2/2^8$), raggiunto con concordanza perfetta. Holm
su sei condizioni dà 0.0469: **è il primo risultato di questa tornata che supera la soglia corretta**,
e ci passa per un soffio strutturale, non per margine.

La crescita è **isotropa**: `blockshuf_neg_2x` dà +45.9% di larghezza e +49.3% di altezza. Un bias
che includesse un'ombra sotto o un riflesso di lato darebbe crescita su un asse solo. Questo è
coerente con un cambio di scala vero.

## Il gate anti-saturazione del brief: superato, e in direzione opposta a quella temuta

Il brief chiedeva di verificare che la metrica non stesse misurando saturazione invece di dimensione.
Fra le sei condizioni, Δ colorfulness e Δ area bbox correlano a **Pearson r = +0.983** — a prima
vista, esattamente il confound temuto.

**Non lo è, e la prova sta nel baseline.** Immagine per immagine, dentro ogni singola condizione, area
del bbox e colorfulness correlano a r ≈ +0.75 ÷ +0.78 — **compreso il baseline, dove non c'è nessuna
perturbazione**. Un'auto che occupa più fotogramma mette più pixel saturi in una scena il cui sfondo è
verde giungla: è un accoppiamento meccanico delle immagini, non un errore della mano.

Quindi la direzione causale è **dimensione → saturazione**, non saturazione → bbox più grande. Il
confound che il brief temeva è disinnescato.

Regressione nel solo baseline: `colorfulness = 13.4 + 238.1 × frazione_area`, r = +0.776. Cioè
**+1 punto percentuale di area vale +2.38 di colorfulness.**

## La correzione che ne discende: la "firma cromatica" delle condizioni era in gran parte dimensione

Applicando quella pendenza alle variazioni di area misurate:

| condizione | Δ area | Δ colorfulness **attesa dalla sola dimensione** | Δ colorfulness osservata | quota spiegata |
| --- | --- | --- | --- | --- |
| `preset_pos_1x` | −0.86 | −2.06 | −2.17 | **95%** |
| `preset_pos_2x` | −1.67 | −3.97 | −3.54 | **112%** |
| `blockshuf_neg_1x` | +4.06 | +9.66 | +6.68 | **145%** |
| `blockshuf_neg_2x` | +15.06 | +35.84 | +27.69 | **129%** |
| `rand_pos_1x` | −0.22 | −0.53 | +1.44 | segno opposto |
| `rand_pos_2x` | +2.44 | +5.80 | +9.13 | 64% |

Per quattro condizioni su sei il cambiamento di dimensione **spiega interamente** quello di
saturazione, e per blockshuffle lo sovrastima — cioè a parità di ingrandimento la perturbazione
*riduce* la saturazione rispetto all'atteso.

**Questo corregge `observations_stage9.md` e il commit `09e2cc9`**, dove era scritto che
`blockshuf_neg` "satura fortemente" (+27.69, 8/8, 40/40) e `preset_pos` "desatura", presentandoli come
firme cromatiche delle condizioni. In larga parte **non sono firme cromatiche: sono la conseguenza
fotometrica di un soggetto che cambia dimensione**. La nota di correzione è in fondo a quel documento.

## Controllo sul corpus dei ritratti: §1.4 e §1.5 non sono toccate

La domanda ovvia è se lo stesso mediatore inquini i risultati cromatici già pubblicati. **No.** Sul
corpus stage 7 (ritratti con `white background`, dove `subject_frac` è valido):

* la dimensione del soggetto **quasi non si muove** sotto perturbazione: Δ`subject_frac` fra −0.016 e
  +0.020, con concordanza 4÷9 prompt su 16, cioè al livello del caso;
* e il suo accoppiamento con la croma è debole, r = +0.263 contro +0.776 nelle scene di giungla.

Ha senso: in un primo piano la testa riempie il fotogramma comunque. Il problema è **specifico dei
corpus a scena intera** e va dichiarato come vincolo per ogni corpus futuro di quel tipo.

## Il punto debole vero, che non è la saturazione

Il commit descrive l'annotazione come *blind*. **La procedura non lo sostiene.**

| | orario |
| --- | --- |
| chiave creata e sigillata | 12:17:29 |
| scoring dei fari (cieco) | 12:28 – 12:38 |
| **commit `f386bc4`: chiave aperta e risultati pubblicati** | **12:45:36** |
| **annotazione bbox** | **12:53 – 13:26** |

L'annotazione è partita **otto minuti dopo l'apertura della chiave**, riusando la *stessa* chiave. E
c'è un problema che nessun hash risolve: **`blockshuf_neg_2x` è visivamente riconoscibile a questo
osservatore** — è la condizione che aveva appena descritto come "più versatile e rispettosa dello
stile", ed è quella senza fari accesi, cosa che aveva appena letto nei risultati. Nascondere
l'etichetta nel nome del file non nasconde l'immagine.

La misura è un rettangolo tracciato a mano, continuo e soggettivo, su un'ipotesi che l'osservatore
possiede. È la configurazione in cui il bias inconscio opera meglio.

**Due cose in senso contrario, però, e pesano.** L'isotropia (+45.9% e +49.3%) è difficile da
produrre con un bias. E l'ampiezza: portare la larghezza a +46% su un compito di *punti estremi*
— si clicca dove l'auto visibilmente finisce — richiederebbe di cliccare ben dentro lo sfondo, il che
è un errore molto più difficile da commettere inconsciamente che non su un giudizio a scala.

## Come si chiude, a basso costo

Ri-annotare le due condizioni `blockshuf_neg` più i baseline (circa 120 immagini) su immagini
**convertite in scala di grigi e normalizzate in contrasto**, con una **chiave nuova, sigillata**, in
ordine rimescolato. Se l'ingrandimento sopravvive in grigio, non è né saturazione né riconoscibilità
cromatica. Mezz'ora di lavoro.

Nello stesso passaggio conviene inserire **una ventina di immagini duplicate sotto hash diversi**: la
stessa immagine annotata due volte dà una stima diretta del rumore dell'annotatore, che è la quantità
di cui qui stiamo discutendo e che non è mai stata misurata.

## Nota su `subject_frac` e sulla maschera per tinta

La maschera algoritmica per tinta ha correlazione **ρ = −0.0020** con il bbox vero: non misura nulla.
Il gate di accettazione del brief l'ha intercettata prima che producesse un risultato, ed è il motivo
per cui era stato scritto. Vale la pena registrarlo: una metrica plausibile, costruita con cura, e
completamente scorrelata dalla verità.
