# -*- coding: utf-8 -*-
"""
experiments/analyze_bbox_groundtruth.py

Analisi statistica delle annotazioni umane a 4 punti estremi (Ground Truth Cieca):
1. Carica data/stage9_bbox_raw.csv (280 annotazioni umane).
2. Unisce con la chiave sigillata data/stage9_headlights_key.csv.
3. Calcola per ciascuna immagine:
   - Larghezza (W = right_x - left_x)
   - Altezza (H = bottom_y - top_y)
   - Area Bounding Box (W * H) e frazione di canvas (Area / (1024 * 1280))
4. Analisi appaiata rispetto alla baseline dello stesso prompt e seed:
   - Delta = condizione - baseline
   - Unita' di analisi: il prompt (media sui 5 seed)
   - Test esatto sign-flip su 8 prompt
   - Correzione sequenziale di Holm sulle condizioni
5. Confronto quantitativo con la metrica automatica (stage9_body_area.csv):
   - Correlazione fra BBox umano e maschera algoritmica di tinta.
   - Quantificazione dell'errore di segmentazione algoritmica.
6. Salva data/stage9_bbox_results.csv.
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

RAW_BBOX_CSV = os.path.join(DATA_DIR, "stage9_bbox_raw.csv")
KEY_CSV = os.path.join(DATA_DIR, "stage9_headlights_key.csv")
ALGO_CSV = os.path.join(DATA_DIR, "stage9_body_area.csv")
RESULTS_CSV = os.path.join(DATA_DIR, "stage9_bbox_results.csv")

CONDS = [
    "preset_pos_1x", "preset_pos_2x",
    "blockshuf_neg_1x", "blockshuf_neg_2x",
    "rand_pos_1x", "rand_pos_2x"
]
ALL_CONDS = ["baseline"] + CONDS


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
    print("=== ANALISI GROUND TRUTH BBOX 4 PUNTI (STAGE 10 · CAR SIZE) ===")

    if not os.path.exists(RAW_BBOX_CSV):
        raise SystemExit(f"File non trovato: {RAW_BBOX_CSV}\nCompleta prima l'annotazione in viewer/bbox_annotator.html!")

    raw = pd.read_csv(RAW_BBOX_CSV)
    raw = raw.drop_duplicates(subset=["hash_id"], keep="last")

    if len(raw) < 280:
        raise SystemExit(f"Annotazione parziale: {len(raw)}/280 immagini registrate. Completa l'intero set!")

    print(f"[OK] Rilevate 280 annotazioni umane univoche in {RAW_BBOX_CSV}")

    if not os.path.exists(KEY_CSV):
        raise SystemExit(f"File chiave non trovato: {KEY_CSV}")

    key = pd.read_csv(KEY_CSV)
    merged = pd.merge(raw, key, on="hash_id")
    if len(merged) != 280:
        raise SystemExit(f"Errore nel merge: {len(merged)} record invece di 280")

    # Verifica dimensioni naturali e area
    merged["bbox_area"] = merged["bbox_width"] * merged["bbox_height"]
    total_canvas_px = 1024 * 1280
    merged["bbox_area_frac"] = merged["bbox_area"] / total_canvas_px

    # Carica la metrica automatica per confronto se disponibile
    if os.path.exists(ALGO_CSV):
        algo = pd.read_csv(ALGO_CSV)
        merged = pd.merge(merged, algo[["filename", "body_area_frac", "contrast_proxy_frac"]],
                          left_on="src_path", right_on="filename", how="left")
        r_algo, p_algo = stats.spearmanr(merged["bbox_area_frac"], merged["body_area_frac"])
        print(f"\n--- CONFRONTO HUMAN GROUND TRUTH VS ALGORITMO ---")
        print(f"  Correlazione di Spearman fra BBox umano e maschera tinta algoritmica: rho = {r_algo:+.4f} (p = {p_algo:.4e})")

    # 1. Medie assolute di BBox Area per condizione
    print("\n--- 1. AREA MEDIA BOUNDING BOX PER CONDIZIONE ---")
    cond_stats = merged.groupby("cond_name").agg(
        area_frac_mean=("bbox_area_frac", "mean"),
        width_mean=("bbox_width", "mean"),
        height_mean=("bbox_height", "mean")
    )
    for c in ALL_CONDS:
        if c in cond_stats.index:
            row = cond_stats.loc[c]
            print(f"  {c:18s}: Area = {row['area_frac_mean']*100:5.2f}% canvas | W = {row['width_mean']:6.1f} px | H = {row['height_mean']:6.1f} px")

    # 2. Test appaiato prompt-level contro baseline
    base_sub = merged[merged["cond_name"] == "baseline"].set_index(["prompt_id", "seed"])["bbox_area_frac"]

    results = []
    raw_p_values = []
    temp_rows = []
    prompts = sorted(merged["prompt_id"].unique())

    for c in CONDS:
        c_sub = merged[merged["cond_name"] == c].set_index(["prompt_id", "seed"])["bbox_area_frac"]
        paired_deltas = c_sub - base_sub

        prompt_deltas = []
        for p in prompts:
            prompt_deltas.append(paired_deltas.loc[p].mean())

        mean_delta = float(np.mean(prompt_deltas))
        p_raw = exact_sign_flip_test(prompt_deltas)
        raw_p_values.append(p_raw)
        temp_rows.append((c, mean_delta, p_raw, prompt_deltas))

    adj_p_values = holm_bonferroni(raw_p_values)

    print("\n--- 2. EFFETTO DI INGRANDIMENTO SULLA GROUND TRUTH UMANA (PAIRED DELTA) ---")
    print("Condizione         | Delta BBox Area | p grezzo (sign-flip) | Holm     | Verdetto")
    print("-------------------|-----------------|----------------------|----------|-----------------")
    for (c, mean_delta, p_raw, p_deltas), p_adj in zip(temp_rows, adj_p_values):
        verdict = "QUANTIFICATO (INGRANDITO)" if (p_adj < 0.05 and mean_delta > 0) else ("QUANTIFICATO (RIDOTTO)" if (p_adj < 0.05 and mean_delta < 0) else "NOT_SIGNIFICANT")
        print(f"{c:18s} | {mean_delta*100:+14.3f}% | {p_raw:20.4f} | {p_adj:8.4f} | {verdict}")

        results.append({
            "condition": c,
            "mean_delta_bbox_pct": round(mean_delta * 100, 3),
            "p_raw_signflip": round(p_raw, 4),
            "p_adj_holm": round(p_adj, 4),
            "verdict": verdict
        })

    out_df = pd.DataFrame(results)
    out_df.to_csv(RESULTS_CSV, index=False)
    print(f"\n[OK] Risultati ground truth salvati in: {RESULTS_CSV}")


if __name__ == "__main__":
    main()
