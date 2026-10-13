# Directive for Antigravity — C74, 199 renders (amendment 1: +126) (authorised by Alessandro on 2026-10-13)

Written by Claude.

**Rules:**

* Do not close anything. Do not use `monitor_and_shutdown.py`, do not shut the PC down, and do not change power or
  system settings.
* If a step fails, stop and paste the output. Do not change the script or the plan.
* The plan is frozen (`data/te_dose_plan.csv`, 199 rows after amendment 1): do **not** run `--plan`.
* No new node is needed.

Pre-registration: `docs/prereg_te_dose.md`.

## Step 1 — the gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_dose.py --queue --first 1
```

When `Text2Img\benchmark_te_dose\D1_dwarf_paladin_L06_mlp_p1.00_krea2_seed2645751_00001_.png` exists, run:

```powershell
python te_dose.py --gate
```

It must print `max abs diff 0` and `GATE PASS`. If it prints `FAIL`, **stop** and paste.

## Step 2 — all the other renders (also after amendment 1)

```powershell
python te_dose.py --queue
```

When ComfyUI's queue is empty, run:

```powershell
python te_dose.py --count
```

It must print `expected 199 missing 0 []`. If the first round was already running, simply run `--queue` again
when ComfyUI is idle: it skips every image that already exists and queues only the 126 new doses.

## Step 3 — paste back (required)

Write `docs/RENDERS_2026-10-13_te_dose.md` with:

* the commands and outputs of Steps 1–2, inside plain triple-backtick fences;
* the size of `Text2Img\benchmark_te_dose`.

Do not commit; Claude commits.

## Not authorised

* Renders outside the plan.
* `--plan`.
* Changes to the script or the plan.
* Shutting down the PC.
* Push.
