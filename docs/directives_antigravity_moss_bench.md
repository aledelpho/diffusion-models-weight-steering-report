# Directive for Antigravity — MOSS2, the MOSS bench (84 renders, about 50 minutes)

Written by Claude, 2026-10-25 (clean version of amendment 2). Pre-registration: `docs/prereg_moss_bench.md`
(amendments 1 and 2). Script: `experiments/moss_bench.py`. Plan frozen: `data/moss_bench_plan.csv` (do **not** run
`--plan`).

**Settings.** 77 renders at **T10**: MOSS-Image SFT bf16 + the DMD2 LoRA
`D:\StabilityMatrix-win-x64\Data\Models\Lora\Moss\lodestones-8-steps-dmd2-lora.safetensors` (strength 1.0), euler,
10 steps, CFG 1 (about 24 s each). 7 confirmation renders at **R50**: no LoRA, euler, 50 steps, CFG 3 (about 170 s
each). The script builds both graphs; nothing to set by hand.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. **Do not restart ComfyUI yourself**; if it needs a restart, ask Alessandro.
* **If a step fails,** stop and paste the output. Do not change the node, the script or the plan.
* ComfyUI must have the MOSS tuner **version 4** installed (as for MOSS-S and MOSS-S2). No restart is needed.

```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
```

## Step 0 — clean start

Make sure ComfyUI's queue is empty. If the folder
`D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_moss_bench` exists (pictures of the stopped first run),
move it aside:

```powershell
Rename-Item D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_moss_bench benchmark_moss_bench_stopped
```

## Step 1 — queue and wait

```powershell
& $PY moss_bench.py --queue
```

It must print `queued 84`. Wait for the queue to empty (a background wait is fine), then:

```powershell
& $PY moss_bench.py --count
```

It must print `expected 84 missing 0 []`.

## Step 2 — analyze (loads DINOv2)

```powershell
& $PY moss_bench.py --analyze
```

Paste every line: one `V1` line, two `V2` and two `V2r` lines, six `floor` lines and twelve `ladder` lines. It writes
`data/moss_bench_metrics.csv` (including six `confirm` rows) and `data/moss_bench_tests.csv`. **If V1 is `FAIL`, say so
at the top of the report.**

## Step 3 — paste back and commit

Write `docs/RENDERS_2026-10-25_moss_bench.md` with the outputs of Steps 0–2 and the render times (T10 and R50
separately). Commit it with the two data files, message in Italian:

```
MOSS2: banco MOSS (84 render, turbo T10 e 7 conferme a 50 step), riproducibilità, pavimento tra seed e prima scala di sensibilità, resoconto di Antigravity
```

Do not open or describe the pictures: the blind confirmation page is written by Claude after the renders.
