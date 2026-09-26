#!/usr/bin/env python3
"""Pixel-level decomposition of the signed block map.

Pre-registration: docs/prereg_sign_decomposition_pixels.md (deposited 2026-09-26,
commit 0fb062e, before any statistic here was computed).

For a matched pair of renders at +d and -d on the same block group, same prompt,
same seed, against the same-seed baseline:

    c = (Dplus + Dminus)/2   the common mode  -- what happens whatever the sign
    m = (Dplus - Dminus)/2   the signed mode  -- what reverses with the sign
    F = |c|^2 / (|c|^2 + |m|^2)               -- the sign-blind share of the energy

F is the primary statistic. F -> 0 is a linear knob, F -> 1 is a rectified block.

Resumable: one chunk per (prompt, seed, dose); already-written chunks are skipped.
No renders are generated or requested.
"""
import os, sys, csv, itertools
import numpy as np
from PIL import Image

RENDERS = os.environ.get("MAPPA_RENDERS", os.path.expanduser("~/mnt/benchmark_mappa--renders"))
OUT_CELLS = "data/sign_decomposition_cells.csv"
OUT_PAIRS = "data/sign_decomposition_blockpairs.csv"

PROMPTS = ["P01", "P02"]
SEEDS = ["42", "777", "1337"]
DOSES = ["0.020", "0.035", "0.050", "0.080", "0.120", "0.200"]
BLOCKS = ["Block_1", "Block_2", "Block_3", "Block_4", "Block_5", "Block_6"]
SHAPE = (1280, 1024, 3)

CELL_FIELDS = ["prompt", "seed", "region", "dose", "n_pix",
               "norm_plus", "norm_minus", "rho_mag", "cos_pm", "F",
               "norm_c", "norm_m", "hf_c", "hf_m", "hf_plus", "hf_minus"]
PAIR_FIELDS = ["prompt", "seed", "dose", "block_a", "block_b",
               "cos_plus_plus", "cos_plus_minus", "cos_minus_minus"]


def fname(prompt, region, sign, dose, seed):
    if region == "baseline":
        return f"{prompt}_baseline_krea2_seed{seed}_00001_.png"
    return f"{prompt}_{region}{sign}_{dose}_krea2_seed{seed}_00001_.png"


def load(path):
    im = Image.open(path)
    if im.size != (SHAPE[1], SHAPE[0]) or im.mode != "RGB":
        raise SystemExit(f"GUARD G2 FAILED: {os.path.basename(path)} is {im.size} {im.mode}")
    return np.asarray(im, dtype=np.float32) / 255.0


def laplacian_energy(x):
    """HF share: |lap(x)|^2 / |x|^2, fixed 3x3 kernel [[0,-1,0],[-1,4,-1],[0,-1,0]]."""
    d = float(np.sum(x.astype(np.float64) ** 2))
    if d == 0.0:
        return float("nan")
    lap = (4.0 * x[1:-1, 1:-1, :]
           - x[:-2, 1:-1, :] - x[2:, 1:-1, :]
           - x[1:-1, :-2, :] - x[1:-1, 2:, :])
    return float(np.sum(lap.astype(np.float64) ** 2) / d)


def cos(a, b):
    na = float(np.sqrt(np.sum(a.astype(np.float64) ** 2)))
    nb = float(np.sqrt(np.sum(b.astype(np.float64) ** 2)))
    if na == 0.0 or nb == 0.0:
        return float("nan")
    return float(np.sum(a.astype(np.float64) * b.astype(np.float64)) / (na * nb))


def done_chunks(path, keyfn):
    if not os.path.exists(path):
        return set()
    with open(path, newline="") as fh:
        return {keyfn(r) for r in csv.DictReader(fh)}


def append(path, fields, rows):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    budget = float(os.environ.get("CHUNK_BUDGET_S", "150"))
    import time
    t0 = time.time()

    # --- G1: baselines ---
    missing = [fname(p, "baseline", "", "", s) for p in PROMPTS for s in SEEDS
               if not os.path.exists(os.path.join(RENDERS, fname(p, "baseline", "", "", s)))]
    if missing:
        raise SystemExit(f"GUARD G1 FAILED: missing baselines {missing}")

    have = done_chunks(OUT_CELLS, lambda r: (r["prompt"], r["seed"], r["dose"]))
    todo = [(p, s, d) for p in PROMPTS for s in SEEDS for d in DOSES if (p, s, d) not in have]
    print(f"chunks done {len(have)}/36, todo {len(todo)}")

    zeros = []
    for (p, s, d) in todo:
        if time.time() - t0 > budget:
            print("budget reached, rerun to continue")
            break
        base = load(os.path.join(RENDERS, fname(p, "baseline", "", "", s)))
        Dp, Dm = {}, {}
        cell_rows = []
        for b in BLOCKS:
            plus = load(os.path.join(RENDERS, fname(p, b, "pos", d, s))) - base
            minus = load(os.path.join(RENDERS, fname(p, b, "neg", d, s))) - base
            np_ = float(np.sqrt(np.sum(plus.astype(np.float64) ** 2)))
            nm_ = float(np.sqrt(np.sum(minus.astype(np.float64) ** 2)))
            # --- G3: dead slot check ---
            if np_ == 0.0 or nm_ == 0.0:
                zeros.append((p, s, b, d, np_, nm_))
                continue
            c = 0.5 * (plus + minus)
            m = 0.5 * (plus - minus)
            nc = float(np.sqrt(np.sum(c.astype(np.float64) ** 2)))
            nmm = float(np.sqrt(np.sum(m.astype(np.float64) ** 2)))
            cell_rows.append(dict(
                prompt=p, seed=s, region=b, dose=d, n_pix=int(plus.size),
                norm_plus=f"{np_:.8f}", norm_minus=f"{nm_:.8f}",
                rho_mag=f"{np_/nm_:.8f}", cos_pm=f"{cos(plus, minus):.8f}",
                F=f"{nc**2/(nc**2+nmm**2):.8f}",
                norm_c=f"{nc:.8f}", norm_m=f"{nmm:.8f}",
                hf_c=f"{laplacian_energy(c):.8f}", hf_m=f"{laplacian_energy(m):.8f}",
                hf_plus=f"{laplacian_energy(plus):.8f}",
                hf_minus=f"{laplacian_energy(minus):.8f}"))
            Dp[b], Dm[b] = plus, minus
        pair_rows = []
        for a, bb in itertools.combinations(BLOCKS, 2):
            if a not in Dp or bb not in Dp:
                continue
            pair_rows.append(dict(prompt=p, seed=s, dose=d, block_a=a, block_b=bb,
                                  cos_plus_plus=f"{cos(Dp[a], Dp[bb]):.8f}",
                                  cos_plus_minus=f"{cos(Dp[a], Dm[bb]):.8f}",
                                  cos_minus_minus=f"{cos(Dm[a], Dm[bb]):.8f}"))
        append(OUT_CELLS, CELL_FIELDS, cell_rows)
        append(OUT_PAIRS, PAIR_FIELDS, pair_rows)
        print(f"  {p} seed{s} d={d}: {len(cell_rows)} cells, {len(pair_rows)} pairs")
        del Dp, Dm, base

    if zeros:
        print("GUARD G3: exact-zero displacement (dead slots), excluded:")
        for z in zeros:
            print("   ", z)


if __name__ == "__main__":
    main()
