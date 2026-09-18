# Pre-registrazione — l'ingrandimento del soggetto sotto blockshuf_neg, su corpus nuovo

**Depositata prima che esista un solo render di stage 12.** Congelata: se qualcosa deve cambiare, si
aggiunge in fondo con data e motivo, e l'originale resta visibile.

## Che cosa cambia rispetto a tutto quello fatto finora sui bbox

La prima tornata (`68c0875`, verificata in `fca0d58`) ha **quantificato** un'osservazione nata
guardando quegli stessi render, con una mano che conosceva l'ipotesi e riconosceva le condizioni a
vista. Quella non poteva essere una conferma.

Questa lo è: **render nuovi, che l'annotatore non ha mai visto**, con stili, colore del veicolo e
ambientazione diversi, previsione scritta qui sotto prima che esistano.

## L'ipotesi

> Una perturbazione dei pesi `blockshuf_neg` **aumenta la porzione di fotogramma occupata dal soggetto
> nominato dal prompt**, e l'aumento cresce con l'ampiezza. `preset_pos` si muove nella direzione
> **opposta**.

## Il corpus

**Dieci** stili nuovi, nessuno dei quali usato in stage 9. Soggetto: un veicolo, **di colore diverso**
da quello di stage 9 e in **ambientazione diversa**. Struttura del prompt identica a stage 9
(`Style: … . Subject: … .`), così che l'unica cosa che cambia fra i dieci sia la clausola di stile.

Perché dieci e non sette: il pavimento della permutazione esatta è $2/2^n$, e con Holm su tre
condizioni serve $p \le 0.0167$.

| prompt | pavimento $2/2^n$ | dopo Holm ×3 | utilizzabile |
| --- | --- | --- | --- |
| 7 | 0.0156 | 0.047 | al filo, serve 7/7 |
| 8 | 0.0078 | 0.023 | sì |
| **10** | **0.0020** | **0.0059** | **con margine** |

Prompt fissati e hashati prima di renderizzare. **Non si toccano** dopo: `prompt_sha1` esiste per
accorgersene.

## Condizioni e budget

`baseline` · `blockshuf_neg_1x` · `blockshuf_neg_2x` · `preset_pos_2x` — cinque seed standard
(42, 777, 1337, 9999, 4242145).

`preset_pos_2x` è il **controllo negativo** ed è la parte che rende questa pre-registrazione difficile
da superare per caso: una previsione bidirezionale non si produce con un bias inconscio unidirezionale.

10 × 4 × 5 = **200 render.** Circa due ore.

## La misura

Bounding box a quattro punti estremi, tracciati a mano, con lo strumento del
`BRIEF_stage11_bbox_controllo.md`: quattro click in **ordine libero**, rettangolo derivato come
`alto = y minima`, `basso = y massima`, `sinistra = x minima`, `destra = x massima`, conferma dopo il
quarto click.

### La statistica primaria è un RAPPORTO, non una differenza

L'area in punti percentuali di canvas **non è confrontabile fra corpus diversi**: con sfondo e
inquadratura nuovi il baseline parte da una dimensione diversa. La quantità che viaggia è

$$\rho = \frac{\text{area}_{\text{condizione}}}{\text{area}_{\text{baseline appaiata}}}$$

Nella prima tornata: 13.22% → 28.28% di canvas, cioè $\rho = 2.14$ per `blockshuf_neg_2x`.

La differenza in punti percentuali si riporta comunque, come secondaria.

## Cecità — tre livelli, e il terzo è nuovo

1. **Prima esposizione dentro lo strumento.** L'annotatore **non vede i render prima di annotarli**:
   nessun contact sheet, nessun controllo qualità a occhio, nessuna anteprima. Il gate di
   degradazione gira in automatico e **il suo esito non viene mostrato prima dell'annotazione**,
   perché "la condizione X ha prodotto render rotti" è una fuga di informazione.
2. **Chiave nuova, sigillata.** Hash nuovi, ordine rimescolato con seme nuovo, chiave scritta prima e
   aperta dopo l'ultimo punteggio. Non si riusa nessuna chiave esistente.
3. **Disturbi randomizzati e registrati**, come in `BRIEF_stage11_bbox_controllo.md`: specchiatura e
   ribaltamento (che **non cambiano l'area**), rotazione di tinta, saturazione 0.6–1.6, luminosità
   0.85–1.15, rumore gaussiano σ 0–4. Decisi a caso, mai in funzione della condizione, e salvati per
   ogni immagine insieme alla chiave.

Nessuna trasformazione geometrica oltre a specchiatura e ribaltamento: niente ritaglio, niente
riscalatura, niente rotazione libera.

Più **20 duplicati nascosti** con stato di specchiatura diverso dalla prima occorrenza, stratificati
sull'intervallo di dimensioni e distanziati nella sequenza. **Totale presentato: 220 immagini.**

## La regola di decisione, fissata adesso

**Primaria.** $\rho > 1$ per `blockshuf_neg_2x`, per permutazione esatta sign-flip sui 10 prompt,
$p < 0.05$ dopo Holm sulle tre condizioni.

**Direzionale, e vincolante.** I tre segni previsti sono:

> `blockshuf_neg_1x` $\rho > 1$ · `blockshuf_neg_2x` $\rho > 1$ e maggiore di quello a 1× ·
> `preset_pos_2x` $\rho < 1$

Una condizione che raggiunge la significatività con il **segno sbagliato** conta come **fallimento**
di questa pre-registrazione, non come successo parziale.

**Confermata** se la primaria passa e nessun segno è invertito.
**Rifiutata** se la primaria non passa, o se un segno si inverte con significatività.
**Ambigua**, e riportata come tale senza arrotondare, se la primaria passa ma `preset_pos_2x` va nella
direzione sbagliata senza significatività.

## Diagnostiche pubblicate comunque, qualunque sia l'esito

1. **Rumore dell'annotatore**, dai 20 duplicati: differenza assoluta media fra le due annotazioni
   della stessa immagine e sua deviazione standard. È il metro con cui si legge tutto il resto, e non
   è mai stato misurato.
2. **Regressione dei disturbi**: area annotata su saturazione, luminosità e rumore applicati, con
   effetti per prompt. Se la saturazione che abbiamo applicato noi predice quanto grande viene
   tracciato il box, il bias esiste ed è quantificato; se non la predice, è escluso per misura.
3. **Accoppiamento dimensione–colore nel nuovo corpus.** Su stage 9 area e `colorfulness_hs`
   correlavano a $r = +0.776$ **nel solo baseline**: più auto nel fotogramma, più pixel saturi in una
   scena con sfondo verde. Con sfondo nuovo quel coefficiente cambia, e va ricalcolato e pubblicato —
   serve a sapere quanta parte di un eventuale effetto cromatico sia in realtà dimensione.
4. **Gate di degradazione** a 2.0×, censito e riportato. **Non si scartano celle**: su stage 9 le
   celle marcate DEGRADED erano spesso quelle che a occhio funzionavano meglio, e il gate non
   distingue "danneggiato" da "fortemente ri-stilizzato".

## Un secondo esito che viaggia gratis, se lo si vuole

Gli stessi 200 render possono servire a confermare il risultato dei fari, che oggi è quantificato ma
non confermato. I fari sono un tratto **implicato dall'oggetto e mai nominato nel prompt**, e la
prima tornata ha dato baseline 0.286 → `preset_pos_2x` 0.816 e `blockshuf_neg_2x` 0.000 su 39.

Richiede `preset_pos_1x` fra le condizioni (quindi 250 render invece di 200) e una **passata di
scoring separata**, con rimescolamento indipendente, **prima** di quella dei bbox perché è più veloce
e meno scrutinante. Costa una decina di minuti in più di annotazione.

Se si fa, va registrato qui prima di renderizzare: previsione `preset_pos` accende, `blockshuf_neg`
spegne, con la stessa clausola sul segno sbagliato.

## Cosa NON si fa

* Non si mostra nessun render all'annotatore prima dell'annotazione, in nessuna forma.
* Non si riusa nessuna chiave esistente.
* Non si sceglie la trasformazione in funzione della condizione.
* Non si guardano le diagnostiche 1–3 prima che l'annotazione sia chiusa.
* Non si modificano i prompt dopo l'hash.
* Non si scarta nessuna cella per degradazione.

---

## Registrazione Formale del Corpus e Scelta del Budget (2026-09-18)

In accordo con le decisioni operative approvate prima del lancio dei render:

### 1. Budget Scelto: 250 Render (Ingrandimento BBox + Conferma Fari)
- **5 Condizioni**: `baseline`, `blockshuf_neg_1x`, `blockshuf_neg_2x`, `preset_pos_1x`, `preset_pos_2x`
- **5 Seed standard**: `42`, `777`, `1337`, `9999`, `4242145`
- **Totale**: 10 stili × 5 condizioni × 5 seed = **250 render**
- **Doppia ipotesi confermativa**:
  1. *Ingrandimento BBox*: $\rho > 1$ su `blockshuf_neg_1x` e `blockshuf_neg_2x`, con $2\text{x} > 1\text{x}$; $\rho < 1$ su `preset_pos_2x`.
  2. *Accensione Fari*: tasso fari accesi $\text{Rate}(\text{preset\_pos}) > \text{Rate}(\text{baseline})$ e $\text{Rate}(\text{blockshuf\_neg}) < \text{Rate}(\text{baseline})$.

### 2. Manifest dei 10 Prompt e Hash Congelati
Soggetto comune a tutti i 10 prompt:
`Subject: a red and white vintage sports car cruising along a scenic coastal cliff road, ocean waves, rocky shoreline, golden hour, clear sky.`

| Prompt ID | SHA-1 (10 hex) | Stile Dichiarato |
| :--- | :---: | :--- |
| `S01_oil` | `6de4189f5e` | classic oil painting on textured canvas, visible impasto brushwork, rich blending, fine art realism |
| `S02_linocut` | `e20e86ac75` | bold linocut print, sharp relief carving, graphic ink lines, paper texture, stark contrasts |
| `S03_cyberpunk` | `6ab02b69aa` | neon cyberpunk digital art, glowing vibrant neon lights, glossy surfaces, chromatic aberration, high-tech aesthetic |
| `S04_gouache` | `6335032007` | opaque gouache illustration, matte finish, layered flat brushstrokes, vibrant poster art |
| `S05_pencil` | `9a68323a39` | detailed graphite pencil drawing, fine cross-hatching, smooth shading, tonal gradients, sketchbook paper |
| `S06_pastel` | `61861c7677` | soft chalk pastel drawing, powdery texture, smudged colors, velvety highlights, tinted paper |
| `S07_comic` | `69f4e68eba` | classic western comic book art, dynamic ink inking, halftones, benday dots, cel shading |
| `S08_papercraft` | `17e466c859` | layered cut paper craft, 3D paper collage, visible paper edges, cast shadows, tactile depth |
| `S09_fresco` | `9e81add78f` | ancient Renaissance fresco mural, weathered plaster texture, distressed pigment, crackled wall surface |
| `S10_synthwave` | `25147e923b` | retro 80s synthwave vector art, wireframe grid, duotone gradient, airbrush aesthetic, retrowave styling |

---

## Dichiarazione a verbale dell'operatore umano (2026-09-18 16:36:09)

> *«Metti agli atti che ho odiato fare la prima versione di questo esperimento e la mia previsione è che lo odierò ancora di più questa volta.»*  
> — **Alessandro** (Human Operator / Lead Annotator)

*Nota metodologica a verbale:*  
Registrata formalmente prima dell'inizio della sessione di scoring cieco a 220 immagini (disturbi visivi su 3 livelli + 20 duplicati nascosti). La previsione soggettiva sul gradimento del compito non inficia la validità della procedura a doppio cieco, ma certifica in modo trasparente e indelebile il gravoso costo cognitivo imposto dal rigore metodologico pre-registrato.
