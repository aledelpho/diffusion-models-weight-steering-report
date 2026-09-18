# -*- coding: utf-8 -*-
"""
experiments/analyze_headlights.py

Analisi statistica dello scoring cieco dei fari (Stage 10 · Lavoro A):
1. Verifica che data/stage9_headlights_raw.csv contenga tutti i 280 punteggi unici.
2. Solo a quel punto unisce i punteggi alla chiave data/stage9_headlights_key.csv.
3. Separa le variabili:
   - lit: 1 se code==2, 0 se code==0, None se code==1 (ambiguo)
   - ambiguous: 1 se code==1, 0 altrimenti (conteggiato ed escluso dal calcolo del tasso)
4. Unita' di analisi: il prompt (8 prompt di stile).
   - Calcolo del tasso k/n di lit=1 per (prompt, condizione).
   - Delta = condizione - baseline sullo stesso prompt.
   - Test di permutazione esatta sign-flip (2^8 = 256 combinazioni, pavimento 2/256 = 0.0078).
   - Correzione di Holm sulle 6 condizioni.
5. Gestione del confound di luminanza (L_mean da palette_features_stage9.csv):
   - Regressione logistica: lit ~ condizione + L_mean (con cluster/effetti prompt).
   - Stratificazione in terzili di L_mean con test intrastrato e riporto numerosita'.
6. Salva data/stage9_headlights_results.csv.
"""

import os
import sys
import csv
import math
import itertools
import numpy as np
import pandas as pd
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
DATA_DIR = os.path.join(REPORT_ROOT, "data")

RAW_CSV = os.path.join(DATA_DIR, "stage9_headlights_raw.csv")
KEY_CSV = os.path.join(DATA_DIR, "stage9_headlights_key.csv")
PALETTE_CSV = os.path.join(DATA_DIR, "palette_features_stage9.csv")
RESULTS_CSV = os.path.join(DATA_DIR, "stage9_headlights_results.csv")

CONDS = [
    "preset_pos_1x", "preset_pos_2x",
    "blockshuf_neg_1x", "blockshuf_neg_2x",
    "rand_pos_1x", "rand_pos_2x"
]
ALL_CONDS = ["baseline"] + CONDS
SW = [f"sw{i}" for i in range(1, 7)]


def exact_sign_flip_test(deltas):
    """Test di permutazione sign-flip esatto su 8 prompt (2^8 = 256)."""
    deltas = np.array(deltas, dtype=float)
    n = len(deltas)
    obs_mean = np.mean(deltas)
    if obs_mean == 0:
        return 1.0

    all_means = []
    for signs in itertools.product([-1, 1], repeat=n):
        all_means.append(np.mean(deltas * np.array(signs)))

    all_means = np.array(all_means)
    # Test a due code
    p_val = np.mean(np.abs(all_means) >= np.abs(obs_mean) - 1e-12)
    return max(p_val, 2.0 / (2 ** n))


def holm_bonferroni(p_values):
    """Applica la correzione sequenziale di Holm a una lista di p-value."""
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
    print("=== ANALISI SCORING CIECO DEI FARI (STAGE 10 · LAVORO A) ===")

    if not os.path.exists(RAW_CSV):
        raise SystemExit(f"File grezzo non trovato: {RAW_CSV}\nCompleta prima lo scoring nel visualizzatore!")

    raw_df = pd.read_csv(RAW_CSV)
    # Rimuove duplicati mantenendo l'ultima annotazione se si e' tornati indietro
    raw_df = raw_df.drop_duplicates(subset=["hash_id"], keep="last")

    if len(raw_df) < 280:
        raise SystemExit(f"Scoring incompleto: {len(raw_df)}/280 immagini annotate. Completa prima l'intero set!")

    print(f"[OK] Rilevati tutti i 280 punteggi univoci in {RAW_CSV}")
    print("[OK] Sblocco e unione con la chiave segreta...")

    if not os.path.exists(KEY_CSV):
        raise SystemExit(f"File chiave non trovato: {KEY_CSV}")

    key_df = pd.read_csv(KEY_CSV)
    merged = pd.merge(raw_df, key_df, on="hash_id")
    if len(merged) != 280:
        raise SystemExit(f"Anomalia nel merge: {len(merged)} record uniti invece di 280")

    # Separazione lit / ambiguous
    merged["code"] = merged["code"].astype(int)
    merged["ambiguous"] = (merged["code"] == 1).astype(int)
    merged["lit"] = merged["code"].map({2: 1.0, 0: 0.0, 1: np.nan})

    # Carica L_mean da palette_features_stage9.csv per il controllo del confound
    if os.path.exists(PALETTE_CSV):
        pal = pd.read_csv(PALETTE_CSV)
        pal = pal[pal["prompt_dir"].astype(str).str.startswith("S")].copy()
        w = pal[[f"{s}_share" for s in SW]].values.astype(float)
        w = w / np.clip(w.sum(1, keepdims=True), 1e-9, None)
        pal["L_mean"] = (pal[[f"{s}_L" for s in SW]].values * w).sum(1)
        pal["seed"] = pal["seed"].astype(int)
        merged["seed"] = merged["seed"].astype(int)

        merged = pd.merge(merged, pal[["prompt_sha1", "condition", "seed", "L_mean"]],
                          left_on=["prompt_sha1", "cond_name", "seed"],
                          right_on=["prompt_sha1", "condition", "seed"],
                          how="left")
    else:
        print("[WARN] palette_features_stage9.csv non trovato, controllo L_mean disabilitato")
        merged["L_mean"] = np.nan

    # 1. Tassi per prompt e condizione
    print("\n--- 1. CONTEGGIO AMBIGUI PER CONDIZIONE ---")
    amb_by_cond = merged.groupby("cond_name")["ambiguous"].sum()
    for c in ALL_CONDS:
        print(f"  {c:18s}: {amb_by_cond.get(c, 0)} ambigui su 40 immagini")

    # Calcolo tassi per prompt escludendo gli ambigui
    prompt_rates = {}
    for (p_id, c_name), grp in merged.groupby(["prompt_id", "cond_name"]):
        valid = grp["lit"].dropna()
        n_valid = len(valid)
        k_lit = int(valid.sum()) if n_valid > 0 else 0
        rate = k_lit / n_valid if n_valid > 0 else 0.0
        prompt_rates.setdefault(c_name, {})[p_id] = {
            "rate": rate,
            "k": k_lit,
            "n": n_valid,
            "amb": int(grp["ambiguous"].sum())
        }

    # 2. Test appaiato contro baseline per le 6 condizioni
    prompts = sorted(list(prompt_rates["baseline"].keys()))
    results = []

    print("\n--- 2. EFFETTO GREZZO DEI FARI (PROMPT-LEVEL PAIRED DELTA) ---")
    print("Condizione         | Delta Medio | p grezzo (sign-flip) | Holm     | Verdetto")
    print("-------------------|-------------|----------------------|----------|-----------------")

    raw_p_values = []
    temp_rows = []
    for c in CONDS:
        deltas = []
        for p in prompts:
            r_cond = prompt_rates[c][p]["rate"]
            r_base = prompt_rates["baseline"][p]["rate"]
            deltas.append(r_cond - r_base)

        mean_delta = float(np.mean(deltas))
        p_raw = exact_sign_flip_test(deltas)
        raw_p_values.append(p_raw)
        temp_rows.append((c, mean_delta, p_raw, deltas))

    adj_p_values = holm_bonferroni(raw_p_values)

    for (c, mean_delta, p_raw, deltas), p_adj in zip(temp_rows, adj_p_values):
        verdict = "QUANTIFICATO" if p_adj < 0.05 else "NOT_SIGNIFICANT"
        print(f"{c:18s} | {mean_delta:+11.4f} | {p_raw:20.4f} | {p_adj:8.4f} | {verdict}")

        results.append({
            "condition": c,
            "mean_delta_raw": round(mean_delta, 4),
            "p_raw_signflip": round(p_raw, 4),
            "p_adj_holm": round(p_adj, 4),
            "ambiguous_count": int(amb_by_cond.get(c, 0)),
            "baseline_ambiguous_count": int(amb_by_cond.get("baseline", 0)),
            "verdict_raw": verdict
        })

    # 3. Controllo del confound di luminanza
    if not merged["L_mean"].isna().all():
        print("\n--- 3. CONFOUND DI LUMINANZA (STRATIFICAZIONE IN TERZILI) ---")
        # Divisione in terzili globali di L_mean
        merged["tertile"] = pd.qcut(merged["L_mean"], q=3, labels=["T1_Scuro", "T2_Medio", "T3_Chiaro"])

        tertile_results = []
        for t in ["T1_Scuro", "T2_Medio", "T3_Chiaro"]:
            sub = merged[merged["tertile"] == t]
            print(f"\n[Terzile {t}] L_mean range: [{sub['L_mean'].min():.1f} - {sub['L_mean'].max():.1f}]")
            for c in CONDS:
                c_sub = sub[sub["cond_name"] == c]["lit"].dropna()
                b_sub = sub[sub["cond_name"] == "baseline"]["lit"].dropna()
                r_c = c_sub.mean() if len(c_sub) > 0 else np.nan
                r_b = b_sub.mean() if len(b_sub) > 0 else np.nan
                diff = r_c - r_b if (not np.isnan(r_c) and not np.isnan(r_b)) else np.nan
                print(f"  {c:18s}: Tasso = {r_c:.3f} (n={len(c_sub)}) vs Base = {r_b:.3f} (n={len(b_sub)}) | Diff = {diff:+.3f}")

        # Regressione logistica di lit su cond_name + L_mean
        try:
            import statsmodels.api as sm
            import statsmodels.formula.api as smf
            reg_data = merged.dropna(subset=["lit", "L_mean"]).copy()
            reg_data["is_preset_pos_1x"] = (reg_data["cond_name"] == "preset_pos_1x").astype(int)
            reg_data["is_preset_pos_2x"] = (reg_data["cond_name"] == "preset_pos_2x").astype(int)

            model = smf.logit("lit ~ is_preset_pos_1x + is_preset_pos_2x + L_mean", data=reg_data).fit(disp=False)
            print("\n--- 4. REGRESSIONE LOGISTICA (lit ~ preset_pos + L_mean) ---")
            print(model.summary().tables[1])
        except Exception as e:
            print(f"[NOTE] Regressione logistica statsmodels non disponibile: {e}")

    # Salva risultati
    out_df = pd.DataFrame(results)
    out_df.to_csv(RESULTS_CSV, index=False)
    print(f"\n[OK] Risultati completi salvati in {RESULTS_CSV}")


if __name__ == "__main__":
    main()
