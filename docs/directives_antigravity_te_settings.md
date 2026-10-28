# Directive for Antigravity — C112, subject fixed and setting free (4 prompts × 8 seeds × 9 conditions)

Pre-registration: `docs/prereg_te_settings.md`. Script: `experiments/te_settings.py` (C111's encoder and workflow).
Outputs in `D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_te_settings` and `data/te_settings_*`.
**Run only after Alessandro has authorised the renders.** 292 renders, about 3 hours.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI; if it needs a restart, ask Alessandro.
* **If a step fails, stop and paste the output.** Do not change the script, the prompts, the doses or the plan.
* Do not run `--page` or `--rules`. Do not open or describe the pictures.

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
& $PY te_settings.py --selftest
& $PY te_settings.py --plan
& $PY te_settings.py --queue --block gate
```

`selftest ok; 44 cards (+4 repeats)`; `plan rows: 292 (292 expected)` (report any `NONFINITE` line); `queued 4`. When
the queue is empty:

```powershell
& $PY te_settings.py --gate
```

Four lines `max abs diff 0` and `GATE PASS`; otherwise **stop**. Then:

```powershell
& $PY te_settings.py --queue --block main
```

When the queue is empty:

```powershell
& $PY te_settings.py --count
& $PY te_settings.py --analyze
```

`missing 0 []`; paste every `--analyze` line.

## Paste back and commit

Write `docs/RENDERS_2026-10-28_te_settings.md` with the commands and outputs, the number and size of the files in
`benchmark_te_settings` and the run time. Commit it with `data/te_settings_plan.csv`, `data/te_settings_metrics.csv` and
`data/te_settings_dino_tests.csv`, message in Italian:

```
C112: render consegnati (soggetto fisso, ambiente libero), dati come prodotti, resoconto di Antigravity
```
