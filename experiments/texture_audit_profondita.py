#!/usr/bin/env python3
"""The decisive test for `first-block-is-an-inverted-knob`, on the corpus the claim was built on.

benchmark_profondita (+0.200) and benchmark_profondita_neg (-0.200), 28 single blocks x 2 prompts
x 3 seeds each. Baselines from benchmark_mappa at the same prompts and seeds: identical prompt
text, sampler, scheduler, steps, CFG and resolution, and `deterministic-across-sessions` is the
claim that licenses comparing them.

Same three estimators as experiments/texture_estimator_audit.py; r_flat is computed but is known
to be saturated (docs/texture_estimator_audit_result.md section 0) and is not argued from.
No render.
"""
import csv, os, time
import numpy as np
from PIL import Image
from numpy.lib.stride_tricks import sliding_window_view

H = os.path.expanduser("~/mnt")
POS = f"{H}/benchmark_profondita/renders"
NEG = f"{H}/benchmark_profondita_neg/renders"
BASE = f"{H}/benchmark_mappa--renders"
OUT = "data/texture_audit_profondita.csv"
P = ["P01", "P02"]; S = ["42", "777", "1337"]
BLK = [f"blk{i:02d}" for i in range(28)]
FIELDS = ["prompt", "seed", "block", "sign", "r_global", "r_flat", "r_cnorm"]


def gray(p): return np.asarray(Image.open(p).convert("L"), dtype=np.float32) / 255.0
def lapmap(a): return (4*a[1:-1,1:-1]-a[:-2,1:-1]-a[2:,1:-1]-a[1:-1,:-2]-a[1:-1,2:])**2
def flatmask(a, q=40):
    v = sliding_window_view(a, (9, 9)).var(axis=(2, 3))
    return v <= np.percentile(v, q)


def main():
    budget = float(os.environ.get("B", "100")); t0 = time.time()
    done = set()
    if os.path.exists(OUT):
        done = {(r["prompt"], r["seed"], r["block"], r["sign"])
                for r in csv.DictReader(open(OUT, encoding="utf-8"))}
    cache = {}
    def base(p, s):
        if (p, s) not in cache:
            a = gray(f"{BASE}/{p}_baseline_krea2_seed{s}_00001_.png")
            lp = lapmap(a); m = flatmask(a)
            cache[(p, s)] = (float(lp.mean()),
                             float(lp[3:3+m.shape[0], 3:3+m.shape[1]][m].mean()),
                             float(a.var()), m)
        return cache[(p, s)]
    rows = []
    todo = [(p, s, b, sg) for p in P for s in S for b in BLK for sg in ("pos", "neg")
            if (p, s, b, sg) not in done]
    print(f"done {len(done)}/336, todo {len(todo)}")
    for (p, s, b, sg) in todo:
        if time.time() - t0 > budget:
            print("budget reached, rerun"); break
        f = f"{POS if sg=='pos' else NEG}/{p}_{b}{sg}_0.200_krea2_seed{s}_00001_.png"
        if not os.path.exists(f):
            print(f"  missing {os.path.basename(f)}"); continue
        hb, hbf, vb, m = base(p, s)
        a = gray(f); lp = lapmap(a)
        h = float(lp.mean()); hf_ = float(lp[3:3+m.shape[0], 3:3+m.shape[1]][m].mean()); v = float(a.var())
        rows.append(dict(prompt=p, seed=s, block=b, sign=sg,
                         r_global=f"{h/hb:.6f}", r_flat=f"{hf_/hbf:.6f}", r_cnorm=f"{(h/v)/(hb/vb):.6f}"))
    new = not os.path.exists(OUT)
    with open(OUT, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new: w.writeheader()
        for r in rows: w.writerow(r)
    print(f"wrote {len(rows)}, total {len(done)+len(rows)}/336")


if __name__ == "__main__":
    main()
