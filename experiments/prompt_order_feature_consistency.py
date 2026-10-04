"""Layout-free version of prompt_order_consistency.py.

Pixel correlation cannot follow an edit when the five word orders already
move pose and framing (baseline-to-baseline dE 16-31). Here each image is
reduced to the 23 style features of style_features.py (stored in
data/prompt_order_style_features.csv), and each arm to the vector of feature
changes dF = F(edit) - F(baseline of the same order and seed), each feature
scaled by the SD of that feature over the 10 baselines (5 orders x 2 seeds).

Per arm:
  size        mean |dF| (in baseline-SD units, over 23 features)
  cos_order   mean cosine of dF between different orders, same seed (20 pairs)
  cos_seed    mean cosine of dF between the two seeds, same order (5 pairs)
  sign_agree  share of the 23 features whose sign of dF is the same in all 10 images
              (chance level for 10 independent coin flips: 2 / 2**10 = 0.002 per feature)
Also: size of the change produced by reordering alone (mean |F(Vi) - F(Vj)|, same seed).
Writes data/prompt_order_feature_consistency.csv.
"""
import csv, itertools, os, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PAT = re.compile(r"^(V\d_[A-Za-z]+)_(blk\d\d_(?:pos|neg))_d([\d.]+)_krea2_seed(\d+)_")
BASE = re.compile(r"^(V\d_[A-Za-z]+)_baseline_krea2_seed(\d+)_")
VARS = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
SEEDS = ["3141592", "1234567"]


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    rows = list(csv.DictReader(open(os.path.join(DATA, "prompt_order_style_features.csv"))))
    feats = [k for k in rows[0] if k not in ("file", "width_px", "height_px")]
    F, B, dose = {}, {}, {}
    for r in rows:
        v = np.array([float(r[k]) for k in feats])
        m = BASE.match(r["file"])
        if m: B[(m[1], m[2])] = v; continue
        m = PAT.match(r["file"])
        if m: F[(m[1], m[4], m[2])] = v; dose[m[2]] = m[3]
    sd = np.std(np.array(list(B.values())), axis=0, ddof=1)
    sd[sd == 0] = 1
    reorder = [np.abs((B[(a, s)] - B[(b, s)]) / sd).mean() for s in SEEDS for a, b in itertools.combinations(VARS, 2)]
    out = []
    for arm in sorted(dose):
        dF = {(v, s): (F[(v, s, arm)] - B[(v, s)]) / sd for v in VARS for s in SEEDS}
        co = [cos(dF[(a, s)], dF[(b, s)]) for s in SEEDS for a, b in itertools.combinations(VARS, 2)]
        cs = [cos(dF[(v, SEEDS[0])], dF[(v, SEEDS[1])]) for v in VARS]
        M = np.sign(np.array(list(dF.values())))
        agree = float(np.mean(np.abs(M.sum(axis=0)) == len(M)))
        size = float(np.mean([np.abs(x).mean() for x in dF.values()]))
        out.append([arm, dose[arm], round(size, 3), round(np.mean(co), 3), round(np.std(co, ddof=1), 3),
                    round(np.mean(cs), 3), round(agree, 3)])
    with open(os.path.join(DATA, "prompt_order_feature_consistency.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arm", "dose", "size", "cos_order", "cos_order_sd", "cos_seed", "sign_agree_all10"])
        w.writerows(out)
        w.writerow(["REORDER_ONLY", "", round(float(np.mean(reorder)), 3), "", "", "", ""])
    print("reorder-only size", round(float(np.mean(reorder)), 3))


if __name__ == "__main__":
    main()
