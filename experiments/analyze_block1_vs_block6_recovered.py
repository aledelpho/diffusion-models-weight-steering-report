# DERIVED from analyze_block1_vs_block6.py on 2026-09-23 17:14; only path constants differ. Source sha256: 9a3a16beefd7004eb9465868040ca849508752d49e284d2b98be816336dfd4b8
# -*- coding: utf-8 -*-
"""
experiments/analyze_block1_vs_block6.py
======================================
Analisi statistica formale dell'esperimento pre-registrato:
Block_1 vs Block_6 con Frobenius Displacement appaiato (D = 0.04500)
e doppio controllo scramble (scramble_A vs scramble_B).

Implementa esattamente le specifiche congelate in docs/prereg_rotations_block1_vs_block6.md.
"""

import os
import sys
import csv
import math
import itertools
import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
PILOT_ROOT = os.path.abspath(os.path.join(_HERE, os.pardir))
REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"
DATA_DIR_REPORT = os.path.join(REPORT_ROOT, "data")
DATA_DIR_PILOT = os.path.join(PILOT_ROOT, "data")

STYLE_CSV = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_style_recovered_features.csv")
PALETTE_CSV = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_palette_recovered_features.csv")

RESULTS_CSV_REPORT = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_recovered_results.csv")
RESULTS_CSV_PILOT = os.path.join(DATA_DIR_PILOT, "rotations_block1_vs_block6_results.csv")

SCORES_CSV_REPORT = os.path.join(DATA_DIR_REPORT, "rotations_block1_vs_block6_recovered_prompt_scores.csv")
SCORES_CSV_PILOT = os.path.join(DATA_DIR_PILOT, "rotations_block1_vs_block6_prompt_scores.csv")

TEXTURE_COLS = ["glcm_contrast", "glcm_homogeneity", "lbp_entropy"]

LINEWORK_COLS = ["stroke_width_cv", "edge_density", "contour_mean_length_px"]
SHADOW_COLS = ["crosshatch_entropy_mean", "crosshatch_entropy_p90"]
FREQ_COLS = ["high_freq_ratio"]
PALETTE_COLS = ["paper_L", "ink_L", "sw1_L", "chroma_spread", "tonal_range"]


def cos_sim(u, v):
    nu = np.linalg.norm(u)
    nv = np.linalg.norm(v)
    if nu < 1e-12 or nv < 1e-12:
        return 0.0
    return float(np.dot(u, v) / (nu * nv))


def sign_flip_test(vals):
    v = np.asarray(vals, dtype=float)
    n = len(v)
    obs = float(np.mean(v))
    # 2^n combinazioni esatte
    signs = np.array(list(itertools.product([1, -1], repeat=n)))
    perm_means = (signs * v).mean(axis=1)
    p_val = float(np.mean(np.abs(perm_means) >= abs(obs) - 1e-12))
    floor = 2.0 / (2 ** n)
    return obs, p_val, floor, n


def run_analysis_for_space(st_df, pa_df, space_name, feature_cols):
    # Unione delle colonne necessarie
    combined_cols = {}
    for col in feature_cols:
        if col in st_df.columns:
            combined_cols[col] = st_df[col].astype(float)
        elif col in pa_df.columns:
            combined_cols[col] = pa_df[col].astype(float)
        else:
            raise KeyError(f"Feature '{col}' non trovata in style né in palette!")

    feat_df = pd.DataFrame(combined_cols)

    # 1. z-standardizzazione rispetto alla distribuzione congiunta dell'esperimento (210 immagini)
    feat_z = (feat_df - feat_df.mean(axis=0)) / (feat_df.std(axis=0, ddof=0).replace(0, np.nan))
    feat_z = feat_z.fillna(0.0)

    # Associa i metadati
    meta = st_df[["prompt_id", "seed", "condition", "angle"]].copy()
    z_df = pd.concat([meta, feat_z], axis=1)

    # 2. Calcolo dei delta rispetto al baseline dello STESSO prompt e STESSO seed
    prompts = sorted(z_df["prompt_id"].unique())
    seeds = sorted(z_df["seed"].unique())

    deltas = {}
    for p in prompts:
        for s in seeds:
            base_row = z_df[(z_df.prompt_id == p) & (z_df.seed == s) & (z_df.condition == "baseline")]
            if len(base_row) == 0:
                raise ValueError(f"Baseline mancante per prompt={p}, seed={s}")
            base_vec = base_row[feature_cols].values[0]

            for cond in ["Block_1_pos", "Block_1_neg", "Block_6_pos", "Block_6_neg", "scramble_A", "scramble_B"]:
                cond_row = z_df[(z_df.prompt_id == p) & (z_df.seed == s) & (z_df.condition == cond)]
                if len(cond_row) == 0:
                    raise ValueError(f"Condizione '{cond}' mancante per prompt={p}, seed={s}")
                cond_vec = cond_row[feature_cols].values[0]
                deltas[(p, s, cond)] = cond_vec - base_vec

    # 3. Componente antisimmetrica per ciascun blocco e media sui 3 seed
    # A_b(p) = 1/3 sum_{s=1}^3 (Delta(+theta) - Delta(-theta)) / 2
    A1 = {}
    A6 = {}
    S1 = {}
    S6 = {}
    A_scrA = {}
    A_scrB = {}

    for p in prompts:
        a1_seeds = []
        a6_seeds = []
        s1_seeds = []
        s6_seeds = []
        scra_seeds = []
        scrb_seeds = []

        for s in seeds:
            d1_p = deltas[(p, s, "Block_1_pos")]
            d1_n = deltas[(p, s, "Block_1_neg")]
            d6_p = deltas[(p, s, "Block_6_pos")]
            d6_n = deltas[(p, s, "Block_6_neg")]
            d_sa = deltas[(p, s, "scramble_A")]
            d_sb = deltas[(p, s, "scramble_B")]

            a1_seeds.append((d1_p - d1_n) / 2.0)
            s1_seeds.append((d1_p + d1_n) / 2.0)
            a6_seeds.append((d6_p - d6_n) / 2.0)
            s6_seeds.append((d6_p + d6_n) / 2.0)
            scra_seeds.append(d_sa)
            scrb_seeds.append(d_sb)

        A1[p] = np.mean(a1_seeds, axis=0)
        S1[p] = np.mean(s1_seeds, axis=0)
        A6[p] = np.mean(a6_seeds, axis=0)
        S6[p] = np.mean(s6_seeds, axis=0)
        A_scrA[p] = np.mean(scra_seeds, axis=0)
        A_scrB[p] = np.mean(scrb_seeds, axis=0)

    # 4. Leave-One-Out Cross-Prompt Statistica Primaria V(p)
    V_per_prompt = {}
    for p in prompts:
        other_prompts = [q for q in prompts if q != p]
        c1_loo = np.mean([A1[q] for q in other_prompts], axis=0)
        c6_loo = np.mean([A6[q] for q in other_prompts], axis=0)

        cos_1_same = cos_sim(A1[p], c1_loo)
        cos_1_diff = cos_sim(A1[p], c6_loo)
        cos_6_same = cos_sim(A6[p], c6_loo)
        cos_6_diff = cos_sim(A6[p], c1_loo)

        v_p = 0.5 * ((cos_1_same - cos_1_diff) + (cos_6_same - cos_6_diff))
        V_per_prompt[p] = {
            "v_p": v_p,
            "cos_1_same": cos_1_same,
            "cos_1_diff": cos_1_diff,
            "cos_6_same": cos_6_same,
            "cos_6_diff": cos_6_diff,
        }

    v_vals = [V_per_prompt[p]["v_p"] for p in prompts]
    mean_V, p_val_V, floor_V, n_V = sign_flip_test(v_vals)

    # 5. Criterio Nullo di Falsificazione: V_scramble(p)
    V_scr_per_prompt = {}
    for p in prompts:
        other_prompts = [q for q in prompts if q != p]
        c_sa_loo = np.mean([A_scrA[q] for q in other_prompts], axis=0)
        c_sb_loo = np.mean([A_scrB[q] for q in other_prompts], axis=0)

        cos_sa_same = cos_sim(A_scrA[p], c_sa_loo)
        cos_sa_diff = cos_sim(A_scrA[p], c_sb_loo)
        cos_sb_same = cos_sim(A_scrB[p], c_sb_loo)
        cos_sb_diff = cos_sim(A_scrB[p], c_sa_loo)

        v_scr_p = 0.5 * ((cos_sa_same - cos_sa_diff) + (cos_sb_same - cos_sb_diff))
        V_scr_per_prompt[p] = {
            "v_scr_p": v_scr_p,
            "cos_sa_same": cos_sa_same,
            "cos_sa_diff": cos_sa_diff,
            "cos_sb_same": cos_sb_same,
            "cos_sb_diff": cos_sb_diff,
        }

    v_scr_vals = [V_scr_per_prompt[p]["v_scr_p"] for p in prompts]
    mean_V_scr, p_val_V_scr, _, _ = sign_flip_test(v_scr_vals)

    # 6. Coerenza intra-blocco e inter-blocco
    pairs_b1 = [cos_sim(A1[p1], A1[p2]) for p1, p2 in itertools.combinations(prompts, 2)]
    pairs_b6 = [cos_sim(A6[p1], A6[p2]) for p1, p2 in itertools.combinations(prompts, 2)]
    pairs_sa = [cos_sim(A_scrA[p1], A_scrA[p2]) for p1, p2 in itertools.combinations(prompts, 2)]
    pairs_sb = [cos_sim(A_scrB[p1], A_scrB[p2]) for p1, p2 in itertools.combinations(prompts, 2)]

    coh_b1 = float(np.mean(pairs_b1))
    coh_b6 = float(np.mean(pairs_b6))
    coh_sa = float(np.mean(pairs_sa))
    coh_sb = float(np.mean(pairs_sb))

    # Coseno cross-blocco (medio dei centroidi)
    c1_all = np.mean([A1[p] for p in prompts], axis=0)
    c6_all = np.mean([A6[p] for p in prompts], axis=0)
    raw_cross_cos = cos_sim(c1_all, c6_all)

    den = math.sqrt(max(coh_b1, 0.0) * max(coh_b6, 0.0))
    disattenuated_cos = (raw_cross_cos / den) if den > 1e-6 else np.nan

    # Norme e quota antisimmetrica
    norm_s1 = float(np.mean([np.linalg.norm(S1[p]) for p in prompts]))
    norm_a1 = float(np.mean([np.linalg.norm(A1[p]) for p in prompts]))
    share_a1 = norm_a1 / (norm_s1 + norm_a1) if (norm_s1 + norm_a1) > 0 else 0.0

    norm_s6 = float(np.mean([np.linalg.norm(S6[p]) for p in prompts]))
    norm_a6 = float(np.mean([np.linalg.norm(A6[p]) for p in prompts]))
    share_a6 = norm_a6 / (norm_s6 + norm_a6) if (norm_s6 + norm_a6) > 0 else 0.0

    return {
        "space": space_name,
        "n_features": len(feature_cols),
        "mean_V": mean_V,
        "p_val_V": p_val_V,
        "floor_V": floor_V,
        "mean_V_scramble": mean_V_scr,
        "p_val_V_scramble": p_val_V_scr,
        "falsification_passed": bool(mean_V > mean_V_scr and p_val_V <= 0.05),
        "coh_b1": coh_b1,
        "coh_b6": coh_b6,
        "coh_scramble_A": coh_sa,
        "coh_scramble_B": coh_sb,
        "raw_cross_cos_B1_B6": raw_cross_cos,
        "disattenuated_cos": disattenuated_cos,
        "share_antisym_B1": share_a1,
        "share_antisym_B6": share_a6,
        "norm_A1": norm_a1,
        "norm_S1": norm_s1,
        "norm_A6": norm_a6,
        "norm_S6": norm_s6,
        "V_per_prompt": V_per_prompt,
        "V_scr_per_prompt": V_scr_per_prompt,
    }


def main():
    print("=== ANALISI STATISTICA PRE-REGISTRATA: BLOCK_1 VS BLOCK_6 ===")
    if not os.path.exists(STYLE_CSV) or not os.path.exists(PALETTE_CSV):
        raise FileNotFoundError(f"File feature mancanti:\n  {STYLE_CSV}\n  {PALETTE_CSV}")

    st_df = pd.read_csv(STYLE_CSV)
    pa_df = pd.read_csv(PALETTE_CSV)
    print(f"Righe caricate: {len(st_df)} (style), {len(pa_df)} (palette)")
    if len(st_df) != 210:
        raise ValueError(f"Attese esattamente 210 righe, trovate {len(st_df)}")

    # Spazi da analizzare
    # Spazio primario
    spaces = [
        ("Tessitura (PRIMARIO)", TEXTURE_COLS),
        ("Global 23 Features (Secondario)", [c for c in st_df.columns if c not in [
            "run_idx", "prompt_id", "seed", "condition", "node_type", "angle", "d_target", "image_path", "file",
            "width_px", "height_px"
        ]]),
        ("Linework (Secondario)", LINEWORK_COLS),
        ("Shadow Hardness (Secondario)", SHADOW_COLS),
        ("Palette LAB/Chroma (Secondario)", PALETTE_COLS),
    ]

    all_results = []
    scores_records = []

    for space_name, cols in spaces:
        print(f"\nAnalisi per lo spazio: {space_name} ({len(cols)} dimensioni)...")
        res = run_analysis_for_space(st_df, pa_df, space_name, cols)

        print(f"  Vantaggio LOO V: {res['mean_V']:+.4f} (p = {res['p_val_V']:.5f}, floor = {res['floor_V']:.5f})")
        print(f"  Controllo Scramble: {res['mean_V_scramble']:+.4f} (p = {res['p_val_V_scramble']:.5f})")
        print(f"  Falsificazione superata (V > V_scr e p <= 0.05): {res['falsification_passed']}")
        print(f"  Coerenza B1: {res['coh_b1']:+.4f} | Coerenza B6: {res['coh_b6']:+.4f}")
        print(f"  Coseno cross B1-B6: grezzo {res['raw_cross_cos_B1_B6']:+.4f}, disattenuato {res['disattenuated_cos']:+.4f}")

        row = {
            "space": res["space"],
            "n_features": res["n_features"],
            "mean_V": round(res["mean_V"], 5),
            "p_val_V": round(res["p_val_V"], 5),
            "floor_V": round(res["floor_V"], 5),
            "mean_V_scramble": round(res["mean_V_scramble"], 5),
            "p_val_V_scramble": round(res["p_val_V_scramble"], 5),
            "falsification_passed": res["falsification_passed"],
            "coh_b1": round(res["coh_b1"], 5),
            "coh_b6": round(res["coh_b6"], 5),
            "coh_scramble_A": round(res["coh_scramble_A"], 5),
            "coh_scramble_B": round(res["coh_scramble_B"], 5),
            "raw_cross_cos_B1_B6": round(res["raw_cross_cos_B1_B6"], 5),
            "disattenuated_cos": round(res["disattenuated_cos"], 5) if not np.isnan(res["disattenuated_cos"]) else "NaN",
            "share_antisym_B1": round(res["share_antisym_B1"], 4),
            "share_antisym_B6": round(res["share_antisym_B6"], 4),
        }
        all_results.append(row)

        # Raccogli punteggi dettagliati per prompt nello spazio primario
        if "PRIMARIO" in space_name:
            for p, v_dict in res["V_per_prompt"].items():
                scr_dict = res["V_scr_per_prompt"][p]
                scores_records.append({
                    "prompt_id": p,
                    "V_p": round(v_dict["v_p"], 5),
                    "cos_1_same": round(v_dict["cos_1_same"], 5),
                    "cos_1_diff": round(v_dict["cos_1_diff"], 5),
                    "cos_6_same": round(v_dict["cos_6_same"], 5),
                    "cos_6_diff": round(v_dict["cos_6_diff"], 5),
                    "V_scramble_p": round(scr_dict["v_scr_p"], 5),
                    "cos_sa_same": round(scr_dict["cos_sa_same"], 5),
                    "cos_sa_diff": round(scr_dict["cos_sa_diff"], 5),
                    "cos_sb_same": round(scr_dict["cos_sb_same"], 5),
                    "cos_sb_diff": round(scr_dict["cos_sb_diff"], 5),
                })

    # Salva risultati su entrambi i repository
    for res_p in [RESULTS_CSV_REPORT, RESULTS_CSV_PILOT]:
        os.makedirs(os.path.dirname(res_p), exist_ok=True)
        with open(res_p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_results[0].keys()))
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n[Salvato] Risultati statistici: {res_p}")

    for sc_p in [SCORES_CSV_REPORT, SCORES_CSV_PILOT]:
        os.makedirs(os.path.dirname(sc_p), exist_ok=True)
        with open(sc_p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(scores_records[0].keys()))
            writer.writeheader()
            writer.writerows(scores_records)
        print(f"[Salvato] Punteggi per prompt: {sc_p}")


if __name__ == "__main__":
    main()
