"""Score C49 (docs/prereg_prompt_family.md). Written before any C49 render.

  python experiments/analyze_prompt_family.py --features   # 23 style features per image (resumable)
  python experiments/analyze_prompt_family.py              # pre-registered tests
Outputs: data/prompt_family_style_features.csv, data/prompt_family_arms.csv, data/prompt_family_test.csv
"""
import argparse, csv, itertools, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from prompt_family import FAMILIES, SUBJECTS, SEEDS, ARMS, FOLDER

DATA = os.path.join(HERE, "..", "data")
ROOT = r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"
if not os.path.isdir(ROOT):
    ROOT = os.path.expanduser("~/mnt")
D = os.path.join(ROOT, FOLDER)
FEAT = os.path.join(DATA, "prompt_family_style_features.csv")
TESTED = ["blk16_pos_d0.300", "blk20_pos_d0.450", "blk23_neg_d0.300", "blk26_pos_d0.150", "blk27_neg_d0.250", "combo"]
CONTROL = "blk09_pos_d0.450"
STYLE_BAND = ["blk03_pos_d0.400", "blk06_pos_d0.450", "blk13_neg_d0.450", "blk17_pos_d0.400"]  # amendment 1
COST = ["fft_high_freq_share", "edge_density", "lbp_entropy", "glcm_contrast"]


def path(pid, arm, seed):
    return os.path.join(D, f"{pid}_{arm}_krea2_seed{seed}_00001_.png")


def features():
    from style_features import extract_all_features
    done = set()
    if os.path.exists(FEAT):
        done = {(r["prompt_id"], r["arm"], r["seed"]) for r in csv.DictReader(open(FEAT))}
    new = not os.path.exists(FEAT)
    with open(FEAT, "a", newline="") as fh:
        w = None
        for fam in FAMILIES:
            for subj in SUBJECTS:
                pid = f"{fam}_{subj}"
                for seed in SEEDS:
                    for arm in ARMS:
                        if (pid, arm, seed) in done:
                            continue
                        f = extract_all_features(path(pid, arm, seed))
                        row = {"prompt_id": pid, "arm": arm, "seed": seed,
                               **{k: v for k, v in f.items() if k not in ("file", "width_px", "height_px")}}
                        if w is None:
                            w = csv.DictWriter(fh, fieldnames=list(row))
                            if new:
                                w.writeheader()
                        w.writerow(row); fh.flush()


def test():
    rows = list(csv.DictReader(open(FEAT)))
    keys = [k for k in rows[0] if k not in ("prompt_id", "arm", "seed")]
    assert len(keys) == 23
    F = {(r["prompt_id"], r["arm"], r["seed"]): np.array([float(r[k]) for k in keys]) for r in rows}
    pids = [f"{f}_{s}" for f in FAMILIES for s in SUBJECTS]
    B = np.array([F[(p, "baseline", s)] for p in pids for s in SEEDS]); sd = B.std(axis=0, ddof=1); sd[sd == 0] = 1
    d = lambda p, a, s: (F[(p, a, s)] - F[(p, "baseline", s)]) / sd
    cos = lambda x, y: float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))
    fam = lambda p: p.split("_")[0]
    out = []
    for a in [x for x in ARMS if x != "baseline"]:
        within, between, seed = [], [], []
        for s in SEEDS:
            for p, q in itertools.combinations(pids, 2):
                (within if fam(p) == fam(q) else between).append(cos(d(p, a, s), d(q, a, s)))
        for p in pids:
            seed.append(cos(d(p, a, SEEDS[0]), d(p, a, SEEDS[1])))
        row = {"arm": a, "W_within_family": np.mean(within), "B_between_families": np.mean(between),
               "S_seed": np.mean(seed), "size": np.mean([np.abs(d(p, a, s)).mean() for p in pids for s in SEEDS])}
        for k in COST:
            i = keys.index(k)
            row[f"cost_{k}_up_share"] = np.mean([F[(p, a, s)][i] > F[(p, "baseline", s)][i] for p in pids for s in SEEDS])
        out.append(row)
    with open(os.path.join(DATA, "prompt_family_arms.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader()
        for o in out:
            w.writerow({k: round(v, 4) if isinstance(v, float) else v for k, v in o.items()})
    T = [o for o in out if o["arm"] in TESTED]; C = [o for o in out if o["arm"] == CONTROL][0]
    wins = sum(o["W_within_family"] > o["B_between_families"] for o in T)
    med_gap = float(np.median([o["W_within_family"] - o["B_between_families"] for o in T]))
    med_W = float(np.median([o["W_within_family"] for o in T]))
    t = [["H1 W > B on tested arms", f"{wins}/{len(T)}", ""],
         ["H1 median (W - B)", round(med_gap, 4), "supported" if wins >= 5 and med_gap >= 0.10 else "refuted" if wins <= 3 or med_gap < 0.05 else "inconclusive"],
         ["H2 median W on tested arms", round(med_W, 4), "supported" if med_W >= 0.40 else "refuted" if med_W < 0.25 else "inconclusive"],
         ["H3 control blk09 pos W below the tested median", round(C["W_within_family"], 4), "supported" if C["W_within_family"] < med_W else "refuted"],
         ["H4 style band: median W (03+,06+,13-,17+) vs late tested median W",
          f"{float(np.median([o['W_within_family'] for o in out if o['arm'] in STYLE_BAND])):.4f} vs {med_W:.4f}",
          "supported" if float(np.median([o['W_within_family'] for o in out if o['arm'] in STYLE_BAND])) < med_W - 0.10 else "refuted" if float(np.median([o['W_within_family'] for o in out if o['arm'] in STYLE_BAND])) >= med_W else "inconclusive"],
         ["H4b style band: W > B on", f"{sum(o['W_within_family'] > o['B_between_families'] for o in out if o['arm'] in STYLE_BAND)}/4", ""],
         ["reference: median S_seed on tested arms", round(float(np.median([o["S_seed"] for o in T])), 4), ""],
         ["combo: W / B / S", f"{[o for o in out if o['arm']=='combo'][0]['W_within_family']:.3f} / {[o for o in out if o['arm']=='combo'][0]['B_between_families']:.3f} / {[o for o in out if o['arm']=='combo'][0]['S_seed']:.3f}", ""]]
    with open(os.path.join(DATA, "prompt_family_test.csv"), "w", newline="") as fh:
        csv.writer(fh).writerows([["test", "value", "verdict"]] + t)
    for r in t:
        print(r)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--features", action="store_true")
    features() if ap.parse_args().features else test()
