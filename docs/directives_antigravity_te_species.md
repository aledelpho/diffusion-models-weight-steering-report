# Directive for Antigravity — C107, 40 renders (authorised by Alessandro on 2026-10-20)

Written by Claude. Pre-registration: `docs/prereg_te_species.md`. Script: `experiments/te_species.py`.

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI yourself: if it is not running or stops responding, stop and ask Alessandro.
* **If a step fails,** stop and paste the output. Do not change the script or the plan.
* **The plan is frozen** (`data/te_species_plan.csv`, committed): do **not** run `--plan`.
* **No new node:** the workflow uses only nodes already installed (ArthemyKrea2CLIPTuner for the L06 edit).
* Python: `D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe` (or the `python` used for C73).
  Renders land in `D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_te_species`.

## Step 0 — check

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_species.py --selftest
```

It must end with `selftest ok`.

## Step 1 — the two gates

```powershell
python te_species.py --queue --first 2
```

When both `EN_plain_krea2_seed2645751_00001_.png` and `EN_L06_krea2_seed2645751_00001_.png` exist in
`benchmark_te_species`:

```powershell
python te_species.py --gate
```

Both lines must print `max abs diff 0`, then `GATE PASS`. If it prints `FAIL`, **stop** and paste: do not queue the rest.

## Step 2 — the other 38 renders

```powershell
python te_species.py --queue
```

When ComfyUI's queue is empty:

```powershell
python te_species.py --count
```

It must print `expected 40 missing 0 []`.

## Step 3 — paste back

Write `docs/RENDERS_2026-10-20_te_species.md` with the commands and outputs of Steps 0–2, the start and end times, and
any error. Commit **only** that file, message in Italian:

```
C107: render consegnati (40, gate 2 di 2), resoconto di Antigravity
```

Do not open, describe or label the pictures: the blind page is written by Claude after the renders.
