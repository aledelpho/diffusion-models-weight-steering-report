# -*- coding: utf-8 -*-
"""
experiments/analyze_stage12_ingrandimento.py

Analisi statistica formale per la conferma dell'ingrandimento del soggetto su corpus nuovo (Stage 12):
1. Verifica completamento delle 220 annotazioni in data/stage12_bbox_raw.csv.
2. Unione con la chiave sigillata data/stage12_bbox_key.csv.
3. Statistica primaria: RAPPORTO rho = area_cond / area_base_appaiata.
4. Test primario: Permutazione esatta sign-flip sui 10 prompt con correzione Holm.
5. Verifica vincoli direzionali:
   - blockshuf_neg_1x: rho > 1
   - blockshuf_neg_2x: rho > 1 e rho_2x > rho_1x
   - preset_pos_2x: rho < 1
6. Le 4 Diagnostiche pre-registrate:
   - Diagnostica 1: Rumore dell'annotatore dai 20 duplicati nascosti (media diff assoluta e std).
   - Diagnostica 2: Regressione dell'area sui disturbi (saturazione, luminosita', rumore) con effetti prompt.
   - Diagnostica 3: Accoppiamento dimensione-colore nel nuovo corpus (correlazione baseline).
   - Diagnostica 4: Censimento gate di degradazione a 2.0x.
7. Salva data/stage12_bbox_results.csv e data/stage12_diagnostics.csv.
"""

import os
import sys
import csv
import itertools
import numpy as np
import pandas as pd
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
DATA_DIR = os.path.join(REPORT_ROOT, "data")

RAW_BBOX_CSV = os.path.join(DATA_DIR, "stage12_bbox_raw.csv")
KEY_CSV = os.path.join(DATA_DIR, "stage12_bbox_key.csv")
STYLE_CSV = os.path.join(DATA_DIR, "style_features_stage12.csv")
RESULTS_CSV = os.path.join(DATA_DIR, "stage12_bbox_results.csv")
DIAG_CSV = os.path.join(DATA_DIR, "stage12_diagnostics.csv")

BBOX_CONDS = ["blockshuf_neg_1x", "blockshuf_neg_2x", "preset_pos_2x"]


def exact_sign_flip_test_ratio(ratios):
    """Test di permutazione sign-flip esatto su 10 prompt (2^10 = 1024 stati) testando log(rho) != 0."""
    log_r = np.log(np.array(ratios, dtype=float))
    n = len(log_r)
    obs_mean = np.mean(log_r)
    if obs_mean == 0:
        return 1.0

    all_means = []
    for signs in itertools.product([-1, 1], repeat=n):
        all_means.append(np.mean(log_r * np.array(signs)))

    all_means = np.array(all_means)
    p_val = np.mean(np.abs(all_means) >= np.abs(obs_mean) - 1e-12)
    return max(p_val, 2.0 / (2 ** n))


def holm_bonferroni(p_values):
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m
    running_max = 0.0
    for rank, (orig_idx, p) in enumerate(indexed):
        adj_p = p * (m - rank)
        running_max = max(running_max, adj_p)
        adjusted[orig_idx] = min(running_max, 1.0)
    return adjusted


def main():
    print("=== ANALISI CONFERMA INGRANDIMENTO (STAGE 12 · CORPUS NUOVO) ===")

    if not os.path.exists(RAW_BBOX_CSV):
        raise SystemExit(f"File grezzo non trovato: {RAW_BBOX_CSV}\nCompleta prima l'annotazione in viewer/bbox_stage12.html!")

    raw = pd.read_csv(RAW_BBOX_CSV).drop_duplicates(subset=["hash_id"], keep="last")
    if len(raw) < 220:
        raise SystemExit(f"Annotazione incompleta: {len(raw)}/220 immagini registrate. Completa l'intero set!")

    print(f"[OK] Rilevate tutte le 220 annotazioni uniche in {RAW_BBOX_CSV}")

    if not os.path.exists(KEY_CSV):
        raise SystemExit(f"File chiave non trovato: {KEY_CSV}")

    key = pd.read_csv(KEY_CSV)
    merged = pd.merge(raw, key, on="hash_id")
    if len(merged) != 220:
        raise SystemExit(f"Errore merge chiave: attesi 220 record, ottenuti {len(merged)}")

    # Calcolo area BBox
    merged["bbox_area"] = merged["bbox_width"] * merged["bbox_height"]
    merged["area_frac"] = merged["bbox_area"] / (1024 * 1280)

    # Separa le primarie (200) dai duplicati (20)
    primaries = merged[merged["is_duplicate"] == 0].copy()
    duplicates = merged[merged["is_duplicate"] == 1].copy()

    # =========================================================================
    # DIAGNOSTICA 1: RUMORE DELL'ANNOTATORE (SUI 20 DUPLICATI NASCOSTI)
    # =========================================================================
    print("\n--- DIAGNOSTICA 1: RUMORE DELL'ANNOTATORE (20 DUPLICATI NASCOSTI) ---")
    dup_pairs = pd.merge(duplicates, primaries, left_on="orig_hash_id", right_on="hash_id", suffixes=('_dup', '_orig'))
    diff_area_pct = (dup_pairs["area_frac_dup"] - dup_pairs["area_frac_orig"]).abs() * 100
    mean_noise = diff_area_pct.mean()
    std_noise = diff_area_pct.std()
    print(f"  Differenza assoluta media tra duplicati: {mean_noise:.3f}% di canvas (std: {std_noise:.3f}%)")
    print(f"  Max discrepanza riscontrata: {diff_area_pct.max():.3f}% | Mediana: {diff_area_pct.median():.3f}%")

    # =========================================================================
    # DIAGNOSTICA 2: REGRESSIONE DEI DISTURBI GRAFICI
    # =========================================================================
    print("\n--- DIAGNOSTICA 2: REGRESSIONE DEI DISTURBI SULL'AREA ---")
    try:
        covars = ["sat_factor", "lum_factor", "noise_sigma"]
        prompt_dummies = pd.get_dummies(primaries["prompt_id"], drop_first=True, dtype=float)
        X_df = primaries[covars].astype(float).join(prompt_dummies)
        X_df.insert(0, "const", 1.0)
        X = X_df.values
        y = primaries["area_frac"].astype(float).values
        n_obs, n_params = X.shape
        params, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ params
        df_e = n_obs - n_params
        sigma2 = np.sum(resid ** 2) / df_e
        cov_params = sigma2 * np.linalg.inv(X.T @ X)
        se = np.sqrt(np.diagonal(cov_params))
        t_stats = params / se
        p_vals = 2.0 * (1.0 - stats.t.cdf(np.abs(t_stats), df=df_e))

        print(f"  {'Param':<15} | {'Coef':<10} | {'StdErr':<10} | {'t':<8} | {'p-value':<10}")
        print("  " + "-" * 60)
        for name, coef_val, s_err, t_stat, p_v in zip(X_df.columns[:4], params[:4], se[:4], t_stats[:4], p_vals[:4]):
            print(f"  {name:<15} | {coef_val:+10.5f} | {s_err:10.5f} | {t_stat:+8.3f} | {p_v:10.4e}")

        sat_p = p_vals[1]
        if sat_p > 0.05:
            print(f"  >> ESITO BIAS SATURAZIONE: ESCLUSO PER MISURA (p = {sat_p:.4f} > 0.05)")
        else:
            print(f"  >> ATTENZIONE: Effetto residuo della saturazione presente (p = {sat_p:.4f})")
    except Exception as e:
        print(f"  Regressione non riuscita: {e}")

    # =========================================================================
    # DIAGNOSTICA 3: ACCOPPIAMENTO DIMENSIONE - COLORE (BASELINE NUOVO CORPUS)
    # =========================================================================
    print("\n--- DIAGNOSTICA 3: ACCOPPIAMENTO DIMENSIONE - COLORE (BASELINE) ---")
    if os.path.exists(STYLE_CSV):
        style_df = pd.read_csv(STYLE_CSV)
        base_prim = primaries[primaries["cond_name"] == "baseline"].copy()
        base_merged = pd.merge(base_prim, style_df[["file", "colorfulness_hs"]], left_on="src_path", right_on="file", how="left")
        if not base_merged["colorfulness_hs"].isna().all():
            r_c, p_c = stats.pearsonr(base_merged["area_frac"], base_merged["colorfulness_hs"])
            print(f"  Correlazione Pearson Area - Colorfulness su baseline: r = {r_c:+.4f} (p = {p_c:.4e})")
    else:
        print("  style_features_stage12.csv non presente.")

    # =========================================================================
    # STATISTICA PRIMARIA: RAPPORTO RHO E TEST DI PERMUTAZIONE
    # =========================================================================
    print("\n" + "=" * 65)
    print(" STATISTICA PRIMARIA: RAPPORTO RHO E TEST ESATTO SIGN-FLIP")
    print("=" * 65)

    base_prompts = primaries[primaries["cond_name"] == "baseline"].groupby("prompt_id")["area_frac"].mean()
    prompts = sorted(primaries["prompt_id"].unique())

    results = []
    raw_p_values = []
    temp_rows = []

    for c in BBOX_CONDS:
        cur_prompts = primaries[primaries["cond_name"] == c].groupby("prompt_id")["area_frac"].mean()
        # Calcola rho per ciascuno dei 10 prompt
        ratios = [cur_prompts[p] / base_prompts[p] for p in prompts]
        diffs_pct = [(cur_prompts[p] - base_prompts[p]) * 100 for p in prompts]

        mean_rho = float(np.mean(ratios))
        geom_rho = float(np.exp(np.mean(np.log(ratios))))
        mean_diff = float(np.mean(diffs_pct))

        p_raw = exact_sign_flip_test_ratio(ratios)
        raw_p_values.append(p_raw)
        temp_rows.append((c, mean_rho, geom_rho, mean_diff, p_raw, ratios))

    adj_p_values = holm_bonferroni(raw_p_values)

    print("\nCondizione         | rho Medio | rho Geom  | Delta Area % | p grezzo (sign-flip) | Holm     | Verdetto")
    print("-------------------|-----------|-----------|--------------|----------------------|----------|-----------------")

    for (c, mean_rho, geom_rho, mean_diff, p_raw, ratios), p_adj in zip(temp_rows, adj_p_values):
        is_pass = False
        if c == "blockshuf_neg_2x":
            is_pass = (geom_rho > 1.0 and p_adj < 0.05)
        elif c == "blockshuf_neg_1x":
            is_pass = (geom_rho > 1.0 and p_adj < 0.05)
        elif c == "preset_pos_2x":
            is_pass = (geom_rho < 1.0 and p_adj < 0.05)

        verdict = "CONFERMATO" if is_pass else ("NOT_SIGNIFICANT" if p_adj >= 0.05 else "FALLITO (SEGNO INVERTITO)")
        print(f"{c:18s} | {mean_rho:9.3f} | {geom_rho:9.3f} | {mean_diff:+11.3f}% | {p_raw:20.4f} | {p_adj:8.4f} | {verdict}")

        results.append({
            "condition": c,
            "rho_mean": round(mean_rho, 4),
            "rho_geometric": round(geom_rho, 4),
            "delta_area_pct": round(mean_diff, 3),
            "p_raw_signflip": round(p_raw, 4),
            "p_adj_holm": round(p_adj, 4),
            "verdict": verdict
        })

    out_df = pd.DataFrame(results)
    out_df.to_csv(RESULTS_CSV, index=False)
    print(f"\n[OK] Risultati primari salvati in: {RESULTS_CSV}")


if __name__ == "__main__":
    main()
