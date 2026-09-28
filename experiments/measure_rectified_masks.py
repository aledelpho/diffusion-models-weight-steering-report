#!/usr/bin/env python3
"""Measures the 72 rectified-sign-mask renders and scores them against the frozen predictions.

Design and predictions: docs/RENDERS_2026-09-27_rectified_masks.md (frozen before the renders).
Renders: benchmark_rectified_masks/renders, 6 conditions x 2 arms x 2 prompts x 3 seeds.
Baselines: benchmark_mappa, the same prompts and seeds as every other bench in this project.

Two statistics, the same two the pre-check used (docs/internal_fights_by_group.md section 1):
  contrast = var(x)/var(baseline)
  grain    = r_cnorm = [HF(x)/var(x)] / [HF(b)/var(b)]   (docs/texture_estimator_audit_result.md)
r_flat is not computed: it is saturated and nothing is argued from it.

Predictions are composed from the single-block measurements already on disk
(data/texture_audit_profondita.csv) -- nothing is fitted here.

Writes data/rectified_mask_vector_check.csv (the tuner vector read back out of every render's
metadata and compared with the plan), data/rectified_mask_measurements.csv (72 rows),
data/rectified_mask_verdict.csv and data/rectified_mask_stats.csv (the M1-M6 scoring and the
side-of-1 test).
No render.
"""
import csv, json, math, os, statistics
import numpy as np
from PIL import Image

H = os.path.expanduser("~/mnt")
REN = f"{H}/benchmark_rectified_masks/renders"
BASE = f"{H}/benchmark_mappa--renders"
SINGLES = "data/texture_audit_profondita.csv"
OUT_M = "data/rectified_mask_measurements.csv"
OUT_V = "data/rectified_mask_verdict.csv"
OUT_S = "data/rectified_mask_stats.csv"
OUT_C = "data/rectified_mask_vector_check.csv"

P = ["P01", "P02"]
S = ["42", "777", "1337"]
# condition -> {block index: sign of its gain in the `pos` arm}; the `neg` arm flips every sign.
COND = {
    "B4_mask":   {15: +1, 18: -1},
    "B4_anti":   {15: +1, 18: +1},
    "B6_mask":   {27: +1, 26: -1},
    "B6_anti":   {27: +1, 26: +1},
    "B4B6_mask": {15: +1, 18: -1, 27: +1, 26: -1},
    "B4B6_anti": {15: +1, 18: +1, 27: +1, 26: +1},
}


def check_vectors():
    """Reads the tuner vector back out of every render's metadata and compares it with the plan."""
    want = {}
    for c, spec in COND.items():
        for arm in ("pos", "neg"):
            v = [0.0] * 34
            for idx, s in spec.items():
                v[idx] = round(s * 0.200 * (1 if arm == "pos" else -1), 3)
            want[(c, arm)] = v
    out = []
    for c in COND:
        for arm in ("pos", "neg"):
            for pr in P:
                for s in S:
                    f = f"{REN}/{pr}_{c}_{arm}_seed{s}_00001_.png"
                    if not os.path.exists(f):
                        continue
                    node = next(n for n in json.loads(Image.open(f).info["prompt"]).values()
                                if n.get("class_type") == "ArthemyKrea2ModelTuner")
                    got = [float(x) for x in node["inputs"]["vectors_override"].split(",") if x.strip()]
                    ok = (len(got) == 34 and node["inputs"]["mode"] == "Real Value"
                          and node["inputs"]["granular_json"] == ""
                          and all(abs(a - b) < 1e-6 for a, b in zip(got, want[(c, arm)])))
                    out.append(dict(file=os.path.basename(f), condition=c, arm=arm,
                                    mode=node["inputs"]["mode"], slots=len(got),
                                    granular_json_empty=int(node["inputs"]["granular_json"] == ""),
                                    nonzero=";".join(f"{i}={v:+.3f}" for i, v in enumerate(got) if v),
                                    matches_plan=int(ok)))
    with open(OUT_C, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader()
        for r in out: w.writerow(r)
    k = sum(r["matches_plan"] for r in out)
    print(f"vectors: {k}/{len(out)} renders carry exactly the planned vector -> {OUT_C}")


def gray(p):
    return np.asarray(Image.open(p).convert("L"), dtype=np.float32) / 255.0


def lapmap(a):
    return (4*a[1:-1, 1:-1] - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:])**2


def colour_stats(path):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    mx = a.max(2); mn = a.min(2)
    sat = np.where(mx > 1e-5, (mx - mn) / np.maximum(mx, 1e-5), 0.0)
    g = np.asarray(Image.open(path).convert("L"), dtype=np.float32) / 255.0
    gy, gx = np.gradient(g)
    return float(sat.mean()), float(np.hypot(gx, gy).mean())


def measure():
    cache = {}
    def base(p, s):
        if (p, s) not in cache:
            a = gray(f"{BASE}/{p}_baseline_krea2_seed{s}_00001_.png")
            cache[(p, s)] = (float(lapmap(a).mean()), float(a.var()))
        return cache[(p, s)]
    rows = []
    for c in COND:
        for arm in ("pos", "neg"):
            for p in P:
                for s in S:
                    f = f"{REN}/{p}_{c}_{arm}_seed{s}_00001_.png"
                    if not os.path.exists(f):
                        print(f"  MISSING {os.path.basename(f)}")
                        continue
                    hb, vb = base(p, s)
                    a = gray(f)
                    h = float(lapmap(a).mean()); v = float(a.var())
                    sm, gm = colour_stats(f)
                    rows.append(dict(prompt=p, seed=s, condition=c, arm=arm,
                                     r_global=f"{h/hb:.6f}",
                                     contrast=f"{v/vb:.6f}",
                                     grain=f"{(h/v)/(hb/vb):.6f}",
                                     sat_mean=f"{sm:.4f}", grad_mean=f"{gm:.5f}"))
    with open(OUT_M, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["prompt", "seed", "condition", "arm",
                                           "r_global", "contrast", "grain",
                                           "sat_mean", "grad_mean"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)} rows to {OUT_M}")
    return rows


def singles():
    """Single-block ratios, pooled over the same 6 cells, from the corpus the masks were built on."""
    acc = {}
    for r in csv.DictReader(open(SINGLES, encoding="utf-8")):
        g = float(r["r_global"]); cn = float(r["r_cnorm"])
        key = (int(r["block"][3:]), r["sign"])
        acc.setdefault(key, {"contrast": [], "grain": []})
        acc[key]["contrast"].append(g / cn)   # r_global / r_cnorm == var ratio
        acc[key]["grain"].append(cn)
    return {k: {st: statistics.fmean(v[st]) for st in v} for k, v in acc.items()}


def binom_ge(k, n):
    """P(X >= k) for X ~ Binomial(n, 1/2)."""
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2**n


def fisher_two_sided(a, b, c, d):
    """Two-sided Fisher exact on the 2x2 table [[a,b],[c,d]], by summing tables no more likely."""
    n = a + b + c + d
    r1, r2, c1 = a + b, c + d, a + c
    def prob(x):
        return (math.comb(r1, x) * math.comb(r2, c1 - x)) / math.comb(n, c1)
    p0 = prob(a) * (1 + 1e-9)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    return sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= p0)


def score(out, rows):
    """M1-M6 against the thresholds frozen in docs/RENDERS_2026-09-27_rectified_masks.md section 5."""
    def v(c, arm, st, field="observed"):
        return float(next(r[field] for r in out
                          if r["condition"] == c and r["arm"] == arm and r["statistic"] == st))
    res = []
    def verdict(x, conf, fals):
        return "CONFIRMED" if conf(x) else ("FALSIFIED" if fals(x) else "GREY")
    m1 = v("B4_mask", "pos", "contrast")
    m2 = v("B4_anti", "pos", "contrast")
    m3 = v("B6_mask", "pos", "grain")
    m4 = v("B6_anti", "pos", "grain")
    res.append(("M1", "B4_mask pos contrast", v("B4_mask", "pos", "contrast", "predicted"), m1,
                verdict(m1, lambda x: x > 1.08, lambda x: x < 1.02)))
    res.append(("M2", "B4_anti pos contrast", v("B4_anti", "pos", "contrast", "predicted"), m2,
                verdict(m2, lambda x: x < 1.00, lambda x: x > 1.06)))
    res.append(("M3", "B6_mask pos grain", v("B6_mask", "pos", "grain", "predicted"), m3,
                verdict(m3, lambda x: x > 1.12, lambda x: x < 1.03)))
    res.append(("M4", "B6_anti pos grain", v("B6_anti", "pos", "grain", "predicted"), m4,
                verdict(m4, lambda x: x < 0.95, lambda x: x > 1.02)))
    gc, gg = m1 - m2, m3 - m4
    res.append(("M5a", "separation on contrast (B4_mask - B4_anti)", 0.21, gc,
                verdict(gc, lambda x: x > 0.08, lambda x: x < 0)))
    res.append(("M5b", "separation on grain (B6_mask - B6_anti)", 0.37, gg,
                verdict(gg, lambda x: x > 0.08, lambda x: x < 0)))
    dc = abs(v("B4B6_mask", "pos", "contrast") - m1)
    dg = abs(v("B4B6_mask", "pos", "grain") - m3)
    res.append(("M6a", "|B4B6_mask - B4_mask| on contrast", 0.0, dc,
                verdict(dc, lambda x: x < 0.10, lambda x: x > 0.20)))
    res.append(("M6b", "|B4B6_mask - B6_mask| on grain", 0.0, dg,
                verdict(dg, lambda x: x < 0.10, lambda x: x > 0.20)))
    km = sum(r["side_agrees"] for r in out if r["condition"].endswith("mask"))
    ka = sum(r["side_agrees"] for r in out if r["condition"].endswith("anti"))
    with open(OUT_S, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "quantity", "predicted", "observed", "verdict"])
        for i, q, p_, o, vd in res:
            w.writerow([i, q, f"{p_:.4f}", f"{o:.4f}", vd])
        w.writerow(["S1", "masks: side of 1 correct out of 12", 6, km,
                    f"binomial p={binom_ge(km, 12):.5f}"])
        w.writerow(["S2", "anti-masks: side of 1 correct out of 12", 6, ka,
                    f"binomial p={binom_ge(ka, 12):.5f}"])
        w.writerow(["S3", "masks vs anti-masks, all cells", "", f"{km}/12 vs {ka}/12",
                    f"Fisher exact p={fisher_two_sided(km, 12-km, ka, 12-ka):.5f}"])
        # The combined arm shares its blocks with both single arms, so its 8 cells are not
        # independent of the other 16. S4 repeats S3 on the independent cells only.
        sub = [r for r in out if not r["condition"].startswith("B4B6")]
        jm = sum(r["side_agrees"] for r in sub if r["condition"].endswith("mask"))
        ja = sum(r["side_agrees"] for r in sub if r["condition"].endswith("anti"))
        w.writerow(["S4", "masks vs anti-masks, combined arm dropped", "", f"{jm}/8 vs {ja}/8",
                    f"Fisher exact p={fisher_two_sided(jm, 8-jm, ja, 8-ja):.5f}"])
        # The coin-flip null of S1/S2 is wrong if edits mostly push a statistic below 1 anyway.
        # S5 is the naive rule "always predict below 1", scored on the same cells.
        for kind in ("mask", "anti"):
            sel = [r for r in out if r["condition"].endswith(kind)]
            naive = sum(1 for r in sel if r["side_observed"] == -1)
            w.writerow([f"S5_{kind}", f"naive rule 'always below 1' on {kind} cells", "",
                        f"{naive}/{len(sel)}", "control for the marginal tendency"])
        # The only cells where composition says something the naive rule does not.
        up = [r for r in out if r["condition"].endswith("mask") and r["side_predicted"] == 1]
        w.writerow(["S6", "mask cells where composition predicts ABOVE 1", "",
                    f"{sum(r['side_agrees'] for r in up)}/{len(up)}",
                    f"binomial p={binom_ge(sum(r['side_agrees'] for r in up), len(up)):.5f}"])
    print(f"wrote {len(res)} verdict rows + the side tests to {OUT_S}")
    for i, q, p_, o, vd in res:
        print(f"  {i:4s} {q:44s} pred {p_:7.4f}  obs {o:7.4f}  {vd}")
    print(f"  S3   masks {km}/12 vs anti {ka}/12, Fisher p={fisher_two_sided(km, 12-km, ka, 12-ka):.5f}")


def main():
    check_vectors()
    rows = measure()
    sg = singles()
    out = []
    for c, spec in COND.items():
        for arm in ("pos", "neg"):
            for st in ("contrast", "grain"):
                pred = 1.0
                for idx, s in spec.items():
                    sign = ("pos" if s > 0 else "neg") if arm == "pos" else ("neg" if s > 0 else "pos")
                    pred *= sg[(idx, sign)][st]
                obs = statistics.fmean(float(r[st]) for r in rows
                                       if r["condition"] == c and r["arm"] == arm)
                n = sum(1 for r in rows if r["condition"] == c and r["arm"] == arm)
                sp = 1 if pred > 1 else -1
                so = 1 if obs > 1 else -1
                out.append(dict(condition=c, arm=arm, statistic=st, n=n,
                                predicted=f"{pred:.4f}", observed=f"{obs:.4f}",
                                deviation=f"{obs-pred:+.4f}",
                                side_predicted=sp, side_observed=so,
                                side_agrees=int(sp == so)))
    with open(OUT_V, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        for r in out:
            w.writerow(r)
    print(f"wrote {len(out)} rows to {OUT_V}")
    score(out, rows)


if __name__ == "__main__":
    main()
