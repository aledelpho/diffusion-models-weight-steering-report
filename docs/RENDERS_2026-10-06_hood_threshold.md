# Renders - C56 hood threshold

## Step 1 — reproduction check

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python hood_threshold.py --queue --first 1
```

```text
queued P3_archerforest_baseline_krea2_seed3141592
queued 1 of 1
```

```powershell
python hood_threshold.py --repro
```

```text
REPRO PASS max abs diff 0
```

## Step 2 — the 40 renders

```powershell
python hood_threshold.py --queue
```

```text
queued P3_archerforest_blk00_neg_d0.010_krea2_seed3141592
queued P3_archerforest_blk00_neg_d0.020_krea2_seed3141592
queued P3_archerforest_blk00_neg_d0.040_krea2_seed3141592
queued P3_archerforest_blk00_neg_d0.080_krea2_seed3141592
queued P3_archerforest_blk00_neg_d0.160_krea2_seed3141592
queued P3_archerforest_blk00_pos_d0.010_krea2_seed3141592
queued P3_archerforest_blk00_pos_d0.020_krea2_seed3141592
queued P3_archerforest_blk00_pos_d0.040_krea2_seed3141592
queued P3_archerforest_blk00_pos_d0.080_krea2_seed3141592
queued P3_archerforest_blk00_pos_d0.160_krea2_seed3141592
queued P3_archerforest_blk10_neg_d0.010_krea2_seed3141592
queued P3_archerforest_blk10_neg_d0.020_krea2_seed3141592
queued P3_archerforest_blk10_neg_d0.040_krea2_seed3141592
queued P3_archerforest_blk10_neg_d0.080_krea2_seed3141592
queued P3_archerforest_blk10_neg_d0.160_krea2_seed3141592
queued P3_archerforest_blk10_pos_d0.010_krea2_seed3141592
queued P3_archerforest_blk10_pos_d0.020_krea2_seed3141592
queued P3_archerforest_blk10_pos_d0.040_krea2_seed3141592
queued P3_archerforest_blk10_pos_d0.080_krea2_seed3141592
queued P3_archerforest_blk10_pos_d0.160_krea2_seed3141592
queued P3_archerforest_blk20_neg_d0.010_krea2_seed3141592
queued P3_archerforest_blk20_neg_d0.020_krea2_seed3141592
queued P3_archerforest_blk20_neg_d0.040_krea2_seed3141592
queued P3_archerforest_blk20_neg_d0.080_krea2_seed3141592
queued P3_archerforest_blk20_neg_d0.160_krea2_seed3141592
queued P3_archerforest_blk20_pos_d0.010_krea2_seed3141592
queued P3_archerforest_blk20_pos_d0.020_krea2_seed3141592
queued P3_archerforest_blk20_pos_d0.040_krea2_seed3141592
queued P3_archerforest_blk20_pos_d0.080_krea2_seed3141592
queued P3_archerforest_blk20_pos_d0.160_krea2_seed3141592
queued P3_archerforest_blk23_neg_d0.010_krea2_seed3141592
queued P3_archerforest_blk23_neg_d0.020_krea2_seed3141592
queued P3_archerforest_blk23_neg_d0.040_krea2_seed3141592
queued P3_archerforest_blk23_neg_d0.080_krea2_seed3141592
queued P3_archerforest_blk23_neg_d0.160_krea2_seed3141592
queued P3_archerforest_blk23_pos_d0.010_krea2_seed3141592
queued P3_archerforest_blk23_pos_d0.020_krea2_seed3141592
queued P3_archerforest_blk23_pos_d0.040_krea2_seed3141592
queued P3_archerforest_blk23_pos_d0.080_krea2_seed3141592
queued P3_archerforest_blk23_pos_d0.160_krea2_seed3141592
queued 40 of 41
```

```powershell
python hood_threshold.py --count
```

```text
expected 41 missing 0 []
```
Tuner lines `Model Tuner finished | Total time: ... | Layers patched: 13` for this run: **40** (extracted from the ComfyUI daemon log, isolated from previous tests).

## Step 3 — the blind page

```powershell
python hood_threshold.py --page
```

```text
41 images, 49 showings -> C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_hood_threshold\hood_test.html
```
