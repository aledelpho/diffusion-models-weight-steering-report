# Renders — C99 minimal text-encoder perturbations

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_te.py --selftest
```

```text
selftest ok
```

## Step 1 — the 2 gate renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_te.py --queue --block gate
```

```text
queued 2
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_te.py --gate
```

```text
P3_archerforest seed 3141592 zero vs C97 base: max abs diff 0
D1_dwarf_paladin seed 2645751 zero vs C97 base: max abs diff 0
GATE PASS
```

## Step 2 — the 48 main renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_te.py --queue --block main
```

```text
queued 48
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_te.py --count
```

```text
expected 50 missing 0 []
```

## Benchmark folder size

```text
Text2Img\benchmark_watersheds_te: 50 files, 86.21 MB (90396531 bytes)
```
