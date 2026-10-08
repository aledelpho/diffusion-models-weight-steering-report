# Renders - C61 cost floor (page 05)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python cost_floor_test.py --queue --checks
```

```text
queued 1
```

```powershell
python cost_floor_test.py --check
```

```text
REPRO page 05 render (P01, seed 42, block 9, +0.200): max abs diff 0
CHECK PASS
```

```powershell
python cost_floor_test.py --queue
```

```text
queued 912
```

```powershell
python cost_floor_test.py --count
```

```text
expected 913 missing 0 []
```
