"""C98 - micro-watersheds on the colour-binding leaf renders (docs/prereg_watersheds_leaf.md). Written 2026-10-18 with
the pre-registration, before any computation. No renders.

  python watersheds_leaf.py            # data/watersheds_leaf_cells.csv, data/watersheds_leaf_tests.csv
"""
import csv, itertools, statistics, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import micro_watersheds as MW
import watersheds_origin as WO

DATA = HERE.parent / "data"
PROMPTS, SEEDS = ["LP", "LG", "LN"], ["42", "777", "1337"]
EDITS = [f"Block_{b}{s}" for b in range(1, 7) for s in ("pos", "neg")]


def path(p, cond, s, dose="0.050"):
    r = MW.img_root() / "benchmark_colour_binding" / "renders"
    return r / (f"{p}_baseline_krea2_seed{s}_00001_.png" if cond == "base" else f"{p}_{cond}_{dose}_krea2_seed{s}_00001_.png")


def main():
    rows, out, F, T, meanW = [], [], {}, {}, {}
    r1, share, share2 = {}, [], []
    for p in PROMPTS:
        for s in SEEDS:
            base = MW.load(path(p, "base", s)); t = np.log1p(MW.texture(base).ravel()); T[(p, s)] = t
            E = {}
            for e in EDITS:
                im = MW.load(path(p, e, s)); E[e], _ = WO.logE(base, im)
                d = np.abs(im - base).max(axis=2).astype(np.float32); tot = float((d ** 2).sum())
                share.append(float((d[d >= 32] ** 2).sum() / tot) if tot else 0.0)
                im2 = MW.load(path(p, e, s, "0.200")); d2 = np.abs(im2 - base).max(axis=2).astype(np.float32); t2 = float((d2 ** 2).sum())
                share2.append(float((d2[d2 >= 32] ** 2).sum() / t2) if t2 else 0.0)
            pr = [WO.pcorr(E[a], E[b], t) for a, b in itertools.combinations(EDITS, 2)]
            r1[(p, s)] = statistics.median(pr)
            meanW[(p, s)] = np.mean([E[e] for e in EDITS], axis=0); F[(p, s)] = WO.resid(meanW[(p, s)], t)
            rows.append({"prompt": p, "seed": s, "what": "R1 median pairwise partial r (66 pairs)", "value": round(r1[(p, s)], 4)})
    n = sum(v >= 0.30 for v in r1.values())
    out.append({"test": "R1 replication: cells with median pairwise partial r >= 0.30", "value": f"{n} of 9; " + " ".join(f"{p}/{s}:{v:.2f}" for (p, s), v in sorted(r1.items())),
                "verdict": "replicated" if n >= 7 else ("not replicated" if n <= 3 else "mixed")})
    r2 = []
    for s in SEEDS:
        bn = MW.load(path("LN", "base", s))
        for p in ("LP", "LG"):
            e, _ = WO.logE(bn, MW.load(path(p, "base", s)))
            v = WO.pcorr(e, meanW[("LN", s)], T[("LN", s)]); r2.append(v)
            rows.append({"prompt": f"{p} vs LN", "seed": s, "what": "R2 colour word vs mean LN edit map", "value": round(v, 4)})
    m2 = statistics.median(r2)
    out.append({"test": "R2 one word of the prompt hits the same places (median of 6)", "value": f"{m2:.3f}; " + " ".join(f"{v:.2f}" for v in r2),
                "verdict": "supported" if m2 >= 0.30 else ("refuted" if m2 <= 0.10 else "inconclusive")})
    out.append({"test": "T1 flip share (delta >= 32) at 0.050 / 0.200 (reported)", "value": f"median {statistics.median(share):.3f} / {statistics.median(share2):.3f}", "verdict": ""})
    same = [WO.pcorr(F[(a, s)], F[(b, s)], T[(a, s)], T[(b, s)]) for a, b in itertools.combinations(PROMPTS, 2) for s in SEEDS]
    diff = [WO.pcorr(F[(a, s)], F[(b, u)], T[(a, s)], T[(b, u)]) for a, b in itertools.combinations(PROMPTS, 2) for s in SEEDS for u in SEEDS if u != s]
    out.append({"test": "fragility maps across prompts, same seed vs different seed (reported; same picture at a seed)", "value": f"{statistics.mean(same):+.3f} vs {statistics.mean(diff):+.3f}", "verdict": ""})
    for fn, data in (("watersheds_leaf_cells.csv", rows), ("watersheds_leaf_tests.csv", out)):
        with open(DATA / fn, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    for o in out:
        print(o["test"], "|", o["value"], "|", o["verdict"])


if __name__ == "__main__":
    main()
