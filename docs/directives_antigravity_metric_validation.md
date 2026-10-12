# Directive for Antigravity — C66, automatic measures on images already judged (no renders)

Written by Claude, 2026-10-12. **No renders. Do not close anything; do not use `monitor_and_shutdown.py`; do not
change power or system settings.** If a step fails, stop and paste the output; do not change the script or choose
another model to make a step pass. Pre-registration: `docs/prereg_metric_validation.md`.

## Step 0 — packages (allowed, nothing else)

```powershell
pip install transformers t2v_metrics
```

(`torch`, `scipy`, `Pillow` are already installed. The models download from Hugging Face on first use:
`tomg-group-umd/CSD-ViT-L`, `facebook/dinov2-large`, `openai/clip-vit-large-patch14`, and the VQAScore model
`clip-flant5-xl`.)

## Step 1 — image list and smoke test

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python metric_validation.py --selftest
python metric_validation.py --list
python metric_validation.py --smoke
```

`--list` must print `657 images, 0 missing []`. `--smoke` must print, for 3 images, a `csd` shape, a `dino`
shape, 7 genre probabilities and one `vqa` value. **If any model fails to load, stop and paste.**

## Step 2 — the measures

```powershell
python metric_validation.py --embed
```

Ends with `embed ok: 657 images; csd (657, …) dino (657, 1024) ; vqa 153`.

## Step 3 — paste back

Write `docs/RENDERS_2026-10-12_metric_validation.md` (no renders: the name keeps the usual place) with the exact
commands and outputs of Steps 1–2 inside plain triple-backtick fences. Do not commit; Claude commits. Do **not**
run `--test`.

## Not authorised

Renders, `--test`, any other model or package, changes to the script, push.
