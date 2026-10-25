# Directive for Antigravity — MOSS-S, choosing the sampling settings (84 renders, about 2 h)

Written by Claude, 2026-10-25. Pre-registration: `docs/prereg_moss_settings.md`. Script: `experiments/moss_settings.py`.
Plan frozen: `data/moss_settings_plan.csv` (do **not** run `--plan`). **MOSS2 is on hold** until this is read.

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. **Do not restart ComfyUI yourself: ask Alessandro.**
* **If a step fails,** stop and paste the output. Do not change the node, the script or the plan.

```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
```

## Step 0 — stop MOSS2, install tuner v4

1. If MOSS2 is still running, clear ComfyUI's queue (Alessandro may do it from the UI) and wait for the current picture.
2. Copy `..\tools\comfyui_moss_tuner\__init__.py` over
   `D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_MOSS_Tuner\__init__.py`, then **ask Alessandro
   to restart ComfyUI**.
3. Check that the LoRA exists:
   `D:\StabilityMatrix-win-x64\Data\Models\Lora\Moss\lodestones-8-steps-dmd2-lora.safetensors`.

## Step 1 — queue

```powershell
& $PY moss_settings.py --queue
```

`queued 84`. The 28 turbo pictures come first (fast), then E25, then R50. After the **first** turbo picture, read the
ComfyUI log and paste every line mentioning the LoRA (in particular any `lora key not loaded` line) and the
`patches attached` count of the model: if the log says that LoRA keys were not loaded, **stop the queue** and report.

When the queue is empty: `& $PY moss_settings.py --count` → `expected 84 missing 0 []`.

## Step 2 — analyze and sheet

```powershell
& $PY moss_settings.py --analyze
& $PY moss_settings.py --sheet
```

Paste every line. The sheet is `D:\StabilityMatrix-win-x64\Data\Images\Text2Img\_moss_settings_sheet.jpg` (for
Alessandro; do not describe it).

## Step 3 — paste back and commit

Write `docs/RENDERS_2026-10-25_moss_settings.md` with the outputs of Steps 0–2, the LoRA log lines and the render time
per setting. Commit it with `data/moss_settings_metrics.csv` and `data/moss_settings_tests.csv`, message in Italian:

```
MOSS-S: scelta delle impostazioni di campionamento (84 render, R50 / E25 / turbo), resoconto di Antigravity
```
