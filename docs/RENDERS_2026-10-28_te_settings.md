# Renders & Analysis — C112, subject fixed and setting free (4 prompts × 8 seeds × 9 conditions)

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
& $PY te_settings.py --selftest
```

```text
selftest ok; 44 cards (+4 repeats)
```

## Step 1 — plan

```powershell
& $PY te_settings.py --plan
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
[08:58:24] [ArthemyKrea2Suite] [INFO] [Arthemy Profiler] CLIP Tuner finished | Total time: 0.0170s | Layers patched: 3
...
plan rows: 292 (292 expected)
```

## Step 2 — gate queue, C0 baseline queue, gate check

```powershell
& $PY te_settings.py --queue --block gate
```

```text
queued 4
```

```powershell
& $PY -c "import te_settings as S; rows=[r for r in S.rd(S.PLAN) if r['block']=='main' and r['cond']=='C0' and r['seed']=='2645751']; [S.TT.post(r) for r in rows]; print('queued', len(rows))"
```

```text
queued 4
```

```powershell
& $PY te_settings.py --gate
```

```text
S1_bluetree_C0_krea2_seed2645751_00001_.png vs S1_bluetree_TEXT_krea2_seed2645751_00001_.png: max abs diff 0
S2_alienaxe_C0_krea2_seed2645751_00001_.png vs S2_alienaxe_TEXT_krea2_seed2645751_00001_.png: max abs diff 0
S3_evilhelmet_C0_krea2_seed2645751_00001_.png vs S3_evilhelmet_TEXT_krea2_seed2645751_00001_.png: max abs diff 0
S4_flyingcar_C0_krea2_seed2645751_00001_.png vs S4_flyingcar_TEXT_krea2_seed2645751_00001_.png: max abs diff 0
GATE PASS
```

## Step 3 — main renders

```powershell
& $PY te_settings.py --queue --block main
```

```text
queued 284
```

## Step 4 — count & analyze

```powershell
& $PY te_settings.py --count
```

```text
expected 292 missing 0 []
```

```powershell
& $PY te_settings.py --analyze
```

```text
Rule 1 S1_bluetree: median pairwise D of the 8 plain pictures | 0.383 (bar 0.15) | the seeds vary
Rule 1 S2_alienaxe: median pairwise D of the 8 plain pictures | 0.094 (bar 0.15) | same picture at every seed
Rule 1 S3_evilhelmet: median pairwise D of the 8 plain pictures | 0.056 (bar 0.15) | same picture at every seed
Rule 1 S4_flyingcar: median pairwise D of the 8 plain pictures | 0.277 (bar 0.15) | the seeds vary
Rule 1 prompts whose plain pictures are the same at every seed | 2 of 4 | not supported
Reported S1_bluetree: median D from plain per edit | E05 0.111; E06 0.426; E14 0.284; E26 0.353; E28 0.708; P01 0.100; P06 0.406; P10 0.334 | -
Reported S1_bluetree: mean cosine of the displacements across seeds per edit (null: different edits, different seeds) | E05 0.09; E06 0.05; E14 0.02; E26 0.08; E28 0.31; P01 -0.04; P06 -0.00; P10 0.06; null 0.01 | -
Reported S2_alienaxe: median D from plain per edit | E05 0.076; E06 0.078; E14 0.072; E26 0.071; E28 0.131; P01 0.076; P06 0.049; P10 0.048 | -
Reported S2_alienaxe: mean cosine of the displacements across seeds per edit (null: different edits, different seeds) | E05 0.14; E06 -0.02; E14 0.09; E26 0.11; E28 0.23; P01 0.06; P06 0.04; P10 0.04; null -0.02 | -
Reported S3_evilhelmet: median D from plain per edit | E05 0.022; E06 0.029; E14 0.056; E26 0.022; E28 0.107; P01 0.039; P06 0.054; P10 0.041 | -
Reported S3_evilhelmet: mean cosine of the displacements across seeds per edit (null: different edits, different seeds) | E05 -0.01; E06 0.10; E14 0.27; E26 0.13; E28 0.36; P01 0.02; P06 0.06; P10 0.09; null -0.00 | -
Reported S4_flyingcar: median D from plain per edit | E05 0.086; E06 0.074; E14 0.044; E26 0.098; E28 0.110; P01 0.101; P06 0.073; P10 0.070 | -
Reported S4_flyingcar: mean cosine of the displacements across seeds per edit (null: different edits, different seeds) | E05 0.04; E06 0.05; E14 0.03; E26 0.10; E28 0.14; P01 0.10; P06 0.05; P10 0.07; null 0.04 | -
```

## Benchmark folder size

```text
Text2Img\benchmark_te_settings: 292 files, 335.11 MB (351388836 bytes)
```

## Run time

```text
2h 38m 10s (9490s)
```
