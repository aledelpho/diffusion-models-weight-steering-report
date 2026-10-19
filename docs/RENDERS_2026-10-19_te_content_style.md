# Analysis — C104 CSD style vectors of C103's renders

## Step 1

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
& $PY te_content_style.py --selftest
```

```text
selftest ok
```

```powershell
& $PY te_content_style.py --csd
```

```text
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_content_style_csd.npz 96
```
