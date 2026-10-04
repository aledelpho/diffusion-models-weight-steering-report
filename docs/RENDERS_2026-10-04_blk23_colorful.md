# Renders: blk23 vs "colorful" Experiment (2026-10-04)

## Commands Run
`ash
python experiments/blk23_colorful.py --queue --first 1
python experiments/blk23_colorful.py --repro
python experiments/blk23_colorful.py --queue
python experiments/blk23_colorful.py --repro
`

## Output of Step 2 (Reproducibility check on first image)
`	ext
E1_cartoon       baseline    max abs diff 0
MISSING E1_cartoon_b23_m0.300_krea2_seed2718281_00001_.png
MISSING E1_cartoon_b23_p0.300_krea2_seed2718281_00001_.png
MISSING E3_oil_baseline_krea2_seed2718281_00001_.png
MISSING E3_oil_b23_m0.300_krea2_seed2718281_00001_.png
MISSING E3_oil_b23_p0.300_krea2_seed2718281_00001_.png
MISSING E7_sepiaphoto_baseline_krea2_seed2718281_00001_.png
MISSING E7_sepiaphoto_b23_m0.300_krea2_seed2718281_00001_.png
MISSING E7_sepiaphoto_b23_p0.300_krea2_seed2718281_00001_.png
MISSING C2_rally_baseline_krea2_seed2718281_00001_.png
MISSING C2_rally_b23_m0.300_krea2_seed2718281_00001_.png
MISSING C2_rally_b23_p0.300_krea2_seed2718281_00001_.png
MISSING C3_fox_baseline_krea2_seed2718281_00001_.png
MISSING C3_fox_b23_m0.300_krea2_seed2718281_00001_.png
MISSING C3_fox_b23_p0.300_krea2_seed2718281_00001_.png
MISSING C4_stilllife_baseline_krea2_seed2718281_00001_.png
MISSING C4_stilllife_b23_m0.300_krea2_seed2718281_00001_.png
MISSING C4_stilllife_b23_p0.300_krea2_seed2718281_00001_.png
MISSING P3_archerforest_baseline_krea2_seed3141592_00001_.png
MISSING P3_archerforest_b23_m0.300_krea2_seed3141592_00001_.png
MISSING P3_archerforest_b23_p0.300_krea2_seed3141592_00001_.png
MISSING P3_archerforest_b23_p0.150_krea2_seed3141592_00001_.png
MISSING P4_selfie_baseline_krea2_seed1618033_00001_.png
MISSING P4_selfie_b23_m0.300_krea2_seed1618033_00001_.png
MISSING P4_selfie_b23_p0.300_krea2_seed1618033_00001_.png
MISSING P4_selfie_b23_p0.150_krea2_seed1618033_00001_.png
REPRO FAIL (1 pairs)
`

## Output of Step 4 (Full reproducibility check)
`	ext
E1_cartoon       baseline    max abs diff 0
E1_cartoon       b23_m0.300  max abs diff 0
E1_cartoon       b23_p0.300  max abs diff 0
E3_oil           baseline    max abs diff 0
E3_oil           b23_m0.300  max abs diff 0
E3_oil           b23_p0.300  max abs diff 0
E7_sepiaphoto    baseline    max abs diff 0
E7_sepiaphoto    b23_m0.300  max abs diff 0
E7_sepiaphoto    b23_p0.300  max abs diff 0
C2_rally         baseline    max abs diff 0
C2_rally         b23_m0.300  max abs diff 0
C2_rally         b23_p0.300  max abs diff 0
C3_fox           baseline    max abs diff 0
C3_fox           b23_m0.300  max abs diff 0
C3_fox           b23_p0.300  max abs diff 0
C4_stilllife     baseline    max abs diff 0
C4_stilllife     b23_m0.300  max abs diff 0
C4_stilllife     b23_p0.300  max abs diff 0
P3_archerforest  baseline    max abs diff 0
P3_archerforest  b23_m0.300  max abs diff 0
P3_archerforest  b23_p0.300  max abs diff 0
P3_archerforest  b23_p0.150  max abs diff 0
P4_selfie        baseline    max abs diff 0
P4_selfie        b23_m0.300  max abs diff 0
P4_selfie        b23_p0.300  max abs diff 0
P4_selfie        b23_p0.150  max abs diff 0
REPRO PASS (26 pairs)
`

## Output of Step 5 (File count verification)
`	ext
Total PNGs found: 128
Total Expected: 128
No missing files!
No duplicates found!
`
