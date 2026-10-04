"""Score C47 (docs/prereg_blk23_vs_colorful.md). Code fixed before any render.

Images: benchmark_blk23_colorful/, names
  {prompt_id}_{cond}_krea2_seed{seed}_00001_.png
  cond in: baseline, txtpos, txtneg, b23_m0.450, b23_m0.300, b23_m0.150, b23_p0.150, b23_p0.300
(m = negative signed dose = more saturation, p = positive = less).

Per image against the baseline of the same prompt and seed, CIELAB at 64x80:
  d_chroma  change of mean chroma
  layout_r  Pearson r of the L channel with the baseline's
Outputs: data/blk23_colorful_measures.csv, data/blk23_colorful_test.csv
  python experiments/analyze_blk23_vs_colorful.py
"""
import csv, glob, os, re
import numpy as np
from block_effect_overlap import lab

ROOT = r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"
if not os.path.isdir(ROOT):
    ROOT = os.path.expanduser("~/mnt")
D = os.path.join(ROOT, "benchmark_blk23_colorful")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
PAT = re.compile(r"^(.+?)_(baseline|txtpos|txtneg|b23_[mp]\d\.\d{3})_krea2_seed(\d+)_")
LADDER = [("b23_m0.450", -0.45), ("b23_m0.300", -0.30), ("b23_m0.150", -0.15), ("baseline", 0.0),
          ("b23_p0.150", 0.15), ("b23_p0.300", 0.30)]


def interp_at_chroma(points, target):
    """points: [(dose, d_chroma, layout_r)] sorted by dose. Linear interpolation of layout_r
    at the dose where d_chroma == target; None if target is outside the ladder's range."""
    for (d0, c0, l0), (d1, c1, l1) in zip(points, points[1:]):
        lo, hi = sorted((c0, c1))
        if lo <= target <= hi and c1 != c0:
            t = (target - c0) / (c1 - c0)
            return d0 + t * (d1 - d0), l0 + t * (l1 - l0)
    return None


def main():
    imgs = {}
    for f in glob.glob(os.path.join(D, "*.png")):
        m = PAT.match(os.path.basename(f))
        if m:
            imgs[(m[1], m[3], m[2])] = lab(f)
    cells = sorted({(p, s) for p, s, _ in imgs})
    meas = []
    per = {}
    for p, s in cells:
        B = imgs.get((p, s, "baseline"))
        if B is None:
            continue
        cB = np.hypot(B[..., 1], B[..., 2]).mean()
        per[(p, s)] = {}
        for (pp, ss, c), X in imgs.items():
            if (pp, ss) != (p, s):
                continue
            dc = float(np.hypot(X[..., 1], X[..., 2]).mean() - cB)
            lr = float(np.corrcoef(X[..., 0].ravel(), B[..., 0].ravel())[0, 1])
            per[(p, s)][c] = (dc, lr)
            meas.append([p, s, c, round(dc, 4), round(lr, 4)])
    with open(os.path.join(DATA, "blk23_colorful_measures.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["prompt", "seed", "cond", "d_chroma", "layout_r"]); w.writerows(meas)

    n = len(per)
    mono = lin = 0; ratios = []
    wins = losses = 0; diffs = []; text_no_effect = 0; out_of_range = 0
    for key, v in per.items():
        ch = [v[c][0] if c in v else None for c, _ in LADDER]
        if None not in ch and all(a > b for a, b in zip(ch, ch[1:])):
            mono += 1
        if "b23_m0.150" in v and "b23_m0.300" in v and v["b23_m0.150"][0] > 0:
            ratios.append(v["b23_m0.300"][0] / v["b23_m0.150"][0])
        if "txtpos" not in v:
            continue
        tc, tl = v["txtpos"]
        if tc <= 0:
            text_no_effect += 1
            continue
        pts = [(dose, v[c][0], v[c][1]) for c, dose in LADDER if c in v]
        hit = interp_at_chroma(pts, tc)
        if hit is None:
            out_of_range += 1
            continue
        _, l23 = hit
        diffs.append(l23 - tl)
        wins += l23 > tl
        losses += l23 < tl
    med_ratio = float(np.median(ratios)) if ratios else float("nan")
    med_diff = float(np.median(diffs)) if diffs else float("nan")
    k = len(diffs)
    rows = [
        ["cells (prompt x seed)", n, ""],
        ["V1 monotone ladder (chroma strictly falls from -0.45 to +0.30)", f"{mono}/{n}",
         "supported" if mono >= 0.875 * n else "refuted"],
        ["V2 median chroma ratio d(-0.30)/d(-0.15)", round(med_ratio, 3),
         "approximately linear" if 1.6 <= med_ratio <= 2.4 else "monotone, not linear"],
        ["T0 cells where the text did not raise chroma", text_no_effect, ""],
        ["T0b cells where the text's chroma gain is beyond the blk23 ladder", out_of_range, ""],
        ["T1 blk23 keeps layout better at matched chroma (wins/losses of scored)", f"{wins}/{losses} of {k}", ""],
        ["T1 median layout_r(blk23 matched) - layout_r(text)", round(med_diff, 4),
         ("blk23 better" if k and wins >= 0.75 * k and med_diff >= 0.05 else
          "text better" if k and wins <= 0.25 * k else "no clear difference") if k else "not scorable"],
    ]
    with open(os.path.join(DATA, "blk23_colorful_test.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["test", "value", "verdict"]); w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
