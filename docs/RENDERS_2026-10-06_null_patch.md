# Renders - C55 null patch

## Step 1 — queue

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python null_patch.py --queue
```

```text
queued P3_archerforest_N0_baseline_krea2_seed3141592
queued P3_archerforest_N1_null_krea2_seed3141592
queued P3_archerforest_N2_blk27_p0.0001_krea2_seed3141592
queued P3_archerforest_N3_blk27_p0.004_krea2_seed3141592
queued P3_archerforest_N4_blk27_m0.004_krea2_seed3141592
```

## Step 2 — confirm the patch was really active

From `comfyui.log`:
```text
[12:56:28] [ArthemyKrea2Suite] [INFO] [Arthemy Profiler] Model Tuner finished | Total time: 0.0095s | Layers patched: 8
[12:57:02] [ArthemyKrea2Suite] [INFO] [Arthemy Profiler] Model Tuner finished | Total time: 0.0111s | Layers patched: 13
[12:57:36] [ArthemyKrea2Suite] [INFO] [Arthemy Profiler] Model Tuner finished | Total time: 0.0136s | Layers patched: 13
[12:58:10] [ArthemyKrea2Suite] [INFO] [Arthemy Profiler] Model Tuner finished | Total time: 0.0131s | Layers patched: 13
```

## Step 3 — the decisive check

```powershell
python null_patch.py --check
```

```text
N0 re-render vs C47 baseline: max abs diff 0 -> REPRO PASS
N1 null patch vs N0: max abs diff 0, pixels differing 0.000%
C55 VERDICT: CLEAN - the active node adds nothing beyond the multiplication
```

## Step 4 — the blind page for Alessandro

```powershell
python null_patch.py --page
```

```text
page -> C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_null_patch\hood_test.html
```
