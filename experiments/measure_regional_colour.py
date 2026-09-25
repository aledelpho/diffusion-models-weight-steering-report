# -*- coding: utf-8 -*-
"""
experiments/measure_regional_colour.py
======================================
Extracts regional CIELAB colour features per docs/prereg_colour_identifiability.md §3.

For each (corpus, prompt, seed) group:
  1. Cut points are taken from the baseline image's L* terciles (3 bands) and
     quintiles (5 bands sensitivity).
  2. Cut points are applied unchanged to both baseline and edited images.
  3. Per band: mean L*, mean a*, mean b*, and pixel fraction.
     - 3 bands x 4 = 12 features (primary)
     - 5 bands x 4 = 20 features (sensitivity)

Writes: data/colour_features_regional.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image
from skimage.color import rgb2lab

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

ROOTS = [
    Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"),
    Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output"),
    Path(r"c:\Users\aless\Desktop\comfyui-pilot"),
]

STAGE7_TEST_PROMPTS = [
    "I01", "I02", "I05", "I06", "I07", "I09", "I10", "I11",
    "I12", "I16", "I17", "I18", "I20", "I21", "I23", "I24"
]
STAGE7_ARMS = [
    "baseline",
    "preset_pos", "preset_neg",
    "blockshuf_pos", "blockshuf_neg",
    "rand_pos", "rand_neg"
]

STAGE9_STYLE_PROMPTS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
STAGE9_ARMS = [
    "baseline",
    "preset_pos_1x", "preset_pos_2x",
    "blockshuf_neg_1x", "blockshuf_neg_2x",
    "rand_pos_1x", "rand_pos_2x"
]

SEEDS_5 = [42, 777, 1337, 9999, 4242145]


def find_on_disk(rel_path: str, bench_folder: str = "benchmark_stage7") -> Path | None:
    fn = os.path.basename(rel_path.replace("\\", "/"))
    bench_candidates = [bench_folder, "benchmark_stage7a", "benchmark_stage7", "benchmark_stage9"]
    for r in ROOTS:
        c1 = r / rel_path
        if c1.is_file():
            return c1
        for bf in bench_candidates:
            c2 = r / bf / rel_path
            if c2.is_file():
                return c2
            c3 = r / bf / "renders" / fn
            if c3.is_file():
                return c3
            d = r / bf
            if d.is_dir():
                matches = list(d.glob(f"**/{fn}"))
                if matches:
                    return matches[0]
    return None


def extract_lab_arrays(im_path: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Loads image and converts to flat L*, a*, b* arrays in float32."""
    im = Image.open(im_path).convert("RGB")
    arr = np.array(im, dtype=np.float32) / 255.0
    lab = rgb2lab(arr)
    return lab[:, :, 0].flatten(), lab[:, :, 1].flatten(), lab[:, :, 2].flatten()


def compute_band_features(
    L: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
    cuts: List[float],
    n_bands: int
) -> Dict[str, float]:
    """Assigns pixels to luminance bands using fixed cut points and returns 4 metrics per band."""
    band_idx = np.zeros(len(L), dtype=np.int32)
    for c in cuts:
        band_idx += (L >= c).astype(np.int32)

    feats: Dict[str, float] = {}
    tot_pixels = len(L)

    for k in range(n_bands):
        mask = (band_idx == k)
        cnt = int(np.sum(mask))
        frac = cnt / tot_pixels if tot_pixels else 0.0
        if cnt > 0:
            mL = float(np.mean(L[mask]))
            ma = float(np.mean(a[mask]))
            mb = float(np.mean(b[mask]))
        else:
            mL = 0.0
            ma = 0.0
            mb = 0.0

        prefix = f"band{n_bands}_b{k}"
        feats[f"{prefix}_mean_L"] = round(mL, 6)
        feats[f"{prefix}_mean_a"] = round(ma, 6)
        feats[f"{prefix}_mean_b"] = round(mb, 6)
        feats[f"{prefix}_frac"] = round(frac, 6)

    return feats


def collect_manifest_renders() -> List[Dict[str, Any]]:
    """Gathers all target renders for Stage 7 and Stage 9 with verified disk paths."""
    all_renders: List[Dict[str, Any]] = []

    # 1. Stage 7
    s7_csv = DATA / "style_features_stage7.csv"
    with s7_csv.open(encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            arm = r.get("condition") or r.get("arm")
            p = r.get("prompt_dir") or r.get("prompt_id")
            seed = int(r["seed"])
            if p not in STAGE7_TEST_PROMPTS or arm not in STAGE7_ARMS or seed not in SEEDS_5:
                continue
            fn = r["file"]
            bench = "benchmark_stage7a" if arm == "baseline" else "benchmark_stage7"
            p_disk = find_on_disk(r.get("rel_path") or fn, bench)
            if not p_disk:
                p_disk = find_on_disk(fn, bench)
            if not p_disk:
                sys.exit(f"Missing stage 7 render on disk: {fn}")
            all_renders.append({
                "corpus": "stage7",
                "arm": arm,
                "prompt": p,
                "seed": seed,
                "file": fn,
                "disk_path": p_disk,
            })

    # 2. Stage 9
    s9_csv = DATA / "stage9_images.csv"
    with s9_csv.open(encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            arm = r.get("cond_name") or r.get("arm")
            raw_p = r.get("prompt_id") or ""
            p = raw_p.split("_")[0]
            seed = int(r["seed"])
            if p not in STAGE9_STYLE_PROMPTS or arm not in STAGE9_ARMS or seed not in SEEDS_5:
                continue
            rel = r.get("image_path") or ""
            fn = os.path.basename(rel)
            p_disk = find_on_disk(rel, "benchmark_stage9")
            if not p_disk:
                sys.exit(f"Missing stage 9 render on disk: {fn}")
            all_renders.append({
                "corpus": "stage9",
                "arm": arm,
                "prompt": p,
                "seed": seed,
                "file": fn,
                "disk_path": p_disk,
            })

    return all_renders


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract regional colour features per §3.")
    ap.add_argument("--out", default=str(DATA / "colour_features_regional.csv"),
                    help="Target path for regional colour features CSV")
    args = ap.parse_args()

    print("=== EXTRACTING REGIONAL COLOUR FEATURES (§3) ===")
    renders = collect_manifest_renders()
    print(f"Total target renders: {len(renders)} (Stage 7 + Stage 9)")

    # Group renders by (corpus, prompt, seed)
    grouped: Dict[Tuple[str, str, int], List[Dict[str, Any]]] = {}
    for r in renders:
        grouped.setdefault((r["corpus"], r["prompt"], r["seed"]), []).append(r)

    print(f"Total (corpus, prompt, seed) groups: {len(grouped)}")

    output_rows: List[Dict[str, Any]] = []
    processed_count = 0
    total_renders = len(renders)

    for (corpus, p, s), group_renders in sorted(grouped.items()):
        # Locate baseline
        base_match = [r for r in group_renders if r["arm"] == "baseline"]
        if not base_match:
            sys.exit(f"FATAL: Missing baseline for ({corpus}, {p}, {s})")
        base_item = base_match[0]

        # Extract baseline L* and compute terciles (3 bands) and quintiles (5 bands)
        L_base, a_base, b_base = extract_lab_arrays(base_item["disk_path"])

        # 3 bands: 2 cuts at 33.33% and 66.67%
        cuts_3 = [
            float(np.percentile(L_base, 100.0 / 3.0)),
            float(np.percentile(L_base, 200.0 / 3.0))
        ]

        # 5 bands: 4 cuts at 20%, 40%, 60%, 80%
        cuts_5 = [
            float(np.percentile(L_base, 20.0)),
            float(np.percentile(L_base, 40.0)),
            float(np.percentile(L_base, 60.0)),
            float(np.percentile(L_base, 80.0))
        ]

        # Process all renders in this group (including baseline itself)
        for r_item in group_renders:
            if r_item["arm"] == "baseline":
                L_r, a_r, b_r = L_base, a_base, b_base
            else:
                L_r, a_r, b_r = extract_lab_arrays(r_item["disk_path"])

            row_dict = {
                "file": r_item["file"],
                "corpus": corpus,
                "arm": r_item["arm"],
                "prompt": p,
                "seed": s,
            }

            # 3-band primary features (12)
            f3 = compute_band_features(L_r, a_r, b_r, cuts_3, n_bands=3)
            row_dict.update(f3)

            # 5-band sensitivity features (20)
            f5 = compute_band_features(L_r, a_r, b_r, cuts_5, n_bands=5)
            row_dict.update(f5)

            output_rows.append(row_dict)
            processed_count += 1

            if processed_count % 100 == 0:
                print(f"  [{processed_count}/{total_renders}] renders processed...")

    # Write output CSV
    out_csv = Path(args.out)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(output_rows[0].keys())

    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(output_rows)

    print(f"\nwrote {out_csv} ({len(output_rows)} rows: 560 stage7, 280 stage9)")


if __name__ == "__main__":
    main()
