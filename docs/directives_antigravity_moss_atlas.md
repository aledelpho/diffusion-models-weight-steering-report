# Directive for Antigravity — MOSS3, the MOSS atlas (891 renders, about 5 h 30 min; amendments 1-2)

Written by Claude, 2026-10-25. Pre-registration: `docs/prereg_moss_atlas.md`. Script: `experiments/moss_atlas.py`.
Amendment 1: the Krea-2 atlas prompts (blacksmith, rally, close-up) at seed 2718281. Plan frozen: `data/moss_atlas_plan.csv` (do **not** run `--plan`). Settings as MOSS2 (T10 with the DMD2 LoRA). Amendment 2: no 50-step renders in this run. Tuner v4, no restart needed.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. **Do not restart ComfyUI yourself**; if it needs a restart, ask Alessandro.
* **If a step fails,** stop and paste the output. Do not change the node, the script or the plan.
* The run is long: if ComfyUI stops, re-run `--queue` after Alessandro restarts it; existing pictures are skipped.

```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
```

## Step 1 — queue and wait

```powershell
& $PY moss_atlas.py --queue
```

`queued 891`. Wait for the queue to empty (a background wait is fine). Then
`& $PY moss_atlas.py --count` → `expected 891 missing 0 []`.

## Step 2 — analyze and sheets

```powershell
& $PY moss_atlas.py --analyze
& $PY moss_atlas.py --sheets
```

Paste every line of `--analyze`. The sheets go to `D:\StabilityMatrix-win-x64\Data\Images\Text2Img\_moss_atlas\` (six
files; for Alessandro, do not describe them).

## Step 3 — paste back and commit

Write `docs/RENDERS_2026-10-25_moss_atlas.md` (outputs, render time, any interruption). Commit it with
`data/moss_atlas_metrics.csv` and `data/moss_atlas_tests.csv`, message in Italian:

```
MOSS3: atlante MOSS in turbo (891 render, 148 unità x 2 segni x 3 prompt degli atlanti Krea), resoconto di Antigravity
```
