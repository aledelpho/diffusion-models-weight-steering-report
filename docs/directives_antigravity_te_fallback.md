# Directive for Antigravity — C73, 29 renders (authorised by Alessandro on 2026-10-13)

Written by Claude.

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings.
* **If a step fails,** stop and paste the output. Do not change the script or the plan.
* **The plan is frozen** (`data/te_fallback_plan.csv`): do **not** run `--plan`.
* **No new node:** the workflow uses only nodes already installed.

Pre-registration: `docs/prereg_te_fallback.md`.

## Step 1 — the gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_fallback.py --queue --first 1
```

When `Text2Img\benchmark_te_fallback\D1_dwarf_paladin_withstyle_repro_krea2_seed2645751_00001_.png` exists:

```powershell
python te_fallback.py --gate
```

It must print `max abs diff 0` and `GATE PASS`. If it prints `FAIL`, **stop** and paste.

## Step 2 — the other 28 renders

```powershell
python te_fallback.py --queue
```

When ComfyUI's queue is empty:

```powershell
python te_fallback.py --count
```

It must print `expected 29 missing 0 []`.

## Step 3 — paste back

Write `docs/RENDERS_2026-10-13_te_fallback.md` with:

* the commands and outputs of Steps 1–2, inside plain triple-backtick fences;
* the size of `Text2Img\benchmark_te_fallback`.

**This paste-back is required.** Last time it was missing. Do not commit; Claude commits.

## Not authorised

* Renders outside the plan.
* `--plan`.
* Changes to the script or the plan.
* Shutting down.
* Push.
