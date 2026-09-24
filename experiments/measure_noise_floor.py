"""
experiments/measure_noise_floor.py  --  the seed-to-seed floor of fine texture, measured

sigma(HF) -- how much high-frequency pixel energy varies between two renders that differ
only by their random seed -- is the constant nearly every threshold in this notebook is
quoted against ("11 to 14 times the noise floor" on page 05, the bench check on page 00).
Until this script existed, that number lived only in prose and in two hand-filled CSVs:
docs/punto7_attrito_e_rettificazione.md sec. 7, data/bench_checks.csv, and
data/noise_floor_history.csv. It could not be checked, and neither could its declared n.

The measure is the one frozen in docs/prereg_punto7_simmetria_segno.md sec. 1, before the
data were seen, and it is reproduced here verbatim rather than re-invented:

    g  = cvtColor(imread(file), COLOR_BGR2GRAY).astype(float32)
    HF = std( g - GaussianBlur(g, ksize=(0,0), sigmaX=1.5) )

The floor is, per prompt, the sample standard deviation of HF across INDEPENDENT baseline
seeds (ddof = 1) divided by the mean, in percent.

CORPUS -- the 18 seeds are not one bench. They are:

    benchmark_latenti_b6/renders      seeds 42, 777, 1337   (the three pre-registered
                                      baselines, already on disk when the floor was
                                      still an estimate on three seeds)
    benchmark_pavimento_rumore/renders  seeds 42, 101..115  (the bench rendered to
                                      replace that estimate)

Seed 42 appears in both. Its two renders are pixel-identical -- the PNG files differ only
in the ComfyUI graph carried in their tEXt chunks, which is why an early check on file
hashes failed. This script asserts that identity on pixels and then counts seed 42 ONCE.
18 distinct seeds per prompt, C(18, 2) = 153 pairs.

Counting seed 42 twice would understate the sigma by injecting a zero-variance duplicate,
which is pitfall 17 in miniature: a repeated measure entered as an independent one.

Nothing is rendered. Nothing is deleted. The script reads images and writes two CSVs.

Usage:
    python experiments/measure_noise_floor.py \
        --renders "C:/StabilityMatrix-win-x64/Data/Images/Text2Img/benchmark_latenti_b6/renders" \
        --renders "C:/StabilityMatrix-win-x64/Data/Images/Text2Img/benchmark_pavimento_rumore/renders" \
        --out-renders data/noise_floor_hf_by_render.csv \
        --out-summary data/noise_floor_measured.csv
"""

from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import os
import re
import statistics
import sys

import cv2
import numpy as np

SIGMA_X = 1.5
BASELINE = re.compile(r"^(?P<prompt>P\d+)_baseline_lat_(?P<model>[A-Za-z0-9]+)_seed(?P<seed>\d+)_")


def hf(path: str) -> tuple[float, np.ndarray]:
    """The pre-registered high-frequency energy, and the greyscale it was measured on."""
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"cannot read {path}")
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    return float(np.std(g - cv2.GaussianBlur(g, (0, 0), sigmaX=SIGMA_X))), g


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def measure(dirs: list[str]) -> list[dict]:
    """One row per baseline render. Duplicated seeds are kept, flagged, and proved identical."""
    rows: list[dict] = []
    seen: dict[tuple[str, int], np.ndarray] = {}
    for d in dirs:
        bench = os.path.basename(os.path.dirname(os.path.normpath(d))) or os.path.basename(d)
        paths = sorted(glob.glob(os.path.join(d, "*.png")))
        if not paths:
            sys.exit(f"no PNG in {d}")
        for p in paths:
            name = os.path.basename(p)
            m = BASELINE.match(name)
            if not m:
                continue          # conditions, not baselines: this floor is baseline-only
            key = (m.group("prompt"), int(m.group("seed")))
            value, g = hf(p)
            duplicate = key in seen
            if duplicate:
                diff = int(np.max(np.abs(g - seen[key])))
                if diff != 0:
                    sys.exit(f"{name}: seed {key[1]} of {key[0]} is NOT pixel-identical to its "
                             f"earlier render (max channel difference {diff}). The two benches "
                             f"cannot be pooled until that is explained.")
            else:
                seen[key] = g
            rows.append({
                "file": name,
                "bench": bench,
                "prompt_id": key[0],
                "model": m.group("model"),
                "seed": key[1],
                "width_px": g.shape[1],
                "height_px": g.shape[0],
                "hf": round(value, 6),
                "duplicate_of_earlier_bench": "yes" if duplicate else "no",
                "counted_in_sigma": "no" if duplicate else "yes",
                "sha256": sha256(p),
            })
            print(f"  [{bench}] {name}  HF = {value:.4f}"
                  f"{'   (duplicate, pixel-identical, not counted)' if duplicate else ''}",
                  file=sys.stderr)
    return rows


def summarise(rows: list[dict]) -> list[dict]:
    out = []
    counted = [r for r in rows if r["counted_in_sigma"] == "yes"]
    for prompt in sorted({r["prompt_id"] for r in counted}):
        sub = sorted((r for r in counted if r["prompt_id"] == prompt), key=lambda r: r["seed"])
        vals = [r["hf"] for r in sub]
        n = len(vals)
        mean = statistics.fmean(vals)
        sd = statistics.stdev(vals)
        sizes = sorted({(r["width_px"], r["height_px"]) for r in sub})
        out.append({
            "prompt_id": prompt,
            "n_seeds": n,
            "pairs": n * (n - 1) // 2,
            "seeds": " ".join(str(r["seed"]) for r in sub),
            "benches": " ".join(sorted({r["bench"] for r in sub})),
            "mean_hf": round(mean, 6),
            "sd_hf": round(sd, 6),
            "relative_sigma_pct": round(100.0 * sd / mean, 4),
            "resolutions": " ".join(f"{w}x{h}" for w, h in sizes),
            "feature": "HF = std(g - GaussianBlur(g, sigmaX=1.5)) on BGR2GRAY float32, "
                       "frozen in docs/prereg_punto7_simmetria_segno.md sec. 1",
            "estimator": "sample sd (ddof=1) across distinct baseline seeds, over the mean, percent",
        })
    return out


def write(path: str, rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path}  ({len(rows)} rows)", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", action="append", required=True,
                    help="a renders directory; repeat the flag for every bench in the corpus")
    ap.add_argument("--out-renders", required=True)
    ap.add_argument("--out-summary", required=True)
    a = ap.parse_args()
    rows = measure(a.renders)
    write(a.out_renders, rows)
    summary = summarise(rows)
    write(a.out_summary, summary)
    print()
    for s in summary:
        print(f"{s['prompt_id']}: n = {s['n_seeds']} seeds ({s['pairs']} pairs)  "
              f"mean HF = {s['mean_hf']:.4f}  sd = {s['sd_hf']:.4f}  "
              f"relative sigma = {s['relative_sigma_pct']:.4f}%")


if __name__ == "__main__":
    main()
