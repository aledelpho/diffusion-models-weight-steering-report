#!/usr/bin/env python3
"""
measure_pilot_rotation_directions.py
====================================
Estrae le feature di style_features.py e analyze_palette.py sulle 216 immagini
di rotazione (rotX) e sulle 9 baseline dei benchmark pilota.

Calcola:
1. Vettori di differenza rispetto alla baseline: Δf = f_rot - f_baseline
2. Similarità coseno direzionale tra i blocchi (cos(v_i, v_j))
3. Verifica: la direzione differisce per blocco o cambia solo l'ampiezza?

Output:
- data/pilot_rotations_style_features.csv
- data/pilot_rotations_palette_features.csv
- data/pilot_rotations_directions.csv
"""

import os
import sys
import csv
import glob
import time
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"
DATA_DIR = os.path.join(REPORT_ROOT, "data")
EXPERIMENTS_DIR = os.path.join(REPORT_ROOT, "experiments")
COMFY_OUTPUT = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output"

sys.path.insert(0, EXPERIMENTS_DIR)
from style_features import extract_all_features
from analyze_palette import palette_features

BENCHMARK_REPORTS = [
    ("benchmark_african_scientist", "african_scientist", 4242145),
    ("benchmark_combat_robot", "combat_robot", 4242145),
    ("benchmark_elf_brawler", "elf_brawler", 4242145),
    ("benchmark_flag", "flag", 4242145),
    ("benchmark_preraphaelite_altar", "preraphaelite_altar", 4242145),
    ("benchmark_tiefling", "tiefling", 4242145),
    ("benchmark_tiefling_seed1337", "tiefling", 1337),
    ("benchmark_tiefling_seed42", "tiefling", 42),
    ("benchmark_troll_shaman", "troll_shaman", 4242145),
]

BLOCKS = [f"Block_{i}" for i in range(1, 7)]
ANGLES = [-30.0, -15.0, 15.0, 30.0]

def extract_single_image(args):
    path, meta = args
    try:
        s_feats = extract_all_features(path)
    except Exception as e:
        s_feats = {"error_style": str(e)}

    try:
        p_feats = palette_features(path)
    except Exception as e:
        p_feats = {"error_palette": str(e)}

    return path, meta, s_feats, p_feats

def main():
    print("=== MISURA DI DIREZIONE DELLE ROTAZIONI (STYLE + PALETTE) ===")
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. Raccogli tutti i percorsi delle immagini (216 rotX + 9 baseline)
    tasks = []
    
    # Baseline
    for b_dir, prompt_id, seed in BENCHMARK_REPORTS:
        b_path = os.path.join(COMFY_OUTPUT, b_dir, "00_baseline_00001_.png")
        if not os.path.exists(b_path):
            raise FileNotFoundError(f"Baseline mancante: {b_path}")
        meta = {
            "type": "baseline",
            "report": b_dir,
            "prompt_id": prompt_id,
            "seed": seed,
            "block": "None",
            "rot_kind": "None",
            "angle_deg": 0.0,
        }
        tasks.append((b_path, meta))

    # RotX
    for b_dir, prompt_id, seed in BENCHMARK_REPORTS:
        for b in BLOCKS:
            for ang in ANGLES:
                fn = f"{b}_rotX_{ang:+.1f}_00001_.png"
                # Controlla formattazione nome file (+30.0 o 30.0)
                path = os.path.join(COMFY_OUTPUT, b_dir, "rotations", f"{b}_rotX_{ang:.1f}_00001_.png")
                if not os.path.exists(path):
                    path = os.path.join(COMFY_OUTPUT, b_dir, "rotations", f"{b}_rotX_{ang:+.1f}_00001_.png")
                if not os.path.exists(path):
                    # Cerca per pattern
                    cand = glob.glob(os.path.join(COMFY_OUTPUT, b_dir, "rotations", f"{b}_rotX_*{abs(ang):.1f}*.png"))
                    if cand:
                        path = cand[0]
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Immagine rotazione mancante: {b_dir}/rotations/{b}_rotX_{ang}")

                meta = {
                    "type": "rotX",
                    "report": b_dir,
                    "prompt_id": prompt_id,
                    "seed": seed,
                    "block": b,
                    "rot_kind": "rotX",
                    "angle_deg": ang,
                }
                tasks.append((path, meta))

    print(f"Immagini da processare: {len(tasks)} (9 baseline + 216 rotX)")

    # 2. Estrazione parallela
    t0 = time.time()
    style_rows = []
    palette_rows = []

    print("Avvio estrazione con ProcessPoolExecutor...")
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as executor:
        futures = {executor.submit(extract_single_image, t): t for t in tasks}
        done = 0
        for fut in as_completed(futures):
            path, meta, s_feats, p_feats = fut.result()
            
            s_row = dict(meta)
            s_row["image_path"] = path
            s_row.update(s_feats)
            style_rows.append(s_row)

            p_row = dict(meta)
            p_row["image_path"] = path
            p_row.update(p_feats)
            palette_rows.append(p_row)

            done += 1
            if done % 25 == 0 or done == len(tasks):
                print(f"  Completate {done}/{len(tasks)} immagini ({time.time()-t0:.1f}s)")

    # Salva i due CSV delle feature
    df_style = pd.DataFrame(style_rows)
    df_palette = pd.DataFrame(palette_rows)

    style_csv = os.path.join(DATA_DIR, "pilot_rotations_style_features.csv")
    palette_csv = os.path.join(DATA_DIR, "pilot_rotations_palette_features.csv")
    df_style.to_csv(style_csv, index=False)
    df_palette.to_csv(palette_csv, index=False)
    print(f"\n[OK] Salvato {style_csv} ({len(df_style)} righe)")
    print(f"[OK] Salvato {palette_csv} ({len(df_palette)} righe)")

    # 3. Analisi delle Direzioni: Delta rispetto a Baseline
    # Seleziona feature numeriche rilevanti da style_features
    # Linework: edge_coverage_pct, mean_line_width_px, line_contrast
    # Shadows: shadow_hardness_kurtosis, shadow_edge_sharpness
    # Texture: glcm_contrast, glcm_homogeneity, lbp_entropy
    # Colore: colorfulness_hasler, saturation_std, hue_entropy
    # Frequenze: hf_power_ratio, spectral_slope
    style_num_cols = [
        c for c in df_style.columns
        if c not in ["type", "report", "prompt_id", "seed", "block", "rot_kind", "angle_deg", "image_path"]
        and pd.api.types.is_numeric_dtype(df_style[c])
    ]

    palette_num_cols = [
        c for c in df_palette.columns
        if c not in ["type", "report", "prompt_id", "seed", "block", "rot_kind", "angle_deg", "image_path", "file", "condition", "prompt_dir", "prompt_sha1", "rel_path"]
        and pd.api.types.is_numeric_dtype(df_palette[c])
        and not c.endswith("_hex")
    ]

    all_num_cols = ["s_" + c for c in style_num_cols] + ["p_" + c for c in palette_num_cols]

    # Crea un unico DataFrame unificato
    df_merged = df_style[["type", "report", "prompt_id", "seed", "block", "rot_kind", "angle_deg", "image_path"]].copy()
    for c in style_num_cols:
        df_merged["s_" + c] = df_style[c]
    for c in palette_num_cols:
        df_merged["p_" + c] = df_palette[c]

    # Z-score globale delle colonne per renderle adimensionali
    df_norm = df_merged.copy()
    for col in all_num_cols:
        col_std = df_merged[col].std()
        col_mean = df_merged[col].mean()
        df_norm[col] = (df_merged[col] - col_mean) / (col_std if col_std > 1e-9 else 1.0)

    # Calcola il delta per ogni rotX rispetto alla baseline dello stesso report (stesso prompt_id e seed)
    baseline_lookup = {}
    for idx, row in df_norm[df_norm["type"] == "baseline"].iterrows():
        key = (row["prompt_id"], row["seed"])
        baseline_lookup[key] = row[all_num_cols].values.astype(float)

    rot_deltas = []
    for idx, row in df_norm[df_norm["type"] == "rotX"].iterrows():
        key = (row["prompt_id"], row["seed"])
        base_vec = baseline_lookup[key]
        rot_vec = row[all_num_cols].values.astype(float)
        delta = rot_vec - base_vec

        delta_norm = float(np.linalg.norm(delta))
        record = {
            "report": row["report"],
            "prompt_id": row["prompt_id"],
            "seed": row["seed"],
            "block": row["block"],
            "angle_deg": row["angle_deg"],
            "delta_l2_norm": delta_norm,
        }
        for i, col in enumerate(all_num_cols):
            record["delta_" + col] = delta[i]
        rot_deltas.append(record)

    df_deltas = pd.DataFrame(rot_deltas)

    # Calcola il vettore medio di direzione per blocco (aggregando prima per prompt, poi per blocco)
    delta_cols = [c for c in df_deltas.columns if c.startswith("delta_") and c != "delta_l2_norm"]

    # Media per (prompt_id, block)
    prompt_block_dir = df_deltas.groupby(["prompt_id", "block"])[delta_cols].mean().reset_index()
    # Media globale per block
    block_dir = prompt_block_dir.groupby("block")[delta_cols].mean()

    # Matrice di similarità coseno tra i vettori di direzione dei blocchi
    cos_sim_matrix = np.zeros((len(BLOCKS), len(BLOCKS)))
    for i, b1 in enumerate(BLOCKS):
        v1 = block_dir.loc[b1].values
        norm1 = np.linalg.norm(v1)
        for j, b2 in enumerate(BLOCKS):
            v2 = block_dir.loc[b2].values
            norm2 = np.linalg.norm(v2)
            cos_sim_matrix[i, j] = np.dot(v1, v2) / (norm1 * norm2) if norm1 > 1e-9 and norm2 > 1e-9 else 0.0

    print("\n" + "="*80)
    print("MATRICE DI SIMILARITÀ COSENO DIREZIONALE TRA I BLOCCHI cos(Δv_i, Δv_j)")
    print("="*80)
    header = f"{'':10s} | " + " | ".join(f"{b:8s}" for b in BLOCKS)
    print(header)
    print("-" * len(header))
    for i, b1 in enumerate(BLOCKS):
        row_str = f"{b1:10s} | " + " | ".join(f"{cos_sim_matrix[i, j]:+8.4f}" for j in range(len(BLOCKS)))
        print(row_str)

    # L2 norm medio per blocco (ampiezza dello spostamento nello spazio di stile/palette)
    print("\n" + "-"*80)
    print("AMPIEZZA MEDIA DELLO SPOSTAMENTO MULTIDIMENSIONALE ||Δf|| PER BLOCCO")
    print("-" * 80)
    mean_amp_per_block = df_deltas.groupby("block")["delta_l2_norm"].mean()
    for b in BLOCKS:
        print(f"  {b:10s}: ||Δf|| = {mean_amp_per_block[b]:.4f}")

    # Salva tabella delle direzioni
    dir_rows = []
    for i, b1 in enumerate(BLOCKS):
        row_dict = {"block": b1, "mean_l2_norm": mean_amp_per_block[b1]}
        for j, b2 in enumerate(BLOCKS):
            row_dict[f"cos_sim_{b2}"] = cos_sim_matrix[i, j]
        dir_rows.append(row_dict)

    df_dir_out = pd.DataFrame(dir_rows)
    dir_csv = os.path.join(DATA_DIR, "pilot_rotations_directions.csv")
    df_dir_out.to_csv(dir_csv, index=False)
    print(f"\n[OK] Salvato {dir_csv}")

if __name__ == "__main__":
    main()
