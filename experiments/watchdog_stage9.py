# -*- coding: utf-8 -*-
"""
experiments/watchdog_stage9.py

Watchdog per lo Stage 9 (300 render totali):
1. Monitora la coda di ComfyUI e la cartella benchmark_stage9/renders.
2. Al termine (300 PNG e coda vuota), esegue:
   - palette_from_manifest.py -> palette_features_stage9.csv
   - style_from_manifest.py -> style_features_stage9.csv
   - analyze_stage9_style_direction.py -> stage9_coherence_results.csv
3. Sincronizza tutti i risultati in diffusion-models-weight-steering-report/data/.
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

SLUG = "benchmark_stage9"
BASE_DIR_9 = rf"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\{SLUG}"
RENDERS_DIR_9 = os.path.join(BASE_DIR_9, "renders")

STAGE7A_RENDERS = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_stage7a\renders"
STAGE7A_MANIFEST = os.path.join(PILOT_ROOT, "stage7a_images.csv")

MANIFEST_9 = os.path.join(PILOT_ROOT, "stage9_images.csv")
PALETTE_9_OUT = os.path.join(PILOT_ROOT, "palette_features_stage9.csv")
STYLE_9_OUT = os.path.join(PILOT_ROOT, "style_features_stage9.csv")
COHERENCE_OUT = os.path.join(PILOT_ROOT, "stage9_coherence_results.csv")

LOG_FILE_PILOT = os.path.join(PILOT_ROOT, "stage9_progress.log")
LOG_FILE_REPORT = os.path.join(REPORT_ROOT, "data", "stage9_progress.log")
REPORT_DATA = os.path.join(REPORT_ROOT, "data")

EXPECTED_TOTAL = 300


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
    log(" AVVIO WATCHDOG STAGE 9 (300 render)")
    log(f" Directory monitorata: {RENDERS_DIR_9}")
    log(f" Attesi: {EXPECTED_TOTAL} file PNG e azzeramento coda ComfyUI")
    log("==================================================================")

    last_count = -1
    while True:
        pngs = glob.glob(os.path.join(RENDERS_DIR_9, "*.png"))
        cnt = len(pngs)
        r, p = get_queue()

        if cnt != last_count and (cnt % 10 == 0 or cnt == EXPECTED_TOTAL or cnt < 5):
            pct = (cnt / EXPECTED_TOTAL) * 100
            log(f"[Stage 9 Monitor] Render completati: {cnt}/{EXPECTED_TOTAL} ({pct:.1f}%) | Queue: {r} running, {p} pending")
            last_count = cnt

        if cnt >= EXPECTED_TOTAL and r == 0 and p == 0:
            log("******************************************************************")
            log("[LOG FINE CODA REGISTRATO CON SUCCESSO]")
            log(f"Tutti i {EXPECTED_TOTAL} render di Stage 9 sono completati e la coda ComfyUI e' a zero.")
            log("******************************************************************")
            break

        time.sleep(20)

    # 1. Estrazione palette
    log(">>> Esecuzione palette_from_manifest.py su Stage 9 (300 immagini)...")
    cmd_pal = [
        PYTHON_EXE, "-u", os.path.join(PILOT_ROOT, "experiments", "palette_from_manifest.py"),
        "--manifest", MANIFEST_9,
        "--renders-root", BASE_DIR_9,
        "--out", PALETTE_9_OUT,
        "--source-csv", "palette_features_stage9.csv"
    ]
    res_pal = subprocess.run(cmd_pal)
    if res_pal.returncode != 0:
        log(f"[ERRORE] palette_from_manifest.py fallito con codice {res_pal.returncode}")
    else:
        log(f"[Stage 9] Palette estratta in {PALETTE_9_OUT}")

    # 2. Estrazione style features
    log(">>> Esecuzione style_from_manifest.py su Stage 9 + baseline Stage 7a...")
    cmd_style = [
        PYTHON_EXE, "-u", os.path.join(PILOT_ROOT, "experiments", "style_from_manifest.py"),
        "--manifest", MANIFEST_9,
        "--renders-root", RENDERS_DIR_9,
        "--out", STYLE_9_OUT,
        "--also", f"{STAGE7A_MANIFEST}={STAGE7A_RENDERS}"
    ]
    res_style = subprocess.run(cmd_style)
    if res_style.returncode != 0:
        log(f"[ERRORE] style_from_manifest.py fallito con codice {res_style.returncode}")
    else:
        log(f"[Stage 9] Style features estratte in {STYLE_9_OUT}")

    # 3. Analisi direzionale nei 4 spazi
    log(">>> Esecuzione analyze_stage9_style_direction.py...")
    cmd_ana = [
        PYTHON_EXE, "-u", os.path.join(PILOT_ROOT, "experiments", "analyze_stage9_style_direction.py")
    ]
    res_ana = subprocess.run(cmd_ana)
    if res_ana.returncode != 0:
        log(f"[ERRORE] analyze_stage9_style_direction.py fallito con codice {res_ana.returncode}")
    else:
        log(f"[Stage 9] Analisi completata con successo.")

    # 4. Sincronizzazione file nel repo report
    if os.path.exists(REPORT_DATA):
        for f in [MANIFEST_9, PALETTE_9_OUT, STYLE_9_OUT, COHERENCE_OUT, LOG_FILE_PILOT]:
            if os.path.exists(f):
                shutil.copy2(f, REPORT_DATA)
                log(f"[Sync] Copiato in report/data: {os.path.basename(f)}")

    log("==================================================================")
    log(" STAGE 9 COMPLETATO AL 100%. TUTTI I DATI ESTRATTI E SINCRONIZZATI.")
    log("==================================================================")


if __name__ == "__main__":
    main()
