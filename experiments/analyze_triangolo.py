# -*- coding: utf-8 -*-
"""
experiments/analyze_triangolo.py
================================
Analisi statistica formale dell'esperimento pre-registrato:
Triangolo Block_1 vs Block_3 vs Block_6 con Frobenius Displacement appaiato (D = 0.04500)
e controlli scramble omologhi e incrociati (scramble_A, B su B1 e scramble_C, D su B3).

Implementa esattamente le specifiche congelate in:
docs/prereg_rotations_triangolo_block1_block3_block6.md
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

STYLE_CSV = os.path.join(DATA_DIR_PILOT, "rotations_triangolo_style_features.csv")
PALETTE_CSV = os.path.join(DATA_DIR_PILOT, "rotations_triangolo_palette_features.csv")

RESULTS_CSV_REPORT = os.path.join(DATA_DIR_REPORT, "rotations_triangolo_results.csv")
RESULTS_CSV_PILOT = os.path.join(DATA_DIR_PILOT, "rotations_triangolo_results.csv")

SCORES_CSV_REPORT = os.path.join(DATA_DIR_REPORT, "rotations_triangolo_prompt_scores.csv")
SCORES_CSV_PILOT = os.path.join(DATA_DIR_PILOT, "rotations_triangolo_prompt_scores.csv")

TEXTURE_COLS = ["glcm_contrast", "glcm_homogeneity", "lbp_entropy"]
LINEWORK_COLS = ["stroke_width_cv", "edge_density", "contour_mean_length_px"]
SHADOW_COLS = ["crosshatch_entropy_mean", "crosshatch_entropy_p90"]
FREQ_COLS = ["fft_high_freq_share"]
PALETTE_COLS = ["paper_L", "ink_L", "sw1_L", "chroma_spread", "tonal_range"]

DELTA_EQUIV = 0.25

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
    signs = np.array(list(itertools.product([1, -1], repeat=n)))
    perm_means = (signs * v).mean(axis=1)
    p_val = float(np.mean(np.abs(perm_means) >= abs(obs) - 1e-12))
    floor = 2.0 / (2 ** n)
    return obs, p_val, floor, n

def calc_loo_v(A_dict, B_dict, prompts):
    V_dict = {}
    for p in prompts:
        other = [q for q in prompts if q != p]
        cA_loo = np.mean([A_dict[q] for q in other], axis=0)
        cB_loo = np.mean([B_dict[q] for q in other], axis=0)

        cos_A_same = cos_sim(A_dict[p], cA_loo)
        cos_A_diff = cos_sim(A_dict[p], cB_loo)
        cos_B_same = cos_sim(B_dict[p], cB_loo)
        cos_B_diff = cos_sim(B_dict[p], cA_loo)

        v_p = 0.5 * ((cos_A_same - cos_A_diff) + (cos_B_same - cos_B_diff))
        V_dict[p] = {
            "v_p": v_p,
            "cos_A_same": cos_A_same,
            "cos_A_diff": cos_A_diff,
            "cos_B_same": cos_B_same,
            "cos_B_diff": cos_B_diff,
        }
    return V_dict

def run_analysis_for_space(st_df, pa_df, space_name, feature_cols):
    combined_cols = {}
    for col in feature_cols:
        if col in st_df.columns:
            combined_cols[col] = st_df[col].astype(float)
        elif col in pa_df.columns:
            combined_cols[col] = pa_df[col].astype(float)
        else:
            raise KeyError(f"Feature '{col}' non trovata!")

    feat_df = pd.DataFrame(combined_cols)

    # 1. z-standardizzazione congiunta sulle 330 immagini
    feat_z = (feat_df - feat_df.mean(axis=0)) / (feat_df.std(axis=0, ddof=0).replace(0, np.nan))
    feat_z = feat_z.fillna(0.0)

    meta = st_df[["prompt_id", "seed", "condition", "angle"]].copy()
    z_df = pd.concat([meta, feat_z], axis=1)

    prompts = sorted(z_df["prompt_id"].unique())
    seeds = sorted(z_df["seed"].unique())

    # 2. Delta rispetto a baseline (stesso prompt e seed)
    deltas = {}
    for p in prompts:
        for s in seeds:
            base_row = z_df[(z_df.prompt_id == p) & (z_df.seed == s) & (z_df.condition == "baseline")]
            if len(base_row) == 0:
                raise ValueError(f"Baseline mancante per prompt={p}, seed={s}")
            base_vec = base_row[feature_cols].values[0]

            for cond in [
                "Block_1_pos", "Block_1_neg",
                "Block_3_pos", "Block_3_neg",
                "Block_6_pos", "Block_6_neg",
                "scramble_A", "scramble_B", "scramble_C", "scramble_D"
            ]:
                cond_row = z_df[(z_df.prompt_id == p) & (z_df.seed == s) & (z_df.condition == cond)]
                if len(cond_row) == 0:
                    raise ValueError(f"Condizione '{cond}' mancante per prompt={p}, seed={s}")
                cond_vec = cond_row[feature_cols].values[0]
                deltas[(p, s, cond)] = cond_vec - base_vec

    # 3. Componenti Antisimmetriche e Simmetriche mediate sui 3 seed
    A1, A3, A6 = {}, {}, {}
    S1, S3, S6 = {}, {}, {}
    A_scrA, A_scrB, A_scrC, A_scrD = {}, {}, {}, {}

    for p in prompts:
        a1_s, a3_s, a6_s = [], [], []
        s1_s, s3_s, s6_s = [], [], []
        sa_s, sb_s, sc_s, sd_s = [], [], [], []

        for s in seeds:
            d1_p = deltas[(p, s, "Block_1_pos")]
            d1_n = deltas[(p, s, "Block_1_neg")]
            d3_p = deltas[(p, s, "Block_3_pos")]
            d3_n = deltas[(p, s, "Block_3_neg")]
            d6_p = deltas[(p, s, "Block_6_pos")]
            d6_n = deltas[(p, s, "Block_6_neg")]

            d_sa = deltas[(p, s, "scramble_A")]
            d_sb = deltas[(p, s, "scramble_B")]
            d_sc = deltas[(p, s, "scramble_C")]
            d_sd = deltas[(p, s, "scramble_D")]

            a1_s.append((d1_p - d1_n) / 2.0)
            s1_s.append((d1_p + d1_n) / 2.0)
            a3_s.append((d3_p - d3_n) / 2.0)
            s3_s.append((d3_p + d3_n) / 2.0)
            a6_s.append((d6_p - d6_n) / 2.0)
            s6_s.append((d6_p + d6_n) / 2.0)

            sa_s.append(d_sa)
            sb_s.append(d_sb)
            sc_s.append(d_sc)
            sd_s.append(d_sd)

        A1[p] = np.mean(a1_s, axis=0)
        S1[p] = np.mean(s1_s, axis=0)
        A3[p] = np.mean(a3_s, axis=0)
        S3[p] = np.mean(s3_s, axis=0)
        A6[p] = np.mean(a6_s, axis=0)
        S6[p] = np.mean(s6_s, axis=0)

        A_scrA[p] = np.mean(sa_s, axis=0)
        A_scrB[p] = np.mean(sb_s, axis=0)
        A_scrC[p] = np.mean(sc_s, axis=0)
        A_scrD[p] = np.mean(sd_s, axis=0)

    # 4. Leave-One-Out per le 3 coppie di blocchi
    V_1_3 = calc_loo_v(A1, A3, prompts)
    V_3_6 = calc_loo_v(A3, A6, prompts)
    V_1_6 = calc_loo_v(A1, A6, prompts)

    # 5. Leave-One-Out per i controlli Scramble
    # Omologhi:
    V_scr_1_1 = calc_loo_v(A_scrA, A_scrB, prompts)  # scramble_A vs scramble_B
    V_scr_3_3 = calc_loo_v(A_scrC, A_scrD, prompts)  # scramble_C vs scramble_D

    # Cross-anchored (nullo formale per i contrasti con Block_3):
    V_scr_1_3 = calc_loo_v(A_scrA, A_scrC, prompts)  # scramble_A vs scramble_C
    V_scr_3_6 = calc_loo_v(A_scrC, A_scrA, prompts)  # scramble_C vs scramble_A

    # Media delle 4 combinazioni cross (A-C, A-D, B-C, B-D) per robustezza
    V_cross_AC = V_scr_1_3
    V_cross_AD = calc_loo_v(A_scrA, A_scrD, prompts)
    V_cross_BC = calc_loo_v(A_scrB, A_scrC, prompts)
    V_cross_BD = calc_loo_v(A_scrB, A_scrD, prompts)
    V_scr_cross_mean = {}
    for p in prompts:
        V_scr_cross_mean[p] = (
            V_cross_AC[p]["v_p"] + V_cross_AD[p]["v_p"] +
            V_cross_BC[p]["v_p"] + V_cross_BD[p]["v_p"]
        ) / 4.0

    # 6. Contrasti Appaiati Primari rispetto al Nullo Scramble Cross-Anchored
    # Delta V(p) = V(p) - V_scr(p)
    Delta_V_1_3 = [V_1_3[p]["v_p"] - V_scr_1_3[p]["v_p"] for p in prompts]
    Delta_V_3_6 = [V_3_6[p]["v_p"] - V_scr_3_6[p]["v_p"] for p in prompts]
    Delta_V_1_6 = [V_1_6[p]["v_p"] - V_scr_1_1[p]["v_p"] for p in prompts]

    # Test di permutazione esatta
    mean_Delta_1_3, p_Delta_1_3, floor_p, _ = sign_flip_test(Delta_V_1_3)
    mean_Delta_3_6, p_Delta_3_6, _, _ = sign_flip_test(Delta_V_3_6)
    mean_Delta_1_6, p_Delta_1_6, _, _ = sign_flip_test(Delta_V_1_6)

    # Medie grezze e relativi test
    vals_1_3 = [V_1_3[p]["v_p"] for p in prompts]
    vals_3_6 = [V_3_6[p]["v_p"] for p in prompts]
    vals_1_6 = [V_1_6[p]["v_p"] for p in prompts]

    mean_V_1_3, p_V_1_3, _, _ = sign_flip_test(vals_1_3)
    mean_V_3_6, p_V_3_6, _, _ = sign_flip_test(vals_3_6)
    mean_V_1_6, p_V_1_6, _, _ = sign_flip_test(vals_1_6)

    # Medie scramble
    mean_scr_1_1, p_scr_1_1, _, _ = sign_flip_test([V_scr_1_1[p]["v_p"] for p in prompts])
    mean_scr_3_3, p_scr_3_3, _, _ = sign_flip_test([V_scr_3_3[p]["v_p"] for p in prompts])
    mean_scr_1_3, p_scr_1_3, _, _ = sign_flip_test([V_scr_1_3[p]["v_p"] for p in prompts])
    mean_scr_cross, p_scr_cross, _, _ = sign_flip_test([V_scr_cross_mean[p] for p in prompts])

    # Correzione di Holm sui due primari (Delta_1_3 e Delta_3_6)
    p_primaries = sorted([(p_Delta_1_3, "Delta_1_3"), (p_Delta_3_6, "Delta_3_6")])
    holm_crit_1 = 0.05 / 2.0  # 0.025
    holm_crit_2 = 0.05 / 1.0  # 0.050
    sig_1 = p_primaries[0][0] <= holm_crit_1
    sig_2 = sig_1 and (p_primaries[1][0] <= holm_crit_2)
    holm_results = {
        p_primaries[0][1]: sig_1,
        p_primaries[1][1]: sig_2
    }

    # 7. Applicazione dell'Albero Decisionale a 4 Vie (con margine Delta_equiv = 0.25)
    pass_1_3 = (mean_Delta_1_3 > 0) and holm_results["Delta_1_3"]
    pass_3_6 = (mean_Delta_3_6 > 0) and holm_results["Delta_3_6"]

    diff_13_36 = abs(mean_V_1_3 - mean_V_3_6)
    max_13_36 = max(mean_V_1_3, mean_V_3_6)

    regime = "Indeterminato"
    regime_desc = ""

    if not pass_1_3 or not pass_3_6:
        regime = "1. Centro Piatto / Prossimita ai Confini"
        regime_desc = (
            f"Almeno uno dei due contrasti contro lo scramble non e' significativo "
            f"(Delta_1_3={mean_Delta_1_3:+.4f}, p={p_Delta_1_3:.5f}; Delta_3_6={mean_Delta_3_6:+.4f}, p={p_Delta_3_6:.5f}). "
            f"L'effetto e' limitato ai confini (ingresso e uscita) del modello."
        )
    elif diff_13_36 <= DELTA_EQUIV and (mean_V_1_6 - max_13_36 > DELTA_EQUIV):
        regime = "2. Gradiente Continuo di Profondita"
        regime_desc = (
            f"Entrambi i contrasti superano lo scramble, V_1,3 ({mean_V_1_3:.4f}) e V_3,6 ({mean_V_3_6:.4f}) "
            f"sono equivalenti (|diff|={diff_13_36:.4f} <= {DELTA_EQUIV}), e V_1,6 ({mean_V_1_6:.4f}) dista "
            f"> {DELTA_EQUIV} ({mean_V_1_6 - max_13_36:.4f}). Il vantaggio scala monotonamente con la profondita."
        )
    elif (abs(mean_V_1_3 - mean_V_1_6) <= DELTA_EQUIV) and (abs(mean_V_3_6 - mean_V_1_6) <= DELTA_EQUIV):
        regime = "3. Specializzazione Discreta Idiosincratica"
        regime_desc = (
            f"Tutti e tre i lati del triangolo sono equivalenti entro il margine di {DELTA_EQUIV} "
            f"(V_1,3={mean_V_1_3:.4f}, V_3,6={mean_V_3_6:.4f}, V_1,6={mean_V_1_6:.4f}). "
            f"Il centro possiede una direzione autonoma forte e distinguibile tanto quanto gli estremi."
        )
    elif diff_13_36 > DELTA_EQUIV or (pass_1_3 != pass_3_6):
        regime = "4. Asimmetria di Propagazione"
        regime_desc = (
            f"Forte asimmetria tra ingresso e uscita (|V_1,3 - V_3,6| = {diff_13_36:.4f} > {DELTA_EQUIV}). "
            f"La dinamica di uno dei due confini penetra nel centro molto piu' profondamente dell'altra."
        )

    # 8. Coerenze intra-blocco e coseni cross-blocco
    pairs_b1 = [cos_sim(A1[p1], A1[p2]) for p1, p2 in itertools.combinations(prompts, 2)]
    pairs_b3 = [cos_sim(A3[p1], A3[p2]) for p1, p2 in itertools.combinations(prompts, 2)]
    pairs_b6 = [cos_sim(A6[p1], A6[p2]) for p1, p2 in itertools.combinations(prompts, 2)]
    pairs_scra = [cos_sim(A_scrA[p1], A_scrA[p2]) for p1, p2 in itertools.combinations(prompts, 2)]
    pairs_scrb = [cos_sim(A_scrB[p1], A_scrB[p2]) for p1, p2 in itertools.combinations(prompts, 2)]
    pairs_scrc = [cos_sim(A_scrC[p1], A_scrC[p2]) for p1, p2 in itertools.combinations(prompts, 2)]
    pairs_scrd = [cos_sim(A_scrD[p1], A_scrD[p2]) for p1, p2 in itertools.combinations(prompts, 2)]

    coh_b1 = float(np.mean(pairs_b1))
    coh_b3 = float(np.mean(pairs_b3))
    coh_b6 = float(np.mean(pairs_b6))
    coh_sa = float(np.mean(pairs_scra))
    coh_sb = float(np.mean(pairs_scrb))
    coh_sc = float(np.mean(pairs_scrc))
    coh_sd = float(np.mean(pairs_scrd))

    c1_all = np.mean([A1[p] for p in prompts], axis=0)
    c3_all = np.mean([A3[p] for p in prompts], axis=0)
    c6_all = np.mean([A6[p] for p in prompts], axis=0)

    cross_1_3 = cos_sim(c1_all, c3_all)
    cross_3_6 = cos_sim(c3_all, c6_all)
    cross_1_6 = cos_sim(c1_all, c6_all)

    # Disattenuazione
    den_13 = math.sqrt(max(coh_b1, 0.0) * max(coh_b3, 0.0))
    den_36 = math.sqrt(max(coh_b3, 0.0) * max(coh_b6, 0.0))
    den_16 = math.sqrt(max(coh_b1, 0.0) * max(coh_b6, 0.0))

    disatt_13 = (cross_1_3 / den_13) if den_13 > 1e-6 else np.nan
    disatt_36 = (cross_3_6 / den_36) if den_36 > 1e-6 else np.nan
    disatt_16 = (cross_1_6 / den_16) if den_16 > 1e-6 else np.nan

    # Quote antisimmetriche
    norm_s1 = float(np.mean([np.linalg.norm(S1[p]) for p in prompts]))
    norm_a1 = float(np.mean([np.linalg.norm(A1[p]) for p in prompts]))
    share_a1 = norm_a1 / (norm_s1 + norm_a1) if (norm_s1 + norm_a1) > 0 else 0.0

    norm_s3 = float(np.mean([np.linalg.norm(S3[p]) for p in prompts]))
    norm_a3 = float(np.mean([np.linalg.norm(A3[p]) for p in prompts]))
    share_a3 = norm_a3 / (norm_s3 + norm_a3) if (norm_s3 + norm_a3) > 0 else 0.0

    norm_s6 = float(np.mean([np.linalg.norm(S6[p]) for p in prompts]))
    norm_a6 = float(np.mean([np.linalg.norm(A6[p]) for p in prompts]))
    share_a6 = norm_a6 / (norm_s6 + norm_a6) if (norm_s6 + norm_a6) > 0 else 0.0

    return {
        "space": space_name,
        "n_features": len(feature_cols),
        "mean_Delta_1_3": mean_Delta_1_3,
        "p_Delta_1_3": p_Delta_1_3,
        "sig_Delta_1_3": holm_results["Delta_1_3"],
        "mean_Delta_3_6": mean_Delta_3_6,
        "p_Delta_3_6": p_Delta_3_6,
        "sig_Delta_3_6": holm_results["Delta_3_6"],
        "mean_Delta_1_6": mean_Delta_1_6,
        "p_Delta_1_6": p_Delta_1_6,
        "mean_V_1_3": mean_V_1_3,
        "p_V_1_3": p_V_1_3,
        "mean_V_3_6": mean_V_3_6,
        "p_V_3_6": p_V_3_6,
        "mean_V_1_6": mean_V_1_6,
        "p_V_1_6": p_V_1_6,
        "mean_scr_1_1": mean_scr_1_1,
        "p_scr_1_1": p_scr_1_1,
        "mean_scr_3_3": mean_scr_3_3,
        "p_scr_3_3": p_scr_3_3,
        "mean_scr_1_3": mean_scr_1_3,
        "p_scr_1_3": p_scr_1_3,
        "mean_scr_cross": mean_scr_cross,
        "p_scr_cross": p_scr_cross,
        "regime": regime,
        "regime_desc": regime_desc,
        "coh_b1": coh_b1,
        "coh_b3": coh_b3,
        "coh_b6": coh_b6,
        "coh_sa": coh_sa,
        "coh_sb": coh_sb,
        "coh_sc": coh_sc,
        "coh_sd": coh_sd,
        "cross_1_3": cross_1_3,
        "cross_3_6": cross_3_6,
        "cross_1_6": cross_1_6,
        "disatt_1_3": disatt_13,
        "disatt_3_6": disatt_36,
        "disatt_1_6": disatt_16,
        "share_a1": share_a1,
        "share_a3": share_a3,
        "share_a6": share_a6,
        "V_1_3_per_prompt": V_1_3,
        "V_3_6_per_prompt": V_3_6,
        "V_1_6_per_prompt": V_1_6,
        "V_scr_1_3_per_prompt": V_scr_1_3,
        "V_scr_3_6_per_prompt": V_scr_3_6,
        "V_scr_1_1_per_prompt": V_scr_1_1,
        "V_scr_3_3_per_prompt": V_scr_3_3,
    }

def main():
    print("=== ANALISI STATISTICA FORMALE ESPERIMENTO TRIANGOLO ===")
    if not os.path.exists(STYLE_CSV) or not os.path.exists(PALETTE_CSV):
        sys.exit(f"File feature mancanti:\n  {STYLE_CSV}\n  {PALETTE_CSV}")

    st_df = pd.read_csv(STYLE_CSV)
    pa_df = pd.read_csv(PALETTE_CSV)
    print(f"Caricate {len(st_df)} righe di style e {len(pa_df)} righe di palette.\n")

    spaces = [
        ("Tessitura (Primario)", TEXTURE_COLS),
        ("Tratteggio e Bordi", LINEWORK_COLS),
        ("Ombreggio e Crosshatch", SHADOW_COLS),
        ("Frequenze Spaziali", FREQ_COLS),
        ("Spazio Palette", PALETTE_COLS),
    ]

    all_results = []
    tex_res = None

    for s_name, cols in spaces:
        res = run_analysis_for_space(st_df, pa_df, s_name, cols)
        all_results.append(res)
        if s_name.startswith("Tessitura"):
            tex_res = res

    # Stampa del Verdetto Primario
    print("=" * 80)
    print("  VERDETTO SPAZIO PRIMARIO TESSITURA (GLCM Contrast, Homogeneity, LBP Entropy)")
    print("=" * 80)
    print(f"Vantaggio Block_1 vs Block_3:  V_1,3 = {tex_res['mean_V_1_3']:+.4f} (p = {tex_res['p_V_1_3']:.5f})")
    print(f"Vantaggio Block_3 vs Block_6:  V_3,6 = {tex_res['mean_V_3_6']:+.4f} (p = {tex_res['p_V_3_6']:.5f})")
    print(f"Vantaggio Block_1 vs Block_6:  V_1,6 = {tex_res['mean_V_1_6']:+.4f} (p = {tex_res['p_V_1_6']:.5f})")
    print("-" * 80)
    print("PAVIMENTI NULLI SCRAMBLE (Displacement D = 0.04500 appaiato):")
    print(f"  Nullo Omologo Block_1 (scrA vs scrB): V_scr(1,1) = {tex_res['mean_scr_1_1']:+.4f} (p = {tex_res['p_scr_1_1']:.5f})")
    print(f"  Nullo Omologo Block_3 (scrC vs scrD): V_scr(3,3) = {tex_res['mean_scr_3_3']:+.4f} (p = {tex_res['p_scr_3_3']:.5f})")
    print(f"  Nullo Cross-Anchored (scrA vs scrC):  V_scr(1,3) = {tex_res['mean_scr_1_3']:+.4f} (p = {tex_res['p_scr_1_3']:.5f})")
    print(f"  Nullo Cross Medio (4 combinazioni):   V_scr_cross= {tex_res['mean_scr_cross']:+.4f} (p = {tex_res['p_scr_cross']:.5f})")
    print("-" * 80)
    print("IPOTESI PRIMARIE (Contrasti Appaiati vs Nullo Cross-Anchored):")
    print(f"  Delta V_1,3 = V_1,3 - V_scr(1,3): {tex_res['mean_Delta_1_3']:+.4f} | p = {tex_res['p_Delta_1_3']:.5f} | Sig (Holm): {tex_res['sig_Delta_1_3']}")
    print(f"  Delta V_3,6 = V_3,6 - V_scr(3,6): {tex_res['mean_Delta_3_6']:+.4f} | p = {tex_res['p_Delta_3_6']:.5f} | Sig (Holm): {tex_res['sig_Delta_3_6']}")
    print(f"  Delta V_1,6 = V_1,6 - V_scr(1,1): {tex_res['mean_Delta_1_6']:+.4f} | p = {tex_res['p_Delta_1_6']:.5f}")
    print("-" * 80)
    print(f"ALBERO DECISIONALE A 4 VIE (Margine di Equivalenza Delta_equiv = {DELTA_EQUIV}):")
    print(f"  REGIME SELEZIONATO: {tex_res['regime']}")
    print(f"  MOTIVAZIONE: {tex_res['regime_desc']}")
    print("=" * 80)

    # Salvataggio CSV Risultati
    summary_rows = []
    for r in all_results:
        summary_rows.append({
            "space": r["space"],
            "n_features": r["n_features"],
            "mean_V_1_3": r["mean_V_1_3"],
            "p_V_1_3": r["p_V_1_3"],
            "mean_V_3_6": r["mean_V_3_6"],
            "p_V_3_6": r["p_V_3_6"],
            "mean_V_1_6": r["mean_V_1_6"],
            "p_V_1_6": r["p_V_1_6"],
            "mean_scr_1_1": r["mean_scr_1_1"],
            "p_scr_1_1": r["p_scr_1_1"],
            "mean_scr_3_3": r["mean_scr_3_3"],
            "p_scr_3_3": r["p_scr_3_3"],
            "mean_scr_1_3": r["mean_scr_1_3"],
            "p_scr_1_3": r["p_scr_1_3"],
            "mean_scr_cross": r["mean_scr_cross"],
            "p_scr_cross": r["p_scr_cross"],
            "mean_Delta_1_3": r["mean_Delta_1_3"],
            "p_Delta_1_3": r["p_Delta_1_3"],
            "sig_Delta_1_3": r["sig_Delta_1_3"],
            "mean_Delta_3_6": r["mean_Delta_3_6"],
            "p_Delta_3_6": r["p_Delta_3_6"],
            "sig_Delta_3_6": r["sig_Delta_3_6"],
            "mean_Delta_1_6": r["mean_Delta_1_6"],
            "p_Delta_1_6": r["p_Delta_1_6"],
            "regime": r["regime"],
            "regime_desc": r["regime_desc"],
            "coh_b1": r["coh_b1"],
            "coh_b3": r["coh_b3"],
            "coh_b6": r["coh_b6"],
            "coh_sa": r["coh_sa"],
            "coh_sb": r["coh_sb"],
            "coh_sc": r["coh_sc"],
            "coh_sd": r["coh_sd"],
            "cross_1_3": r["cross_1_3"],
            "cross_3_6": r["cross_3_6"],
            "cross_1_6": r["cross_1_6"],
            "disatt_1_3": r["disatt_1_3"],
            "disatt_3_6": r["disatt_3_6"],
            "disatt_1_6": r["disatt_1_6"],
            "share_antisym_b1": r["share_a1"],
            "share_antisym_b3": r["share_a3"],
            "share_antisym_b6": r["share_a6"],
        })

    for out_p in [RESULTS_CSV_PILOT, RESULTS_CSV_REPORT]:
        os.makedirs(os.path.dirname(out_p), exist_ok=True)
        with open(out_p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
            w.writeheader()
            w.writerows(summary_rows)
        print(f"[Salvato] {out_p}")

    # Salvataggio Punteggi per Prompt (Spazio Primario Tessitura)
    prompts = sorted(tex_res["V_1_3_per_prompt"].keys())
    scores_rows = []
    for p in prompts:
        scores_rows.append({
            "prompt_id": p,
            "V_1_3": tex_res["V_1_3_per_prompt"][p]["v_p"],
            "V_3_6": tex_res["V_3_6_per_prompt"][p]["v_p"],
            "V_1_6": tex_res["V_1_6_per_prompt"][p]["v_p"],
            "V_scr_1_3": tex_res["V_scr_1_3_per_prompt"][p]["v_p"],
            "V_scr_3_6": tex_res["V_scr_3_6_per_prompt"][p]["v_p"],
            "V_scr_1_1": tex_res["V_scr_1_1_per_prompt"][p]["v_p"],
            "V_scr_3_3": tex_res["V_scr_3_3_per_prompt"][p]["v_p"],
            "Delta_1_3": tex_res["V_1_3_per_prompt"][p]["v_p"] - tex_res["V_scr_1_3_per_prompt"][p]["v_p"],
            "Delta_3_6": tex_res["V_3_6_per_prompt"][p]["v_p"] - tex_res["V_scr_3_6_per_prompt"][p]["v_p"],
        })

    for out_p in [SCORES_CSV_PILOT, SCORES_CSV_REPORT]:
        with open(out_p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(scores_rows[0].keys()))
            w.writeheader()
            w.writerows(scores_rows)
        print(f"[Salvato] {out_p}")

if __name__ == "__main__":
    main()
