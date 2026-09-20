# «Stanno solo facendo scrambling?» — quanto di ogni modifica è danno universale

**Data**: 2026-09-20 · **Domanda dell'utente**: «anche le rotazioni muovono le immagini in modo
simile, sarebbe da quantificare ogni spostamento per capire se c'è una differenza o se stanno
tutte a loro modo facendo solo una operazione di scrambling.»

**Materiale**: `rotations_block1_vs_block6`, 210 render — 10 stili × 3 seed × 7 condizioni, tutte
appaiate a $D_{\text{modello}} = 0.04500$ nello spazio dei pesi. Rotazioni di `Block_1` e
`Block_6` nei due segni, più **due scramble alla stessa $D$**. Ogni condizione è un vettore di
spostamento nello spazio a 23 feature di stile.

---

## 1. Un discriminatore che non funziona, e va detto

L'idea naturale è: una modifica *strutturata* spinge nella stessa direzione su scene diverse, uno
scramble manda ogni render dove capita. Misurato, il coseno medio fra le 435 coppie di celle:

| condizione | coerenza di direzione |
|---|--:|
| `Block_6_pos` | 0.901 |
| **`scramble_A`** | **0.814** |
| `Block_6_neg` | 0.742 |
| `Block_1_pos` | 0.699 |
| `Block_1_neg` | 0.695 |
| `scramble_B` | 0.596 |

**Uno scramble è coerente quanto una rotazione**, e più coerente di due su quattro. Il criterio
non separa niente, ed è ovvio a posteriori: uno scramble è una perturbazione *fissa*, applicata
identica a ogni render. Qualunque modifica fissa dei pesi è sistematica. La coerenza misura se
l'operazione è ripetibile, non se significa qualcosa.

## 2. Esiste un asse comune, ed è quasi tutto

Prima componente principale di tutti i 180 spostamenti: **spiega il 78.3% dell'energia
complessiva**. La sua feature dominante è `fft_high_freq_share` a **+0.73**, seguita da
`glcm_energy` +0.40.

È la stessa cosa misurata separatamente la notte prima: a dose alta ogni modifica dei pesi
amplifica di 3.3–4.8× il residuo ad alta frequenza nelle zone piatte. **La grana.**

> **Il grosso di ciò che fa qualunque modifica di peso — strutturata o casuale — è iniettare
> alta frequenza.** L'intuizione dell'utente è corretta in proporzione: circa quattro quinti.

## 3. Ma la quota varia moltissimo, e in modo controintuitivo

| condizione | \|D\| immagine | quota lungo l'asse comune | residuo specifico |
|---|--:|--:|--:|
| `Block_6_pos` | **42.20** | **99.6%** | 3.61 |
| `scramble_A` | 12.61 | 72.1% | 8.74 |
| `Block_6_neg` | 14.58 | 52.1% | 12.44 |
| `Block_1_pos` | 6.28 | 27.3% | 6.04 |
| **`scramble_B`** | 4.44 | 24.7% | 4.30 |
| **`Block_1_neg`** | 6.31 | **14.3%** | 6.24 |

`Block_6_pos` ha lo spostamento d'immagine più grande di tutti — sette volte uno scramble a
parità di costo sui pesi — ed è **quasi interamente grana**: il 99.6% giace sull'asse comune.
Grande e generico.

`Block_1` è l'opposto: spostamento piccolo, ma per l'86% **fuori** dall'asse del danno.

Chi guardasse solo la dimensione dell'effetto concluderebbe che `Block_6` è la manopola potente.
Chi guarda cosa fa, trova che `Block_6_pos` è soprattutto un generatore di grana ben educato.

## 4. Il vero discriminatore: il residuo si inverte col segno?

Tolto l'asse comune, resta la parte specifica. Se quella parte è uno *sterzo*, deve invertirsi
cambiando segno alla modifica. Coseni fra i residui:

| coppia | coseno del residuo | lettura |
|---|--:|---|
| `Block_6_pos` ↔ `Block_6_neg` | **−0.70** | si inverte → **sterzo vero** |
| `Block_1_pos` ↔ `Block_1_neg` | **+0.65** | non si inverte → **deriva** |
| `Block_1_neg` ↔ `scramble_B` | **+0.92** | quasi la stessa direzione |
| `Block_1_pos` ↔ `scramble_B` | +0.54 | |
| `Block_6_pos` ↔ `scramble_A` | −0.39 | direzioni distinte |

**Risposta alla domanda, in due parti.**

*Sì, in gran parte è scrambling*: il 78% di ogni spostamento sta su un unico asse di grana
condiviso da modifiche strutturate e casuali indifferentemente.

*No, non del tutto, e si può dire dove*: la rotazione di `Block_6` conserva un residuo che
**si inverte col segno** (−0.70), cosa che nessuno scramble può fare per costruzione. Quello è
sterzo, ed è l'unica cosa in questo esperimento che uno scramble non riproduce.

*E almeno un caso è indistinguibile*: il residuo di `Block_1_neg` giace a coseno **+0.92** da
quello di `scramble_B`, e non si inverte col segno. Su questa misura, la rotazione di `Block_1`
non si distingue da uno scramble a norma appaiata.

## 5. Guadagno e rotazione non sono la stessa operazione

Il confronto con le misure sui **guadagni** (`docs/mappa_completa_sterzo_e_deriva.md`) mostra
un'inversione dei ruoli:

| | guadagno scalare | rotazione |
|---|---|---|
| `Block_1` | **sterza** il tono (frazione di sterzo 0.72–0.93) | **deriva** (residuo +0.65) |
| `Block_6` | in gran parte deriva (0.36–0.43 sulla saturazione) | **sterza** (residuo −0.70) |

Sullo stesso blocco le due operazioni si comportano in modo opposto. Non sono due dosaggi della
stessa cosa: sono due cose diverse, e vanno tenute separate in ogni enunciato.

**Avvertenza**: i due esperimenti usano corpus diversi (10 stili qui, 2 sonde là) e dosi diverse.
L'inversione è un'osservazione da confermare su materiale appaiato, non un risultato.

## 6. Le altre due strade dell'utente

**Le dimensioni (SVD).** «Non sono slider, cambiandone una di 1 si rompe il flusso.» È atteso: i
valori singolari sono una *base*, non una manopola. Scalare una direzione singolare cambia la
struttura del rango in modo discontinuo, mentre un guadagno scalare percorre un cammino liscio.
L'osservazione collegata — un LoRA rende il 70% con le sue 5 dimensioni più comuni — è la
concentrazione spettrale nota in letteratura, ed è il motivo per cui il motore geometrico lavora
già con rotazioni troncate a rango 8/16/32 invece che sulla base piena.

**I canali.** La base per dimostrarlo esiste, ed è **lo stesso metodo di questo documento**:
raggruppare per canale di uscita invece che per blocco, misurare per ciascun gruppo la quota
lungo l'asse comune e se il residuo si inverte col segno. Se un raggruppamento per canale produce
residui che si invertono, i canali sono manopole; se produce solo asse comune, sono un altro modo
di iniettare grana. È l'esperimento del §4 con un asse di raggruppamento diverso, e non richiede
strumenti nuovi.
