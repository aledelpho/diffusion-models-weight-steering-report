# Directive for Antigravity — C75 part B, 122 renders (authorised by Alessandro on 2026-10-13)

Written by Claude.

**Rules:**

* Do not close anything. Do not use `monitor_and_shutdown.py`, do not shut the PC down, and do not change power or
  system settings.
* If a step fails, stop and paste the output. Do not change the script or the plan.
* The plan is frozen (`data/te_traits_plan.csv`, 122 rows): do **not** run `--plan`.
* The node `Krea2ConditioningPush` (v2, `tools/comfyui_krea2_condpush`) is already installed from C72. No new node
  is needed.

Pre-registration: `docs/prereg_te_traits.md` (amendment 1).

## Step 1 — the gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_traits.py --queue --first 2
```

When both files exist in `Text2Img\benchmark_te_traits\`, run:

```powershell
python te_traits.py --gate
```

It must print `max abs diff 0` twice and `GATE PASS`. If it prints `FAIL`, **stop** and paste.

## Step 2 — the other 120 renders

```powershell
python te_traits.py --queue
```

When ComfyUI's queue is empty, run:

```powershell
python te_traits.py --count
```

It must print `expected 122 missing 0 []`. If some are missing, run `--queue` again when ComfyUI is idle: it skips
every image that already exists.

## Step 3 — paste back (required)

Write `docs/RENDERS_2026-10-13_te_traits.md` with:

* the commands and outputs of Steps 1–2, inside plain triple-backtick fences;
* the size of `Text2Img\benchmark_te_traits`.

Do not commit; Claude commits.

## Not authorised

* Renders outside the plan.
* `--plan`.
* Changes to the script or the plan.
* Shutting down the PC.
* Push.
