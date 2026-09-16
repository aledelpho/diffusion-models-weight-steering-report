# experiments/run_style_features.py
import os
import sys
import csv
import time
import glob
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style_features import extract_all_features, ExtractionConfig

ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
OUT_CSV = os.path.join(ROOT, "style_features.csv")

def collect_paths():
    csvs = [
        os.path.join(ROOT, "stage4_images.csv"),
        os.path.join(ROOT, "stage5_images.csv"),
        os.path.join(ROOT, "stage6_images.csv"),
        os.path.join(ROOT, "stage7_images.csv"),
    ]
    files = set()
    candidate_dirs = [
        r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage7\renders",
        r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage6\renders",
        r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage5\renders",
        r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage4_preset\renders",
        r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage2_family\renders",
    ]
    for c in csvs:
        if os.path.exists(c):
            with open(c, encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    root = r.get("renders_root")
                    img = r.get("image_path")
                    base = r.get("baseline_path")
                    # stage4_images.csv NON ha la colonna renders_root: e' stato
                    # scritto prima che esistesse. Cercando solo per renders_root
                    # le immagini TRATTATE di F1..F4 (preset+-, rand+-, half) non
                    # entravano mai, e la famiglia si riduceva ai soli sei G.
                    # Qui image_path e baseline_path seguono la stessa strada:
                    # prima renders_root se c'e', poi ricerca per basename.
                    for rel in (img, base):
                        if not rel:
                            continue
                        bname = os.path.basename(rel)
                        cand = []
                        if root:
                            cand.append(os.path.join(root, bname))
                        cand += [os.path.join(c, bname) for c in candidate_dirs]
                        for c in cand:
                            c = os.path.normpath(c)
                            if os.path.exists(c):
                                files.add(c)
                                break
    return sorted(list(files))

def worker(path):
    try:
        res = extract_all_features(path)
        return res
    except Exception as e:
        return {"file": os.path.basename(path), "error": str(e)}

def main():
    paths = collect_paths()
    print(f"[StyleFeatures] Raccolte {len(paths)} immagini univoche da Stage 2, 4 e 5.", flush=True)
    if len(paths) < 500:
        print(f"[StyleFeatures] ATTENZIONE: attese ~600 immagini (10 prompt x baseline + 6 condizioni).\n"
              f"    Con {len(paths)} la famiglia si riduce e il test a permutazione perde risoluzione.", flush=True)
    # Carica cache esistente se presente
    existing_records = {}
    if os.path.exists(OUT_CSV):
        try:
            df_old = pd.read_csv(OUT_CSV)
            for r in df_old.to_dict(orient="records"):
                existing_records[r["file"]] = r
        except Exception:
            existing_records = {}

    to_process = [p for p in paths if os.path.basename(p) not in existing_records]
    print(f"[StyleFeatures] Immagini gia' presenti in cache: {len(existing_records)}. Mancanti da elaborare: {len(to_process)}", flush=True)

    t0 = time.time()
    results = list(existing_records.values())
    done = 0
    if to_process:
        with ProcessPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(worker, p): p for p in to_process}
            for fut in as_completed(futures):
                res = fut.result()
                results.append(res)
                done += 1
                if done % 20 == 0 or done == len(to_process):
                    elapsed = time.time() - t0
                    print(f"  [{done}/{len(to_process)}] Elaborate in {elapsed:.1f}s (media {elapsed/done:.2f}s/img)", flush=True)

    # Ordina per nome file
    results.sort(key=lambda x: str(x.get("file", "")))
    df = pd.DataFrame(results)
    df.to_csv(OUT_CSV, index=False)
    print(f"\n[StyleFeatures] Output salvato con successo: {OUT_CSV} ({len(df)} righe, {len(df.columns)} colonne)", flush=True)

if __name__ == "__main__":
    main()
