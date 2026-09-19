# BRIEF — Anima Stage 1: il preset trasposto funziona su un'altra architettura?

**Esecutore**: Antigravity, pilotando ComfyUI.  
**Generato da**: `experiments/make_anima_brief.py`, con i prompt letti verbatim da
`data/prompts.json` e ogni `prompt_sha1` ri-verificato in fase di generazione.  
**Non modificare i prompt.** Il `prompt_sha1` è la prova che non sono stati toccati:
se un carattere cambia, l'hash non torna e il confronto con Krea-2 non vale più.

---

## 1. La domanda, e cosa la chiuderebbe

Su Krea-2 una perturbazione strutturata dei pesi separa il preset calibrato dai controlli
appaiati in norma sulla morfologia del tratto. **Qui si chiede se lo stesso preset,
trasposto gerarchicamente, produca un effetto misurabile su un'architettura diversa.**

Anima differisce da Krea-2 su tre assi contemporaneamente: ha cross-attention in ogni
blocco (Krea-2 non ne ha in nessuno), ha 2048 di dimensione nascosta contro 6144, e i
suoi 28 blocchi hanno 20 tensori invece di 13. Un esito positivo è quindi informativo;
un esito negativo, da solo, non distingue quale dei tre assi lo ha causato.

**Esito atteso dichiarato prima**: separazione del preset da `randsign` sull'asse
principale di continuità del tratto, con intervallo di confidenza al 95% che esclude lo
zero. È lo stesso criterio pre-dichiarato nella Priorità 8 della roadmap.

## 2. Cancello da superare PRIMA di misurare qualunque condizione

Guardare **solo i 50 render baseline**, prima di toccare le altre condizioni.

* Se i baseline non mostrano tratteggio riconoscibile, l'asse di tratteggio è **indefinito**
  su questo modello e va **escluso**, non riportato come risultato negativo. Le altre
  famiglie di feature restano misurabili.
* Se i baseline sono deformi o illeggibili, il regime di campionamento è sbagliato: si
  ferma tutto e si ritara, non si prosegue.

Registrare l'esito del cancello per iscritto prima di generare il resto.

## 3. Condizioni

I preset sono **gia' costruiti** e verificati. Comando che li ha prodotti:

```
python experiments/build_anima_preset.py \
    --ckpt ...\anima_baseV10.safetensors \
    --out-dir .\presets_anima       --match-d 0.045745 --cross attn
python experiments/build_anima_preset.py \
    --ckpt ...\anima_baseV10.safetensors \
    --out-dir .\presets_anima_nocross --match-d 0.045745 --cross none
```

| condizione | file | ruolo |
|---|---|---|
| `baseline` | — | checkpoint non modificato |
| `preset` | `presets_anima/Anima_Bench_PRESET.json` | trasposizione gerarchica del preset Krea-2 |
| `blockshuf_neg` | `presets_anima/Anima_Bench_BLOCKSHUF_NEG.json` | stessi valori, destinazione dei blocchi permutata |
| `randsign` | `presets_anima/Anima_Bench_RANDSIGN.json` | stessi valori, segno casuale per tensore |
| `preset_nocross` | `presets_anima_nocross/Anima_Bench_PRESET.json` | come `preset` ma senza toccare la cross-attention |

**Tutte e cinque a $D_{\text{backbone}} = 0.045745$ esatto**, ciascuna riscalata
individualmente. `blockshuf_neg` senza riscalatura propria sarebbe finita a 0.044077, il
3.6% sotto: un controllo appaiato che non e' appaiato non e' un controllo, e la differenza
verrebbe attribuita alla struttura quando invece e' dose.

`randsign` decide il senso di tutto il resto: conserva l'ampiezza e distrugge la struttura.
Se produce lo stesso effetto del preset, il risultato riguarda la distanza dal checkpoint e
non la direzione, e la claim centrale del progetto non si trasferisce. **Non va omessa per
risparmiare render.**

`preset_nocross` risponde a una domanda che su Krea-2 non e' ponibile: Anima ha
cross-attention in ogni blocco, Krea-2 in nessuno. Confrontarla con `preset` misura quanto
dell'effetto passa dal percorso testuale. E' l'analogo Anima-nativo dello split
DiT / text-encoder di §2.3.

Il text encoder resta **intatto** in tutte le condizioni.

### Come si applicano — checkpoint cotti, nessun custom node

**La suite Anima non e' installata**: in `custom_nodes` esistono solo
`Arthemy_Anima_Suite.py.backup_original` e `.bak`, con estensione non caricabile, e
nessuna delle due ha un rotator o un caricatore di preset. I nodi `ArthemyAnima*` che
compaiono nel workflow oggi non hanno un'implementazione attiva.

Quindi l'edit si applica **offline**, producendo checkpoint gia' modificati che qualunque
workflow carica come modelli normali. Oltre a togliere la dipendenza dal nodo, questo
rende l'edit verificabile *prima* di generare qualunque immagine e da' a ogni condizione
uno SHA-256 che la rende riproducibile alla lettera.

```
cd comfyui-pilot
set BASE=...\Models\DiffusionModels\anima_baseV10.safetensors
set OUT=...\Models\DiffusionModels\anima_bench

python experiments\bake_preset.py --base %BASE% --preset presets_anima\Anima_Bench_PRESET.json        --out %OUT%\anima_PRESET.safetensors
python experiments\bake_preset.py --base %BASE% --preset presets_anima\Anima_Bench_BLOCKSHUF_NEG.json --out %OUT%\anima_BLOCKSHUF_NEG.safetensors
python experiments\bake_preset.py --base %BASE% --preset presets_anima\Anima_Bench_RANDSIGN.json      --out %OUT%\anima_RANDSIGN.safetensors
python experiments\bake_preset.py --base %BASE% --preset presets_anima_nocross\Anima_Bench_PRESET.json --out %OUT%\anima_PRESET_nocross.safetensors
```

Ogni chiamata ricalcola il $D$ del backbone **dal file prodotto** e lo confronta con quello
dichiarato nel preset. **Se una qualsiasi stampa `FUORI TOLLERANZA` o elenca chiavi non
trovate, fermarsi**: significa che il checkpoint non e' quello per cui il preset e' stato
costruito. Annotare i quattro SHA-256.

Servono ~16 GB liberi. La condizione `baseline` usa il checkpoint originale non modificato.

> Nota sulla precisione: il bake riscrive in bf16, che ha 8 bit di mantissa, quindi il
> guadagno realizzato devia dal richiesto fino a $3.9\times10^{-3}$ relativo. I guadagni
> qui vanno da 0.013 a 0.142, cioe' da 3 a 36 volte quel pavimento: l'edit sopravvive. Non
> vale per dosi molto piu' piccole — vedi pitfall 46.

### Nota metodologica: perche' $D$ e' misurato sul solo backbone

Anima ha un tensore, `llm_adapter.embed.weight` (32128 x 1024, la tabella di embedding
dei token), la cui norma di Frobenius e' **38558 contro le ~101 di tutto il resto del
modello messo insieme**: da solo vale il **99.96%** di $\|W\|^2$. Un $D$ calcolato
sull'intero checkpoint misura quindi quasi solo quella tabella.

Conseguenza concreta: il primo tentativo, che appaiava il $D$ sull'intero checkpoint a
0.0538, produceva un fattore di riscalatura di **0.425** — cioe' avrebbe generato un edit
del backbone due volte e mezzo piu' debole del dovuto, e il confronto con Krea-2 sarebbe
stato un confronto fra dosi diverse. Misurato sul solo backbone, che e' la parte che le due
architetture condividono e l'unica su cui il preset ha significato:

* Krea-2, preset calibrato, blocchi 0-27: $D = 0.045745$
* Anima, trasposizione diretta, blocchi 0-27: $D = 0.040771$

cioe' un fattore 1.12, non 2.35. La tabella di embedding e' inoltre **esclusa dall'edit**:
e' l'analogo strutturale di cio' che sta nel text encoder, che per decisione di progetto
non viene toccato.

**Questa e' una scoperta sulla portabilita' del metodo, non un dettaglio di
implementazione**: lo spostamento relativo di Frobenius sull'intero checkpoint non e'
un'unita' di dose portabile fra architetture. Va nell'errors_log.

## 4. Regimi di campionamento — due bracci, e perché servono entrambi

| | passi | CFG | sampler | scheduler |
|---|---|---|---|---|
| **A · nativo Anima** | 30 | 5.5 | `euler_ancestral` | `simple` |
| **B · ponte** | 9 | 1.0 | `euler_ancestral` | `simple` |

Il braccio B usa il regime di Krea-2 (9 passi, CFG 1.0) e verrà **brutto**. Serve comunque: senza,
una differenza fra i due modelli confonde architettura e regime di campionamento, che è
l'alternativa che la Priorità 4 della roadmap dichiara non testata e capace di spiegare
l'intero programma. Se la firma dell'edit sopravvive nel braccio B, il confronto con
Krea-2 è appaiato; se compare solo nel braccio A, la scoperta riguarda il regime e non
l'architettura — che resta un risultato, diverso da quello atteso.

Il braccio B gira su **3 seed** invece di 5 (42, 777, 1337): serve a decidere se la firma
c'è, non a stimarne la dimensione.

**Trappola**: `euler_ancestral` inietta rumore nuovo a ogni passo, quindi lo stesso seed a
9 e a N passi è un'immagine **diversa**, non una coppia appaiata. I due bracci non vanno
confrontati seed per seed fra loro; ciascuno si confronta con il proprio baseline.

## 5. Matrice di generazione

* **Braccio A**: 10 prompt × 5 seed × 5 condizioni = **250 immagini**
* **Braccio B**: 10 prompt × 3 seed × 4 condizioni (senza `preset_nocross`) = **120 immagini**
* **Totale: 370 immagini**

Seed braccio A: `42, 777, 1337, 9999, 4242145` — gli stessi cinque canonici di tutto
il progetto. Seed braccio B: `42, 777, 1337`.

Risoluzione: quella nativa di Anima. **Non** forzare 1024×1280 se non è la sua: una
risoluzione fuori specifica degrada i render e il degrado verrebbe letto come effetto
dell'edit. Annotare la risoluzione usata.

## 6. Nomi dei file — vincolante

Gli script di estrazione già esistenti (`experiments/style_features.py`,
`experiments/analyze_palette.py`) leggono il nome del file. Deve essere esattamente:

```
<prompt_id>_<condizione>_<braccio>_seed<seed>_00001_.png
```

Esempi: `I01_baseline_A_seed42_00001_.png`, `I07_randsign_B_seed1337_00001_.png`.

Cartella: `output\benchmark_anima1\renders\` — tutti i file in una sola cartella piatta,
come per stage 9 e stage 12.

Scrivere anche `anima1_images.csv` con le stesse colonne di `stage12_images.csv`:
`run_id, stage, arm, cond_name, renders_root, image_path, baseline_path, prompt_id,`
`prompt_sha1, prompt_text, seed, sampler, steps, cfg, width, height, preset_file, timestamp`.

## 7. Ordine di esecuzione

1. Cuocere i quattro checkpoint (§3) e **registrare l'output di ogni chiamata**: copertura per
   gruppo, $D$ verificato, SHA-256. Se una stampa `FUORI TOLLERANZA` o elenca chiavi
   non trovate, fermarsi e segnalare.
2. Generare i **50 baseline del braccio A**. Applicare il cancello del §2. Non proseguire
   senza averlo registrato.
3. Generare il resto del braccio A.
4. Generare il braccio B per intero.
5. Estrarre le feature con gli script esistenti e scrivere i CSV accanto agli altri in
   `comfyui-pilot/`.

## 8. Cosa NON fare

* Non riscrivere, tradurre o accorciare i prompt. Nemmeno per farli rendere meglio.
* Non cambiare seed, sampler o risoluzione fra una condizione e l'altra dello stesso
  braccio: le condizioni si confrontano appaiate per prompt e seed.
* Non scartare render brutti. Un render degradato è un dato sul comportamento dell'edit,
  e scartarlo selettivamente è la via più rapida per fabbricare un risultato.
* Non applicare upscaler, detailer, face-fix o post-processing di alcun tipo.
* Non toccare il text encoder.

---

## 9. I dieci prompt, verbatim

Selezione dichiarata in anticipo: i dieci ID più bassi del corpus di conferma stage 7
(quello su cui l'asse di tratteggio ha dato 16/16 su Krea-2). Dieci prompt mettono il
pavimento del test di permutazione esatto a $2/2^{10} = 0.00195$.

### `I01` · `prompt_sha1 2adb8ea1cd`

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A viking woman with blonde long braided hair. armor made of ice, She wears an iron crown and large metallic shoulder pads. She's holding a mace with both hands, casual pose, snob, playful. snow covered plains, simple background. blue reflections on the metal.
```

### `I02` · `prompt_sha1 0aa12a28b0`

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. An elf man with long white straight hair. armor made of obsidian, He wears a silver circlet and thin curved shoulder guards. He's holding a rapier upright in one hand, defensive pose, calm, focused. misty autumn forest, simple background. green reflection on the glass.
```

### `I05` · `prompt_sha1 5b67e787c8`

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A tiefling woman with curled ram horns and purple hair. armor made of chitin, She wears a gold diadem and spiked black shoulder pads. She's holding a curved dagger underhand, dynamic pose, smug, cunning. brimstone volcanic wasteland, simple background. violet reflection on the chitin.
```

### `I06` · `prompt_sha1 a324a148e4`

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A human man with cropped brown hair and stubble. armor made of steel, He wears a chainmail coif and round polished shoulder guards. He's holding a tower shield across his chest, guarding pose, weary, resolute. ruined castle courtyard, simple background. white reflection on the metal.
```

### `I07` · `prompt_sha1 402376662d`

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A half-orc man with a shaved head and facial scars. armor made of granite, He wears an iron jaw visor and layered stone shoulder pads. He's holding a heavy greataxe pointed down, relaxed pose, solemn, tired. cracked dry earth, simple background. blue reflection on the stone.
```

### `I09` · `prompt_sha1 0a1c94584d`

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A dwarf woman with twin braided ginger pigtails. armor made of copper, She wears an iron miner cap and thick square shoulder pads. She's holding a heavy pickaxe leaning forward, cheerful pose, grinning, confident. underground crystal mine, simple background. yellow reflection on the copper.
```

### `I10` · `prompt_sha1 90ec9bbe8c`

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A lizardfolk man with spiked crest and yellow eyes. armor made of hard scales, He wears a feather headdress and woven rope shoulder pads. He's holding a flint spear ready to strike, predatory pose, wild, alert. murky green swamp, simple background. green reflection on the scales.
```

### `I11` · `prompt_sha1 2b36c75165`

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A gnome woman with wild blue curls. armor made of carved amber, She wears oversized brass monocles and round gear-shaped shoulder guards. She's holding an alchemical vial in both hands, frantic pose, manic, excited. stone alchemy laboratory, simple background. orange reflection on the glass.
```

### `I12` · `prompt_sha1 8c3325ffd9`

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A human woman with short raven pixie cut. armor made of polished silver, She wears a cloth hood and sleek aerodynamic shoulder guards. She's holding a shortsword crossed over chest, ready pose, cold, calculating. rain-soaked rooftop, simple background. blue reflection on the silver.
```

### `I16` · `prompt_sha1 5421ab290b`

```text
Western comics style, bold ink outlines, hatched shadows, upper body portrait. A halfling man with curly blond sideburns. armor made of layered leather, He wears a wool beret and hardened boiled-leather shoulder pads. He's holding a small iron buckler and sling, nimble pose, cheekily defiant, smirking. rolling green hillside, simple background. white reflection on the leather.
```
