# Directive for Antigravity — C71, style-swap encodes (16 encodes, no images; authorised by Alessandro on 2026-10-12)

Written by Claude. **No image renders. Do not close anything. Do not use `monitor_and_shutdown.py`. Do not change
power or system settings.** If a step fails, stop and paste the output. Do not change the script, the plan or the
node.

Pre-registration: `docs/prereg_te_direction.md`. The plan is frozen (`data/te_direction_plan.csv`, 16 rows): do
**not** run `--plan`.

The C67 node `Krea2ConditioningProbe` is already installed (`custom_nodes\comfyui_krea2_probe`). Nothing to install.
ComfyUI must be running, as for C68.

## Step 1 — gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_direction.py --queue --first 1
```

When `Text2Img\benchmark_te_direction\V1_Original_baseline_again.npz` exists, run:

```powershell
python te_direction.py --gate
```

It must print `identical` and `GATE PASS`. If it prints `FAIL`, **stop** and paste the output.

## Step 2 — the other 15 encodes

```powershell
python te_direction.py --queue
```

When ComfyUI's queue is empty, run:

```powershell
python te_direction.py --count
```

It must print `expected 16 missing 0 []`.

## Step 3 — paste back

Write `docs/RENDERS_2026-10-12_te_direction.md`. Put the exact commands and outputs of Steps 1–2 inside plain
triple-backtick fences, and include the size of `Text2Img\benchmark_te_direction`.

Do not commit; Claude commits. Do **not** run `--analyze`.

## Not authorised

* Image renders.
* `--plan` or `--analyze`.
* Changes to the script, the plan or the node.
* Push.
