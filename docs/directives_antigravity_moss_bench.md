# Directive for Antigravity — MOSS2, the MOSS bench (84 renders, amendment 2)

**Amendment 2 (2026-10-25).** Working setting: the turbo LoRA at 10 steps with euler (T10), chosen by MOSS-S2; 7
confirmation renders at 50 steps. The plan is regenerated and committed: 84 renders, about 50 minutes. Everything below
holds with these numbers (`queued 84`, `expected 84 missing 0 []`). The LoRA must be at
`D:\StabilityMatrix-win-x64\Data\Models\Lora\Moss\lodestones-8-steps-dmd2-lora.safetensors`; tuner v4.

**Amendment 1 (2026-10-25).** The first run was stopped by Alessandro. New settings: euler, 50 steps, CFG 3; 12
euler_ancestral renders added; V1 changed (`docs/prereg_moss_bench.md`, amendment 1; plan regenerated and committed).
Before Step 1: make sure ComfyUI's queue is empty and move the old pictures aside:
`Rename-Item D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_moss_bench benchmark_moss_bench_stopped`
(if the folder exists). About 170 s per picture, about 50 min in all.

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

## Step 1 — queue (ComfyUI running, queue empty; about 50 min)

```powershell
& $PY moss_bench.py --queue
```

`queued 84`. Wait for the queue to empty (a background wait is fine), then:

```powershell
& $PY moss_bench.py --count
```

`expected 84 missing 0 []`.

## Step 2 — analyze (after the renders; loads DINOv2)

```powershell
& $PY moss_bench.py --analyze
```

It prints V1, V2 and V2r lines, six `floor` lines, twelve `ladder` lines and six `confirm` rows in the metrics file, and writes `data/moss_bench_metrics.csv`
and `data/moss_bench_tests.csv`. If V1 is `FAIL`, report it prominently.

## Step 3 — paste back and commit

Write `docs/RENDERS_2026-10-25_moss_bench.md` with the outputs of Steps 1–2 and the render times. Commit it with the two
data files, message in Italian:

```
MOSS2: banco MOSS (84 render, turbo T10 e 7 conferme a 50 step), riproducibilità, pavimento tra seed e prima scala di sensibilità, resoconto di Antigravity
```

Do not describe the pictures.
