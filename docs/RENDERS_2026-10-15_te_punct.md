# Renders — C78 punctuation and separation

## Step 1 — the gate

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_punct.py --queue --block gate
```

```text
queued 2 block gate
```

```powershell
python te_punct.py --gate
```

```text
D1_dwarf_paladin re-render vs existing: max abs diff 0
P1_elfbrawler re-render vs existing: max abs diff 0
GATE PASS
```

## Step 2 — smoke, pilot, and natural prompts

```powershell
python te_punct.py --queue --block smoke
```

```text
queued 1 block smoke
```

```powershell
python te_punct.py --queue --block pilot
```

```text
queued 16 block pilot
```

```powershell
python te_punct.py --queue --block natural
```

```text
queued 26 block natural
```

```powershell
python te_punct.py --count
```

```text
expected 93 missing 48 ['P1_three_styles_period_krea2_seed2645751_00001_.png', 'P1_three_styles_period_krea2_seed3316624_00001_.png', 'P1_three_styles_period_krea2_seed3605551_00001_.png']
```

## Benchmark folder size

```text
Text2Img\benchmark_te_punct (official C78): 45 files, 67.69 MB (70981616 bytes)
Text2Img\benchmark_te_punct (total with 24 extra nopunct renders): 69 files, 103.58 MB (108611223 bytes)
```

## Additional exploration (authorised by Alessandro) — Unpunctuated stream

Continuous stream with no punctuation marks (commas, periods, semicolons, or BREAK) across 3 prompts x 8 seeds:

```powershell
python te_punct_nopunct.py --queue
```

```text
queued 24
```

```powershell
python te_punct_nopunct.py --count
```

```text
expected 24 missing 0 []
```

## Amendment 3 pilot

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_punct2.py --queue --block pilot2
```

```text
queued 16 block pilot2
```

```powershell
python te_punct2.py --count
```

```text
expected 16 missing 0 []
```

## Amendment 4 versions

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
python te_punct2.py --queue --block versions
```

```text
queued 96 block versions
```

```powershell
python te_punct2.py --count
```

```text
expected 112 missing 0 []
```

## Benchmark folder size (after Amendment 4)

```text
Text2Img\benchmark_te_punct: 181 files, 318.52 MB (333992654 bytes)
  - C78 original: 45 files, 67.69 MB (70981616 bytes)
  - C78 extra nopunct: 24 files, 35.89 MB (37629607 bytes)
  - C78 amendment 3 pilot2: 16 files, 30.75 MB (32244645 bytes)
  - C78 amendment 4 versions: 96 files, 184.19 MB (193136786 bytes)
```
