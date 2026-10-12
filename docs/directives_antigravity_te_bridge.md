# Directive for Antigravity — C69, attention maps in the DiT (25 renders, authorised by Alessandro on 2026-10-12)

Written by Claude. **Do not close anything. Do not use `monitor_and_shutdown.py`. Do not change power or system
settings.** If a step fails, stop and paste the output. Do not change the script, the plan or the node to make a
step pass.

Pre-registration: `docs/prereg_te_bridge.md`. The plan is frozen (`data/te_bridge_plan.csv`, 25 rows): do **not**
run `--plan`.

## Step 0 — install the attention probe node

```powershell
Copy-Item -Recurse C:\Users\aless\Desktop\diffusion-models-weight-steering-report\tools\comfyui_krea2_attnprobe `
  C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\custom_nodes\comfyui_krea2_attnprobe
```

Restart ComfyUI the usual way, through StabilityMatrix. Check that the console says the node loaded
(`Krea2AttentionProbe`). The ArthemyKrea2CLIPTuner node must also be loaded, as for C65.

## Step 1 — one render, then the reproduction gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_bridge.py --queue --first 1
```

Wait until both of these exist:

* the image `Text2Img\benchmark_te_bridge\V1_Original_baseline_krea2_seed3141592_00001_.png`;
* 9 files `step00.npz` … `step08.npz` in `Text2Img\benchmark_te_bridge\attn\V1_Original_baseline`.

Then run:

```powershell
python te_bridge.py --repro
```

It must print `REPRO PASS: 1 renders checked …`. If it prints `FAIL`, **stop** and paste the output. If ComfyUI shows
an error (for example out of memory inside the probe), stop and paste the console lines.

## Step 2 — the other 24 renders

```powershell
python te_bridge.py --queue
```

When ComfyUI's queue is empty, run:

```powershell
python te_bridge.py --count
python te_bridge.py --repro
```

`--count` must print `expected 25 missing 0 []`. `--repro` must print `REPRO PASS: 25 renders checked …`.

## Step 3 — paste back

Write `docs/RENDERS_2026-10-12_te_bridge.md`. Put the exact commands and outputs of Steps 1–2 inside plain
triple-backtick fences. Include the size of `Text2Img\benchmark_te_bridge`, and the render time per image if
ComfyUI's console shows it.

Do not commit; Claude commits. Do **not** run `--analyze`; Claude runs it.

## Not authorised

* Any render outside the plan.
* `--plan` or `--analyze`.
* Changes to the script, the plan or the node.
* Any change to ComfyUI other than copying the node folder.
* Push.
