# Analysis — C101 shapes of the push across every layer of the text encoder

## Step 0 — selftest

```powershell
cd C:\Users\aless\Desktop\diffusion-models-weight-steering-report\experiments
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes_layers.py --selftest
```

```text
selftest ok
```

## Step 1 — encodes and measures

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" te_shapes_layers.py --run
```

```text
P1_elfbrawler_baseline vs C67 .npz: cond bit-identical=True, ids bit-identical=True, max_abs_diff=0.0
GATE PASS
GATE b L06 MLP 1.00 dwarf vs C67: max rel err 0.000276 (limit 0.000977)
GATE c PASS
done L00_mlp p 28
done L00_mlp m 42
done L01_mlp p 70
done L01_mlp m 84
done L02_mlp p 110
done L02_mlp m 123
done L03_mlp p 149
done L03_mlp m 162
done L04_mlp p 188
done L04_mlp m 201
done L05_mlp p 225
done L05_mlp m 237
GATE d L06_mlp p edit vs C93: rel err 0.000000 (limit 0.000977)
GATE d L06_mlp p control vs C93: rel err 0.000000 (limit 0.000977)
done L06_mlp p 261
GATE d L06_mlp m edit vs C93: rel err 0.000000 (limit 0.000977)
done L06_mlp m 273
done L07_mlp p 297
done L07_mlp m 309
done L08_mlp p 331
done L08_mlp m 342
done L09_mlp p 364
done L09_mlp m 375
done L10_mlp p 397
done L10_mlp m 408
done L11_mlp p 428
done L11_mlp m 438
done L12_mlp p 458
done L12_mlp m 468
done L13_mlp p 488
done L13_mlp m 498
GATE d L14_mlp p edit vs C93: rel err 0.000000 (limit 0.000977)
GATE d L14_mlp p control vs C93: rel err 0.000000 (limit 0.000977)
done L14_mlp p 516
GATE d L14_mlp m edit vs C93: rel err 0.000000 (limit 0.000977)
done L14_mlp m 525
done L15_mlp p 543
done L15_mlp m 552
done L16_mlp p 570
done L16_mlp m 579
done L17_mlp p 595
done L17_mlp m 603
done L18_mlp p 619
done L18_mlp m 627
done L19_mlp p 643
done L19_mlp m 651
done L20_mlp p 665
done L20_mlp m 672
done L21_mlp p 686
done L21_mlp m 693
done L22_mlp p 707
done L22_mlp m 714
done L23_mlp p 726
done L23_mlp m 732
done L24_mlp p 744
done L24_mlp m 750
done L25_mlp p 762
done L25_mlp m 768
done L26_mlp p 778
done L26_mlp m 783
done L27_mlp p 793
done L27_mlp m 798
GATE d L28_mlp p edit vs C93: rel err 0.000000 (limit 0.000977)
GATE d L28_mlp p control vs C93: rel err 0.000000 (limit 0.000977)
done L28_mlp p 808
GATE d L28_mlp m edit vs C93: rel err 0.000000 (limit 0.000977)
done L28_mlp m 813
done L29_mlp p 821
done L29_mlp m 825
done L30_mlp p 833
done L30_mlp m 837
done L31_mlp p 845
done L31_mlp m 849
done L32_mlp p 855
done L32_mlp m 858
done L33_mlp p 864
done L33_mlp m 867
done L34_mlp p 873
done L34_mlp m 876
done L00_attn p 890
done L00_attn m 904
done L01_attn p 918
done L01_attn m 932
done L02_attn p 945
done L02_attn m 958
done L03_attn p 971
done L03_attn m 984
done L04_attn p 997
done L04_attn m 1010
done L05_attn p 1022
done L05_attn m 1034
GATE d L06_attn p edit vs C93: rel err 0.000000 (limit 0.000977)
done L06_attn p 1046
GATE d L06_attn m edit vs C93: rel err 0.000000 (limit 0.000977)
done L06_attn m 1058
done L07_attn p 1070
done L07_attn m 1082
done L08_attn p 1093
done L08_attn m 1104
done L09_attn p 1115
done L09_attn m 1126
done L10_attn p 1137
done L10_attn m 1148
done L11_attn p 1158
done L11_attn m 1168
done L12_attn p 1178
done L12_attn m 1188
done L13_attn p 1198
done L13_attn m 1208
GATE d L14_attn p edit vs C93: rel err 0.000000 (limit 0.000977)
done L14_attn p 1217
GATE d L14_attn m edit vs C93: rel err 0.000000 (limit 0.000977)
done L14_attn m 1226
done L15_attn p 1235
done L15_attn m 1244
done L16_attn p 1253
done L16_attn m 1262
done L17_attn p 1270
done L17_attn m 1278
done L18_attn p 1286
done L18_attn m 1294
done L19_attn p 1302
done L19_attn m 1310
done L20_attn p 1317
done L20_attn m 1324
done L21_attn p 1331
done L21_attn m 1338
done L22_attn p 1345
done L22_attn m 1352
done L23_attn p 1358
done L23_attn m 1364
done L24_attn p 1370
done L24_attn m 1376
done L25_attn p 1382
done L25_attn m 1388
done L26_attn p 1393
done L26_attn m 1398
done L27_attn p 1403
done L27_attn m 1408
done L28_attn p 1413
done L28_attn m 1418
done L29_attn p 1422
done L29_attn m 1426
done L30_attn p 1430
done L30_attn m 1434
done L31_attn p 1438
done L31_attn m 1442
done L32_attn p 1445
done L32_attn m 1448
done L33_attn p 1451
done L33_attn m 1454
done L34_attn p 1457
done L34_attn m 1460
wrote C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data\te_shapes_layers_trajectories.csv 1460
```

## Step 2 — figures

```powershell
& "C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe" plot_te_shapes_layers.py
```

```text
wrote C:\StabilityMatrix-win-x64\Data\Images\Text2Img\_te_shapes\C101_overview.png
wrote C:\StabilityMatrix-win-x64\Data\Images\Text2Img\_te_shapes\C101_grid_mlp_p.png
wrote C:\StabilityMatrix-win-x64\Data\Images\Text2Img\_te_shapes\C101_grid_mlp_m.png
wrote C:\StabilityMatrix-win-x64\Data\Images\Text2Img\_te_shapes\C101_grid_attn_p.png
wrote C:\StabilityMatrix-win-x64\Data\Images\Text2Img\_te_shapes\C101_grid_attn_m.png
```

## Benchmark folder size

```text
Text2Img\benchmark_te_shapes_layers: 175 files, 95.87 MB (100526074 bytes)
```

## Run time

```text
1h 58m 09s (7089s)
```
