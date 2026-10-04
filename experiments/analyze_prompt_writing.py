"""Score C45 (docs/prereg_prompt_writing.md). Written before any C45 render.

  python experiments/analyze_prompt_writing.py --features   # 23 style features per image (cached, resumable)
  python experiments/analyze_prompt_writing.py              # pre-registered test

Images: S1_W1 = benchmark_prompt_order/V1_Original_*, S1_W2 = .../V5_Inverse_*;
everything else benchmark_prompt_writing/{prompt_id}_{cond}_krea2_seed{seed}_00001_.png.
Outputs: data/prompt_writing_style_features.csv, data/prompt_writing_arms.csv,
data/prompt_writing_test.csv
"""
import argparse, csv, glob, itertools, os, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
ROOT = r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"
if not os.path.isdir(ROOT):
    ROOT = os.path.expanduser("~/mnt")
PW = os.path.join(ROOT, "benchmark_prompt_writing")
PO = os.path.join(ROOT, "benchmark_prompt_order")
FEAT = os.path.join(DATA, "prompt_writing_style_features.csv")
SEEDS = ["3141592", "1234567"]
WRIT = {"S1": ["S1_W1_original", "S1_W2_reordered", "S1_W3_tags", "S1_W4_synonyms"],
        "S2": ["S2_W1_original", "S2_W2_reordered", "S2_W3_tags", "S2_W4_synonyms"]}
CONTENT = {"S1": "S1_C1_flamegauntlet", "S2": "S2_C1_oldman"}
ALIAS = {"S1_W1_original": (PO, "V1_Original"), "S1_W2_reordered": (PO, "V5_Inverse")}
PAT = re.compile(r"^(.+?)_(baseline|blk\d\d_(?:pos|neg)_d[\d.]+)_krea2_seed(\d+)_00001_\.png$")


def path(pid, cond, seed):
    d, name = ALIAS.get(pid, (PW, pid))
    return os.path.join(d, f"{name}_{cond}_krea2_seed{seed}_00001_.png")


def plan():
    rows = list(csv.DictReader(open(os.path.join(DATA, "prompt_writing_plan.csv"), encoding="utf-8-sig")))
    conds = sorted({r["cond_id"] for r in rows})
    assert len(conds) == 25 and "baseline" in conds
    return conds


def features():
    import sys
    sys.path.insert(0, HERE)
    from style_features import extract_all_features
    conds = plan()
    pids = WRIT["S1"] + WRIT["S2"] + list(CONTENT.values())
    done = set()
    if os.path.exists(FEAT):
        done = {(r["prompt_id"], r["cond"], r["seed"]) for r in csv.DictReader(open(FEAT))}
    new = not os.path.exists(FEAT)
    with open(FEAT, "a", newline="") as fh:
        w = None
        for pid in pids:
            for c in conds:
                for s in SEEDS:
                    if (pid, c, s) in done:
                        continue
                    p = path(pid, c, s)
                    if not os.path.exists(p):
                        print("missing", p); continue
                    d = extract_all_features(p)
                    d = {"prompt_id": pid, "cond": c, "seed": s, **{k: v for k, v in d.items() if k not in ("file", "width_px", "height_px")}}
                    if w is None:
                        w = csv.DictWriter(fh, fieldnames=list(d))
                        if new:
                            w.writeheader()
                    w.writerow(d); fh.flush()


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def test():
    rows = list(csv.DictReader(open(FEAT)))
    keys = [k for k in rows[0] if k not in ("prompt_id", "cond", "seed")]
    assert len(keys) == 23, len(keys)
    F = {(r["prompt_id"], r["cond"], r["seed"]): np.array([float(r[k]) for k in keys]) for r in rows}
    conds = [c for c in plan() if c != "baseline"]
    sd = {}
    for subj, ws in WRIT.items():
        B = np.array([F[(w, "baseline", s)] for w in ws for s in SEEDS])
        x = B.std(axis=0, ddof=1); x[x == 0] = 1; sd[subj] = x
    def dF(pid, c, s, subj):
        return (F[(pid, c, s)] - F[(pid, "baseline", s)]) / sd[subj]
    size_writing = np.mean([np.abs((F[(a, "baseline", s)] - F[(b, "baseline", s)]) / sd[subj]).mean()
                            for subj, ws in WRIT.items() for s in SEEDS for a, b in itertools.combinations(ws, 2)])
    out = []
    for c in conds:
        aw, ac, asub, aseed, size, w3 = [], [], [], [], [], []
        for subj, ws in WRIT.items():
            for s in SEEDS:
                for a, b in itertools.combinations(ws, 2):
                    aw.append(cos(dF(a, c, s, subj), dF(b, c, s, subj)))
                ac.append(cos(dF(ws[0], c, s, subj), dF(CONTENT[subj], c, s, subj)))
                w3.append(cos(dF(ws[0], c, s, subj), dF(ws[2], c, s, subj)))
                size += [np.abs(dF(w, c, s, subj)).mean() for w in ws]
            for w in ws:
                aseed.append(cos(dF(w, c, SEEDS[0], subj), dF(w, c, SEEDS[1], subj)))
        for k in range(4):
            for s in SEEDS:
                asub.append(cos(dF(WRIT["S1"][k], c, s, "S1"), dF(WRIT["S2"][k], c, s, "S2")))
        out.append({"arm": c, "size": np.mean(size), "A_writing": np.mean(aw), "A_content_small": np.mean(ac),
                    "A_subject": np.mean(asub), "A_seed": np.mean(aseed), "W1_vs_W3_tags": np.mean(w3)})
    with open(os.path.join(DATA, "prompt_writing_arms.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        for o in out:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in o.items()})
    sc = [o for o in out if o["size"] > size_writing]
    n = len(sc)
    med = float(np.median([o["A_writing"] - o["A_seed"] for o in sc])) if n else float("nan")
    f_sub = np.mean([o["A_writing"] > o["A_subject"] for o in sc]) if n else float("nan")
    f_con = np.mean([o["A_writing"] > o["A_content_small"] for o in sc]) if n else float("nan")
    if n and med >= -0.10 and f_sub >= 0.75 and f_con >= 0.60:
        verdict = "supported"
    elif n and (med < -0.20 or f_sub < 0.50):
        verdict = "refuted"
    else:
        verdict = "inconclusive"
    t = [["size_writing (baseline-to-baseline, writings only)", round(size_writing, 4)],
         ["scored arms (size > size_writing)", f"{n}/{len(out)}"],
         ["median(A_writing - A_seed)", round(med, 4)],
         ["share A_writing > A_subject", round(float(f_sub), 3)],
         ["share A_writing > A_content_small", round(float(f_con), 3)],
         ["VERDICT", verdict]]
    with open(os.path.join(DATA, "prompt_writing_test.csv"), "w", newline="") as fh:
        csv.writer(fh).writerows([["test", "value"]] + t)
    for r in t:
        print(r)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--features", action="store_true")
    features() if ap.parse_args().features else test()
