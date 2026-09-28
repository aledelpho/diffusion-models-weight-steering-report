# -*- coding: utf-8 -*-
"""
experiments/monitor_centre_push.py
==================================
Monitors progress of benchmark_centre_push renders and logs status periodically to
centre_push_progress.log with elapsed time, render count, queue status and ETA.
Does NOT shut down or close the machine.
"""

import time
import os
import json
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

COMFY_QUEUE_URL = "http://127.0.0.1:8188/queue"
COMFY_OUTPUT_ROOT = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output")
RENDERS_DIR = COMFY_OUTPUT_ROOT / "benchmark_centre_push" / "renders"
TOTAL_EXPECTED = 295
POLL_INTERVAL_SEC = 30

LOG_FILE = Path(r"c:\Users\aless\Desktop\comfyui-pilot\centre_push_progress.log")


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")


def get_queue_status():
    try:
        req = urllib.request.Request(COMFY_QUEUE_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            running = len(data.get("queue_running", []))
            pending = len(data.get("queue_pending", []))
            return running, pending
    except Exception:
        return -1, -1


def count_png_renders():
    if not RENDERS_DIR.exists():
        return 0
    return len([f for f in os.listdir(RENDERS_DIR) if f.lower().endswith(".png")])


def main():
    log("=" * 72)
    log("  AVVIO MONITOR CENTRE PUSH (295 render)")
    log(f"  Directory monitorata: {RENDERS_DIR}")
    log(f"  File attesi: {TOTAL_EXPECTED} file PNG")
    log("=" * 72)

    t_start = time.time()
    initial_count = count_png_renders()
    last_count = initial_count

    while True:
        current_count = count_png_renders()
        running, pending = get_queue_status()
        pct = (current_count / TOTAL_EXPECTED) * 100 if TOTAL_EXPECTED > 0 else 0

        # Calculate speed and ETA
        elapsed_sec = time.time() - t_start
        new_done = current_count - initial_count
        if new_done > 0 and elapsed_sec > 0:
            sec_per_render = elapsed_sec / new_done
            rem_renders = max(0, TOTAL_EXPECTED - current_count)
            rem_sec = rem_renders * sec_per_render
            eta_time = datetime.now() + timedelta(seconds=rem_sec)
            eta_str = f"ETA: ~{round(rem_sec / 60)} min ({eta_time.strftime('%H:%M')}) | {sec_per_render:.1f}s/render"
        else:
            eta_str = "ETA: in calcolo..."

        queue_str = f"Queue: {running} running, {pending} pending" if running != -1 else "Queue: non raggiungibile"

        log(f"[Centre Push Monitor] Render completati: {current_count}/{TOTAL_EXPECTED} ({pct:.1f}%) | {queue_str} | {eta_str}")

        if current_count >= TOTAL_EXPECTED and (running == 0 and pending == 0):
            log("=" * 72)
            log("  TUTTI I 295 RENDER DI CENTRE PUSH COMPLETATI CON SUCCESSO!")
            log("=" * 72)
            break

        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    main()
