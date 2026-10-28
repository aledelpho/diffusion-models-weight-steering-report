# Directive for Antigravity — C113, dose ladders (2 prompts × 4 edits × 3 new levels × 8 seeds)

Pre-registration: `docs/prereg_te_dose2.md`. Script: `experiments/te_dose2.py`. Outputs in
`D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_te_dose2` and `data/te_dose2_*`. Level 1 and the plain
pictures are read from `benchmark_te_settings` (do not move or rename it). Authorised by Alessandro on 2026-10-28.
194 renders, about 1 hour 45 minutes.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI; if it needs a restart, ask Alessandro.
* **If a step fails, stop and paste the output.** Do not change the script, the prompts, the doses or the plan.
* Do not run `--page` or `--rules`. Do not open or describe the pictures.

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
& $PY te_dose2.py --selftest
& $PY te_dose2.py --plan
& $PY te_dose2.py --queue --block gate
```

`selftest ok; 40 cards (+4 repeats)`; `plan rows: 194 (194 expected)` (report any `NONFINITE` line); `queued 2`. When
the queue is empty:

```powershell
& $PY te_dose2.py --gate
```

Two lines `max abs diff 0` and `GATE PASS`; otherwise **stop**. Then:

```powershell
& $PY te_dose2.py --queue --block main
```

`queued 192`. When the queue is empty:

```powershell
& $PY te_dose2.py --count
& $PY te_dose2.py --analyze
```

`--count`: `missing 0 []` and `reused from C112: 80 missing 0`. Paste every `--analyze` line.

## Paste back and commit

Write `docs/RENDERS_2026-10-28_te_dose2.md` with the commands and outputs, the number and size of the files in
`benchmark_te_dose2` and the run time. Commit it with `data/te_dose2_plan.csv` and `data/te_dose2_dino.csv`, message in
Italian:

```
C113: render consegnati (scale di dose), dati come prodotti, resoconto di Antigravity
```
