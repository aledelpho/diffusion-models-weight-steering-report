# Directive for Antigravity — C65, text-encoder edits on seven characters, five word orders and one watercolour (renders authorised by Alessandro on 2026-10-11)

Written by Claude. **Only the 531 renders of `data/te_characters_plan.csv` are authorised. Do not close
anything; do not use `monitor_and_shutdown.py`; do not change power or system settings.** The one exception,
authorised by Alessandro for this run only because it runs at night: the PC is powered off by
`te_characters.py --night --shutdown` (Step 3), and only after the renders have finished and the log is written. If a step fails,
stop and paste the output; do not change any script, plan or prompt to make a step pass. The plan is frozen with
the pre-registration (`docs/prereg_te_characters.md`): do **not** run `--plan`.

ComfyUI must have the `ArthemyKrea2CLIPTuner` node loaded (the same setup as C64, `benchmark_te_pilot`).
Renders go to `Text2Img\benchmark_te_characters\`. The comic-character baselines are **not** rendered again
(read from `Text2Img\benchmark_portraits\phase_c\`), nor are the word-order baselines (read from
`Text2Img\benchmark_prompt_order\`). The watercolour baselines are rendered (they are in the plan).

## Step 1 — reproduction gate (two renders)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_characters.py --count
```

Must end with `reused baselines missing 0`. Then:

```powershell
python te_characters.py --queue --first 2
```

When `Text2Img\benchmark_te_characters\D1_dwarf_paladin_REPRO_baseline_krea2_seed2645751_00001_.png` and
`...\V1_Original_REPRO_baseline_krea2_seed3141592_00001_.png` both exist:

```powershell
python te_characters.py --repro
```

Must print `REPRO ... PASS max abs diff 0` **twice**. If either FAILs, **stop** and paste; do not queue anything else.

## Step 2 — the other 529 renders

```powershell
python te_characters.py --queue
```

## Step 3 — the night watchdog (start it right after Step 2, then leave)

```powershell
python te_characters.py --night --shutdown
```

It waits until ComfyUI's queue has been empty for three checks one minute apart, then runs `--count`,
`--repro` and `--page`, writes `docs\RENDERS_2026-10-11_te_characters.md` with their output, and schedules the
shutdown in 5 minutes (`shutdown /s /t 300`; it can be cancelled with `shutdown /a`). Leave the terminal open;
start nothing else after it. If ComfyUI must be restarted during the night, the watchdog keeps waiting.

`--count` must print `expected 531 missing 0 [] | reused baselines missing 0`; `--repro` also prints the seven
layer-35 null renders (expected max abs diff 0; reported, not a gate). `--page` writes
`Text2Img\benchmark_te_characters\eye_test\eye_test.html` and `data\te_characters_eye_key.csv`.
**Next morning: stop here** and tell Alessandro; Claude commits the key **before** he opens the page. Alessandro then fills the page and exports `te_characters_eye_alessandro.csv`; Claude commits the key
and the labels. Only after Claude says the labels are committed:

## Step 4 — the measurements

```powershell
python te_characters.py --features
python te_characters.py --faces
```

`--faces` needs `insightface` (model `buffalo_l`, already in `C:\Users\aless\.insightface\models`),
`onnxruntime-gpu` and `piq`, as in C52. Do **not** run `--test`; Claude runs it.

## Step 5 — paste back

Append to `docs/RENDERS_2026-10-11_te_characters.md` (written by the watchdog) the exact commands and outputs of
Step 1, `--features` (it prints `features ok` twice: characters and word order) and `--faces` (last lines,
including `faces ok: N of M with a face`), inside plain triple-backtick fences. Do not commit; Claude commits.

## Not authorised

No other renders, no `--plan`, no `--test`, no figures, no change to scripts, plan or prompts, no push. No
shutdown other than the one scheduled by the watchdog.
