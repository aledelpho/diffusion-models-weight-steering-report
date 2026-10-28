# Renders & Analysis — C114, C113's doses on three unseen prompts

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
& $PY te_unseen.py --selftest
```

```text
selftest ok; 21 cards (+3 repeats)
```

## Step 1 — plan

```powershell
& $PY te_unseen.py --plan
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
...
plan rows: 123 (292 expected)
```

## Step 2 — gate queue & gate check

```powershell
& $PY te_unseen.py --queue --block gate
& $PY -c "import te_unseen as U; rows=[r for r in U.rd(U.PLAN) if r['block']=='main' and r['cond']=='C0' and r['seed']=='2645751']; [U.TT.post(r) for r in rows]; print('queued', len(rows))"
```

```text
queued 3
queued 3
```

```powershell
& $PY te_unseen.py --gate
```

```text
U1_redtree_C0_krea2_seed2645751_00001_.png vs U1_redtree_TEXT_krea2_seed2645751_00001_.png: max abs diff 0
U2_dagger_C0_krea2_seed2645751_00001_.png vs U2_dagger_TEXT_krea2_seed2645751_00001_.png: max abs diff 0
U3_robot_C0_krea2_seed2645751_00001_.png vs U3_robot_TEXT_krea2_seed2645751_00001_.png: max abs diff 0
GATE PASS
```

## Step 3 — main renders

```powershell
& $PY te_unseen.py --queue --block main
```

```text
queued 117
```

## Step 4 — count & analyze

```powershell
& $PY te_unseen.py --count
```

```text
expected 123 missing 0 []
```

```powershell
& $PY te_unseen.py --analyze
```

```text
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_unseen_dino.csv 12 rows (not printed: applied with the labels)
```

## Benchmark folder size

```text
Text2Img\benchmark_te_unseen: 123 files, 188.11 MB (197252258 bytes)
```

## Run time

```text
1h 09m 00s (4140s)
```
