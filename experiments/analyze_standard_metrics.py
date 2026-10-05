"""Score the standard metrics (docs/prereg_standard_metrics.md). Written before the metrics exist.

  python experiments/analyze_standard_metrics.py
Reads data/standard_metrics_{c45,c47,c49}.csv and *_emb.npz; writes
data/standard_metrics_summary.csv (one row per reported quantity).
"""
import csv, itertools, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")
OUT = []


def rd(b):
    p = os.path.join(DATA, f"standard_metrics_{b}.csv")
    if not os.path.exists(p):
        return None, None
    rows = {(r["prompt_id"], r["seed"], r["cond"]): r for r in csv.DictReader(open(p))}
    z = np.load(os.path.join(DATA, f"standard_metrics_{b}_emb.npz"))
    emb = {k: (dv, cv) for k, dv, cv in zip(z["keys"], z["dino"], z["clip"])}
    return rows, emb


def put(bench, name, value, note=""):
    OUT.append([bench, name, value, note]); print(f"{bench:4s} {name:60s} {value}  {note}")


def f(r, k):
    return float(r[k])


def c47():
    M, _ = rd("c47")
    if M is None:
        return
    ch = {(r["prompt"], r["seed"], r["cond"]): float(r["d_chroma"]) for r in csv.DictReader(open(os.path.join(DATA, "blk23_colorful_measures.csv")))}
    ladder = [("b23_m0.450", -0.45), ("b23_m0.300", -0.30), ("b23_m0.150", -0.15), ("baseline", 0.0), ("b23_p0.150", 0.15), ("b23_p0.300", 0.30)]
    cells = sorted({(p, s) for p, s, _ in M})
    for metric, base_val, better in (("lpips", 0.0, "lower"), ("dino_cos", 1.0, "higher")):
        wins = n = 0; diffs = []
        for p, s in cells:
            tc = ch[(p, s, "txtpos")]
            pts = [(ch[(p, s, c)] if c != "baseline" else 0.0, f(M[(p, s, c)], metric) if c != "baseline" else base_val) for c, _ in ladder]
            hit = None
            for (c0, m0), (c1, m1) in zip(pts, pts[1:]):
                if min(c0, c1) <= tc <= max(c0, c1) and c0 != c1:
                    hit = m0 + (tc - c0) / (c1 - c0) * (m1 - m0); break
            if hit is None:
                continue
            t = f(M[(p, s, "txtpos")], metric); n += 1
            good = hit < t if better == "lower" else hit > t
            wins += good; diffs.append(hit - t)
        put("c47", f"M1 {metric}: blk23 at text-matched chroma closer to base than the text", f"{wins}/{n}", f"median diff (blk23 - text) {np.median(diffs):.4f}" if diffs else "")
    for metric in ("brisque", "clipiqa", "clipscore"):
        for c in ("txtpos", "b23_m0.450", "txtneg", "b23_p0.300"):
            v = [f(M[(p, s, c)], metric) - f(M[(p, s, "baseline")], metric) for p, s in cells]
            put("c47", f"M2 median delta {metric} {c}", round(float(np.median(v)), 4))


def c49():
    M, E = rd("c49")
    if M is None:
        return
    from prompt_family import FAMILIES, SUBJECTS, SEEDS, ARMS
    pids = [f"{fa}_{s}" for fa in FAMILIES for s in SUBJECTS]
    for a in [x for x in ARMS if x != "baseline"]:
        for metric in ("brisque", "clipiqa", "clipscore"):
            v = [f(M[(p, s, a)], metric) - f(M[(p, s, "baseline")], metric) for p in pids for s in SEEDS]
            put("c49", f"Q median delta {metric} {a}", round(float(np.median(v)), 4))
        for metric in ("lpips", "dino_cos"):
            put("c49", f"Q median {metric} {a}", round(float(np.median([f(M[(p, s, a)], metric) for p in pids for s in SEEDS])), 4))
        bs = [f(M[(p, s, a)], "clipscore") - f(M[(p, s, "baseline")], "clipscore") for p in pids for s in SEEDS if p.endswith("blacksmith")]
        put("c49", f"Q median delta clipscore on blacksmith prompts {a}", round(float(np.median(bs)), 4))
    key = lambda p, s, a: f"{p}|{s}|{a}"
    cos = lambda x, y: float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))
    dv = lambda p, s, a: E[key(p, s, a)][0] - E[key(p, s, "baseline")][0]
    fam = lambda p: p.split("_")[0]
    wd = {}
    for a in [x for x in ARMS if x != "baseline"]:
        W, B = [], []
        for s in SEEDS:
            for p, q in itertools.combinations(pids, 2):
                (W if fam(p) == fam(q) else B).append(cos(dv(p, s, a), dv(q, s, a)))
        wd[a] = np.mean(W)
        put("c49", f"H5 DINO-change W / B {a}", f"{np.mean(W):.4f} / {np.mean(B):.4f}")
    mid = ["blk09_pos_d0.450", "blk03_pos_d0.400", "blk06_pos_d0.450", "blk13_neg_d0.450", "blk17_pos_d0.400"]
    ws = {r["arm"]: float(r["W_within_family"]) for r in csv.DictReader(open(os.path.join(DATA, "prompt_family_arms.csv")))}
    md, ms = float(np.median([wd[a] for a in mid])), float(np.median([ws[a] for a in mid]))
    put("c49", "H5 middle arms: median W with DINO vs with style features", f"{md:.4f} vs {ms:.4f}",
        "supported" if md >= ms + 0.10 else "refuted" if md <= ms else "inconclusive")


def c45():
    M, E = rd("c45")
    if M is None:
        return
    import analyze_prompt_writing as A
    cos = lambda x, y: float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))
    dv = lambda p, s, a: E[f"{p}|{s}|{a}"][0] - E[f"{p}|{s}|baseline"][0]
    aw, ac, asu, ase = [], [], [], []
    for a in [c for c in A.plan() if c != "baseline"]:
        for subj, ws in A.WRIT.items():
            for s in A.SEEDS:
                aw += [cos(dv(p, s, a), dv(q, s, a)) for p, q in itertools.combinations(ws, 2)]
                ac.append(cos(dv(ws[0], s, a), dv(A.CONTENT[subj], s, a)))
            ase += [cos(dv(w, A.SEEDS[0], a), dv(w, A.SEEDS[1], a)) for w in ws]
        for kk in range(4):
            for s in A.SEEDS:
                asu.append(cos(dv(A.WRIT["S1"][kk], s, a), dv(A.WRIT["S2"][kk], s, a)))
    for n, v in (("A_writing", aw), ("A_content_small", ac), ("A_subject", asu), ("A_seed", ase)):
        put("c45", f"DINO-change {n} (mean over arms and pairs)", round(float(np.mean(v)), 4))


if __name__ == "__main__":
    c47(); c49(); c45()
    with open(os.path.join(DATA, "standard_metrics_summary.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["bench", "quantity", "value", "note"]); w.writerows(OUT)
