# -*- coding: utf-8 -*-
"""
experiments/extract_triangolo_features.py
=========================================
Estrazione feature per l'esperimento Triangolo (Block_1 vs Block_3 vs Block_6):
- Legge rotations_triangolo_all330_manifest.csv (330 generazioni)
- Riutilizza le feature gia' estratte e congelate per i run 0..209
- Estrae in parallelo tramite style_features e analyze_palette le feature per i run 210..329 (120 nuove immagini)
- Salva i dataset completi unificati a 330 righe:
    rotations_triangolo_style_features.csv
    rotations_triangolo_palette_features.csv
"""

import os
import sys
import csv
import glob
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

_HERE = os.path.dirname(os.path.abspath(__file__))
PILOT_ROOT = os.path.abspath(os.path.join(_HERE, os.pardir))
REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"

data_pilot = os.path.join(PILOT_ROOT, "data")
data_report = os.path.join(REPORT_ROOT, "data")

sys.path.insert(0, _HERE)
from style_features import extract_all_features
from analyze_palette import palette_features

MANIFEST_CSV = os.path.join(data_pilot, "rotations_triangolo_all330_manifest.csv")
RENDERS_DIR = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\rotations_block1_vs_block6"

EXISTING_STYLE_CSV = os.path.join(data_pilot, "rotations_block1_vs_block6_style_features.csv")
EXISTING_PALETTE_CSV = os.path.join(data_pilot, "rotations_block1_vs_block6_palette_features.csv")

def process_single(row):
    fn = row["expected_file"]
    path = os.path.join(RENDERS_DIR, fn)
    if not os.path.exists(path):
        cands = glob.glob(os.path.join(RENDERS_DIR, f"{row['prompt_id']}_s{row['seed']}_{row['condition']}*.png"))
        if cands:
            path = cands[0]
        else:
            return None, None, f"File non trovato: {path}"
    try:
        s_feat = extract_all_features(path)
    except Exception as e:
        return None, None, f"Errore style su {path}: {e}"
    try:
        p_feat = palette_features(path)
    except Exception as e:
        return None, None, f"Errore palette su {path}: {e}"

    meta = {
        "run_idx": row["run_idx"],
        "prompt_id": row["prompt_id"],
        "seed": row["seed"],
        "condition": row["condition"],
        "node_type": row["node_type"],
        "angle": row["angle"],
        "d_target": row["d_target"],
        "image_path": path,
        "file": os.path.basename(path)
    }
    return {**meta, **s_feat}, {**meta, **p_feat}, None

def main():
    print("=== ESTRAZIONE FEATURE ESPERIMENTO TRIANGOLO (330 IMMAGINI) ===")
    with open(MANIFEST_CSV, "r", encoding="utf-8") as f:
        manifest = list(csv.DictReader(f))
    print(f"Righe totali nel manifesto unificato: {len(manifest)}")

    cached_style = {}
    cached_palette = {}
    if os.path.exists(EXISTING_STYLE_CSV) and os.path.exists(EXISTING_PALETTE_CSV):
        with open(EXISTING_STYLE_CSV, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                cached_style[int(r["run_idx"])] = r
        with open(EXISTING_PALETTE_CSV, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                cached_palette[int(r["run_idx"])] = r
        print(f"[Cache] Caricate {len(cached_style)} righe esistenti per style e palette (run 0..209).")

    to_process = [r for r in manifest if int(r["run_idx"]) not in cached_style]
    print(f"Righe nuove da estrarre: {len(to_process)}")

    style_rows = [cached_style[int(r["run_idx"])] for r in manifest if int(r["run_idx"]) in cached_style]
    palette_rows = [cached_palette[int(r["run_idx"])] for r in manifest if int(r["run_idx"]) in cached_palette]
    errors = []

    if to_process:
        max_workers = min(6, os.cpu_count() or 4)
        print(f"Avvio estrazione con {max_workers} worker in parallelo...")
        t0 = time.time()
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_single, r): r for r in to_process}
            cnt = 0
            for f in as_completed(futures):
                s_r, p_r, err = f.result()
                cnt += 1
                if err:
                    errors.append(err)
                    print("[ERRORE]", err)
                else:
                    style_rows.append(s_r)
                    palette_rows.append(p_r)
                if cnt % 20 == 0 or cnt == len(to_process):
                    print(f"  Elaborate nuove: {cnt}/{len(to_process)} ({time.time() - t0:.1f}s)")

    if errors:
        print(f"ATTENZIONE: Riscontrati {len(errors)} errori!")
        sys.exit(1)

    style_rows.sort(key=lambda r: int(r["run_idx"]))
    palette_rows.sort(key=lambda r: int(r["run_idx"]))

    print(f"\nTotale record estratti: style={len(style_rows)}, palette={len(palette_rows)}")
    assert len(style_rows) == 330, f"Attese 330 righe, trovate {len(style_rows)}"
    assert len(palette_rows) == 330, f"Attese 330 righe, trovate {len(palette_rows)}"

    for out_dir in [data_pilot, data_report]:
        os.makedirs(out_dir, exist_ok=True)
        style_p = os.path.join(out_dir, "rotations_triangolo_style_features.csv")
        with open(style_p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(style_rows[0].keys()))
            w.writeheader()
            w.writerows(style_rows)
        print(f"[Salvato] {style_p}")

        pal_p = os.path.join(out_dir, "rotations_triangolo_palette_features.csv")
        with open(pal_p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(palette_rows[0].keys()))
            w.writeheader()
            w.writerows(palette_rows)
        print(f"[Salvato] {pal_p}")

    print("\n[OK] Estrazione feature completata con successo al 100%!")

if __name__ == "__main__":
    main()
