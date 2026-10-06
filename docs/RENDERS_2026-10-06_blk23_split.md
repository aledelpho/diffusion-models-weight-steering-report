# Renders - C58 blk23 split

## Step 1 — the three checks first

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python blk23_split.py --queue --checks
```

```text
queued E1_cartoon_CHK_whole_m0.450_krea2_seed2718281
queued E1_cartoon_CHK_all8_m0.450_krea2_seed2718281
queued E1_cartoon_CHK_all8_p0.300_krea2_seed2718281
queued 3
```

```powershell
python blk23_split.py --check
```

```text
REPRO whole -0.45 (vector) vs C47: max abs diff 0
SPLIT=WHOLE all eight (granular) m0.450 vs C47 whole block: max abs diff 0
SPLIT=WHOLE all eight (granular) p0.300 vs C47 whole block: max abs diff 0
CHECK PASS
```

Loading line from `comfyui.log`:
```text
[2026-10-06 16:35:57.073] Model Krea2 prepared for dynamic VRAM loading. 24449MB Staged. 8 patches attached. Force pre-loaded 160 weights: 2824 KB.
```
*(Note: the literal strings "loaded completely" or "loaded partially" were not found in the logs)*

## Step 2 — the 64 renders

```powershell
python blk23_split.py --queue
```

```text
queued E1_cartoon_attn_m0.450_krea2_seed2718281
queued E1_cartoon_mlp_m0.450_krea2_seed2718281
...
queued 64
```

```powershell
python blk23_split.py --count
```

```text
expected 165 missing 98 ['E1_cartoon_whole_m1.000_krea2_seed2718281_00001_.png', 'E1_cartoon_whole_p1.000_krea2_seed2718281_00001_.png', 'E1_cartoon_CHK_all8_m1.000_krea2_seed2718281_00001_.png', 'E1_cartoon_CHK_all8_p1.000_krea2_seed2718281_00001_.png', 'E1_cartoon_attn_m1.000_krea2_seed2718281_00001_.png']
```

**STOPPED HERE due to failure: The directive says this must print `expected 67 missing 0 []`.**

## Resume

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python blk23_split.py --queue --checks
```

```text
queued E1_cartoon_whole_p1.000_krea2_seed2718281
queued E1_cartoon_CHK_all8_m1.000_krea2_seed2718281
queued E1_cartoon_CHK_all8_p1.000_krea2_seed2718281
queued 3
```

```powershell
python blk23_split.py --check
```

```text
REPRO whole -0.45 (vector) vs C47: max abs diff 0
SPLIT=WHOLE all eight (granular) m0.450 vs whole block (vector): max abs diff 0
SPLIT=WHOLE all eight (granular) p0.300 vs whole block (vector): max abs diff 0
SPLIT=WHOLE all eight (granular) m1.000 vs whole block (vector): max abs diff 0
SPLIT=WHOLE all eight (granular) p1.000 vs whole block (vector): max abs diff 0
CHECK PASS
```

```powershell
python blk23_split.py --queue
```

```text
queued E1_cartoon_attn_m1.000_krea2_seed2718281
...
queued P4_selfie_mlp_p1.000_krea2_seed4669201
queued 94
```

```powershell
python blk23_split.py --count
```

```text
expected 165 missing 0 []
```

```powershell
python blk23_split.py --page
```

```text
64 sheets, 70 showings -> C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_blk23_split\eye_test.html
```
