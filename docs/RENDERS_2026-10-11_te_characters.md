# C65 renders — unattended night run

```
night run finished 2026-10-12T03:11:50

$ python te_characters.py --count
expected 531 missing 0 [] | reused baselines missing 0

$ python te_characters.py --repro
REPRO D1_dwarf_paladin PASS max abs diff 0
REPRO V1_Original PASS max abs diff 0
null L35 (reported): 7 renders, max abs diff [0, 0, 0, 0, 0, 0, 0]

$ python te_characters.py --page
40 sheets, 46 showings -> C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_te_characters\eye_test\eye_test.html
```

## Step 1 & 2 logs (before night watchdog)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_characters.py --count
```

```text
expected 531 missing 531 ['D1_dwarf_paladin_REPRO_baseline_krea2_seed2645751_00001_.png', 'V1_Original_REPRO_baseline_krea2_seed3141592_00001_.png', 'D1_dwarf_paladin_CHK_null_L35_both_p1.00_krea2_seed2645751_00001_.png', 'E2_elf_rogue_CHK_null_L35_both_p1.00_krea2_seed2645751_00001_.png', 'O4_halforc_fighter_CHK_null_L35_both_p1.00_krea2_seed2645751_00001_.png'] | reused baselines missing 0
```

```powershell
python te_characters.py --queue --first 2
```

```text
queued 2
```

```powershell
python te_characters.py --repro
```

```text
REPRO D1_dwarf_paladin PASS max abs diff 0
REPRO V1_Original PASS max abs diff 0
```

```powershell
python te_characters.py --queue
```

```text
queued 529
```
