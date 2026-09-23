# -*- coding: utf-8 -*-
"""
experiments/sensitivity_curve.py  --  response per unit of weight displacement

Page 10 measures how far the image moves when each of the six block groups is rotated by
the same angle. That is a depth profile of the *bench*, not of the model: the same angle is
not the same dose, because the displacement a rotation produces,
D = ||dW||_F / ||W_model||_F, scales with the rotated group's own norm. B6 needs a LARGER
angle than B1 to reach the same D, so at a common angle B6 is pushed LESS -- and page 10
reports it moving the image more. Dividing one by the other is the sensitivity curve.

Two sources of displacement, in order of preference:

1. data/block_group_displacements.csv, written by
   experiments/measure_block_group_displacements.py from the checkpoint. All six groups,
   every angle, measured. This is the one to use.

2. Fallback, when that file is absent: data/matched_rotation_calibration_v4.json, which
   solved for the angle each of B1 and B6 needs to reach the same D at three doses. The
   ratio theta_B6 / theta_B1 is 1.351370, 1.351431, 1.351339 at the three doses -- constant
   to five figures, which is what D(theta) proportional to sin(theta/2) predicts and is the
   evidence that a single angle-independent ratio is legitimate. It gives B1 and B6 only;
   B2 to B5 are left blank rather than guessed.

The output column that matters is `response_per_unit_displacement`: mean_norm_A divided by
the group's displacement relative to B1. `ratio_to_B1` restates it as a multiple.

Nothing is rendered. Reads data/, writes data/sensitivity_by_block.csv.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESPONSE = DATA / "all_blocks_clean_v2_response_by_block.csv"
MEASURED = DATA / "block_group_displacements.csv"
CALIB = DATA / "matched_rotation_calibration_v4.json"
OUT = DATA / "sensitivity_by_block.csv"

ANGLE_DEG = {"low": 5.0, "mid": 10.0, "high": 15.0}


def relative_from_measured() -> tuple[dict[tuple[str, str], float], str]:
    """D of each group at each angle, divided by B1's D at the same angle."""
    rows = list(csv.DictReader(MEASURED.open(encoding="utf-8-sig")))
    by: dict[tuple[str, str], list[float]] = {}
    for r in rows:
        short = "B" + r["group_label"].split("_")[1].split(" ")[0]   # "Block_6 (All 24-27)" -> "B6"
        by.setdefault((short, r["angle_label"]), []).append(float(r["D_fp32"]))
    mean = {k: statistics.fmean(v) for k, v in by.items()}
    rel = {}
    for (g, a), d in mean.items():
        base = mean.get(("B1", a))
        if base:
            rel[(g, a)] = d / base
    return rel, "data/block_group_displacements.csv (measured on the checkpoint)"


def relative_from_calibration() -> tuple[dict[tuple[str, str], float], str]:
    """B1 and B6 only, from the angles that equalise D at three doses."""
    lv = json.loads(CALIB.read_text(encoding="utf-8"))["levels"]
    ratios = [v["theta_B6_deg"] / v["theta_B1_deg"] for v in lv.values()]
    spread = max(ratios) - min(ratios)
    if spread > 1e-3:
        raise SystemExit(f"theta_B6/theta_B1 is not constant across doses (spread {spread:.2e}): "
                         f"the angle-independent ratio cannot be used, run "
                         f"experiments/measure_block_group_displacements.py instead")
    r = statistics.fmean(ratios)
    rel = {}
    for a in ANGLE_DEG:
        rel[("B1", a)] = 1.0
        rel[("B6", a)] = 1.0 / r          # equal D at theta_B6 > theta_B1 means less D at equal theta
    return rel, (f"data/matched_rotation_calibration_v4.json (B1 and B6 only, "
                 f"theta_B6/theta_B1 = {r:.6f} across 3 doses)")


def main() -> None:
    global MEASURED, RESPONSE
    ap = argparse.ArgumentParser()
    ap.add_argument("--displacements", default=str(MEASURED),
                    help="block_group_displacements.csv; falls back to the v4 calibration")
    ap.add_argument("--response", default=str(RESPONSE))
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    MEASURED, RESPONSE = Path(a.displacements), Path(a.response)
    out_path = Path(a.out)
    if MEASURED.exists():
        rel, source = relative_from_measured()
    elif CALIB.exists():
        rel, source = relative_from_calibration()
    else:
        raise SystemExit("neither data/block_group_displacements.csv nor "
                         "data/matched_rotation_calibration_v4.json is present")

    rows = list(csv.DictReader(RESPONSE.open(encoding="utf-8-sig")))
    out = []
    for r in rows:
        g, a = r["block"], r["angle"]
        resp = float(r["mean_norm_A"])
        d = rel.get((g, a))
        out.append({
            "angle_label": a,
            "angle_deg": ANGLE_DEG[a],
            "block": g,
            "n_cells": r["n_cells"],
            "mean_norm_A": round(resp, 6),
            "sd_norm_A": round(float(r["sd_norm_A"]), 6),
            "relative_displacement_vs_B1": round(d, 6) if d else "not measured",
            "response_per_unit_displacement": round(resp / d, 6) if d else "not measured",
            "displacement_source": source,
        })
    order = {"low": 0, "mid": 1, "high": 2}
    out.sort(key=lambda r: (order[r["angle_label"]], r["block"]))

    # ratio_to_B1 is computed after the sort so every angle has its own B1 in hand
    base = {r["angle_label"]: r["response_per_unit_displacement"] for r in out if r["block"] == "B1"}
    for r in out:
        v, b = r["response_per_unit_displacement"], base.get(r["angle_label"])
        r["ratio_to_B1"] = round(v / b, 4) if isinstance(v, float) and isinstance(b, float) else "not measured"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"wrote {out_path}  ({len(out)} rows)")
    print(f"displacement source: {source}\n")
    for r in out:
        print(f"{r['angle_label']:>4} {r['angle_deg']:>5.1f} deg  {r['block']}  "
              f"response {r['mean_norm_A']:>8.4f}  "
              f"rel D {r['relative_displacement_vs_B1']}  "
              f"per unit D {r['response_per_unit_displacement']}  "
              f"x B1 {r['ratio_to_B1']}")


if __name__ == "__main__":
    main()
