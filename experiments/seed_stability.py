# -*- coding: utf-8 -*-
"""
experiments/seed_stability.py
=============================
Evaluates whether model steering alters seed-to-seed dispersion (wobble).
Frozen in docs/prereg_seed_stability.md and docs/RUNBOOK_2026-09-25b.md.

Inputs:
  - data/style_features_stage7.csv (Primary confirmatory corpus, 23 style features)
  - data/style_features_stage9.csv (Exploratory corpus, quarantined)
  - data/palette_instrument_check_stage7.csv (Stage 7 instrument gate)
  - data/palette_swatches.json (Stage 9 palette data for exploratory)

Outputs:
  - data/seed_stability.csv (V and R per condition, prompt, and space)
  - data/seed_stability_tests.csv (Hypothesis tests, Holm correction, fragility checks, verdicts)
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

STYLE_23 = [
    "stroke_width_median_px", "stroke_width_std_px", "stroke_width_cv",
    "edge_density", "contour_mean_length_px", "contour_n_components",
    "crosshatch_entropy_mean", "crosshatch_entropy_p90",
    "color_top4_cluster_share", "color_cluster_entropy_norm",
    "color_n_effective", "colorfulness_hs", "luminance_hist_n_peaks",
    "shadow_edge_transition_width_px", "shadow_edge_transition_width_std",
    "glcm_contrast", "glcm_homogeneity", "glcm_energy", "glcm_correlation",
    "lbp_entropy", "lbp_uniform_share", "fft_radial_slope", "fft_high_freq_share"
]

SEEDS_5 = [42, 777, 1337, 9999, 4242145]

STAGE7_ARMS = [
    "preset_pos", "preset_neg",
    "blockshuf_pos", "blockshuf_neg",
    "rand_pos", "rand_neg"
]

STAGE9_STYLE_PROMPTS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
STAGE9_ARMS = [
    "preset_pos_1x", "preset_pos_2x",
    "blockshuf_neg_1x", "blockshuf_neg_2x",
    "rand_pos_1x", "rand_pos_2x"
]


def euc_dist(v1: List[float], v2: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(v1, v2)))


def sign_flip(diffs: List[float]) -> Tuple[float, float]:
    """Exact two-tailed sign-flip permutation p-value and floor."""
    n = len(diffs)
    if n > 20:
        raise SystemExit(f"{n} pairs is too many to enumerate exactly")
    obs = abs(statistics.fmean(diffs))
    hits = sum(
        1 for s in itertools.product((1, -1), repeat=n)
        if abs(statistics.fmean(a * d for a, d in zip(s, diffs))) >= obs - 1e-12
    )
    return hits / 2 ** n, 2 / 2 ** n


def holm(ps: List[float]) -> List[float]:
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out = [0.0] * len(ps)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, ps[i] * (len(ps) - rank)))
        out[i] = running
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate seed stability across model steering.")
    ap.add_argument("--out-stab", default=str(DATA / "seed_stability.csv"),
                    help="Target path for stability measurements CSV")
    ap.add_argument("--out-tests", default=str(DATA / "seed_stability_tests.csv"),
                    help="Target path for stability tests CSV")
    args = ap.parse_args()

    # =========================================================================
    # 1. PRIMARY CONFIRMATORY: STAGE 7 STYLE SPACE (23 features)
    # =========================================================================
    stage7_csv = DATA / "style_features_stage7.csv"
    if not stage7_csv.exists():
        sys.exit(f"style_features_stage7.csv missing: {stage7_csv}")
    with stage7_csv.open(encoding="utf-8-sig") as fh:
        s7_rows = list(csv.DictReader(fh))

    # Standardisation: computed once over Stage 7 baselines (120 renders)
    baselines_s7 = [r for r in s7_rows if r["condition"] == "baseline"]
    if len(baselines_s7) != 120:
        sys.exit(f"Expected 120 Stage 7 baselines, found {len(baselines_s7)}")

    mu_s7 = [statistics.fmean(float(r[col]) for r in baselines_s7) for col in STYLE_23]
    sd_s7 = [statistics.stdev(float(r[col]) for r in baselines_s7) for col in STYLE_23]

    for idx, s in enumerate(sd_s7):
        if s == 0:
            sys.exit(f"Feature {STYLE_23[idx]} has 0 variance across Stage 7 baselines")

    def z_s7(r: dict) -> List[float]:
        return [(float(r[col]) - mu_s7[i]) / sd_s7[i] for i, col in enumerate(STYLE_23)]

    cells_s7: Dict[Tuple[str, str, int], List[float]] = {}
    for r in s7_rows:
        c = r["condition"]
        p = r["prompt_dir"]
        s = int(r["seed"])
        cells_s7[(c, p, s)] = z_s7(r)

    prompts_base_s7 = sorted(set(r["prompt_dir"] for r in baselines_s7))  # 24 prompts
    prompts_arms_s7 = sorted(set(r["prompt_dir"] for r in s7_rows if r["condition"] == "preset_pos"))  # 16 prompts

    # Compute V(c, P) for Stage 7
    V_s7: Dict[Tuple[str, str], float] = {}
    all_conds_s7 = ["baseline"] + STAGE7_ARMS
    for c in all_conds_s7:
        p_list = prompts_base_s7 if c == "baseline" else prompts_arms_s7
        for p in p_list:
            dists = [
                euc_dist(cells_s7[(c, p, s1)], cells_s7[(c, p, s2)])
                for s1, s2 in itertools.combinations(SEEDS_5, 2)
            ]
            V_s7[(c, p)] = statistics.fmean(dists)

    # Compute R(arm, P) = V(arm, P) - V(baseline, P)
    R_s7: Dict[str, Dict[str, float]] = {}
    for a in STAGE7_ARMS:
        R_s7[a] = {p: V_s7[(a, p)] - V_s7[("baseline", p)] for p in prompts_arms_s7}

    # =========================================================================
    # 2. EXPLORATORY: STAGE 9 STYLE SPACE (Quarantined)
    # =========================================================================
    stage9_csv = DATA / "style_features_stage9.csv"
    V_s9_style: Dict[Tuple[str, str], float] = {}
    R_s9_style: Dict[str, Dict[str, float]] = {}

    if stage9_csv.exists():
        with stage9_csv.open(encoding="utf-8-sig") as fh:
            s9_rows = list(csv.DictReader(fh))

        # Standardise on Stage 9 baselines
        baselines_s9 = [
            r for r in s9_rows
            if (r.get("cond_name") or r.get("arm") or r.get("condition")) == "baseline"
            and (r.get("prompt_id") or r.get("prompt") or r.get("prompt_dir")) in STAGE9_STYLE_PROMPTS
        ]
        if baselines_s9:
            mu_s9 = [statistics.fmean(float(r[col]) for r in baselines_s9) for col in STYLE_23]
            sd_s9 = [statistics.stdev(float(r[col]) for r in baselines_s9) for col in STYLE_23]

            def z_s9(r: dict) -> List[float]:
                return [(float(r[col]) - mu_s9[i]) / sd_s9[i] for i, col in enumerate(STYLE_23)]

            cells_s9: Dict[Tuple[str, str, int], List[float]] = {}
            for r in s9_rows:
                c = r.get("cond_name") or r.get("arm") or r.get("condition")
                p = r.get("prompt_id") or r.get("prompt") or r.get("prompt_dir")
                s = int(r["seed"])
                if p in STAGE9_STYLE_PROMPTS and c in (["baseline"] + STAGE9_ARMS):
                    cells_s9[(c, p, s)] = z_s9(r)

            for c in ["baseline"] + STAGE9_ARMS:
                for p in STAGE9_STYLE_PROMPTS:
                    if all((c, p, s) in cells_s9 for s in SEEDS_5):
                        dists = [
                            euc_dist(cells_s9[(c, p, s1)], cells_s9[(c, p, s2)])
                            for s1, s2 in itertools.combinations(SEEDS_5, 2)
                        ]
                        V_s9_style[(c, p)] = statistics.fmean(dists)

            for a in STAGE9_ARMS:
                R_s9_style[a] = {}
                for p in STAGE9_STYLE_PROMPTS:
                    if (a, p) in V_s9_style and ("baseline", p) in V_s9_style:
                        R_s9_style[a][p] = V_s9_style[(a, p)] - V_s9_style[("baseline", p)]

    # =========================================================================
    # 3. ASSEMBLE data/seed_stability.csv
    # =========================================================================
    stab_rows = []

    # Stage 7 Style rows (Primary)
    for c in all_conds_s7:
        p_list = prompts_base_s7 if c == "baseline" else prompts_arms_s7
        for p in p_list:
            v_val = V_s7[(c, p)]
            v_base = V_s7[("baseline", p)]
            r_val = v_val - v_base if c != "baseline" else 0.0
            ratio = v_val / v_base if v_base > 0 else 1.0
            stab_rows.append({
                "corpus": "stage7",
                "role": "primary_confirmatory",
                "space": "style_space_23d",
                "condition": c,
                "prompt": p,
                "n_seeds": len(SEEDS_5),
                "V_seed_dispersion": round(v_val, 6),
                "V_baseline": round(v_base, 6),
                "R_contrast": round(r_val, 6) if c != "baseline" else "",
                "ratio_vs_baseline": round(ratio, 4) if c != "baseline" else "1.0000",
                "interpretability": "interpretable",
            })

    # Stage 7 Palette rows (Secondary - Instrument Insufficient)
    for c in all_conds_s7:
        p_list = prompts_base_s7 if c == "baseline" else prompts_arms_s7
        for p in p_list:
            stab_rows.append({
                "corpus": "stage7",
                "role": "secondary",
                "space": "palette_ciede2000_n15",
                "condition": c,
                "prompt": p,
                "n_seeds": len(SEEDS_5),
                "V_seed_dispersion": "",
                "V_baseline": "",
                "R_contrast": "",
                "ratio_vs_baseline": "",
                "interpretability": "instrument_insufficient",
            })

    # Stage 9 Style rows (Exploratory in quarantine)
    for c in ["baseline"] + STAGE9_ARMS:
        for p in STAGE9_STYLE_PROMPTS:
            if (c, p) in V_s9_style:
                v_val = V_s9_style[(c, p)]
                v_base = V_s9_style[("baseline", p)]
                r_val = v_val - v_base if c != "baseline" else 0.0
                ratio = v_val / v_base if v_base > 0 else 1.0
                stab_rows.append({
                    "corpus": "stage9",
                    "role": "exploratory_hypothesis_generating",
                    "space": "style_space_23d",
                    "condition": c,
                    "prompt": p,
                    "n_seeds": len(SEEDS_5),
                    "V_seed_dispersion": round(v_val, 6),
                    "V_baseline": round(v_base, 6),
                    "R_contrast": round(r_val, 6) if c != "baseline" else "",
                    "ratio_vs_baseline": round(ratio, 4) if c != "baseline" else "1.0000",
                    "interpretability": "exploratory_quarantined",
                })

    out_stab_path = Path(args.out_stab)
    out_stab_path.parent.mkdir(parents=True, exist_ok=True)
    with out_stab_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(stab_rows[0].keys()))
        w.writeheader()
        w.writerows(stab_rows)
    print(f"wrote {out_stab_path} ({len(stab_rows)} rows)")

    # =========================================================================
    # 4. HYPOTHESIS TESTS AND VERDICTS: data/seed_stability_tests.csv
    # =========================================================================
    tests_rows = []

    # A. Stage 7 Style Space: Primary Contrasts R(arm, P) = V(arm) - V(base)
    raw_ps_s7 = []
    temp_s7_primary = []

    for a in STAGE7_ARMS:
        diffs = [R_s7[a][p] for p in prompts_arms_s7]
        mean_r = statistics.fmean(diffs)
        pos_p = sum(1 for d in diffs if d > 0)
        n_p = len(diffs)

        # Fragility check (§7 & G4): does any single prompt carry > 40% of the sum of absolute values?
        abs_diffs = [abs(d) for d in diffs]
        total_abs = sum(abs_diffs)
        max_share = max(abs_diffs) / total_abs if total_abs > 0 else 0.0
        is_fragile = max_share > 0.40

        pv, floor = sign_flip(diffs)
        raw_ps_s7.append(pv)

        temp_s7_primary.append({
            "corpus": "stage7",
            "role": "primary_confirmatory",
            "space": "style_space_23d",
            "contrast_type": "primary_arm_vs_baseline",
            "arm": a,
            "control": "baseline",
            "metric_tested": "seed_dispersion_difference_R",
            "n_prompts": n_p,
            "mean_R": round(mean_r, 4),
            "prompts_positive": pos_p,
            "max_single_prompt_share": round(max_share, 4),
            "is_fragile": is_fragile,
            "p_sign_flip": round(pv, 6),
            "p_floor": round(floor, 6),
        })

    holm_s7 = holm(raw_ps_s7)
    for t, h in zip(temp_s7_primary, holm_s7):
        t["p_holm"] = round(h, 6)
        if t["is_fragile"]:
            t["verdict"] = "fragile"
            t["details"] = (
                f"Single prompt carries {t['max_single_prompt_share']:.1%} of mean (exceeds 40% threshold); "
                f"result is fragile per §7, no claim promoted"
            )
        else:
            if h < 0.05:
                if t["mean_R"] > 0:
                    t["verdict"] = "injects_variability"
                    t["details"] = f"R significantly positive (mean {t['mean_R']:+.3f}, p_holm={h:.4f}); edit injects variability"
                else:
                    t["verdict"] = "stabilises_output"
                    t["details"] = f"R significantly negative (mean {t['mean_R']:+.3f}, p_holm={h:.4f}); edit stabilises output"
            else:
                t["verdict"] = "dispersion_unchanged"
                t["details"] = (
                    f"R not significant after Holm correction (mean {t['mean_R']:+.3f}, p_holm={h:.4f}); "
                    f"edit moves output without changing its spread"
                )
        tests_rows.append(t)

    # B. Stage 7 Style Space: Secondary Contrasts R(preset) - R(scramble)
    sec_contrasts_s7 = [
        ("preset_pos", "rand_pos"),
        ("preset_neg", "rand_neg"),
        ("blockshuf_pos", "rand_pos"),
        ("blockshuf_neg", "rand_neg"),
    ]
    raw_ps_s7_sec = []
    temp_s7_sec = []

    for a, ctrl in sec_contrasts_s7:
        diffs = [R_s7[a][p] - R_s7[ctrl][p] for p in prompts_arms_s7]
        mean_d = statistics.fmean(diffs)
        pos_p = sum(1 for d in diffs if d > 0)
        n_p = len(diffs)

        abs_diffs = [abs(d) for d in diffs]
        total_abs = sum(abs_diffs)
        max_share = max(abs_diffs) / total_abs if total_abs > 0 else 0.0
        is_fragile = max_share > 0.40

        pv, floor = sign_flip(diffs)
        raw_ps_s7_sec.append(pv)

        temp_s7_sec.append({
            "corpus": "stage7",
            "role": "secondary_prespecified",
            "space": "style_space_23d",
            "contrast_type": "structured_minus_scramble",
            "arm": a,
            "control": ctrl,
            "metric_tested": "delta_R_arm_minus_scramble",
            "n_prompts": n_p,
            "mean_R": round(mean_d, 4),
            "prompts_positive": pos_p,
            "max_single_prompt_share": round(max_share, 4),
            "is_fragile": is_fragile,
            "p_sign_flip": round(pv, 6),
            "p_floor": round(floor, 6),
        })

    holm_s7_sec = holm(raw_ps_s7_sec)
    for t, h in zip(temp_s7_sec, holm_s7_sec):
        t["p_holm"] = round(h, 6)
        if t["is_fragile"]:
            t["verdict"] = "fragile"
            t["details"] = f"Single prompt carries {t['max_single_prompt_share']:.1%} of contrast; fragile per §7"
        else:
            if h < 0.05:
                if t["mean_R"] > 0:
                    t["verdict"] = "structured_destabilises_more"
                    t["details"] = f"Structured edit destabilises significantly more than scramble (diff {t['mean_R']:+.3f}, p_holm={h:.4f})"
                else:
                    t["verdict"] = "structured_stabilises_more"
                    t["details"] = f"Structured edit stabilises significantly more than scramble (diff {t['mean_R']:+.3f}, p_holm={h:.4f})"
            else:
                t["verdict"] = "does_not_separate_from_scramble"
                t["details"] = f"Does not separate from scramble (diff {t['mean_R']:+.3f}, p_holm={h:.4f})"
        tests_rows.append(t)

    # C. Stage 7 Palette Space: Instrument Gate Record
    tests_rows.append({
        "corpus": "stage7",
        "role": "secondary",
        "space": "palette_ciede2000_n15",
        "contrast_type": "all_arms",
        "arm": "ALL_ARMS",
        "control": "baseline",
        "metric_tested": "D_pal_dispersion",
        "n_prompts": len(prompts_arms_s7),
        "mean_R": "",
        "prompts_positive": "",
        "max_single_prompt_share": "",
        "is_fragile": "",
        "p_sign_flip": "",
        "p_floor": "",
        "p_holm": "",
        "verdict": "instrument_insufficient",
        "details": "Hue +180 deg positive control (ratio 1.487x) did not clear p95 floor by 1.5x in G2; palette space is uninterpretable",
    })

    # D. Stage 9 Style Space: Quarantined Exploratory Rows (No p-value, no claim, no verdict)
    for a in STAGE9_ARMS:
        if a in R_s9_style and R_s9_style[a]:
            diffs = list(R_s9_style[a].values())
            mean_r = statistics.fmean(diffs)
            pos_p = sum(1 for d in diffs if d > 0)
            tests_rows.append({
                "corpus": "stage9",
                "role": "exploratory_hypothesis_generating",
                "space": "style_space_23d",
                "contrast_type": "exploratory_quarantined",
                "arm": a,
                "control": "baseline",
                "metric_tested": "seed_dispersion_difference_R",
                "n_prompts": len(diffs),
                "mean_R": round(mean_r, 4),
                "prompts_positive": pos_p,
                "max_single_prompt_share": "",
                "is_fragile": "",
                "p_sign_flip": "",
                "p_floor": "",
                "p_holm": "",
                "verdict": "exploratory_no_verdict",
                "details": "Quarantined exploratory data that generated the hypothesis (§2 & G5); no p-value and no claim",
            })

    out_tests_path = Path(args.out_tests)
    out_tests_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "corpus", "role", "space", "contrast_type", "arm", "control",
        "metric_tested", "n_prompts", "mean_R", "prompts_positive",
        "max_single_prompt_share", "is_fragile", "p_sign_flip",
        "p_floor", "p_holm", "verdict", "details"
    ]
    with out_tests_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(tests_rows)
    print(f"wrote {out_tests_path} ({len(tests_rows)} rows)")

    print("\n=== SUMMARY OF TESTS (STAGE 7 PRIMARY) ===")
    for t in tests_rows:
        if t["corpus"] == "stage7" and t["space"] == "style_space_23d":
            print(f"[{t['contrast_type']:28s}] {t['arm']:16s} vs {t['control']:10s} "
                  f"mean_R={str(t['mean_R']):>7s} ({t['prompts_positive']}/{t['n_prompts']} pos) "
                  f"pHolm={str(t['p_holm']):>7s} -> {t['verdict'].upper()}")


if __name__ == "__main__":
    main()
