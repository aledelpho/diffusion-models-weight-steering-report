# Renders & Analysis — C103 random edits: own direction or the network's?

## Step 0 — selftest and calibration encodes

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control2.py --selftest
```

```text
selftest ok
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control2.py --encode-cal
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
done D1_dwarf_paladin
done S1_rally
done C4_stilllife
done P5_comic_panels
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_depth_control2_cal_plan.csv 132
```

## Step 1 — calibration renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control2.py --queue --block cal
```

```text
queued 132
```

## Step 2 — strengths and matched conditionings

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control2.py --calibrate
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
calibrated D1_dwarf_paladin
calibrated S1_rally
calibrated C4_stilllife
UNREACHABLE P5_comic_panels L09 t
UNREACHABLE P5_comic_panels R09a t
UNREACHABLE P5_comic_panels R09b t
UNREACHABLE P5_comic_panels R09c t
calibrated P5_comic_panels
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_depth_control2_calibration.csv C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_depth_control2_strengths.csv and C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_depth_control2_plan.csv 96 (108 if every target was reached)
```

## Step 3 — gate and main renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control2.py --queue --block gate
```

```text
queued 12
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control2.py --gate
```

```text
D1_dwarf_paladin_C0_krea2_seed2645751_00001_.png: max abs diff 0
D1_dwarf_paladin_C0_krea2_seed3316624_00001_.png: max abs diff 0
D1_dwarf_paladin_C0_krea2_seed2718281_00001_.png: max abs diff 0
S1_rally_C0_krea2_seed2645751_00001_.png: max abs diff 0
S1_rally_C0_krea2_seed3316624_00001_.png: max abs diff 0
S1_rally_C0_krea2_seed2718281_00001_.png: max abs diff 0
C4_stilllife_C0_krea2_seed2645751_00001_.png: max abs diff 0
C4_stilllife_C0_krea2_seed3316624_00001_.png: max abs diff 0
C4_stilllife_C0_krea2_seed2718281_00001_.png: max abs diff 0
P5_comic_panels_C0_krea2_seed2645751_00001_.png: max abs diff 0
P5_comic_panels_C0_krea2_seed3316624_00001_.png: max abs diff 0
P5_comic_panels_C0_krea2_seed2718281_00001_.png: max abs diff 0
GATE PASS
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control2.py --queue --block main
```

```text
queued 84
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control2.py --count
```

```text
te_depth_control2_cal_plan.csv expected 132 missing 0 []
te_depth_control2_plan.csv expected 96 missing 0 []
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control2.py --analyze
```

```text
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_depth_control2_metrics.csv 96 and C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_depth_control2_dino.npz
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control2.py --page
```

```text
units 55 (A 28 B 21 + 6 repeats) -> C:\StabilityMatrix-win-x64\Data\Images\Text2Img\occhio_C103.html
```

## Benchmark folder size

```text
Text2Img\benchmark_te_depth_control2: 388 files, 1984.65 MB (2081054004 bytes)
```

## Run time

```text
2h 09m 43s (7783s)
```
