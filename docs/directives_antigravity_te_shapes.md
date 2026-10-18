# Directive for Antigravity — C93, shapes of the push along the dose (encoder only, no renders)

Pre-registration: `docs/prereg_te_shapes.md`. Script: `experiments/te_shapes.py`.
Output: `data/te_shapes_trajectories.csv` and `Text2Img\benchmark_te_shapes\*.npz`.

**Start only after C97 (`docs/directives_antigravity_watersheds_origin.md`) has finished all its steps.** ComfyUI does
not need to be running (the script loads the text encoder itself), but the GPU must be free.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings.
* **If a step fails, stop and paste the output.** Do not change the script or any result page. Do not commit.

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes.py --selftest
```

Must print `selftest ok` followed by the five synthetic shapes.

## Step 1 — encodes and measures

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes.py --run
```

It must print, in order: `GATE PASS` (the elf baseline, bit-identical), `GATE b ... max rel err` below the limit,
then one `done <character> <edit> <sign> <rows>` line per trajectory (30 lines), and finally
`wrote ...te_shapes_trajectories.csv <rows>`. If any line says `FAIL` or the script stops, paste the output and stop.

## Step 2 — paste back

Write `docs/RENDERS_2026-10-18_te_shapes.md` with the exact commands and outputs of Steps 0–1 in plain
triple-backtick fences, the size of `Text2Img\benchmark_te_shapes`, and the run time. Do not run `--rules` (Claude runs
it), do not edit any other file, do not commit.
