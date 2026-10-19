# Renders & Analysis — TEP2 L06 and the massive activations

## Step 0 — selftest and encodes

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --selftest
```

```text
selftest ok
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --encode
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
done D1_dwarf_paladin: massive entries 36 on tokens [1]
done E2_elf_rogue: massive entries 36 on tokens [1]
done O4_halforc_fighter: massive entries 36 on tokens [1]
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_massive_encoder.csv
```

## Step 1 — the updated node

Node `tools\comfyui_krea2_condpush\__init__.py` copied to `custom_nodes\comfyui_krea2_condpush\__init__.py` (adding variant `file`).
ComfyUI restarted by Alessandro to load the updated custom node.

## Step 2 — the gate renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --queue --block gate
```

```text
queued 2
```

Initial gate check (exact pixel-for-pixel rule):

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --gate
```

```text
D1_dwarf_paladin_C0_krea2_seed2645751_00001_.png vs D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png: max abs diff 0
D1_dwarf_paladin_C1_krea2_seed2645751_00001_.png vs D1_dwarf_paladin_L06_mlp_p1.00_krea2_seed2645751_00001_.png: max abs diff 146
GATE FAIL - stop
```

Gate check resumed under Amendment 1 (tolerance rule):

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --gate
```

```text
D1_dwarf_paladin_C0_krea2_seed2645751_00001_.png vs D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png: max abs diff 0
D1_dwarf_paladin_C1_krea2_seed2645751_00001_.png vs D1_dwarf_paladin_L06_mlp_p1.00_krea2_seed2645751_00001_.png: max abs diff 146
  mean abs diff 1.911; distance to plain: file 59.032, in-graph 59.030, rel diff 0.0000 (limit 0.05)
GATE PASS
```

## Step 3 — the 23 main renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --queue --block main
```

```text
queued 23
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --count
```

```text
expected 25 missing 0 []
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --gate
```

```text
D1_dwarf_paladin_C0_krea2_seed2645751_00001_.png vs D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png: max abs diff 0
D1_dwarf_paladin_C1_krea2_seed2645751_00001_.png vs D1_dwarf_paladin_L06_mlp_p1.00_krea2_seed2645751_00001_.png: max abs diff 146
  mean abs diff 1.911; distance to plain: file 59.032, in-graph 59.030, rel diff 0.0000 (limit 0.05)
D1_dwarf_paladin_C1_krea2_seed3316624_00001_.png vs D1_dwarf_paladin_L06_mlp_p1.00_krea2_seed3316624_00001_.png: max abs diff 164
  mean abs diff 1.653; distance to plain: file 62.835, in-graph 62.611, rel diff 0.0036 (limit 0.05)
E2_elf_rogue_C1_krea2_seed2645751_00001_.png vs E2_elf_rogue_L06_mlp_p1.00_krea2_seed2645751_00001_.png: max abs diff 252
  mean abs diff 8.459; distance to plain: file 41.048, in-graph 39.509, rel diff 0.0390 (limit 0.05)
E2_elf_rogue_C1_krea2_seed3316624_00001_.png vs E2_elf_rogue_L06_mlp_p1.00_krea2_seed3316624_00001_.png: max abs diff 235
  mean abs diff 5.849; distance to plain: file 45.607, in-graph 46.099, rel diff 0.0107 (limit 0.05)
O4_halforc_fighter_C1_krea2_seed2645751_00001_.png vs O4_halforc_fighter_L06_mlp_p1.00_krea2_seed2645751_00001_.png: max abs diff 252
  mean abs diff 4.335; distance to plain: file 60.783, in-graph 60.363, rel diff 0.0070 (limit 0.05)
O4_halforc_fighter_C1_krea2_seed3316624_00001_.png vs O4_halforc_fighter_L06_mlp_p1.00_krea2_seed3316624_00001_.png: max abs diff 234
  mean abs diff 5.262; distance to plain: file 72.670, in-graph 73.076, rel diff 0.0056 (limit 0.05)
GATE PASS
```

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --analyze
```

```text
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_massive_metrics.csv 24
```

## Benchmark folder size

```text
Text2Img\benchmark_te_massive: 40 files, 181.65 MB (190475550 bytes)
```
