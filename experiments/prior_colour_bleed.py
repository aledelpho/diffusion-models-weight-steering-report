#!/usr/bin/env python3
"""When a declared unusual colour is perturbed, does the object's OWN colour come back?

Seen by eye on `PCU` (a purple pinecone), seed 777: after the edit the purple is still there, and
brown has appeared in the crevices and at the scale bases. The mean-hue statistic cannot say that
-- it averages purple and brown into a 36 degree "shift" and loses which of the two moved.

So this counts pixels instead of averaging them. For each subject, two hue bands are defined from
that subject's OWN BASELINES, not by hand:
  prototypical band = circular mean hue of the `P` baseline (brown mushroom, red tomato, ...) +-30
  declared band     = circular mean hue of the `U` baseline (purple ...) +-30
and for the `U` cells it reports the share of the object that falls in each, before and after.

If the declared colour simply rotated, the declared share falls and the prototypical share does not
rise. If the object's prior colour is coming back, the prototypical share rises.

Arm C of benchmark_leaf_collapse: 4 subjects x 3 seeds. Exact sign test over the 12 cells.
Writes data/prior_colour_bleed.csv. No render.
"""
import csv, math, os, statistics
import numpy as np
from PIL import Image
from scipy import ndimage

REN = os.path.expanduser("~/mnt/benchmark_leaf_collapse/renders")
OUT = "data/prior_colour_bleed.csv"
SUBJECTS = ["MU", "TO", "PC", "BA"]
SEEDS = ["42", "777", "1337"]
HALFWIDTH = 30.0


def load(path):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    mx, mn = a.max(2), a.min(2)
    d = mx - mn
    sat = np.where(mx > 1e-5, d / np.maximum(mx, 1e-5), 0.0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hue = np.zeros_like(mx)
    m = (mx == r) & (d > 1e-5); hue[m] = (60 * ((g[m] - b[m]) / d[m]) + 360) % 360
    m = (mx == g) & (d > 1e-5); hue[m] = (60 * ((b[m] - r[m]) / d[m]) + 120) % 360
    m = (mx == b) & (d > 1e-5); hue[m] = (60 * ((r[m] - g[m]) / d[m]) + 240) % 360
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
    return hue[fg], sat[fg]


def mean_hue(h, s):
    rad = np.deg2rad(h)
    return float(np.rad2deg(np.arctan2((s*np.sin(rad)).sum(), (s*np.cos(rad)).sum())) % 360)


def share(h, s, centre):
    """Share of coloured object pixels whose hue is within HALFWIDTH of `centre`.
    Only pixels with saturation above 0.15 count: an achromatic pixel has no hue to place."""
    ok = s > 0.15
    if ok.sum() == 0:
        return 0.0
    d = np.abs((h[ok] - centre + 180) % 360 - 180)
    return float((d <= HALFWIDTH).mean())


def main():
    rows = []
    for sub in SUBJECTS:
        # bands from this subject's own baselines, pooled over seeds
        hp, sp = zip(*[load(f"{REN}/{sub}P_baseline_krea2_seed{s}_00001_.png") for s in SEEDS])
        hu, su = zip(*[load(f"{REN}/{sub}U_baseline_krea2_seed{s}_00001_.png") for s in SEEDS])
        proto = mean_hue(np.concatenate(hp), np.concatenate(sp))
        decl = mean_hue(np.concatenate(hu), np.concatenate(su))
        for s in SEEDS:
            hb, sb = load(f"{REN}/{sub}U_baseline_krea2_seed{s}_00001_.png")
            hx, sx = load(f"{REN}/{sub}U_B4neg_0.200_krea2_seed{s}_00001_.png")
            rows.append(dict(
                subject=sub, seed=s,
                prototypical_hue=f"{proto:.1f}", declared_hue=f"{decl:.1f}",
                proto_share_baseline=f"{share(hb, sb, proto):.4f}",
                proto_share_perturbed=f"{share(hx, sx, proto):.4f}",
                proto_delta=f"{share(hx, sx, proto) - share(hb, sb, proto):+.4f}",
                declared_share_baseline=f"{share(hb, sb, decl):.4f}",
                declared_share_perturbed=f"{share(hx, sx, decl):.4f}",
                declared_delta=f"{share(hx, sx, decl) - share(hb, sb, decl):+.4f}"))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    print(f"wrote {len(rows)} cells to {OUT}\n")
    for sub in SUBJECTS:
        g = [r for r in rows if r["subject"] == sub]
        print("  %s  prototypical %5s deg, declared %5s deg | proto share %+.3f, declared share %+.3f"
              % (sub, g[0]["prototypical_hue"], g[0]["declared_hue"],
                 statistics.fmean(float(r["proto_delta"]) for r in g),
                 statistics.fmean(float(r["declared_delta"]) for r in g)))
    up = sum(1 for r in rows if float(r["proto_delta"]) > 0)
    dn = sum(1 for r in rows if float(r["declared_delta"]) < 0)
    n = len(rows)
    def sgn(k):
        return min(1.0, 2 * sum(math.comb(n, i) for i in range(k, n+1)) / 2**n)
    print(f"\n  prototypical share rises in {up}/{n} cells, exact sign test p = {sgn(up):.5f}")
    print(f"  declared share falls in    {dn}/{n} cells, exact sign test p = {sgn(dn):.5f}")


if __name__ == "__main__":
    main()
