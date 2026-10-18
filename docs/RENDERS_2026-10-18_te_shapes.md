# Analysis — C93 shapes of the push along the dose

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes.py --selftest
```

```text
selftest ok {'straight': ['straight'], 'spiral': ['spiral'], 'wave': ['wave'], 'clip': ['clip'], 'accel': ['spiral', 'accelerating']}
```

## Step 1 — encodes and measures

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes.py --run
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
GATE b L06 MLP 1.00 dwarf vs C67: max rel err 0.000276 (limit 0.000977)
done D1_dwarf_paladin L06_mlp p 184
done D1_dwarf_paladin L06_mlp m 276
done D1_dwarf_paladin L14_mlp p 460
done D1_dwarf_paladin L14_mlp m 552
done D1_dwarf_paladin L28_mlp p 736
done D1_dwarf_paladin L28_mlp m 828
done D1_dwarf_paladin L06_attn p 920
done D1_dwarf_paladin L06_attn m 1012
done D1_dwarf_paladin L14_attn p 1104
done D1_dwarf_paladin L14_attn m 1196
done E2_elf_rogue L06_mlp p 1384
done E2_elf_rogue L06_mlp m 1478
done E2_elf_rogue L14_mlp p 1666
done E2_elf_rogue L14_mlp m 1760
done E2_elf_rogue L28_mlp p 1948
done E2_elf_rogue L28_mlp m 2042
done E2_elf_rogue L06_attn p 2136
done E2_elf_rogue L06_attn m 2230
done E2_elf_rogue L14_attn p 2324
done E2_elf_rogue L14_attn m 2418
done O4_halforc_fighter L06_mlp p 2622
done O4_halforc_fighter L06_mlp m 2724
done O4_halforc_fighter L14_mlp p 2928
done O4_halforc_fighter L14_mlp m 3030
done O4_halforc_fighter L28_mlp p 3234
done O4_halforc_fighter L28_mlp m 3336
done O4_halforc_fighter L06_attn p 3438
done O4_halforc_fighter L06_attn m 3540
done O4_halforc_fighter L14_attn p 3642
done O4_halforc_fighter L14_attn m 3744
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_shapes_trajectories.csv 3744
```

## Benchmark folder size

```text
Text2Img\benchmark_te_shapes: 39 files, 19.98 MB (20946210 bytes)
```

## Run time

```text
26m 19s (1579s)
```
