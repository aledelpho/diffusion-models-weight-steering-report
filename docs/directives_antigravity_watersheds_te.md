# Directive for Antigravity — C99, minimal text-encoder perturbations (50 renders: 2 gate + 48 main)

Pre-registration: `docs/prereg_watersheds_te.md`. Script: `experiments/watersheds_te.py`. Plan:
`data/watersheds_te_plan.csv` (50 rows, already written and committed — **do not run `--plan`**).
Output folder: `Text2Img\benchmark_watersheds_te`.

**Queue order: start only after C93 (`docs/directives_antigravity_te_shapes.md`) has finished all its steps.**

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings.
* **If a step fails, stop and paste the output.** Do not change the script, the plan or any result page. Do not commit.
* ComfyUI must be running, with the `Krea2ConditioningPush` node as used in C79/C87 (nothing to install). Use the
  ComfyUI venv Python: `C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe`.

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_te.py --selftest
```

Must print `selftest ok`.

## Step 1 — the 2 gate renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_te.py --queue --block gate
```

Must print `queued 2`. When ComfyUI's queue is empty:

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_te.py --gate
```

Must print `max abs diff 0` twice and `GATE PASS`. Otherwise **stop** and paste.

## Step 2 — the 48 main renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_te.py --queue --block main
```

Must print `queued 48`. When ComfyUI's queue is empty:

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" watersheds_te.py --count
```

Must print `expected 50 missing 0 []`.

## Step 3 — paste back

Write `docs/RENDERS_2026-10-18_watersheds_te.md` with the exact commands and outputs of Steps 0–2 in plain
triple-backtick fences, and the number and total size of the files in `Text2Img\benchmark_watersheds_te`. Do not run
`--analyze` (Claude runs it), do not edit any other file, do not commit.
