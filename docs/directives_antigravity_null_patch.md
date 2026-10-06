# Directive for Antigravity — C55, the null patch (renders authorised by Alessandro on 2026-10-06)

Written by Claude. **Only the 5 renders listed here are authorised. Do not shut down or close
anything; do not use `monitor_and_shutdown.py`.** If a step fails, stop and paste the output; do not
change any script, plan, prompt or setting to make a step pass. The plan
(`data/null_patch_plan.csv`, 5 rows) is committed; do **not** regenerate it.
Pre-registration: `docs/prereg_null_patch.md`.

| id | what the tuner does |
|---|---|
| N0_baseline | no tuner node (re-render of the C47 baseline, to check this session reproduces it) |
| N1_null | tuner active; `granular_json` multiplies the 8 bf16 matrices of block 27 by 1.0001, which changes no weight |
| N2_blk27_p0.0001 | block 27 at +0.0001 (only its float32 scales change) |
| N3_blk27_p0.004 | block 27 at +0.004 (every weight moves by about one bf16 step) |
| N4_blk27_m0.004 | block 27 at −0.004 |

All: archer prompt `P3_archerforest`, seed 3141592, the C47 settings (euler_ancestral, simple,
9 steps, cfg 1.0, 1024×1280, `krea2_turbo_bf16.safetensors`, weight_dtype default).

## Step 1 — queue the 5 renders

ComfyUI must be running at http://127.0.0.1:8188 with the Arthemy Krea2 Tuner loaded, as for C47.

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python null_patch.py --queue
```

## Step 2 — confirm the patch was really active

In the ComfyUI console (or `comfyui.log`), find the lines written by the tuner for these renders:
`[Arthemy Profiler] Model Tuner finished | ... | Layers patched: N`. Paste them. Expected:
**N1 → 8**, N2/N3/N4 → 13, N0 → no tuner line. If N1 reports 0 patched layers, the test is void:
stop and paste.

## Step 3 — the decisive check

When ComfyUI's queue is empty and the 5 files exist in
`Text2Img\benchmark_null_patch\`:

```powershell
python null_patch.py --check
```

Paste the three lines. The first must say `REPRO PASS`; the third is the verdict.

## Step 4 — the blind page for Alessandro, and nothing else

```powershell
python null_patch.py --page
```

It writes `Text2Img\benchmark_null_patch\hood_test.html` and `data/null_patch_page_key.csv`.
**Do not open the page and do not describe the images.** Alessandro labels the hood blind.

## Step 5 — paste back

Write `docs/RENDERS_2026-10-06_null_patch.md` with the exact commands and outputs of steps 1–4
(including the tuner log lines), inside plain triple-backtick fences. Do not commit; Claude commits.

## Not authorised

No other renders, no measurements beyond `--check`, no figures, no change to scripts, plan, prompts
or the tuner.
