# Renders — C66 automatic measures on images already judged (no renders)

## Loader patch note (authorised by Alessandro, 2026-10-17)

1. `tomg-group-umd/CSD-ViT-L` on Hugging Face sets `"model_type": "custom"` in `config.json` without `auto_map`, so `transformers.pipeline` fails with `KeyError: 'custom'`. Its `pytorch_model.bin` is an `open_clip` `ViT-L-14` (`quick_gelu=True`, `proj=None`) state dict (`module.backbone.*`) plus `module.last_layer_style` (`[1024, 768]`), loaded with `strict=True` (`<All keys matched successfully>`).
2. In `t2v_metrics` (`VQAScore(model="clip-flant5-xl")`) under `transformers 4.57`:
   - `CLIPVisionTower` is initialised with `delay_load=True` so `CLIPVisionModel.from_pretrained` runs outside the outer `meta` context of `CLIPT5ForConditionalGeneration.from_pretrained`;
   - `CLIPT5ForConditionalGeneration.resize_token_embeddings` is made a no-op during `mm_utils.load_pretrained_model` (vocab size is already `32100`), preventing `tie_weights()` from overwriting the untied `lm_head.weight` (`mean = 0.1632`) with `shared.weight` (`mean = 7.2145`).

## Step 1 — image list and smoke test

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe metric_validation.py --selftest
```

```text
selftest ok
```

```powershell
C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe metric_validation.py --list
```

```text
657 images, 0 missing []
```

```powershell
C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe metric_validation.py --smoke
```

```text
elf baseline csd (768,) dino (1024,) genre {'comic': 0.051, 'anime': 0.934, 'cartoon': 0.0, 'oil': 0.001, 'render3d': 0.01, 'photo': 0.001, 'watercolor': 0.002} vqa [0.8933353424072266]
elf L00_attn_p1.00 csd (768,) dino (1024,) genre {'comic': 0.044, 'anime': 0.937, 'cartoon': 0.001, 'oil': 0.002, 'render3d': 0.01, 'photo': 0.003, 'watercolor': 0.004} vqa [0.6077163815498352]
elf L00_attn_m1.00 csd (768,) dino (1024,) genre {'comic': 0.104, 'anime': 0.025, 'cartoon': 0.011, 'oil': 0.066, 'render3d': 0.048, 'photo': 0.742, 'watercolor': 0.004} vqa [0.5971271991729736]
```

## Step 2 — the measures

```powershell
C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe metric_validation.py --embed
```

```text
0 / 657
50 / 657
100 / 657
150 / 657
200 / 657
250 / 657
300 / 657
350 / 657
400 / 657
450 / 657
500 / 657
550 / 657
600 / 657
650 / 657
embed ok: 657 images; csd (657, 768) dino (657, 1024) ; vqa 153
```
