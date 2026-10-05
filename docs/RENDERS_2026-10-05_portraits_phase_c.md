# Renders: Portraits Preset Phase C (2026-10-05)

## Commands Run
```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python portraits.py --queue-c --first 1
python portraits.py --repro-c
python portraits.py --queue-c
python portraits.py --count-c
python build_portrait_preset_eye_page.py
python analyze_portrait_preset.py --features
python analyze_portrait_preset.py --faces
```

## Outputs
```text
REPRO PASS max abs diff 0
expected 57 missing 0 [] duplicates 0
written 7
features ok
faces ok: 50 of 56 with a face
```
