#!/usr/bin/env python3
"""Does a declared colour move more, or less, under a weight edit?

Pre-registration: docs/prereg_declared_colour.md (commit 5aa4f52), deposited before this ran.
Matched pairs G1-G6 (colour clause) against S7_01-S7_06 (same subject, no colour clause), from
data/style_features.csv. No render, no new extraction.
"""
import csv, math, re, collections
import numpy as np

SRC = "data/style_features.csv"
OUT = "data/declared_colour_test.csv"
PAIRS = [("G1", "S7_01"), ("G2", "S7_02"), ("G3", "S7_03"),
         ("G4", "S7_04"), ("G5", "S7_05"), ("G6", "S7_06")]
HUE = {"G1": "teal", "G2": "yellow", "G3": "teal", "G4": "chartreuse", "G5": "blue", "G6": "purple"}
SIM = {"G1": 0.94, "G2": 0.94, "G3": 0.78, "G4": 0.95, "G5": 0.45, "G6": 0.95}
COND = ["rand_pos", "rand_neg", "preset_pos", "preset_neg", "blockshuf_pos", "blockshuf_neg"]
SEEDS = ["42", "777", "1337", "9999", "4242145"]     # the five shared by both arms
COL = ["color_top4_cluster_share", "color_cluster_entropy_norm", "color_n_effective",
       "colorfulness_hs"]
TEX = ["glcm_contrast", "glcm_homogeneity", "glcm_energy", "glcm_correlation", "lbp_entropy",
       "lbp_uniform_share", "fft_radial_slope", "fft_high_freq_share"]


def load():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8", errors="replace")))
    T = {}
    for r in rows:
        m = re.match(r"^(G\d|S7_\d\d)_(.+?)_seed(\d+)_", r["file"])
        if not m:
            continue
        try:
            T[(m.group(1), m.group(2), m.group(3))] = {t: float(r[t]) for t in COL + TEX}
        except (ValueError, KeyError):
            pass
    return T


def zscores(T, p):
    """Displacement per trait, in units of that prompt's own baseline seed noise."""
    base = {}
    sig = {}
    for t in COL + TEX:
        v = [T[(p, "baseline", s)][t] for s in SEEDS if (p, "baseline", s) in T]
        if len(v) < 3:
            return None
        base[t], sig[t] = float(np.mean(v)), float(np.std(v, ddof=1))
    out = {}
    for t in COL + TEX:
        if sig[t] <= 0:
            continue
        z = [abs(T[(p, c, s)][t] - base[t]) / sig[t]
             for c in COND for s in SEEDS if (p, c, s) in T]
        if z:
            out[t] = float(np.mean(z))
    return out


def main():
    T = load()
    print(f"{len(T)} feature rows indexed\n")
    rows = []
    print(f"{'pair':22s} {'hue':11s} {'sim':>5s} | {'colour_z':>9s} {'texture_z':>10s} {'ratio':>7s} "
          f"| {'colour_z':>9s} {'texture_z':>10s} {'ratio':>7s} | direction")
    print(f"{'':22s} {'':11s} {'':5s} | {'------ DECLARED (A1) ------':^28s} "
          f"| {'---- UNDECLARED (A2) -----':^28s} |")
    for a1, a2 in PAIRS:
        za, zb = zscores(T, a1), zscores(T, a2)
        if za is None or zb is None:
            print(f"{a1}/{a2}: insufficient baselines, skipped"); continue
        ca, ta = np.mean([za[t] for t in COL if t in za]), np.mean([za[t] for t in TEX if t in za])
        cb, tb = np.mean([zb[t] for t in COL if t in zb]), np.mean([zb[t] for t in TEX if t in zb])
        ra, rb = ca / ta, cb / tb
        d = "declared MORE" if ra > rb else "declared LESS"
        rows.append(dict(pair=f"{a1}/{a2}", hue=HUE[a1], text_sim=SIM[a1],
                         colour_z_declared=f"{ca:.4f}", texture_z_declared=f"{ta:.4f}",
                         ratio_declared=f"{ra:.4f}", colour_z_undeclared=f"{cb:.4f}",
                         texture_z_undeclared=f"{tb:.4f}", ratio_undeclared=f"{rb:.4f}",
                         declared_moves_more=int(ra > rb)))
        print(f"{a1+' / '+a2:22s} {HUE[a1]:11s} {SIM[a1]:5.2f} | {ca:9.3f} {ta:10.3f} {ra:7.3f} "
              f"| {cb:9.3f} {tb:10.3f} {rb:7.3f} | {d}")
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    def verdict(sub, label):
        k = sum(r["declared_moves_more"] for r in sub)
        n = len(sub)
        # two-sided exact sign test, capped at 1: doubling the smaller tail can exceed 1
        # when k == n/2, which it did on the first run (printed 1.3125). Capped here.
        p = min(1.0, 2 * min(sum(math.comb(n, i) for i in range(k, n + 1)),
                             sum(math.comb(n, i) for i in range(0, k + 1))) / 2 ** n)
        v = ("H-A CONFIRMED (declared moves MORE)" if k >= n - 1 and k > n / 2 else
             "H-C CONFIRMED (declared moves LESS)" if (n - k) >= n - 1 and k < n / 2 else
             "UNDECIDED")
        print(f"\n{label}: declared moves more in {k}/{n} pairs, exact two-sided p = {p:.5f}"
              f"  (floor {2/2**n:.5f})\n   -> {v}")
        return k, n

    print("\n" + "=" * 92)
    verdict(rows, "PRIMARY, all six pairs")
    verdict([r for r in rows if r["pair"] != "G5/S7_05"], "SENSITIVITY, pair 5 excluded (text sim 0.45)")
    ra = np.mean([float(r["ratio_declared"]) for r in rows])
    rb = np.mean([float(r["ratio_undeclared"]) for r in rows])
    print(f"\nmean ratio: declared {ra:.4f}   undeclared {rb:.4f}   difference {ra-rb:+.4f}")
    ca = np.mean([float(r["colour_z_declared"]) for r in rows])
    cb = np.mean([float(r["colour_z_undeclared"]) for r in rows])
    print(f"SECONDARY, colour_z alone: declared {ca:.3f}   undeclared {cb:.3f}   "
          f"declared higher in {sum(1 for r in rows if float(r['colour_z_declared'])>float(r['colour_z_undeclared']))}/6")
    ta = np.mean([float(r["texture_z_declared"]) for r in rows])
    tb = np.mean([float(r["texture_z_undeclared"]) for r in rows])
    print(f"CONTROL,   texture_z alone: declared {ta:.3f}   undeclared {tb:.3f}   "
          f"(should not differ systematically -- the colour clause is not about texture)")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
