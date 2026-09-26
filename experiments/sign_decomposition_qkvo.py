#!/usr/bin/env python3
"""Pixel-level sign decomposition on the q/k/v/o atlas.

Pre-registration: docs/prereg_sign_decomposition_pixels.md, Amendment 01 (commit 9bf01f0),
deposited before this script was run. Frozen predictions:
  A1-P1  F higher for wq/wk than for wv/wo, gap of means > 0.15
  A1-P2  F lower than the 0.673 of whole block groups in >= 6 of 8 cells

Baseline per (scene, seed) = the normscales_all control, exact zero displacement.
Resumable per (scene, seed). No new renders.
"""
import os, csv, itertools, time
import numpy as np
from PIL import Image

RENDERS = os.environ.get("QKVO_RENDERS", os.path.expanduser("~/mnt/benchmark_qkvo_atlas--renders"))
OUT = "data/sign_decomposition_qkvo_cells.csv"
OUTP = "data/sign_decomposition_qkvo_pairs.csv"
PREFIX = "Arthemy_QKVO"
CELLS = ["wq_b1", "wk_b1", "wv_b1", "wo_b1", "wq_b6", "wk_b6", "wv_b6", "wo_b6"]
SEEDS = ["42", "777", "1337"]
FIELDS = ["scene", "seed", "cell", "norm_plus", "norm_minus", "rho_mag", "cos_pm", "F",
          "hf_c", "hf_m", "hf_plus", "hf_minus"]
PFIELDS = ["scene", "seed", "cell_a", "cell_b", "cos_plus_plus", "cos_plus_minus"]


def path(scene, cell, sign, seed):
    return os.path.join(RENDERS, f"{scene}_{PREFIX}_{cell}_{sign}_seed{seed}_00001_.png")


def load(p):
    im = Image.open(p)
    assert im.size == (1024, 1280) and im.mode == "RGB", (p, im.size, im.mode)
    return np.asarray(im, dtype=np.float32) / 255.0


def e(x):
    return float(np.sum(x.astype(np.float64) ** 2))


def hf(x):
    d = e(x)
    if d == 0:
        return float("nan")
    lap = (4.0 * x[1:-1, 1:-1, :] - x[:-2, 1:-1, :] - x[2:, 1:-1, :]
           - x[1:-1, :-2, :] - x[1:-1, 2:, :])
    return e(lap) / d


def cos(a, b):
    na, nb = np.sqrt(e(a)), np.sqrt(e(b))
    return float(np.sum(a.astype(np.float64) * b.astype(np.float64)) / (na * nb)) if na and nb else float("nan")


def append(p, fields, rows):
    new = not os.path.exists(p)
    with open(p, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        if new: w.writeheader()
        for r in rows: w.writerow(r)


def main():
    scenes = sorted({f.split("_" + PREFIX)[0] for f in os.listdir(RENDERS)
                     if PREFIX in f and not f.startswith("determinism")})
    have = set()
    if os.path.exists(OUT):
        have = {(r["scene"], r["seed"]) for r in csv.DictReader(open(OUT))}
    print(f"scenes {len(scenes)}: {scenes}")
    t0 = time.time()
    for sc in scenes:
        for sd in SEEDS:
            if (sc, sd) in have: continue
            if time.time() - t0 > float(os.environ.get("CHUNK_BUDGET_S", "145")):
                print("budget reached, rerun"); return
            # baseline = normscales control; + and - are byte-identical, average for safety
            b1 = load(path(sc, "normscales_all", "pos", sd))
            b2 = load(path(sc, "normscales_all", "neg", sd))
            dmax = float(np.max(np.abs(b1 - b2)))
            base = 0.5 * (b1 + b2)
            rows, D = [], {}
            for c in CELLS:
                pl = load(path(sc, c, "pos", sd)) - base
                mn = load(path(sc, c, "neg", sd)) - base
                npl, nmn = np.sqrt(e(pl)), np.sqrt(e(mn))
                if npl == 0 or nmn == 0:
                    print(f"GUARD G3: zero displacement {sc} {sd} {c}"); continue
                cc, mm = 0.5 * (pl + mn), 0.5 * (pl - mn)
                rows.append(dict(scene=sc, seed=sd, cell=c,
                                 norm_plus=f"{npl:.8f}", norm_minus=f"{nmn:.8f}",
                                 rho_mag=f"{npl/nmn:.8f}", cos_pm=f"{cos(pl,mn):.8f}",
                                 F=f"{e(cc)/(e(cc)+e(mm)):.8f}",
                                 hf_c=f"{hf(cc):.8f}", hf_m=f"{hf(mm):.8f}",
                                 hf_plus=f"{hf(pl):.8f}", hf_minus=f"{hf(mn):.8f}"))
                D[c] = (pl, mn)
            prs = [dict(scene=sc, seed=sd, cell_a=a, cell_b=b,
                        cos_plus_plus=f"{cos(D[a][0],D[b][0]):.8f}",
                        cos_plus_minus=f"{cos(D[a][0],D[b][1]):.8f}")
                   for a, b in itertools.combinations(CELLS, 2) if a in D and b in D]
            append(OUT, FIELDS, rows); append(OUTP, PFIELDS, prs)
            print(f"  {sc} seed{sd}: {len(rows)} cells (control +/- max px diff {dmax:.6f})")
            del D


if __name__ == "__main__":
    main()
