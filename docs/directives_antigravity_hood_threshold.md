# Directive for Antigravity — C56, the hood threshold (renders authorised by Alessandro on 2026-10-06)

Written by Claude. **Only the 41 renders of `data/hood_threshold_plan.csv` are authorised** (one
reproduction of the baseline + 40). Do not shut down or close anything; do not use
`monitor_and_shutdown.py`. If a step fails, stop and paste the output; do not change any script,
plan, prompt or setting to make a step pass, and do not regenerate the plan.
Pre-registration: `docs/prereg_hood_threshold.md`.

Archer prompt `P3_archerforest`, seed 3141592, C47 settings. Blocks 00, 10, 20, 23; each at
−0.16, −0.08, −0.04, −0.02, −0.01, +0.01, +0.02, +0.04, +0.08, +0.16 (Real Value, vectors_override).
Output: `Text2Img\benchmark_hood_threshold\`.

## Step 1 — reproduction check (one render)

ComfyUI running at http://127.0.0.1:8188 with the Arthemy Krea2 Tuner loaded, as for C55.

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python hood_threshold.py --queue --first 1
```

When the file exists:

```powershell
python hood_threshold.py --repro
```

Must print `REPRO PASS max abs diff 0`. If FAIL, **stop** and paste.

## Step 2 — the 40 renders

```powershell
python hood_threshold.py --queue
```

When ComfyUI's queue is empty:

```powershell
python hood_threshold.py --count
```

Must print `expected 41 missing 0 []`. From `comfyui.log`, count the tuner lines
`Model Tuner finished ... Layers patched: 13` for this run: there must be 40. Paste the count (not
the 40 lines).

## Step 3 — the blind page, and nothing else

```powershell
python hood_threshold.py --page
```

It writes `Text2Img\benchmark_hood_threshold\hood_test.html` and `data/hood_threshold_page_key.csv`.
**Do not open the page and do not look at or describe the images.** Alessandro labels them blind.

## Step 4 — paste back

Write `docs/RENDERS_2026-10-06_hood_threshold.md` with the exact commands and outputs of steps 1–3
inside plain triple-backtick fences. Do not commit; Claude commits.

## Not authorised

No other renders, no `--tally`, no measurements, no figures, no change to scripts, plan or tuner.
