# Directive for Antigravity — MOSS1: install the MOSS tuner and run its three gates (6 renders)

Written by Claude, 2026-10-25. Authorised by Alessandro ("Procedi"). Reading: `docs/moss_structure_reading.md`.
Node: `tools/comfyui_moss_tuner/__init__.py` (a new node; the Krea-2 tuner is not touched). Script:
`experiments/moss_gate.py`.

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. **Do not restart ComfyUI yourself: ask Alessandro** (Step 1 needs one restart).
* **If a step fails,** stop and paste the output. Do not change the node, the script or the gates.

```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
```

## Step 1 — install the node

```powershell
New-Item -ItemType Directory -Force D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_MOSS_Tuner | Out-Null
Copy-Item ..\tools\comfyui_moss_tuner\__init__.py D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\Arthemy_MOSS_Tuner\__init__.py
```

Then **ask Alessandro to restart ComfyUI** and wait for his confirmation. Check that the log shows no import error for
`Arthemy_MOSS_Tuner`.

## Step 2 — gate B (no server needed; loads the text encoder on its own)

```powershell
& $PY moss_gate.py --quant
```

Six lines `max relative error ...`, one line `conditioning with '{}' bit-identical: True ...`, then `GATE B PASS`.
If `FAIL`, **stop**. (If it fails for lack of memory while ComfyUI holds the GPU, report it: it can be re-run with
ComfyUI idle.)

## Step 3 — gates A and C (ComfyUI running, queue empty)

```powershell
& $PY moss_gate.py --queue
```

Six lines with a prompt id. When the queue is empty (six files in
`D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_moss_gate`):

```powershell
& $PY moss_gate.py --renders
```

It must print `GATE A PASS` and `GATE C PASS`.

## Step 4 — paste back and commit

Write `docs/RENDERS_2026-10-25_moss_gates.md` with the outputs of Steps 1–3, the render time per picture, and the GPU
memory if visible. Commit it, message in Italian:

```
MOSS1: nodo MOSS installato e cancelli A, B, C eseguiti, resoconto di Antigravity
```

Do not describe the pictures.
