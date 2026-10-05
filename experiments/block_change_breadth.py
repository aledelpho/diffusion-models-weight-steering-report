"""How many rendering statistics a single-block edit moves at once (exploratory, 2026-10-05).

benchmark_single_blocks_atlas: every block, both signs, the same dose 0.350, three prompts, one seed.
For each edit, the change of 29 rendering statistics (data/single_blocks_measures.csv, each divided
by its SD over all 171 images) is summarised by
  * size        — the norm of the change vector;
  * breadth     — the participation ratio (sum x^2)^2 / sum x^4, the effective number of
                  statistics that carry the change (1 = one statistic, 29 = all equally).
Written after Alessandro's observation that the ends of the stack change few properties and the
middle many things at once; no threshold, descriptive only. Output: data/block_change_breadth.csv.
"""
import csv
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(ROOT / "data" / "single_blocks_measures.csv")))
feats = [k for k in rows[0] if k not in ("file", "coherence", "hue")]
X = {r["file"]: np.array([float(r[k]) for k in feats]) for r in rows}
sd = np.array(list(X.values())).std(0)
sd[sd == 0] = 1
base = {re.match(r"(\w+?)_baseline", f).group(1): v for f, v in X.items() if "baseline" in f}
out = []
for f, v in sorted(X.items()):
    m = re.match(r"(P01_blacksmith|S1_rally|F4_closeup)_blk(\d+)_(pos|neg)", f)
    if not m:
        continue
    d = (v - base[m.group(1)]) / sd
    out.append({"prompt": m.group(1), "block": int(m.group(2)), "sign": m.group(3),
                "size": round(float(np.linalg.norm(d)), 4),
                "breadth": round(float((d ** 2).sum() ** 2 / (d ** 4).sum()), 4)})
with open(ROOT / "data" / "block_change_breadth.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]))
    w.writeheader(); w.writerows(out)
print(len(out), "rows,", len(feats), "statistics")
for name, lo, hi in [("00-01", 0, 1), ("02-04", 2, 4), ("05-14", 5, 14), ("15-20", 15, 20), ("21-27", 21, 27)]:
    sel = [r for r in out if lo <= r["block"] <= hi]
    print(name, "median breadth", round(float(np.median([r["breadth"] for r in sel])), 2),
          "median size", round(float(np.median([r["size"] for r in sel])), 2), "n", len(sel))
