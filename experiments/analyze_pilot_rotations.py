#!/usr/bin/env python3
"""
analyze_pilot_rotations.py
==========================
Lavori C e D del BRIEF per la ri-analisi delle rotazioni dei benchmark pilota.

Esegue:
1. Aggregazione a livello prompt (n = 7, media preliminare dei 3 seed di tiefling).
2. Regressione di clip_dist su D_modello e su D_blocco.
3. Calcolo dei residui per blocco: verifica se l'effetto estremi (1 & 6) sopravvive a D.
4. Test di permutazione esatta (sign-flip su 7 prompt, pavimento 2/2^7 = 0.0156).
5. Decomposizione simmetrica/antisimmetrica S e A con test di permutazione esatta.
"""

import os
import sys
import csv
import math
import itertools
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"
DATA_DIR = os.path.join(REPORT_ROOT, "data")
ROTATIONS_CSV = os.path.join(DATA_DIR, "pilot_rotations.csv")
DISPLACEMENT_CSV = os.path.join(DATA_DIR, "pilot_rotation_displacement.csv")

def load_data():
    # Carica displacement
    disp = {}
    with open(DISPLACEMENT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            b = r["block"]
            rot_k = r["rot_kind"]
            ang = float(r["angle_deg"])
            disp[(b, rot_k, ang)] = {
                "tensors_touched": int(r["tensors_touched"]),
                "delta_norm": float(r["delta_norm"]),
                "d_block": float(r["d_block"]),
                "d_model": float(r["d_model"]),
            }

    # Carica rotazioni
    rot_rows = []
    with open(ROTATIONS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rot_rows.append({
                "report": r["report"],
                "prompt_id": r["prompt_id"],
                "seed": int(r["seed"]),
                "family": r["family"],
                "block": r["block"],
                "rot_kind": r["rot_kind"],
                "angle_deg": float(r["angle_deg"]) if r["angle_deg"] else None,
                "clip_dist": float(r["clip_dist"]),
                "cosine_sim": float(r["cosine_sim"]),
            })

    return disp, rot_rows

def aggregate_by_prompt(rot_rows):
    """
    Raggruppa le righe per (prompt_id, family, block, rot_kind, angle_deg)
    e fa la media su tutti i seed/report per quel prompt.
    Per tiefling (3 seed), media i 3 valori prima di procedere.
    """
    grouped = defaultdict(list)
    for r in rot_rows:
        key = (r["prompt_id"], r["family"], r["block"], r["rot_kind"], r["angle_deg"])
        grouped[key].append(r["clip_dist"])

    aggregated = []
    for (prompt_id, family, block, rot_kind, angle_deg), dists in grouped.items():
        mean_dist = sum(dists) / len(dists)
        aggregated.append({
            "prompt_id": prompt_id,
            "family": family,
            "block": block,
            "rot_kind": rot_kind,
            "angle_deg": angle_deg,
            "clip_dist": mean_dist,
            "n_seeds": len(dists),
        })

    return aggregated

def linear_regression(x, y):
    """Calcola pendenza, intercetta, R^2 e residui per OLS univariata."""
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    ss_xx = sum((xi - mean_x) ** 2 for xi in x)
    ss_yy = sum((yi - mean_y) ** 2 for yi in y)
    ss_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))

    slope = ss_xy / ss_xx if ss_xx != 0 else 0.0
    intercept = mean_y - slope * mean_x

    y_pred = [intercept + slope * xi for xi in x]
    residuals = [yi - ypi for yi, ypi in zip(y, y_pred)]
    ss_res = sum(r ** 2 for r in residuals)
    r2 = 1.0 - (ss_res / ss_yy) if ss_yy != 0 else 0.0

    return slope, intercept, r2, residuals

def exact_sign_flip_test(diffs):
    """
    Test di permutazione esatta a scambio di segno per campioni appaiati / contrasti per prompt.
    H0: media della differenza = 0 (la distribuzione e' simmetrica attorno a 0).
    Pavimento teorico per n=7: 2 / 2^7 = 2 / 128 = 0.015625.
    """
    n = len(diffs)
    observed_t = sum(diffs) / n
    abs_observed = abs(observed_t)

    # Tutte le 2^n combinazioni di segno (+1, -1)
    all_combos = list(itertools.product([-1, 1], repeat=n))
    total_perms = len(all_combos)
    count_extreme = 0

    for signs in all_combos:
        perm_t = sum(s * d for s, d in zip(signs, diffs)) / n
        if abs(perm_t) >= abs_observed - 1e-12:
            count_extreme += 1

    p_value = count_extreme / total_perms
    floor_p = 2.0 / (2 ** n)
    return observed_t, p_value, floor_p, total_perms

def main():
    disp, rot_rows = load_data()
    print("Dati caricati:")
    print(f"  Righe rotazioni grezze: {len(rot_rows)}")
    print(f"  Condizioni di displacement: {len(disp)}")

    # Filtra solo rotX (216 righe grezze)
    rotX_rows = [r for r in rot_rows if r["family"] == "rotX"]
    print(f"  Righe rotX grezze: {len(rotX_rows)} (9 report x 24 celle)")

    # Aggregazione per prompt
    agg = aggregate_by_prompt(rotX_rows)
    prompts = sorted(list(set(r["prompt_id"] for r in agg)))
    print(f"\nPrompt unici ({len(prompts)}): {prompts}")
    assert len(prompts) == 7, f"Attesi 7 prompt, trovati {len(prompts)}"
    assert len(agg) == 7 * 24, f"Attese 168 righe aggregate, trovate {len(agg)}"

    # Verifica medie grezze per blocco e angolo (per confrontare con tabella §0 del brief)
    print("\n" + "="*80)
    print("TABELLA GREZZA MEDIE CLIP-Dist SUI 7 PROMPT")
    print("="*80)
    print(f"{'Blocco':10s} | {'-30°':8s} | {'-15°':8s} | {'+15°':8s} | {'+30°':8s} | {'Media |ang|':12s}")
    print("-" * 65)

    blocks = [f"Block_{i}" for i in range(1, 7)]
    raw_block_means = {}
    for b in blocks:
        row_vals = {}
        for ang in [-30.0, -15.0, 15.0, 30.0]:
            vals = [r["clip_dist"] for r in agg if r["block"] == b and r["angle_deg"] == ang]
            row_vals[ang] = sum(vals) / len(vals)
        mean_all = sum(row_vals.values()) / 4.0
        raw_block_means[b] = mean_all
        print(f"{b:10s} | {row_vals[-30.0]:8.4f} | {row_vals[-15.0]:8.4f} | {row_vals[15.0]:8.4f} | {row_vals[30.0]:8.4f} | {mean_all:12.4f}")

    # ==============================================================================
    # LAVORO C: REGRESSIONE DI CLIP_DIST SU D E ANALISI DEI RESIDUI
    # ==============================================================================
    print("\n" + "="*80)
    print("LAVORO C: REGRESSIONE DI CLIP_DIST SU DISPLACEMENT")
    print("="*80)

    # Prepariamo i dataset per la regressione
    # 1. Su D_modello
    # 2. Su D_blocco
    x_dmodel = []
    x_dblock = []
    y_clip = []
    metadata = []

    for r in agg:
        b = r["block"]
        ang = r["angle_deg"]
        d_info = disp[(b, "rotX", ang)]
        x_dmodel.append(d_info["d_model"])
        x_dblock.append(d_info["d_block"])
        y_clip.append(r["clip_dist"])
        metadata.append(r)

    # 1. Regressione su D_modello
    slope_m, incpt_m, r2_m, res_m = linear_regression(x_dmodel, y_clip)
    print(f"\n[1] Regressione su D_modello (n = 168 osservazioni prompt-aggregate):")
    print(f"    Pendenza:  {slope_m:.4f}")
    print(f"    Intercetta: {incpt_m:.4f}")
    print(f"    R^2:        {r2_m:.4f} ({r2_m*100:.2f}% di varianza spiegata da D_modello)")

    # 2. Regressione su D_blocco
    slope_b, incpt_b, r2_b, res_b = linear_regression(x_dblock, y_clip)
    print(f"\n[2] Regressione su D_blocco (n = 168 osservazioni prompt-aggregate):")
    print(f"    Pendenza:  {slope_b:.4f}")
    print(f"    Intercetta: {incpt_b:.4f}")
    print(f"    R^2:        {r2_b:.4f} ({r2_b*100:.2f}% di varianza spiegata da D_blocco)")

    # Aggiungi i residui ai record
    for i, r in enumerate(metadata):
        r["res_dmodel"] = res_m[i]
        r["res_dblock"] = res_b[i]

    # Medie dei residui per blocco
    print("\n" + "-"*80)
    print("PROFILO DEI RESIDUI MEDI PER BLOCCO")
    print("-" * 80)
    print(f"{'Blocco':10s} | {'CLIP-Dist grezzo':18s} | {'Residuo (su D_model)':22s} | {'Residuo (su D_block)':22s}")
    print("-" * 80)

    res_block_dmodel = {}
    res_block_dblock = {}
    for b in blocks:
        b_res_m = [r["res_dmodel"] for r in metadata if r["block"] == b]
        b_res_b = [r["res_dblock"] for r in metadata if r["block"] == b]
        mean_res_m = sum(b_res_m) / len(b_res_m)
        mean_res_b = sum(b_res_b) / len(b_res_b)
        res_block_dmodel[b] = mean_res_m
        res_block_dblock[b] = mean_res_b
        print(f"{b:10s} | {raw_block_means[b]:18.4f} | {mean_res_m:+22.4f} | {mean_res_b:+22.4f}")

    # Contrasto per prompt: Estremi (1 & 6) vs Centrali (2, 3, 4, 5)
    # Per ciascun prompt p:
    # contrast_p = mean(residui estremi) - mean(residui centrali)
    prompt_contrasts_dmodel = []
    prompt_contrasts_dblock = []
    prompt_contrasts_raw = []

    print("\n" + "-"*80)
    print("CONTRASTO ESTREMI (1 & 6) vs CENTRALI (2, 3, 4, 5) PER PROMPT")
    print("-" * 80)
    print(f"{'Prompt ID':25s} | {'Δ Grezzo':12s} | {'Δ Residui (D_model)':20s} | {'Δ Residui (D_block)':20s}")
    print("-" * 80)

    for p in prompts:
        p_ext_raw = [r["clip_dist"] for r in metadata if r["prompt_id"] == p and r["block"] in ["Block_1", "Block_6"]]
        p_cen_raw = [r["clip_dist"] for r in metadata if r["prompt_id"] == p and r["block"] in ["Block_2", "Block_3", "Block_4", "Block_5"]]
        d_raw = (sum(p_ext_raw) / len(p_ext_raw)) - (sum(p_cen_raw) / len(p_cen_raw))
        prompt_contrasts_raw.append(d_raw)

        p_ext_m = [r["res_dmodel"] for r in metadata if r["prompt_id"] == p and r["block"] in ["Block_1", "Block_6"]]
        p_cen_m = [r["res_dmodel"] for r in metadata if r["prompt_id"] == p and r["block"] in ["Block_2", "Block_3", "Block_4", "Block_5"]]
        d_m = (sum(p_ext_m) / len(p_ext_m)) - (sum(p_cen_m) / len(p_cen_m))
        prompt_contrasts_dmodel.append(d_m)

        p_ext_b = [r["res_dblock"] for r in metadata if r["prompt_id"] == p and r["block"] in ["Block_1", "Block_6"]]
        p_cen_b = [r["res_dblock"] for r in metadata if r["prompt_id"] == p and r["block"] in ["Block_2", "Block_3", "Block_4", "Block_5"]]
        d_b = (sum(p_ext_b) / len(p_ext_b)) - (sum(p_cen_b) / len(p_cen_b))
        prompt_contrasts_dblock.append(d_b)

        print(f"{p:25s} | {d_raw:+12.4f} | {d_m:+20.4f} | {d_b:+20.4f}")

    # TEST DI PERMUTAZIONE ESATTA (Sign-flip su 7 prompt)
    print("\n" + "="*80)
    print("TEST DI PERMUTAZIONE ESATTA (Sign-flip, n = 7 prompt, floor = 2/128 = 0.0156)")
    print("="*80)

    obs_raw, p_raw, floor_p, n_perms = exact_sign_flip_test(prompt_contrasts_raw)
    print(f"Contrasto Grezzo (Estremi - Centrali):")
    print(f"  Δ osservato medio:  {obs_raw:+.4f}")
    print(f"  p-value (two-tail): {p_raw:.4f}  [pavimento teorico: {floor_p:.4f}, {n_perms} permutazioni]")
    print(f"  Segni su 7 prompt:  {[1 if x > 0 else -1 for x in prompt_contrasts_raw]}")

    obs_m, p_m, _, _ = exact_sign_flip_test(prompt_contrasts_dmodel)
    print(f"\nContrasto sui Residui da D_modello (Estremi - Centrali):")
    print(f"  Δ residuo medio:    {obs_m:+.4f}")
    print(f"  p-value (two-tail): {p_m:.4f}  [pavimento teorico: {floor_p:.4f}, {n_perms} permutazioni]")
    print(f"  Segni su 7 prompt:  {[1 if x > 0 else -1 for x in prompt_contrasts_dmodel]}")

    obs_b, p_b, _, _ = exact_sign_flip_test(prompt_contrasts_dblock)
    print(f"\nContrasto sui Residui da D_blocco (Estremi - Centrali):")
    print(f"  Δ residuo medio:    {obs_b:+.4f}")
    print(f"  p-value (two-tail): {p_b:.4f}  [pavimento teorico: {floor_p:.4f}, {n_perms} permutazioni]")
    print(f"  Segni su 7 prompt:  {[1 if x > 0 else -1 for x in prompt_contrasts_dblock]}")

    # ==============================================================================
    # LAVORO D: DECOMPOSIZIONE SIMMETRIA / ANTISIMMETRIA
    # ==============================================================================
    print("\n" + "="*80)
    print("LAVORO D: DECOMPOSIZIONE SIMMETRICA / ANTISIMMETRICA (S e A)")
    print("="*80)
    print("Formule:")
    print("  S = (d^+ + d^-) / 2")
    print("  A = (d^+ - d^-) / 2   [o A_diff = d^+ - d^-]")

    # Calcolo per blocco aggregato sui prompt
    print(f"\n{'Blocco':10s} | {'S (15°)':10s} | {'A (15°)':10s} | {'S (30°)':10s} | {'A (30°)':10s} | {'A medio':10s} | {'A_diff medio (pos - neg)':25s}")
    print("-" * 95)

    block_a_diffs = {b: [] for b in blocks}

    for b in blocks:
        # Per ciascun prompt, calcoliamo S e A
        p_A_means = []
        p_A_diffs = []
        s15_list, a15_list = [], []
        s30_list, a30_list = [], []

        for p in prompts:
            # Trova i 4 valori per questo prompt e blocco
            d_m30 = [r["clip_dist"] for r in agg if r["prompt_id"] == p and r["block"] == b and r["angle_deg"] == -30.0][0]
            d_m15 = [r["clip_dist"] for r in agg if r["prompt_id"] == p and r["block"] == b and r["angle_deg"] == -15.0][0]
            d_p15 = [r["clip_dist"] for r in agg if r["prompt_id"] == p and r["block"] == b and r["angle_deg"] == 15.0][0]
            d_p30 = [r["clip_dist"] for r in agg if r["prompt_id"] == p and r["block"] == b and r["angle_deg"] == 30.0][0]

            s15 = (d_p15 + d_m15) / 2.0
            a15 = (d_p15 - d_m15) / 2.0
            s30 = (d_p30 + d_m30) / 2.0
            a30 = (d_p30 - d_m30) / 2.0

            s15_list.append(s15)
            a15_list.append(a15)
            s30_list.append(s30)
            a30_list.append(a30)

            # A medio per questo prompt: media di a15 e a30
            p_A_means.append((a15 + a30) / 2.0)
            # A_diff: medio(+) - medio(-) = ((d_p15 + d_p30)/2) - ((d_m15 + d_m30)/2)
            p_diff = ((d_p15 + d_p30) / 2.0) - ((d_m15 + d_m30) / 2.0)
            p_A_diffs.append(p_diff)

        mean_s15 = sum(s15_list) / len(s15_list)
        mean_a15 = sum(a15_list) / len(a15_list)
        mean_s30 = sum(s30_list) / len(s30_list)
        mean_a30 = sum(a30_list) / len(a30_list)
        mean_a = sum(p_A_means) / len(p_A_means)
        mean_diff = sum(p_A_diffs) / len(p_A_diffs)

        block_a_diffs[b] = p_A_diffs

        print(f"{b:10s} | {mean_s15:10.4f} | {mean_a15:+10.4f} | {mean_s30:10.4f} | {mean_a30:+10.4f} | {mean_a:+10.4f} | {mean_diff:+25.4f}")

    # Test di permutazione su A_diff per ciascun blocco
    print("\n" + "-"*80)
    print("TEST DI PERMUTAZIONE ESATTA SULL'ANTISIMMETRIA A_diff = (pos - neg) [H0: simmetria, A = 0]")
    print("-" * 80)
    print(f"{'Blocco':10s} | {'A_diff medio':14s} | {'p-value':10s} | {'Pavimento':10s} | {'Segni prompt (+/-)':20s}")
    print("-" * 80)

    for b in blocks:
        diffs = block_a_diffs[b]
        obs_a, p_val, floor_p, _ = exact_sign_flip_test(diffs)
        signs_str = str([1 if x > 0 else -1 for x in diffs])
        print(f"{b:10s} | {obs_a:+14.4f} | {p_val:10.4f} | {floor_p:10.4f} | {signs_str:20s}")

    # Test antisimmetria globale (aggregando tutti i 6 blocchi per prompt)
    global_prompt_a = []
    for p_idx in range(7):
        p_val = sum(block_a_diffs[b][p_idx] for b in blocks) / 6.0
        global_prompt_a.append(p_val)

    obs_ga, p_ga, floor_p, _ = exact_sign_flip_test(global_prompt_a)
    print(f"\nAntisimmetria Globale (media dei 6 blocchi per prompt):")
    print(f"  A_diff globale medio: {obs_ga:+.4f}")
    print(f"  p-value (two-tail):   {p_ga:.4f}  [pavimento teorico: {floor_p:.4f}]")
    print(f"  Segni per prompt:     {[1 if x > 0 else -1 for x in global_prompt_a]}")

if __name__ == "__main__":
    main()
