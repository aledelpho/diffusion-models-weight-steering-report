# Renders — C77 layer 0 text-encoder replication

## Step 1 — the gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_layer0.py --queue --first 1
```

```text
queued 1
```

```powershell
python te_layer0.py --gate
```

```text
re-rendered C64 layer-0 picture vs existing: max abs diff 0
GATE PASS
```

## Step 2 — the other 6 renders

```powershell
python te_layer0.py --queue
```

```text
queued 6
```

```powershell
python te_layer0.py --count
```

```text
expected 7 missing 0 []
```

## Benchmark folder size

```text
Text2Img\benchmark_te_layer0: 7 files, 11.80 MB (12375847 bytes)
```
