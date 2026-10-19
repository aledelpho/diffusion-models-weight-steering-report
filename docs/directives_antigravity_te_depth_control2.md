# Directive for Antigravity — C103, deep against early edits matched on the picture (encodes + about 256 renders)

Pre-registration: `docs/prereg_te_depth_control2.md`. Script: `experiments/te_depth_control2.py`. Outputs in
`Text2Img\benchmark_te_depth_control2` and `data/te_depth_control2_*`.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI; if it needs a restart, ask Alessandro.
* **If a step fails, stop and paste the output.** Do not change the script, the plans or any result page. Do not commit.
* Python: `C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe` (below: `PY`).

## Step 0 — selftest and calibration encodes (ComfyUI's queue empty)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& PY te_depth_control2.py --selftest
& PY te_depth_control2.py --encode-cal
```

`selftest ok`; `--encode-cal`: `GATE PASS`, four `done <prompt>` lines, `wrote ...te_depth_control2_cal_plan.csv 100`.
Lines `NONFINITE` are allowed (that rung is dropped); report them.

## Step 1 — calibration renders (ComfyUI running)

```powershell
& PY te_depth_control2.py --queue --block cal
```

`queued 100` (or fewer if rungs were dropped). Wait until ComfyUI's queue is empty.

## Step 2 — strengths and matched conditionings (ComfyUI's queue empty)

```powershell
& PY te_depth_control2.py --calibrate
```

Four `calibrated <prompt>` lines, then `wrote ... and ...te_depth_control2_plan.csv <n>`. `UNREACHABLE` lines are
allowed and expected for some deep conditions; report them all.

## Step 3 — gate and main renders

```powershell
& PY te_depth_control2.py --queue --block gate
```

`queued 12`. When the queue is empty: `& PY te_depth_control2.py --gate` must print 12 lines `max abs diff 0` and
`GATE PASS`; otherwise **stop**. Then:

```powershell
& PY te_depth_control2.py --queue --block main
```

When the queue is empty:

```powershell
& PY te_depth_control2.py --count
& PY te_depth_control2.py --analyze
& PY te_depth_control2.py --page
```

`--count`: `missing 0` for both plans. `--analyze`: `wrote ...metrics.csv <n> and ...dino.npz`. `--page`:
`units <n> -> ...occhio_C103.html`.

## Step 4 — paste back

Write `docs/RENDERS_2026-10-19_te_depth_control2.md` with the exact commands and outputs of Steps 0–3 in plain
triple-backtick fences, all `NONFINITE`/`UNREACHABLE` lines, the number and size of the files in
`Text2Img\benchmark_te_depth_control2`, and the run time. Do not run `--rules`, do not open the blind page, do not edit
any other file, do not commit.
