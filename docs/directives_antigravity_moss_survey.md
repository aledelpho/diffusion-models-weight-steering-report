# Directive for Antigravity — MOSS-Image survey (read-only, no renders)

Written by Claude, 2026-10-25. Script: `experiments/moss_survey.py`. It reads only the headers of the checkpoints (no
weight is loaded, no GPU) and copies ComfyUI's source files that mention MOSS into `docs/moss_source/`.

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI. **No renders.**
* **If a step fails,** stop and paste the output. Do not change the script.

## Step 1 — the files

List, with size, every file whose name contains `moss`, `qwen3.5` or `flux2-vae` under
`D:\StabilityMatrix-win-x64\Data\Models` and `C:\StabilityMatrix-win-x64\Data\Models`:

```powershell
Get-ChildItem -Recurse D:\StabilityMatrix-win-x64\Data\Models, C:\StabilityMatrix-win-x64\Data\Models -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match 'moss|qwen3\.5|flux2-vae' } | Select-Object FullName, Length
```

## Step 2 — the survey

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python moss_survey.py
```

It prints one line per checkpoint and `source ...` lines, and ends with `wrote docs/moss_survey.md`. A `NOT FOUND`
section is allowed: report it.

## Step 3 — also record

* The ComfyUI version (Settings → About, or `git log -1 --oneline` in the ComfyUI folder).
* Whether `ArthemyKrea2ModelTuner` and `ArthemyKrea2CLIPTuner` are installed, and the path of the tuner's folder
  (`custom_nodes`), with `git log -1 --oneline` there.

## Step 4 — paste back and commit

Write `docs/RENDERS_2026-10-25_moss_survey.md` with the outputs of Steps 1–3. Commit it with `docs/moss_survey.md`,
`docs/moss_source/` and `data/moss_structure_*.csv`, message in Italian:

```
MOSS-Image: ricognizione in sola lettura (struttura dei checkpoint e sorgenti di ComfyUI), resoconto di Antigravity
```
