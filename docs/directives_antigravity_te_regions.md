# Directive for Antigravity — C68, regions of the text-encoder push (no images; authorised by Alessandro on 2026-10-12)

Written by Claude. **No image renders. Do not close anything; do not use `monitor_and_shutdown.py`; do not change
power or system settings.** If a step fails, stop and paste the output; do not change the script, the plan or the
node. Pre-registration: `docs/prereg_te_regions.md`. Plan frozen (`data/te_regions_plan.csv`, 241 rows): do **not**
run `--plan`.

## Step 0 — update the probe node

The node has a new optional input (`taps`; C68 leaves it empty and stores all 12 taps, about 2 GB in total). Copy the repository's version over the installed one and restart
ComfyUI through StabilityMatrix:

```powershell
Copy-Item -Force C:\Users\aless\Desktop\diffusion-models-weight-steering-report\tools\comfyui_krea2_probe\__init__.py `
  C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\comfyui_krea2_probe\__init__.py
```

## Step 1 — the 241 encodes

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_regions.py --queue
```

When ComfyUI's queue is empty:

```powershell
python te_regions.py --count
python te_regions.py --gate
```

`--count` must print `expected 241 missing 0 []`; `--gate` must print `determinism: identical` and `GATE PASS`.
If it prints `FAIL`, **stop** and paste.

## Step 2 — paste back

Write `docs/RENDERS_2026-10-12_te_regions.md` with the exact commands and outputs inside plain triple-backtick
fences, and the size of `Text2Img\benchmark_te_regions` (expected around 2 GB). Do not commit; Claude commits and runs `--analyze`.

## Not authorised

Image renders, `--plan`, `--analyze`, changes to the script, the plan or the node (beyond the copy in Step 0), push.
