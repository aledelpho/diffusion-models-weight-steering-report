# Renders — C107, 40 renders (species edit transfer)

## Step 0 — check

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_species.py --selftest
```

```text
female rogue human, young adult, smug lopsided smirk, undercut asymmetrical rave
selftest ok
```

## Step 1 — the two gates

```powershell
python te_species.py --queue --first 2
```

```text
queued 2
```

```powershell
python te_species.py --gate
```

```text
EN_plain_krea2_seed2645751_00001_.png vs benchmark_portraits/phase_c/E2_elf_rogue_baseline_krea2_seed2645751_00001_.png: max abs diff 0
EN_L06_krea2_seed2645751_00001_.png vs benchmark_te_characters/E2_elf_rogue_L06_mlp_p1.00_krea2_seed2645751_00001_.png: max abs diff 0
GATE PASS
```

## Step 2 — the other 38 renders

```powershell
python te_species.py --queue
```

```text
queued 38
```

```powershell
python te_species.py --count
```

```text
expected 40 missing 0 []
```

## Benchmark folder size

```text
Text2Img\benchmark_te_species: 40 files, 50.80 MB (53268320 bytes)
```

## Run time and errors

- Start: 2026-10-20 21:40:53
- End:   2026-10-20 22:03:40
- Total run time: 22m 47s (1367s)
- Errors: none
