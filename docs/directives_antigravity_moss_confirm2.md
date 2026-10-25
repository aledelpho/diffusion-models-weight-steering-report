# Directive for Antigravity — MOSS2 amendment 3: 6 confirmation renders at 50 steps (about 17 minutes)

Written by Claude, 2026-10-25. Pre-registration: `docs/prereg_moss_bench.md`, amendment 3. The plan
`data/moss_bench_plan.csv` now has 90 rows (6 new `confirm2` rows at the end); do **not** run `--plan`.

* Same hard rules as `docs/directives_antigravity_moss_bench.md`: do not close anything, do not restart ComfyUI, stop
  and paste on any failure, do not open or describe the pictures.

```powershell
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& $PY moss_bench.py --queue
```

It must print `queued 6` (the 84 existing pictures are skipped). When the queue is empty:

```powershell
& $PY moss_bench.py --count
& $PY moss_confirm_page.py
```

`expected 90 missing 0 []`; `cards 15 -> ...occhio_MOSS2b.html`. Append the outputs and the render times to
`docs/RENDERS_2026-10-25_moss_bench.md` and commit it with `data/moss_confirm2_key.csv`, message in Italian:

```
MOSS2: 6 conferme a 50 step a d = 2 (emendamento 3) e pagina cieca occhio_MOSS2b, resoconto di Antigravity
```
