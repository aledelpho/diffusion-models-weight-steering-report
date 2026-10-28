# Renders & Analysis — C113, dose ladders (2 prompts × 4 edits × 3 new levels × 8 seeds)

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
& $PY te_dose2.py --selftest
```

```text
selftest ok; 40 cards (+4 repeats)
```

## Step 1 — plan

```powershell
& $PY te_dose2.py --plan
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
[16:51:21] [ArthemyKrea2Suite] [INFO] [Arthemy Profiler] CLIP Tuner finished | Total time: 0.0170s | Layers patched: 3
...
plan rows: 194 (194 expected)
```

## Step 2 — gate queue & gate check

```powershell
& $PY te_dose2.py --queue --block gate
```

```text
queued 2
```

```powershell
& $PY te_dose2.py --gate
```

```text
S1_bluetree: re-rendered plain vs C112 plain, max abs diff 0
S3_evilhelmet: re-rendered plain vs C112 plain, max abs diff 0
GATE PASS
```

## Step 3 — main renders

```powershell
& $PY te_dose2.py --queue --block main
```

```text
queued 192
```

## Step 4 — count & analyze

```powershell
& $PY te_dose2.py --count
```

```text
expected 194 missing 0 [] | reused from C112: 80 missing 0
```

```powershell
& $PY te_dose2.py --analyze
```

```text
{'prompt': 'S1_bluetree', 'edit': 'E06', 'level': 1, 'dose': 0.4, 'median_D_from_plain': 0.4259, 'plain_seed_D': 0.3831, 'ratio_to_seed': 1.112, 'consistency': 0.0518}
{'prompt': 'S1_bluetree', 'edit': 'E06', 'level': 2, 'dose': 0.8, 'median_D_from_plain': 0.5101, 'plain_seed_D': 0.3831, 'ratio_to_seed': 1.331, 'consistency': 0.3173}
{'prompt': 'S1_bluetree', 'edit': 'E06', 'level': 3, 'dose': 1.2, 'median_D_from_plain': 0.7747, 'plain_seed_D': 0.3831, 'ratio_to_seed': 2.022, 'consistency': 0.4252}
{'prompt': 'S1_bluetree', 'edit': 'E06', 'level': 4, 'dose': 1.6, 'median_D_from_plain': 0.881, 'plain_seed_D': 0.3831, 'ratio_to_seed': 2.3, 'consistency': 0.5779}
{'prompt': 'S1_bluetree', 'edit': 'E14', 'level': 1, 'dose': 0.4, 'median_D_from_plain': 0.2837, 'plain_seed_D': 0.3831, 'ratio_to_seed': 0.741, 'consistency': 0.0229}
{'prompt': 'S1_bluetree', 'edit': 'E14', 'level': 2, 'dose': 0.8, 'median_D_from_plain': 0.5248, 'plain_seed_D': 0.3831, 'ratio_to_seed': 1.37, 'consistency': 0.4061}
{'prompt': 'S1_bluetree', 'edit': 'E14', 'level': 3, 'dose': 1.2, 'median_D_from_plain': 0.8552, 'plain_seed_D': 0.3831, 'ratio_to_seed': 2.232, 'consistency': 0.5445}
{'prompt': 'S1_bluetree', 'edit': 'E14', 'level': 4, 'dose': 1.6, 'median_D_from_plain': 0.9618, 'plain_seed_D': 0.3831, 'ratio_to_seed': 2.511, 'consistency': 0.643}
{'prompt': 'S1_bluetree', 'edit': 'E28', 'level': 1, 'dose': 1.06066, 'median_D_from_plain': 0.7078, 'plain_seed_D': 0.3831, 'ratio_to_seed': 1.847, 'consistency': 0.3055}
{'prompt': 'S1_bluetree', 'edit': 'E28', 'level': 2, 'dose': 1.59099, 'median_D_from_plain': 0.8144, 'plain_seed_D': 0.3831, 'ratio_to_seed': 2.126, 'consistency': 0.3534}
{'prompt': 'S1_bluetree', 'edit': 'E28', 'level': 3, 'dose': 2.12132, 'median_D_from_plain': 0.8215, 'plain_seed_D': 0.3831, 'ratio_to_seed': 2.144, 'consistency': 0.5021}
{'prompt': 'S1_bluetree', 'edit': 'E28', 'level': 4, 'dose': 2.65165, 'median_D_from_plain': 0.8417, 'plain_seed_D': 0.3831, 'ratio_to_seed': 2.197, 'consistency': 0.3435}
{'prompt': 'S1_bluetree', 'edit': 'P01', 'level': 1, 'dose': 0.7071, 'median_D_from_plain': 0.1004, 'plain_seed_D': 0.3831, 'ratio_to_seed': 0.262, 'consistency': -0.0401}
{'prompt': 'S1_bluetree', 'edit': 'P01', 'level': 2, 'dose': 1.41421, 'median_D_from_plain': 0.19, 'plain_seed_D': 0.3831, 'ratio_to_seed': 0.496, 'consistency': 0.0243}
{'prompt': 'S1_bluetree', 'edit': 'P01', 'level': 3, 'dose': 2.12132, 'median_D_from_plain': 0.646, 'plain_seed_D': 0.3831, 'ratio_to_seed': 1.686, 'consistency': 0.1654}
{'prompt': 'S1_bluetree', 'edit': 'P01', 'level': 4, 'dose': 2.82843, 'median_D_from_plain': 0.9371, 'plain_seed_D': 0.3831, 'ratio_to_seed': 2.446, 'consistency': 0.5531}
{'prompt': 'S3_evilhelmet', 'edit': 'E06', 'level': 1, 'dose': 0.4, 'median_D_from_plain': 0.0293, 'plain_seed_D': 0.0556, 'ratio_to_seed': 0.527, 'consistency': 0.0961}
{'prompt': 'S3_evilhelmet', 'edit': 'E06', 'level': 2, 'dose': 0.8, 'median_D_from_plain': 0.2754, 'plain_seed_D': 0.0556, 'ratio_to_seed': 4.956, 'consistency': 0.5756}
{'prompt': 'S3_evilhelmet', 'edit': 'E06', 'level': 3, 'dose': 1.2, 'median_D_from_plain': 0.8809, 'plain_seed_D': 0.0556, 'ratio_to_seed': 15.851, 'consistency': 0.6792}
{'prompt': 'S3_evilhelmet', 'edit': 'E06', 'level': 4, 'dose': 1.6, 'median_D_from_plain': 0.9442, 'plain_seed_D': 0.0556, 'ratio_to_seed': 16.99, 'consistency': 0.759}
{'prompt': 'S3_evilhelmet', 'edit': 'E14', 'level': 1, 'dose': 0.4, 'median_D_from_plain': 0.0564, 'plain_seed_D': 0.0556, 'ratio_to_seed': 1.015, 'consistency': 0.2691}
{'prompt': 'S3_evilhelmet', 'edit': 'E14', 'level': 2, 'dose': 0.8, 'median_D_from_plain': 0.1776, 'plain_seed_D': 0.0556, 'ratio_to_seed': 3.197, 'consistency': 0.5157}
{'prompt': 'S3_evilhelmet', 'edit': 'E14', 'level': 3, 'dose': 1.2, 'median_D_from_plain': 0.9051, 'plain_seed_D': 0.0556, 'ratio_to_seed': 16.287, 'consistency': 0.7572}
{'prompt': 'S3_evilhelmet', 'edit': 'E14', 'level': 4, 'dose': 1.6, 'median_D_from_plain': 0.8815, 'plain_seed_D': 0.0556, 'ratio_to_seed': 15.861, 'consistency': 0.7468}
{'prompt': 'S3_evilhelmet', 'edit': 'E28', 'level': 1, 'dose': 1.06066, 'median_D_from_plain': 0.1071, 'plain_seed_D': 0.0556, 'ratio_to_seed': 1.927, 'consistency': 0.3603}
{'prompt': 'S3_evilhelmet', 'edit': 'E28', 'level': 2, 'dose': 1.59099, 'median_D_from_plain': 0.655, 'plain_seed_D': 0.0556, 'ratio_to_seed': 11.786, 'consistency': 0.6322}
{'prompt': 'S3_evilhelmet', 'edit': 'E28', 'level': 3, 'dose': 2.12132, 'median_D_from_plain': 0.7134, 'plain_seed_D': 0.0556, 'ratio_to_seed': 12.836, 'consistency': 0.739}
{'prompt': 'S3_evilhelmet', 'edit': 'E28', 'level': 4, 'dose': 2.65165, 'median_D_from_plain': 0.7417, 'plain_seed_D': 0.0556, 'ratio_to_seed': 13.346, 'consistency': 0.6977}
{'prompt': 'S3_evilhelmet', 'edit': 'P01', 'level': 1, 'dose': 0.7071, 'median_D_from_plain': 0.0392, 'plain_seed_D': 0.0556, 'ratio_to_seed': 0.705, 'consistency': 0.0167}
{'prompt': 'S3_evilhelmet', 'edit': 'P01', 'level': 2, 'dose': 1.41421, 'median_D_from_plain': 0.067, 'plain_seed_D': 0.0556, 'ratio_to_seed': 1.206, 'consistency': 0.2082}
{'prompt': 'S3_evilhelmet', 'edit': 'P01', 'level': 3, 'dose': 2.12132, 'median_D_from_plain': 0.7433, 'plain_seed_D': 0.0556, 'ratio_to_seed': 13.374, 'consistency': 0.6893}
{'prompt': 'S3_evilhelmet', 'edit': 'P01', 'level': 4, 'dose': 2.82843, 'median_D_from_plain': 0.8811, 'plain_seed_D': 0.0556, 'ratio_to_seed': 15.853, 'consistency': 0.7437}
```

## Benchmark folder size

```text
Text2Img\benchmark_te_dose2: 194 files, 289.11 MB (303153438 bytes)
```

## Run time

```text
1h 56m 00s (6960s)
```
