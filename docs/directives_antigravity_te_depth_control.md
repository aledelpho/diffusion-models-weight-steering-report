# Directive for Antigravity — C102, deep against early text-encoder edits at the same push (encodes + 156 renders)

Pre-registration: `docs/prereg_te_depth_control.md`. Script: `experiments/te_depth_control.py`. Outputs:
`Text2Img\benchmark_te_depth_control` (renders and `conds\*.pt`), `data/te_depth_control_encoder.csv`,
`data/te_depth_control_plan.csv`, `data/te_depth_control_metrics.csv`, `data/te_depth_control_dino.npz`.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI; if it needs a restart, ask Alessandro.
* **If a step fails, stop and paste the output.** Do not change the script, the plan or any result page. Do not commit.
* Python: `C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe`. The `file` variant of the
  conditioning node is already installed (TEP2).

## Step 0 — selftest and encodes (no renders; ComfyUI's queue must be empty)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --selftest
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --encode
```

`--selftest`: `selftest ok`. `--encode` (about 30–45 minutes): `GATE PASS` (elf baseline), then four lines
`done <prompt> {'t1': ..., 't2': ...}`, then `wrote ...te_depth_control_encoder.csv 48` and
`plan rows: 156 (156 if every target was reached)`. Lines starting with `UNREACHABLE` are allowed (the condition is
dropped and the plan is shorter); report them. Any `FAIL`: stop and paste.

## Step 1 — gate renders (ComfyUI running)

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --queue --block gate
```

Must print `queued 3`. When ComfyUI's queue is empty:

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --gate
```

Three lines `max abs diff 0` and `GATE PASS`. Otherwise **stop** and paste.

## Step 2 — main renders

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --queue --block main
```

Must print `queued` followed by the plan size minus 3. When ComfyUI's queue is empty:

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --count
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_depth_control.py --analyze
```

`--count`: `missing 0 []`. `--analyze`: `wrote ...te_depth_control_metrics.csv <n> and ...te_depth_control_dino.npz`.

## Step 3 — paste back

Write `docs/RENDERS_2026-10-19_te_depth_control.md` with the exact commands and outputs of Steps 0–2 in plain
triple-backtick fences, the number and total size of the files in `Text2Img\benchmark_te_depth_control`, and the run
time. Do not run `--rules` (Claude runs it after Alessandro's blind pass), do not edit any other file, do not commit.
