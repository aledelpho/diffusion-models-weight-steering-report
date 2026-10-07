# Renders - C59 split atlas

## Step 1 — the two checks

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python split_atlas.py --queue --checks
```

```text
queued 2
```

```powershell
python split_atlas.py --check
```

```text
REPRO baseline vs equal-dose atlas: max abs diff 0
SPLIT=WHOLE blk09 +0.35 (eight matrices, granular) vs atlas whole block: max abs diff 0
CHECK PASS
```

## Step 2 — queue everything else

```powershell
python split_atlas.py --queue
```

```text
queued 1014
```

## Step 3 — in the morning

*Generations running overnight.*

```powershell
python split_atlas.py --count
```

```text
expected 1016 missing 0 []
```
