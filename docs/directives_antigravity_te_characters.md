# Directive for Antigravity — C65, text-encoder edits on seven characters (renders authorised by Alessandro on 2026-10-11)

Written by Claude. **Only the 288 renders of `data/te_characters_plan.csv` are authorised. Do not shut down or
close anything; do not use `monitor_and_shutdown.py`; do not change power or system settings.** If a step fails,
stop and paste the output; do not change any script, plan or prompt to make a step pass. The plan is frozen with
the pre-registration (`docs/prereg_te_characters.md`): do **not** run `--plan`.

ComfyUI must have the `ArthemyKrea2CLIPTuner` node loaded (the same setup as C64, `benchmark_te_pilot`).
Renders go to `Text2Img\benchmark_te_characters\`. The baselines are **not** rendered again: they are read from
`Text2Img\benchmark_portraits\phase_c\`.

## Step 1 — reproduction gate (one render)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_characters.py --queue --first 1
```

When `Text2Img\benchmark_te_characters\D1_dwarf_paladin_REPRO_baseline_krea2_seed2645751_00001_.png` exists:

```powershell
python te_characters.py --repro
```

Must print `REPRO PASS max abs diff 0`. If FAIL, **stop** and paste.

## Step 2 — the other 287 renders

```powershell
python te_characters.py --queue
```

When ComfyUI's queue is empty:

```powershell
python te_characters.py --count
python te_characters.py --repro
```

`--count` must print `expected 288 missing 0 [] | reused baselines missing 0`. The second `--repro` also
prints the seven layer-35 null renders (expected max abs diff 0; reported, not a gate).

## Step 3 — the eye page, and nothing else yet

```powershell
python te_characters.py --page
```

It writes `Text2Img\benchmark_te_characters\eye_test\eye_test.html` and `data\te_characters_eye_key.csv`.
**Stop here.** Alessandro fills the page and exports `te_characters_eye_alessandro.csv`; Claude commits the key
and the labels. Only after Claude says the labels are committed:

## Step 4 — the measurements

```powershell
python te_characters.py --features
python te_characters.py --faces
```

`--faces` needs `insightface` (model `buffalo_l`, already in `C:\Users\aless\.insightface\models`),
`onnxruntime-gpu` and `piq`, as in C52. Do **not** run `--test`; Claude runs it.

## Step 5 — paste back

Write `docs/RENDERS_2026-10-11_te_characters.md` with the exact commands and outputs of both `--repro` runs,
`--count`, `--page`, `--features` and `--faces` (last lines, including `faces ok: N of M with a face`), inside
plain triple-backtick fences. Do not commit; Claude commits.

## Not authorised

No other renders, no `--plan`, no `--test`, no figures, no change to scripts, plan or prompts, no push.
