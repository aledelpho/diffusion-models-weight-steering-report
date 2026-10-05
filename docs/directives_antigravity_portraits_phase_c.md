# Directive for Antigravity — portrait preset, phase C (renders authorised by Alessandro on 2026-10-05)

Written by Claude. **Only the 57 renders listed here are authorised. Do not shut down or close
anything; do not use `monitor_and_shutdown.py`.** If a step fails, stop and paste the output; do not
change any script, plan, prompt or preset to make a step pass. The preset is frozen
(`presets/portrait_preset_alessandro.json`, commit 4da5117) and so is the plan
(`data/portraits_preset_plan.csv`, 57 rows). Do **not** regenerate either.

## Step 1 — reproduction check (one render)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python portraits.py --queue-c --first 1
```

When `Text2Img\benchmark_portraits\phase_c\REPRO_D1_dwarf_paladin_baseline_krea2_seed2236067_00001_.png`
exists:

```powershell
python portraits.py --repro-c
```

Must print `REPRO PASS max abs diff 0`. If FAIL, **stop** and paste.

## Step 2 — the 56 renders

```powershell
python portraits.py --queue-c
```

When ComfyUI's queue is empty:

```powershell
python portraits.py --count-c
```

Must print `expected 57 missing 0 [] duplicates 0`.

## Step 3 — the eye page, and nothing else yet

```powershell
python build_portrait_preset_eye_page.py
```

It writes `Text2Img\benchmark_portraits\phase_c\occhio_C52.html`. **Stop here.** Alessandro fills the
page and exports `portrait_preset_eye_alessandro.csv`; Claude commits it. Only after that commit:

## Step 4 — the measurements (after the eye pass is committed)

```powershell
python analyze_portrait_preset.py --features
python analyze_portrait_preset.py --faces
```

`--faces` needs `insightface` (model `buffalo_l`, already in `C:\Users\aless\.insightface\models`),
`onnxruntime-gpu` and `piq`. If `insightface` is missing, `pip install insightface onnxruntime-gpu`
is allowed; nothing else. Do **not** run `--test`; Claude runs it.

## Step 5 — paste back

Write `docs/RENDERS_2026-10-05_portraits_phase_c.md` with the exact commands and outputs of
`--repro-c`, `--count-c`, the eye-page build, `--features` and `--faces` (the last lines, including
`faces ok: N of 56 with a face`), inside plain triple-backtick fences. Do not commit; Claude commits.

## Not authorised

No other renders, no `--test`, no figures, no change to scripts, plan, prompts or preset.
