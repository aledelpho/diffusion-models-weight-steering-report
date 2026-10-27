# Renders & Analysis — C111, "Photo of a tree" (calibration + test; amendment 1)

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
$PY = "D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
& $PY te_tree.py --selftest
```

```text
selftest ok; 28 cards with every perturbation reached (+4 repeats)
```

## Step 1 — automatic calibration

```powershell
& $PY te_tree.py --calibrate
```

```text
round: 32 strengths to render x 2 seeds
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
queued 64

round: 5 strengths to render x 2 seeds
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
queued 10

round: 2 strengths to render x 2 seeds
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
queued 4

calibration done: 8 of 8 pairs reached; 8 in the window
```

## Step 2 — test plan, gate, main renders

```powershell
& $PY te_tree.py --plan
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
plan rows: 73 (73 if every perturbation was reached)
```

```powershell
& $PY te_tree.py --queue --block gate
```

```text
queued 1
```

```powershell
& $PY te_tree.py --queue --block main
```

```text
queued 72
```

```powershell
& $PY te_tree.py --gate
```

```text
T1_tree_C0_krea2_seed2645751_00001_.png vs T1_tree_TEXT_krea2_seed2645751_00001_.png: max abs diff 0
GATE PASS
```

```powershell
& $PY te_tree.py --count
```

```text
expected 73 missing 0 []
```

```powershell
& $PY te_tree.py --analyze
```

```text
Rule 1 plain seeds: median pairwise D of the 8 plain trees | 0.475 (bar 0.15); median D of the real edits from the plain tree 0.257 | the seeds already vary
Rule 1 reference: D1_dwarf_paladin plain, pairwise D over its 4 C109 seeds (reported) | median 0.134 | -
Rule 1 reference: E2_elf_rogue plain, pairwise D over its 4 C109 seeds (reported) | median 0.083 | -
Rule 1 reference: O4_halforc_fighter plain, pairwise D over its 4 C109 seeds (reported) | median 0.115 | -
Rule 1 reference: G5_gnome_wizard plain, pairwise D over its 4 C109 seeds (reported) | median 0.068 | -
Rule 1 reference: S1_rally plain, pairwise D over its 4 C109 seeds (reported) | median 0.178 | -
Rule 1 reference: C4_stilllife plain, pairwise D over its 4 C109 seeds (reported) | median 0.090 | -
Rule 1 reference: P2_lotuscanoe plain, pairwise D over its 4 C109 seeds (reported) | median 0.057 | -
Rule 1 reference: LN plain, pairwise D over its 4 C109 seeds (reported) | median 0.140 | -
Reported: direction of the change shared across seeds (mean cosine of the DINOv2 displacements) | edits 0.057; different perturbations at different seeds 0.009; seed changes of the plain tree -0.052 | -
Reported: per perturbation, mean cosine across seeds | E05 0.02; E06 0.08; E14 0.04; E26 0.01; E28 0.09; P01 -0.01; P06 0.09; P10 0.14 | -
Reported: median pairwise D across seeds after each perturbation (plain above) | E05 0.706; E06 0.632; E14 0.549; E26 0.498; E28 0.601; P01 0.476; P06 0.632; P10 0.746 | -
Reported: perturbations that did not reach the calibration window | none | -
```

## Benchmark folder size

```text
Text2Img\benchmark_te_tree: 153 files, 296.85 MB (311267156 bytes)
```

## Run time

```text
1h 31m 09s (5469s)
```
