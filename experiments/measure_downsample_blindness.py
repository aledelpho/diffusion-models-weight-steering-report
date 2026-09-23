# -*- coding: utf-8 -*-
"""
experiments/measure_downsample_blindness.py
===========================================
Why page 01 says CLIP cannot see the mark-style shift, measured instead of argued.

The claim `clip-224-is-blind-to-it` has always carried a mechanism and no measurement: CLIP's
vision tower reads a 224x224 thumbnail, the preset's signature lives in stroke width and
crosshatch density, and those are high-frequency, so the resample should destroy them before
the encoder ever looks. Nothing in the repository tested any part of that.

This script tests the part that needs no encoder: **does the separation survive the
resample?** For each prompt it takes the preset arm and the block-shuffle control at the same
seed -- the same contrast the published PC1 uses -- and extracts the repository's own stroke
and texture features twice:

    native    the render as saved, 1024x1280
    clip224   exactly CLIP's preprocessing: bicubic resize of the shorter side to 224,
              then a 224x224 centre crop

Then, per feature, the paired effect size across prompts (Cohen's dz) and an exact sign-flip
p, in both conditions. If the mechanism is real, dz collapses toward zero at 224 on the
features the claim names. If dz survives, the claim's reason is wrong even if its conclusion
happens to hold.

What this does NOT do: run CLIP. No CLIP image encoder can be reached from here, and the one
on this machine, Data/Models/ClipVision/clip_vision_h.safetensors, is 1.2 GB. The encoder
itself is measured by experiments/measure_clip_distance.py, which must run locally.

The prompt is the unit of analysis, one seed per prompt: seeds are repeated measures, not
independent observations (pitfall 17).

Nothing is rendered. Writes data/downsample_blindness.csv.

Usage:
    python experiments/measure_downsample_blindness.py \
        --renders "C:/StabilityMatrix-win-x64/Data/Images/Text2Img/benchmark_stage7/renders" \
        --manifest data/stage7b_images.csv --seed 1337 \
        --out data/downsample_blindness.csv
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import os
import statistics
import sys
import tempfile

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style_features import extract_all_features  # noqa: E402

CLIP_SIDE = 224

# The features the claim is about: the stroke and crosshatch family, plus two texture
# summaries. Declared here, before any number is looked at.
FEATURES = [
    "stroke_width_median_px", "stroke_width_std_px", "stroke_width_cv",
    "edge_density", "contour_mean_length_px", "contour_n_components",
    "crosshatch_entropy_mean", "crosshatch_entropy_p90",
    "lbp_entropy", "glcm_contrast", "fft_high_freq_share",
]


def clip_preprocess(path: str) -> np.ndarray:
    """CLIP's own image pipeline: bicubic resize of the shorter side, then a centre crop."""
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"cannot read {path}")
    h, w = img.shape[:2]
    scale = CLIP_SIDE / min(h, w)
    small = cv2.resize(img, (int(round(w * scale)), int(round(h * scale))),
                       interpolation=cv2.INTER_CUBIC)
    sh, sw = small.shape[:2]
    y, x = (sh - CLIP_SIDE) // 2, (sw - CLIP_SIDE) // 2
    return small[y:y + CLIP_SIDE, x:x + CLIP_SIDE]


def features_at(path: str, scale: str) -> dict:
    if scale == "native":
        return extract_all_features(path)
    crop = clip_preprocess(path)
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        cv2.imwrite(tmp, crop)
        return extract_all_features(tmp)
    finally:
        os.unlink(tmp)


def sign_flip_p(diffs: list[float]) -> tuple[float, float]:
    """Exact two-tailed sign-flip p on the paired differences, and its floor."""
    n = len(diffs)
    if n > 20:
        raise SystemExit(f"{n} pairs is too many to enumerate exactly; the floor claim would be false")
    obs = abs(statistics.fmean(diffs))
    hits = 0
    for signs in itertools.product((1, -1), repeat=n):
        if abs(statistics.fmean(s * d for s, d in zip(signs, diffs))) >= obs - 1e-12:
            hits += 1
    return hits / 2 ** n, 2 / 2 ** n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--treatment", default="preset_pos")
    ap.add_argument("--control", default="blockshuf_pos")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.manifest, encoding="utf-8-sig")))
    cells: dict[str, dict[str, str]] = {}
    for r in rows:
        if r["seed"] != a.seed:
            continue
        cells.setdefault(r["prompt_id"], {})[r["cond_name"]] = os.path.basename(r["image_path"])
    prompts = sorted(p for p, c in cells.items() if a.treatment in c and a.control in c)
    if len(prompts) < 4:
        sys.exit(f"only {len(prompts)} prompts carry both arms at seed {a.seed}")

    measured: dict[tuple[str, str, str], dict] = {}
    for p in prompts:
        for arm in (a.treatment, a.control):
            path = os.path.join(a.renders, cells[p][arm])
            for scale in ("native", "clip224"):
                measured[(p, arm, scale)] = features_at(path, scale)
                print(f"  {p} {arm:16s} {scale:8s}", file=sys.stderr, flush=True)

    out = []
    for scale in ("native", "clip224"):
        for f in FEATURES:
            diffs = [measured[(p, a.treatment, scale)][f] - measured[(p, a.control, scale)][f]
                     for p in prompts]
            mean = statistics.fmean(diffs)
            sd = statistics.stdev(diffs)
            dz = mean / sd if sd else float("nan")
            p_val, floor = sign_flip_p(diffs)
            out.append({
                "scale": scale,
                "side_px": "native 1024x1280" if scale == "native" else f"{CLIP_SIDE}x{CLIP_SIDE}",
                "feature": f,
                "n_prompts": len(prompts),
                "seed": a.seed,
                "mean_diff": round(mean, 6),
                "sd_diff": round(sd, 6),
                "dz": round(dz, 4),
                "abs_dz": round(abs(dz), 4),
                "p_sign_flip": round(p_val, 8),
                "p_floor": round(floor, 8),
                "contrast": f"{a.treatment} minus {a.control}",
            })

    # the survival ratio: how much of the native effect size is left at 224
    by = {(r["scale"], r["feature"]): r["abs_dz"] for r in out}
    for r in out:
        n = by[("native", r["feature"])]
        r["fraction_of_native_dz"] = round(by[("clip224", r["feature"])] / n, 4) if n else ""

    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"\nwrote {a.out}  ({len(out)} rows, {len(prompts)} prompts)\n")
    print(f"{'feature':26s} {'|dz| native':>12s} {'|dz| 224':>10s} {'kept':>7s} {'p native':>10s} {'p 224':>10s}")
    for f in FEATURES:
        n = next(r for r in out if r["scale"] == "native" and r["feature"] == f)
        c = next(r for r in out if r["scale"] == "clip224" and r["feature"] == f)
        print(f"{f:26s} {n['abs_dz']:12.3f} {c['abs_dz']:10.3f} "
              f"{c['fraction_of_native_dz']:7} {n['p_sign_flip']:10.5f} {c['p_sign_flip']:10.5f}")


if __name__ == "__main__":
    main()
