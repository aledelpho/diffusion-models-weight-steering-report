# -*- coding: utf-8 -*-
"""
experiments/watchdog_shutdown_on_empty_queue.py
===============================================
Monitors ComfyUI queue until completely empty (running=0, pending=0).
Once queue is confirmed empty:
  1. Runs evaluate_colour_object_sweep.py --dose 0.200
  2. Runs validate_notebook.py
  3. Git adds and commits generated measurement and verdict files
  4. Initiates forced Windows PC shutdown (shutdown.exe /s /f /t 60)

Usage:
  python experiments/watchdog_shutdown_on_empty_queue.py
"""

from __future__ import annotations

import datetime
import glob
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
LOG_FILE = DATA_DIR / "watchdog_shutdown.log"

COMFY_QUEUE_URL = "http://127.0.0.1:8188/queue"
COMFY_OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")

MASKS_DIR = COMFY_OUTPUT_ROOT / "benchmark_rectified_masks" / "renders"
COLOUR_DIR = COMFY_OUTPUT_ROOT / "benchmark_colour_binding" / "renders"

PYTHON_EXE = sys.executable


def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_queue() -> tuple[int, int]:
    try:
        req = urllib.request.Request(COMFY_QUEUE_URL, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            running = len(data.get("queue_running", []))
            pending = len(data.get("queue_pending", []))
            return running, pending
    except Exception:
        return -1, -1


def main():
    log("==================================================================")
    log(" AVVIO WATCHDOG SHUTDOWN CODA COMFYUI")
    log(" Azione: Monitoraggio coda fino ad azzeramento (0 running, 0 pending).")
    log(" Al termine: Valutazione Stage 2b (dose 0.200), commit locale e shutdown forzato.")
    log("==================================================================")

    empty_cycles = 0
    REQUIRED_EMPTY_CYCLES = 3  # 3 checks consecutive = ~90 seconds of confirmed idle queue
    CHECK_INTERVAL_SEC = 30

    while True:
        r, p = get_queue()
        masks_count = len(list(MASKS_DIR.glob("*.png"))) if MASKS_DIR.exists() else 0
        colour_count = len(list(COLOUR_DIR.glob("*.png"))) if COLOUR_DIR.exists() else 0

        log(f"[Watchdog] Queue: Running={r}, Pending={p} | Renders completati -> Maschere: {masks_count}/72, Foglie: {colour_count}/150+")

        if r == 0 and p == 0:
            empty_cycles += 1
            log(f"[Watchdog] Coda vuota rilevata ({empty_cycles}/{REQUIRED_EMPTY_CYCLES} conferme consecutive)...")
            if empty_cycles >= REQUIRED_EMPTY_CYCLES:
                log("******************************************************************")
                log("[FINE CODA REGISTRATO CON SUCCESSO] Coda ComfyUI completamente vuota!")
                log("******************************************************************")
                break
        else:
            empty_cycles = 0

        time.sleep(CHECK_INTERVAL_SEC)

    # 1. Valutazione automatica dello Stage 2b (dose 0.200)
    log(">>> Esecuzione valutazione automatica: evaluate_colour_object_sweep.py --dose 0.200...")
    eval_script = ROOT / "experiments" / "evaluate_colour_object_sweep.py"
    try:
        res = subprocess.run([PYTHON_EXE, str(eval_script), "--dose", "0.200"], cwd=ROOT, capture_output=True, text=True, check=True)
        log(f"[OK] Valutazione completata con successo:\n{res.stdout}")
    except subprocess.CalledProcessError as e:
        log(f"[ERRORE] evaluate_colour_object_sweep.py fallito:\n{e.stderr}")

    # 2. Validazione notebook
    log(">>> Esecuzione validate_notebook.py...")
    val_script = ROOT / "experiments" / "validate_notebook.py"
    try:
        subprocess.run([PYTHON_EXE, str(val_script)], cwd=ROOT, check=True)
        log("[OK] Validazione notebook superata a 0 errori.")
    except Exception as e:
        log(f"[WARN] Validatore notebook: {e}")

    # 3. Commit dei risultati
    log(">>> Esecuzione Git commit dei risultati...")
    try:
        subprocess.run(["git", "add", "data/colour_object_sweep_measurements*", "data/colour_object_sweep_verdict*"], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", "dissociazione (Stage 2b): risultati finali e verdetto a dose 0.200"], cwd=ROOT, check=True)
        log("[GIT OK] Commit completato con successo.")
    except Exception as e:
        log(f"[GIT WARN] Commit non eseguito o nessun cambiamento: {e}")

    # 4. Spegnimento forzato del PC
    log("==================================================================")
    log(" TUTTE LE OPERAZIONI SONO CONCLUSE.")
    log(" [SHUTDOWN] Avvio spegnimento forzato del computer entro 60 secondi...")
    log(" (Per annullare prima dello spegnimento digitare da terminale: shutdown /a)")
    log("==================================================================")

    try:
        subprocess.run(
            ["shutdown.exe", "/s", "/f", "/t", "60", "/c", "ComfyUI queue complete. Evaluations and commits finished. Forced PC shutdown initiated."],
            check=True
        )
        log("[SHUTDOWN] Comando shutdown.exe inviato con successo.")
    except Exception as e:
        log(f"[SHUTDOWN ERRORE] Impossibile inviare comando di shutdown: {e}")


if __name__ == "__main__":
    main()
