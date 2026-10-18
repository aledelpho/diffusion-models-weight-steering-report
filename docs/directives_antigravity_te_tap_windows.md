# Directive for Antigravity — C87, tap windows and single taps of the L06 edit (156 renders: 18 gate + 138 main)

Pre-registration: `docs/prereg_te_tap_windows.md` (committed before this plan).
Script: `experiments/te_tap_windows.py`. Plan: `data/te_tap_windows_plan.csv` (156 rows, already written and
committed — **do not run `--plan`**).
Output folder: `Text2Img\benchmark_te_tap_windows`.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings.
* **If a step fails, stop and paste the output.** Do not change the script, the plan or any result page. Do not commit.
* The node is the same as in C79 (`Krea2ConditioningPush` with `variant="taps"`); nothing to install. ComfyUI must be
  running.
* Use the ComfyUI venv Python: `C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe`
 .

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --selftest
```

Must print `selftest ok`.

## Step 1 — the 18 gate renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --queue --block gate
```

Must print `queued 18`. When ComfyUI's queue is empty:

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --gate
```

It must print `max abs diff 0` on all 18 lines and end with `GATE PASS`. Any other value, or `FAIL`: **stop** and
paste the output.

## Step 2 — the 138 main renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --queue --block main
```

Must print `queued 138`. When ComfyUI's queue is empty:

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --count
```

Must print `expected 156 missing 0 []`.

## Step 3 — automatic distances (GPU, after Step 2)

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_tap_windows.py --analyze
```

Must end with `wrote ... te_tap_windows_metrics.csv rows 162` and `RULE 4 PASS`. If `RULE 4 FAIL`, paste the output
and stop.

## Step 4 — paste back

Write `docs/RENDERS_2026-10-18_te_tap_windows.md` with the exact commands and outputs of Steps 0–3 inside plain
triple-backtick fences, and the number and total size of the files in `Text2Img\benchmark_te_tap_windows`. Do not
edit any other file and do not commit: Claude checks the gates again and commits.
