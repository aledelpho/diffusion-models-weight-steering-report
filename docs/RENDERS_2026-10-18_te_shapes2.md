# Analysis — C100 shapes with different prompts and heavier edits

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes2.py --selftest
```

```text
selftest ok
```

## First run — traceback (stopped on L06_block at d = 10)

```text
done D1_dwarf_paladin L28_mlp m 78
C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments\te_punct_encoder.py:48: RuntimeWarning: overflow encountered in cast
  return c.astype(np.float16).astype(np.float32), c.astype(np.float16), ids
C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments\te_shapes.py:32: RuntimeWarning: invalid value encountered in divide
  U = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-12)
Traceback (most recent call last):
  File "C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments\te_shapes2.py", line 188, in <module>
    if a.run: run()
  File "C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments\te_shapes2.py", line 119, in run
    m = TS.measures(sub.reshape(len(sub), -1))
  File "C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments\te_shapes.py", line 35, in measures
    _, s, vt = np.linalg.svd(U, full_matrices=False)
  File "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\lib\site-packages\numpy\linalg\_linalg.py", line 1812, in svd
    u, s, vh = gufunc(a, signature=signature)
  File "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\lib\site-packages\numpy\linalg\_linalg.py", line 113, in _raise_linalgerror_svd_nonconvergence
    raise LinAlgError("SVD did not converge")
numpy.linalg.LinAlgError: SVD did not converge
```

## Step 1 — encodes and measures (restart with Amendment 1)

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes2.py --run
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
GATE b L06 MLP 1.00 dwarf vs C67: max rel err 0.000276 (limit 0.000977)
done D1_dwarf_paladin L06_mlp p 24
done D1_dwarf_paladin L06_mlp m 36
done D1_dwarf_paladin L14_mlp p 54
done D1_dwarf_paladin L14_mlp m 63
done D1_dwarf_paladin L28_mlp p 73
done D1_dwarf_paladin L28_mlp m 78
C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments\te_punct_encoder.py:48: RuntimeWarning: overflow encountered in cast
  return c.astype(np.float16).astype(np.float32), c.astype(np.float16), ids
overflow {'prompt': 'D1_dwarf_paladin', 'edit': 'L06_block', 'sign': 'p', 'kind': 'edit', 'n_doses': 21, 'overflow': '10'}
done D1_dwarf_paladin L06_block p 90
done D1_dwarf_paladin L06_block m 102
done D1_dwarf_paladin L06+L14+L28_mlp p 114
done D1_dwarf_paladin L06+L14+L28_mlp m 126
done S1_rally L06_mlp p 150
done S1_rally L06_mlp m 162
done S1_rally L14_mlp p 180
done S1_rally L14_mlp m 189
done S1_rally L28_mlp p 199
done S1_rally L28_mlp m 204
done S1_rally L06_block p 216
done S1_rally L06_block m 228
done S1_rally L06+L14+L28_mlp p 240
done S1_rally L06+L14+L28_mlp m 252
done P2_lotuscanoe L06_mlp p 276
done P2_lotuscanoe L06_mlp m 288
done P2_lotuscanoe L14_mlp p 306
done P2_lotuscanoe L14_mlp m 315
done P2_lotuscanoe L28_mlp p 325
done P2_lotuscanoe L28_mlp m 330
done P2_lotuscanoe L06_block p 342
done P2_lotuscanoe L06_block m 354
done P2_lotuscanoe L06+L14+L28_mlp p 366
done P2_lotuscanoe L06+L14+L28_mlp m 378
done P5_comic_panels L06_mlp p 402
done P5_comic_panels L06_mlp m 414
done P5_comic_panels L14_mlp p 432
done P5_comic_panels L14_mlp m 441
done P5_comic_panels L28_mlp p 451
done P5_comic_panels L28_mlp m 456
done P5_comic_panels L06_block p 468
done P5_comic_panels L06_block m 480
done P5_comic_panels L06+L14+L28_mlp p 492
done P5_comic_panels L06+L14+L28_mlp m 504
done C4_stilllife L06_mlp p 528
done C4_stilllife L06_mlp m 540
done C4_stilllife L14_mlp p 558
done C4_stilllife L14_mlp m 567
done C4_stilllife L28_mlp p 577
done C4_stilllife L28_mlp m 582
done C4_stilllife L06_block p 594
done C4_stilllife L06_block m 606
done C4_stilllife L06+L14+L28_mlp p 618
done C4_stilllife L06+L14+L28_mlp m 630
done LN L06_mlp p 654
done LN L06_mlp m 666
done LN L14_mlp p 684
done LN L14_mlp m 693
done LN L28_mlp p 703
done LN L28_mlp m 708
done LN L06_block p 720
done LN L06_block m 732
done LN L06+L14+L28_mlp p 744
done LN L06+L14+L28_mlp m 756
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_shapes2_trajectories.csv 756
```

## Benchmark folder size

```text
Text2Img\benchmark_te_shapes2: 78 files, 52.32 MB (54866365 bytes)
```

## Run time

```text
1h 02m 44s (3764s)
```
