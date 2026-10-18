# Directive for Antigravity — C79, 12-tap isolation on `Qwen3-VL-4B` (76 renders: 4 gate + 72 main)

Pre-registration: `docs/prereg_te_tap_isolation.md`.
Script: `experiments/te_tap_isolation.py`.
Plan: `data/te_tap_isolation_plan.csv` (76 rows).

## Hard rules

* **Do not close anything.** Do not use `monitor_and_shutdown.py`, do not shut the PC down, and do not change power or system settings.
* **If a step fails,** stop and paste the output. Do not change the script or the plan.
* **The plan is frozen** (`data/te_tap_isolation_plan.csv`, 76 rows): do **not** re-run `--plan` after the gate starts.
* **Node requirement:** `tools/comfyui_krea2_condpush/__init__.py` has been updated with `variant="taps"` and copied to `C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\comfyui_krea2_condpush\__init__.py`. Make sure ComfyUI has been started (or restarted) after this update so `Krea2ConditioningPush` accepts `variant="taps"` and the optional `taps` string.

---

## Step 0 — Zero-render encoder & `txtfusion` weight audit (can run without ComfyUI)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe te_tap_isolation.py --selftest
C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe te_tap_isolation.py --plan
C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe te_tap_isolation.py --encoder
```

* `--selftest` must print `selftest ok`.
* `--plan` must print `plan rows: 76 {'gate': 4, 'main': 72}`.
* `--encoder` must print `ENCODER GATE P1_elfbrawler max_abs_diff = 0.0` and write `data/te_tap_isolation_txtfusion_weights.csv`, `data/te_tap_isolation_encoder_by_tap.csv`, and `data/te_tap_isolation_encoder_summary.csv`.

---

## Step 1 — The 4-render reproduction & partition gate (requires ComfyUI running)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe te_tap_isolation.py --queue --block gate
```

When ComfyUI's queue is empty and all 4 files exist in `Text2Img\benchmark_te_tap_isolation\`, run:

```powershell
C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe te_tap_isolation.py --gate
```

It must print `max abs diff 0` four times (`gate_zero`, `gate_real_L06`, `gate_all12_L06`, and `gate_late_L28`) and end with `GATE PASS`. If any line is not `0` or it prints `FAIL`, **stop immediately** and paste the output.

---

## Step 2 — The 72 main renders (`L06` and `L14` × `taps_local`, `taps_early_mid`, `taps_late`)

```powershell
C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe te_tap_isolation.py --queue --block main
```

When ComfyUI's queue is empty, run:

```powershell
C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe te_tap_isolation.py --count
```

It must print `expected 76 missing 0 []`.

---

## Step 3 — Paste back

Write `docs/RENDERS_2026-10-17_te_tap_isolation.md` with the exact commands and outputs of Steps 0–2 inside plain triple-backtick fences, and the size of `Text2Img\benchmark_te_tap_isolation`.
