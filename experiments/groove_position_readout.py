# -*- coding: utf-8 -*-
"""
experiments/groove_position_readout.py
======================================
Alessandro's position prediction (A1-A3), read out of data/groove_by_condition.csv.
Frozen in docs/prereg_groove_or_hole_amendment_02.md. Descriptive: no p-values.

  python experiments/groove_position_readout.py
"""
from __future__ import annotations

import csv
import statistics
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
V_MIN, L_MIN = 1.0, 0.98


def position(bench: str, unit: str) -> str | None:
    if bench == "M":
        g = int(unit.split("_")[1])
        return "end" if g in (1, 6) else "centre"
    if bench == "D":
        b = int(unit[3:])
        return "end" if b <= 4 or b >= 24 else "centre"
    return None


def share(rows, pred):
    return sum(1 for r in rows if pred(r)) / len(rows) if rows else float("nan")


def main() -> None:
    rows = []
    with (DATA / "groove_by_condition.csv").open(encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            pos = position(r["bench"], r["unit"])
            if pos is None or r["L"] == "":
                continue
            r["pos"], r["V"], r["L"] = pos, float(r["V"]), float(r["L"])
            r["cells_negative"], r["n_seeds"] = int(r["cells_negative"]), int(r["n_seeds"])
            rows.append(r)

    out = []
    for bench in ("M", "D"):
        b = [r for r in rows if r["bench"] == bench]
        end = [r for r in b if r["pos"] == "end"]
        cen = [r for r in b if r["pos"] == "centre"]

        a1_e, a1_c = share(end, lambda r: r["L"] < L_MIN), share(cen, lambda r: r["L"] < L_MIN)
        out.append({"claim": "A1", "bench": bench, "ends": round(a1_e, 4), "centre": round(a1_c, 4),
                    "holds": a1_e > a1_c, "note": "share of units with L < 0.98"})

        if bench == "M":
            doses = sorted({r["dose"] for r in b})
            wins, detail = 0, []
            for d in doses:
                me = statistics.median(r["V"] for r in end if r["dose"] == d)
                mc = statistics.median(r["V"] for r in cen if r["dose"] == d)
                wins += mc > me
                detail.append(f"{d}: centre {mc:.3f} / ends {me:.3f}")
            out.append({"claim": "A2a", "bench": bench, "ends": "", "centre": f"{wins} of {len(doses)} doses",
                        "holds": wins >= 4, "note": "; ".join(detail)})
        else:
            me, mc = statistics.median(r["V"] for r in end), statistics.median(r["V"] for r in cen)
            out.append({"claim": "A2a", "bench": bench, "ends": round(me, 4), "centre": round(mc, 4),
                        "holds": mc > me, "note": "median V at 0.200"})

        ok = lambda r: r["V"] >= V_MIN and r["L"] >= L_MIN
        a2b_e, a2b_c = share(end, ok), share(cen, ok)
        out.append({"claim": "A2b", "bench": bench, "ends": round(a2b_e, 4), "centre": round(a2b_c, 4),
                    "holds": a2b_c > a2b_e, "note": "share of units with V >= 1 and L >= 0.98"})

        vis = [r for r in cen if r["V"] >= V_MIN]
        agree = share(vis, lambda r: r["cells_negative"] in (0, r["n_seeds"]))
        out.append({"claim": "A3", "bench": bench, "ends": "", "centre": round(agree, 4) if vis else "no visible units",
                    "holds": bool(vis) and agree >= 2 / 3,
                    "note": f"{len(vis)} visible central units; share with all seeds agreeing on the sign of delta_out"})

    for claim in ("A1", "A2a", "A2b", "A3"):
        h = [r["holds"] for r in out if r["claim"] == claim]
        verdict = "supported" if all(h) else ("partial" if any(h) else "not supported")
        out.append({"claim": claim, "bench": "M+D", "ends": "", "centre": "", "holds": "", "note": verdict})
    out.append({"claim": "A4", "bench": "-", "ends": "", "centre": "", "holds": "",
                "note": "untested: benches M and D hold two comic prompts"})

    with (DATA / "groove_position_tests.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["claim", "bench", "ends", "centre", "holds", "note"])
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(f"{r['claim']:<4} {r['bench']:<4} ends={r['ends']!s:<8} centre={r['centre']!s:<16} "
              f"{'' if r['holds'] == '' else ('HOLDS' if r['holds'] else 'fails')}  {r['note']}")


if __name__ == "__main__":
    main()
