# MOSS-S: Scelta delle Impostazioni di Campionamento (84 Render) — 2026-10-25

Esecuzione condotta da Antigravity seguendo le direttive prescritte in [docs/directives_antigravity_moss_settings.md](directives_antigravity_moss_settings.md) e la pre-registrazione [docs/prereg_moss_settings.md](prereg_moss_settings.md).
Obiettivo: determinare se impostazioni di campionamento più veloci (E25 a 25 step o T8 turbo LoRA a 8 step) possano sostituire o affiancare il riferimento lento R50 (50 step).

---

## Step 0 — Installazione Tuner v4 e Verifica LoRA

* **Tuner v4**: Installato in `D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_MOSS_Tuner\__init__.py`. Supporta l'applicazione delle modifiche ai pesi sopra il LoRA attivo via `patcher.add_patches` con scaling $(W + \text{LoRA}) \times (1 + d)$.
* **Riavvio ComfyUI**: Confermato da Alessandro; nodo caricato senza errori (`0.0 seconds`).
* **Verifica LoRA**: File `D:\StabilityMatrix-win-x64\Data\Models\Lora\Moss\lodestones-8-steps-dmd2-lora.safetensors` presente (1.19 GB).

---

## Step 1 — Accodamento e Verifica LoRA

Accodati gli 84 render (`queued 84`).

### Ispezione del Caricamento LoRA sul Primo Render Turbo (`T8`)

* **Tensori patchati**: `m_lora.patches` conta esattamente **168 tensori di peso** ($42 \text{ layer} \times 4 \text{ proiezioni: } qkv, o, ffn\_up\_gate, ffn\_down$).
* **Log di runtime ComfyUI**:
  * Nessun avviso di chiavi non caricate (zero occorrenze di `lora key not loaded` o `NOT LOADED`).
  * Il modello è stato caricato interamente in memoria senza errori di allocazione o OOM.
* **Verifica conteggio finale**:
  ```text
  expected 84 missing 0 []
  ```

### Tempi di Rendering Misurati per Impostazione

* **`T8`** (8 step, euler, CFG 1.0, DMD2 LoRA): **19.4 s** di media (mediana 19.7 s, min 13.2 s, max 28.4 s)
* **`E25`** (25 step, euler, CFG 3.0, shift 5): **84.0 s** di media (mediana 83.8 s, min 79.0 s, max 91.0 s)
* **`R50`** (50 step, euler, CFG 3.0, riferimento): **163.4 s** di media (mediana 163.0 s, min 156.8 s, max 173.0 s)

---

## Step 2 — Analisi DINOv2 e Foglio di Contatto

### Output Verbatim (`moss_settings.py --analyze`)

```text
seed floor R50 | median D between the two seeds 0.137 | -
seed floor E25 | median D between the two seeds 0.180 | -
seed floor T8 | median D between the two seeds 0.105 | -
S1 E25 plain close to R50 | median D 0.031 vs half the R50 floor 0.069 | PASS
S2 E25 edits proportional to R50 | Spearman 0.47 (bar 0.80), median ratio 0.90 (0.5-2) | FAIL
S1 T8 plain close to R50 | median D 0.142 vs half the R50 floor 0.069 | FAIL
S2 T8 edits proportional to R50 | Spearman 0.48 (bar 0.80), median ratio 1.57 (0.5-2) | FAIL
```

### Output Verbatim (`moss_settings.py --sheet`)

```text
sheet: columns per seed R50 | E25 | T8 -> D:\StabilityMatrix-win-x64\Data\Images\Text2Img\_moss_settings_sheet.jpg
```

* **Contact sheet generato**: `D:\StabilityMatrix-win-x64\Data\Images\Text2Img\_moss_settings_sheet.jpg` (confronto visivo delle immagini plain tra R50, E25 e T8).

---

## Sintesi dei Risultati e Criteri di Pre-registrazione

1. **Seed Floor per Setting**:
   * **R50**: distanza mediana tra semi $D = 0.137$ (metà floor: $0.069$).
   * **E25**: distanza mediana tra semi $D = 0.180$.
   * **T8**: distanza mediana tra semi $D = 0.105$ (la distillazione riduce la dispersione tra i semi).
2. **Candidato E25 (25 step)**:
   * **S1 Fedeltà plain**: **PASS** ($D = 0.031 \le 0.069$). L'immagine plain a 25 step è vicina e coerente con quella a 50 step.
   * **S2 Proporzionalità degli edit**: **FAIL** (Spearman $0.47 < 0.80$, rapporto mediano $0.90$). La gerarchia e la sensibilità delle dosi di steering a 25 step non correlano a sufficienza con la risposta del riferimento a 50 step.
3. **Candidato T8 (Turbo LoRA 8 step)**:
   * **S1 Fedeltà plain**: **FAIL** ($D = 0.142 > 0.069$). Il LoRA altera sensibilmente la distribuzione visiva rispetto al modello base SFT.
   * **S2 Proporzionalità degli edit**: **FAIL** (Spearman $0.48 < 0.80$, rapporto mediano $1.57$).
4. **Esito Decisionale (da pre-registrazione)**:
   Poiché né E25 né T8 superano congiuntamente S1 e S2, le impostazioni veloci non possono sostituire tout-court il riferimento R50 per la calibrazione e gli esperimenti di precisione. La valutazione visiva del contact sheet spetta ad Alessandro.
