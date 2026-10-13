# Renders — C73 character genre fallback

## Step 1 — the gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_fallback.py --queue --first 1
```

```text
queued 1
```

```powershell
python te_fallback.py --gate
```

```text
re-rendered C52 baseline vs existing: max abs diff 0
GATE PASS
```

## Step 2 — the other 28 renders

```powershell
python te_fallback.py --queue
```

```text
queued 28
```

```powershell
python te_fallback.py --count
```

```text
expected 29 missing 0 []
```

## Benchmark folder size

```text
Text2Img\benchmark_te_fallback: 29 files, 45.14 MB (47336119 bytes)
```
