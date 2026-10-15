# Directive for Antigravity — C78, 93 renders in three stages (authorised by Alessandro on 2026-10-15)

Written by Claude.

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings.
* **If a step fails,** stop and paste the output. Do not change the script or the plan.
* **The plan is frozen** (`data/te_punct_plan.csv`): do **not** run `--plan`.
* **No new node:** the workflow uses only nodes already installed.

Pre-registration: `docs/prereg_te_punct.md`.

## Step 1 — the gate (2 renders)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_punct.py --queue --block gate
```

When ComfyUI's queue is empty:

```powershell
python te_punct.py --gate
```

Both lines must print `max abs diff 0`, then `GATE PASS`. If it prints `FAIL`, **stop** and paste.

## Step 2 — one BREAK render, then the pilot and the natural prompts (1 + 16 + 26 renders)

The BREAK version uses the core `ConditioningConcat` node (already installed with ComfyUI). Run it alone first:

```powershell
python te_punct.py --queue --block smoke
```

When `Text2Img\benchmark_te_punct\D1_dwarf_paladin_break_krea2_seed2645751_00001_.png` exists, go on. If ComfyUI
reports an error for it, paste the error, **skip the other BREAK renders** and go on with the rest.

```powershell
python te_punct.py --queue --block pilot
python te_punct.py --queue --block natural
```

When ComfyUI's queue is empty:

```powershell
python te_punct.py --count
```

It must print `expected 93 missing 48`.

**Then stop.** Write the paste-back (Step 4) for Steps 1–2 and wait. Claude checks the pilot against the rule in the
pre-registration and says whether to run Step 3.

## Step 3 — only after Claude's go (48 renders)

```powershell
python te_punct.py --queue --block main
```

When the queue is empty, `python te_punct.py --count` must print `expected 93 missing 0 []`.

## Step 4 — paste back

Write `docs/RENDERS_2026-10-15_te_punct.md` with the commands and outputs of each step, inside plain
triple-backtick fences, and the size of `Text2Img\benchmark_te_punct`. **This paste-back is required.** Do not commit;
Claude commits.

## Not authorised

* Step 3 before Claude's go.
* Renders outside the plan, `--plan`, changes to the script or the plan.
* Shutting down. Push.
