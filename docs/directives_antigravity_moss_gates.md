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

**Third resume note (2026-10-25).** Your diagnosis is right: `CLIP.clone()` kept the old `cond_stage_model`, so the
text-encoder edit was never used and the mismatch moved the picture (mean 5.2). Node version 3 encodes with the patcher's
own model. Gate C now compares each edit with `empty_json` (same route). To do: copy the node again, **ask Alessandro to
restart ComfyUI**, rename `benchmark_moss_gate` to `benchmark_moss_gate_v2`, re-run Step 2 and Step 3. If gate A still
fails only on `empty_json`, report the pairwise table as you did: it would mean the non-dynamic text-encoder route
itself changes the conditioning.

**Second resume note (2026-10-25).** Gate A passed; gate C failed (mean 0.0): with dynamic VRAM,
ComfyUI ignored the object patches (your diagnosis, confirmed). Node version 2 always works on a non-dynamic clone.
To do: (1) copy the new `tools/comfyui_moss_tuner/__init__.py` over the installed one (Step 1, copy only) and **ask
Alessandro to restart ComfyUI**; (2) move the six old gate renders aside, so that the queue renders them again:
`Rename-Item D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_moss_gate benchmark_moss_gate_v1`;
(3) re-run Step 2 (gate B; its output was missing from the last report, paste it this time) and Step 3 (gates A and C). Gate A's "tuners with '{}'" now checks that the non-dynamic route
alone changes nothing. If RAM or VRAM runs out (the non-dynamic clone reloads the weights), stop and report.

**Resume note (2026-10-25).** Steps 1 is done (both nodes registered, no import error). Gate B failed on a bug in the
gate script, not in the node: the script looked for `language_model.` only, while ComfyUI names the encoder's
parameters `qwen35_9b.transformer.model.layers...`. Fixed in `experiments/moss_gate.py` (same anchors as the node). The
node is unchanged, so **no restart is needed: resume from Step 2.**

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
