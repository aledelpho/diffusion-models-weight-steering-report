# Renders — C75 part B trait test

## Step 1 — the gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_traits.py --queue --first 2
```

```text
queued 2
```

```powershell
python te_traits.py --gate
```

```text
zero push vs plain portrait: max abs diff 0
real push L06 d=0.85 vs C74 render: max abs diff 0
GATE PASS
```

## Step 2 — the other 120 renders

```powershell
python te_traits.py --queue
```

```text
queued 120
```

```powershell
python te_traits.py --count
```

```text
expected 122 missing 0 []
```

## Benchmark folder size

```text
Text2Img\benchmark_te_traits: 122 files, 178.07 MB (186721417 bytes)
```
