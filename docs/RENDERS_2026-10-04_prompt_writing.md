# Renders: Prompt Writing Experiment (2026-10-04)

This document provides instructions for Alessandro to launch the C45 prompt writing experiment renders.

## 1. Overview
- **Total images to render**: 401
- **Output folder**: C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_prompt_writing
- **Expected disk use**: ~1.3 GB (401 images × ~3.3 MB each)

## 2. Launch Sequence

### Step 1: Reproducibility Check
Do **NOT** run the full queue immediately. First, we must ensure the aseline matches our previous runs identically.

1. Open ComfyUI and ensure the environment is ready.
2. Queue only the REPRO row: `python experiments/queue_prompt_writing.py --first 1` (option added by Claude on 2026-10-04; the earlier advice to stop the script and clear the queue is withdrawn, because the script posts every row at once).
3. Wait for REPRO_V1_Original_baseline_krea2_seed3141592_00001_.png to be generated in the output folder.

### Step 2: Pixel-by-Pixel Verification
Run the verification script from the terminal:
```bash
python experiments/check_prompt_writing_repro.py
```
- If the output is **PASS** (max absolute difference is 0), proceed to Step 3.
- If the output is **FAIL**, **STOP IMMEDIATELY**. Do not queue the rest of the renders.

### Step 3: Run the Full Queue
Once reproducibility is confirmed, queue the rest of the experiment:
```bash
python experiments/queue_prompt_writing.py
```
*(Note: The script is designed to skip files that already exist on disk, so it will safely skip the REPRO image and continue with the remaining 400.)*

---

## Self-Check Validation

**Sample 1: S2_W3_tags (Row ID: 328)**
- Expected SHA-1: 68e2b88cd02a4b181097d44f96d9bbe5c0f54120
- CSV SHA-1:      68e2b88cd02a4b181097d44f96d9bbe5c0f54120
- Match:          ✅ YES
- Prereg preview: dreamlike fantasy scene, top-down view, perfectly vertical o... serene, mysterious, award winning, breathtaking masterpiece
- CSV preview:    dreamlike fantasy scene, top-down view, perfectly vertical o... serene, mysterious, award winning, breathtaking masterpiece

**Sample 2: S1_C1_flamegauntlet (Row ID: 58)**
- Expected SHA-1: 4520c63271bfd9a7380c815930d04f10911d3f75
- CSV SHA-1:      4520c63271bfd9a7380c815930d04f10911d3f75
- Match:          ✅ YES
- Prereg preview: realistic western comics style, bold ink outlines, hatched s...dows and sharp orange highlights along her flaming gauntlet.
- CSV preview:    realistic western comics style, bold ink outlines, hatched s...dows and sharp orange highlights along her flaming gauntlet.

**Sample 3: S1_W3_tags (Row ID: 13)**
- Expected SHA-1: c6ea6966754348d798e120bdca40a445c44f9bdb
- CSV SHA-1:      c6ea6966754348d798e120bdca40a445c44f9bdb
- Match:          ✅ YES
- Prereg preview: realistic western comics style, bold ink outlines, hatched s...light, deep amber shadows, sharp blue highlights on gauntlet
- CSV preview:    realistic western comics style, bold ink outlines, hatched s...light, deep amber shadows, sharp blue highlights on gauntlet


## Phase 2 — Launch Log
### Commands Run
`ash
python experiments/queue_prompt_writing.py --first 1
python experiments/check_prompt_writing_repro.py
python experiments/queue_prompt_writing.py
python experiments/prompt_writing_eye_sheets.py
`

### Reproducibility Output
`	ext
PASS: Images are exactly pixel-identical (max diff: 0)
`

### Verification
- **Total PNGs Found:** 401
- **Expected PNGs:** 401
- **Missing Files:** None
- **Duplicate Files:** None

### Eye Sheets Generated
The visual inspection HTML was successfully generated at:
C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_prompt_writing\eye_sheets.html
