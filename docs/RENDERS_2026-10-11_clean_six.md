# Renders - C63 clean six

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python clean_six_test.py --queue --checks
```

```text
queued 1
```

```powershell
python clean_six_test.py --check
```

```text
REPRO C60 elf, seed 1618033, block 8 MLP +0.35: max abs diff 0
CHECK PASS
```

```powershell
python clean_six_test.py --queue
```

```text
queued 108
```

```powershell
python clean_six_test.py --count
```

```text
expected 109 missing 0 []
```
