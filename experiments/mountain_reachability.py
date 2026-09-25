# -*- coding: utf-8 -*-
"""
experiments/mountain_reachability.py
====================================
Tests whether an edit re-routes into the existing mountain or creates new artefacts.
Frozen in docs/prereg_mountain_reachability.md (2026-09-24).

Contract:
  python experiments/mountain_reachability.py --inventory      # only §3, prints and stops
  python experiments/mountain_reachability.py                  # the full run
  python experiments/mountain_reachability.py --space palette  # the declared replication
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import os
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

ROOTS = [
    Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"),
    Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output"),
    Path(r"c:\Users\aless\Desktop\comfyui-pilot"),
]

MANIFESTS_BENCH_MAP = {
    "stage2_images.csv": "benchmark_stage2_family",
    "stage4_images.csv": "benchmark_stage4_preset",
    "stage5_images.csv": "benchmark_stage5",
    "stage6_images.csv": "benchmark_stage6",
    "stage6b_pilot_images.csv": "archive_stage7_s7_old",
    "stage7a_images.csv": "benchmark_stage7a",
    "stage7b_images.csv": "benchmark_stage7",
    "stage9_images.csv": "benchmark_stage9",
}

STAGE9_ARMS = [
    "preset_pos_1x", "preset_pos_2x",
    "blockshuf_neg_1x", "blockshuf_neg_2x",
    "rand_pos_1x", "rand_pos_2x"
]
TESTED_ARMS = ["preset_pos_1x", "preset_pos_2x", "blockshuf_neg_1x", "rand_pos_1x"]

STYLE_PROMPTS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]

NOT_FEATURES = {
    "file", "width_px", "height_px", "condition", "prompt_dir", "prompt_id",
    "prompt_sha1", "seed", "rel_path", "source_manifest", "source_csv",
    "paper_hex", "ink_hex", "sw1_hex", "sw2_hex", "sw3_hex", "sw4_hex", "sw5_hex", "sw6_hex"
}


def find_on_disk(rel_path: str, bench_folder: str) -> Path | None:
    fn = os.path.basename(rel_path.replace("\\", "/"))
    for r in ROOTS:
        # direct
        c1 = r / rel_path
        if c1.is_file():
            return c1
        # via bench folder
        c2 = r / bench_folder / rel_path
        if c2.is_file():
            return c2
        # in renders/ subfolder
        c3 = r / bench_folder / "renders" / fn
        if c3.is_file():
            return c3
        # recursive search in bench folder
        bf = r / bench_folder
        if bf.is_dir():
            matches = list(bf.glob(f"**/{fn}"))
            if matches:
                return matches[0]
    return None


def sign_flip(diffs: list[float]) -> tuple[float, float]:
    """Exact two-tailed sign-flip p on paired differences, and its floor."""
    n = len(diffs)
    if n > 20:
        raise SystemExit(f"{n} pairs is too many to enumerate exactly")
    obs = abs(statistics.fmean(diffs))
    hits = sum(1 for s in itertools.product((1, -1), repeat=n)
               if abs(statistics.fmean(a * d for a, d in zip(s, diffs))) >= obs - 1e-12)
    return hits / (2 ** n), 2 / (2 ** n)


def holm(ps: list[float]) -> list[float]:
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out = [0.0] * len(ps)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, ps[i] * (len(ps) - rank)))
        out[i] = running
    return out


def euclidean_dist(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def main() -> None:
    ap = argparse.ArgumentParser(description="Mountain reachability analysis.")
    ap.add_argument("--inventory", action="store_true",
                    help="Run only the §3 inventory step, print and stop")
    ap.add_argument("--space", choices=["style", "palette"], default="style",
                    help="Feature space: 'style' (primary 23 features) or 'palette' (secondary replication)")
    ap.add_argument("--out", default=str(DATA / "mountain_reachability.csv"))
    ap.add_argument("--out-by-prompt", default=str(DATA / "mountain_reachability_by_prompt.csv"))
    ap.add_argument("--out-tests", default=str(DATA / "mountain_reachability_tests.csv"))
    args = ap.parse_args()

    # Load HUD contaminated list
    hud_files: set[str] = set()
    hud_csv = DATA / "hud_contaminated_images.csv"
    if hud_csv.exists():
        with hud_csv.open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                hud_files.add(os.path.basename(r.get("file", "") or r.get("image_path", "")))

    # Scan candidate manifests
    candidates = list(MANIFESTS_BENCH_MAP.keys())
    raw_baselines: dict[tuple[str, int], dict] = {}
    skipped_manifest_rows = {
        "not_baseline": 0,
        "wrong_resolution": 0,
        "hud_contaminated": 0,
        "not_on_disk": 0,
    }
    missing_files: list[str] = []

    for m_name in candidates:
        p = DATA / m_name
        if not p.exists():
            continue
        with p.open(encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        bench_folder = MANIFESTS_BENCH_MAP.get(m_name, "")
        cond_col = "condition" if "condition" in rows[0] else (
            "cond_name" if "cond_name" in rows[0] else (
                "operation" if "operation" in rows[0] else None
            )
        )
        for r in rows:
            is_base = (cond_col and r.get(cond_col) == "baseline") or (r.get("operation") == "baseline")
            if not is_base:
                skipped_manifest_rows["not_baseline"] += 1
                continue
            w = r.get("width") or r.get("width_px")
            h = r.get("height") or r.get("height_px")
            if f"{w}x{h}" != "1024x1280":
                skipped_manifest_rows["wrong_resolution"] += 1
                continue
            img_rel = r.get("image_path") or r.get("rel_path") or ""
            fn = os.path.basename(img_rel)
            if fn in hud_files:
                skipped_manifest_rows["hud_contaminated"] += 1
                continue

            disk_path = find_on_disk(img_rel, bench_folder)
            if disk_path is None:
                skipped_manifest_rows["not_on_disk"] += 1
                missing_files.append(fn)
                continue

            raw_prompt = r.get("prompt_id") or r.get("prompt_dir") or ""
            # Canonicalise prompt: e.g. S1_photo -> S1 if in style prompts
            prompt = raw_prompt.split("_")[0] if raw_prompt.startswith("S") and "_" in raw_prompt and raw_prompt.split("_")[0] in STYLE_PROMPTS else raw_prompt
            seed = int(r.get("seed", 0))

            key = (prompt, seed)
            if key not in raw_baselines:
                raw_baselines[key] = {
                    "prompt": prompt,
                    "seed": seed,
                    "file": fn,
                    "disk_path": disk_path,
                    "manifest": m_name,
                }

    # Include benchmark_pavimento_rumore if available
    for root in ROOTS:
        p_bench = root / "benchmark_pavimento_rumore"
        if p_bench.is_dir():
            for png in p_bench.glob("**/*.png"):
                fn = png.name
                if "baseline" in fn:
                    # e.g. S1_baseline_seed101_00001_.png
                    parts = fn.split("_")
                    prompt = parts[0]
                    seed_part = [x for x in parts if x.startswith("seed")]
                    if seed_part:
                        seed = int(seed_part[0].replace("seed", ""))
                        key = (prompt, seed)
                        if key not in raw_baselines and fn not in hud_files:
                            raw_baselines[key] = {
                                "prompt": prompt,
                                "seed": seed,
                                "file": fn,
                                "disk_path": png,
                                "manifest": "benchmark_pavimento_rumore",
                            }

    # Filter prompts with fewer than 3 seeds
    prompt_seed_counts: dict[str, set[int]] = {}
    for (p, s) in raw_baselines:
        prompt_seed_counts.setdefault(p, set()).add(s)

    base_cloud_keys = {
        (p, s) for (p, s) in raw_baselines
        if len(prompt_seed_counts[p]) >= 3
    }
    dropped_for_seed_count = {
        p: len(seeds) for p, seeds in prompt_seed_counts.items()
        if len(seeds) < 3
    }

    base_cloud = [raw_baselines[k] for k in sorted(base_cloud_keys)]
    distinct_prompts_b = sorted({b["prompt"] for b in base_cloud})
    n_prompts_b = len(distinct_prompts_b)
    n_renders_b = len(base_cloud)

    # Load / Extract Features for B
    cache_path = DATA / f"mountain_base_features_{args.space}.csv"
    existing_feat_cache: dict[str, list[float]] = {}
    feats_list: list[str] = []

    if args.space == "style":
        # Load from existing style_features CSVs
        source_csvs = [
            cache_path,
            DATA / "style_features.csv",
            DATA / "style_features_stage7.csv",
            DATA / "style_features_stage9.csv",
        ]
        for sc in source_csvs:
            if sc.exists():
                with sc.open(encoding="utf-8-sig") as fh:
                    r = csv.DictReader(fh)
                    f_cols = [c for c in r.fieldnames if c not in NOT_FEATURES]
                    if not feats_list:
                        feats_list = f_cols
                    for row in r:
                        fn = row.get("file") or os.path.basename(row.get("rel_path", "") or row.get("image_path", ""))
                        if fn and fn not in existing_feat_cache:
                            try:
                                existing_feat_cache[fn] = [float(row[c]) for c in feats_list]
                            except (ValueError, TypeError):
                                pass

        # Extract features for missing baselines
        missing_to_extract = [b for b in base_cloud if b["file"] not in existing_feat_cache]
        if missing_to_extract:
            print(f"Extracting style features for {len(missing_to_extract)} baseline renders...")
            sys.path.insert(0, str(ROOT / "experiments"))
            from style_features import extract_all_features
            for b in missing_to_extract:
                feats_dict = extract_all_features(str(b["disk_path"]))
                vec = [float(feats_dict[c]) for c in feats_list]
                existing_feat_cache[b["file"]] = vec

            # Save updated cache
            cache_rows = []
            for b in base_cloud:
                fn = b["file"]
                row_dict = {"file": fn, "prompt_id": b["prompt"], "seed": b["seed"]}
                for i, col in enumerate(feats_list):
                    row_dict[col] = existing_feat_cache[fn][i]
                cache_rows.append(row_dict)
            with cache_path.open("w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=["file", "prompt_id", "seed"] + feats_list)
                w.writeheader()
                w.writerows(cache_rows)
            print(f"Cached baseline features to {cache_path}")

    else: # palette
        source_csvs = [
            cache_path,
            DATA / "palette_features_all.csv",
            DATA / "palette_features_stage9.csv",
            DATA / "palette_features_stage7.csv",
        ]
        for sc in source_csvs:
            if sc.exists():
                with sc.open(encoding="utf-8-sig") as fh:
                    r = csv.DictReader(fh)
                    f_cols = [c for c in r.fieldnames if c not in NOT_FEATURES and not c.endswith("_hex")]
                    if not feats_list:
                        feats_list = f_cols
                    for row in r:
                        fn = row.get("file") or os.path.basename(row.get("rel_path", "") or row.get("image_path", ""))
                        if fn and fn not in existing_feat_cache:
                            try:
                                existing_feat_cache[fn] = [float(row[c]) for c in feats_list]
                            except (ValueError, TypeError):
                                pass

        missing_to_extract = [b for b in base_cloud if b["file"] not in existing_feat_cache]
        if missing_to_extract:
            sys.exit(f"Palette space: {len(missing_to_extract)} baseline renders missing from palette features CSVs")

    # Standardise on B once
    n_feats = len(feats_list)
    b_vectors = [existing_feat_cache[b["file"]] for b in base_cloud]
    mu_B = [statistics.fmean(v[i] for v in b_vectors) for i in range(n_feats)]
    sd_B = [statistics.stdev(v[i] for v in b_vectors) for i in range(n_feats)]
    for i, s in enumerate(sd_B):
        if s == 0:
            sys.exit(f"Feature {feats_list[i]} has zero standard deviation across base cloud B")

    def z_B(vec: list[float]) -> list[float]:
        return [(vec[i] - mu_B[i]) / sd_B[i] for i in range(n_feats)]

    for b in base_cloud:
        b["z"] = z_B(existing_feat_cache[b["file"]])

    # Compute d_out and d_in for all baselines in B
    b_d_out_list: list[float] = []
    for b in base_cloud:
        d_out = min(
            euclidean_dist(b["z"], b_other["z"])
            for b_other in base_cloud
            if b_other["prompt"] != b["prompt"]
        )
        d_in = min(
            euclidean_dist(b["z"], b_other["z"])
            for b_other in base_cloud
            if b_other["file"] != b["file"]
        )
        b["d_out"] = d_out
        b["d_in"] = d_in
        b_d_out_list.append(d_out)

    median_d_out_b = statistics.median(b_d_out_list)

    # ------------------------------------------------------------------
    # INVENTORY REPORT & STOP
    # ------------------------------------------------------------------
    print(f"=== Mountain Reachability Inventory ({args.space.upper()} space) ===")
    print(f"Distinct prompts in B : {n_prompts_b}")
    print(f"Total baseline renders: {n_renders_b}")
    print(f"Skipped manifest rows : {skipped_manifest_rows}")
    if dropped_for_seed_count:
        print(f"Prompts dropped (< 3 seeds): {dropped_for_seed_count}")
    print(f"Median d_out among baselines in B: {median_d_out_b:.6f}")

    if n_prompts_b < 12:
        print(f"\n[POWER GATE FAILED] B holds {n_prompts_b} prompts (< 12). Analysis is declared UNDERPOWERED.")
    else:
        print(f"\n[POWER GATE PASSED] B holds {n_prompts_b} prompts (>= 12). Sufficient power for statistical testing.")

    if args.inventory:
        sys.exit(0)

    # If full run, check power gate
    if n_prompts_b < 12:
        sys.exit("Underpowered run (< 12 distinct prompts). Stopping per prereg §3.")

    # ------------------------------------------------------------------
    # FULL RUN: Load Stage 9 Edited Renders
    # ------------------------------------------------------------------
    s9_feat_path = DATA / f"{'style' if args.space == 'style' else 'palette'}_features_stage9.csv"
    if not s9_feat_path.exists():
        sys.exit(f"Stage 9 features file missing: {s9_feat_path}")

    with s9_feat_path.open(encoding="utf-8-sig") as fh:
        s9_rows = list(csv.DictReader(fh))

    # Base cloud map for fast lookup: (prompt, seed) -> b
    b_map = {(b["prompt"], b["seed"]): b for b in base_cloud}

    # Edited rows for the 8 style prompts and 6 arms
    reachability_rows = []
    # R1 baseline reference band: 5th and 95th percentiles of baselines' own d_out
    b_p05 = float(statistics.quantiles(b_d_out_list, n=100)[4])
    b_p95 = float(statistics.quantiles(b_d_out_list, n=100)[94])

    for r in s9_rows:
        arm = r.get("condition") or r.get("arm")
        if arm not in STAGE9_ARMS:
            continue
        raw_p = r.get("prompt_dir") or r.get("prompt_id")
        p = raw_p.split("_")[0]
        if p not in STYLE_PROMPTS:
            continue
        seed = int(r["seed"])

        base_pair = b_map.get((p, seed))
        if not base_pair:
            continue

        raw_vec = [float(r[col]) for col in feats_list]
        z_edit = z_B(raw_vec)
        z_base = base_pair["z"]

        # d_out and d_in for edited
        best_d_out = float("inf")
        nearest_prompt_edited = ""
        for b_cand in base_cloud:
            if b_cand["prompt"] != p:
                d = euclidean_dist(z_edit, b_cand["z"])
                if d < best_d_out:
                    best_d_out = d
                    nearest_prompt_edited = b_cand["prompt"]

        best_d_in = min(euclidean_dist(z_edit, b_cand["z"]) for b_cand in base_cloud)

        # Baseline distances
        d_out_base = base_pair["d_out"]
        d_in_base = base_pair["d_in"]
        delta = best_d_out - d_out_base
        delta_norm = euclidean_dist(z_edit, z_base)

        # nearest prompt for baseline
        nearest_prompt_baseline = ""
        best_d_out_b = float("inf")
        for b_cand in base_cloud:
            if b_cand["prompt"] != p:
                d = euclidean_dist(z_base, b_cand["z"])
                if d < best_d_out_b:
                    best_d_out_b = d
                    nearest_prompt_baseline = b_cand["prompt"]

        reachability_rows.append({
            "arm": arm,
            "prompt": p,
            "seed": seed,
            "d_out_edited": round(best_d_out, 6),
            "d_out_baseline": round(d_out_base, 6),
            "delta": round(delta, 6),
            "d_in_edited": round(best_d_in, 6),
            "d_in_baseline": round(d_in_base, 6),
            "nearest_prompt_edited": nearest_prompt_edited,
            "nearest_prompt_baseline": nearest_prompt_baseline,
            "delta_norm": round(delta_norm, 6),
            "space": args.space,
        })

    # Write data/mountain_reachability.csv
    out_csv = Path(args.out)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(reachability_rows[0].keys()))
        w.writeheader()
        w.writerows(reachability_rows)
    print(f"wrote {out_csv} ({len(reachability_rows)} rows)")

    # Aggregate by prompt (unit of analysis)
    by_prompt_rows = []
    for arm in STAGE9_ARMS:
        arm_rows = [r for r in reachability_rows if r["arm"] == arm]
        for p in STYLE_PROMPTS:
            p_rows = [r for r in arm_rows if r["prompt"] == p]
            if not p_rows:
                continue
            mean_delta = statistics.fmean(r["delta"] for r in p_rows)
            mean_d_out_edit = statistics.fmean(r["d_out_edited"] for r in p_rows)
            mean_d_out_base = statistics.fmean(r["d_out_baseline"] for r in p_rows)
            mean_d_norm = statistics.fmean(r["delta_norm"] for r in p_rows)
            by_prompt_rows.append({
                "arm": arm,
                "prompt": p,
                "n_seeds": len(p_rows),
                "mean_delta": round(mean_delta, 6),
                "mean_d_out_edited": round(mean_d_out_edit, 6),
                "mean_d_out_baseline": round(mean_d_out_base, 6),
                "mean_delta_norm": round(mean_d_norm, 6),
                "space": args.space,
            })

    out_bp = Path(args.out_by_prompt)
    with out_bp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(by_prompt_rows[0].keys()))
        w.writeheader()
        w.writerows(by_prompt_rows)
    print(f"wrote {out_bp} ({len(by_prompt_rows)} rows)")

    # Hypothesis testing on 4 pre-registered arms (TESTED_ARMS)
    raw_p_values = []
    arm_stats = []
    for arm in TESTED_ARMS:
        sub = [r for r in by_prompt_rows if r["arm"] == arm]
        deltas = [r["mean_delta"] for r in sub]
        mean_d = statistics.fmean(deltas)
        n_neg = sum(1 for d in deltas if d < 0)
        p_val, p_fl = sign_flip(deltas)
        raw_p_values.append(p_val)

        # R1 evaluation: fraction of edited renders above 95th percentile band
        arm_cells = [r for r in reachability_rows if r["arm"] == arm]
        frac_above_p95 = sum(1 for r in arm_cells if r["d_out_edited"] > b_p95) / len(arm_cells)
        r1_status = "R1 fails" if frac_above_p95 > 0.25 else "R1 holds"

        arm_stats.append({
            "arm": arm,
            "mean_delta": mean_d,
            "prompts_negative": f"{n_neg}/{len(deltas)}",
            "p_sign_flip": p_val,
            "p_floor": p_fl,
            "frac_above_p95": frac_above_p95,
            "r1_status": r1_status,
        })

    holm_ps = holm(raw_p_values)

    test_rows = []
    for i, ast in enumerate(arm_stats):
        p_h = holm_ps[i]
        m_d = ast["mean_delta"]
        n_neg_count = int(ast["prompts_negative"].split("/")[0])

        # Verbatim criteria from §4
        if m_d < 0 and p_h <= 0.05 and n_neg_count >= 6:
            r2_verdict = "R2 confirmed"
        elif m_d > 0 and p_h <= 0.05:
            r2_verdict = "R2 refuted"
        else:
            r2_verdict = "R2 ambiguous"

        test_rows.append({
            "arm": ast["arm"],
            "space": args.space,
            "mean_delta": round(m_d, 6),
            "prompts_negative": ast["prompts_negative"],
            "p_sign_flip": round(ast["p_sign_flip"], 6),
            "p_floor": round(ast["p_floor"], 6),
            "p_holm": round(p_h, 6),
            "verdict_r2": r2_verdict,
            "verdict_r1": ast["r1_status"],
            "frac_above_p95_band": round(ast["frac_above_p95"], 4),
        })

    out_tests = Path(args.out_tests)
    with out_tests.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(test_rows[0].keys()))
        w.writeheader()
        w.writerows(test_rows)
    print(f"wrote {out_tests} ({len(test_rows)} rows)")


if __name__ == "__main__":
    main()
