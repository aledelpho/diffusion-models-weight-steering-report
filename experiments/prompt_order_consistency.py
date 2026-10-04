"""Does a single-block edit move the image the same way whatever the word order?

benchmark_prompt_order: one prompt (P1_elfbrawler) rewritten in five word
orders V1..V5, two seeds, 57 conditions each (baseline + 28 blocks x 2 signs).
For each arm, D = render - baseline of the same (variant, seed), in CIELAB at
64x80 (same encoding as block_effect_overlap.py).

Reported per arm:
  dE_edit          mean |D| (how much the arm changes the image)
  r_order          mean Pearson r of D between the 5 orders, same seed (10 pairs x 2 seeds)
  r_order_resid    the same after removing the common mode (mean D over the 56 arms
                   of that variant and seed)
  r_seed           mean r of D between the 2 seeds, same order (5 pairs)
  r_other_prompt   mean r of D between this arm on P1 V1 and the same arm on the other
                   v3 prompts is not computed: layouts differ, pixel r is meaningless there.
Also written: baseline-to-baseline dE between orders (same seed), the scale against
which "the order changed the image" should be read, and a check that V1/seed 3141592
reproduces v3 P1_elfbrawler/seed 3141592 (same prompt text, same seed).

Writes data/prompt_order_consistency.csv and data/prompt_order_baselines.csv.
"""
import csv, glob, itertools, os, re
import numpy as np
from block_effect_overlap import lab

ROOT = r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"
if not os.path.isdir(ROOT):
    ROOT = os.path.expanduser("~/mnt")
PO = os.path.join(ROOT, "benchmark_prompt_order")
V3 = os.path.join(ROOT, "benchmark_single_blocks_v3", "renders")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
PAT = re.compile(r"^(V\d_[A-Za-z]+)_(blk\d\d_(?:pos|neg))_d([\d.]+)_krea2_seed(\d+)_")
BASE = re.compile(r"^(V\d_[A-Za-z]+)_baseline_krea2_seed(\d+)_")
VARS = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
SEEDS = ["3141592", "1234567"]


def r(a, b):
    return float(np.corrcoef(a.ravel(), b.ravel())[0, 1])


def main():
    B, X, dose = {}, {}, {}
    for f in glob.glob(os.path.join(PO, "*.png")):
        n = os.path.basename(f)
        m = BASE.match(n)
        if m: B[(m[1], m[2])] = lab(f); continue
        m = PAT.match(n)
        if m: X[(m[1], m[4], m[2])] = lab(f); dose[m[2]] = m[3]
    arms = sorted(dose)
    D = {k: X[k] - B[(k[0], k[1])] for k in X}
    C = {(v, s): np.mean([D[(v, s, a)] for a in arms if (v, s, a) in D], axis=0) for v in VARS for s in SEEDS}
    with open(os.path.join(OUT, "prompt_order_baselines.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["seed", "order_a", "order_b", "dE_baselines"])
        for s in SEEDS:
            for a, b in itertools.combinations(VARS, 2):
                w.writerow([s, a, b, round(float(np.linalg.norm(B[(a, s)] - B[(b, s)], axis=-1).mean()), 3)])
        v3 = glob.glob(os.path.join(V3, "P1_elfbrawler_baseline_krea2_seed3141592_*.png"))
        if v3:
            w.writerow(["3141592", "V1_Original", "v3:P1_elfbrawler", round(float(np.linalg.norm(B[("V1_Original", "3141592")] - lab(v3[0]), axis=-1).mean()), 3)])
    rows = []
    for a in arms:
        ro, rr, rs, de = [], [], [], []
        for s in SEEDS:
            for v1, v2 in itertools.combinations(VARS, 2):
                ro.append(r(D[(v1, s, a)], D[(v2, s, a)]))
                rr.append(r(D[(v1, s, a)] - C[(v1, s)], D[(v2, s, a)] - C[(v2, s)]))
        for v in VARS:
            rs.append(r(D[(v, SEEDS[0], a)], D[(v, SEEDS[1], a)]))
            for s in SEEDS:
                de.append(float(np.linalg.norm(D[(v, s, a)], axis=-1).mean()))
        rows.append([a, dose[a], round(np.mean(de), 3), round(np.mean(ro), 3), round(np.std(ro, ddof=1), 3),
                     round(np.mean(rr), 3), round(np.mean(rs), 3)])
    with open(os.path.join(OUT, "prompt_order_consistency.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["arm", "dose", "dE_edit", "r_order", "r_order_sd", "r_order_resid", "r_seed"])
        w.writerows(rows)
    print(len(rows), "arms")


if __name__ == "__main__":
    main()
