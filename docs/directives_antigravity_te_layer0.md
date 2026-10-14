# Directive for Antigravity — C77, 7 renders (authorised by Alessandro on 2026-10-14)

Written by Claude.

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings.
* **If a step fails,** stop and paste the output. Do not change the script or the plan.
* **The plan is frozen** (`data/te_layer0_plan.csv`): do **not** run `--plan`.
* **No new node:** the workflow uses only nodes already installed.

Rule and prediction: in the docstring of `experiments/te_layer0.py`, written before any render.

## Step 1 — the gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_layer0.py --queue --first 1
```

When `Text2Img\benchmark_te_layer0\P1_elfbrawler_L00_mlp_m1.00_krea2_seed1618033_00001_.png` exists:

```powershell
python te_layer0.py --gate
```

It must print `max abs diff 0` and `GATE PASS`. If it prints `FAIL`, **stop** and paste.

## Step 2 — the other 6 renders

```powershell
python te_layer0.py --queue
```

When ComfyUI's queue is empty:

```powershell
python te_layer0.py --count
```

It must print `expected 7 missing 0 []`.

## Step 3 — paste back

Write `docs/RENDERS_2026-10-14_te_layer0.md` with the commands and outputs of Steps 1–2, inside plain
triple-backtick fences. **This paste-back is required.** Do not commit; Claude commits.

## Not authorised

* Renders outside the plan.
* `--plan`.
* Changes to the script or the plan.
* Shutting down.
* Push.
