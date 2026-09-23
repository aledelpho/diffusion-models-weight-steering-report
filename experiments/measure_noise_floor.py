"""
experiments/measure_noise_floor.py  --  the seed-to-seed floor of fine texture, measured

Nearly every threshold in this notebook is quoted as a multiple of sigma(HF): how much
the high-frequency share of the power spectrum varies between two renders that differ
only by their random seed. Until now that number existed only as prose typed into
data/bench_checks.csv and data/noise_floor_history.csv. No script in the repository
computed it, so it could not be checked, and its declared n could not be checked either.

This script computes it from the renders themselves.

  feature   fft_high_freq_share, imported unchanged from experiments/style_features.py
            (the share of radial power-spectrum energy in the top third of the 40 rings,
            measured on the native-resolution greyscale -- no resize, no crop)
  estimator per prompt, the sample standard deviation across independent baseline seeds
            (ddof = 1) divided by the mean, in percent
  corpus    benchmark_pavimento_rumore/renders, every baseline PNG in it

The pair count C(n, 2) is reported because the notebook quotes one; it is descriptive,
it is not what the relative sigma is computed over.

Nothing is rendered. Nothing is deleted. The script reads images and writes two CSVs.

Usage:
    python experiments/measure_noise_floor.py \
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style_features import load_image, fft_radial_profile  # noqa: E402

FFT_BINS = 40
NAME = re.compile(r"^(?P<prompt>P\d+)_baseline_lat_(?P<model>[A-Za-z0-9]+)_seed(?P<seed>\d+)_")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def measure(renders_dir: str) -> list[dict]:
    paths = sorted(glob.glob(os.path.join(renders_dir, "*.png")))
    if not paths:
        sys.exit(f"no PNG in {renders_dir}")
    rows = []
    for p in paths:
        name = os.path.basename(p)
        m = NAME.match(name)
        if not m:
            print(f"  skipped, name does not parse: {name}", file=sys.stderr)
            continue
        _, gray = load_image(p)
        feats = fft_radial_profile(gray, n_bins=FFT_BINS)
        rows.append({
            "file": name,
            "prompt_id": m.group("prompt"),
            "model": m.group("model"),
            "seed": int(m.group("seed")),
            "width_px": gray.shape[1],
            "height_px": gray.shape[0],
            "fft_high_freq_share": feats["fft_high_freq_share"],
            "fft_radial_slope": feats["fft_radial_slope"],
            "sha256": sha256(p),
        })
        print(f"  {name}  HF = {feats['fft_high_freq_share']:.6f}", file=sys.stderr)
    return rows


def summarise(rows: list[dict]) -> list[dict]:
    out = []
    for prompt in sorted({r["prompt_id"] for r in rows}):
        sub = [r for r in rows if r["prompt_id"] == prompt]
        seeds = sorted({r["seed"] for r in sub})
        if len(seeds) != len(sub):
            sys.exit(f"{prompt}: {len(sub)} renders but {len(seeds)} distinct seeds -- "
                     f"a seed appears twice, the sigma would be understated")
        vals = [r["fft_high_freq_share"] for r in sub]
        n = len(vals)
        mean = statistics.fmean(vals)
        sd = statistics.stdev(vals) if n > 1 else float("nan")
        sizes = sorted({(r["width_px"], r["height_px"]) for r in sub})
        out.append({
            "prompt_id": prompt,
            "n_seeds": n,
            "pairs": n * (n - 1) // 2,
            "seed_min": seeds[0],
            "seed_max": seeds[-1],
            "mean_hf_share": round(mean, 10),
            "sd_hf_share": round(sd, 10),
            "relative_sigma_pct": round(100.0 * sd / mean, 4),
            "resolutions": " ".join(f"{w}x{h}" for w, h in sizes),
            "feature": "fft_high_freq_share (style_features.fft_radial_profile, 40 bins, top third)",
            "estimator": "sample sd (ddof=1) across seeds, divided by the mean, in percent",
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
    ap.add_argument("--renders", required=True)
    ap.add_argument("--out-renders", required=True)
    ap.add_argument("--out-summary", required=True)
    a = ap.parse_args()
    rows = measure(a.renders)
    write(a.out_renders, rows)
    summary = summarise(rows)
    write(a.out_summary, summary)
    print()
    for s in summary:
        print(f"{s['prompt_id']}: n = {s['n_seeds']} seeds ({s['pairs']} pairs), "
              f"mean HF = {s['mean_hf_share']:.6f}, sd = {s['sd_hf_share']:.6f}, "
              f"relative sigma = {s['relative_sigma_pct']:.4f}%  [{s['resolutions']}]")


if __name__ == "__main__":
    main()
