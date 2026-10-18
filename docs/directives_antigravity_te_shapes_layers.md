# Directive for Antigravity — C101, the push's shape at every layer of the text encoder (encoder only, no renders)

Pre-registration: `docs/prereg_te_shapes_layers.md`. Script: `experiments/te_shapes_layers.py`.
Output: `data/te_shapes_layers_trajectories.csv` and `Text2Img\benchmark_te_shapes_layers\*.npz` (about 175 files).

**Start only after C100 (`docs/directives_antigravity_te_shapes2.md`) has finished all its steps, including the paste
back.** ComfyUI does not need to be running (the script loads the text encoder itself), but the GPU must be free:
ComfyUI's queue must be empty. **The run takes about 2.5 hours.**

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI.
* **If a step fails, stop and paste the output.** Do not change the scripts or any result page. Do not commit.

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes_layers.py --selftest
```

Must print `selftest ok`.

## Step 1 — encodes and measures (about 2.5 hours)

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes_layers.py --run
```

It must print, in order: `GATE PASS` (the elf baseline), `GATE b ... max rel err` below the limit, `GATE c PASS`, then
one `done L<nn>_<half> <sign> <rows>` line per trajectory (140 lines: 35 layers x MLP and attention x 2 signs). Among
them, seven `GATE d ... rel err` lines (against C93) must be below their limit. Finally
`wrote ...te_shapes_layers_trajectories.csv <rows>`. If any line says `FAIL` or the script stops, paste the output and
stop.

## Step 2 — figures

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" plot_te_shapes_layers.py
```

Must print five `wrote` lines (`C101_overview.png` and four `C101_grid_*.png` in `Text2Img\_te_shapes`).

## Step 3 — paste back

Write `docs/RENDERS_2026-10-18_te_shapes_layers.md` with the exact commands and outputs of Steps 0–2 in plain
triple-backtick fences, the number and total size of the files in `Text2Img\benchmark_te_shapes_layers`, and the run
time. Do not run `--rules` (Claude runs it), do not edit any other file, do not commit.
