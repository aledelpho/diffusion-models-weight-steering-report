# Directive for Antigravity — C105, does a fixed edit carry the same change across subjects? (calibration + test)

Pre-registration: `docs/prereg_te_domain_transfer.md`. Script: `experiments/te_domain_transfer.py`. Outputs in
`D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_te_domain_transfer` and `data/te_domain_transfer_*`.

**StabilityMatrix now lives on D:.** Every path below is on D:; the repository is still on C:.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI; if it needs a restart, ask Alessandro.
* **If a step fails, stop and paste the output.** Do not change the script, the plans or any result page. Do not commit.
* **Do not open `occhio_C105.html`** (Alessandro's blind page).

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
```

## Step 0 — selftest

`& $PY te_domain_transfer.py --selftest` → `selftest ok`.

## Step 1 — automatic calibration (ComfyUI running, its queue empty; several hours)

```powershell
& $PY te_domain_transfer.py --calibrate
```

The command encodes, queues the renders itself, waits for them, measures and decides the next strengths; it prints
`round: ...`, `queued ...` per round (three rounds at most), and ends with
`calibration done: <a> of 32 pairs reached; <b> in the window`. `UNREACHABLE` and `NONFINITE` lines are allowed; report
them all. If it stops (error or `TIMEOUT`), paste the output; it can be **re-run as is**: it resumes from
`data/te_domain_transfer_cal_state.json`.

## Step 2 — test plan, gate, main renders

```powershell
& $PY te_domain_transfer.py --plan
& $PY te_domain_transfer.py --queue --block gate
```

`plan rows: <n>`; `queued 6`. When the queue is empty: `& $PY te_domain_transfer.py --gate` must print six lines
`max abs diff 0` (and up to six `(reported)` lines, any value) and `GATE PASS`; otherwise **stop**. Then:

```powershell
& $PY te_domain_transfer.py --queue --block main
```

When the queue is empty:

```powershell
& $PY te_domain_transfer.py --count
& $PY te_domain_transfer.py --analyze
& $PY te_domain_transfer.py --page
```

`missing 0 []`; `wrote ...te_domain_transfer_metrics.csv <n>`; `units <n> -> ...occhio_C105.html`.

## Step 3 — paste back

Write `docs/RENDERS_2026-10-20_te_domain_transfer.md` with the exact commands and outputs of Steps 0–2 in plain
triple-backtick fences, every `UNREACHABLE`/`NONFINITE` line, the number and size of the files in
`benchmark_te_domain_transfer`, and the run time. Do not run `--rules`, do not edit any other file, do not commit.
