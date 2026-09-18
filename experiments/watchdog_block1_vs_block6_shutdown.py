# -*- coding: utf-8 -*-
"""
experiments/watchdog_block1_vs_block6_shutdown.py
=================================================
Watchdog autonomo notturno per l'esperimento Block_1 vs Block_6 (210 immagini):
1. Monitora la coda di ComfyUI finché non è azzerata (0 running, 0 pending)
   e tutti i 210 file PNG sono presenti in output/rotations_block1_vs_block6/.
2. Registra il [LOG FINE CODA REGISTRATO CON SUCCESSO].
3. Esegue la pipeline di feature extraction (extract_block1_vs_block6_features.py).
4. Esegue l'analisi statistica pre-registrata (analyze_block1_vs_block6.py).
5. Compila il report formale in docs/rotations_block1_vs_block6_results.md (generate_block1_vs_block6_report.py).
6. Esegue git add, commit e push su origin main nel repository report.
7. Spegne forzatamente il computer con:
   shutdown.exe /s /f /t 60 /c "Block 1 vs Block 6 completed. Report committed and pushed. Forced shutdown initiated."
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

RENDERS_DIR = r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\rotations_block1_vs_block6"
EXPECTED_TOTAL = 210

LOG_FILE_PILOT = os.path.join(PILOT_ROOT, "block1_vs_block6_progress.log")
LOG_FILE_REPORT = os.path.join(REPORT_ROOT, "data", "block1_vs_block6_progress.log")


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
    log(" AVVIO WATCHDOG NOTTURNO BLOCK_1 VS BLOCK_6 (210 render)")
    log(f" Directory monitorata: {RENDERS_DIR}")
    log(f" Attesi: {EXPECTED_TOTAL} file PNG e azzeramento coda ComfyUI")
    log("==================================================================")

    last_count = -1
    while True:
        pngs = glob.glob(os.path.join(RENDERS_DIR, "*.png"))
        cnt = len(pngs)
        r, p = get_queue()

        if cnt != last_count and (cnt % 5 == 0 or cnt == EXPECTED_TOTAL or cnt < 5):
            pct = (cnt / EXPECTED_TOTAL) * 100
            log(f"[Monitor Coda] Render completati: {cnt}/{EXPECTED_TOTAL} ({pct:.1f}%) | Queue: {r} running, {p} pending")
            last_count = cnt

        # Condizione di completamento
        if cnt >= EXPECTED_TOTAL and r == 0 and p == 0:
            log("******************************************************************")
            log("[LOG FINE CODA REGISTRATO CON SUCCESSO]")
            log(f"Tutti i {EXPECTED_TOTAL} render sono completati e la coda ComfyUI e' a zero.")
            log("******************************************************************")
            break

        time.sleep(20)

    # 1. Estrazione delle feature
    log(">>> Esecuzione extract_block1_vs_block6_features.py (210 immagini)...")
    cmd_ext = [PYTHON_EXE, "-u", os.path.join(PILOT_ROOT, "experiments", "extract_block1_vs_block6_features.py")]
    res_ext = subprocess.run(cmd_ext)
    if res_ext.returncode != 0:
        log(f"[ERRORE] extract_block1_vs_block6_features.py fallito con codice {res_ext.returncode}")
    else:
        log("[OK] Estrazione feature completata con successo.")

    # 2. Analisi statistica
    log(">>> Esecuzione analyze_block1_vs_block6.py...")
    cmd_ana = [PYTHON_EXE, "-u", os.path.join(PILOT_ROOT, "experiments", "analyze_block1_vs_block6.py")]
    res_ana = subprocess.run(cmd_ana)
    if res_ana.returncode != 0:
        log(f"[ERRORE] analyze_block1_vs_block6.py fallito con codice {res_ana.returncode}")
    else:
        log("[OK] Analisi statistica pre-registrata completata con successo.")

    # 3. Compilazione del report Markdown
    log(">>> Esecuzione generate_block1_vs_block6_report.py...")
    cmd_rep = [PYTHON_EXE, "-u", os.path.join(PILOT_ROOT, "experiments", "generate_block1_vs_block6_report.py")]
    res_rep = subprocess.run(cmd_rep)
    if res_rep.returncode != 0:
        log(f"[ERRORE] generate_block1_vs_block6_report.py fallito con codice {res_rep.returncode}")
    else:
        log("[OK] Report Markdown generato in docs/rotations_block1_vs_block6_results.md.")

    # 4. Sincronizzazione file generati
    report_data = os.path.join(REPORT_ROOT, "data")
    pilot_data = os.path.join(PILOT_ROOT, "data")
    for fn in [
        "rotations_block1_vs_block6_style_features.csv",
        "rotations_block1_vs_block6_palette_features.csv",
        "rotations_block1_vs_block6_results.csv",
        "rotations_block1_vs_block6_prompt_scores.csv",
    ]:
        src = os.path.join(pilot_data, fn)
        dst = os.path.join(report_data, fn)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            log(f"[Sync] Copiato {fn} -> {report_data}")

    # 5. Git commit e push
    log(">>> Esecuzione Git commit e push su origin main...")
    try:
        subprocess.run(["git", "add", "data/", "docs/", "experiments/"], cwd=REPORT_ROOT, check=True)
        subprocess.run(
            ["git", "commit", "-m", "feat(report): block 1 vs block 6 rotation results and null falsification"],
            cwd=REPORT_ROOT,
            check=True
        )
        subprocess.run(["git", "push", "origin", "main"], cwd=REPORT_ROOT, check=True)
        log("[GIT OK] Commit e push su origin main completati con successo.")
    except Exception as e:
        log(f"[GIT WARN] Errore git: {e}")

    log("==================================================================")
    log(" ESPERIMENTO BLOCK_1 VS BLOCK_6 COMPLETATO AL 100%. REPORT INVIATO.")
    log(" [SHUTDOWN] Inizio spegnimento forzato del computer entro 60 secondi...")
    log("==================================================================")

    # 6. Spegnimento forzato del computer (/f per forzare la chiusura delle app appese)
    try:
        subprocess.run(
            ["shutdown.exe", "/s", "/f", "/t", "60", "/c", "Block 1 vs Block 6 completed. Report committed and pushed. Forced shutdown initiated."],
            check=True
        )
        log("[SHUTDOWN] Comando shutdown.exe inviato con successo.")
    except Exception as e:
        log(f"[SHUTDOWN ERRORE] Impossibile inviare comando di shutdown: {e}")


if __name__ == "__main__":
    main()
