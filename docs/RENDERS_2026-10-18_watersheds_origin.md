# Renders — C97 where pictures are fragile

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --selftest
```

```text
selftest ok
```

## Step 1 — the 2 gate renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --queue --block gate
```

```text
queued 2
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --gate
```

```text
P3_archerforest seed 3141592 base vs benchmark_hood_threshold/P3_archerforest_baseline_krea2_seed3141592_00001_.png: max abs diff 0
D1_dwarf_paladin seed 2645751 base vs benchmark_portraits/phase_c/D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png: max abs diff 0
GATE PASS
```

## Step 2 — the 106 main renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --queue --block main
```

```text
queued 106
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --count
```

```text
expected 108 missing 0 []
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --gate
```

```text
P3_archerforest seed 3141592 W1 vs benchmark_null_patch/P3_archerforest_N3_blk27_p0.004_krea2_seed3141592_00001_.png: max abs diff 0
P3_archerforest seed 3141592 W2 vs benchmark_null_patch/P3_archerforest_N4_blk27_m0.004_krea2_seed3141592_00001_.png: max abs diff 0
P3_archerforest seed 3141592 W3 vs benchmark_hood_threshold/P3_archerforest_blk00_neg_d0.010_krea2_seed3141592_00001_.png: max abs diff 0
P3_archerforest seed 3141592 W4 vs benchmark_hood_threshold/P3_archerforest_blk10_neg_d0.010_krea2_seed3141592_00001_.png: max abs diff 0
P3_archerforest seed 3141592 W5 vs benchmark_hood_threshold/P3_archerforest_blk23_pos_d0.010_krea2_seed3141592_00001_.png: max abs diff 0
P3_archerforest seed 3141592 base vs benchmark_hood_threshold/P3_archerforest_baseline_krea2_seed3141592_00001_.png: max abs diff 0
D1_dwarf_paladin seed 2645751 base vs benchmark_portraits/phase_c/D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png: max abs diff 0
GATE PASS
```

## Step 3 — starting noise

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --noise
```

```text
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\watersheds_origin_noise.npz {'s3141592': (16, 160, 128), 's2645751': (16, 160, 128), 's1618033': (16, 160, 128), 's2718281': (16, 160, 128), 's3316624': (16, 160, 128), 's4123105': (16, 160, 128)}
```

## Benchmark folder size

```text
Text2Img\benchmark_watersheds_origin: 108 files, 186.09 MB (195134602 bytes)
```
