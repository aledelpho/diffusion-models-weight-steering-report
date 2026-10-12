"""C70 amendment 2 tally: G1d-G3d (docs/prereg_te_genre.md). Written after the intensity labels, before any count."""
import csv, json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
DATA = Path(__file__).resolve().parent.parent / "data"
SEED = "3141592"
rd = lambda n: list(csv.DictReader(open(DATA / n, encoding="utf-8")))
dose = {r["row"]: [int(r[f"d{i}"]) if r[f"d{i}"] != "" else None for i in range(1, 6)] for r in rd("te_genre_dose_alessandro.csv")}
gen = {r["row"]: [r[f"g{i}"] for i in range(1, 6)] for r in rd("te_genre_alessandro.csv") if r["grid"] == f"te_genre_{SEED}"}
dose.pop("originali"); edits = list(dose)
mean = {k: np.mean([x for x in v if x is not None]) for k, v in dose.items()}
st = {r["cond"]: json.loads(r["per_order_style_share"]) for r in rd("te_bridge_style.csv")}
out = []
x, y, who = [], [], []
for k in ["L06_mlp_p1.00", "L12_mlp_p1.00", "L10_mlp_m1.00", "L19_attn_m1.00"]:
    for i in range(5):
        if dose[k][i] is not None:
            x.append(st[k][i]); y.append(dose[k][i]); who.append(k)
rho, p = spearmanr(x, y)
out.append({"test": "G1d", "value": f"rho {rho:.3f} (p {p:.3f}, n {len(x)}) style share vs intensity", "verdict": "supported" if rho <= -0.40 else "not supported"})
for k in ["L06_mlp_p1.00", "L12_mlp_p1.00"]:
    m = [i for i, w in enumerate(who) if w == k]
    r_, _ = spearmanr([x[i] for i in m], [y[i] for i in m])
    out.append({"test": f"G1d within {k}", "value": f"rho {r_:.3f} (n 5)", "verdict": "reported"})
sc = {r["row"]: float(r["score_1_5"]) for r in rd("te_order_grid_notes_alessandro.csv") if r["grid"] == f"te_order_{SEED}" and r["score_1_5"]}
sz = {r["cond"]: float(r["size"]) for r in rd("te_order_tests.csv")}
for name, ref, src in [("G2d", sc, "order score 1-5"), ("G3d", sz, "conditioning size")]:
    ks = [k for k in edits if k in ref]
    r_, p_ = spearmanr([mean[k] for k in ks], [ref[k] for k in ks])
    out.append({"test": name, "value": f"rho {r_:.3f} (p {p_:.3f}, n {len(ks)}) mean intensity vs {src}", "verdict": "supported" if r_ >= 0.50 else "not supported"})
# reported: consistency between the two passes
same = [(gen[k][i], dose[k][i]) for k in edits for i in range(5)]
cons = {g: np.round(np.mean([d for gg, d in same if gg == g]), 2) for g in sorted({g for g, _ in same})}
out.append({"test": "intensity by genre label (reported)", "value": json.dumps({k: float(v) for k, v in cons.items()}), "verdict": "reported"})
with open(DATA / "te_genre_dose_tests.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
for r in out: print(r)
print({k: round(float(mean[k]), 2) for k in edits})
