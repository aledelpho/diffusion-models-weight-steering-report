# -*- coding: utf-8 -*-
"""
experiments/watchdog_stage12.py

Watchdog per lo Stage 12 (250 render totali):
1. Monitora la cartella benchmark_stage12/renders e l'endpoint /queue di ComfyUI.
2. Al raggiungimento di 250 PNG e coda azzerata:
   - Esegue prepare_stage12_blind.py -> genera 220 immagini con disturbi e sigilla la chiave data/stage12_bbox_key.csv
   - Esegue palette_from_manifest.py -> data/palette_features_stage12.csv
   - Esegue style_from_manifest.py -> data/style_features_stage12.csv
   - Sincronizza tutti i file in report/data/
"""

import os
import sys
import time
import glob
import json
import shutil
import urllib.request
import subprocess

PYTHON_EXE = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\venv\Scripts\python.exe"
PILOT_ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"

SLUG = "benchmark_stage12"
BASE_DIR_12 = rf"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\{SLUG}"
RENDERS_DIR_12 = os.path.join(BASE_DIR_12, "renders")

MANIFEST_12 = os.path.join(REPORT_ROOT, "data", "stage12_images.csv")
PALETTE_12_OUT = os.path.join(REPORT_ROOT, "data", "palette_features_stage12.csv")
STYLE_12_OUT = os.path.join(REPORT_ROOT, "data", "style_features_stage12.csv")

LOG_FILE_PILOT = os.path.join(PILOT_ROOT, "stage12_progress.log")
LOG_FILE_REPORT = os.path.join(REPORT_ROOT, "data", "stage12_progress.log")
REPORT_DATA = os.path.join(REPORT_ROOT, "data")

EXPECTED_TOTAL = 250


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE_PILOT, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    try:
        if os.path.exists(REPORT_DATA):
            with open(LOG_FILE_REPORT, "a", encoding="utf-8") as f:
                f.write(line + "\n")
    except Exception:
        pass


def get_queue():
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8188/queue", timeout=5)
        d = json.loads(req.read().decode("utf-8"))
        return len(d.get("queue_running", [])), len(d.get("queue_pending", []))
    except Exception:
        return -1, -1


def main():
    log("==================================================================")
    log(" AVVIO WATCHDOG STAGE 12 (250 render)")
    log(f" Directory monitorata: {RENDERS_DIR_12}")
    log(f" Attesi: {EXPECTED_TOTAL} file PNG e azzeramento coda ComfyUI")
    log("==================================================================")

    last_count = -1
    while True:
        pngs = glob.glob(os.path.join(RENDERS_DIR_12, "*.png"))
        cnt = len(pngs)
        r, p = get_queue()

        if cnt != last_count and (cnt % 10 == 0 or cnt == EXPECTED_TOTAL or cnt < 5):
            pct = (cnt / EXPECTED_TOTAL) * 100
            log(f"[Stage 12 Monitor] Render completati: {cnt}/{EXPECTED_TOTAL} ({pct:.1f}%) | Queue: {r} running, {p} pending")
            last_count = cnt

        if cnt >= EXPECTED_TOTAL and r == 0 and p == 0:
            log("******************************************************************")
            log("[LOG FINE CODA REGISTRATO CON SUCCESSO]")
            log(f"Tutti i {EXPECTED_TOTAL} render di Stage 12 sono completati e la coda ComfyUI e' a zero.")
            log("******************************************************************")
            break

        time.sleep(20)

    # 1. Preparazione del set cieco a 220 immagini con disturbi e 20 duplicati
    log(">>> Esecuzione prepare_stage12_blind.py (3 livelli di cecità)...")
    cmd_prep = [
        PYTHON_EXE, "-u", os.path.join(REPORT_ROOT, "experiments", "prepare_stage12_blind.py")
    ]
    res_prep = subprocess.run(cmd_prep)
    if res_prep.returncode != 0:
        log(f"[ERRORE] prepare_stage12_blind.py fallito con codice {res_prep.returncode}")
    else:
        log("[Stage 12] Set cieco a 220 immagini e chiave preparati con successo.")

    # 2. Estrazione palette
    log(">>> Esecuzione palette_from_manifest.py su Stage 12 (250 immagini)...")
    cmd_pal = [
        PYTHON_EXE, "-u", os.path.join(PILOT_ROOT, "experiments", "palette_from_manifest.py"),
        "--manifest", MANIFEST_12,
        "--renders-root", BASE_DIR_12,
        "--out", PALETTE_12_OUT,
        "--source-csv", "palette_features_stage12.csv"
    ]
    res_pal = subprocess.run(cmd_pal)
    if res_pal.returncode != 0:
        log(f"[ERRORE] palette_from_manifest.py fallito con codice {res_pal.returncode}")
    else:
        log(f"[Stage 12] Palette estratta in {PALETTE_12_OUT}")

    # 3. Estrazione feature di stile
    log(">>> Esecuzione style_from_manifest.py su Stage 12...")
    cmd_style = [
        PYTHON_EXE, "-u", os.path.join(PILOT_ROOT, "experiments", "style_from_manifest.py"),
        "--manifest", MANIFEST_12,
        "--renders-root", RENDERS_DIR_12,
        "--out", STYLE_12_OUT
    ]
    res_style = subprocess.run(cmd_style)
    if res_style.returncode != 0:
        log(f"[ERRORE] style_from_manifest.py fallito con codice {res_style.returncode}")
    else:
        log(f"[Stage 12] Feature di stile estratte in {STYLE_12_OUT}")

    log("==================================================================")
    log(" STAGE 12 GENERATO E PREPARATO. PRONTO PER L'ANNOTAZIONE CIECA.")
    log("==================================================================")


if __name__ == "__main__":
    main()
