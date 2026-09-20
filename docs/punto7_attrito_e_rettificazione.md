# Il braccio negativo: spingere costa dettaglio, e la coda è rettificata

**Data**: 2026-09-20 · **Materiale**: 168 render (`benchmark_profondita_neg`), 28 blocchi singoli
× 2 prompt × 3 seed, dose **−0.200**, appaiati ai 168 a **+0.200** già in `benchmark_profondita`.
Più 32 baseline nuovi (`benchmark_pavimento_rumore`) che portano il pavimento di rumore a **18
semi per prompt**. Modalità `Real Value`, 9 passi, CFG 1.0, `euler_ancestral`.
**Pre-registrazione**: [`prereg_punto7_simmetria_segno.md`](prereg_punto7_simmetria_segno.md),
depositata con la cartella di destinazione vuota (0 file verificati). Otto previsioni numeriche:
**5 confermate, 2 falsificate, 1 in zona grigia.**

---

## 0. In una frase

Fino a oggi ogni blocco era stato spinto in una direzione sola. Spingendoli anche nell'altra
emergono due cose che il braccio positivo non poteva mostrare: **una perturbazione qualunque, in
qualunque verso, toglie dettaglio fine** — e il prezzo non è distribuito, si concentra negli
ultimi cinque blocchi; e **la coda del modello è rettificata**, cioè reagisce molto al più e
quasi niente al meno.

La seconda è direttamente utile a chi usa il tuner. La prima riguarda cosa sia, davvero, uno
strumento di steering nello spazio dei pesi.

---

## 1. Il prezzo dell'attrito

Per ogni blocco misuro l'energia ad alta frequenza dell'immagine rispetto al baseline dello stesso
seme, una volta spingendo a `+0.200` (chiamiamolo $r^+$) e una volta a `−0.200` ($r^-$). Da questi
due numeri se ne ricavano altri due, che dicono cose diverse:

$$c = \sqrt{r^+ r^-} \qquad\text{(modo comune: cosa succede a prescindere dal verso)}$$
$$s = r^+ / r^- \qquad\text{(swing: quanto il verso conta)}$$

Lo *swing* è la misura che il progetto usava già. Il *modo comune* è nuovo, e lo swing **non può
vederlo**: se un blocco fa la stessa cosa in entrambi i versi, il rapporto vale 1 e il blocco
sembra inerte.

**Risultato**: il modo comune medio vale **0.978**, cioè ogni perturbazione toglie in media il
**2.2%** di texture fine, e lo fa in **23 blocchi su 28**.

Tre controlli, perché una media non basta:

* **I due bracci separatamente.** Il modo comune è un prodotto di due misure, e i prodotti sono
  sospetti ([pitfall 63](errors_log.md)). Scomposto: il braccio positivo vale in media $0.970$, il
  negativo $0.985$. **Sono negativi entrambi**, quindi non è un artefatto dell'accoppiamento.
  Presi singolarmente non raggiungono la significatività (test dei segni $p = 0.17$ e $p = 0.09$);
  è la loro media a raggiungerla, perché mediare due misure ne dimezza il rumore.
* **Il nullo, generato dai dati.** Ho calcolato la stessa quantità fra **coppie di baseline**, dove
  per costruzione non c'è nessun trattamento: 612 coppie, media $-0.00000$, deviazione $0.0246$.
  Sulla media di 28 blocchi il nullo ha deviazione $0.0019$; il valore osservato è $-0.0226$.
  **Circa dodici deviazioni standard.**
* **Il test dei segni** su 23/28: $p = 4.6 \times 10^{-4}$.

Non è una manopola. Ma **non è nemmeno degrado dei pesi**, ed è la scoperta che questa misura
da sola non poteva dare.

### Dove nasce davvero il costo

Rifacendo la stessa misura sui sei macro-blocchi **prima** della VAE, dove esistono i latenti:

| | modo comune nel **latente** | nei **pixel** | scarto |
|---|---|---|---|
| media sui 6 gruppi | **1.021** | **0.955** | −0.067 |
| gruppi sopra 1 | 4 / 6 | 1 / 6 | negativo in **6/6** |

**Nel latente la perturbazione *aggiunge* alta frequenza; è il decodificatore a non consegnarla.**
E il gradiente con la profondità del §2 sparisce nel latente ($r \approx -0.05$) mentre nei pixel
vale $-0.74$: anche la crescita del costo con la profondità è un fatto della VAE.

È lo stesso meccanismo di [pitfall 62](errors_log.md) su scala nuova: il decodificatore lascia
passare la perdita di dettaglio e assorbe l'aggiunta. Quello che una perturbazione inietta nel
latente è **rumore ad alta frequenza**, e una VAE addestrata su immagini naturali non lo rende
come dettaglio.

La formulazione corretta è quindi: *spingere un blocco non consuma dettaglio, inietta rumore che
il decodificatore si rifiuta di consegnare.* Per il caso d'uso di questo taccuino — controllo
sull'immagine, non spiegazione del modello — la conseguenza pratica non cambia: **il dettaglio
perso è perso**. Cambia l'attribuzione del meccanismo, e cambia dove cercare un rimedio.

### E il costo dipende dalla dose

Sul banco appaiato in norma a $D = 0.050$ (tre prompt, scaling e rotazioni), il modo comune vale
**1.004** per lo scaling e **0.997** per le rotazioni: **a quella dose non costa niente**. Il
costo osservato qui vive a dosi più alte. Non è una tassa fissa: è una soglia, e dove cada non è
ancora misurato.

> Lo stesso fenomeno si vede da un'altra angolazione in [`stage1_gate`](#) (banco appaiato in
> norma di Frobenius, tre prompt): a spostamento identico dei pesi, una perturbazione **casuale**
> muove l'immagine **1.68×** più di uno scaling strutturato (1.36× / 1.91× / 2.06× sui tre
> prompt). L'edit coerente è in buona parte assorbito dalle normalizzazioni a valle; il rumore non
> ha nulla da farsi cancellare. Le due misure dicono la stessa cosa: l'energia si converte in
> degrado prima che in controllo.

## 2. Il prezzo è un gradino al blocco 23, non una salita

La pre-registrazione prevedeva che il costo crescesse con la profondità, con correlazione
$< -0.30$. **Osservata: $r = -0.659$**, permutazione $p = 6\times10^{-5}$. Previsione confermata.

Ma la lettura «cresce con la profondità» sarebbe sbagliata, ed è precisamente l'errore che
[`monotonia_profondita_esito.md`](monotonia_profondita_esito.md) ha già documentato su un'altra
grandezza. Applicando lo stesso test:

| test | risultato |
|---|---|
| correlazione su tutti e 28 | $r = -0.659$ |
| **solo blocchi 0–19** | **$r = -0.221$** — nessuna discesa |
| solo blocchi 20–27 | $r = -0.937$ |
| passi consecutivi in discesa | **13 su 27** (per caso 13.5) |
| retta contro gradino, somma dei quadrati residui | retta 0.01173 · **gradino 0.00680** |
| **punto di rottura migliore** | **blocco 23** |

Il modello a gradino descrive i dati **1.7 volte meglio** di una retta. Media del costo prima del
blocco 23: $0.988$; dopo: $0.932$. **Gli ultimi cinque blocchi costano quasi sei volte tanto.**

E il punto di rottura è **lo stesso blocco 23** trovato indipendentemente dalla coerenza di
traiettoria sul braccio positivo. Due grandezze diverse, due bracci diversi, lo stesso confine.
Non è «essere profondi»: è «essere quei blocchi» — la stessa conclusione, per una via nuova.

## 3. La coda è rettificata: al più stravolge, al meno quasi non si muove

Questa è la previsione che è **caduta**, ed è la caduta più utile della giornata.

Prevedevo che gli estremi fossero violenti in entrambi i versi. Misurando l'ampiezza dello
spostamento estetico (luminanza, contrasto, croma, dettaglio, ciascuno in unità della propria
variabilità fra semi):

| blocco | ampiezza a **+0.200** | ampiezza a **−0.200** | rapporto |
|---|---|---|---|
| blk26 | 13.66 | **1.50** | **9.1×** |
| blk24 | 5.91 | 1.41 | 4.2× |
| blk25 | 10.85 | 3.06 | 3.5× |
| blk23 | 11.06 | 3.95 | 2.8× |
| blk18 | 8.52 | 3.51 | 2.4× |
| blk00 | 11.44 | 7.88 | 1.5× |
| **blk27** | 10.31 | **14.75** | **0.7×** |

`blk26` spinto in positivo stravolge l'immagine; spinto in negativo, alla stessa dose, quasi non
la tocca. Un fattore **nove**.

**Conseguenza pratica**: sulla coda del modello, il **verso negativo è il lato sicuro**. Costa
comunque texture fine — quello lo fa ovunque, §1 — ma non stravolge la composizione. Chi vuole
correggere senza perdere l'immagine, sulla coda, deve andare al meno.

L'unica eccezione è **`blk27`**, l'ultimo blocco, che inverte il pattern in ogni sua parte: è più
violento in negativo, ed è l'unico della coda che *alza* l'alta frequenza in positivo (swing
**1.393**, il massimo dei 28, contro 0.97 / 0.87 / 0.80 dei suoi tre vicini). Merita un
esperimento suo.

## 4. Il primo blocco è una manopola al contrario — confermato

Previsione depositata: `blk00` avrebbe $r^- > 1.00$ e swing $< 0.85$.
**Misurato**: $r^+ = 0.841$ (leviga), $r^- = 1.100$ (incide), swing $= 0.764$.

Spinto in positivo il primo blocco **toglie** dettaglio; spinto in negativo lo **aggiunge** — il
verso opposto alla coda. Insieme alla separabilità pre-registrata Block_1 / Block_6 del 19/09, è
la seconda ipotesi congelata prima dei dati che regge sull'asimmetria fra i due estremi, e la
prima misurata su una statistica invece che su una distanza.

## 5. La bidirezionalità è la regola, e cade dove c'è segnale

Previsione: la specularità (cioè $r^- = 1/r^+$, verso invertito ed effetto invertito) sarebbe
stata rara. **Falsificata**: **17 blocchi su 28** sono compatibili con una risposta perfettamente
speculare entro il rumore misurato ($3\sigma$ su $\log r^+ r^-$ vale $0.030$).

Gli **11 che la violano** non sono però sparsi a caso: `blk00`, `blk03`, `blk13`, `blk18`,
`blk19`, `blk22` e tutta la coda da `blk23` a `blk27`. **La specularità regge dove non succede
molto e cade dove succede qualcosa.**

## 6. Cosa NON è nuovo, e va detto

Il braccio positivo di `Block_6` alza l'alta frequenza del **40%** nel latente e **non la alza
affatto** nei pixel. Questo era **già** documentato in
[`block6_nel_latente.md`](block6_nel_latente.md) e in [pitfall 62](errors_log.md): il
decodificatore lascia passare la perdita e assorbe l'aggiunta. La riverifica di oggi lo conferma
e nient'altro.

Ne segue un limite dichiarato del Punto 7: **tutto quello che c'è in questo documento è misurato
nei pixel**, cioè nella banda che la VAE lascia passare — e il §1 mostra quanto quella distinzione
pesi anche sul risultato principale. La previsione P6 — nessun blocco singolo
avrebbe superato swing 1.5 in pixel, mentre nel latente `B6` arriva a 2.00 — è stata confermata
(massimo 1.393). Non è una smentita del risultato latente: è un'altra banda.

## 7. Il pavimento di rumore, finalmente misurato

Tutte le soglie precedenti poggiavano su una deviazione stimata da **tre** semi. Trenta render in
più portano il conto a **18 semi per prompt**, 153 coppie ciascuno:

| | σ dell'alta frequenza (pixel) | σ (latente) | correlazione fra due baseline |
|---|---|---|---|
| P01 | **1.65%** | 1.24% | 0.500 ± 0.044 |
| P02 | **1.83%** | 1.94% | 0.503 ± 0.031 |

La stima su tre semi (1.15%) era bassa di circa una volta e mezza. Nel corso della giornata avevo
anche importato il σ di prompt diversi (3.3–5.2%), concludendo erroneamente che metà dei risultati
fosse fragile: **quei prompt hanno davvero più variabilità fra semi, questi no**. Con il valore
misurato, tutti i risultati reggono.

Il numero `0.50` nell'ultima colonna è il **tetto di decorrelazione**: due immagini dello stesso
prompt con semi diversi correlano a 0.50. Un edit che porta la correlazione col baseline a quel
livello ha prodotto, in sostanza, un'altra immagine. Serve come riferimento e **dipende dal
prompt** — sui prompt di `stage1_gate` va da 0.29 a 0.58, quindi non è una costante del modello.

## 8. Limiti

* Due prompt, tre semi per cella, una dose per verso. La generalità resta quella di sempre.
* Banda fine soltanto (§6). Per la scala media servirebbero i latenti su entrambi i bracci a
  blocco singolo: 336 render, oggi non prioritari.
* **P5 resta indecisa**: 9 blocchi superano soglia di swing contro i ≤ 8 previsti, con
  falsificazione posta a ≥ 12. Da rifare con una soglia ricavata dal σ misurato invece che scelta
  a mano.
* **Quattro slot del tuner non consegnano quello che dichiarano** — `MOD` e `NORMS` producono
  latenti *bit per bit* identici al baseline a ogni dose provata, 0.500 compresa, benché
  `blocks.N.mod.lin`, `prenorm.scale` e `postnorm.scale` esistano tutti nel checkpoint. Va
  diagnosticato leggendo il conteggio `Patches: N` che il nodo restituisce. Non intacca i
  risultati qui, che non usano quegli slot.

---

### Nota di metodo, a spese dell'autore

Il cancello di accettazione dei 32 baseline nuovi era «hash SHA-256 del file identico»: è fallito
su file dai pixel identici, perché ComfyUI scrive i parametri di invocazione nei chunk `tEXt` e lo
script nuovo ne scrive di diversi. È **esattamente [pitfall 60](errors_log.md)**, già in questo
repository, ricommesso dall'autore della checklist. Il criterio va scritto sul contenuto
decodificato, mai sul contenitore. La checklist funziona solo se la si rilegge.
