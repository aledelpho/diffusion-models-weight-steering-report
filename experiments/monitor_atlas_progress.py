# -*- coding: utf-8 -*-
"""
experiments/monitor_atlas_progress.py
====================================
Monitors progress of Perturbation Atlas renders in real-time.
Prints summary to stdout and appends timestamped status to data/render_progress.log.
"""

from __future__ import annotations

import datetime
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RENDERS_DIR = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_atlas_phase1\renders")
LOG_FILE = ROOT / "data" / "render_progress.log"
COMFY_QUEUE_URL = "http://127.0.0.1:8188/queue"

TOTAL_TASKS = 649  # 1 check + 81 Phase 1 + 567 Phase 2


def get_queue_info() -> tuple[int, int]:
    try:
        req = urllib.request.Request(COMFY_QUEUE_URL, method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            running = len(data.get("queue_running", []))
            pending = len(data.get("queue_pending", []))
            return running, pending
    except Exception:
        return -1, -1


def main():
    now = datetime.datetime.now()
    png_files = sorted(RENDERS_DIR.glob("*.png"), key=lambda p: p.stat().st_mtime)
    completed_count = len(png_files)

    running, pending = get_queue_info()

    # Calculate cadence based on last 10 files
    cadence_sec = 34.0  # default fallback
    if len(png_files) >= 10:
        times = [p.stat().st_mtime for p in png_files[-10:]]
        cadence_sec = (times[-1] - times[0]) / (len(times) - 1)

    remaining_tasks = pending if pending >= 0 else (TOTAL_TASKS - completed_count)
    eta_seconds = remaining_tasks * cadence_sec
    eta_time = now + datetime.timedelta(seconds=eta_seconds)

    pct = (completed_count / TOTAL_TASKS) * 100.0

    current_preset = "Unknown"
    latest_file = "None"
    if png_files:
        latest_file = png_files[-1].name
        # Extract preset from filename if present
        parts = latest_file.split("_Arthemy_Atlas_")
        if len(parts) > 1:
            current_preset = "Arthemy_Atlas_" + parts[1].split("_seed")[0]
        elif "baseline" in latest_file:
            current_preset = "baseline"

    report_lines = [
        f"==================================================",
        f"PERTURBATION ATLAS - RENDER PROGRESS LOG",
        f"Timestamp:          {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Completed Renders:  {completed_count} / {TOTAL_TASKS} ({pct:.1f}%)",
        f"Queue Running:      {running}",
        f"Queue Pending:      {pending}",
        f"Current Preset:     {current_preset}",
        f"Latest PNG Saved:   {latest_file}",
        f"Cadence:            {cadence_sec:.1f}s / render",
        f"Estimated Finish:   {eta_time.strftime('%Y-%m-%d %H:%M:%S')} (~{eta_seconds/60:.0f} min remaining)",
        f"==================================================",
    ]

    report_str = "\n".join(report_lines)
    print(report_str)

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {completed_count}/{TOTAL_TASKS} ({pct:.1f}%) | "
                f"Pending: {pending} | Preset: {current_preset} | Cadence: {cadence_sec:.1f}s | "
                f"ETA: {eta_time.strftime('%H:%M:%S')}\n")


if __name__ == "__main__":
    main()
