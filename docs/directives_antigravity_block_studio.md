# Directive for Antigravity — install and check Block Studio (2026-10-06)

Written by Claude for Alessandro. Block Studio is a local page to move single-block weights, press
Generate and see the image, with − / + buttons that show what each block does alone at the same seed
(from the portrait atlas). The code is already written and committed:
`experiments/block_studio/block_studio.py` (standard library only) and
`experiments/block_studio/index.html`. **Do not modify them.** Nothing is installed into ComfyUI:
the page talks to ComfyUI's HTTP API from Python.

**Authorised renders: only the 2 of step 2.** Do not shut down or close anything; do not use
`monitor_and_shutdown.py`. If a step fails, stop and paste the output.

## Step 1 — ComfyUI must already be running

ComfyUI at http://127.0.0.1:8188 with the Arthemy Krea2 Tuner, as for the benches. If it is not
running, stop and tell Alessandro; do not start or restart it yourself.

## Step 2 — check that the studio reproduces the bench (2 renders)

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report
python experiments\block_studio\block_studio.py --check
```

It renders the dwarf at seed 2236067 with no edit and with blk09 +0.55, through the studio's own
path, and compares each with the existing atlas file pixel for pixel. It must end with
`CHECK PASS - the studio reproduces the bench`. If it prints FAIL, stop and paste the output.

## Step 3 — a launcher on the Desktop

Create `C:\Users\aless\Desktop\Block Studio.bat` with exactly:

```bat
@echo off
cd /d C:\Users\aless\Desktop\diffusion-models-weight-steering-report
python experiments\block_studio\block_studio.py
pause
```

## Step 4 — open it once, do not generate

Double-click `Block Studio.bat`. A console opens and the browser opens http://127.0.0.1:8199/.
Check that the top right says **ComfyUI connected** and that, with "dwarf paladin" and seed 2236067
selected, the − / + buttons beside the blocks show doses (not "ref"). Click blk09 "+": the dwarf
reference appears. **Do not press Generate.** Close the browser tab and the console window you
opened in this step (only those).

## Step 5 — paste back

The output of step 2 and yes/no for the checks of step 4. Do not commit anything.

## Not authorised

No renders beyond the 2 of step 2, no change to the code, no installation into ComfyUI.
