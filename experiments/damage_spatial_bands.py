#!/usr/bin/env python3
"""Where, in spatial frequency, does an edit's damage actually live?

Alessandro, looking at native-resolution crops: the render this project's frontier ranked best
(`blk27 neg`) has visible structural defects, and the reason nobody called them grain may be that
they are expressed as loose blobs of colour rather than as fine speckle.

If that is right it is a hole in the instrument, because the two statistics in use sample the two
ENDS of the spectrum and nothing samples the middle:
  grain (r_cnorm)  -- a 3x3 Laplacian: band 0, detail of 1-2 px
  layout_cost_z    -- an 8x downsample: bands 3 and coarser, structure of 16 px and up
Bands 1 and 2 -- detail between 2 and 8 px, which is the scale of mottling, of a face's modelling,
of smeared background objects -- are measured by neither.

This decomposes (render - baseline) into octave bands with a Gaussian pyramid and reports the
energy in each, so the claim can be checked instead of asserted. Band energies are normalised by
the baseline's own energy in the same band, so a band that is naturally quiet does not look calm.

Corpus and baselines identical to experiments/style_damage_frontier.py. No render.
Writes data/damage_bands_cells.csv and data/damage_bands.csv. Resumable: B is a seconds budget.
"""
import csv, os, time
import numpy as np
from PIL import Image
from scipy import ndimage

H = os.path.expanduser("~/mnt")
BASE = f"{H}/benchmark_mappa--renders"
OUT = "data/damage_bands_cells.csv"
OUT_A = "data/damage_bands.csv"
P = ["P01", "P02"]
S = ["42", "777", "1337"]
NB = 6
FIELDS = (["family", "condition", "dose", "arm", "prompt", "seed"] +
          [f"band{i}" for i in range(NB)])


def jobs():
    out = []
    for g in range(1, 7):
        for arm in ("pos", "neg"):
            for d in ("0.020", "0.035", "0.050", "0.080", "0.120", "0.200"):
                out.append(("group", f"Block_{g}", arm, d,
                            f"{BASE}/{{p}}_Block_{g}{arm}_{d}_krea2_seed{{s}}_00001_.png"))
    for b in range(28):
        for arm in ("pos", "neg"):
            root = f"{H}/benchmark_profondita" + ("" if arm == "pos" else "_neg") + "/renders"
            out.append(("subblock", f"blk{b:02d}", arm, "0.200",
                        f"{root}/{{p}}_blk{b:02d}{arm}_0.200_krea2_seed{{s}}_00001_.png"))
    for c in ("B4_mask", "B4_anti", "B6_mask", "B6_anti", "B4B6_mask", "B4B6_anti"):
        for arm in ("pos", "neg"):
            out.append(("mask", c, arm, "0.200",
                        f"{H}/benchmark_rectified_masks/renders/{{p}}_{c}_{arm}_seed{{s}}_00001_.png"))
    return out


def blur(a):
    """Binomial 5-tap, separable, edges extended. `np.convolve(..., mode="same")` ZERO-PADS:
    on a constant image, whose true band energy is 0, it reports 4.0e-4 -- a quarter of a real
    render's band-0 energy. Away from an 8 px frame the two agree to 0.000%."""
    k = np.array([1, 4, 6, 4, 1], dtype=np.float32) / 16.0
    return ndimage.convolve1d(ndimage.convolve1d(a, k, axis=0, mode="nearest"),
                              k, axis=1, mode="nearest")


def pyramid(a):
    """Laplacian-pyramid band energies: band i holds detail of about 2^(i+1) pixels."""
    out, cur = [], a
    for _ in range(NB):
        lo = blur(cur)
        out.append(lo - cur)          # the detail removed at this scale
        cur = lo[::2, ::2]
    return out


def gray(p):
    return np.asarray(Image.open(p).convert("L"), dtype=np.float32) / 255.0


def main():
    budget = float(os.environ.get("B", "165")); t0 = time.time()
    done = set()
    if os.path.exists(OUT):
        done = {(r["family"], r["condition"], r["arm"], r["dose"], r["prompt"], r["seed"])
                for r in csv.DictReader(open(OUT, encoding="utf-8"))}
    cache = {}
    def base(p, s):
        if (p, s) not in cache:
            a = gray(f"{BASE}/{p}_baseline_krea2_seed{s}_00001_.png")
            cache[(p, s)] = (a, [float((b**2).mean()) for b in pyramid(a)])
        return cache[(p, s)]
    todo = [(f, c, a, d, t, p, s) for (f, c, a, d, t) in jobs() for p in P for s in S
            if (f, c, a, d, p, s) not in done]
    print(f"done {len(done)}, todo {len(todo)}")
    rows = []
    for (fam, cond, arm, dose, tpl, p, s) in todo:
        if time.time() - t0 > budget:
            print("budget reached, rerun to continue"); break
        f = tpl.format(p=p, s=s)
        if not os.path.exists(f):
            continue
        ba, benergy = base(p, s)
        d = gray(f) - ba
        e = [float((b**2).mean()) for b in pyramid(d)]
        r = dict(family=fam, condition=cond, dose=dose, arm=arm, prompt=p, seed=s)
        for i in range(NB):
            r[f"band{i}"] = f"{e[i]/benergy[i]:.6f}"
        rows.append(r)
    new = not os.path.exists(OUT)
    with open(OUT, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new: w.writeheader()
        for r in rows: w.writerow(r)
    print(f"wrote {len(rows)}, total {len(done)+len(rows)}")


def aggregate():
    import statistics
    rows = list(csv.DictReader(open(OUT, encoding="utf-8")))
    agg = {}
    for r in rows:
        k = (r["family"], r["condition"], r["arm"], r["dose"])
        agg.setdefault(k, [[] for _ in range(NB)])
        for i in range(NB):
            agg[k][i].append(float(r[f"band{i}"]))
    out = []
    for k, v in agg.items():
        m = [statistics.fmean(x) for x in v]
        tot = sum(m)
        out.append(dict(family=k[0], condition=k[1], arm=k[2], dose=k[3], n=len(v[0]),
                        **{f"band{i}": f"{m[i]:.5f}" for i in range(NB)},
                        mid_share=f"{(m[1]+m[2])/tot:.4f}" if tot else "",
                        fine_share=f"{m[0]/tot:.4f}" if tot else "",
                        coarse_share=f"{sum(m[3:])/tot:.4f}" if tot else ""))
    out.sort(key=lambda r: -float(r["band1"]) - float(r["band2"]))
    with open(OUT_A, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader()
        for r in out: w.writerow(r)
    print(f"{len(out)} conditions -> {OUT_A}")


if __name__ == "__main__":
    main()
    if not os.environ.get("NO_AGG"):
        aggregate()
