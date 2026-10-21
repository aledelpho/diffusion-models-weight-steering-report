# Renders — C108, 96 renders (gender swap vs L06 edit)

## Step 0 — check

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_gender.py --selftest
```

```text
Western comics style, portrait of a female human.
Western comics style. Comic book page layout, single image divided into four equal rectangular panels by thick bold black borders, a close-up portrait in each panel. Panel 1 (Top Left): non-binary rogue wood elf, young adult, smug lopsided  ... 181 words
selftest ok
```

## Step 1 — the two gates

```powershell
python te_gender.py --queue --first 2
```

```text
queued 2
```

```powershell
python te_gender.py --gate
```

```text
A_D1_orig_plain_krea2_seed2645751_00001_.png vs benchmark_portraits/phase_c/D1_dwarf_paladin_baseline_krea2_seed2645751_00001_.png: max abs diff 0
A_D1_orig_L06_krea2_seed2645751_00001_.png vs benchmark_te_characters/D1_dwarf_paladin_L06_mlp_p1.00_krea2_seed2645751_00001_.png: max abs diff 0
GATE PASS
```

## Step 2 — the other 94 renders

```powershell
python te_gender.py --queue
```

```text
queued 94
```

```powershell
python te_gender.py --count
```

```text
expected 96 missing 0 []
```

## Benchmark folder size

```text
Text2Img\benchmark_te_gender: 96 files, 132.56 MB (139003100 bytes)
```

## Run time and errors

- Start: 2026-10-21 14:35:34
- End:   2026-10-21 15:30:55
- Total run time: 55m 21s (3321s)
- Errors: none
