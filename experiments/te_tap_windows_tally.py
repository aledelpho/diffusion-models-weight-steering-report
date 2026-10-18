"""C87 tally (docs/prereg_te_tap_windows.md, rules 1-3 and the blind control). Written 2026-10-18 after the renders and
the metrics, before any count and before any label.

  python te_tap_windows_tally.py --auto        # rules 1-3 on DINOv2 -> data/te_tap_windows_tests.csv (sealed until the
                                               # blind control is counted)
  python te_tap_windows_tally.py --control     # blind control: Spearman(DINOv2, eye trait loss) on the 36 sampled renders
  python te_tap_windows_tally.py --selftest
"""
import argparse, csv, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
DATA = HERE.parent / "data"
VAL = {"sì": 1, "no": 0, "non so": None}


def rd(n):
    return list(csv.DictReader(open(DATA / n, encoding="utf-8-sig")))


def shares(M):
    """M: rows of te_tap_windows_metrics.csv -> {(char, seed): {cond: f}} with f = D / D(full)."""
    D = defaultdict(dict)
    for r in M:
        D[(r["char"], r["seed"])][r["cond_tag"]] = float(r["dinov2_dist_to_base"])
    return {c: {k: v / d["FULL"] for k, v in d.items()} for c, d in D.items()}


def rules(F):
    out, cells = [], sorted(F)
    # rule 1
    steps, maxd = [], []
    for c in cells:
        f = F[c]; seq = [f["F02"]] + [f[f"F{k:02d}"] - f[f"F{k - 1:02d}"] for k in range(3, 11)] + [1 - f["F10"]]
        ks = list(range(2, 12)); i = int(np.argmax(seq))
        steps.append(ks[i] if seq[i] >= 0.40 else None); maxd.append(max(seq))
    st = [k for k in steps if k]; same = Counter(st).most_common(1)[0][1] if st else 0
    if len(st) >= 4 and same >= 3: v1 = f"step (at tap {Counter(st).most_common(1)[0][0]})"
    elif sum(m <= 0.25 for m in maxd) >= 4: v1 = "gradual"
    else: v1 = "mixed"
    out.append({"test": "Rule 1 step or slope (forward windows)", "value": f"cells with one increment >= 0.40: {len(st)} of 6 (taps {st}); largest increment per cell {[round(m, 2) for m in maxd]}", "verdict": v1})
    # rule 2
    taps = list(range(3, 11))
    mean = {k: statistics.mean(F[c][f"S{k:02d}"] for c in cells) for k in taps}
    lead = Counter(max(taps, key=lambda k: F[c][f"S{k:02d}"]) for c in cells)
    hubs = [k for k in (7, 6) if lead[k] >= 4 and mean[k] >= 0.30]
    if hubs: v2 = f"tap {hubs[0]} is a hub"
    elif all(m < 0.30 for m in mean.values()): v2 = "no hub"
    else: v2 = "reported, no verdict"
    out.append({"test": "Rule 2 hub tap (single taps 3-10)", "value": "mean share " + " ".join(f"t{k}:{mean[k]:.2f}" for k in taps) + f"; largest per cell {dict(lead)}", "verdict": v2})
    # rule 3 (reported)
    s = {k: statistics.mean(F[c][f"F{k - 1:02d}"] + F[c][f"B{k:02d}"] for c in cells) for k in range(3, 12)}
    out.append({"test": "Rule 3 complementary windows F(2..k-1) + B(k..11), mean share (reported; < 1 read only with the eye)", "value": " ".join(f"k{k}:{v:.2f}" for k, v in s.items()), "verdict": ""})
    out.append({"test": "forward curve, mean share (reported)", "value": " ".join(f"F{k:02d}:{statistics.mean(F[c][f'F{k:02d}'] for c in cells):.2f}" for k in range(2, 11)), "verdict": ""})
    out.append({"test": "backward curve, mean share (reported)", "value": " ".join(f"B{k:02d}:{statistics.mean(F[c][f'B{k:02d}'] for c in cells):.2f}" for k in range(3, 12)), "verdict": ""})
    return out


def control(key, sched, labels, metrics):
    a1 = {}
    for r in labels:
        if str(r["showing"]) == "1":
            a1[(r["item"], r["question"])] = r["answer"]
    traits = defaultdict(set)
    for s in sched:
        if s["kind"] == "trait":
            traits[s["char"]].add(s["question"])
    base = {(k["char"], k["seed"]): k["item"] for k in key if k["cond"] == "baseline"}
    full = {"D1": "D1_dwarf_paladin", "E2": "E2_elf_rogue", "O4": "O4_halforc_fighter"}
    D = {(r["char"], r["seed"], r["cond_tag"]): float(r["dinov2_dist_to_base"]) for r in metrics}
    xs, ys = [], []
    for k in key:
        if k["cond"] == "baseline":
            continue
        o = base[(k["char"], k["seed"])]
        p0 = [q for q in traits[k["char"]] if VAL.get(a1.get((o, q))) == 1]
        j = [q for q in p0 if VAL.get(a1.get((k["item"], q))) is not None]
        if not j:
            continue
        R = sum(VAL[a1[(k["item"], q)]] for q in j) / len(j)
        xs.append(D[(full[k["char"]], k["seed"], k["cond"])]); ys.append(1 - R)
    from scipy.stats import spearmanr
    rho = float(spearmanr(xs, ys).correlation)
    return {"test": "Blind control: Spearman(DINOv2 distance, eye trait loss) on the sampled renders", "value": f"{rho:+.3f} (n {len(xs)})",
            "verdict": "DINOv2 may decide" if rho >= 0.50 else "DINOv2 may not decide: rules to be recomputed on the eye"}


def selftest():
    rng = np.random.default_rng(0); F = {}
    for i in range(6):
        f = {"FULL": 1.0}
        for k in range(2, 11):
            f[f"F{k:02d}"] = 0.1 if k < 7 else 0.8          # jump when tap 7 is added
        for k in range(3, 12):
            f[f"B{k:02d}"] = 0.9 if k <= 7 else 0.1
        for k in range(3, 11):
            f[f"S{k:02d}"] = 0.5 if k == 7 else 0.05 + 0.02 * rng.random()
        F[(f"c{i}", "s")] = f
    out = rules(F)
    assert out[0]["verdict"].startswith("step (at tap 7)"), out[0]
    assert out[1]["verdict"] == "tap 7 is a hub", out[1]
    for c in F:                                               # gradual world
        for k in range(2, 11):
            F[c][f"F{k:02d}"] = (k - 1) / 10
        for k in range(3, 11):
            F[c][f"S{k:02d}"] = 0.1
    out = rules(F)
    assert out[0]["verdict"] == "gradual" and out[1]["verdict"] == "no hub", out[:2]
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for a in ("auto", "control", "selftest"):
        ap.add_argument(f"--{a}", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    if a.auto:
        out = rules(shares(rd("te_tap_windows_metrics.csv")))
        with open(DATA / "te_tap_windows_tests.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        print("wrote data/te_tap_windows_tests.csv (sealed until the blind control is counted)")
    if a.control:
        o = control(rd("te_tap_windows_key.csv"), rd("te_tap_windows_schedule.csv"), rd("te_tap_windows_alessandro.csv"),
                    rd("te_tap_windows_metrics.csv"))
        print(o)
        with open(DATA / "te_tap_windows_control.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(o)); w.writeheader(); w.writerow(o)
