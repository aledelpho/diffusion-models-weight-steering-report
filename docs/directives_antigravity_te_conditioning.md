# Directive for Antigravity — C67, reading the text encoder's output (no images; authorised by Alessandro on 2026-10-12)

Written by Claude. **No image renders. Do not close anything; do not use `monitor_and_shutdown.py`; do not change
power or system settings.** If a step fails, stop and paste the output; do not change the script, the plan or the
node to make a step pass. Pre-registration: `docs/prereg_te_conditioning.md`. The plan is frozen
(`data/te_conditioning_plan.csv`, 721 rows): do **not** run `--plan`.

## Step 0 — install the probe node

Copy the folder `tools\comfyui_krea2_probe` of the repository into ComfyUI's custom nodes:

```powershell
Copy-Item -Recurse C:\Users\aless\Desktop\diffusion-models-weight-steering-report\tools\comfyui_krea2_probe `
  C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\comfyui_krea2_probe
```

Restart ComfyUI (the usual way, through StabilityMatrix) and check the console says the node loaded
(`Krea2ConditioningProbe`). The ArthemyKrea2CLIPTuner node must be loaded as for C64.

## Step 1 — determinism gate (two encodes)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_conditioning.py --queue --first 2
```

When `Text2Img\benchmark_te_conditioning\elf\P1_elfbrawler_baseline.npz` and `..._baseline_again.npz` exist,
queue the rest (Step 2) and, after it, run the gate (Step 3). Encodes take seconds each; ComfyUI loads the DiT once
because the reset-patcher node needs it, but no sampling runs.

## Step 2 — the other 719 encodes

```powershell
python te_conditioning.py --queue
```

The script sends the baselines first; the "diff" encodes read them. When ComfyUI's queue is empty:

```powershell
python te_conditioning.py --count
```

Must print `expected 721 missing 0 []`.

## Step 3 — gate

```powershell
python te_conditioning.py --gate
```

Must print `determinism: identical` and `GATE PASS`. If it prints `FAIL`, **stop** and paste.

## Step 4 — reduce and logit lens

```powershell
python te_conditioning.py --reduce
python te_conditioning.py --logitlens
```

`--reduce` ends with `reduce ok: 686 edits, …`; `--logitlens` reads `C:\StabilityMatrix-win-x64\Data\Models\TextEncoders\qwen3vl_4b_bf16.safetensors`
(only the token-embedding tensor) and ends with `logit lens ok: …`. If `safetensors` is missing, `pip install
safetensors` is allowed.

## Step 5 — paste back

Write `docs/RENDERS_2026-10-12_te_conditioning.md` with the exact commands and outputs of Steps 1–4 inside plain
triple-backtick fences, and list the size of `Text2Img\benchmark_te_conditioning`. Do not commit; Claude commits.
Do **not** run `--test`.

## Not authorised

Image renders, `--plan`, `--test`, changes to the script, the plan or the node, any change to ComfyUI other than
copying the node folder, push.
