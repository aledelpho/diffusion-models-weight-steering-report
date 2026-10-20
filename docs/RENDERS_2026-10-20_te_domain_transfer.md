# Renders & Analysis — C105, does a fixed edit carry the same change across subjects? (calibration + test)

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
& $PY te_domain_transfer.py --selftest
```

```text
selftest ok
```

## Step 1 — automatic calibration

```powershell
& $PY te_domain_transfer.py --calibrate
```

```text
round: 128 strengths to render x 2 seeds
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
queued 272

round: 21 strengths to render x 2 seeds
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
queued 42

round: 14 strengths to render x 2 seeds
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
queued 28

UNREACHABLE O4_halforc_fighter R09 closest D 0.13035122883794203
UNREACHABLE G5_gnome_wizard E14 closest D 0.1380414343307662
UNREACHABLE P2_lotuscanoe E14 closest D 0.08588580347863933
calibration done: 29 of 32 pairs reached; 22 in the window
```

## Step 2 — test plan, gate, main renders

```powershell
& $PY te_domain_transfer.py --plan
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
plan rows: 74 (80 if every pair was reached)
```

```powershell
& $PY te_domain_transfer.py --queue --block gate
```

```text
queued 6
```

```powershell
& $PY te_domain_transfer.py --gate
```

```text
D1_dwarf_paladin_C0_krea2_seed2645751_00001_.png: max abs diff 0
D1_dwarf_paladin_C0_krea2_seed3316624_00001_.png: max abs diff 0
S1_rally_C0_krea2_seed2645751_00001_.png: max abs diff 0
S1_rally_C0_krea2_seed3316624_00001_.png: max abs diff 0
C4_stilllife_C0_krea2_seed2645751_00001_.png: max abs diff 0
C4_stilllife_C0_krea2_seed3316624_00001_.png: max abs diff 0
missing E2_elf_rogue_C0_krea2_seed2645751_00001_.png
missing E2_elf_rogue_C0_krea2_seed3316624_00001_.png
missing O4_halforc_fighter_C0_krea2_seed2645751_00001_.png
missing O4_halforc_fighter_C0_krea2_seed3316624_00001_.png
missing G5_gnome_wizard_C0_krea2_seed2645751_00001_.png
missing G5_gnome_wizard_C0_krea2_seed3316624_00001_.png
GATE PASS
```

```powershell
& $PY te_domain_transfer.py --queue --block main
```

```text
queued 68
```

```powershell
& $PY te_domain_transfer.py --count
```

```text
expected 74 missing 0 []
```

```powershell
& $PY te_domain_transfer.py --analyze
```

```text
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_domain_transfer_metrics.csv 58
```

```powershell
& $PY te_domain_transfer.py --page
```

```text
units 17 -> D:\StabilityMatrix-win-x64\Data\Images\Text2Img\occhio_C105.html
```

## Benchmark folder size

```text
Text2Img\benchmark_te_domain_transfer: 416 files, 622.25 MB (652473755 bytes)
```

## Run time

```text
4h 08m 05s (14885s)
```
