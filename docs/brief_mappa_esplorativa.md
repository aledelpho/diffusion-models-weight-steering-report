# BRIEF — Mappa esplorativa dei blocchi su Krea-2: cosa fa ogni area, e su cosa

**Esecutore**: Antigravity, pilotando ComfyUI.
**Natura**: **esplorativo e descrittivo.** Non c'è ipotesi da confermare, non c'è test
statistico, non c'è pre-registrazione da rispettare. Lo scopo è produrre un quadro visivo di
cosa fa ciascuna area del modello, per poter poi formulare previsioni che oggi non sarebbero
formulabili.

**Non contamina lo stage 2**: quei test sono meccanici e le loro feature sono congelate in
`docs/prereg_stage2_corpus_nativo.md`. Guardare queste immagini non cambia quell'analisi.
**Contamina invece il futuro round di previsioni calibrate**, che è a giudizio umano: i
prompt usati qui non potranno essere usati lì. Servirà un gruppo separato, sigillato.

---

## PARTE 0 — La patch, tre righe, già verificata

Serve solo per la Parte 2 (Anima). La Parte 1 (Krea-2) gira senza toccare nulla.

### Il problema, misurato

`ArthemyKrea2ModelTuner.GROUP_MAP` assegna i tensori ai nove slot con la regola
`clean_key.startswith(prefisso) or ".prefisso" in clean_key`. Su Anima esistono chiavi
`llm_adapter.blocks.0.` … `llm_adapter.blocks.5.`, che sono i sei blocchi **dell'adattatore
testuale**, non del backbone. La stringa `.blocks.0.` compare dentro
`llm_adapter.blocks.0.cross_attn.k_proj.weight`, quindi quella chiave viene catturata da
`Block_1`.

Simulazione sulle 685 chiavi reali di `anima_baseV10.safetensors`:

| gruppo | oggi | atteso |
|---|---:|---:|
| Block_1 | **195** | 100 |
| Block_2 | **119** | 100 |
| Text_Fusion | **0** | 118 |
| Time_Embed | **0** | 3 |
| Projection | **0** | 4 |
| nessun gruppo | **11** | 0 |

**114 chiavi dell'adattatore testuale finiscono nei blocchi del backbone.** Nessuna eccezione
viene sollevata: la mappa girerebbe, le immagini uscirebbero, e i valori di Block_1 e Block_2
misurerebbero in parte il percorso del testo. È il pitfall 47, vivo.

### La correzione

File: `custom_nodes/Arthemy_Krea2_Tuner/Arthemy_Krea2_Tuner.py`
Classe: `ArthemyKrea2ModelTuner`, dizionario `GROUP_MAP` (intorno a riga 2041).

**Tre righe, solo aggiunte in coda alle liste esistenti. Non toccare le righe `Block_*`.**

PRIMA:
```python
    GROUP_MAP = {
        "Text_Fusion": ["txtfusion.", "txtmlp."],
        "Time_Embed": ["tmlp.", "tproj."],
        "Projection": ["first.", "last."],
```

DOPO:
```python
    GROUP_MAP = {
        "Text_Fusion": ["txtfusion.", "txtmlp.", "llm_adapter."],
        "Time_Embed": ["tmlp.", "tproj.", "t_embedder.", "t_embedding_norm"],
        "Projection": ["first.", "last.", "x_embedder.", "final_layer."],
```

**Perché è sicura.** `Text_Fusion` è la prima voce del dizionario e il ciclo di
assegnazione esce al primo riscontro, quindi `llm_adapter.` cattura quelle chiavi prima che
`Block_1` possa vederle. Verificato per non regressione sulle 430 chiavi di
`krea2_turbo_bf16.safetensors`: **assegnazioni identiche prima e dopo, zero differenze.**
Krea-2 non ha nessuna chiave contenente `llm_adapter`, `t_embedder`, `x_embedder` o
`final_layer`.

Dopo la modifica, su Anima i nove slot ricevono: Text_Fusion 118, Time_Embed 3, Projection 4,
Block_1…4 cento ciascuno, Block_5 e Block_6 ottanta ciascuno. Totale 685, zero non assegnate.

### Accettazione della patch

1. ComfyUI riavviato senza errori in console.
2. Su **Krea-2**, un render con tutti gli slot a 0 deve essere **identico byte per byte** a un
   render baseline con lo stesso seed. Se differisce, la patch ha rotto qualcosa: si annulla.
3. Nessun'altra modifica al file. Se serve altro, fermarsi e segnalare invece di improvvisare.

---

## PARTE 1 — Mappa su Krea-2 (nessuna patch, si può fare subito)

### Modalità e dose: il punto dove è facilissimo sbagliare

Il nodo ha due modalità, e cambiano il significato del numero che si digita:

| modalità | formula | per ottenere guadagno +0.05 si digita |
|---|---|---|
| `Real Value` | $1.0 + \delta$ | **0.05** |
| `Soft Value` | $1.0 + \delta \times 0.10$ | **0.5** |

**Usare `Real Value`** e digitare il guadagno direttamente.

> **Cancello di sanità**: se le immagini con uno slot a 0.05 sono indistinguibili dal
> baseline, quasi certamente la modalità è `Soft Value` e il guadagno reale è 0.005, dieci
> volte troppo piccolo. Controllare la modalità **prima** di concludere che un blocco non
> fa niente.

**Dose della mappa: ±0.05 su ogni slot, uguale per tutti.**

Guadagno uguale, **non** effetto uguale. Equalizzare l'effetto distruggerebbe l'informazione
più interessante: su Krea-2 `Block_6` muove l'immagine 3.7 volte più di `Block_2` a parità di
spostamento, e quello è un risultato, non un fastidio da normalizzare. Con guadagno uguale
si ottengono due mappe in una sola sweep: **dove spinge ogni blocco** e **quanto è sensibile**.

### Condizioni: una rampa di dose per blocco

Non due punti, ma una **rampa**: lo stesso slot a dosi crescenti, tutti gli altri a `0`.
Una rampa dice cose che due punti non possono dire — se l'effetto cresce liscio o a scatti,
dove satura, e a che dose si rompe. Su Krea-2 §4.3 `Block_1` era normale a 15° e ×3.14 a 30°:
una rottura non lineare che un disegno a due punti non avrebbe mai visto.

**Sei slot di blocco, rampa completa** (`Block_1` … `Block_6`):

| dose | | | | | | |
|---|---|---|---|---|---|---|
| positive | 0.02 | 0.035 | 0.05 | 0.08 | 0.12 | 0.20 |
| negativa | −0.05 | | | | | |

Sette condizioni per slot. Le dosi sono in progressione quasi geometrica e racchiudono
l'intervallo dei guadagni reali del preset (0.019–0.055), così la mappa copre il regime in cui
il preset lavora davvero e due passi oltre. La dose negativa serve a controllare se la
direzione si inverte o se il blocco spinge nello stesso verso comunque.

**Tre slot non-blocco** (`Text_Fusion`, `Time_Embed`, `Projection`): solo **±0.05**, due
condizioni ciascuno. Non sono blocchi, non c'è una topografia da mappare, e servono solo come
riferimento.

Totale: $6 \times 7 + 3 \times 2 = 48$ condizioni, più il baseline = **49**.

`vectors_override` e `granular_json` restano **vuoti**. Nessuna rotazione, nessun chaos,
nessun 5D, nessuna patch sul CLIP. **Uno slot alla volta**: la mappa serve a isolare, e
l'interazione fra blocchi è una domanda successiva e separata.

### Prima la rampa pilota, poi il resto

Su **un solo prompt** (`A01`) e tre seed, eseguire la rampa dei soli `Block_1` e `Block_6` —
i due estremi, quelli dove su Krea-2 succedono le cose strane. Sono $2 \times 7 \times 3 = 42$
immagini.

Serve a trovare **la dose di rottura per blocco** prima di spendere il corpus intero. Se un
blocco collassa già a 0.08, inutile generare 0.12 e 0.20 per tutti gli altri: si accorcia la
rampa. Se nessuno collassa nemmeno a 0.20, si può allungarla.

La dose di rottura per blocco è essa stessa un risultato, non un parametro di servizio: è la
misura più diretta di quanto ciascuna area sia fragile.

### Prompt: due sonde multi-contenuto, non i ritratti

`data/prompts_probe_krea2.json`, verbatim. **`P01` (forge_bench)** e **`P02` (greenhouse)**.

Non sono ritratti su fondo bianco, ed è deliberato: un ritratto su bianco ha pochissima
varietà spaziale e la mappa mostrerebbe solo il soggetto. Queste due scene mettono in una sola
inquadratura molti tipi di materia — pelle, capelli, acciaio lucido, rame, legno, cuoio, lino,
corda, granito, fuoco con gradiente caldo, fumo nella prima; pelle, lana, cotone, vetro
trasparente, acqua, terracotta, ottone, foglie cerose, felci fini, terriccio, gradiente di
cielo, condensa nella seconda. Così la mappa può dire **su cosa** agisce un blocco, non solo
dove.

Registro nativo Krea-2 (0.114 e 0.091 verbi/parola, contro 0.105 del corpus storico): sono
coerenti con i 40 prompt del progetto e non con quello Anima.

**Non entrano in nessuna statistica.** Sono descrittivi, servono a guardare, e non vanno
riusati come corpus di test — sono due sole scene e non rappresentano niente.

> **Compromesso da conoscere.** Una scena affollata varia di più fra seed: il rumore di seed
> sale, la soglia del null sale con lui, e la mappa perde sensibilità. Per questo la
> composizione è specificata con insistenza nel testo — inquadratura, posizione del soggetto,
> disposizione degli elementi. Se il null risulta comunque alto, si aggiunge un quarto seed
> prima di concludere che un blocco non fa niente.

### Seed

**42**, **1337** e **777**. Tre, non due, e il motivo è preciso: l'analisi per pixel costruisce
il proprio null dalle differenze fra baseline a seed diversi. Con due seed c'è una sola coppia
per prompt e il null è instabile — lo script lo segnala esplicitamente. Con tre seed ci sono
tre coppie e la soglia regge.

Regime: quello nativo di Krea-2 — **9 passi, CFG 1.0, `euler_ancestral`, `simple`**.

### Le regioni si disegnano DOPO aver visto i baseline

La lettura per regioni è ciò che trasforma la mappa da "dove" a "su cosa". Serve un file
`regions.json` nella forma:

```json
{ "P01": { "acciaio": [0.55, 0.30, 0.75, 0.55],
           "fuoco":   [0.05, 0.15, 0.30, 0.60],
           "legno":   [0.20, 0.60, 0.85, 0.85],
           "pelle":   [0.40, 0.18, 0.60, 0.40],
           "fondo":   [0.75, 0.05, 1.00, 0.35] } }
```

Coordinate in **frazioni** dell'immagine, `[x0, y0, x1, y1]`, origine in alto a sinistra.

**I valori qui sopra sono un esempio di formato, non coordinate da usare.** Le regioni vanno
disegnate guardando i sei baseline reali (2 prompt × 3 seed) e verificando che ciascun
riquadro contenga lo stesso materiale in **tutti e tre** i seed. Un riquadro che su un seed
cade sull'acciaio e su un altro sul legno produce un numero che non significa niente.
Includere sempre una regione **`fondo`** come controllo: un blocco che agisce dappertutto la
accenderà quanto le altre, e quello è il segnale che non sta facendo niente di specifico.

### Matrice Parte 1

49 condizioni × 2 prompt × 3 seed = **294 immagini**.
Più la rampa pilota (42 immagini), da eseguire per prima.

Nomi file — **vincolante, lo script di analisi li legge**:

```
<prompt>_<slot><segno>_<dose>_<modello>_seed<seed>_00001_.png
<prompt>_baseline_<modello>_seed<seed>_00001_.png
```

La dose va scritta con **tre decimali**, sempre, e senza segno: il segno sta in `pos`/`neg`.

Esempi: `A01_Block_3pos_0.080_krea2_seed42_00001_.png`,
`A10_Block_6neg_0.050_krea2_seed1337_00001_.png`,
`A01_baseline_krea2_seed42_00001_.png`.

Cartella piatta: `output\benchmark_mappa\renders\`.

---

## PARTE 2 — La stessa mappa su Anima, più avanti

Non adesso. Richiede la patch `GROUP_MAP` (`BRIEF_patch_anima_groupmap.md`) e prompt sonda
scritti nel registro nativo di Anima, che sono da scrivere. Il protocollo è identico: stesse
49 condizioni, stessa rampa, tre seed, stessa analisi.

Il confronto fra le due mappe è più interessante di ciascuna delle due prese da sola — *i
blocchi fanno le stesse cose nelle due architetture?* — ed è la continuazione naturale di tutto
il programma cross-architettura. Ma viene dopo: prima si impara a leggere una mappa sul modello
dove il tuner funziona già.

## Cosa produrre alla fine

1. Le immagini nella cartella piatta, con i nomi esatti sopra.
2. `mappa_images.csv`: `prompt_id`, `prompt_sha1`, `slot`, `sign`, `dose`, `mode`, `model`,
   `seed`, `steps`, `cfg`, `image_path`.
3. **L'analisi per pixel**, con lo script già pronto:

```
python experiments\block_sweep_maps.py ^
    --renders <cartella renders> ^
    --out    <cartella analisi> ^
    --gif
```

Produce, per ogni slot e ogni dose: la mappa di differenza media contro il baseline, la
frazione di area che supera il rumore di seed, lo spostamento di composizione, una gif della
rampa, e `sweep_summary.csv` con tutto in forma tabellare.

**Due cose nello script vanno capite prima di leggere i risultati.**

*Il null.* `euler_ancestral` inietta rumore nuovo a ogni passo: una perturbazione minima dei
pesi può far riorganizzare un bordo intero, e quella differenza è reale nei pixel ma non dice
dove agisce il blocco. Lo script costruisce quindi il proprio null dalle differenze fra
baseline a seed diversi — quanto due render differiscono quando **nessun peso** è stato
toccato — e conta solo i pixel che lo superano. Su dati sintetici con un effetto confinato al
6.7% dell'area, lo script recupera **6.7%**; senza il null la stessa misura riportava 34%.

*Lo spostamento di composizione.* Una differenza per pixel vale solo se le due immagini sono
spazialmente confrontabili. Quando la dose cresce la composizione si muove — su Krea-2
l'ingrandimento del soggetto è misurato a $\rho = 1.22$ — e da lì in poi la mappa dice "il
soggetto si è spostato", non "questa regione è cambiata". Lo script lo stima con la
correlazione di fase e marca quelle dosi come **NON INTERPRETABILI**. Su un test con
traslazione nota di 6 e 14 pixel le ha misurate esattamente e le ha marcate: senza quel
segnale, un blocco che sposta soltanto l'inquadratura verrebbe letto come un blocco che
agisce ovunque.

4. **La tabella che serve davvero**, ricavata da `sweep_summary.csv`: per ogni blocco, la dose
   alla quale l'effetto emerge dal rumore, la dose alla quale la composizione comincia a
   muoversi, la dose alla quale si rompe, e *dove* nell'immagine agisce nel regime in cui le
   mappe sono ancora valide.

## Cosa NON fare

* **Non toccare i prompt.** Verbatim da `data/prompts_anima_native.json`, hash incluso nel CSV.
* **Non cambiare la serie di dosi fra uno slot e l'altro.** La mappa vale come confronto solo
  se tutti i blocchi percorrono la stessa rampa. Se uno slot sembra non fare niente, si annota
  — non si alza la dose solo per lui. La rampa si accorcia o si allunga per **tutti insieme**,
  e solo in base all'esito della rampa pilota.
* **Non scartare immagini brutte o collassate.** Sono il dato.
* **Non applicare upscaler, detailer, face-fix o post-processing.**
* **Non combinare due slot.** Uno alla volta: la mappa serve a isolare, e l'interazione fra
  blocchi è una domanda successiva e separata.
* **Non modificare `Arthemy_Krea2_Tuner.py` oltre le tre righe della Parte 0.** Se qualcosa
  non funziona, fermarsi e riferire.
