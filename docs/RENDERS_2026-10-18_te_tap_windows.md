# Renders & Analysis — C87 tap windows and single taps of the L06 edit

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --selftest
```

```text
selftest ok
```

## Step 1 — the 18 gate renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --queue --block gate
```

```text
queued 18
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --gate
```

```text
D1_dwarf_paladin 2645751 F03 vs C79 taps_local: max abs diff 0
D1_dwarf_paladin 2645751 F08 vs C79 taps_early_mid: max abs diff 0
D1_dwarf_paladin 2645751 B09 vs C79 taps_late: max abs diff 0
D1_dwarf_paladin 3316624 F03 vs C79 taps_local: max abs diff 0
D1_dwarf_paladin 3316624 F08 vs C79 taps_early_mid: max abs diff 0
D1_dwarf_paladin 3316624 B09 vs C79 taps_late: max abs diff 0
E2_elf_rogue 2645751 F03 vs C79 taps_local: max abs diff 0
E2_elf_rogue 2645751 F08 vs C79 taps_early_mid: max abs diff 0
E2_elf_rogue 2645751 B09 vs C79 taps_late: max abs diff 0
E2_elf_rogue 3316624 F03 vs C79 taps_local: max abs diff 0
E2_elf_rogue 3316624 F08 vs C79 taps_early_mid: max abs diff 0
E2_elf_rogue 3316624 B09 vs C79 taps_late: max abs diff 0
O4_halforc_fighter 2645751 F03 vs C79 taps_local: max abs diff 0
O4_halforc_fighter 2645751 F08 vs C79 taps_early_mid: max abs diff 0
O4_halforc_fighter 2645751 B09 vs C79 taps_late: max abs diff 0
O4_halforc_fighter 3316624 F03 vs C79 taps_local: max abs diff 0
O4_halforc_fighter 3316624 F08 vs C79 taps_early_mid: max abs diff 0
O4_halforc_fighter 3316624 B09 vs C79 taps_late: max abs diff 0
GATE PASS
```

## Step 2 — the 138 main renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --queue --block main
```

```text
queued 138
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --count
```

```text
expected 156 missing 0 []
```

## Step 3 — automatic distances

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --analyze
```

```text
analyzed 18/162
analyzed 36/162
analyzed 54/162
analyzed 72/162
analyzed 90/162
analyzed 108/162
analyzed 126/162
analyzed 144/162
analyzed 162/162
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_tap_windows_metrics.csv rows 162
RULE 4 PASS
```

## Benchmark folder size

```text
Text2Img\benchmark_te_tap_windows: 156 files, 224.05 MB (234934553 bytes)
```
