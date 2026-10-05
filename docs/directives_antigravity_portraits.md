# Directive for Antigravity — portrait atlas, phase A (renders authorised by Alessandro on 2026-10-05)

Written by Claude. **Only the renders listed here are authorised. Do not shut down or close
anything; do not use `monitor_and_shutdown.py`.** If a step fails, stop and paste the output; do not
change any script, plan or prompt to make a step pass.

The plan is already committed: `data/portraits_atlas_plan.csv`, 457 rows, written by
`experiments/portraits.py --plan`. Do **not** regenerate it.

## Step 1 — reproduction check (one render)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python portraits.py --queue --first 1
```

Wait until `Text2Img\benchmark_portraits\renders\REPRO_F1cartoon_fox_baseline_krea2_seed5772156_00001_.png`
exists, then:

```powershell
python portraits.py --repro
```

It must print `REPRO PASS max abs diff 0`. If it prints FAIL, **stop** and paste the output.

## Step 2 — the atlas (456 renders)

```powershell
python portraits.py --queue
```

When ComfyUI's queue is empty:

```powershell
python portraits.py --count
```

It must print `expected 457 missing 0 [] duplicates 0`. If anything is missing, run `--queue` once more
(it skips files that exist) and `--count` again; if still incomplete, stop and paste.

## Step 3 — the page Alessandro calibrates on

```powershell
python build_annotation_page.py portraits
```

It writes `Text2Img\benchmark_portraits\presets.html` and `_thumbs\`.

## Step 4 — paste back

Write `docs/RENDERS_2026-10-05_portraits.md` with the exact commands run and the exact outputs of
`--repro`, `--count` and `build_annotation_page.py`, inside plain triple-backtick fences (check that
the fences survive PowerShell). Do not commit anything; Claude commits.

## Not authorised

- No analysis, no metrics, no figures.
- No render of H3, R6 or T7 (the held-out characters) — they are phase C, after the preset is frozen.
- No change to `portraits.py`, the plan, or the prompts.
