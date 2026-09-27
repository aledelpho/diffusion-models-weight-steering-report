#!/usr/bin/env python3
"""Arm B in feature space -- is a block edit a transferable treatment?

Pre-registration: docs/prereg_damage_or_style.md, Amendment 02 section E (commit de7a0e6),
deposited after the multi-image judge gate failed and BEFORE any statistic here was computed.
Prediction D3 carries over verbatim: confirmed if pooled > 0.60 with >= 5/6 blocks above 0.50,
falsified if pooled <= 0.55. Chance is exactly 0.50 by construction.

Two-alternative forced choice, no judge:
    reference = (block b, dose d, sign s) on P01, seed sigma, centred on P01's baseline mean
    target    = the same (b,d,s) on P02, seed sigma, centred on P02's baseline mean
    foil      = (b', d, s) on P02, seed sigma, b' the block matched in ||D|| at that dose
    hit  iff  cos(reference, target) > cos(reference, foil)

Centring per prompt removes the content. One scale, from BASELINES ONLY (pitfall 33).
No render, no judge call.
"""
import collections, csv, itertools, math, sys
import numpy as np

FEAT = "data/style_features_mappa.csv"
DISP = "data/sign_decomposition_cells.csv"
OUT = "data/transfer_test_mappa.csv"
BLOCKS = [f"Block_{i}" for i in range(1, 7)]
DOSES_PRIMARY = ["0.050", "0.200"]
DOSES_ALL = ["0.020", "0.035", "0.050", "0.080", "0.120", "0.200"]
SIGNS = ["pos", "neg"]
SEEDS = ["42", "777", "1337"]
NON = {"file", "width_px", "height_px"}


def parse(f):
    n = f[:-len("_00001_.png")] if f.endswith("_00001_.png") else f
    p, rest = n.split("_", 1)
    seed = rest.rsplit("_seed", 1)[1]
    rest = rest.rsplit("_krea2_seed", 1)[0]
    if rest == "baseline":
        return p, "baseline", "", "", seed
    dose = rest.rsplit("_", 1)[1]
    reg = rest.rsplit("_", 1)[0]
    return p, reg[:-3], reg[-3:], dose, seed


def foils():
    g = collections.defaultdict(list)
    for r in csv.DictReader(open(DISP, encoding="utf-8")):
        g[(r["region"], r["dose"])].append(
            (float(r["norm_plus"]) ** 2 + float(r["norm_minus"]) ** 2) / 2)
    nm = {k: float(np.mean(v)) ** 0.5 for k, v in g.items()}
    return {(b, d): min((abs(nm[(b, d)] - nm[(o, d)]), o) for o in BLOCKS if o != b)[1]
            for d in DOSES_ALL for b in BLOCKS}


def main():
    rows = list(csv.DictReader(open(FEAT, encoding="utf-8")))
    traits = [c for c in rows[0] if c not in NON]
    V = {}
    for r in rows:
        k = parse(r["file"])
        try:
            V[k] = np.array([float(r[t]) for t in traits])
        except ValueError:
            print(f"  non-numeric row skipped: {r['file']}")
    prompts = sorted({k[0] for k in V})
    print(f"{len(V)} images, {len(traits)} traits, prompts {prompts}")

    # --- centring per prompt, and ONE scale taken from the baselines only (pitfall 33)
    base_mean, resid = {}, []
    for p in prompts:
        bs = [V[(p, "baseline", "", "", s)] for s in SEEDS if (p, "baseline", "", "", s) in V]
        if not bs:
            continue
        base_mean[p] = np.mean(bs, axis=0)
        resid += [b - base_mean[p] for b in bs]
    scale = np.std(np.array(resid), axis=0, ddof=1)
    scale[scale == 0] = 1.0
    print(f"scale from {len(resid)} baselines only; {int((scale==1).sum())} trait(s) with zero spread")

    def vec(p, b, sg, d, s):
        k = (p, b, sg, d, s)
        return (V[k] - base_mean[p]) / scale if k in V else None

    def cos(a, b):
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        return float(a @ b / (na * nb)) if na and nb else float("nan")

    F = foils()
    out = []
    for b, d, sg, s in itertools.product(BLOCKS, DOSES_ALL, SIGNS, SEEDS):
        ref = vec("P01", b, sg, d, s)
        tgt = vec("P02", b, sg, d, s)
        fl = vec("P02", F[(b, d)], sg, d, s)
        if ref is None or tgt is None or fl is None:
            continue
        ct, cf = cos(ref, tgt), cos(ref, fl)
        out.append(dict(kind="cross_prompt", block=b, dose=d, sign=sg, seed=s,
                        foil=F[(b, d)], cos_target=f"{ct:.6f}", cos_foil=f"{cf:.6f}",
                        hit=int(ct > cf)))
    # ceiling: same prompt, different seed -- how well does the signature transfer when the
    # content is identical? The cross-prompt number must be read against this, not against 1.0.
    for p, b, d, sg in itertools.product(prompts, BLOCKS, DOSES_ALL, SIGNS):
        if p == "A01":
            continue
        for s1, s2 in itertools.permutations(SEEDS, 2):
            ref = vec(p, b, sg, d, s1)
            tgt = vec(p, b, sg, d, s2)
            fl = vec(p, F[(b, d)], sg, d, s2)
            if ref is None or tgt is None or fl is None:
                continue
            ct, cf = cos(ref, tgt), cos(ref, fl)
            out.append(dict(kind="ceiling_same_prompt", block=b, dose=d, sign=sg,
                            seed=f"{s1}>{s2}", foil=F[(b, d)], cos_target=f"{ct:.6f}",
                            cos_foil=f"{cf:.6f}", hit=int(ct > cf)))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        for r in out:
            w.writerow(r)
    print(f"wrote {len(out)} rows to {OUT}\n")

    cp = [r for r in out if r["kind"] == "cross_prompt"]
    cl = [r for r in out if r["kind"] == "ceiling_same_prompt"]

    def sh(rs):
        return (np.mean([r["hit"] for r in rs]) if rs else float("nan")), len(rs)

    print("=" * 74)
    print("PRIMARY -- doses 0.050 and 0.200, the two the pre-registration named")
    prim = [r for r in cp if r["dose"] in DOSES_PRIMARY]
    print(f"{'block':10s}" + "".join(f"{d:>14s}" for d in DOSES_PRIMARY) + "        mean")
    per = {}
    for b in BLOCKS:
        line = f"{b:10s}"; vals = []
        for d in DOSES_PRIMARY:
            v, n = sh([r for r in prim if r["block"] == b and r["dose"] == d])
            per[(b, d)] = v; vals.append(v)
            line += f"   {v:.3f} ({n:2d})"
        print(line + f"   {np.mean(vals):.3f}")
    pooled, n = sh(prim)
    above = sum(1 for b in BLOCKS if np.mean([per[(b, d)] for d in DOSES_PRIMARY]) > 0.50)
    print(f"\nD3  pooled {pooled:.4f} over {n} items, blocks above 0.50: {above}/6")
    print(f"    confirmed if >0.60 and >=5/6 | falsified if <=0.55  ->  "
          f"{'CONFIRMED' if pooled > 0.60 and above >= 5 else ('FALSIFIED' if pooled <= 0.55 else 'GREY')}")
    k = sum(r["hit"] for r in prim)
    pbin = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
    print(f"    exact binomial, {k}/{n} hits, chance 0.5, one-sided p = {pbin:.3e}")
    kc = sum(1 for b in BLOCKS for d in DOSES_PRIMARY if per[(b, d)] > 0.5)
    print(f"    exact sign test over the 12 block x dose cells: {kc}/12, one-sided p = "
          f"{sum(math.comb(12,i) for i in range(kc,13))/2**12:.5f}")
    print()
    print("=" * 74)
    print("ALL SIX DOSES (secondary, declared exploratory -- the prereg named two)")
    print(f"{'block':10s}" + "".join(f"{d:>8s}" for d in DOSES_ALL))
    for b in BLOCKS:
        print(f"{b:10s}" + "".join(
            f"{sh([r for r in cp if r['block']==b and r['dose']==d])[0]:8.3f}" for d in DOSES_ALL))
    print(f"{'POOLED':10s}" + "".join(
        f"{sh([r for r in cp if r['dose']==d])[0]:8.3f}" for d in DOSES_ALL))
    print()
    print("=" * 74)
    v, n = sh(cl)
    print(f"CEILING -- same prompt, different seed: {v:.4f} over {n} items")
    print(f"    the cross-prompt number is read against this, not against 1.0")
    for sg in SIGNS:
        print(f"    sign {sg}: cross-prompt {sh([r for r in cp if r['sign']==sg])[0]:.3f}   "
              f"ceiling {sh([r for r in cl if r['sign']==sg])[0]:.3f}")
    print()
    rng = np.random.default_rng(0)
    nullv = [np.mean(rng.integers(0, 2, len(prim))) for _ in range(20000)]
    print(f"permutation check that chance is 0.50: null mean {np.mean(nullv):.4f} "
          f"sd {np.std(nullv):.4f}, observed {pooled:.4f} = "
          f"{(pooled-np.mean(nullv))/np.std(nullv):+.1f} sd")


if __name__ == "__main__":
    main()
