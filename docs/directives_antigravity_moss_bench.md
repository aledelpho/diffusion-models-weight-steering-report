# Directive for Antigravity — MOSS2, the MOSS bench (89 renders, amendment 1)

**Amendment 1 (2026-10-25).** The first run was stopped by Alessandro. New settings: euler, 50 steps, CFG 3; 12
euler_ancestral renders added; V1 changed (`docs/prereg_moss_bench.md`, amendment 1; plan regenerated and committed).
Before Step 1: make sure ComfyUI's queue is empty and move the old pictures aside:
`Rename-Item D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_moss_bench benchmark_moss_bench_stopped`
(if the folder exists). About 170 s per picture, about 4 h 10 min in all.

Written by Claude, 2026-10-25. Pre-registration: `docs/prereg_moss_bench.md`. Script: `experiments/moss_bench.py`.
Plan frozen: `data/moss_bench_plan.csv` (do **not** run `--plan`).

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI; if it needs a restart, ask Alessandro.
* **If a step fails,** stop and paste the output. Do not change the node, the script or the plan.
* ComfyUI must have the MOSS tuner **version 3** installed (as after MOSS1).

```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
```

## Step 1 — queue (ComfyUI running, queue empty; about 4 h 10 min)

```powershell
& $PY moss_bench.py --queue
```

`queued 89`. Wait for the queue to empty (a background wait is fine), then:

```powershell
& $PY moss_bench.py --count
```

`expected 89 missing 0 []`.

## Step 2 — analyze (after the renders; loads DINOv2)

```powershell
& $PY moss_bench.py --analyze
```

It prints V1, V2 and V2r lines, six `floor` lines, one `euler_ancestral` line and twelve `ladder` lines, and writes `data/moss_bench_metrics.csv`
and `data/moss_bench_tests.csv`. If V1 is `FAIL`, report it prominently.

## Step 3 — paste back and commit

Write `docs/RENDERS_2026-10-25_moss_bench.md` with the outputs of Steps 1–2 and the render times. Commit it with the two
data files, message in Italian:

```
MOSS2: banco MOSS (89 render), riproducibilità, pavimento tra seed e prima scala di sensibilità, resoconto di Antigravity
```

Do not describe the pictures.
