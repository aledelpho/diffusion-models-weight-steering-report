# Directive for Antigravity — MOSS3, the MOSS atlas (1,335 renders; amendment 3 adds d = +2)

**Amendment 3 (2026-10-25).** The plan now has 1,335 rows: the 891 of the running batch plus 444 at d = +2 (rows
`..._pp`). Let the current queue finish, then run `--queue` again: it queues only the missing pictures (`queued 444`
if the first batch is complete). Then continue from `--count` (`expected 1335 missing 0 []`).

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
`& $PY moss_atlas.py --count` → `expected 1335 missing 0 []`.

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
MOSS3: atlante MOSS in turbo (1335 render, 148 unità x 3 dosi x 3 prompt degli atlanti Krea), resoconto di Antigravity
```
