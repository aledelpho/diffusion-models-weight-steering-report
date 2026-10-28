# Directive for Antigravity — C114, C113's doses on three unseen prompts

Pre-registration: `docs/prereg_te_unseen.md` (**do not quote the prompts to Alessandro**). Script:
`experiments/te_unseen.py`. Outputs in `D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_te_unseen` and
`data/te_unseen_*`. Authorised by Alessandro on 2026-10-28. 123 renders, about 1 hour 10 minutes.

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI; if it needs a restart, ask Alessandro.
* **If a step fails, stop and paste the output.** Do not change the script, the prompts, the doses or the plan.
* Do not run `--page` or `--rules`. Do not open or describe the pictures, and do not write the prompts in your report.

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
& $PY te_unseen.py --selftest
& $PY te_unseen.py --plan
& $PY te_unseen.py --queue --block gate
& $PY -c "import te_unseen as U; rows=[r for r in U.rd(U.PLAN) if r['block']=='main' and r['cond']=='C0' and r['seed']=='2645751']; [U.TT.post(r) for r in rows]; print('queued', len(rows))"
```

`selftest ok; 21 cards (+3 repeats)`; `--plan` prints `plan rows: 123` (the "(292 expected)" text after it is C112's
and can be ignored; report any `NONFINITE` line); `queued 3`; `queued 3`. When the queue is empty:

```powershell
& $PY te_unseen.py --gate
```

Three lines `max abs diff 0` and `GATE PASS`; otherwise **stop**. Then:

```powershell
& $PY te_unseen.py --queue --block main
```

`queued 117`. When the queue is empty:

```powershell
& $PY te_unseen.py --count
& $PY te_unseen.py --analyze
```

`missing 0 []`; `wrote ...te_unseen_dino.csv 12 rows`.

## Paste back and commit

Write `docs/RENDERS_2026-10-28_te_unseen.md` with the commands and outputs (without the prompts), the number and size
of the files in `benchmark_te_unseen` and the run time. Commit it with `data/te_unseen_plan.csv` and
`data/te_unseen_dino.csv`, message in Italian:

```
C114: render consegnati (prompt nuovi, dosi di C113), dati come prodotti, resoconto di Antigravity
```
