# Directive for Antigravity — C109, 12 light text-encoder presets (calibration + test)

Pre-registration: `docs/prereg_te_light_presets.md`. Script: `experiments/te_light_presets.py` (C105's script with 12
presets in place of its four perturbations). Outputs in
`D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_te_light_presets` and `data/te_light_presets_*`.
Authorised by Alessandro on 2026-10-22.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI; if it needs a restart, ask Alessandro.
* **If a step fails, stop and paste the output.** Do not change the script, the presets or the plans.
* Do not run `--page` or `--rules` (they are written by Claude after the renders).

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
```

## Step 0 — selftest

`& $PY te_light_presets.py --selftest` → `selftest ok`.

## Step 1 — automatic calibration (ComfyUI running, its queue empty; many hours, up to about 1,000 renders)

```powershell
& $PY te_light_presets.py --calibrate
```

It encodes, queues, waits, measures and decides by itself; it prints `round: ...` and `queued ...` per round (three
rounds at most) and ends with `calibration done: <a> of 96 pairs reached; <b> in the window`. `UNREACHABLE` and
`NONFINITE` lines are allowed; report them all. If it stops (error or `TIMEOUT`), paste the output; it can be **re-run as
is** and resumes from `data/te_light_presets_cal_state.json`.

## Step 2 — test plan, gate, main renders

```powershell
& $PY te_light_presets.py --plan
& $PY te_light_presets.py --queue --block gate
```

`plan rows: <n>`; `queued 6`. When the queue is empty, `& $PY te_light_presets.py --gate` must print six lines
`max abs diff 0` (plus up to six `(reported)` lines, any value) and `GATE PASS`; otherwise **stop**. Then:

```powershell
& $PY te_light_presets.py --queue --block main
```

When the queue is empty:

```powershell
& $PY te_light_presets.py --count
& $PY te_light_presets.py --analyze
```

`missing 0 []`; `wrote ...te_light_presets_metrics.csv <n>`.

## Step 3 — paste back and commit

Write `docs/RENDERS_2026-10-22_te_light_presets.md` with the exact commands and outputs of Steps 0–2, every
`UNREACHABLE`/`NONFINITE` line, the number and size of the files in `benchmark_te_light_presets`, and the run time.
Commit that file together with `data/te_light_presets_cal_state.json`, `data/te_light_presets_cal_plan.csv`,
`data/te_light_presets_strengths.csv`, `data/te_light_presets_plan.csv` and `data/te_light_presets_metrics.csv`, message
in Italian:

```
C109: calibrazione e render consegnati (preset leggeri), dati come prodotti, resoconto di Antigravity
```

Do not open or describe the pictures.
