# Encodes - C71 style-swap encodes

## Step 1 — gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_direction.py --queue --first 1
```

```text
queued 1
```

```powershell
python te_direction.py --gate
```

```text
re-encoded V1 baseline vs C67 baseline: identical
GATE PASS
```

## Step 2 — the other 15 encodes

```powershell
python te_direction.py --queue
```

```text
queued 15
```

```powershell
python te_direction.py --count
```

```text
expected 16 missing 0 []
```

## Benchmark folder size

```text
Text2Img\benchmark_te_direction: 16 files, 178.33 MB (186995579 bytes)
```
