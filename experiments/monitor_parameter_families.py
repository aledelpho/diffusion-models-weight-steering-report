# -*- coding: utf-8 -*-
"""
experiments/monitor_parameter_families.py
=========================================
Monitors progress of benchmark_parameter_families renders and logs status periodically to
parameter_families_progress.log with elapsed time, render count, queue status and ETA.
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
RENDERS_DIR = COMFY_OUTPUT_ROOT / "benchmark_parameter_families" / "renders"
TOTAL_EXPECTED = 180
POLL_INTERVAL_SEC = 20

LOG_FILE = Path(r"c:\Users\aless\Desktop\comfyui-pilot\parameter_families_progress.log")


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
    log(f"  AVVIO MONITOR PARAMETER FAMILIES ({TOTAL_EXPECTED} render)")
    log(f"  Directory monitorata: {RENDERS_DIR}")
    log("=" * 72)

    start_time = time.time()
    consecutive_empty = 0

    while True:
        current_count = count_png_renders()
        running, pending = get_queue_status()
        elapsed = time.time() - start_time

        if current_count > 0:
            avg_per_render = elapsed / current_count
            remaining = max(0, TOTAL_EXPECTED - current_count)
            eta_seconds = remaining * avg_per_render
            eta_str = (datetime.now() + timedelta(seconds=eta_seconds)).strftime("%H:%M")
            speed_str = f"{avg_per_render:.1f}s/render"
            eta_display = f"ETA: ~{int(eta_seconds//60)} min ({eta_str}) | {speed_str}"
        else:
            eta_display = "ETA: in calcolo..."

        pct = (current_count / TOTAL_EXPECTED) * 100 if TOTAL_EXPECTED > 0 else 0.0

        log(
            f"[Parameter Families Monitor] Render: {current_count}/{TOTAL_EXPECTED} ({pct:.1f}%) | "
            f"Queue: {running} running, {pending} pending | {eta_display}"
        )

        if running == 0 and pending == 0:
            consecutive_empty += 1
            if consecutive_empty >= 2 and current_count >= TOTAL_EXPECTED:
                log("=" * 72)
                log(f"  TUTTI I {TOTAL_EXPECTED} RENDER DEL BENCHMARK COMPLETATI!")
                log("=" * 72)
                break
        else:
            consecutive_empty = 0

        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    main()
