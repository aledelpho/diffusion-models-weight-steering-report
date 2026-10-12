"""C70 tally (docs/prereg_te_genre.md, amendment 1): G1-G3 and the reported counts. Written after the labels and the
amendment, before any count."""
import csv, json, sys
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, mannwhitneyu
DATA = Path(__file__).resolve().parent.parent / "data"
SEED = "3141592"
ORD = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
rd = lambda n: list(csv.DictReader(open(DATA / n, encoding="utf-8")))

lab = {r["row"]: [r[f"g{i}"] for i in range(1, 6)] for r in rd("te_genre_alessandro.csv") if r["grid"] == f"te_genre_{SEED}"}
orig = lab.pop("originali")
edits = list(lab)
sw = {k: [None if not g or not orig[i] else int(g != orig[i]) for i, g in enumerate(v)] for k, v in lab.items()}
rate = {k: np.mean([x for x in v if x is not None]) for k, v in sw.items()}
out = []
print("originals:", orig)
for k in edits:
    print(f"  {k:16s} {' '.join(f'{g:8s}' for g in lab[k])} switch {rate[k]:.1f}")
allsw = [(lab[k][i]) for k in edits for i in range(5) if sw[k][i]]
print("switched images:", len(allsw), "of", 5 * len(edits), dict(Counter(allsw)))

# G1
st = {r["cond"]: json.loads(r["per_order_style_share"]) for r in rd("te_bridge_style.csv")}
x, y, who = [], [], []
for k in ["L06_mlp_p1.00", "L12_mlp_p1.00", "L10_mlp_m1.00", "L19_attn_m1.00"]:
    for i in range(5):
        if sw[k][i] is not None:
            x.append(st[k][i]); y.append(sw[k][i]); who.append(k)
x, y = np.array(x), np.array(y)
n1, n0 = int(y.sum()), int((1 - y).sum())
if min(n1, n0) < 3:
    auc, g1 = float("nan"), "inconclusive"
else:
    auc = mannwhitneyu(x[y == 0], x[y == 1]).statistic / (n0 * n1)   # P(share non-switched > share switched)
    g1 = "supported" if auc >= 0.70 else ("not supported" if auc <= 0.50 else "between thresholds")
out.append({"test": "G1", "value": f"AUC {auc:.3f} (switched {n1}, not {n0})", "verdict": g1})
for k in ["L06_mlp_p1.00", "L12_mlp_p1.00"]:
    m = np.array(who) == k
    print("  within", k, "share", np.round(x[m], 4).tolist(), "switch", y[m].tolist())
# G2, G3
sc = {r["row"]: float(r["score_1_5"]) for r in rd("te_order_grid_notes_alessandro.csv") if r["grid"] == f"te_order_{SEED}" and r["score_1_5"]}
sz = {r["cond"]: float(r["size"]) for r in rd("te_order_tests.csv")}
for name, ref, src in [("G2", sc, "order score 1-5"), ("G3", sz, "conditioning size")]:
    ks = [k for k in edits if k in ref]
    rho, p = spearmanr([rate[k] for k in ks], [ref[k] for k in ks])
    out.append({"test": name, "value": f"rho {rho:.3f} (p {p:.3f}, n {len(ks)}) vs {src}", "verdict": "supported" if rho >= 0.50 else "not supported"})
with open(DATA / "te_genre_tests.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
with open(DATA / "te_genre_by_edit.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["cond", *ORD, "switch_rate", "order_score", "size"])
    for k in edits:
        w.writerow([k, *lab[k], round(rate[k], 2), sc.get(k, ""), sz.get(k, "")])
for r in out:
    print(r)
