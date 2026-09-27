# -*- coding: utf-8 -*-
"""
experiments/monitor_colour_sweep.py
===================================
Monitors progress of Stage 2 Colour Object Sweep (117 renders) in real-time.
Prints summary to stdout and appends timestamped status to data/colour_sweep_progress.log.

Usage:
  python experiments/monitor_colour_sweep.py
  python experiments/monitor_colour_sweep.py --loop 30
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PLAN_CSV = DATA_DIR / "colour_object_sweep_plan.csv"
LOG_FILE = DATA_DIR / "colour_sweep_progress.log"
RENDERS_DIR = Path(r"C:\StabilityMatrix-win-x64\Data\Packages\ComfyUI\output\benchmark_colour_binding\renders")
COMFY_QUEUE_URL = "http://127.0.0.1:8188/queue"


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


def check_progress(log_to_file: bool = True) -> tuple[int, int, float, str]:
    now = datetime.datetime.now()

    if not PLAN_CSV.exists():
        sys.exit(f"Error: {PLAN_CSV} not found.")

    with open(PLAN_CSV, encoding="utf-8") as f:
        plan = list(csv.DictReader(f))

    total_tasks = len(plan)
    completed_rows = []
    missing_rows = []

    for r in plan:
        target_png = RENDERS_DIR / (r["output_prefix"].split("/")[-1] + "_00001_.png")
        if target_png.exists():
            completed_rows.append((r, target_png.stat().st_mtime))
        else:
            missing_rows.append(r)

    completed_count = len(completed_rows)
    pct = (completed_count / total_tasks * 100.0) if total_tasks > 0 else 0.0

    running, pending = get_queue_info()

    # Calculate cadence based on recently finished Stage 2 files
    cadence_sec = 35.0  # sensible default
    if len(completed_rows) >= 4:
        # Sort by mtime
        completed_rows.sort(key=lambda x: x[1])
        recent_mtimes = [m for _, m in completed_rows[-10:]]
        if len(recent_mtimes) >= 2 and (recent_mtimes[-1] - recent_mtimes[0]) > 0:
            cadence_sec = (recent_mtimes[-1] - recent_mtimes[0]) / (len(recent_mtimes) - 1)

    remaining_tasks = total_tasks - completed_count
    eta_seconds = remaining_tasks * cadence_sec
    eta_time = now + datetime.timedelta(seconds=eta_seconds)

    # Detect current condition from latest completed or next missing
    current_condition = "Tutti completati"
    if missing_rows:
        next_task = missing_rows[0]
        if next_task["type"] == "baseline":
            current_condition = "Baseline (controllo)"
        else:
            current_condition = f"{next_task['block']} ({next_task['sign']}, gain={float(next_task['gain']):+.3f})"

    latest_file_name = "Nessuno"
    if completed_rows:
        completed_rows.sort(key=lambda x: x[1])
        latest_file_name = (completed_rows[-1][0]["output_prefix"].split("/")[-1] + "_00001_.png")

    report_lines = [
        "==================================================",
        "STAGE 2 COLOUR/OBJECT SWEEP - PROGRESS LOG",
        f"Timestamp:          {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Completed:          {completed_count} / {total_tasks} ({pct:.1f}%)",
        f"Remaining:          {remaining_tasks} renders",
        f"ComfyUI Queue:      Running={running}, Pending={pending}",
        f"Current Condition:  {current_condition}",
        f"Latest Rendered:    {latest_file_name}",
        f"Cadence:            {cadence_sec:.1f}s / render",
        f"Estimated Finish:   {eta_time.strftime('%Y-%m-%d %H:%M:%S')} (~{eta_seconds/60:.1f} min remaining)",
        "==================================================",
    ]

    report_str = "\n".join(report_lines)
    print(report_str)

    if log_to_file:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(
                f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {completed_count}/{total_tasks} ({pct:.1f}%) | "
                f"Remaining: {remaining_tasks} | Cond: {current_condition} | "
                f"Cadence: {cadence_sec:.1f}s | Queue Pending: {pending} | "
                f"ETA: {eta_time.strftime('%H:%M:%S')} (~{eta_seconds/60:.1f}m)\n"
            )

    return completed_count, total_tasks, eta_seconds, current_condition


def main():
    parser = argparse.ArgumentParser(description="Monitor Colour Object Sweep Progress")
    parser.add_argument("--loop", type=int, default=0, help="Poll interval in seconds (0 = run once)")
    args = parser.parse_args()

    if args.loop <= 0:
        check_progress(log_to_file=True)
    else:
        print(f"Starting continuous progress logger (polling every {args.loop}s)... Press Ctrl+C to stop.")
        try:
            while True:
                completed, total, eta_sec, _ = check_progress(log_to_file=True)
                if completed >= total:
                    print("\nAll tasks completed!")
                    break
                time.sleep(args.loop)
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
