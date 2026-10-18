# Result C48 — How much each block writes into the residual stream

Date: 2026-10-17
Pre-registration: `docs/prereg_residual_probe.md`
Data: `data/residual_probe_raw.csv` (5,796 rows = 23 runs × 9 steps × 28 blocks), `data/residual_probe_blocks.csv` (28 rows), `data/residual_probe_test.csv` (4 rows)
Script: `experiments/analyze_residual_probe.py`

## 1. Reproducibility gate (`analyze_residual_probe.py --repro`)

All 23 baseline renders generated with `ArthemyResidualProbe` attached are pixel-identical (`max abs diff = 0`) to the existing baselines across `benchmark_single_blocks_styles` (12), `benchmark_single_blocks_v3` (6), and `benchmark_single_blocks_v4` (5):

```text
C1_blacksmith_seed2718281 max abs diff 0
C2_rally_seed2718281 max abs diff 0
C3_fox_seed2718281 max abs diff 0
C4_stilllife_seed2718281 max abs diff 0
E1_cartoon_seed2718281 max abs diff 0
E2_watercolor_seed2718281 max abs diff 0
E3_oil_seed2718281 max abs diff 0
E4_colorpencil_seed2718281 max abs diff 0
E5_childrensbook_seed2718281 max abs diff 0
E6_claymation_seed2718281 max abs diff 0
E7_sepiaphoto_seed2718281 max abs diff 0
E8_cartoon_styleend_seed2718281 max abs diff 0
P1_crown_topdown_seed1234567 max abs diff 0
P1_elfbrawler_seed3141592 max abs diff 0
P2_crown_bottomup_seed1234567 max abs diff 0
P2_lotuscanoe_seed3141592 max abs diff 0
P3_archerforest_seed3141592 max abs diff 0
P3_crown_rusted_seed1234567 max abs diff 0
P4_crown_glass_seed1234567 max abs diff 0
P4_selfie_seed1618033 max abs diff 0
P5_comic_panels_seed1234567 max abs diff 0
P5_gingervampire_seed1618033 max abs diff 0
P6_ghostgirl_seed1618033 max abs diff 0
REPRO PASS 23 images
```

## 2. Pre-registered decision rules (`data/residual_probe_test.csv`)

| Test | Value | Rule | Verdict |
|---|---:|---|---|
| **P1** — `Spearman(ratio, stability)` (raw, 28 blocks) | `+0.49` | `≤ -0.50` supported, `> -0.30` refuted | **refuted** |
| **P1b** — `Spearman(ratio, stability)` (depth removed, reported) | `-0.056` | reported | — |
| **P2** — block with largest `mlp_ratio` among blocks `02..20` | `10` | `8` or `9` supported, otherwise refuted | **refuted** |
| **P3** — `Spearman(stream, block)` (stream norm grows with depth) | `+0.99` | `≥ +0.80` supported | **supported** |

## 3. Block-by-block profile (`data/residual_probe_blocks.csv`)

| block | stream | write | ratio | attn_write | mlp_write | cos_write_stream | attn_ratio | mlp_ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 32.286481 | 1420.598307 | 44.316856 | 137.993141 | 1383.813137 | 0.263539 | 4.274022 | 42.860451 |
| 1 | 1429.444990 | 298.831099 | 0.209581 | 276.645860 | 59.064857 | -0.305458 | 0.193534 | 0.041320 |
| 2 | 1364.013371 | 96.562651 | 0.071292 | 90.505915 | 54.889929 | -0.095464 | 0.066353 | 0.040241 |
| 3 | 1358.833356 | 80.566328 | 0.059797 | 54.309081 | 57.955303 | -0.002643 | 0.039967 | 0.042651 |
| 4 | 1360.996666 | 103.313572 | 0.076117 | 76.198816 | 64.357222 | 0.166777 | 0.055988 | 0.047287 |
| 5 | 1384.697207 | 153.445579 | 0.110110 | 99.403229 | 98.249165 | 0.226770 | 0.071787 | 0.070954 |
| 6 | 1429.375285 | 171.795914 | 0.119660 | 108.078292 | 118.591891 | 0.280115 | 0.075612 | 0.082968 |
| 7 | 1490.849347 | 209.341926 | 0.139699 | 127.244612 | 168.170450 | 0.318165 | 0.085350 | 0.112802 |
| 8 | 1576.206065 | 266.559737 | 0.167415 | 160.443685 | 246.514976 | 0.319386 | 0.101791 | 0.156398 |
| 9 | 1695.269663 | 270.955515 | 0.158324 | 232.919781 | 301.216155 | 0.168109 | 0.137394 | 0.177680 |
| 10 | 1774.661726 | 1372.713393 | 0.771557 | 388.125317 | 1086.667864 | 0.622932 | 0.218704 | 0.612324 |
| 11 | 2844.292477 | 536.588850 | 0.189567 | 404.753487 | 537.760482 | 0.379996 | 0.142304 | 0.189067 |
| 12 | 3083.478689 | 539.198384 | 0.173800 | 459.223763 | 548.293032 | 0.179828 | 0.148930 | 0.177816 |
| 13 | 3233.821729 | 641.255437 | 0.197821 | 378.494034 | 592.599323 | 0.479422 | 0.117042 | 0.183250 |
| 14 | 3584.414710 | 654.329434 | 0.182114 | 455.435923 | 566.070155 | 0.355065 | 0.127060 | 0.157925 |
| 15 | 3861.704178 | 731.697132 | 0.189409 | 472.075385 | 613.309822 | 0.343315 | 0.122245 | 0.158818 |
| 16 | 4154.847641 | 726.480368 | 0.174373 | 558.183965 | 549.690817 | 0.253740 | 0.134345 | 0.132301 |
| 17 | 4409.698971 | 806.199035 | 0.182266 | 561.825138 | 707.702030 | 0.076622 | 0.127407 | 0.160488 |
| 18 | 4532.193542 | 1221.595312 | 0.269088 | 907.633440 | 971.407238 | 0.177361 | 0.200264 | 0.214335 |
| 19 | 4857.658170 | 1565.286943 | 0.321796 | 981.548849 | 1507.014347 | -0.301997 | 0.202062 | 0.310235 |
| 20 | 4597.353143 | 1760.138790 | 0.382484 | 1463.231840 | 1640.234732 | 0.204116 | 0.318277 | 0.356778 |
| 21 | 5218.332442 | 2683.364681 | 0.513539 | 1374.281598 | 2486.555025 | -0.173920 | 0.263356 | 0.476504 |
| 22 | 5364.590134 | 2810.600069 | 0.523749 | 2354.450957 | 2224.580065 | 0.059739 | 0.438887 | 0.414678 |
| 23 | 6213.312206 | 2866.579373 | 0.461218 | 2286.324733 | 2782.155648 | 0.133097 | 0.367972 | 0.447773 |
| 24 | 7142.589299 | 4432.939841 | 0.621228 | 3253.093102 | 3666.504572 | 0.194933 | 0.455450 | 0.513330 |
| 25 | 9083.505473 | 5840.583804 | 0.644640 | 4536.374537 | 4346.910563 | -0.015951 | 0.499408 | 0.478550 |
| 26 | 10738.667274 | 9374.467462 | 0.879891 | 5329.242530 | 6530.385137 | 0.315432 | 0.496267 | 0.608119 |
| 27 | 16306.944921 | 16210.187336 | 0.993196 | 6971.171444 | 12405.835223 | 0.224585 | 0.427497 | 0.760770 |

## 4. What the numbers show

1. **The residual stream grows 505× from input to output (P3 supported, $\rho = +0.99$).** Block 0 enters at `32.29` and its MLP writes `1383.81` (`ratio = 44.32`, `mlp_ratio = 42.86`), establishing the initial stream norm (`1429.44` at Block 1). From Block 2 (`1364.01`) to Block 27 (`16306.94`), the stream norm rises almost monotonically.
2. **Why P1 failed ($\rho = +0.49$, depth-removed $-0.056$): late blocks write *more* relative to the stream, not less.** The hypothesis behind P1 was that blocks 21–27 keep the layout (`layout r = 0.88`) because their writes are small relative to a large residual stream. In reality, `ratio` is largest in blocks 21–27 (`0.46` to `0.99`) and smallest in blocks 02–09 (`0.06` to `0.17`). So write size does not explain why late blocks keep the layout. A reading consistent with page 21, not tested here: by block 21 the composition is already fixed, and the large late writes act on the surface (saturation, grain, sharpness); blocks 26 (`ratio = 0.88`) and 27 (`ratio = 0.99`) are also the first to break the surface when pushed.
3. **Block 10 is the middle-stack write spike (`ratio = 0.77`, `mlp_ratio = 0.61`, `cos = +0.62`).** P2 predicted that among blocks 02–20 the largest `mlp_ratio` would sit at block 08 or 09, where the MLP gate's top singular value peaks (C46). Instead, blocks 08 and 09 have `mlp_ratio = 0.156` and `0.178`, while **block 10** — the third member of the `08–10` positive group — spikes to `mlp_ratio = 0.612` (`write = 1372.71`), jumping the stream norm from `1774.66` to `2844.29` in a single block before blocks 11–17 settle back to `ratio = 0.17`–`0.20`.
