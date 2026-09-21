# BRIEF — Ri-analisi delle rotazioni dei benchmark pilota

**Per**: Antigravity
**Data**: 2026-09-18
**Stato**: lavoro di recupero su dati già esistenti. **Nessun render nuovo.**
**Input**: i nove `comfyui-pilot/benchmark_*_report.html` (escluso `benchmark_dryrun_v3_report.html`,
che non contiene rotazioni) più il checkpoint `krea2_turbo_bf16` e il codice del tuner che ha
prodotto le rotazioni.

---

## 0. Perché questo lavoro esiste

Dentro quei report, da prima che il progetto avesse una pre-registrazione, c'è uno sweep che il
notebook non ha mai analizzato: **le rotazioni per blocco**. È l'unico posto in tutto il materiale
dove la modifica ha una *posizione* e non solo una direzione e un'ampiezza.

Il conteggio esatto, verificato sui file:

| famiglia | celle | struttura |
| --- | --- | --- |
| `Block_N_rotX_±15°/±30°` | **216** | 6 blocchi × 4 angoli × 9 report |
| `Block_3` altre rotazioni (`structural_rot_y`, `tensor_rot_x`, `tensor_rot_y`, ±20°) | 54 | 6 condizioni × 9 report |
| sweep di ampiezza `Block_N_±1.0/±2.0` (tab "Macro") | 216 | 6 blocchi × 4 ampiezze × 9 report |
| baseline | 9 | uno per report |

E questa è la cosa che ha fatto scrivere il brief. Media della `CLIP-Dist` sui 9 report:

| blocco | −30° | −15° | +15° | +30° | media \|angolo\| |
| --- | --- | --- | --- | --- | --- |
| **Block_1** | 0.5771 | 0.1458 | 0.1967 | 0.4089 | **0.3321** |
| Block_2 | 0.1680 | 0.1189 | 0.0952 | 0.1645 | 0.1367 |
| Block_3 | 0.1468 | 0.1084 | 0.1022 | 0.1440 | 0.1254 |
| Block_4 | 0.1268 | 0.1076 | 0.1002 | 0.1528 | 0.1219 |
| Block_5 | 0.1464 | 0.0837 | 0.0721 | 0.1260 | 0.1070 |
| **Block_6** | 0.6016 | 0.4191 | 0.2683 | 0.5564 | **0.4614** |

I due blocchi **estremi** rispondono 3–4 volte più dei quattro centrali, allo stesso angolo. Se è
vero, è la prima indicazione in questo progetto che lo spostamento ha una topografia. Se è falso, va
scritto perché, perché la stessa tentazione tornerà.

---

## 1. Le tre ragioni per cui quella tabella, così com'è, non dimostra niente

Vanno lette prima di toccare i dati, perché decidono che cosa va misurato.

**(a) L'angolo non è lo spostamento.** L'intestazione del tab dice che le rotazioni preservano
$\|W\|_F$, ed è vero — ma la quantità che conta in tutto il resto del notebook è lo **spostamento
relativo** $D = \|W' - W\|_F / \|W\|_F$, e quello *non* è preservato e *non* è uguale fra blocchi allo
stesso angolo. Dipende da quanta massa spettrale del blocco cade nel piano che viene ruotato. Se
`Block_1` e `Block_6` hanno più massa in quel piano, ruotarli di 30° li sposta di più, e la tabella
sopra sta misurando l'ampiezza travestita da posizione. **Questa è l'ipotesi nulla di default e va
esclusa per prima.**

**(b) La metrica è quella che il notebook ha già dichiarato cieca.** `CLIP-Dist` su OpenCLIP ViT-B-32
a 224×224 è esattamente lo strumento che §4 del notebook mostra invertire le conclusioni sulle
proprietà di tratto e palette. Un blocco può cambiare molto la figura e poco il CLIP, o viceversa.

**(c) Non esiste un controllo a spostamento appaiato.** Nessuna delle 216 celle ha accanto una
perturbazione casuale allo stesso $D$. Senza quella, "il Block_6 risponde" non ha un termine di
paragone: è la regola 1 dell'`errors_log` non soddisfatta.

E due dettagli che cambiano i conti:

- **I nove report non sono nove prompt.** Sono **sette** prompt distinti: `tiefling` compare tre
  volte, agli stessi parametri, con seed 4242145 / 1337 / 42. L'unità di analisi è il prompt
  (pitfall 17), quindi i tre tiefling si mediano *prima*, e $n = 7$. Il pavimento del test di
  permutazione esatta diventa $2/2^7 = 0.0156$, che è un pavimento vero ma raggiungibile.
- **Un solo seed per cella** (tranne tiefling). Non c'è modo di stimare il rumore di seed da questi
  dati, se non su quell'unico prompt.
- **Il campionamento è diverso da tutto il resto del progetto**: 6 passi, non 9. Con
  `euler_ancestral` il numero di passi cambia il rumore iniettato a ogni passo, quindi queste
  immagini non sono confrontabili con quelle degli stage 4–12 nemmeno a parità di seed. Qualunque
  conclusione resta **interna a questo sweep**.
- **Le caselle di valutazione sono vuote.** 4505 checkbox nei nove file, **zero** spuntate salvate
  nell'HTML. Non esiste alcun punteggio umano su queste immagini.

---

## 2. Il lavoro, in ordine

### Lavoro A — estrarre, senza interpretare

`experiments/extract_pilot_benchmarks.py`, che legge i nove HTML e scrive
`data/pilot_rotations.csv` e `data/pilot_macro.csv` con una riga per cella:

```
report, prompt_id, seed, steps, cfg, family, block, rot_kind, angle_deg,
amplitude, image_rel, clip_dist, cosine_sim
```

Regole: `prompt_id` deriva dal nome del report **senza** il suffisso di seed, così i tre tiefling
condividono lo stesso `prompt_id`; ogni valore numerico è letto dall'HTML, mai ricalcolato a mano; lo
script **solleva** se il numero di celle estratte non è 216 / 54 / 216 / 9, perché un parser che perde
righe in silenzio è pitfall 21 un'altra volta.

### Lavoro B — misurare lo spostamento vero *(questo è il lavoro che decide tutto)*

Per ogni combinazione (blocco, `rot_kind`, angolo) usata nello sweep, ricostruire la stessa
trasformazione che il tuner applicava e calcolare, **offline, senza generare immagini**:

- $D_{\text{blocco}} = \|W' - W\|_F / \|W\|_F$ ristretto ai tensori di quel blocco;
- $D_{\text{modello}}$, lo stesso rapporto sull'intero DiT, che è la scala confrontabile con il
  $D = 0.05381584$ usato negli Esperimenti 1 e 2;
- il numero di tensori effettivamente toccati, e un'asserzione che quel numero sia lo stesso per
  tutti e sei i blocchi. Se non lo è, metà della tabella del §0 è spiegata da lì e il resto del brief
  decade.

Output: `data/pilot_rotation_displacement.csv`.

Se il codice del tuner non è più ricostruibile con certezza, **fermarsi qui e dirlo**. Una $D$
stimata a occhio è peggio di nessuna $D$: renderebbe pubblicabile un grafico che non si può difendere.

### Lavoro C — la domanda vera

Con $D$ in mano, l'analisi è una sola domanda: **la differenza fra blocchi sopravvive quando si mette
$D$ sull'asse x invece del blocco?**

1. Regressione di `clip_dist` su $D$ su tutte le 216 celle, aggregate prima per prompt ($n = 7$).
2. Residui della regressione, mediati per blocco. Se il profilo `1 e 6 alti, 2–5 bassi` sopravvive nei
   residui, c'è un effetto di posizione. Se scompare, la tabella del §0 era ampiezza.
3. Test di permutazione esatta sull'etichetta blocco-estremo / blocco-centrale, sui residui, con i
   prompt come unità. Riportare il pavimento $2/2^7 = 0.0156$ accanto al $p$, sempre, anche se il $p$
   lo supera.

### Lavoro D — il segno, che qui è gratis

Ci sono sia $+15/+30$ sia $-15/-30$, quindi la decomposizione simmetrica/antisimmetrica
dell'Esperimento 1 si applica direttamente: $S = (d^+ + d^-)/2$, $A = (d^+ - d^-)/2$.
I valori grezzi di $A$ per blocco, dai file, sono:

| | Block_1 | Block_2 | Block_3 | Block_4 | Block_5 | Block_6 |
| --- | --- | --- | --- | --- | --- | --- |
| $A$ (medio, +) − (medio, −) | −0.0587 | −0.0136 | −0.0045 | +0.0092 | −0.0160 | −0.0980 |

Cinque segni su sei negativi: ruotare in un verso sposta di più che ruotare nell'altro. Va testato
allo stesso modo (permutazione sui 7 prompt) e va riportato **anche se non passa**, perché
un'antisimmetria su una rotazione ortogonale non è banale: dice che il piano ruotato non è simmetrico
attorno alla posizione originale.

### Lavoro E — il verdetto, incluso "niente"

`docs/pilot_rotations_verdict.md`, con quattro esiti possibili scritti **prima** di guardare i
residui:

1. **Effetto di posizione.** Il profilo sopravvive alla correzione per $D$. Allora vale una
   pre-registrazione a parte e un round nuovo, a $D$ appaiato per costruzione, con le metriche di
   tratto e palette invece della CLIP-Dist.
2. **Artefatto di ampiezza.** Il profilo scompare. Si scrive così, si chiude la questione, e diventa
   pitfall 41: *un parametro che sembra una posizione e si comporta come un'ampiezza*.
3. **Indeterminato per metrica.** L'effetto c'è ma vive solo nella CLIP-Dist. Allora la domanda non è
   sui blocchi, è sulla metrica, e la risposta richiede di ri-misurare quelle immagini con
   `style_features.py` e `analyze_palette.py` — che è fattibile, perché i PNG esistono ancora.
4. **Non ricostruibile.** Il Lavoro B fallisce. Si scrive che cosa manca e che cosa servirebbe.

Nessuno di questi quattro è un fallimento del lavoro.

---

## 3. Cancelli di accettazione

Il lavoro non è finito finché:

- [ ] `pilot_rotations.csv` ha **esattamente 216** righe `rotX` e 54 righe delle altre rotazioni, e
      lo script fallisce rumorosamente se non è così;
- [ ] `prompt_id` ha **7** valori distinti e i tre tiefling condividono il loro;
- [ ] ogni `clip_dist` nel CSV è rintracciabile alla stringa nell'HTML da cui viene;
- [ ] `pilot_rotation_displacement.csv` esiste **o** il verdetto dichiara l'esito 4;
- [ ] ogni $p$ pubblicato è accompagnato dal pavimento $2/2^7 = 0.0156$;
- [ ] il verdetto dice a voce alta le tre limitazioni del §1 e le due del §1 in coda (6 passi invece
      di 9, nessun punteggio umano), anche nell'esito 1;
- [ ] **nessuna** di queste conclusioni entra nel README o in `index.html` come risultato
      dell'Esperimento 1 o 2: questo sweep precede la pre-registrazione, usa un campionamento diverso
      e non ha controlli appaiati. Va in una sezione sua, dichiarata esplorativa.

---

## 4. Quello che questo brief **non** chiede

- Non chiede di rigenerare immagini. Se i PNG in
  `benchmark_*/rotations/` non ci sono più, i Lavori A–D restano possibili perché i numeri sono
  dentro l'HTML; solo l'esito 3 diventa irrealizzabile.
- Non chiede di spuntare le 4505 checkbox. Uno scoring umano su queste immagini avrebbe oggi lo
  stesso problema misurato in §7.2 del notebook — e senza un test di discriminazione accanto, non
  sarebbe cieco. Se si vuole un punteggio umano su queste immagini, è un brief separato e comincia
  dal test di discriminazione.
- Non chiede di difendere la tabella del §0. Se cade, cade.
