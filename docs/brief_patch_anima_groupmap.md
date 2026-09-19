# BRIEF — Patch del tuner per Anima: `GROUP_MAP`

**Esecutore**: Antigravity.
**Ambito**: un solo file, quattro modifiche, tutte **additive**. Nessuna riga esistente va
riscritta o rimossa: si aggiungono voci in coda a liste che ci sono già.
**Indipendente**: non richiede ComfyUI acceso e non interferisce con la mappa Krea-2, che può
generare in parallelo.

File: `C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_Krea2_Tuner\Arthemy_Krea2_Tuner.py`

---

## 1. Il difetto, misurato

`ArthemyKrea2ModelTuner` assegna ogni tensore a uno dei nove slot con questa regola, al primo
riscontro utile nell'ordine del dizionario:

```python
if any(clean_key.startswith(pfx) or f".{pfx}" in clean_key for pfx in prefixes):
```

Anima contiene sei blocchi dell'**adattatore testuale** chiamati `llm_adapter.blocks.0.` …
`llm_adapter.blocks.5.`. La stringa `.blocks.0.` è contenuta dentro
`llm_adapter.blocks.0.cross_attn.q_proj.weight`, quindi quella chiave viene catturata dal
gruppo `Block_1`, che è il primo gruppo di blocchi a comparire nel dizionario.

Simulazione sulle 685 chiavi reali di `anima_baseV10.safetensors`, stato attuale:

| gruppo | oggi | atteso |
|---|---:|---:|
| Text_Fusion | **0** | 118 |
| Time_Embed | **0** | 3 |
| Projection | **0** | 4 |
| Block_1 | **195** | 100 |
| Block_2 | **119** | 100 |
| Block_3–6 | 100/100/80/80 | corretti |
| nessun gruppo | **11** | 0 |

**114 chiavi dell'adattatore testuale finiscono nei blocchi del backbone.** Non viene sollevata
nessuna eccezione: la generazione andrebbe a buon fine e i valori impostati su `Block_1` e
`Block_2` misurerebbero in parte il percorso del testo invece del solo backbone.

---

## 2. Le modifiche

### 2.1 — OBBLIGATORIA. `ArthemyKrea2ModelTuner.GROUP_MAP`

Intorno a **riga 2041**. È l'unica modifica necessaria perché la mappa esplorativa sia corretta.

**PRIMA**
```python
    GROUP_MAP = {
        "Text_Fusion": ["txtfusion.", "txtmlp."],
        "Time_Embed": ["tmlp.", "tproj."],
        "Projection": ["first.", "last."],
```

**DOPO**
```python
    GROUP_MAP = {
        "Text_Fusion": ["txtfusion.", "txtmlp.", "llm_adapter."],
        "Time_Embed": ["tmlp.", "tproj.", "t_embedder.", "t_embedding_norm"],
        "Projection": ["first.", "last.", "x_embedder.", "final_layer."],
```

**Non toccare le righe `"Block_1": [...]` e seguenti.** Restano identiche: Anima e Krea-2 hanno
entrambi 28 blocchi con la stessa suddivisione, quindi quelle liste sono già corrette per
entrambi.

**Perché funziona.** `Text_Fusion` è la prima voce del dizionario e il ciclo esce al primo
riscontro, quindi `llm_adapter.` cattura quelle 114 chiavi prima che `Block_1` possa vederle.

### 2.2 — CONSIGLIATA. `ArthemyKrea2LoraBlockLoader.GROUP_MAP`

Intorno a **riga 3197**. Le tre righe sono identiche a quelle del punto 2.1 e vanno modificate
allo stesso modo. Non serve alla mappa, ma se un giorno si carica una LoRA per blocchi su
Anima senza questa modifica si ripresenta esattamente lo stesso difetto, in un posto diverso.

### 2.3 — CONSIGLIATA. `_section_for_model_key`

Intorno a **riga 4068**. Serve ai visualizzatori e al preset saver: senza, un preset salvato da
Anima avrebbe le sezioni etichettate male.

**PRIMA**
```python
def _section_for_model_key(ck: str) -> Optional[str]:
    if "txtfusion" in ck or "txtmlp" in ck:
        return "Text_Fusion"
    if "tmlp" in ck or "tproj" in ck:
        return "Time_Embed"
    if clean_key_matches_projection(ck):
        return "Projection"
```

**DOPO**
```python
def _section_for_model_key(ck: str) -> Optional[str]:
    if "txtfusion" in ck or "txtmlp" in ck or "llm_adapter" in ck:
        return "Text_Fusion"
    if "tmlp" in ck or "tproj" in ck or "t_embedder" in ck or "t_embedding_norm" in ck:
        return "Time_Embed"
    if clean_key_matches_projection(ck) or "x_embedder" in ck or "final_layer" in ck:
        return "Projection"
```

L'ordine dei controlli va lasciato com'è: `llm_adapter` viene esaminato prima dei blocchi, che
è ciò che evita il difetto.

### 2.4 — CONSIGLIATA. `Krea2TensorParser.extract_model_block_idx`

Intorno a **riga 373**. Una sola parola aggiunta alla lista. Protegge i nodi sub-blocco dalla
stessa trappola.

**PRIMA**
```python
        if any(prefix in clean_key for prefix in ["txtfusion", "txtmlp", "tmlp", "tproj", "first", "last"]):
```

**DOPO**
```python
        if any(prefix in clean_key for prefix in ["txtfusion", "txtmlp", "tmlp", "tproj", "first", "last", "llm_adapter"]):
```

---

## 3. Fuori ambito — non fare

* **`MODEL_SURGEON_MAP`** (intorno a riga 296) contiene i nomi delle componenti interne di un
  blocco Krea-2 (`attn.wq.weight`, `mlp.up.weight`…). I nomi di Anima sono diversi
  (`self_attn.q_proj.weight`, `mlp.layer1.weight`…). Serve ai soli nodi sub-blocco, **non**
  alla mappa. Aggiungerlo adesso allarga la patch senza necessità: si farà quando servirà.
* **I rotator** su Anima. Richiedono la mappa delle componenti del punto precedente. Fuori
  ambito.
* **Il text encoder / CLIP.** Nessuna modifica.
* **Qualunque altra riga del file.** Se qualcosa sembra richiedere altre modifiche, **fermarsi
  e riferire** invece di proseguire.

---

## 4. Verifica — è uno script, non un giudizio

Lo script è già sul disco, in `custom_nodes\Arthemy_Krea2_Tuner\tests\verify_anima_groupmap.py`.
Non importa il modulo del tuner (servirebbero torch e comfy): legge `GROUP_MAP` **dal sorgente**
con l'AST di Python, quindi verifica il file vero e non una copia. Legge le sole intestazioni
dei safetensors, nessun peso: pochi secondi anche su file da 4 GB.

```
cd C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_Krea2_Tuner

python tests\verify_anima_groupmap.py ^
    --tuner Arthemy_Krea2_Tuner.py ^
    --anima C:\StabilityMatrix-win-x64\Data\Models\DiffusionModels\anima_baseV10.safetensors ^
    --krea2 C:\StabilityMatrix-win-x64\Data\Models\DiffusionModels\krea2_turbo_bf16.safetensors
```

Lo script controlla tre cose:

1. **Anima**, che ogni gruppo riceva esattamente il numero atteso di tensori
   (118 / 3 / 4 / 100 / 100 / 100 / 100 / 80 / 80, totale 685) e che nessuna chiave resti
   senza gruppo;
2. **Anima**, che nessuna chiave `llm_adapter` finisca in un gruppo `Block_*`;
3. **Krea-2**, la **non regressione**: ricostruisce la `GROUP_MAP` originale e confronta
   chiave per chiave. Le assegnazioni devono essere **identiche**, zero differenze su 430.

**Eseguito adesso, prima della patch, stampa `ESITO: FAIL`** con 114 chiavi in trappola — e già
`0` differenze su Krea-2. Dopo la patch deve stampare `ESITO: PASS`. Se stampa ancora FAIL, la
patch non è stata applicata o è stata applicata in una delle altre `GROUP_MAP`: si controlla di
aver modificato quella dentro la classe `ArthemyKrea2ModelTuner`.

*(Nota: non incanalare l'output in `tail` o simili se si vuole leggere il codice di uscita, che
verrebbe mascherato dalla pipe. Lo script esce con 0 su PASS e 1 su FAIL.)*

## 5. Accettazione finale

1. `verify_anima_groupmap.py` stampa **PASS**.
2. ComfyUI si riavvia senza errori in console.
3. **Controllo di non regressione a immagine**: su **Krea-2**, un render con tutti e nove gli
   slot a `0` deve risultare **identico** a un render baseline con lo stesso seed e lo stesso
   prompt. Se differisce, la patch ha effetti collaterali e va annullata.
4. Nessun file modificato oltre `Arthemy_Krea2_Tuner.py`.

Se i punti 1–4 passano, la Parte 2 del brief della mappa (`BRIEF_mappa_esplorativa.md`) può
partire su Anima.
