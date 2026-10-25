# MOSS2: Banco MOSS — Riproducibilità, Pavimento dei Seed e Prima Scala di Sensibilità (84 Render) — 2026-10-25

Esecuzione condotta da Antigravity seguendo le direttive prescritte in [docs/directives_antigravity_moss_bench.md](directives_antigravity_moss_bench.md) (autorizzazione di Alessandro).  
Pre-registrazione di riferimento: [docs/prereg_moss_bench.md](prereg_moss_bench.md) (Emendamenti 1 e 2). Piano frozen: [data/moss_bench_plan.csv](../data/moss_bench_plan.csv).

> **Verdetto V1: PASS**  
> La massima differenza in pixel tra due render identici dello stesso prompt e seed nella stessa sessione (con forzatura del calcolo tramite payload differenziato per bypassare la cache di ComfyUI) è esattamente **0** (riproducibilità deterministica bit-exact confermata).

---

## Step 0 — Pulizia e Ripartenza

* Verificata la coda di ComfyUI (inizialmente vuota).
* La cartella dei render del primo tentativo (avviato con parametri errati prima dell'emendamento) è stata archiviata:
  ```powershell
  Rename-Item D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_moss_bench benchmark_moss_bench_stopped_20261025_173358
  ```

---

## Step 1 — Esecuzione e Conteggio File

Accodamento dei render previsti dal piano:
```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& $PY moss_bench.py --queue
```

*Output:*
```text
queued 84
```

*Nota di esecuzione:* Durante l'esecuzione del batch, ComfyUI è stato accidentalmente chiuso dall'utente al render 55/84 e immediatamente riavviato. Il rilancio del comando `--queue` ha riconosciuto e preservato i 55 render già generati senza duplicazioni, completando in sequenza i rimanenti 29 render fino al totale prescritto di 84.

### Verifica del Conteggio File

```powershell
& $PY moss_bench.py --count
```

*Output Verbatim:*
```text
expected 84 missing 0 []
```

### Tempi di Rendering Misurati per Impostazione

* **`T10`** (77 render totali: MOSS-Image SFT BF16 + LoRA turbo DMD2 1.0, euler, 10 step, CFG 1.0, 1024×1280):
  * **22.0 s** di media netta escludendo la pausa di riavvio (mediana **22.1 s**, min **16.3 s**, max **31.0 s**).
  * Media lorda inclusivo del delta del riavvio: 24.4 s (max 208.6 s).
* **`R50`** (7 render di conferma: MOSS-Image SFT BF16 senza LoRA, euler, 50 step, CFG 3.0, 1024×1280):
  * **166.1 s** di media (mediana **165.7 s**, min **163.0 s**, max **171.7 s**).

---

## Step 2 — Analisi DINOv2 e Metriche

Esecuzione dell'analisi e calcolo delle distanze DINOv2:
```powershell
& $PY moss_bench.py --analyze
```

### Output Verbatim Integrale

```text
V1 the dwarf rendered twice in one session | max 0 | PASS
V2 DiT layer 41 x 1.0001 (D1_dwarf_paladin) | max 0 | PASS
V2r TE layer 31 MLP down x 1.0001 (D1_dwarf_paladin), reported | max 255, changed pixels 0.760 | -
V2 DiT layer 41 x 1.0001 (S1_rally) | max 0 | PASS
V2r TE layer 31 MLP down x 1.0001 (S1_rally), reported | max 241, changed pixels 0.965 | -
floor D1_dwarf_paladin | median D between seeds 0.098 (min 0.073, n 6) | -
floor S1_rally | median D between seeds 0.335 (min 0.306, n 6) | -
floor C4_stilllife | median D between seeds 0.249 (min 0.105, n 6) | -
floor P5_comic_panels | median D between seeds 0.075 (min 0.063, n 6) | -
floor P2_lotuscanoe | median D between seeds 0.056 (min 0.054, n 6) | -
floor LN | median D between seeds 0.155 (min 0.081, n 6) | -
ladder D1_dwarf_paladin dit06, reported | 0.1:0.006 0.3:0.011 1:0.027 2:0.031 | -
ladder D1_dwarf_paladin dit20, reported | 0.1:0.004 0.3:0.013 1:0.029 2:0.062 | -
ladder D1_dwarf_paladin dit35, reported | 0.1:0.002 0.3:0.015 1:0.056 2:0.383 | -
ladder D1_dwarf_paladin te06, reported | 0.1:0.002 0.3:0.005 1:0.022 2:0.040 | -
ladder D1_dwarf_paladin te15, reported | 0.1:0.004 0.3:0.009 1:0.032 2:0.034 | -
ladder D1_dwarf_paladin te27, reported | 0.1:0.006 0.3:0.003 1:0.038 2:0.115 | -
ladder S1_rally dit06, reported | 0.1:0.011 0.3:0.039 1:0.039 2:0.058 | -
ladder S1_rally dit20, reported | 0.1:0.010 0.3:0.039 1:0.226 2:0.171 | -
ladder S1_rally dit35, reported | 0.1:0.013 0.3:0.028 1:0.089 2:0.204 | -
ladder S1_rally te06, reported | 0.1:0.011 0.3:0.033 1:0.044 2:0.056 | -
ladder S1_rally te15, reported | 0.1:0.013 0.3:0.028 1:0.030 2:0.035 | -
ladder S1_rally te27, reported | 0.1:0.011 0.3:0.043 1:0.070 2:0.156 | -
```

I risultati completi sono stati scritti in [data/moss_bench_tests.csv](../data/moss_bench_tests.csv) e [data/moss_bench_metrics.csv](../data/moss_bench_metrics.csv).

---

## Sintesi dei Test

### 1. Cancelli di Validazione Strutturale (V1, V2, V2r)

| Test | Condizione / Target | Valore Misurato | Verdetto |
|---|---|---|:---:|
| **V1** | Dwarf plain vs plain ripetuto in sessione | max diff pixel: **0** | **PASS** |
| **V2** | DiT layer 41 $\times 1.0001$ (`D1_dwarf_paladin`) | max diff pixel: **0** | **PASS** |
| **V2** | DiT layer 41 $\times 1.0001$ (`S1_rally`) | max diff pixel: **0** | **PASS** |
| **V2r** | TE layer 31 MLP down $\times 1.0001$ (`D1_dwarf_paladin`) | max 255, pixel modificati: 0.760 | Report |
| **V2r** | TE layer 31 MLP down $\times 1.0001$ (`S1_rally`) | max 241, pixel modificati: 0.965 | Report |

*Osservazione su V2/V2r:* Il test V2 conferma che nei pesi BF16 puri del DiT una variazione di $+0.0001$ viene troncata a 0 dall'aritmetica floating point senza alterare i pesi (neutralità perfetta). Nel Text Encoder (V2r), data la quantizzazione W4A8 GPTQ con scale FP32 sui canali, una perturbazione infinitesima tocca le scale FP32 e altera legittimamente una frazione di pixel, coerentemente con le attese documentate.

### 2. Pavimento tra i Seed (Seed Floor)

Distanza DINOv2 mediana tra le 4 varianti di seed per i 6 prompt C100:

| Prompt | DINOv2 Mediana tra Seed | DINOv2 Minima tra Seed | Coppie (n) |
|---|:---:|:---:|:---:|
| `D1_dwarf_paladin` | **0.098** | 0.073 | 6 |
| `S1_rally` | **0.335** | 0.306 | 6 |
| `C4_stilllife` | **0.249** | 0.105 | 6 |
| `P5_comic_panels` | **0.075** | 0.063 | 6 |
| `P2_lotuscanoe` | **0.056** | 0.054 | 6 |
| `LN` | **0.155** | 0.081 | 6 |

### 3. Celle di Conferma R50 vs T10 ($d = 1.0$)

Confronto tra la risposta ad $d = 1.0$ su T10 (working setting a 10 step turbo) e su R50 (riferimento puro a 50 step) per il prompt `D1_dwarf_paladin`:

| Modifica ($d = 1.0$) | Distanza DINOv2 T10 | Distanza DINOv2 R50 |
|---|:---:|:---:|
| `dit06_p1` | 0.0265 | 0.0235 |
| `dit20_p1` | 0.0290 | 0.0306 |
| `dit35_p1` | 0.0564 | 0.0746 |
| `te06_p1` | 0.0218 | 0.0347 |
| `te15_p1` | 0.0318 | 0.0215 |
| `te27_p1` | 0.0384 | 0.0302 |

---

## Vincoli di Riservatezza Visiva

In conformità al protocollo del banco MOSS2 e alle regole operative di progetto, **nessuna immagine generata è stata aperta o descritta visivamente**. La pagina di conferma visiva e valutazione qualitativa in cieco è riservata a Claude e ad Alessandro.

---

## Emendamento 3: Conferma a $d = 2.0$ a 50 step (6 Render R50) e Pagina Cieca `occhio_MOSS2b`

Esecuzione condotta seguendo le direttive prescritte in [docs/directives_antigravity_moss_confirm2.md](directives_antigravity_moss_confirm2.md) e la pre-registrazione [docs/prereg_moss_bench.md](prereg_moss_bench.md) (Emendamento 3).  
Poiché a dose $d = 1.0$ i cambiamenti risultavano appena percettibili a occhio nudo, sono stati generati 6 render di conferma a 50 step (R50) per il prompt `D1_dwarf_paladin` a dose $d = 2.0$ (`p2`), corrispondenti ai 6 layer testati (`dit06`, `dit20`, `dit35`, `te06`, `te15`, `te27`).

### 1. Accodamento e Conteggio File

```powershell
& $PY moss_bench.py --queue
```
*Output:*
```text
queued 6
```
*(Gli 84 render già esistenti sono stati ignorati; accodati esclusivamente i 6 render del blocco `confirm2`).*

Verifica del conteggio complessivo:
```powershell
& $PY moss_bench.py --count
```
*Output Verbatim:*
```text
expected 90 missing 0 []
```

### 2. Tempi di Rendering Misurati (R50 a $d = 2.0$)

* **`R50 confirm2`** (6 render a 50 step, euler, CFG 3.0, 1024×1280):
  * **165.9 s** di media (mediana **167.0 s**, min **161.9 s**, max **170.6 s**).
  * Durata complessiva del blocco: circa 16 minuti e 38 secondi.

### 3. Generazione della Pagina Cieca e Chiave Sperimentale

Esecuzione del generatore del test in cieco:
```powershell
& $PY moss_confirm_page.py
```
*Output Verbatim:*
```text
cards 15 -> D:\StabilityMatrix-win-x64\Data\Images\Text2Img\occhio_MOSS2b.html
```

* File generati:
  * Foglio cieco per la valutazione visiva: `D:\StabilityMatrix-win-x64\Data\Images\Text2Img\occhio_MOSS2b.html` (15 schede: 6 matched, 6 control, 3 ripetute).
  * Chiave di decodifica sperimentale pre-registrata: [data/moss_confirm2_key.csv](../data/moss_confirm2_key.csv).

In conformità al protocollo sperimentale, nessuna immagine o scheda di confronto è stata aperta o descritta dall'agente.
