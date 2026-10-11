# Renders - C64 text-encoder pilot

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_pilot.py --queue --checks
```

```text
queued 7
```

```powershell
python te_pilot.py --check
```

```text
repro: max abs diff against the C60 baseline = 0
null_L35: max abs diff against the C60 baseline = 0
null_visual: max abs diff against the C60 baseline = 0
active_L02: max abs diff against the C60 baseline = 255
q+k only (QK-norm prediction, reported, not a gate): {5: 255, 17: 255, 29: 255}
CHECK PASS | structure: layer 35 unread as predicted / visual tower inert
```

```powershell
python te_pilot.py --queue
```

```text
queued 456
```

```powershell
python te_pilot.py --count
```

```text
expected 463 missing 0 []
```
