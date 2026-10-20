"""Exploratory (2026-10-12, after the C72 renders were queued, before any C72 label): how much of a text-encoder
edit's push sits in the few very large channels of Qwen3-VL-4B's hidden states ("massive activations", Sun et al.
2024)? V1 order, all 20 C65 edits, every tap the edit reaches. Writes data/te_massive_channels.csv."""
import csv
from pathlib import Path
import numpy as np
import sys
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import blk23_colorful as c47
import te_conditioning as T
import te_regions as RG
DATA = HERE.parent / "data"
if not c47.IMG_ROOT.exists():
    c47.IMG_ROOT = Path.home() / "mnt" / "D:--StabilityMatrix-win-x64--Data--Images--Text2Img"
v = "V1_Original"
b = np.load(T.out_path("order", v, "baseline"))["cond"].astype(np.float32)
mag = np.abs(b).mean(0)                                   # (12, 2560)
unit = {r["cond"]: r["unit"] for r in csv.DictReader(open(DATA / "te_regions_plan.csv", encoding="utf-8"))}
edits = sorted({r["cond"] for r in csv.DictReader(open(DATA / "te_order_tests.csv", encoding="utf-8"))})
rows = []
for e in edits:
    P = np.load(RG.out_path("order", v, e))["cond"].astype(np.float32) - b
    for t in range(T.first_tap(unit[e]), 12):
        Pt = P[:, t]; e2 = (Pt ** 2).sum(0); tot = float(e2.sum())
        big = np.argsort(-mag[t])[:2]                     # the two largest baseline channels at this tap
        top10 = np.argsort(-e2)[:10]
        rows.append({"cond": e, "tap": t, "baseline_big_channels": " ".join(map(str, big.tolist())),
                     "baseline_big_over_median": round(float(mag[t][big].mean() / np.median(mag[t])), 1),
                     "push_share_big2": round(float(e2[big].sum() / tot), 4),
                     "push_share_top10": round(float(e2[top10].sum() / tot), 4),
                     "push_share_shared_mean": round(float(Pt.shape[0] * (Pt.mean(0) ** 2).sum() / tot), 4)})
with open(DATA / "te_massive_channels.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
last = [r for r in rows if r["tap"] == 11]
for k in ("baseline_big_over_median", "push_share_big2", "push_share_top10", "push_share_shared_mean"):
    xs = [r[k] for r in last]; print(f"tap 11, 20 edits: {k} min {min(xs)} median {float(np.median(xs))} max {max(xs)}")
print("big channels at tap 11:", last[0]["baseline_big_channels"])
