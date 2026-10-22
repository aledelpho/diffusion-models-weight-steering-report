# Renders & Analysis — C109, 12 light text-encoder presets (calibration + test)

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
& $PY te_light_presets.py --selftest
```

```text
selftest ok
```

## Step 1 — automatic calibration

```powershell
& $PY te_light_presets.py --calibrate
```

```text
round: 384 strengths to render x 2 seeds
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
queued 784

round: 54 strengths to render x 2 seeds
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
queued 108

round: 42 strengths to render x 2 seeds
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
queued 84

UNREACHABLE D1_dwarf_paladin P10 closest D 0.11197548122801076
UNREACHABLE E2_elf_rogue P04 closest D 0.106418937102712
UNREACHABLE E2_elf_rogue P12 closest D 0.14503551117014318
UNREACHABLE C4_stilllife P04 closest D 0.13942360617638322
UNREACHABLE C4_stilllife P12 closest D 0.14408026292550502
UNREACHABLE P2_lotuscanoe P04 closest D 0.03847625223827644
UNREACHABLE P2_lotuscanoe P07 closest D 0.10799820359207357
UNREACHABLE P2_lotuscanoe P08 closest D 0.11682220584585795
UNREACHABLE P2_lotuscanoe P09 closest D 0.14203962837148437
UNREACHABLE P2_lotuscanoe P12 closest D 0.06061486384415604
UNREACHABLE LN P04 closest D 0.08997730719041686
UNREACHABLE LN P12 closest D 0.11693154089417046
calibration done: 84 of 96 pairs reached; 61 in the window
```

## Step 2 — test plan, gate, main renders

```powershell
& $PY te_light_presets.py --plan
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
plan rows: 184 (208 if every pair was reached)
```

```powershell
& $PY te_light_presets.py --queue --block gate
```

```text
queued 6
```

```powershell
& $PY te_light_presets.py --gate
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
& $PY te_light_presets.py --queue --block main
```

```text
queued 178
```

```powershell
& $PY te_light_presets.py --count
```

```text
expected 184 missing 0 []
```

```powershell
& $PY te_light_presets.py --analyze
```

```text
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_light_presets_metrics.csv 168
```

## Benchmark folder size

```text
Text2Img\benchmark_te_light_presets: 1160 files, 1738.13 MB (1822563854 bytes)
```

## Run time

```text
12h 12m 35s (43955s)
```
