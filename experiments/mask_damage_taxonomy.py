#!/usr/bin/env python3
"""Alessandro's reading of the rectified-mask contact sheet, tested.

Given the sheet with no labels he described it as:
  rows 1-2 (B4_mask, B4_anti)        almost no visible grain or blur
  row 3 (B6_mask)    pos: very strong grain   neg: soft grain
  row 4 (B6_anti)    pos: weaker grain        neg: loose blur
  row 5 (B4B6_mask)  pos: very strong grain   neg: soft grain     <- same as row 3
  row 6 (B4B6_anti)  pos: weaker grain        neg: loose blur     <- same as row 4

Two structural claims in that, and neither is a matter of taste:
  A. the combined conditions look like the Block_6 ones, not like the Block_4 ones -- adding
     Block_4 to Block_6 changes nothing visible;
  B. the KIND of damage follows the arm sign (positive adds fine detail, negative removes it)
     while mask-against-anti only changes how much.

A is tested by image distance: for each prompt, seed and arm, how far B4B6 sits from B6 against
how far it sits from B4, on the 8x downsampled z-scored luminance (layout, blind to tone).
B is tested with the absolute fine-detail energy against baseline -- above 1 means detail was
ADDED (grain), below 1 means it was REMOVED (blur). The grain ratio already in use cannot say
this: it is normalised by contrast and reports a direction of its own.

Writes data/mask_damage_taxonomy.csv. No render.
"""
import csv, os, statistics
import numpy as np
from PIL import Image

H = os.path.expanduser("~/mnt")
REN = f"{H}/benchmark_rectified_masks/renders"
BASE = f"{H}/benchmark_mappa--renders"
OUT = "data/mask_damage_taxonomy.csv"
P = ["P01", "P02"]
S = ["42", "777", "1337"]
CONDS = ["B4_mask", "B4_anti", "B6_mask", "B6_anti", "B4B6_mask", "B4B6_anti"]


def gray(p):
    return np.asarray(Image.open(p).convert("L"), dtype=np.float32) / 255.0


def fine(a):
    """Absolute energy of the finest band: 1-2 px detail, not normalised by anything."""
    lp = 4*a[1:-1, 1:-1] - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]
    return float((lp**2).mean())


def blur5(a):
    k = np.array([1, 4, 6, 4, 1], dtype=np.float32) / 16.0
    b = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 0, a)
    return np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 1, b)


def bands(a, nb=5):
    """Absolute energy per octave of detail: band i is about 2^(i+1) pixels.
    Not a difference against the baseline -- the energy the image itself carries at that scale,
    so the ratio to baseline says whether detail was ADDED or REMOVED at each scale separately."""
    out, cur = [], a
    for _ in range(nb):
        lo = blur5(cur)
        out.append(float(((lo - cur)**2).mean()))
        cur = lo[::2, ::2]
    return out


def layout(a):
    s = np.asarray(Image.fromarray((a*255).astype(np.uint8)).resize(
        (a.shape[1]//8, a.shape[0]//8), Image.BOX), dtype=np.float32).ravel()
    return (s - s.mean()) / (s.std() + 1e-9)


def main():
    cache, lay, tex = {}, {}, {}
    def g(path):
        if path not in cache:
            cache[path] = gray(path)
        return cache[path]
    rows = []
    for c in CONDS:
        for arm in ("pos", "neg"):
            fr, cells, prof = [], 0, []
            for p in P:
                for s in S:
                    f = f"{REN}/{p}_{c}_{arm}_seed{s}_00001_.png"
                    b = f"{BASE}/{p}_baseline_krea2_seed{s}_00001_.png"
                    fr.append(fine(g(f)) / fine(g(b)))
                    bb, bx = bands(g(b)), bands(g(f))
                    prof.append([x / y for x, y in zip(bx, bb)])
                    lay[(c, arm, p, s)] = layout(g(f))
                    cells += 1
            m = [statistics.fmean(x[i] for x in prof) for i in range(5)]
            tex[(c, arm)] = m
            peak = max(range(5), key=lambda i: m[i])
            rows.append(dict(condition=c, arm=arm, n=cells,
                             fine_energy_ratio=f"{statistics.fmean(fr):.4f}",
                             **{f"band{i}_ratio": f"{m[i]:.4f}" for i in range(5)},
                             peak_band=peak,
                             kind="added detail (grain)" if statistics.fmean(fr) > 1
                                  else "removed detail (blur)"))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)
    print("  Energy at each scale, as a ratio to the untouched render")
    print("  above 1 = detail ADDED at that scale, below 1 = detail REMOVED\n")
    print("  %-11s %-4s %8s %8s %8s %8s %8s   peak" %
          ("condition", "arm", "1-2px", "2-4px", "4-8px", "8-16px", "16-32px"))
    for r in rows:
        print("  %-11s %-4s %8s %8s %8s %8s %8s   band %d" %
              (r["condition"], r["arm"], r["band0_ratio"], r["band1_ratio"], r["band2_ratio"],
               r["band3_ratio"], r["band4_ratio"], r["peak_band"]))

    print("\n  CLAIM A -- where the combined condition sits\n")
    def dist(k1, k2, arm):
        """Distance between two conditions in TEXTURE space -- the log band profile. The claim
        is about how the surface looks, not where things sit, so layout is the wrong space."""
        a = np.log(np.array(tex[(k1, arm)])); b = np.log(np.array(tex[(k2, arm)]))
        return float(np.sqrt(((a - b)**2).mean()))
    for fam in ("mask", "anti"):
        for arm in ("pos", "neg"):
            d6 = dist(f"B4B6_{fam}", f"B6_{fam}", arm)
            d4 = dist(f"B4B6_{fam}", f"B4_{fam}", arm)
            print("  B4B6_%-5s %-4s is %.4f from B6 and %.4f from B4  -> %.1fx closer to %s"
                  % (fam, arm, d6, d4, max(d4/d6, d6/d4),
                     "Block_6" if d6 < d4 else "Block_4"))
    with open(OUT, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([])
        w.writerow(["combined condition", "arm", "texture distance to B6",
                    "texture distance to B4", "verdict"])
        for fam in ("mask", "anti"):
            for arm in ("pos", "neg"):
                d6 = dist(f"B4B6_{fam}", f"B6_{fam}", arm)
                d4 = dist(f"B4B6_{fam}", f"B4_{fam}", arm)
                w.writerow([f"B4B6_{fam}", arm, f"{d6:.4f}", f"{d4:.4f}",
                            f"{max(d4/d6, d6/d4):.1f}x closer to "
                            + ("Block_6" if d6 < d4 else "Block_4")])


if __name__ == "__main__":
    main()
