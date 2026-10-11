"""C62 — a noise measure against the eye (docs/prereg_noise_metric.md). No renders.

  python noise_metric.py --dev    # candidates on C59 labels -> data/noise_metric_dev_scores.csv, data/noise_metric_dev.csv (choice)
  python noise_metric.py --test   # only after the choice is committed -> data/noise_metric_test_scores.csv, verdicts
  --img-root PATH                 # render root (default C:\\StabilityMatrix-win-x64\\Data\\Images\\Text2Img)
"""
import argparse, csv, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
IMG = Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img")
IDS = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"]
NOISE = ["chiazze", "grana", "collasso", "retino"]


def load(p):
    import cv2
    bgr = cv2.imread(str(p)); assert bgr is not None, p
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float64)
    return gray, lab[..., 1], lab[..., 2]


def blur(x, s):
    import cv2
    return cv2.GaussianBlur(x, (0, 0), s)


def flat_mask(gray):
    import cv2
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3); gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    g = blur(np.hypot(gx, gy), 4)
    return g < np.percentile(g, 30)


def immerkaer(g):
    c = (g[:-2, :-2] - 2 * g[:-2, 1:-1] + g[:-2, 2:] - 2 * g[1:-1, :-2] + 4 * g[1:-1, 1:-1] - 2 * g[1:-1, 2:]
         + g[2:, :-2] - 2 * g[2:, 1:-1] + g[2:, 2:])
    h, w = g.shape
    return float(np.sqrt(np.pi / 2) * np.abs(c).sum() / (6 * (w - 2) * (h - 2)))


def feats(gray, a, b, mask):
    hf = gray - blur(gray, 1.5); band = blur(gray, 2) - blur(gray, 8)
    f = {"hf": hf.std(), "band": band.std(), "imm": immerkaer(gray), "fhf": hf[mask].std(), "fband": band[mask].std()}
    for s in (1, 2, 4, 8):
        f[f"dog{s}"] = (blur(gray, s) - blur(gray, 2 * s))[mask].std()
    f["fcol"] = 0.5 * ((a - blur(a, 2))[mask].std() + (b - blur(b, 2))[mask].std())
    return f


def scores(edit_p, base_p, cache):
    if base_p not in cache:
        g, a, b = load(base_p); m = flat_mask(g); cache[base_p] = (m, feats(g, a, b, m))
    m, fb = cache[base_p]
    g, a, b = load(edit_p); fe = feats(g, a, b, m)
    L = lambda k: float(np.log(fe[k] / fb[k]))
    s = {"M1": abs(L("hf")), "M2": abs(L("band")), "M3": L("imm"), "M4": L("fhf"), "M5": L("fband"),
         "M6": max(L(f"dog{k}") for k in (1, 2, 4, 8)), "M7": L("fcol")}
    s["M8"] = max(s["M5"], s["M6"], s["M7"])
    return s


def auc(y, x):
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(y, x))


def dev():
    sys.path.insert(0, str(HERE))
    t = list(csv.DictReader(open(DATA / "split_atlas_eye_tally_alessandro.csv", encoding="utf-8")))
    prompts = ["P01_blacksmith", "F4_closeup", "S1_rally"]
    base = lambda pid: IMG / "benchmark_single_blocks_atlas" / "renders" / f"{pid}_baseline_krea2_seed2718281_00001_.png"
    def edit(pid, r):
        b, part, s = int(r["block"]), r["part"], r["sign"]
        if part == "whole":
            return IMG / "benchmark_single_blocks_atlas" / "renders" / f"{pid}_blk{b:02d}_{s}_d0.350_krea2_seed2718281_00001_.png"
        return IMG / "benchmark_split_atlas" / f"{pid}_blk{b:02d}_{part}_{s}_d0.350_krea2_seed2718281_00001_.png"
    rows, cache = [], {}
    for r in t:
        if r["partial"] in ("1", "True", "true"):
            continue
        y = int(max(int(float(r[k])) for k in NOISE) >= 2)
        for pid in prompts:
            s = scores(edit(pid, r), base(pid), cache)
            rows.append({"sheet": r["sheet"], "block": r["block"], "part": r["part"], "sign": r["sign"], "prompt": pid, "y": y,
                         **{k: round(v, 5) for k, v in s.items()}})
    with open(DATA / "noise_metric_dev_scores.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    y = np.array([r["y"] for r in rows])
    res = {k: auc(y, np.array([r[k] for r in rows])) for k in IDS}
    best = max(res.values()); chosen = next(k for k in IDS if res[k] >= best - 0.005)
    from sklearn.metrics import roc_curve
    fpr, tpr, thr = roc_curve(y, np.array([r[chosen] for r in rows]))
    j = int(np.argmax(tpr - fpr))
    with open(DATA / "noise_metric_dev.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["measure", "auc_dev", "chosen", "threshold", "dev_sensitivity", "dev_specificity", "n", "positives"])
        for k in IDS:
            w.writerow([k, round(res[k], 4), int(k == chosen), round(float(thr[j]), 5) if k == chosen else "",
                        round(float(tpr[j]), 3) if k == chosen else "", round(float(1 - fpr[j]), 3) if k == chosen else "", len(y), int(y.sum())])
    print({k: round(v, 3) for k, v in res.items()}, "chosen", chosen, "threshold", round(float(thr[j]), 4),
          "sens", round(float(tpr[j]), 3), "spec", round(float(1 - fpr[j]), 3), "n", len(y), "pos", int(y.sum()))


def test():
    choice = next(r for r in csv.DictReader(open(DATA / "noise_metric_dev.csv")) if r["chosen"] == "1")
    k, thr = choice["measure"], float(choice["threshold"])
    t = list(csv.DictReader(open(DATA / "comic_form_eye_tally_alessandro.csv", encoding="utf-8")))
    f = lambda pid, seed, cond: IMG / "benchmark_comic_form" / f"{pid}_{cond}_krea2_seed{seed}_00001_.png"
    rows, cache = [], {}
    for r in t:
        s = scores(f(r["prompt"], r["seed"], r["cond"]), f(r["prompt"], r["seed"], "baseline"), cache)
        rows.append({"prompt": r["prompt"], "seed": r["seed"], "cond": r["cond"], "group": r["group"],
                     "y": int(float(r["d_edit"]) >= 2), **{m: round(v, 5) for m, v in s.items()}})
    with open(DATA / "noise_metric_test_scores.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    y = np.array([r["y"] for r in rows]); X = {m: np.array([r[m] for r in rows]) for m in IDS}
    rng = np.random.default_rng(62); n = len(y); bs, bd = [], []
    for _ in range(2000):
        i = rng.integers(0, n, n)
        if y[i].min() == y[i].max():
            continue
        bs.append(auc(y[i], X[k][i])); bd.append(bs[-1] - auc(y[i], X["M1"][i]))
    a = auc(y, X[k]); lo, hi = np.percentile(bs, [2.5, 97.5]); dlo, dhi = np.percentile(bd, [2.5, 97.5])
    pred = X[k] >= thr; sens = float((pred & (y == 1)).sum() / (y == 1).sum()); spec = float((~pred & (y == 0)).sum() / (y == 0).sum())
    print("all candidates, test AUC:", {m: round(auc(y, X[m]), 3) for m in IDS})
    print(f"chosen {k}: AUC {a:.3f} [{lo:.3f}, {hi:.3f}] -> T1 {'HOLDS' if a >= 0.85 and lo >= 0.75 else 'FAILS'}")
    print(f"T2 vs M1: AUC difference {a - auc(y, X['M1']):+.3f} [{dlo:+.3f}, {dhi:+.3f}] -> {'HOLDS' if dlo > 0 else 'FAILS'}")
    print(f"T3 at dev threshold {thr}: sensitivity {sens:.3f}, specificity {spec:.3f} -> {'HOLDS' if sens >= 0.75 and spec >= 0.75 else 'FAILS'}")
    print("n", n, "positives", int(y.sum()))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", action="store_true"); ap.add_argument("--test", action="store_true"); ap.add_argument("--img-root")
    a = ap.parse_args()
    if a.img_root: IMG = Path(a.img_root)
    if a.dev: dev()
    if a.test: test()
