# Directive for Antigravity — C78 amendments 3–4: pilot (done) and versions, 96 renders (authorised by Alessandro on 2026-10-15)

Written by Claude.

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings.
* **If a step fails,** stop and paste the output. Do not change the script or the plan.
* **The plan is frozen** (`data/te_punct2_plan.csv`): do **not** run `--plan`.
* **No new node.** Plain model: no preset, no 5D tuner, no LoRA.
* **C78 Step 3 (`te_punct.py --block main`) stays not authorised.**

Pre-registration: `docs/prereg_te_punct.md`, amendment 3.

## Step 1 — the pilot

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_punct2.py --queue --block pilot2
```

When ComfyUI's queue is empty:

```powershell
python te_punct2.py --count
```

It must print `expected 16 missing 0 []`.

## Step 2 — paste back

Append to `docs/RENDERS_2026-10-15_te_punct.md` a section "Amendment 3 pilot" with the commands and outputs, inside
plain triple-backtick fences. Do not commit; Claude commits. Then stop and wait.

## Step 3 — the versions (96 renders; authorised by Alessandro on 2026-10-15)

The plan now has 112 rows: the 16 pilot rows (unchanged) and 96 `versions` rows. Some use BREAK (the core
`ConditioningConcat` node, as in C78 Step 2).

```powershell
python te_punct2.py --queue --block versions
```

When ComfyUI's queue is empty:

```powershell
python te_punct2.py --count
```

It must print `expected 112 missing 0 []`. Append a section "Amendment 4 versions" to the same RENDERS file, with
the outputs and the size of `Text2Img\benchmark_te_punct`. Do not commit.

## Not authorised

Renders outside this plan, `--plan`, changes to the script or the plan, shutting down, push.
