# Directive for Antigravity — C111, "Photo of a tree" (calibration + test; amendment 1)

Pre-registration: `docs/prereg_te_tree.md`. Script: `experiments/te_tree.py` (C109's encoder and calibration, new plan,
gate and analysis). Outputs in `D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_te_tree` and `data/te_tree_*`.
**Run only after Alessandro has authorised the renders.**

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI; if it needs a restart, ask Alessandro.
* **If a step fails, stop and paste the output.** Do not change the script, the perturbations or the plans.
* Do not run `--page` or `--rules`. Do not open or describe the pictures.

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
```

## Step 0 — selftest

`& $PY te_tree.py --selftest` → `selftest ok; 28 cards ...`.

## Step 1 — automatic calibration (ComfyUI running, queue empty; up to about 100 renders)

```powershell
& $PY te_tree.py --calibrate
```

Ends with `calibration done: <a> of 8 pairs reached; <b> in the window`. Report every `UNREACHABLE` / `NONFINITE` line.
If it stops (error or `TIMEOUT`), paste the output; it can be **re-run as is** and resumes from
`data/te_tree_cal_state.json`.

## Step 2 — test plan, gate, main renders

```powershell
& $PY te_tree.py --plan
& $PY te_tree.py --queue --block gate
& $PY te_tree.py --queue --block main
```

`plan rows: <n>`; `queued 1`; `queued <n-1>`. When the queue is empty:

```powershell
& $PY te_tree.py --gate
& $PY te_tree.py --count
& $PY te_tree.py --analyze
```

`--gate` must print `max abs diff 0` and `GATE PASS`; otherwise **stop** and paste. `--count`: `missing 0 []`.
`--analyze` prints the DINOv2 lines; paste them all.

## Step 3 — paste back and commit

Write `docs/RENDERS_2026-10-27_te_tree.md` with the exact commands and outputs of Steps 0–2, the number and size of the
files in `benchmark_te_tree`, and the run time. Commit it with `data/te_tree_cal_state.json`, `data/te_tree_cal_plan.csv`,
`data/te_tree_strengths.csv`, `data/te_tree_plan.csv`, `data/te_tree_metrics.csv` and `data/te_tree_dino_tests.csv`,
message in Italian:

```
C111: calibrazione e render consegnati (albero), dati come prodotti, resoconto di Antigravity
```
