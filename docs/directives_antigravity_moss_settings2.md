# Directive for Antigravity — MOSS-S2 (72 renders, about 1 h 30 min)

Written by Claude, 2026-10-25. Pre-registration: `docs/prereg_moss_settings2.md`. Script:
`experiments/moss_settings2.py`. Plan frozen: `data/moss_settings2_plan.csv` (do **not** run `--plan`). Tuner v4 as in
MOSS-S, no restart needed.

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI; if it needs a restart, ask Alessandro.
* **If a step fails,** stop and paste the output. Do not change the node, the script or the plan.

```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& $PY moss_settings2.py --queue
```

`queued 72` (turbo first, then E25, then R50). When the queue is empty:

```powershell
& $PY moss_settings2.py --count
& $PY moss_settings2.py --analyze
& $PY moss_settings2.py --sheet
```

`expected 72 missing 0 []`; paste every line of `--analyze`. The sheet `_moss_settings2_sheet.jpg` is for Alessandro.

Write `docs/RENDERS_2026-10-25_moss_settings2.md` (outputs, render times per setting) and commit it with
`data/moss_settings2_metrics.csv` and `data/moss_settings2_tests.csv`, message in Italian:

```
MOSS-S2: proporzionalità degli edit a dosi visibili (R50, E25, turbo 10 step euler ed euler a), resoconto di Antigravity
```
