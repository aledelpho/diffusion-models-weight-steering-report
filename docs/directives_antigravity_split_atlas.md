# Directive for Antigravity — C59, the split atlas (renders authorised by Alessandro on 2026-10-06)

Written by Claude. **Only the 1016 renders of `data/split_atlas_plan.csv` are authorised.** It runs
overnight. Do not shut down or close anything; do not use `monitor_and_shutdown.py`; do not change
power or system settings. If a step fails, stop and write the output into the render notes; do not
change any script, plan or setting, and do not regenerate the plan. Plan: `docs/plan_split_atlas.md`.

## Step 1 — the two checks

ComfyUI running at http://127.0.0.1:8188 with the Arthemy Krea2 Tuner. Do not start or restart it.

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python split_atlas.py --queue --checks
```

When the two files exist in `Text2Img\benchmark_split_atlas\`:

```powershell
python split_atlas.py --check
```

Both lines must say `max abs diff 0`, the last `CHECK PASS`. If FAIL: **stop**, queue nothing else.

## Step 2 — queue everything else, then leave it running

```powershell
python split_atlas.py --queue
```

It queues 1014 prompts into ComfyUI at once (seed 2718281 first) and returns. ComfyUI works through
them on its own; there is nothing to watch. Do not re-run `--queue` while the queue is still running
(it would queue the missing files a second time).

## Step 3 — in the morning, when ComfyUI's queue is empty

```powershell
python split_atlas.py --count
```

Expected `expected 1016 missing 0 []`. If some are missing because the night was short, run
`python split_atlas.py --queue` again (it only queues the missing ones) and `--count` once that queue is
empty.

## Step 4 — paste back

Write `docs/RENDERS_2026-10-07_split_atlas.md` with the commands and outputs of steps 1–3 inside plain
triple-backtick fences. Do not run `--measure`; do not commit. Claude measures and commits.

## Not authorised

No other renders, no `--measure`, no figures, no change to scripts, plan or tuner.
