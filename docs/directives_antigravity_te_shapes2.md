# Directive for Antigravity — C100, the push's shape with very different prompts and heavier edits (encoder only, no renders)

Pre-registration: `docs/prereg_te_shapes2.md`. Script: `experiments/te_shapes2.py`.
Output: `data/te_shapes2_trajectories.csv` and `Text2Img\benchmark_te_shapes2\*.npz`.

**Start only after TEP2 (`docs/directives_antigravity_te_massive.md`) has finished all its steps, including the paste
back.** ComfyUI does not need to be running for this one (the script loads the text encoder itself), but the GPU must be
free: ComfyUI's queue must be empty.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI.
* **If a step fails, stop and paste the output.** Do not change the script or any result page. Do not commit.

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes2.py --selftest
```

Must print `selftest ok`.

## Step 1 — encodes and measures (about an hour)

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes2.py --run
```

It must print, in order: `GATE PASS` (the elf baseline), `GATE b ... max rel err` below the limit, then one
`done <prompt> <edit> <sign> <rows>` line per trajectory (60 lines: 6 prompts x 5 edits x 2 signs), and finally
`wrote ...te_shapes2_trajectories.csv <rows>`. If any line says `FAIL` or the script stops, paste the output and stop.

## Step 2 — paste back

Write `docs/RENDERS_2026-10-18_te_shapes2.md` with the exact commands and outputs of Steps 0–1 in plain
triple-backtick fences, the number and total size of the files in `Text2Img\benchmark_te_shapes2`, and the run time. Do
not run `--rules` (Claude runs it), do not edit any other file, do not commit.
