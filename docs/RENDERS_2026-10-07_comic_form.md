# Renders - C60 comic form test

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python comic_form_test.py --queue --checks
```

```text
queued 2
```

```powershell
python comic_form_test.py --check
```

```text
REPRO split blk19 mlp + vs C59: max abs diff 0
WHOLE via granular blk08 + vs equal-dose atlas: max abs diff 0
CHECK PASS
```

```powershell
python comic_form_test.py --queue
```

```text
queued 189
```

```powershell
python comic_form_test.py --count
```

```text
expected 191 missing 0 []
```
