# -*- coding: utf-8 -*-
"""
experiments/analyze_stage9_style_direction.py

Analisi formale di Stage 9 secondo la pre-registrazione emendata (docs/prereg_stage9_style_direction.md):
1. Affidabilita' di misura split-half (2v3 e Spearman-Brown r5) calcolata su tutti i 10 split dei 5 seed.
2. Statistica decisionale primaria disattenuata:
     Delta C_corr = (C_soggetto / r5_soggetto) - (C_stile / r5_stile)
   ricalcolata endogenamente dentro ogni iterazione del test di permutazione (20.000 estrazioni).
3. Analisi nei 4 spazi:
   - 1. 24-D completo (L*, a*, b* su 8 slot con conversione analitica di croma e tinta)
   - 2. 8-D solo luminanza (L*)
   - 3. 16-D solo cromatico (a*, b*)
   - 4. 5-D asse di tessitura (crosshatch_entropy_mean, edge_density, stroke_width_cv, contour_n_components, lbp_entropy)
4. Standardizzazione CONGIUNTA sull'unione dei due corpora (Stage 9 stile union Stage 7 soggetti).
5. Gate di qualita' 3-sigma sull'ampiezza 2.0x prima del calcolo dei coseni.
"""

import os
import sys
import csv
import math
import random
import itertools
import numpy as np
from collections import defaultdict
import shutil

PILOT_ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"

PALETTE_STAGE9 = os.path.join(PILOT_ROOT, "palette_features_stage9.csv")
STYLE_STAGE9 = os.path.join(PILOT_ROOT, "style_features_stage9.csv")

PALETTE_STAGE7 = os.path.join(PILOT_ROOT, "palette_features_stage7_all.csv")
STYLE_STAGE7 = os.path.join(PILOT_ROOT, "style_features_stage7.csv")

OUT_COHERENCE_CSV = os.path.join(PILOT_ROOT, "stage9_coherence_results.csv")
OUT_RELIABILITY_CSV = os.path.join(PILOT_ROOT, "stage9_reliability_results.csv")
OUT_QUALITY_GATE_CSV = os.path.join(PILOT_ROOT, "stage9_amplitude2x_quality_gate.csv")

REPORT_DATA = os.path.join(REPORT_ROOT, "data")

SW = range(1, 7)
TEXTURE_COLS = ["crosshatch_entropy_mean", "edge_density", "stroke_width_cv", "contour_n_components", "lbp_entropy"]

TREATMENTS_1X = ["preset_pos_1x", "blockshuf_neg_1x", "rand_pos_1x"]
TREATMENTS_2X = ["preset_pos_2x", "blockshuf_neg_2x", "rand_pos_2x"]

TREATMENT_MAPPING_1X = {
    "preset_pos_1x": "preset_pos",
    "blockshuf_neg_1x": "blockshuf_neg",
    "rand_pos_1x": "rand_pos"
}

TREATMENT_MAPPING_2X = {
    "preset_pos_2x": "preset_pos",
    "blockshuf_neg_2x": "blockshuf_neg",
    "rand_pos_2x": "rand_pos"
}

# Tutti i 10 split possibili di 5 seed in 2 contro 3
SPLITS_2V3 = list(itertools.combinations(range(5), 2))


def feature_vector_24(r):
    """(L, a, b) per i sei swatch piu' carta e inchiostro -> 24 dimensioni."""
    v = []
    for pre in [f"sw{i}" for i in SW] + ["paper", "ink"]:
        L = float(r[f"{pre}_L"])
        C = float(r[f"{pre}_C"])
        h = np.deg2rad(float(r[f"{pre}_hue_deg"]))
        v += [L, C * np.cos(h), C * np.sin(h)]
    return np.array(v, dtype=np.float64)


def feature_vector_lum_8(v24):
    """Solo coordinate L* dagli 8 slot."""
    indices = [i * 3 for i in range(8)]
    return v24[indices]


def feature_vector_chroma_16(v24):
    """Solo coordinate a* e b* dagli 8 slot."""
    indices = [i * 3 + j for i in range(8) for j in (1, 2)]
    return v24[indices]


def mean_pairwise_cos(U):
    """Coseno direzionale medio a coppie (i < j)."""
    N = len(U)
    if N < 2:
        return 0.0
    norms = np.linalg.norm(U, axis=1, keepdims=True)
    norms[norms == 0] = 1e-12
    U_norm = U / norms
    M = U_norm @ U_norm.T
    iu = np.triu_indices(N, 1)
    return float(M[iu].mean())


def compute_prompt_split_half_r(seed_diffs_list):
    """
    Calcola l'affidabilita' split-half 2v3 per un singolo prompt:
    seed_diffs_list e' una lista di 5 vettori delta (uno per seed).
    Restituisce la media dei coseni sulle 10 partizioni 2 contro 3.
    """
    if len(seed_diffs_list) < 5:
        return 0.0

    V = np.array(seed_diffs_list)  # (5, dim)
    all_indices = set(range(5))
    cos_splits = []

    for idx2 in SPLITS_2V3:
        idx3 = list(all_indices - set(idx2))
        u_A = np.mean(V[list(idx2)], axis=0)
        u_B = np.mean(V[idx3], axis=0)
        norm_A = np.linalg.norm(u_A)
        norm_B = np.linalg.norm(u_B)
        if norm_A > 1e-12 and norm_B > 1e-12:
            cos_splits.append(np.dot(u_A, u_B) / (norm_A * norm_B))
        else:
            cos_splits.append(0.0)

    return float(np.mean(cos_splits))


def spearman_brown(r_half):
    """Stima affidabilita' a 5 seed: r_5 = 2r / (1 + r)."""
    if r_half <= 0.0:
        return max(r_half, 1e-4)
    r5 = (2.0 * r_half) / (1.0 + r_half)
    return min(1.0, max(1e-4, r5))


def run_permutation_disattenuated(U_style, U_subj, r_prompts_style, r_prompts_subj, n_iter=20000):
    """
    Esegue il test di permutazione Monte Carlo scambiando le etichette di corpus.
    Ricalcola dinamicamente C e r5 per ciascun gruppo permutato.
    """
    n_style = len(U_style)
    n_subj = len(U_subj)
    combined_U = np.vstack([U_style, U_subj])
    combined_r = np.array(list(r_prompts_style) + list(r_prompts_subj))
    total = len(combined_U)

    # 1. Valori osservati
    c_style_obs = mean_pairwise_cos(U_style)
    c_subj_obs = mean_pairwise_cos(U_subj)
    raw_diff_obs = c_subj_obs - c_style_obs

    r_half_style_obs = float(np.mean(r_prompts_style))
    r_half_subj_obs = float(np.mean(r_prompts_subj))
    r5_style_obs = spearman_brown(r_half_style_obs)
    r5_subj_obs = spearman_brown(r_half_subj_obs)

    disatt_style_obs = c_style_obs / r5_style_obs
    disatt_subj_obs = c_subj_obs / r5_subj_obs
    disatt_diff_obs = disatt_subj_obs - disatt_style_obs

    # 2. Monte Carlo permutation
    count_raw_extreme = 0
    count_disatt_extreme = 0
    rng = random.Random(20260918)

    for _ in range(n_iter):
        idx = list(range(total))
        rng.shuffle(idx)
        idx_style = idx[:n_style]
        idx_subj = idx[n_style:]

        perm_U_style = combined_U[idx_style]
        perm_U_subj = combined_U[idx_subj]

        perm_c_style = mean_pairwise_cos(perm_U_style)
        perm_c_subj = mean_pairwise_cos(perm_U_subj)
        perm_raw_diff = perm_c_subj - perm_c_style
        if perm_raw_diff >= raw_diff_obs:
            count_raw_extreme += 1

        perm_r5_style = spearman_brown(float(np.mean(combined_r[idx_style])))
        perm_r5_subj = spearman_brown(float(np.mean(combined_r[idx_subj])))
        perm_disatt_diff = (perm_c_subj / perm_r5_subj) - (perm_c_style / perm_r5_style)
        if perm_disatt_diff >= disatt_diff_obs:
            count_disatt_extreme += 1

    p_raw = (count_raw_extreme + 1) / (n_iter + 1)
    p_disatt = (count_disatt_extreme + 1) / (n_iter + 1)

    return {
        "c_style": c_style_obs,
        "c_subj": c_subj_obs,
        "raw_diff": raw_diff_obs,
        "p_raw": p_raw,
        "r_half_style": r_half_style_obs,
        "r_half_subj": r_half_subj_obs,
        "r5_style": r5_style_obs,
        "r5_subj": r5_subj_obs,
        "c_style_disatt": disatt_style_obs,
        "c_subj_disatt": disatt_subj_obs,
        "disatt_diff": disatt_diff_obs,
        "p_disatt": p_disatt,
        "decision": "CONFIRMED" if (p_disatt < 0.05) else ("ATTENUATION_ARTEFACT" if (p_raw < 0.05) else "NOT_SIGNIFICANT")
    }


def load_raw_features_color(csv_path):
    rows = list(csv.DictReader(open(csv_path, "r", encoding="utf-8-sig")))
    cell = {}
    for r in rows:
        pid = r["prompt_sha1"]
        cond = r["condition"]
        seed = int(r["seed"])
        cell[(pid, cond, seed)] = feature_vector_24(r)
    return cell


def load_raw_features_texture(csv_path):
    rows = list(csv.DictReader(open(csv_path, "r", encoding="utf-8-sig")))
    cell = {}
    for r in rows:
        pid = r["prompt_sha1"]
        cond = r["condition"]
        seed = int(r["seed"])
        vec = np.array([float(r[c]) for c in TEXTURE_COLS], dtype=np.float64)
        cell[(pid, cond, seed)] = vec
    return cell


def evaluate_quality_gate_2x(csv_style_path):
    """
    Gate di qualita' 3-sigma sull'ampiezza 2.0x:
    Confronta lo scostamento in unita' sigma dal baseline su edge_density e lbp_entropy.
    """
    print("\n--- QUALITY GATE AMPIEZZA 2.0x (Soglia 3-sigma) ---")
    rows = list(csv.DictReader(open(csv_style_path, "r", encoding="utf-8-sig")))
    by_cell = defaultdict(lambda: defaultdict(list))

    for r in rows:
        pid = r.get("prompt_dir") or r.get("file", "").split("_")[0]
        cond = r["condition"]
        ed = float(r.get("edge_density", 0.0))
        lbp = float(r.get("lbp_entropy", 0.0))
        by_cell[pid][cond].append((ed, lbp))

    gate_results = []
    degraded_count = 0
    total_cells = 0

    target_prompts = sorted(by_cell.keys())
    for pid in target_prompts:
        base_vals = by_cell[pid].get("baseline", [])
        if len(base_vals) < 2:
            continue
        base_ed = [v[0] for v in base_vals]
        base_lbp = [v[1] for v in base_vals]
        m_base_ed, s_base_ed = np.mean(base_ed), np.std(base_ed, ddof=1)
        m_base_lbp, s_base_lbp = np.mean(base_lbp), np.std(base_lbp, ddof=1)

        for tr_2x in TREATMENTS_2X:
            tr_vals = by_cell[pid].get(tr_2x, [])
            if not tr_vals:
                continue
            total_cells += 1
            tr_ed = [v[0] for v in tr_vals]
            tr_lbp = [v[1] for v in tr_vals]
            m_tr_ed = np.mean(tr_ed)
            m_tr_lbp = np.mean(tr_lbp)

            z_ed = abs(m_tr_ed - m_base_ed) / (s_base_ed + 1e-12)
            z_lbp = abs(m_tr_lbp - m_base_lbp) / (s_base_lbp + 1e-12)
            is_degraded = (z_ed > 3.0) or (z_lbp > 3.0)
            if is_degraded:
                degraded_count += 1

            status = "DEGRADED (OUT_OF_RANGE)" if is_degraded else "PASS"
            print(f"  [{pid:12s} | {tr_2x:16s}] z(edge): {z_ed:5.2f} | z(lbp): {z_lbp:5.2f} -> {status}")

            gate_results.append({
                "prompt": pid,
                "treatment": tr_2x,
                "z_edge_density": f"{z_ed:.3f}",
                "z_lbp_entropy": f"{z_lbp:.3f}",
                "status": status
            })

    print(f"\n  Totale celle 2.0x analizzate: {total_cells} | Fuori range (degradate > 3 sigma): {degraded_count}")

    if gate_results:
        with open(OUT_QUALITY_GATE_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["prompt", "treatment", "z_edge_density", "z_lbp_entropy", "status"])
            w.writeheader()
            w.writerows(gate_results)
        print(f"  -> Salvato in {OUT_QUALITY_GATE_CSV}")

    return degraded_count, total_cells


def run_full_analysis():
    print("==================================================================")
    print(" ANALISI COERENZA STAGE 9: VARIANTI DI STILE vs VARIANTI DI SOGGETTO")
    print(" (CON METODOLOGIA EMENDATA: AFFIDABILITA' & DISATTENUAZIONE)")
    print("==================================================================")

    if not os.path.exists(PALETTE_STAGE9) or not os.path.exists(STYLE_STAGE9):
        print(f"[ATTESA] I render di Stage 9 sono ancora in corso. File non trovati:\n  {PALETTE_STAGE9}\n  {STYLE_STAGE9}")
        return

    # 1. Esegui il Quality Gate sull'ampiezza 2.0x
    evaluate_quality_gate_2x(STYLE_STAGE9)

    # 2. Carica le matrici grezze
    raw_c_s9 = load_raw_features_color(PALETTE_STAGE9)
    raw_c_s7 = load_raw_features_color(PALETTE_STAGE7)

    raw_t_s9 = load_raw_features_texture(STYLE_STAGE9)
    raw_t_s7 = load_raw_features_texture(STYLE_STAGE7)

    amp_configs = [
        ("Ampiezza 1.0x", TREATMENT_MAPPING_1X),
        ("Ampiezza 2.0x", TREATMENT_MAPPING_2X),
    ]

    spaces = [
        ("1. 24-D Completo (L*, a*, b*)", lambda v: v),
        ("2. 8-D Solo Luminanza (L*)", feature_vector_lum_8),
        ("3. 16-D Solo Cromatico (a*, b*)", feature_vector_chroma_16),
        ("4. 5-D Asse Tessitura", "texture"),
    ]

    coherence_results = []
    reliability_results = []

    for amp_label, t_map in amp_configs:
        print(f"\n##################################################################")
        print(f" {amp_label.upper()}")
        print(f"##################################################################")

        for sp_name, sp_fn in spaces:
            print(f"\n--- Spazio: {sp_name} ---")

            for s9_tr, s7_tr in t_map.items():
                # Calcola i vettori differenza seed per seed
                # e proietta nello spazio prescelto
                def get_seed_deltas(cell, cond_name):
                    prompts = sorted({k[0] for k in cell})
                    prompt_deltas = {}
                    for p in prompts:
                        deltas = []
                        for s in [42, 777, 1337, 9999, 4242145]:
                            if (p, cond_name, s) in cell and (p, "baseline", s) in cell:
                                v_cond = cell[(p, cond_name, s)]
                                v_base = cell[(p, "baseline", s)]
                                if sp_fn != "texture":
                                    d = sp_fn(v_cond) - sp_fn(v_base)
                                else:
                                    d = v_cond - v_base
                                deltas.append(d)
                        if len(deltas) == 5:
                            prompt_deltas[p] = deltas
                    return prompt_deltas

                deltas_s9 = get_seed_deltas(raw_c_s9 if sp_fn != "texture" else raw_t_s9, s9_tr)
                deltas_s7 = get_seed_deltas(raw_c_s7 if sp_fn != "texture" else raw_t_s7, s7_tr)

                # Standardizzazione CONGIUNTA:
                # Calcola media e std dev congiunta su TUTTI i delta seed di entrambi i corpora
                all_deltas_flat = []
                for p_d in deltas_s9.values():
                    all_deltas_flat.extend(p_d)
                for p_d in deltas_s7.values():
                    all_deltas_flat.extend(p_d)

                all_deltas_arr = np.array(all_deltas_flat)
                mu_joint = np.mean(all_deltas_arr, axis=0)
                std_joint = np.std(all_deltas_arr, axis=0)
                std_joint[std_joint == 0] = 1.0

                # Applica la standardizzazione congiunta a ciascun vettore seed
                def standardize_deltas(d_dict):
                    std_dict = {}
                    for p, d_list in d_dict.items():
                        std_dict[p] = [(v - mu_joint) / std_joint for v in d_list]
                    return std_dict

                s_deltas_s9 = standardize_deltas(deltas_s9)
                s_deltas_s7 = standardize_deltas(deltas_s7)

                # Calcola r_p (split-half 2v3) per ciascun prompt
                r_prompts_s9 = [compute_prompt_split_half_r(s_deltas_s9[p]) for p in sorted(s_deltas_s9.keys())]
                r_prompts_s7 = [compute_prompt_split_half_r(s_deltas_s7[p]) for p in sorted(s_deltas_s7.keys())]

                # Calcola il vettore prompt (media sui 5 seed)
                U_style = np.array([np.mean(s_deltas_s9[p], axis=0) for p in sorted(s_deltas_s9.keys())])
                U_subj = np.array([np.mean(s_deltas_s7[p], axis=0) for p in sorted(s_deltas_s7.keys())])

                # Esegui test di permutazione disattenuato
                res = run_permutation_disattenuated(U_style, U_subj, r_prompts_s9, r_prompts_s7, n_iter=20000)

                print(f"  [{s9_tr:16s} vs {s7_tr:14s}]")
                print(f"     Grezzo:     C_stile = {res['c_style']:+6.3f} | C_sogg = {res['c_subj']:+6.3f} | Delta = {res['raw_diff']:+6.3f} (p = {res['p_raw']:.4f})")
                print(f"     Affidab:    r5_stile = {res['r5_style']:5.3f} (2v3={res['r_half_style']:+5.3f}) | r5_sogg = {res['r5_subj']:5.3f} (2v3={res['r_half_subj']:+5.3f})")
                print(f"     Disatten:   C_stile = {res['c_style_disatt']:+6.3f} | C_sogg = {res['c_subj_disatt']:+6.3f} | Delta = {res['disatt_diff']:+6.3f} (p = {res['p_disatt']:.4f})")
                print(f"     Verdetto:   {res['decision']}")

                coherence_results.append({
                    "amplitude": amp_label,
                    "space": sp_name,
                    "condition_style": s9_tr,
                    "condition_subject": s7_tr,
                    "c_style_raw": f"{res['c_style']:.4f}",
                    "c_subject_raw": f"{res['c_subj']:.4f}",
                    "delta_c_raw": f"{res['raw_diff']:.4f}",
                    "p_value_raw": f"{res['p_raw']:.4f}",
                    "r5_style": f"{res['r5_style']:.4f}",
                    "r5_subject": f"{res['r5_subj']:.4f}",
                    "c_style_disatt": f"{res['c_style_disatt']:.4f}",
                    "c_subject_disatt": f"{res['c_subj_disatt']:.4f}",
                    "delta_c_disatt": f"{res['disatt_diff']:.4f}",
                    "p_value_disatt": f"{res['p_disatt']:.4f}",
                    "decision": res["decision"]
                })

                reliability_results.append({
                    "amplitude": amp_label,
                    "space": sp_name,
                    "condition": s9_tr,
                    "r_half_style_2v3": f"{res['r_half_style']:.4f}",
                    "r5_style_spearman_brown": f"{res['r5_style']:.4f}",
                    "r_half_subject_2v3": f"{res['r_half_subj']:.4f}",
                    "r5_subject_spearman_brown": f"{res['r5_subj']:.4f}",
                })

    if coherence_results:
        with open(OUT_COHERENCE_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(coherence_results[0].keys()))
            w.writeheader()
            w.writerows(coherence_results)
        print(f"\n[OK] Risultati coerenza salvati in {OUT_COHERENCE_CSV}")

    if reliability_results:
        with open(OUT_RELIABILITY_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(reliability_results[0].keys()))
            w.writeheader()
            w.writerows(reliability_results)
        print(f"[OK] Risultati affidabilita' salvati in {OUT_RELIABILITY_CSV}")

    if os.path.exists(REPORT_DATA):
        for out_f in [OUT_COHERENCE_CSV, OUT_RELIABILITY_CSV, OUT_QUALITY_GATE_CSV]:
            if os.path.exists(out_f):
                shutil.copy2(out_f, REPORT_DATA)
                print(f"[Sync] Copiato in report/data: {os.path.basename(out_f)}")


if __name__ == "__main__":
    run_full_analysis()
