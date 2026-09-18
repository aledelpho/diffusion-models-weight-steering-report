# -*- coding: utf-8 -*-
import os, sys, csv, glob, time
from concurrent.futures import ProcessPoolExecutor, as_completed

_HERE = os.path.dirname(os.path.abspath(__file__))
PILOT_ROOT = os.path.abspath(os.path.join(_HERE, os.pardir))
REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"
data_report = os.path.join(REPORT_ROOT, "data")
data_pilot = os.path.join(PILOT_ROOT, "data")

sys.path.insert(0, _HERE)
from style_features import extract_all_features
from analyze_palette import palette_features

MANIFEST_CSV = os.path.join(data_report, "rotations_block1_vs_block6_manifest.csv")
RENDERS_DIR = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\rotations_block1_vs_block6"

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
    print("=== ESTRAZIONE FEATURE BLOCK_1 VS BLOCK_6 ===")
    with open(MANIFEST_CSV, "r", encoding="utf-8") as f:
        manifest = list(csv.DictReader(f))
    print(f"Righe nel manifesto: {len(manifest)}")
    style_rows, palette_rows, errors = [], [], []
    max_workers = min(6, os.cpu_count() or 4)
    print(f"Avvio estrazione con {max_workers} worker di processo...")
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single, r): r for r in manifest}
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
            if cnt % 25 == 0 or cnt == len(manifest):
                print(f"  Elaborate: {cnt}/{len(manifest)} ({time.time() - t0:.1f}s)")

    if errors:
        print(f"ATTENZIONE: {len(errors)} errori!")
    style_rows.sort(key=lambda r: int(r["run_idx"]))
    palette_rows.sort(key=lambda r: int(r["run_idx"]))

    for out_dir in [data_report, data_pilot]:
        os.makedirs(out_dir, exist_ok=True)
        style_p = os.path.join(out_dir, "rotations_block1_vs_block6_style_features.csv")
        with open(style_p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(style_rows[0].keys()))
            w.writeheader()
            w.writerows(style_rows)
        print(f"[Salvato] {style_p}")

        pal_p = os.path.join(out_dir, "rotations_block1_vs_block6_palette_features.csv")
        with open(pal_p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(palette_rows[0].keys()))
            w.writeheader()
            w.writerows(palette_rows)
        print(f"[Salvato] {pal_p}")

if __name__ == "__main__":
    main()
