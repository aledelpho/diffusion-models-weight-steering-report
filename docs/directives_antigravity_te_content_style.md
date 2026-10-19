# Directive for Antigravity — C104, CSD style vectors of C103's renders (no renders)

Pre-registration: `docs/prereg_te_content_style.md`. Script: `experiments/te_content_style.py`. One GPU step, a few
minutes; ComfyUI's queue must be empty.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI.
* **Do not open `occhio_C104.html`** (Alessandro's blind page). If a step fails, stop and paste. Do not commit.

## Step 1

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
& $PY te_content_style.py --selftest
& $PY te_content_style.py --csd
```

`selftest ok`, then `wrote ...te_content_style_csd.npz 96`.

## Step 2 — paste back

Write `docs/RENDERS_2026-10-19_te_content_style.md` with the commands and outputs in plain triple-backtick fences. Do not
run `--rules`, do not edit any other file, do not commit.
