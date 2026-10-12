# Encodes - C67 reading the text encoder's output

## Step 1 — determinism gate (two encodes)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_conditioning.py --queue --first 2
```

```text
queued 2
```

## Step 2 — the other 719 encodes

```powershell
python te_conditioning.py --queue
```

```text
queued 719
```

```powershell
python te_conditioning.py --count
```

```text
expected 721 missing 0 []
```

## Step 3 — gate (emendamento 1)

```powershell
python te_conditioning.py --gate
```

```text
determinism: identical
nulls bit-identical: True; null max 0.000364 (floor 0.000488); active min over reached taps 0.0475
GATE PASS
```

## Step 4 — logit lens

```powershell
python te_conditioning.py --logitlens
```

```text
logit lens ok: 51660 rows, embedding model.language_model.embed_tokens.weight (151936, 2560)
```

## Benchmark folder size

```text
Text2Img\benchmark_te_conditioning: 721 files, 383.45 MB (402080365 bytes)
```
