# Directives for Antigravity — C50 standard metrics (compute only)

Written by Claude on 2026-10-05. **No renders.** Design: `docs/prereg_standard_metrics.md`.
All code is Claude's: do not modify it.

## Rules

1. Do not write or modify scripts or documents, except the log in step 5.
2. Do not run `analyze_standard_metrics.py` and do not interpret numbers.
3. Never use `monitor_and_shutdown.py`; close nothing. If ComfyUI is running, it can stay open;
   if the GPU runs out of memory, stop and report (do not close ComfyUI yourself).
4. Use the ComfyUI venv python: `C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe`.
   Do not upgrade or reinstall torch, torchvision or any package already there.
5. Commits in Italian, only the files named below, no push; `validate_notebook.py` (0 errors) first.

## Steps

1. `<venv python> -m pip install piq --no-deps` and `<venv python> -c "import piq, open_clip; print(piq.__version__)"`.
   If `open_clip` is missing: `<venv python> -m pip install open_clip_torch --no-deps` and
   `ftfy`, `regex` if import then fails on them. Paste the output. If anything else is needed, stop.
2. `<venv python> experiments/standard_metrics.py --bench c47` (128 images; downloads LPIPS/DISTS,
   CLIP and DINOv2 weights on first run).
3. Same with `--bench c49` (432 images) and `--bench c45` (500 images).
4. Check that these files exist: `data/standard_metrics_c47.csv` (128 rows),
   `data/standard_metrics_c49.csv` (432), `data/standard_metrics_c45.csv` (500), and the three
   `_emb.npz`. Paste the row counts.
5. Write `docs/RENDERS_2026-10-05_standard_metrics.md` (commands, printed outputs, row counts).
   Commit the six data files and that document. Report to Alessandro and stop.
