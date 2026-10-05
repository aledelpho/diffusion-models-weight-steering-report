# -*- coding: utf-8 -*-
"""
experiments/monitor_single_blocks_v3.py
=======================================
Monitors progress of benchmark_single_blocks_v3 renders (171 total).
Logs progress every 10 generations with real-time ETA calculation based on rolling speed.
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
RENDERS_DIR = COMFY_OUTPUT_ROOT / "benchmark_single_blocks_v3" / "renders"
TOTAL_EXPECTED = 342
POLL_INTERVAL_SEC = 5

LOG_FILE = Path(r"c:\Users\aless\Desktop\comfyui-pilot\single_blocks_v3_progress.log")


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


def get_recent_speed(default_sec=32.8):
    try:
        files = sorted(RENDERS_DIR.glob("*.png"), key=os.path.getmtime)
        if len(files) >= 6:
            dt = files[-1].stat().st_mtime - files[-6].stat().st_mtime
            if 10 < dt < 600:
                return dt / 5.0
    except Exception:
        pass
    return default_sec


def main():
    log("=" * 76)
    log(f"  AVVIO MONITOR SINGLE-BLOCK V3 ({TOTAL_EXPECTED} render totali)")
    log(f"  Directory monitorata: {RENDERS_DIR}")
    log(f"  Log impostato a scaglioni di 10 generazioni")
    log("=" * 76)

    consecutive_empty = 0
    last_logged_bucket = -1

    while True:
        current_count = count_png_renders()
        running, pending = get_queue_status()

        bucket = current_count // 10
        if bucket > last_logged_bucket or last_logged_bucket == -1:
            last_logged_bucket = bucket
            speed = get_recent_speed()
            remaining = max(0, TOTAL_EXPECTED - current_count)
            eta_seconds = remaining * speed
            eta_time = datetime.now() + timedelta(seconds=eta_seconds)
            eta_hours = int(eta_seconds // 3600)
            eta_mins = int((eta_seconds % 3600) // 60)
            pct = (current_count / TOTAL_EXPECTED) * 100 if TOTAL_EXPECTED > 0 else 0.0

            time_str = f"{eta_hours}h {eta_mins:02d}m" if eta_hours > 0 else f"{eta_mins}m"
            log(
                f"[Avanzamento +10] Render completati: {current_count}/{TOTAL_EXPECTED} ({pct:.1f}%) | "
                f"Mancano: {remaining} render | "
                f"Velocita: {speed:.1f}s/render | "
                f"Tempo residuo: ~{time_str} (Fine prevista: ~{eta_time.strftime('%H:%M:%S')}) | "
                f"Coda ComfyUI: {running} running, {pending} pending"
            )

        if running == 0 and pending == 0:
            consecutive_empty += 1
            if consecutive_empty >= 3 and current_count >= TOTAL_EXPECTED:
                log("=" * 76)
                log(f"  TUTTI I {TOTAL_EXPECTED} RENDER COMPLETATI CON SUCCESSO!")
                log("=" * 76)
                break
        else:
            consecutive_empty = 0

        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    main()
