# MOSS-Image Survey (Read-Only, No Renders) — 2026-10-25

Esecuzione condotta da Antigravity seguendo le direttive prescritte in [docs/directives_antigravity_moss_survey.md](directives_antigravity_moss_survey.md).
Indagine rigorosamente in sola lettura sugli header dei safetensors (nessun caricamento di pesi in memoria, nessun uso GPU, nessun render, nessun riavvio/spegnimento).

---

## Step 1 — The Files

Elenco dei file contenenti `moss`, `qwen3.5` o `flux2-vae` presenti nei path di StabilityMatrix (`D:\StabilityMatrix-win-x64\Data\Models` e `C:\StabilityMatrix-win-x64\Data\Models`):

```powershell
Get-ChildItem -Recurse D:\StabilityMatrix-win-x64\Data\Models, C:\StabilityMatrix-win-x64\Data\Models -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match 'moss|qwen3\.5|flux2-vae' } | Select-Object FullName, Length | Format-Table -AutoSize
```

### Output

```text
FullName                                                                                     Length
--------                                                                                     ------
D:\StabilityMatrix-win-x64\Data\Models\DiffusionModels\moss_image_base_bf16.safetensors 10164655808
D:\StabilityMatrix-win-x64\Data\Models\DiffusionModels\moss_image_sft_bf16.safetensors  10164655808
D:\StabilityMatrix-win-x64\Data\Models\TextEncoders\qwen3.5_9b_w4a8_gptq.safetensors     7343591088
D:\StabilityMatrix-win-x64\Data\Models\VAE\flux2-vae_small.safetensors                    249521340
```

* **Target primario `moss_image_sft_bf16.safetensors`**: PRESENTE (`D:\StabilityMatrix-win-x64\Data\Models\DiffusionModels\moss_image_sft_bf16.safetensors`, 10.16 GB).
* **Base build `moss_image_base_bf16.safetensors`**: PRESENTE (10.16 GB).
* **Text encoder `qwen3.5_9b_w4a8_gptq.safetensors`**: PRESENTE (7.34 GB).
* **VAE `flux2-vae_small.safetensors`**: PRESENTE (249.5 MB).

---

## Step 2 — The Survey

Esecuzione dello script deterministico di mappatura:

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python moss_survey.py
```

### Output

```text
moss_dit moss_image_sft_bf16.safetensors 379 tensors {'F32': 1, 'BF16': 378}
moss_dit_base moss_image_base_bf16.safetensors 379 tensors {'F32': 1, 'BF16': 378}
moss_te qwen3.5_9b_w4a8_gptq.safetensors 1579 tensors {'F32': 450, 'BF16': 525, 'F8_E4M3': 200, 'I8': 202, 'U8': 202}
moss_vae flux2-vae_small.safetensors 251 tensors {'I64': 1, 'F32': 250}
krea2_dit krea2_turbo_bf16.safetensors 430 tensors {'F32': 174, 'BF16': 256}
krea2_te qwen3vl_4b_bf16.safetensors 713 tensors {'BF16': 713}
krea2_te qwen3vl_4b_fp8_scaled.safetensors 1217 tensors {'F32': 252, 'BF16': 461, 'F8_E4M3': 252, 'U8': 252}
source comfy\lora.py
source comfy\lora_convert.py
source comfy\model_base.py
source comfy\model_detection.py
source comfy\sd.py
source comfy\supported_models.py
source comfy\text_encoders\moss_image.py
source comfy\ldm\moss_image\model.py
source comfy_extras\nodes_moss_image.py
wrote docs/moss_survey.md
```

### Sintesi Strutturale dei Checkpoint (da Header JSON)

* **`moss_dit` (`moss_image_sft_bf16.safetensors`)**:
  * Dimensioni: 10.16 GB
  * Tensori totali: 379 (378 `BF16`, 1 `F32`)
  * Blocchi: 42 `layers` (0–41), 2 `text_embedder.blocks`, 2 `time_embedding`
  * Pattern: 35 pattern unici
  * Mappa CSV generata: `data/moss_structure_moss_dit_moss_image_sft_bf16.csv`

* **`moss_dit_base` (`moss_image_base_bf16.safetensors`)**:
  * Dimensioni: 10.16 GB
  * Tensori totali: 379 (378 `BF16`, 1 `F32`)
  * Blocchi: 42 `layers` (0–41), 2 `text_embedder.blocks`, 2 `time_embedding`
  * Struttura e dtypes identici alla versione SFT.
  * Mappa CSV generata: `data/moss_structure_moss_dit_base_moss_image_base_bf16.csv`

* **`moss_te` (`qwen3.5_9b_w4a8_gptq.safetensors`)**:
  * Dimensioni: 7.34 GB
  * Tensori totali: 1579 (525 `BF16`, 450 `F32`, 200 `F8_E4M3`, 202 `I8`, 202 `U8`)
  * Blocchi: 32 `model.language_model.layers`, 27 `model.visual.blocks`, 1 `mtp.layers`
  * Mappa CSV generata: `data/moss_structure_moss_te_qwen3.5_9b_w4a8_gptq.csv`

* **`moss_vae` (`flux2-vae_small.safetensors`)**:
  * Dimensioni: 0.25 GB
  * Tensori totali: 251 (250 `F32`, 1 `I64`)
  * Blocchi: 4 up-blocks decoder, 4 down-blocks encoder, mid-block attentions e resnets
  * Mappa CSV generata: `data/moss_structure_moss_vae_flux2-vae_small.csv`

### Sorgenti ComfyUI Copiati in `docs/moss_source/`

1. `comfy/lora.py` -> `docs/moss_source/comfy__lora.py`
2. `comfy/lora_convert.py` -> `docs/moss_source/comfy__lora_convert.py`
3. `comfy/model_base.py` -> `docs/moss_source/comfy__model_base.py`
4. `comfy/model_detection.py` -> `docs/moss_source/comfy__model_detection.py`
5. `comfy/sd.py` -> `docs/moss_source/comfy__sd.py`
6. `comfy/supported_models.py` -> `docs/moss_source/comfy__supported_models.py`
7. `comfy/text_encoders/moss_image.py` -> `docs/moss_source/comfy__text_encoders__moss_image.py`
8. `comfy/ldm/moss_image/model.py` -> `docs/moss_source/comfy__ldm__moss_image__model.py`
9. `comfy_extras/nodes_moss_image.py` -> `docs/moss_source/comfy_extras__nodes_moss_image.py`

Documento di dettaglio generato: [docs/moss_survey.md](moss_survey.md).

---

## Step 3 — Environment Metadata

* **ComfyUI Path**: `D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI`
* **ComfyUI Version (`git -C ... log -1 --oneline`)**:
  ```text
  19ae172bf Add a Branch node (#16383)
  ```
* **Installazione Tuner Arthemy (`ArthemyKrea2ModelTuner` & `ArthemyKrea2CLIPTuner`)**:
  * **Stato**: Installati e presenti
  * **Path cartella custom node**: `D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_Krea2_Tuner`
  * **File di definizione**: `D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_Krea2_Tuner\Arthemy_Krea2_Tuner.py`
  * **Git commit (`git -C ... log -1 --oneline`)**:
    ```text
    dbe83af feat(rotator): add ArthemyKrea2ModelScrambleRotator null-control node
    ```
