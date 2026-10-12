"""C65 part B, grid scores (exploratory): Alessandro's 1-5 'how much the picture changes with the word order' against
the part-B statistics (data/te_order_tests.csv). Prints the score table and Spearman correlations."""
import csv
from pathlib import Path
from scipy.stats import spearmanr

DATA = Path(__file__).resolve().parents[1] / "data"
sc = {r["row"]: int(r["score_1_5"]) for r in csv.DictReader(open(DATA / "te_order_grid_notes_alessandro.csv", encoding="utf-8"))
      if r["grid"] == "te_order_3141592" and r["score_1_5"]}
print("originals:", sc.pop("originali", None))
for v in range(1, 6):
    print(v, [k for k in sc if sc[k] == v])
st = {r["cond"]: r for r in csv.DictReader(open(DATA / "te_order_tests.csv"))}
ks = [k for k in sc if k in st]
for col in ("size", "cos_order", "cos_seed", "d"):
    r = spearmanr([sc[k] for k in ks], [float(st[k][col]) for k in ks])
    print(f"spearman score vs {col}: rho {r.statistic:.2f} p {r.pvalue:.4f} (n {len(ks)})")
