# -*- coding: utf-8 -*-
"""
experiments/measure_body_area.py

Misura della frazione di area della carrozzeria e test dell'ipotesi di ingrandimento (Stage 10 · Lavoro B):
1. Disinnesco del confound di saturazione:
   - Settori di tinta (giallo e blu) stimati per ciascun prompt dalle 5 baseline di quello stile.
   - Croma normalizzata per immagine (C / P95(C)) prima della soglia.
   - Soglia fissa (0.35) non ritoccata.
2. Gate di accettazione obbligatorio:
   - Gate 1: Correlazione di Pearson e Spearman fra body_area e colorfulness_hs sulle 280 immagini.
   - Gate 2: Validazione per stile (ispezione di S8_charcoal, S6_pixel, S5_ukiyoe con dichiarazione formale).
   - Gate 3: Secondo proxy indipendente dal colore (componente connessa ad alto contrasto/saliency).
     Verifica di concordanza dell'ordinamento tra proxy.
3. Analisi statistica:
   - Delta appaiato = condizione - baseline (stesso prompt, stesso seed).
   - Unita' di analisi: il prompt (media sui 5 seed).
   - Test esatto sign-flip su stili validi, correzione Holm sulle condizioni.
4. Output: data/stage9_body_area.csv e data/stage9_body_area_results.csv.
"""

import os
import sys
import csv
import cv2
import itertools
import numpy as np
import pandas as pd
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
DATA_DIR = os.path.join(REPORT_ROOT, "data")

MANIFEST_CSV = os.path.join(DATA_DIR, "stage9_images.csv")
STYLE_CSV = os.path.join(DATA_DIR, "style_features_stage9.csv")
OUT_CSV = os.path.join(DATA_DIR, "stage9_body_area.csv")
RESULTS_CSV = os.path.join(DATA_DIR, "stage9_body_area_results.csv")

CONDS = [
    "preset_pos_1x", "preset_pos_2x",
    "blockshuf_neg_1x", "blockshuf_neg_2x",
    "rand_pos_1x", "rand_pos_2x"
]
ALL_CONDS = ["baseline"] + CONDS

CHROMA_NORM_THRESH = 0.35


def compute_cielab_hsv(bgr):
    """Calcola L*, a*, b*, Croma e Tinta (gradi [0, 360]) da BGR."""
    # Converti in float32 scalato [0, 1]
    rgb_f = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    lab = cv2.cvtColor(rgb_f, cv2.COLOR_RGB2Lab)
    L = lab[:, :, 0]
    a = lab[:, :, 1]
    b = lab[:, :, 2]
    chroma = np.sqrt(a ** 2 + b ** 2)
    # Tinta in gradi [0, 360]
    hue_rad = np.arctan2(b, a)
    hue_deg = (np.degrees(hue_rad) + 360.0) % 360.0
    return L, chroma, hue_deg


def calibrate_prompt_hue_sectors(baseline_paths):
    """
    Stima i settori di tinta giallo e blu dalle immagini baseline di un dato stile.
    Isola i pixel cromaticamente salienti (top 15% croma) ed estrae i cluster di tinta.
    """
    all_hues = []
    for p in baseline_paths:
        img = cv2.imread(p)
        if img is None:
            continue
        # Riduci scala per velocizzare calibrazione
        small = cv2.resize(img, (256, 320))
        L, C, h = compute_cielab_hsv(small)
        # Filtra pixel con croma significativa e luminanza media (evita sfondi neri o bianchi)
        c_thresh = np.percentile(C, 85)
        mask = (C >= max(c_thresh, 10.0)) & (L > 20) & (L < 85)
        all_hues.extend(h[mask].tolist())

    if not all_hues:
        # Fallback a settori CIELAB standard se non ci sono pixel salienti (es. monocromatico)
        return (60.0, 110.0), (230.0, 290.0)

    all_hues = np.array(all_hues)
    # Settore Giallo in Lab: attorno a 80-90 gradi (+b*)
    # Settore Blu in Lab: attorno a 250-270 gradi (-b*)
    yellow_candidates = all_hues[(all_hues >= 40) & (all_hues <= 130)]
    blue_candidates = all_hues[(all_hues >= 210) & (all_hues <= 310)]

    if len(yellow_candidates) > 20:
        y_med = float(np.median(yellow_candidates))
        y_sec = (max(0.0, y_med - 30.0), min(360.0, y_med + 30.0))
    else:
        y_sec = (60.0, 115.0)

    if len(blue_candidates) > 20:
        b_med = float(np.median(blue_candidates))
        b_sec = (max(0.0, b_med - 30.0), min(360.0, b_med + 30.0))
    else:
        b_sec = (235.0, 295.0)

    return y_sec, b_sec


def measure_image_body_area(img_path, y_sec, b_sec):
    """
    Calcola:
    1. body_area_frac: frazione pixel maschera tinta normalizzata
    2. contrast_proxy_frac: secondo proxy geometrico indipendente dal colore (componente saliente di contrasto)
    """
    img = cv2.imread(img_path)
    if img is None:
        return np.nan, np.nan

    # Riduci risoluzione a metà per calcolo rapido e coerente
    h_orig, w_orig = img.shape[:2]
    target_w, target_h = 512, 640
    small = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
    total_px = target_w * target_h

    L, C, hue = compute_cielab_hsv(small)

    # Normalizzazione della croma per immagine: C / P95(C)
    p95_c = float(np.percentile(C, 95))
    norm_factor = max(p95_c, 10.0)
    c_norm = C / norm_factor

    # Maschera di tinta
    y_min, y_max = y_sec
    b_min, b_max = b_sec
    is_yellow = (hue >= y_min) & (hue <= y_max)
    is_blue = (hue >= b_min) & (hue <= b_max)

    # Croma normalizzata sopra soglia e luminanza fisiologica
    body_mask = (is_yellow | is_blue) & (c_norm >= CHROMA_NORM_THRESH) & (L >= 15) & (L <= 90)

    # Pulizia morfologica (apertura per rimuovere rumore puntiforme)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    body_mask_clean = cv2.morphologyEx(body_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
    body_area_frac = float(np.sum(body_mask_clean)) / total_px

    # --- SECONDO PROXY: Contrasto e Salienza Indipendente dal Colore ---
    # Converti in scala di grigi, calcola gradiente morfologico ad alto contrasto
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    grad = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
    # Soglia di Otsu per isolare elementi ad alto contrasto
    _, thresh = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Componenti connesse: prendi l'area del bounding box della componente maggiore centrale
    num_labels, labels, stats_cc, centroids = cv2.connectedComponentsWithStats(thresh)
    # Escludi sfondo (label 0)
    if num_labels > 1:
        # Cerca componente maggiore non-sfondo
        areas = stats_cc[1:, cv2.CC_STAT_AREA]
        max_idx = np.argmax(areas) + 1
        comp_area = float(stats_cc[max_idx, cv2.CC_STAT_AREA])
        contrast_proxy_frac = comp_area / total_px
    else:
        contrast_proxy_frac = 0.0

    return body_area_frac, contrast_proxy_frac


def exact_sign_flip_test(deltas):
    """Test di permutazione sign-flip esatto (2^n combinazioni)."""
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
    print("=== MISURA FRAZIONE AREA CARROZZERIA (STAGE 10 · LAVORO B) ===")

    if not os.path.exists(MANIFEST_CSV):
        raise SystemExit(f"Manifesto non trovato: {MANIFEST_CSV}")

    manifest = pd.read_csv(MANIFEST_CSV)
    manifest = manifest[manifest["arm"] == "style_variants"].copy()
    if len(manifest) != 280:
        raise SystemExit(f"Attese 280 immagini, trovate: {len(manifest)}")

    # Risoluzione percorsi fisici
    records = []
    for _, r in manifest.iterrows():
        root = r["renders_root"]
        rel = r["image_path"].replace("/", os.sep)
        path = os.path.join(root, os.path.basename(rel))
        if not os.path.exists(path):
            path = os.path.join(root, rel)
        records.append({
            "prompt_id": r["prompt_id"],
            "prompt_sha1": r["prompt_sha1"],
            "condition": r["cond_name"],
            "seed": int(r["seed"]),
            "file_path": path,
            "filename": os.path.basename(path)
        })
    df_images = pd.DataFrame(records)

    # 1. Calibrazione dei settori di tinta per ciascuno stile sui baseline
    print("[1/4] Calibrazione settori di tinta (giallo/blu) sui render baseline...")
    hue_sectors = {}
    for p_id in df_images["prompt_id"].unique():
        base_paths = df_images[(df_images["prompt_id"] == p_id) & (df_images["condition"] == "baseline")]["file_path"].tolist()
        y_sec, b_sec = calibrate_prompt_hue_sectors(base_paths)
        hue_sectors[p_id] = (y_sec, b_sec)
        print(f"  {p_id:12s}: Giallo [{y_sec[0]:5.1f}°, {y_sec[1]:5.1f}°] | Blu [{b_sec[0]:5.1f}°, {b_sec[1]:5.1f}°]")

    # 2. Calcolo frazione area carrozzeria e secondo proxy per tutte le 280 immagini
    print(f"\n[2/4] Calcolo metriche di area su 280 immagini...")
    body_areas = []
    contrast_proxies = []
    for _, r in df_images.iterrows():
        y_sec, b_sec = hue_sectors[r["prompt_id"]]
        b_area, c_proxy = measure_image_body_area(r["file_path"], y_sec, b_sec)
        body_areas.append(b_area)
        contrast_proxies.append(c_proxy)

    df_images["body_area_frac"] = body_areas
    df_images["contrast_proxy_frac"] = contrast_proxies

    # Carica colorfulness_hs da style_features_stage9.csv per il gate di correlazione
    if os.path.exists(STYLE_CSV):
        df_style = pd.read_csv(STYLE_CSV)
        # Match per filename
        df_images = pd.merge(df_images, df_style[["file", "colorfulness_hs"]],
                             left_on="filename", right_on="file", how="left")
    else:
        df_images["colorfulness_hs"] = np.nan

    # Salva il dataset completo a livello di immagine
    df_images.to_csv(OUT_CSV, index=False)
    print(f"      Dati per immagine salvati in: {OUT_CSV}")

    # =========================================================================
    # GATE DI ACCETTAZIONE OBBLIGATORIO DELLO STRUMENTO
    # =========================================================================
    print("\n" + "=" * 60)
    print(" GATE DI ACCETTAZIONE DELLO STRUMENTO (MANDATORY)")
    print("=" * 60)

    # Gate 1: Correlazione con la saturazione
    if not df_images["colorfulness_hs"].isna().all():
        valid_pairs = df_images.dropna(subset=["body_area_frac", "colorfulness_hs"])
        r_pearson, p_pearson = stats.pearsonr(valid_pairs["body_area_frac"], valid_pairs["colorfulness_hs"])
        r_spearman, p_spearman = stats.spearmanr(valid_pairs["body_area_frac"], valid_pairs["colorfulness_hs"])
        print(f"\n--- GATE 1: CORRELAZIONE CON LA SATURAZIONE (colorfulness_hs) ---")
        print(f"  Pearson r  = {r_pearson:+.4f} (p = {p_pearson:.4e})")
        print(f"  Spearman r = {r_spearman:+.4f} (p = {p_spearman:.4e})")
        if abs(r_spearman) < 0.35:
            gate1_status = "PASS (Indipendente dalla saturazione)"
        else:
            gate1_status = "WARNING / ATTENZIONE (Correlazione presente)"
        print(f"  Esito Gate 1: {gate1_status}")
    else:
        r_pearson, r_spearman = np.nan, np.nan
        gate1_status = "NON MISURATO"

    # Gate 2: Validazione per stile
    print(f"\n--- GATE 2: VALIDAZIONE PER STILE (Ispezione S8, S6, S5) ---")
    # Calcola area media nei baseline per stile
    base_means = df_images[df_images["condition"] == "baseline"].groupby("prompt_id")["body_area_frac"].mean()
    style_validity = {}
    for p_id in sorted(df_images["prompt_id"].unique()):
        bm = base_means.get(p_id, 0.0)
        # Se l'area baseline rilevata e' quasi zero (< 0.005, ovvero < 0.5% del canvas), la metrica cromatica non ha segnale
        if p_id in ["S8_charcoal"]:
            valid = False
            reason = "NON MISURABILE: stile monocromatico B&W dichiarato (assenza di croma)"
        elif bm < 0.005:
            valid = False
            reason = f"NON MISURABILE: segnale cromatico carrozzeria assente o inferiore a 0.5% (area={bm:.4f})"
        else:
            valid = True
            reason = f"VALIDO: segnale cromatico presente (area baseline media = {bm:.4f})"
        style_validity[p_id] = (valid, reason)
        status_tag = "VALIDO" if valid else "NON MISURABILE"
        print(f"  {p_id:14s} [{status_tag:14s}]: {reason}")

    valid_prompts = [p for p, (v, _) in style_validity.items() if v]
    print(f"\n  Stili validi per l'analisi primaria: {len(valid_prompts)}/8 ({', '.join(valid_prompts)})")

    # Gate 3: Secondo proxy indipendente dal colore (Contrasto e Componente Connessa)
    print(f"\n--- GATE 3: SECONDO PROXY INDIPENDENTE (Contrasto / Componente Connessa) ---")
    # Calcola l'ordinamento delle condizioni medio per i due proxy
    cond_order_body = df_images.groupby("condition")["body_area_frac"].mean().sort_values(ascending=False)
    cond_order_proxy = df_images.groupby("condition")["contrast_proxy_frac"].mean().sort_values(ascending=False)

    print("  Ordinamento Condizioni (Proxy 1 - Maschera Tinta Normalizzata):")
    for rank, (c, val) in enumerate(cond_order_body.items(), 1):
        print(f"    {rank}. {c:18s}: {val:.4f}")

    print("\n  Ordinamento Condizioni (Proxy 2 - Componente Connessa di Contrasto):")
    for rank, (c, val) in enumerate(cond_order_proxy.items(), 1):
        print(f"    {rank}. {c:18s}: {val:.4f}")

    # Concordanza di rango tra le condizioni
    common_conds = [c for c in CONDS if c in cond_order_body and c in cond_order_proxy]
    rank1 = [cond_order_body[c] for c in common_conds]
    rank2 = [cond_order_proxy[c] for c in common_conds]
    rho_proxies, p_proxies = stats.spearmanr(rank1, rank2)
    print(f"\n  Concordanza di ordinamento fra Proxy 1 e Proxy 2: Spearman rho = {rho_proxies:+.4f} (p = {p_proxies:.4f})")

    # =========================================================================
    # ANALISI STATISTICA (SUGLI STILI VALIDI)
    # =========================================================================
    print("\n" + "=" * 60)
    print(" ANALISI STATISTICA DI SPOSTAMENTO (SUGLI STILI VALIDI)")
    print("=" * 60)

    # Calcola delta appaiato per (prompt, seed): delta = cond - baseline
    base_sub = df_images[df_images["condition"] == "baseline"].set_index(["prompt_id", "seed"])["body_area_frac"]

    results = []
    raw_p_values = []
    temp_rows = []

    for c in CONDS:
        c_sub = df_images[df_images["condition"] == c].set_index(["prompt_id", "seed"])["body_area_frac"]
        # Unisci sullo stesso prompt e seed
        paired_deltas = c_sub - base_sub

        # Media sui seed per ciascun prompt
        prompt_deltas = []
        for p in valid_prompts:
            p_d = paired_deltas.loc[p].mean()
            prompt_deltas.append(p_d)

        mean_delta = float(np.mean(prompt_deltas))
        p_raw = exact_sign_flip_test(prompt_deltas)
        raw_p_values.append(p_raw)
        temp_rows.append((c, mean_delta, p_raw, prompt_deltas))

    adj_p_values = holm_bonferroni(raw_p_values)

    print("\nCondizione         | Delta Medio | p grezzo (sign-flip) | Holm     | Verdetto")
    print("-------------------|-------------|----------------------|----------|-----------------")
    for (c, mean_delta, p_raw, prompt_deltas), p_adj in zip(temp_rows, adj_p_values):
        verdict = "QUANTIFICATO" if p_adj < 0.05 else "NOT_SIGNIFICANT"
        print(f"{c:18s} | {mean_delta:+11.4f} | {p_raw:20.4f} | {p_adj:8.4f} | {verdict}")

        results.append({
            "condition": c,
            "mean_delta_body_area": round(mean_delta, 6),
            "p_raw_signflip": round(p_raw, 4),
            "p_adj_holm": round(p_adj, 4),
            "valid_prompts_n": len(valid_prompts),
            "total_prompts_n": 8,
            "gate1_spearman_colorfulness": round(r_spearman, 4) if not np.isnan(r_spearman) else None,
            "gate3_proxy_agreement_rho": round(rho_proxies, 4) if not np.isnan(rho_proxies) else None,
            "verdict": verdict
        })

    out_res = pd.DataFrame(results)
    out_res.to_csv(RESULTS_CSV, index=False)
    print(f"\n[OK] Risultati statistici salvati in: {RESULTS_CSV}")


if __name__ == "__main__":
    main()
