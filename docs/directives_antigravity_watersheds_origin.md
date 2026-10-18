# Directive for Antigravity — C97, where pictures are fragile (108 renders: 2 gate + 106 main)

Pre-registration: `docs/prereg_watersheds_origin.md`. Script: `experiments/watersheds_origin.py`. Plan:
`data/watersheds_origin_plan.csv` (108 rows, already written and committed — **do not run `--plan`**).
Output folder: `Text2Img\benchmark_watersheds_origin`.

**Start only after C87 (`docs/directives_antigravity_te_tap_windows.md`) has finished all its steps.**

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings.
* **If a step fails, stop and paste the output.** Do not change the script, the plan or any result page. Do not commit.
* ComfyUI must be running. Use the ComfyUI venv Python:
  `C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe`.

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --selftest
```

Must print `selftest ok`.

## Step 1 — the 2 gate renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --queue --block gate
```

Must print `queued 2`. When ComfyUI's queue is empty:

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --gate
```

Must print `max abs diff 0` twice and `GATE PASS`. Otherwise **stop** and paste.

## Step 2 — the 106 main renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --queue --block main
```

Must print `queued 106`. When ComfyUI's queue is empty:

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --count
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --gate
```

`--count` must print `expected 108 missing 0 []`. `--gate` now also checks the archer's five weight edits at seed
3141592 against the C55/C56 renders: it must print `max abs diff 0` on all seven lines and `GATE PASS`.

## Step 3 — starting noise (no renders)

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_origin.py --noise
```

Must print `wrote ...watersheds_origin_noise.npz` with six arrays of shape `(16, 160, 128)`.

## Step 4 — paste back

Write `docs/RENDERS_2026-10-18_watersheds_origin.md` with the exact commands and outputs of Steps 0–3 in plain
triple-backtick fences, and the number and total size of the files in `Text2Img\benchmark_watersheds_origin`. Do not
run `--analyze` (Claude runs it), do not edit any other file, do not commit.
