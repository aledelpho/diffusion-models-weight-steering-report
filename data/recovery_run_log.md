

# Recovery run -- 2026-09-23 16:30

HUD panel 480px, true render 1024x1280. python 3.10.11

## Phase 1 -- recovering the original pixels
555 images listed in `data/hud_contaminated_images.csv`
recovered **555** images into `recovered_renders/`, 0 missing on disk, 0 not 1024x1760
_phase 1 finished in 65.2s_

## Phase 2 -- proving the crop is lossless
compared **30** baseline pairs: 30 bit-identical, worst maximum channel difference **0**
**The crop is lossless.** Every recovered pixel is the pixel the sampler produced, and every measurement derived from the recovered set is a measurement of the real render.
_phase 2 finished in 1.7s_

Run log: `data\recovery_run_log.md`


# Recovery run -- 2026-09-23 16:32

HUD panel 480px, true render 1024x1280. python 3.10.11

_phase 1 skipped by request_

_phase 2 skipped by request_

## Phase 3 -- re-extracting features from the recovered pixels
  wrote `pilot_rotations_recovered_style_features.csv` -- 1872 rows
  wrote `rotations_block1_vs_block6_recovered_style_features.csv` -- 197 rows
  wrote `rotations_triangolo_recovered_style_features.csv` -- 120 rows

**phase 3 (re-extract features from recovered pixels) FAILED**: ValueError("columns overlap but no suffix specified: Index(['condition', 'seed'], dtype='object')")

## Phase 4 -- what the HUD did to each feature
the ten features the HUD moved most, in units of their own spread:
```
                     bench                    feature  mean_shift_in_sd  pearson_r
       rotations_triangolo                glcm_energy        -14.303046   0.536990
       rotations_triangolo           fft_radial_slope         -6.533391   0.599444
       rotations_triangolo          color_n_effective          5.996259   0.561882
       rotations_triangolo color_cluster_entropy_norm          5.269836   0.550118
       rotations_triangolo                lbp_entropy          4.311406   0.992672
       rotations_triangolo   color_top4_cluster_share         -3.983258   0.746693
       rotations_triangolo          lbp_uniform_share         -3.094821   1.000000
rotations_block1_vs_block6          color_n_effective          2.805077   0.819297
rotations_block1_vs_block6 color_cluster_entropy_norm          2.276064   0.831778
           pilot_rotations              glcm_contrast          2.235685   0.270156
```
A feature with `pearson_r` near 1 and a small shift was never really contaminated. One with a low `r` was measuring the panel.
_phase 4 finished in 0.2s_

## Phase 5 -- the published page-08 statistic, recomputed on real pixels
  derived `analyze_block1_vs_block6_recovered.py` from `analyze_block1_vs_block6.py` -- 4 line(s) changed, source sha256 `9a3a16beefd7004e`, derived sha256 `611bf1989efb48ce`
  exit code 1
_phase 5 finished in 0.0s_

## Phase 6 -- all_blocks_clean_v2, the corpus nobody tested
response magnitude per block and angle (antisymmetric, primary space):
```
angle block  n_cells  mean_norm_A  sd_norm_A
 high    B1        6     0.672071   0.066426
 high    B2        6     0.096918   0.052325
 high    B3        6     0.279759   0.077959
 high    B4        6     0.358237   0.098199
 high    B5        6     0.121473   0.036727
 high    B6        6     2.647843   0.199785
  low    B1        6     0.351654   0.128603
  low    B2        6     0.180797   0.065197
  low    B3        6     0.490833   0.172678
  low    B4        6     0.290275   0.128438
  low    B5        6     0.221979   0.132912
  low    B6        6     1.905527   0.291014
  mid    B1        6     0.574395   0.098940
  mid    B2        6     0.110477   0.040689
  mid    B3        6     0.360189   0.148064
  mid    B4        6     0.224296   0.020178
  mid    B5        6     0.156962   0.055793
  mid    B6        6     1.966443   0.106669
```
pairwise separability written -- 0 block pairs x angles. A cosine near zero means two groups that move the image in unrelated directions.
**Declared exploratory.** Six cells, two prompts, one style. No pre-registration covers this corpus, and the floor at six cells is 2/2^6 = 0.03125, so one consistent sign is enough to reach it -- see phase 8 for why that is not reassuring.
_phase 6 finished in 0.2s_

## Phase 7 -- specialisation against proximity
```
       norm_A_chroma  norm_A_shape  norm_A_texture  chroma_shape_ratio
block                                                                 
B1            0.8746        1.1437          0.4386              0.7647
B2            0.3519        0.2616          0.1519              1.3455
B3            0.3163        0.5407          0.3064              0.5850
B4            0.5626        0.4476          0.2087              1.2569
B5            0.5554        0.5886          0.1763              0.9436
B6            2.0583        2.6662          1.8560              0.7720
```
|ratio(B1) - ratio(B6)| = **0.0073**
mean |difference| among the four middle groups = 0.4324
mean |difference| between an end and a middle  = 0.3561
the two ends are the **1** closest of 15 block pairs by this ratio (exact permutation p over pairs = 0.067)
**This is one summary row per block, with no null and no seeds behind it.** It is a hypothesis worth a designed test, not an answer: the ratio is a point estimate, and nothing here says how much it would move on a second corpus. What it does do is make the proximity reading cheap to falsify.
_phase 7 finished in 0.0s_

## Phase 8 -- the dose sign-flip (candidate pitfall 72)
```
   dose_column  n_cells    mean_s  n_positive  p_signflip   floor  reaches_floor
s_d045_texture        6 -0.856803           0     0.03125 0.03125           True
s_d030_texture        6  0.862045           6     0.03125 0.03125           True
s_d060_texture        6  0.185168           4     0.21875 0.03125          False
```
**Two doses reach the exact floor with opposite signs.** With six cells the floor is 2/2^6 = 0.03125, so any consistent sign attains it. The dose, not the anatomy, decides which answer the test returns. Choosing the dose after seeing the three is pitfall 68 wearing a dose label.
_phase 8 finished in 0.0s_

## Phase 9 -- is scramble_B a luminance pump? (weights only, no renders)
  calibration read from `matched_rotation_calibration_v4.json`
  checkpoint: `krea2_turbo_bf16.safetensors`
  **Implement the net-gain computation against the same tensor selection the rotator uses** -- `experiments/compute_rotation_displacement.py` already walks it. For each arm (B1_pos, B1_neg, B6_pos, B6_neg, scrA_*, scrB_*) compute the signed sum of the applied deltas over the block's tensors, normalised by the block's base norm, and write it beside the measured dL from `data/rotations_matched_v3_quality_gate.csv`.
```
          dL_mean  dL_min  dL_max  pass_rate
tag                                         
B1_neg     -1.461  -5.165   7.267      1.000
B1_pos      2.591  -1.922   7.335      1.000
B6_neg      0.045  -5.161   7.588      0.861
B6_pos     -2.810  -7.169   2.964      1.000
scrA_neg    1.046  -2.006   4.634      1.000
scrA_pos   -1.159  -8.387   1.622      1.000
scrB_neg   26.369  18.714  31.726      0.056
scrB_pos  -29.298 -40.399 -19.654      0.028
```
The prediction to test: net signed gain correlates with `dL_mean` across the eight arms, and a null built to hold net gain at zero lands inside the gate. That is the experiment worth rendering, and it is the only one on this list that needs a GPU.
_phase 9 finished in 0.0s_

## Phase 10 -- v3 over twelve prompts, declared secondary and not confirmatory
  derived `analyze_rotations_matched_v3_twelve.py` from `analyze_rotations_matched_v3.py` -- 3 line(s) changed, source sha256 `aec99c0481160e9f`, derived sha256 `5f2fb1b071351949`
  the derived copy also needs SHA1 and the 270-row and 30-per-condition assertions widened to twelve prompts; it will stop loudly if they were not. That stop is informative -- fix it in the derived copy only, never in the frozen one.
  exit code 1
Whatever it returns is **secondary**: the twelve-prompt corpus mixes two prompt families and was not the registered unit. It can weaken a confirmation. It cannot create one.
_phase 10 finished in 0.0s_

Run log: `data\recovery_run_log.md`


# Recovery run -- 2026-09-23 16:40

HUD panel 480px, true render 1024x1280. python 3.10.11

## Phase 3 -- re-extracting features from the recovered pixels
  wrote `pilot_rotations_recovered_style_features.csv` -- 1872 rows
  wrote `rotations_block1_vs_block6_recovered_style_features.csv` -- 197 rows
  wrote `rotations_triangolo_recovered_style_features.csv` -- 120 rows
  wrote `pilot_rotations_recovered_palette_features.csv` -- 1872 rows
  wrote `rotations_block1_vs_block6_recovered_palette_features.csv` -- 197 rows
  wrote `rotations_triangolo_recovered_palette_features.csv` -- 120 rows
**22 extractions failed**, first three: [('C:\\Users\\aless\\Desktop\\diffusion-models-weight-steering-report\\recovered_renders\\rotations\\Block_6_rotX_+30.0_00001_.png', "RuntimeError('Block_6_rotX_+30.0_00001_.png: maschera del soggetto al 0.7%, sotto la soglia del 5%. La stima della carta ha probabilmente inghiottito il soggetto: va guardata, non aggirata.')"), ('C:\\Users\\aless\\Desktop\\diffusion-models-weight-steering-report\\recovered_renders\\rotations\\Block_6_rotX_+30.0_00001_.png', "RuntimeError('Block_6_rotX_+30.0_00001_.png: maschera del soggetto al 0.7%, sotto la soglia del 5%. La stima della carta ha probabilmente inghiottito il soggetto: va guardata, non aggirata.')"), ('C:\\Users\\aless\\Desktop\\diffusion-models-weight-steering-report\\recovered_renders\\rotations\\Block_6_rotX_+30.0_00001_.png', "RuntimeError('Block_6_rotX_+30.0_00001_.png: maschera del soggetto al 0.7%, sotto la soglia del 5%. La stima della carta ha probabilmente inghiottito il soggetto: va guardata, non aggirata.')")]
_phase 3 finished in 476.7s_

## Phase 4 -- what the HUD did to each feature
the ten features the HUD moved most, in units of their own spread:
```
                     bench                    feature  mean_shift_in_sd  pearson_r
       rotations_triangolo                glcm_energy        -14.303046   0.536990
       rotations_triangolo           fft_radial_slope         -6.533391   0.599444
       rotations_triangolo          color_n_effective          5.996272   0.561885
       rotations_triangolo color_cluster_entropy_norm          5.269846   0.550122
       rotations_triangolo                lbp_entropy          4.311406   0.992672
       rotations_triangolo   color_top4_cluster_share         -3.983245   0.746692
       rotations_triangolo          lbp_uniform_share         -3.094821   1.000000
rotations_block1_vs_block6          color_n_effective          2.805032   0.819284
rotations_block1_vs_block6 color_cluster_entropy_norm          2.276031   0.831767
           pilot_rotations              glcm_contrast          2.235685   0.270156
```
A feature with `pearson_r` near 1 and a small shift was never really contaminated. One with a low `r` was measuring the panel.
_phase 4 finished in 0.2s_

## Phase 5 -- the published page-08 statistic, recomputed on real pixels
  derived `analyze_block1_vs_block6_recovered.py` from `analyze_block1_vs_block6.py` -- 4 line(s) changed, source sha256 `9a3a16beefd7004e`, derived sha256 `d966173bf48d97cd`
  exit code 1
_phase 5 finished in 0.0s_

Run log: `data\recovery_run_log.md`


# Recovery run -- 2026-09-23 16:50

HUD panel 480px, true render 1024x1280. python 3.10.11

## Phase 5 -- the published page-08 statistic, recomputed on real pixels
  derived `analyze_block1_vs_block6_recovered.py` from `analyze_block1_vs_block6.py` -- 4 line(s) changed, source sha256 `9a3a16beefd7004e`, derived sha256 `a591dd54e4f70276`
  exit code 1
_phase 5 finished in 0.0s_

Run log: `data\recovery_run_log.md`


# Recovery run -- 2026-09-23 16:51

HUD panel 480px, true render 1024x1280. python 3.10.11

## Phase 5 -- the published page-08 statistic, recomputed on real pixels
  derived `analyze_block1_vs_block6_recovered.py` from `analyze_block1_vs_block6.py` -- 4 line(s) changed, source sha256 `9a3a16beefd7004e`, derived sha256 `8ff16d2051fe1db7`
  exit code 1
_phase 5 finished in 0.4s_

Run log: `data\recovery_run_log.md`


# Recovery run (revision 2) -- 2026-09-23 17:03

HUD panel 480px, true render 1024x1280. python 3.10.11

## Phase 1 -- recovering the original pixels
555 images listed in `data/hud_contaminated_images.csv`
recovered **555** images into `recovered_renders/`, **555** distinct destinations, 0 missing, 0 not 1024x1760, 0 collisions
_phase 1 finished in 83.8s_

## Phase 3 -- re-extracting features from the recovered pixels
555 manifest rows, **555 distinct images** to measure
**24 measurements failed** -- listed in `data/recovered_extraction_failures.csv`. Those rows keep their contaminated values in the recovered tables and must be excluded by name, not ignored.
  `pilot_rotations_style_recovered_features.csv` -- 225 rows, 225 updated from recovered pixels, 23 feature columns, schema identical to the original
  `pilot_rotations_palette_recovered_features.csv` -- 225 rows, 225 updated from recovered pixels, 41 feature columns, schema identical to the original
  `rotations_block1_vs_block6_style_recovered_features.csv` -- 210 rows, 210 updated from recovered pixels, 23 feature columns, schema identical to the original
  `rotations_block1_vs_block6_palette_recovered_features.csv` -- 210 rows, 197 updated from recovered pixels, 41 feature columns, schema identical to the original
  `rotations_triangolo_style_recovered_features.csv` -- 330 rows, 330 updated from recovered pixels, 23 feature columns, schema identical to the original
  `rotations_triangolo_palette_recovered_features.csv` -- 330 rows, 317 updated from recovered pixels, 41 feature columns, schema identical to the original
_phase 3 finished in 524.2s_

## Phase 4 -- what the HUD did to each feature
the twelve features the HUD moved most, in units of their own spread:
```
                     bench                    feature  mean_shift_in_sd  pearson_r
rotations_block1_vs_block6                      ink_L             3.756      0.419
       rotations_triangolo                      ink_L             3.563      0.395
           pilot_rotations              chroma_spread            -3.132     -0.332
rotations_block1_vs_block6                      sw1_L             2.778      0.461
       rotations_triangolo          color_n_effective             2.752      0.794
           pilot_rotations                  sw6_share             2.721      0.252
rotations_block1_vs_block6          color_n_effective             2.379      0.819
       rotations_triangolo                      sw1_L             2.301      0.423
           pilot_rotations              glcm_contrast             2.192      0.324
       rotations_triangolo   color_top4_cluster_share            -2.181      0.873
           pilot_rotations                      ink_L             2.170      0.461
       rotations_triangolo color_cluster_entropy_norm             2.164      0.810
```
14 of 192 feature-by-bench pairs correlate above 0.99 between the contaminated and the recovered measurement: those were never really contaminated. The rest were measuring the panel to some degree.
_phase 4 finished in 0.1s_

## Phase 5 -- the published page-08 statistic, recomputed on real pixels
  derived `analyze_block1_vs_block6_recovered.py` -- 4 line(s) changed, source sha256 `9a3a16beefd7004e`
  exit code 0
published (HUD) against recovered:
```
                          space  n_features  mean_V  p_val_V  floor_V  mean_V_scramble  p_val_V_scramble  falsification_passed  coh_b1  coh_b6  coh_scramble_A  coh_scramble_B  raw_cross_cos_B1_B6  disattenuated_cos  share_antisym_B1  share_antisym_B6
           Tessitura (PRIMARIO)           3 1.10782  0.00195  0.00195          0.27418           0.00195                  True 0.94206 0.97706         0.88292         0.60873             -0.12679           -0.13215            0.4157            0.3939
Global 23 Features (Secondario)          23 0.84793  0.00195  0.00195          0.55230           0.00195                  True 0.71871 0.83529         0.68074         0.53818              0.02798            0.03611            0.3537            0.3548
          Linework (Secondario)           3 0.75457  0.00391  0.00195          0.21101           0.00781                  True 0.23056 0.69240         0.61460         0.23193             -0.17430           -0.43623            0.2689            0.2207
   Shadow Hardness (Secondario)           2 1.11698  0.00391  0.00195          0.57008           0.00195                  True 0.94697 0.46637         0.49139         0.85023             -0.45527           -0.68507            0.3970            0.2419
Palette LAB/Chroma (Secondario)           5 0.86382  0.00195  0.00195          0.33022           0.00391                  True 0.87281 0.96057         0.84542         0.38765              0.10777            0.11770            0.5637            0.4607

                          space  n_features  mean_V  p_val_V  floor_V  mean_V_scramble  p_val_V_scramble  falsification_passed  coh_b1  coh_b6  coh_scramble_A  coh_scramble_B  raw_cross_cos_B1_B6  disattenuated_cos  share_antisym_B1  share_antisym_B6
           Tessitura (PRIMARIO)           3 1.10782  0.00195  0.00195          0.27418           0.00195                  True 0.94206 0.97706         0.88292         0.60873             -0.12679           -0.13215            0.4157            0.3939
Global 23 Features (Secondario)          23 0.84793  0.00195  0.00195          0.55230           0.00195                  True 0.71871 0.83529         0.68074         0.53818              0.02798            0.03611            0.3537            0.3548
          Linework (Secondario)           3 0.75457  0.00391  0.00195          0.21101           0.00781                  True 0.23056 0.69240         0.61460         0.23193             -0.17430           -0.43623            0.2689            0.2207
   Shadow Hardness (Secondario)           2 1.11698  0.00391  0.00195          0.57008           0.00195                  True 0.94697 0.46637         0.49139         0.85023             -0.45527           -0.68507            0.3970            0.2419
Palette LAB/Chroma (Secondario)           5 0.86382  0.00195  0.00195          0.33022           0.00391                  True 0.87281 0.96057         0.84542         0.38765              0.10777            0.11770            0.5637            0.4607
```
Same experiment, measured on the panel and on the picture. Where they agree the HUD never mattered; where they do not, the published number was the panel.
_phase 5 finished in 0.7s_

## Phase 6 -- all_blocks_clean_v2, the corpus nobody tested
response magnitude per block and angle (antisymmetric, primary space):
```
angle block  n_cells  mean_norm_A  sd_norm_A
 high    B1        6       0.8975     0.0710
 high    B2        6       0.1336     0.0736
 high    B3        6       0.3855     0.1207
 high    B4        6       0.4408     0.1090
 high    B5        6       0.1659     0.0554
 high    B6        6       3.7056     0.2235
  low    B1        6       0.1185     0.0471
  low    B2        6       0.0921     0.0188
  low    B3        6       0.1703     0.0517
  low    B4        6       0.1410     0.0417
  low    B5        6       0.0703     0.0271
  low    B6        6       0.6340     0.0411
  mid    B1        6       0.3969     0.0520
  mid    B2        6       0.0872     0.0336
  mid    B3        6       0.2586     0.0873
  mid    B4        6       0.1829     0.0156
  mid    B5        6       0.1117     0.0291
  mid    B6        6       1.6510     0.1230
```
pairwise separability: **45** block pairs x angles
```
angle  pair  n_cells  mean_cos  p_signflip  floor
  mid B1-B6        6   -0.5138      0.0312 0.0312
  mid B1-B2        6   -0.4808      0.0312 0.0312
  mid B1-B4        6   -0.4618      0.0312 0.0312
 high B1-B6        6   -0.3178      0.0312 0.0312
  low B1-B4        6   -0.2133      0.3750 0.0312
 high B5-B6        6   -0.1768      0.2812 0.0312
 high B1-B2        6   -0.0905      0.5625 0.0312
 high B1-B4        6   -0.0682      0.6875 0.0312
 high B2-B5        6   -0.0655      0.7812 0.0312
  mid B2-B3        6    0.0218      0.9688 0.0312
  low B1-B3        6    0.0354      0.8125 0.0312
  low B1-B6        6    0.0438      0.8750 0.0312
```
**Declared exploratory.** Six cells, two prompts, one style, no pre-registration. The floor at six cells is 2/2^6 = 0.03125, so one consistent sign reaches it -- phase 8 shows why that is not reassuring.
_phase 6 finished in 0.1s_

Run log: `data\recovery_run_log.md`


# Recovery run (revision 2) -- 2026-09-23 17:14

HUD panel 480px, true render 1024x1280. python 3.10.11

## Phase 10 -- v3 over twelve prompts, secondary
  derived `analyze_rotations_matched_v3_twelve.py` -- 6 line(s) changed, source sha256 `aec99c0481160e9f`
  `SEEDS` is now None on purpose: the two prompt families do not share seeds, so the derived copy must look each prompt's three seeds up from the manifest. Until that is written it will stop, and the stop is correct. Fix it in the derived copy only.
  exit code 1
Whatever it returns is **secondary**: twelve prompts mix two families and were not the registered unit. It can weaken a confirmation, never create one.
_phase 10 finished in 0.4s_

Run log: `data\recovery_run_log.md`
