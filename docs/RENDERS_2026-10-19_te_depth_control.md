# Renders & Analysis — C102 deep against early text-encoder edits at the same push

## Step 0 — selftest and encodes

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --selftest
```

```text
selftest ok
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --encode
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
done D1_dwarf_paladin {'t1': 0.2113, 't2': 0.4968}
done S1_rally {'t1': 0.1967, 't2': 0.4576}
done C4_stilllife {'t1': 0.2242, 't2': 0.5168}
done P5_comic_panels {'t1': 0.2049, 't2': 0.4894}
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_depth_control_encoder.csv 48
plan rows: 156 (156 if every target was reached)
```

## Step 1 — gate renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --queue --block gate
```

```text
queued 3
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --gate
```

```text
D1_dwarf_paladin_C0_krea2_seed2645751_00001_.png vs D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png: max abs diff 0
S1_rally_C0_krea2_seed2718281_00001_.png vs S1_rally_baseline_krea2_seed2718281_00001_.png: max abs diff 0
C4_stilllife_C0_krea2_seed2718281_00001_.png vs C4_stilllife_baseline_krea2_seed2718281_00001_.png: max abs diff 0
GATE PASS
```

## Step 2 — main renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --queue --block main
```

```text
queued 153
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --count
```

```text
expected 156 missing 0 []
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --analyze
```

```text
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_depth_control_metrics.csv 156 and C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_depth_control_dino.npz
```

## Benchmark folder size

```text
Text2Img\benchmark_te_depth_control: 208 files, 802.65 MB (841637411 bytes)
```

## Run time

```text
1h 45m 42s (6342s)
```
