# Directive for Antigravity — C108, 96 renders (authorised by Alessandro on 2026-10-21)

Written by Claude. Pre-registration: `docs/prereg_te_gender.md`. Script: `experiments/te_gender.py`.

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, do not change power or
  system settings. Do not restart ComfyUI yourself: if it is not running or stops responding, stop and ask Alessandro.
* **If a step fails,** stop and paste the output. Do not change the script or the plan.
* **The plan is frozen** (`data/te_gender_plan.csv`, committed): do **not** run `--plan`.
* **No new node:** only nodes already installed (ArthemyKrea2CLIPTuner for the L06 edit), as in C107.
* Renders land in `D:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_te_gender`.

## Step 0 — check

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_gender.py --selftest
```

It must end with `selftest ok`.

## Step 1 — the two gates

```powershell
python te_gender.py --queue --first 2
```

When `A_D1_orig_plain_krea2_seed2645751_00001_.png` and `A_D1_orig_L06_krea2_seed2645751_00001_.png` exist:

```powershell
python te_gender.py --gate
```

Both lines must print `max abs diff 0`, then `GATE PASS`. If `FAIL`, **stop** and paste.

## Step 2 — the other 94 renders

```powershell
python te_gender.py --queue
```

When ComfyUI's queue is empty:

```powershell
python te_gender.py --count
```

It must print `expected 96 missing 0 []`.

## Step 3 — paste back

Write `docs/RENDERS_2026-10-21_te_gender.md` with the commands and outputs of Steps 0–2, start and end times, and any
error. Commit **only** that file, message in Italian:

```
C108: render consegnati (96, gate 2 di 2), resoconto di Antigravity
```

Do not open, describe or label the pictures: the blind pages are written by Claude after the renders.
