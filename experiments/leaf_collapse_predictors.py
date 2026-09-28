#!/usr/bin/env python3
"""Register C22: what separates the nine seeds that fire from the eleven that do not?

benchmark_leaf_collapse arm A: identical prompt, identical edit, twenty seeds, and a bimodal
outcome with nothing between chroma ratio 0.085 and 0.518. The only thing that differs is the
seed, so the question is whether anything about the seed is visible in advance.

The seed's fingerprint used here is its OWN UNPERTURBED BASELINE, which is a deterministic function
of the seed. The initial latent itself is not reconstructed: doing so means reimplementing
ComfyUI's RNG exactly, and a near-miss would look like a null result. This is a proxy and is
reported as one.

TWELVE features, listed before any of them was computed, and NOT chosen after seeing which
separates. Exact two-sided Mann-Whitney on 9 against 11, Bonferroni over the twelve. With twelve
features and twenty samples a raw p of 0.02 is noise; only a Bonferroni-surviving result counts,
and the script prints both so the difference cannot be blurred.

Writes data/leaf_collapse_predictors.csv. No render.
"""
import csv, itertools, os, statistics
import numpy as np
from PIL import Image
from scipy import ndimage

REN = os.path.expanduser("~/mnt/benchmark_leaf_collapse/renders")
CELLS = "data/leaf_collapse_cells.csv"
OUT = "data/leaf_collapse_predictors.csv"

FEATURES = ["fg_share", "hue_deg", "chroma", "elongation", "orientation_deg",
            "centroid_x", "centroid_y", "solidity", "contrast", "grain",
            "edge_density_in_leaf", "mean_value_in_leaf"]


def describe(path):
    im = Image.open(path)
    a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    g = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
    mx, mn = a.max(2), a.min(2)
    d = mx - mn
    sat = np.where(mx > 1e-5, d / np.maximum(mx, 1e-5), 0.0)
    r, gg, b = a[..., 0], a[..., 1], a[..., 2]
    hue = np.zeros_like(mx)
    m = (mx == r) & (d > 1e-5); hue[m] = (60 * ((gg[m] - b[m]) / d[m]) + 360) % 360
    m = (mx == gg) & (d > 1e-5); hue[m] = (60 * ((b[m] - r[m]) / d[m]) + 120) % 360
    m = (mx == b) & (d > 1e-5); hue[m] = (60 * ((r[m] - gg[m]) / d[m]) + 240) % 360
    small = np.asarray(Image.fromarray((mx * 255).astype(np.uint8)).resize(
        (mx.shape[1] // 8, mx.shape[0] // 8), Image.BOX), dtype=np.float32) / 255.0
    ring = np.concatenate([small[:5].ravel(), small[-5:].ravel(),
                           small[:, :5].ravel(), small[:, -5:].ravel()])
    msk = ndimage.binary_opening(np.abs(small - float(np.median(ring))) > 0.06, np.ones((3, 3)))
    lab, n = ndimage.label(msk)
    if n:
        msk = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
    fg = np.asarray(Image.fromarray((msk * 255).astype(np.uint8)).resize(
        (mx.shape[1], mx.shape[0]), Image.NEAREST)) > 127

    ys, xs = np.nonzero(fg)
    cy, cx = ys.mean(), xs.mean()
    yy, xx = ys - cy, xs - cx
    cov = np.array([[float((xx*xx).mean()), float((xx*yy).mean())],
                    [float((xx*yy).mean()), float((yy*yy).mean())]])
    ev, evec = np.linalg.eigh(cov)
    elong = float(np.sqrt(ev[1] / max(ev[0], 1e-9)))
    ori = float(np.degrees(np.arctan2(evec[1, 1], evec[0, 1])) % 180)
    filled = ndimage.binary_fill_holes(fg)
    hull = ndimage.binary_closing(filled, np.ones((31, 31)))
    solidity = float(fg.sum() / max(hull.sum(), 1))
    lp = (4*g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:])**2
    inner = fg[1:-1, 1:-1]
    s = sat[fg]
    rad = np.deg2rad(hue[fg])
    h = float(np.rad2deg(np.arctan2((s*np.sin(rad)).sum(), (s*np.cos(rad)).sum())) % 360)
    return dict(fg_share=float(fg.mean()), hue_deg=h, chroma=float(s.mean()),
                elongation=elong, orientation_deg=ori,
                centroid_x=float(cx / fg.shape[1]), centroid_y=float(cy / fg.shape[0]),
                solidity=solidity, contrast=float(g.var()), grain=float(lp.mean()),
                edge_density_in_leaf=float(lp[inner].mean()),
                mean_value_in_leaf=float(g[fg].mean()))


def mannwhitney_exact(a, b):
    """Exact two-sided p on the rank-sum of the smaller group. n=9,11 -> 167960 combinations."""
    all_v = sorted(a + b)
    rank = {v: i + 1 for i, v in enumerate(all_v)}
    if len(set(all_v)) != len(all_v):          # ties -> midranks
        rank = {}
        i = 0
        while i < len(all_v):
            j = i
            while j + 1 < len(all_v) and all_v[j + 1] == all_v[i]:
                j += 1
            for k in range(i, j + 1):
                rank[all_v[k]] = (i + j) / 2 + 1
            i = j + 1
    obs = sum(rank[v] for v in a)
    n, k = len(all_v), len(a)
    idx = list(range(n))
    ranks = [rank[v] for v in all_v]
    cnt = tot = 0
    mean = k * (n + 1) / 2
    for c in itertools.combinations(idx, k):
        s = sum(ranks[i] for i in c)
        tot += 1
        if abs(s - mean) >= abs(obs - mean) - 1e-9:
            cnt += 1
    return cnt / tot


def main():
    cells = [x for x in csv.DictReader(open(CELLS, encoding="utf-8")) if x["arm"] == "A_seeds"]
    rows = []
    for c in cells:
        f = f"{REN}/LN_baseline_krea2_seed{c['seed']}_00001_.png"
        d = describe(f)
        d.update(seed=c["seed"], hit=int(c["hit"]), chroma_ratio=float(c["chroma_ratio"]))
        rows.append(d)
    hit = [r for r in rows if r["hit"]]
    no = [r for r in rows if not r["hit"]]
    print(f"{len(hit)} fire, {len(no)} do not. Twelve features, exact Mann-Whitney, "
          f"Bonferroni x{len(FEATURES)}.\n")
    out = []
    for feat in FEATURES:
        a = [r[feat] for r in hit]
        b = [r[feat] for r in no]
        p = mannwhitney_exact(a, b)
        out.append(dict(feature=feat, mean_fire=f"{statistics.fmean(a):.5f}",
                        mean_quiet=f"{statistics.fmean(b):.5f}",
                        p_raw=f"{p:.5f}", p_bonferroni=f"{min(1.0, p*len(FEATURES)):.5f}",
                        survives=int(p * len(FEATURES) < 0.05)))
    out.sort(key=lambda r: float(r["p_raw"]))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader()
        for r in out: w.writerow(r)
    for r in out:
        flag = "  <== survives Bonferroni" if r["survives"] else ""
        print("  %-22s fire %10s  quiet %10s   p=%s  (corrected %s)%s"
              % (r["feature"], r["mean_fire"], r["mean_quiet"], r["p_raw"],
                 r["p_bonferroni"], flag))
    print(f"\n  {sum(r['survives'] for r in out)} of {len(FEATURES)} survive correction -> {OUT}")




def clustering_test():
    """Do the nine firing seeds occupy a region of seed space, jointly?

    The twelve univariate tests can miss a structure that only exists in combination. This one is
    multivariate and NOT circular: it looks only at the UNPERTURBED baselines, which know nothing
    about the outcome, and asks whether the nine that will fire resemble each other more than a
    random 9/11 split of the same twenty would.

    Similarity is the Pearson correlation of the 8x downsampled, z-scored luminance -- shape and
    layout, blind to tone and to colour. Statistic: mean within-group similarity, pooled over both
    groups. Null: all 167960 ways of splitting twenty seeds 9/11, enumerated exactly, no sampling.
    """
    import csv, itertools, os
    import numpy as np
    from PIL import Image
    cells = [x for x in csv.DictReader(open(CELLS, encoding="utf-8")) if x["arm"] == "A_seeds"]
    seeds = [c["seed"] for c in cells]
    hit = [i for i, c in enumerate(cells) if c["hit"] == "1"]
    vecs = []
    for s in seeds:
        g = np.asarray(Image.open(f"{REN}/LN_baseline_krea2_seed{s}_00001_.png").convert("L"),
                       dtype=np.float32)
        sm = np.asarray(Image.fromarray(g.astype(np.uint8)).resize(
            (g.shape[1] // 8, g.shape[0] // 8), Image.BOX), dtype=np.float32).ravel()
        vecs.append((sm - sm.mean()) / (sm.std() + 1e-9))
    V = np.array(vecs)
    S = (V @ V.T) / V.shape[1]
    n = len(seeds)

    def stat(group):
        g = set(group)
        o = [i for i in range(n) if i not in g]
        def within(idx):
            if len(idx) < 2:
                return 0.0
            return float(np.mean([S[i, j] for i, j in itertools.combinations(idx, 2)]))
        return (within(sorted(g)) * len(g) + within(o) * len(o)) / n

    obs = stat(hit)
    cnt = tot = 0
    for c in itertools.combinations(range(n), len(hit)):
        tot += 1
        if stat(c) >= obs - 1e-12:
            cnt += 1
    p = cnt / tot
    print(f"\n  multivariate clustering of the baselines:")
    print(f"    observed mean within-group similarity {obs:.5f}")
    print(f"    exact permutation p = {p:.5f}  over all {tot} splits")
    print(f"    -> {'the firing seeds cluster' if p < 0.05 else 'no joint structure either'}")
    with open("data/leaf_collapse_clustering.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["statistic", "value"])
        w.writerow(["mean_within_group_similarity_observed", f"{obs:.6f}"])
        w.writerow(["exact_permutation_p", f"{p:.6f}"])
        w.writerow(["splits_enumerated", tot])
        w.writerow(["mean_pairwise_similarity_all_20", f"{float(np.mean([S[i,j] for i,j in itertools.combinations(range(n),2)])):.6f}"])


if __name__ == "__main__":
    main()
    clustering_test()
