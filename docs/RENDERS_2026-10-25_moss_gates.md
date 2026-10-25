# MOSS1: Installazione del Nodo MOSS ed Esecuzione dei Cancelli A, B, C (6 render) — 2026-10-25

Esecuzione condotta da Antigravity seguendo le direttive prescritte in [docs/directives_antigravity_moss_gates.md](directives_antigravity_moss_gates.md) (autorizzazione di Alessandro).
Nessun processo è stato terminato in autonomia; ComfyUI è stato riavviato da Alessandro per ricaricare il nodo. Nessun render oltre i 6 previsti dal protocollo dei cancelli.

---

## Step 1 — Installazione del Nodo

Installazione di `Arthemy_MOSS_Tuner` (versione 3, con clone non-dinamico su patcher e riallineamento di `cond_stage_model = patcher.model` per la codifica del testo):

```powershell
New-Item -ItemType Directory -Force D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_MOSS_Tuner | Out-Null
Copy-Item ..\tools\comfyui_moss_tuner\__init__.py D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_MOSS_Tuner\__init__.py
```

Riavvio di ComfyUI confermato da Alessandro.

### Verifica dell'Import (da `user/comfyui.log`)

```text
[2026-10-25 12:25:41.598]    0.0 seconds: D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_MOSS_Tuner
```

Registrazione confermata via API ComfyUI:
* `ArthemyMossModelTuner`: `True`
* `ArthemyMossCLIPTuner`: `True`

---

## Step 2 — Cancello B (Gate B: Quantizzazione e Invarianza a Vuoto)

Esecuzione del test numerico sul Text Encoder Qwen3.5-9B (W4A8 GPTQ):

```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& $PY moss_gate.py --quant
```

### Output Verbatim

```text
qwen35_9b.transformer.model.layers.6.mlp.down_proj.weight d=+0.10: max relative error 1.28e-07
qwen35_9b.transformer.model.layers.6.mlp.down_proj.weight d=-0.50: max relative error 0.00e+00
qwen35_9b.transformer.model.layers.7.self_attn.o_proj.weight d=+0.10: max relative error 2.03e-07
qwen35_9b.transformer.model.layers.7.self_attn.o_proj.weight d=-0.50: max relative error 0.00e+00
qwen35_9b.transformer.model.layers.0.linear_attn.out_proj.weight d=+0.10: max relative error 1.68e-07
qwen35_9b.transformer.model.layers.0.linear_attn.out_proj.weight d=-0.50: max relative error 0.00e+00
conditioning with '{}' bit-identical: True (1, 85, 4096)
GATE B PASS
```

* **Esito**: **`GATE B PASS`** (errore relativo massimo $< 2.03 \times 10^{-7}$, ampiamente sotto la soglia di $10^{-5}$; condizionamento con `{}` bit-identical: `True`).

---

## Step 3 — Cancelli A e C (Gate A: Determinismo e Invarianza; Gate C: Sensibilità agli Edit)

### Accodamento dei 6 Render

```powershell
& $PY moss_gate.py --queue
```

#### Output (Prompt ID registrati)

```text
plain_a d065d270-bfe6-445c-984b-ea66561ad636
plain_b b5e76c1c-ad86-45bc-b97f-9d834b1af190
empty_json 3f0ee9fa-a2df-42ac-b5f6-76d0621e0b45
te_L06_mlp_down_x2 41261ce8-1e89-4bf8-825f-7d20d3824ddc
dit_L20_ffn_down_x2 bd246ba3-8014-4905-bf67-8c7cc2e1b17a
plain_c b8b93deb-76f1-441f-85f9-8b1dfec83c80
```

### Tempi di Esecuzione per Immagine (da `user/comfyui.log`)

* **`plain_a`**: **83.05 s** (campionamento 25 step a 3.19 s/it, dynamic VRAM)
* **`plain_b`**: **0.10 s** (cache hit ComfyUI su grafo identico)
* **`empty_json`**: **91.02 s** (campionamento 25 step in 1:19 a 3.19 s/it; Text Encoder: 7003.19 MB caricati in memoria, DiT: 9693.73 MB caricati in memoria, full load: True)
* **`te_L06_mlp_down_x2`**: **87.41 s** (campionamento 25 step in 1:19 a 3.13 s/it; Text Encoder: 7003.19 MB caricati in memoria, DiT: 9693 MB staged dynamic)
* **`dit_L20_ffn_down_x2`**: **89.00 s** (campionamento 25 step in 1:18 a 3.15 s/it; Text Encoder: 7002 MB staged dynamic, DiT: 9693.73 MB caricati in memoria, full load: True)
* **`plain_c`**: **82.10 s** (campionamento 25 step in 1:19 a 3.18 s/it, dynamic VRAM)

### Allocazione Memoria GPU / VRAM

* **Text Encoder `MOSSImageTEModel_` (`qwen3.5_9b_w4a8_gptq.safetensors`)**:
  * In modalità non-dinamica: 7003.19 MB caricati interamente su VRAM (`full load: True`).
  * In modalità dinamica: 7002 MB staged per caricamento on-demand.
* **DiT `MOSSImage` (`moss_image_sft_bf16.safetensors`)**:
  * In modalità non-dinamica: 9693.73 MB caricati interamente su VRAM (`full load: True`).
  * In modalità dinamica: 9693 MB staged per caricamento on-demand.
* **VAE `AutoencoderKL` (`flux2-vae_small.safetensors`)**: 118 MB staged.
* **Stabilità VRAM**: nessun errore di out-of-memory o fallimento di allocazione.

### Verifica dei Render

```powershell
& $PY moss_gate.py --renders
```

#### Output Verbatim

```text
A plain twice: max 0 | plain again later: max 0 | tuners with '{}': max 0
C text-encoder edit: mean 13.7 | DiT edit: mean 33.4
GATE A PASS
GATE C PASS
```

* **Gate A**: **`PASS`**
  * Ripetizione plain immediata (`plain_a` vs `plain_b`): differenza massima **0**.
  * Ripetizione plain ritardata (`plain_a` vs `plain_c`): differenza massima **0**.
  * Tuner con JSON vuoto `{}` (`plain_a` vs `empty_json`): differenza massima **0** (determinismo bit-exact preservato anche attraverso il percorso non-dinamico).
* **Gate C**: **`PASS`**
  * Edit Text Encoder (`te_L06_mlp_down_x2` vs `empty_json`): differenza media **13.7** (soglia $> 5$).
  * Edit DiT (`dit_L20_ffn_down_x2` vs `empty_json`): differenza media **33.4** (soglia $> 5$).

Tutti e tre i cancelli metodologici (**A, B, C**) sono convalidati con successo.
