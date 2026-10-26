# Directive for Antigravity — MOSS3b, confirmations at 50 steps and follow-ups (160 renders, about 1 h 40 min)

Written by Claude, 2026-10-26. Pre-registration: `docs/prereg_moss_atlas2.md`. Script: `experiments/moss_atlas2.py`.
Plan frozen: `data/moss_atlas2_plan.csv` (do **not** run `--plan`). Settings as MOSS2/MOSS3: 16 renders at R50 (no LoRA,
euler, 50 steps, CFG 3, about 170 s), 144 at T10 (DMD2 LoRA, euler, 10 steps, CFG 1, about 22 s). Tuner v4, no restart.

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. **Do not restart ComfyUI yourself**; if it needs a restart, ask Alessandro.
* **If a step fails,** stop and paste the output. Do not change the node, the script or the plan.
* The MOSS3 atlas pictures (`benchmark_moss_atlas`) must stay where they are: `--analyze` reads them.

```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& $PY moss_atlas2.py --queue
```

`queued 160`. When the queue is empty:

```powershell
& $PY moss_atlas2.py --count
& $PY moss_atlas2.py --analyze
```

`expected 160 missing 0 []`; paste every line of `--analyze`.

Write `docs/RENDERS_2026-10-26_moss_atlas2.md` (outputs, render times R50 and T10, any interruption) and commit it with
`data/moss_atlas2_metrics.csv` and `data/moss_atlas2_tests.csv`, message in Italian:

```
MOSS3b: conferme a 50 step dell'atlante MOSS e test aggiuntivi (160 render), resoconto di Antigravity
```

Do not open or describe the pictures: the blind confirmation page is written by Claude after the renders.
