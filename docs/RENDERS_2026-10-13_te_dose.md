# Renders — C74 text-encoder dose ladder

## Step 1 — the gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_dose.py --queue --first 1
```

```text
queued 1
```

```powershell
python te_dose.py --gate
```

```text
L06 MLP d=1.00 re-rendered vs C65 render: max abs diff 0
GATE PASS
```

## Step 2 — all the other renders (also after amendment 1)

```powershell
python te_dose.py --queue
```

```text
queued 72
```

```powershell
python te_dose.py --queue
```

```text
queued 126
```

```powershell
python te_dose.py --count
```

```text
expected 199 missing 0 []
```

## Benchmark folder size

```text
Text2Img\benchmark_te_dose: 199 files, 286.07 MB (299971251 bytes)
```
