# Encodes - C68 regions of the text-encoder push

## Step 0 — update the probe node

```powershell
Copy-Item -Force C:\Users\aless\Desktop\diffusion-models-weight-steering-report\tools\comfyui_krea2_probe\__init__.py `
  C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\comfyui_krea2_probe\__init__.py
```

## Step 1 — the 241 encodes

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_regions.py --queue
```

```text
queued 241
```

```powershell
python te_regions.py --count
```

```text
expected 241 missing 0 []
```

```powershell
python te_regions.py --gate
```

```text
determinism: identical
agreement with the C67 diff files (10 edits, all taps): max |rel - rel_C67| = 0.000324 (limit 0.000977)
GATE PASS
```

## Benchmark folder size

```text
Text2Img\benchmark_te_regions: 241 files, 1770.90 MB (1.729 GB, 1856920308 bytes)
```
