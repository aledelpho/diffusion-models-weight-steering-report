# Renders - C69 attention maps in the DiT

## Step 1 — one render, then the reproduction gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_bridge.py --queue --first 1
```

```text
queued 1
```

```powershell
python te_bridge.py --repro
```

```text
REPRO PASS: 1 renders checked (pixel-identical to the existing images, 9 attention files each)
```

## Step 2 — the other 24 renders

```powershell
python te_bridge.py --queue
```

```text
queued 24
```

```powershell
python te_bridge.py --count
```

```text
expected 25 missing 0 []
```

```powershell
python te_bridge.py --repro
```

```text
REPRO PASS: 25 renders checked (pixel-identical to the existing images, 9 attention files each)
```

## Benchmark folder size and execution times

```text
Text2Img\benchmark_te_bridge: 250 files (25 images, 225 attention files), 538.18 MB (0.526 GB, 564322811 bytes)
Render time per image: 68.56s - 73.60s (average 69.92s per image, cold start 73.60s)
```
