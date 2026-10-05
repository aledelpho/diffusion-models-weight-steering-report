# Renders: Standard Metrics Computation (2026-10-05)

## Commands Run
`ash
<venv python> -m pip install piq --no-deps
<venv python> -c "import piq, open_clip; print(piq.__version__)"
<venv python> experiments/standard_metrics.py --bench c47
<venv python> experiments/standard_metrics.py --bench c49
<venv python> experiments/standard_metrics.py --bench c45
`

## Printed Outputs
`	ext
piq.__version__: 0.8.0
c47: written 128 rows
c49: written 432 rows
c45: written 500 rows
`

## Row Counts Verification
`	ext
data/standard_metrics_c47.csv: 128 rows
data/standard_metrics_c49.csv: 432 rows
data/standard_metrics_c45.csv: 500 rows
data/standard_metrics_c47_emb.npz: exists
data/standard_metrics_c49_emb.npz: exists
data/standard_metrics_c45_emb.npz: exists
`
