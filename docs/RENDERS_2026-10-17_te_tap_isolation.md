# Analysis — C79 12-tap isolation on Qwen3-VL-4B

## Step 1 — count verification

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" experiments\te_tap_isolation.py --count
```

```text
expected 76 missing 0 []
```

## Step 2 — analyze

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" experiments\te_tap_isolation.py --analyze
```

```text
analyzed 12/72
analyzed 24/72
analyzed 36/72
analyzed 48/72
analyzed 60/72
analyzed 72/72
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_tap_isolation_metrics.csv C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_tap_isolation_cells.csv and 6 contact sheets in C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_te_tap_isolation\sheets
```

## Files written

- `data/te_tap_isolation_metrics.csv` (9,761 bytes, 72 rows of per-render metrics: DINOv2, CSD, VQAScore, CLIP top genre, comic prob, RMS)
- `data/te_tap_isolation_cells.csv` (4,014 bytes, 24 cell-level rows comparing local vs early_mid vs late taps)
- 6 contact sheets in `C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_te_tap_isolation\sheets\`:
  - `sheet_L06_D1_dwarf_paladin.jpg` (534,370 bytes)
  - `sheet_L06_E2_elf_rogue.jpg` (450,722 bytes)
  - `sheet_L06_O4_halforc_fighter.jpg` (497,071 bytes)
  - `sheet_L14_D1_dwarf_paladin.jpg` (573,326 bytes)
  - `sheet_L14_E2_elf_rogue.jpg` (481,941 bytes)
  - `sheet_L14_O4_halforc_fighter.jpg` (544,461 bytes)
