# Directive for Antigravity — C58, block 23 split into attention and MLP (renders authorised by Alessandro on 2026-10-06)

Written by Claude. **Only the 165 renders of `data/blk23_split_plan.csv` are authorised** (7 in the check
phase + 158; amendment 1 added the doses ±1.0). Do not shut down or close anything; do not use `monitor_and_shutdown.py`. If a step fails, stop and
paste the output; do not change any script, plan, prompt or setting, and do not regenerate the plan.
Pre-registration: `docs/prereg_blk23_split.md`.

The C47 prompts and seeds (8 × 2), C47 settings. Block 23's attention matrices alone, and its MLP
matrices alone, at −0.45, +0.30, −1.0 and +1.0, through the tuner's `granular_json`; the whole block at
±1.0 through the block vector. Output:
`Text2Img\benchmark_blk23_split\`.

## Step 1 — the check phase first (7 renders)

ComfyUI running at http://127.0.0.1:8188 with the Arthemy Krea2 Tuner, as for C55/C56. Do not start or
restart it.

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python blk23_split.py --queue --checks
```

When the seven files exist:

```powershell
python blk23_split.py --check
```

All five comparison lines must say `max abs diff 0` and the last line `CHECK PASS`. If it says FAIL, **stop** and
paste: the bench must not run.

Also, from `comfyui.log`, paste the line that says how the model was loaded for these renders
(`loaded completely ...` or `loaded partially ...`). Paste it whatever it says.

## Step 2 — the other 158 renders

```powershell
python blk23_split.py --queue
```

When ComfyUI's queue is empty:

```powershell
python blk23_split.py --count
```

Must print `expected 165 missing 0 []`.

## Step 3 — the eye page, and nothing else

```powershell
python blk23_split.py --page
```

It writes `Text2Img\benchmark_blk23_split\eye_test.html` and `data/blk23_split_eye_key.csv`.
**Do not open the page, do not look at or describe the images, do not run `--measure`.** Alessandro
does the eye pass blind; Claude runs the measures after it is deposited.

## Step 4 — paste back

Write `docs/RENDERS_2026-10-06_blk23_split.md` with the exact commands and outputs of steps 1–3,
including the `comfyui.log` line about loading, inside plain triple-backtick fences. Do not commit;
Claude commits.

## Not authorised

No other renders, no `--measure`, no figures, no change to scripts, plan or tuner.
