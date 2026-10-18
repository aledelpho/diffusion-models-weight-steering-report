# Directive for Antigravity — TEP2, L06 and the massive activations (encodes + 25 renders)

Pre-registration: `docs/prereg_te_massive.md`. Script: `experiments/te_massive.py`. Plan: `data/te_massive_plan.csv`
(25 rows, already committed — **do not run `--plan`**). Outputs: `Text2Img\benchmark_te_massive` (renders and
`conds\*.pt`), `data/te_massive_encoder.csv`, `data/te_massive_metrics.csv`.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI yourself: Step 1 asks Alessandro to do it.
* **If a step fails, stop and paste the output.** Do not change the script, the plan, the node or any result page. Do
  not commit.
* Python: `C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe`.

## Step 0 — selftest and encodes (no renders; the GPU must be free)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --selftest
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --encode
```

`--selftest` must print `selftest ok`. `--encode` must print `GATE PASS` (elf baseline), then three lines
`done <character>: massive entries <n> on tokens [...]`, then `wrote ...te_massive_encoder.csv`, and must have written
15 files in `Text2Img\benchmark_te_massive\conds\`. Any `FAIL`: stop and paste.

## Step 1 — the updated node (Alessandro)

Copy `tools\comfyui_krea2_condpush\__init__.py` over
`C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\comfyui_krea2_condpush\__init__.py` (it adds the
variant `file`). Then **ask Alessandro to restart ComfyUI** and wait for his confirmation before Step 2.

## Step 2 — the gate renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --queue --block gate
```

Must print `queued 2`. When ComfyUI's queue is empty:

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --gate
```

Must print `max abs diff 0` twice (the saved plain conditioning against the phase_c baseline; the saved C1 against the
`benchmark_te_characters` L06 render) and `GATE PASS`. Otherwise **stop** and paste.

## Step 3 — the 23 main renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --queue --block main
```

Must print `queued 23`. When ComfyUI's queue is empty:

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --count
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --gate
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_massive.py --analyze
```

`--count`: `expected 25 missing 0 []`. `--gate`: seven lines `max abs diff 0` (the plain gate and the six C1 renders)
and `GATE PASS`. `--analyze`: `wrote ...te_massive_metrics.csv 24`.

## Step 4 — paste back

Write `docs/RENDERS_2026-10-18_te_massive.md` with the exact commands and outputs of Steps 0–3 in plain
triple-backtick fences, and the number and total size of the files in `Text2Img\benchmark_te_massive`. Do not run
`--rules` (Claude runs it), do not edit any other file, do not commit.
