#!/usr/bin/env python3
"""B1 -- does the grain statistic survive a correction for contrast?

Pitfall candidate 75 (docs/looking_at_block1_and_block6.md section 3): a texture statistic summed
over the whole frame reports the sum of 'grain added' and 'contrast changed', and on Block_6 the
second hides the first. This re-runs the project's own grain measure three ways on the corpus that
is reachable, and asks whether punto7's conclusions change.

The three estimators, all relative to the same-seed baseline:
  r_global : HF(x) / HF(base)                       -- what the project has used
  r_flat   : HF restricted to the flattest 40% of the BASELINE -- punto7 section 7's own estimator
  r_cnorm  : [HF(x)/var(x)] / [HF(base)/var(base)]  -- contrast-normalised

Then punto7's own summary statistics on top of each: the common mode c = sqrt(r+ * r-), and its
correlation with depth. Nothing is fished: the estimators and the summaries were fixed before
running, and all three are reported whatever they say.

Resumable. No render.
"""
import csv, itertools, os, sys, time
import numpy as np
from PIL import Image
from numpy.lib.stride_tricks import sliding_window_view

D = os.path.expanduser("~/mnt/benchmark_mappa--renders")
OUT = "data/texture_estimator_audit.csv"
P = ["P01", "P02"]
S = ["42", "777", "1337"]
DOSES = ["0.020", "0.035", "0.050", "0.080", "0.120", "0.200"]
B = [f"Block_{i}" for i in range(1, 7)]
FIELDS = ["prompt", "seed", "block", "dose", "sign",
          "hf_global", "hf_flat", "var", "r_global", "r_flat", "r_cnorm"]


def gray(p):
    return np.asarray(Image.open(p).convert("L"), dtype=np.float32) / 255.0


def lapmap(a):
    return (4 * a[1:-1, 1:-1] - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]) ** 2


def flatmask(a, q=40):
    """The flattest q% of the baseline, by local variance in 9x9 windows -- the estimator
    punto7 section 7 already uses. Computed on the BASELINE only, so the same pixels are
    compared in every condition of that cell."""
    v = sliding_window_view(a, (9, 9)).var(axis=(2, 3))
    m = v <= np.percentile(v, q)
    return m


def main():
    budget = float(os.environ.get("B", "100"))
    t0 = time.time()
    done = set()
    if os.path.exists(OUT):
        done = {(r["prompt"], r["seed"], r["block"], r["dose"], r["sign"])
                for r in csv.DictReader(open(OUT, encoding="utf-8"))}
    todo = [(p, s, b, d, sg) for p in P for s in S for b in B for d in DOSES
            for sg in ("pos", "neg") if (p, s, b, d, sg) not in done]
    print(f"done {len(done)}/432, todo {len(todo)}")
    if not todo:
        return
    cache = {}

    def base(p, s):
        if (p, s) not in cache:
            a = gray(f"{D}/{p}_baseline_krea2_seed{s}_00001_.png")
            lp = lapmap(a)
            m = flatmask(a)
            # ALIGNMENT: lapmap[i,j] is pixel (i+1,j+1); the 9x9 variance map[i,j] is pixel
            # (i+4,j+4). The offset is 3. Getting this wrong shifts the mask by three pixels
            # and silently measures the wrong region -- it did, twice, before this comment.
            sub = lp[3:3 + m.shape[0], 3:3 + m.shape[1]]
            cache[(p, s)] = (float(lp.mean()), float(sub[m].mean()), float(a.var()), m)
        return cache[(p, s)]

    rows = []
    for (p, s, b, d, sg) in todo:
        if time.time() - t0 > budget:
            print("budget reached, rerun"); break
        hb, hbf, vb, m = base(p, s)
        f = f"{D}/{p}_{b}{sg}_{d}_krea2_seed{s}_00001_.png"
        if not os.path.exists(f):
            print(f"  missing {os.path.basename(f)}"); continue
        a = gray(f)
        lp = lapmap(a)
        h = float(lp.mean())
        hf_ = float(lp[3:3 + m.shape[0], 3:3 + m.shape[1]][m].mean())
        v = float(a.var())
        rows.append(dict(prompt=p, seed=s, block=b, dose=d, sign=sg,
                         hf_global=f"{h:.8f}", hf_flat=f"{hf_:.8f}", var=f"{v:.8f}",
                         r_global=f"{h/hb:.6f}", r_flat=f"{hf_/hbf:.6f}",
                         r_cnorm=f"{(h/v)/(hb/vb):.6f}"))
    new = not os.path.exists(OUT)
    with open(OUT, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)}, total {len(done)+len(rows)}/432")


if __name__ == "__main__":
    main()
