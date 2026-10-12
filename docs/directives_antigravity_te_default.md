# Directive for Antigravity — C72, 280 renders (authorised by Alessandro on 2026-10-12)

Written by Claude. **Do not close anything, do not use `monitor_and_shutdown.py`, do not shut the PC down, do not
change power or system settings.**

If a step fails, stop and paste the output. Do not change the script, the plan or the node to make a step pass.
Pre-registration: `docs/prereg_te_default.md`. The plan is frozen (`data/te_default_plan.csv`, 280 rows): do
**not** run `--plan`. Expected time: about 5-6 hours at ~70 s per render.

## Step 0 — install the push node

```powershell
Copy-Item -Recurse C:\Users\aless\Desktop\diffusion-models-weight-steering-report\tools\comfyui_krea2_condpush `
  C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\comfyui_krea2_condpush
```

Restart ComfyUI the usual way, through StabilityMatrix. Check that the console says the node loaded
(`Krea2ConditioningPush`).

## Step 1 — the gate (4 renders)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_default.py --queue --first 4
```

When the four images exist in `Text2Img\benchmark_te_default`, run:

```powershell
python te_default.py --gate
```

It must print `GATE PASS`. If it prints `FAIL`, **stop** and paste the output, together with the console lines of
`[Krea2ConditioningPush]`.

## Step 2 — the other 276 renders

```powershell
python te_default.py --queue
```

When ComfyUI's queue is empty, run:

```powershell
python te_default.py --count
```

It should print `expected 280 missing 0 []`.

If ComfyUI refused the **empty-prompt** renders (`EMPTY_empty_...`, 4 rows), that is foreseen by the
pre-registration. Do not retry them and do not change the prompt; paste the console error, and the count may then
show those 4 as missing. Any other missing render: queue once more with `python te_default.py --queue`, then report.

## Step 3 — paste back

Write `docs/RENDERS_2026-10-12_te_default.md` with:

* the exact commands and outputs of Steps 1–2, inside plain triple-backtick fences;
* the `[Krea2ConditioningPush]` console lines of the gate;
* the size of `Text2Img\benchmark_te_default`;
* the render time per image.

Do not commit; Claude commits.

## Not authorised

* Renders outside the plan.
* `--plan`.
* Changes to the script, the plan or the node.
* Any ComfyUI change other than copying the node folder.
* Shutting down.
* Push.
