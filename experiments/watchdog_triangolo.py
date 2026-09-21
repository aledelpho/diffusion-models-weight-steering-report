#!/usr/bin/env python3
"""
experiments/watchdog_triangolo.py
=================================
Watchdog e monitor di avanzamento continuo per l'esperimento Triangolo (120 render).
Monitora in background:
  - Il conteggio delle 120 nuove immagini del Triangolo (Block_3 e scramble_C/D)
  - Il totale nella cartella (330 immagini attese)
  - Lo stato della coda di ComfyUI (running e pending)
  - Calcola l'avanzamento percentuale e l'ETA stimato al completamento
  - Scrive periodicamente nel log `triangolo_progress.log` e nello stato JSON `triangolo_status.json`
  - All'azzeramento della coda e al raggiungimento di tutti i file, registra:
    `[LOG FINE CODA REGISTRATO CON SUCCESSO]`
"""

import os
import sys
import time
import glob
import json
import urllib.request

PILOT_ROOT = r"c:\Users\aless\Desktop\comfyui-pilot"
REPORT_ROOT = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report"
RENDERS_DIR = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\rotations_block1_vs_block6"

LOG_PILOT = os.path.join(PILOT_ROOT, "triangolo_progress.log")
LOG_REPORT = os.path.join(REPORT_ROOT, "data", "triangolo_progress.log")
STATUS_JSON = os.path.join(PILOT_ROOT, "triangolo_status.json")

TOTAL_NEW_EXPECTED = 120
TOTAL_ALL_EXPECTED = 330
COMFY_QUEUE_URL = "http://127.0.0.1:8188/queue"

def log(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    for path in [LOG_PILOT, LOG_REPORT]:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

def get_queue():
    try:
        req = urllib.request.urlopen(COMFY_QUEUE_URL, timeout=5)
        d = json.loads(req.read().decode("utf-8"))
        return len(d.get("queue_running", [])), len(d.get("queue_pending", []))
    except Exception:
        return -1, -1

def main():
    log("==================================================================")
    log(" AVVIO MONITOR & WATCHDOG TRIANGOLO (BLOCK_1 / BLOCK_3 / BLOCK_6)")
    log(f" Directory monitorata: {RENDERS_DIR}")
    log(f" Attesi: {TOTAL_NEW_EXPECTED} nuovi render Triangolo (totale cartella: {TOTAL_ALL_EXPECTED})")
    log("==================================================================")

    start_time = time.time()
    last_count = -1
    initial_new_count = None

    while True:
        all_pngs = glob.glob(os.path.join(RENDERS_DIR, "*.png"))
        new_pngs = [p for p in all_pngs if ("Block_3" in os.path.basename(p) or "scramble_C" in os.path.basename(p) or "scramble_D" in os.path.basename(p))]
        cnt_new = len(new_pngs)
        cnt_all = len(all_pngs)
        r, p = get_queue()

        if initial_new_count is None:
            initial_new_count = cnt_new

        now = time.time()
        elapsed = now - start_time
        rendered_since_start = cnt_new - initial_new_count

        eta_str = "--"
        eta_seconds = 0
        if rendered_since_start > 0:
            sec_per_img = elapsed / rendered_since_start
            remaining_imgs = max(0, TOTAL_NEW_EXPECTED - cnt_new)
            eta_seconds = int(remaining_imgs * sec_per_img)
            eta_mins = eta_seconds // 60
            eta_secs = eta_seconds % 60
            eta_str = f"~{eta_mins}m {eta_secs}s"

        # Logga ad ogni avanzamento o ogni 30 secondi
        if cnt_new != last_count:
            last_file = os.path.basename(sorted(new_pngs, key=os.path.getmtime)[-1]) if new_pngs else "nessuno"
            pct = (cnt_new / TOTAL_NEW_EXPECTED) * 100
            log(f"[Avanzamento] Nuovi render: {cnt_new}/{TOTAL_NEW_EXPECTED} ({pct:.1f}%) | Totale cartella: {cnt_all}/{TOTAL_ALL_EXPECTED} | Coda: {r} running, {p} pending | ETA: {eta_str} | Ultimo: {last_file}")
            last_count = cnt_new

        # Salva stato JSON
        status_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_new": cnt_new,
            "total_new": TOTAL_NEW_EXPECTED,
            "percent_new": round((cnt_new / TOTAL_NEW_EXPECTED) * 100, 1),
            "completed_all": cnt_all,
            "total_all": TOTAL_ALL_EXPECTED,
            "queue_running": r,
            "queue_pending": p,
            "eta_string": eta_str,
            "eta_seconds": eta_seconds,
            "is_complete": False
        }

        # Condizione di completamento
        if cnt_new >= TOTAL_NEW_EXPECTED and r == 0 and p == 0:
            log("******************************************************************")
            log("[LOG FINE CODA REGISTRATO CON SUCCESSO]")
            log(f"Tutti i {TOTAL_NEW_EXPECTED} nuovi render del Triangolo sono stati generati!")
            log(f"Totale immagini verificate in cartella: {cnt_all}/{TOTAL_ALL_EXPECTED}.")
            log(f"Coda ComfyUI azzerata (running=0, pending=0).")
            log("******************************************************************")
            status_data["is_complete"] = True
            with open(STATUS_JSON, "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2)
            break

        with open(STATUS_JSON, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2)

        time.sleep(20)

if __name__ == "__main__":
    main()
