# -*- coding: utf-8 -*-
"""
experiments/check_historical_numbers.py
=======================================
Holds `data/historical_numbers.csv` to its own sources.

The old monolithic README carried its results as prose. A transcription of every number in it
was made on 2026-09-23 and parked in `data/data-temporary.md`, which left the project with two
lists of numbers and no relation between them. `data/historical_numbers.csv` is the merge: one
row per historical figure, carrying what the old README said, what the repository says now, the
file that says it, and a verdict. The transcription it came from is kept, verbatim, at
`docs/history_readme_c843d61.md` -- as a source document, not as data.

This script re-reads every row that names a locator and checks the `current_value` against the
file. A row is machine-checkable when it carries:

    source_file  data/<name>.csv
    locator      match:col=value,col=value|field:column

and the `current_value` then has to contain the number that file holds, to the precision the
row states. Rows without a locator are listed by name at the end, so the unchecked part of the
list is visible rather than implied.

Four verdicts are in use, and the script does not invent them:

    reproduced    the old figure and the current file agree
    corrected     the old figure was wrong and the row says what replaced it
    unsupported   the old README asserted a measurement that does not exist in this repository
    not_checked   no file holds it yet

`unsupported` rows are expected to have no source file, and the script says so rather than
failing. Nothing is rendered; reads data/ only.

Usage:
    python experiments/check_historical_numbers.py
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LIST = DATA / "historical_numbers.csv"

# How close the number in the row has to be to the number in the file. The row quotes the file
# to the precision the page publishes, which is often fewer digits.
TOL = 5e-4


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def numbers(s: str) -> list[float]:
    return [float(x) for x in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s or "")]


def resolve(source: str, locator: str) -> tuple[str | None, str]:
    """The cell the locator points at, or None and the reason it could not be read."""
    path = ROOT / source
    if not path.exists():
        return None, f"{source} is not in the repository"
    m = re.fullmatch(r"match:(.+)\|field:(\w+)", locator.strip())
    if not m:
        return None, f"locator {locator!r} is malformed"
    cond = dict(p.split("=", 1) for p in m.group(1).split(","))
    field = m.group(2)
    hits = [r for r in rows(path) if all((r.get(k) or "").strip() == v.strip()
                                         for k, v in cond.items())]
    if len(hits) != 1:
        return None, f"{len(hits)} rows match {cond} in {source}, expected exactly 1"
    if field not in hits[0]:
        return None, f"{source} has no column {field!r}"
    return hits[0][field], ""


def main() -> None:
    if not LIST.exists():
        sys.exit(f"{LIST} is missing: the merged list is what this script checks")
    entries = rows(LIST)
    ok = bad = 0
    problems: list[str] = []
    unchecked: list[str] = []

    for e in entries:
        rid, status, loc = e["id"], e["status"], (e["locator"] or "").strip()
        if not loc:
            unchecked.append(f"{rid} ({status})"
                             + ("  -- no source file, which is the point of the row"
                                if status == "unsupported" else ""))
            continue
        cell, why = resolve(e["source_file"], loc)
        if cell is None:
            bad += 1
            problems.append(f"{rid}: {why}")
            continue
        want, got = numbers(e["current_value"]), numbers(cell)
        if not got:                                  # a text cell, compared as text
            if cell.strip() in (e["current_value"] or ""):
                ok += 1
            else:
                bad += 1
                problems.append(f"{rid}: the row says {e['current_value']!r}, "
                                f"{e['source_file']} holds {cell!r}")
            continue
        if any(abs(g - w) <= max(TOL, 1e-3 * abs(g)) for g in got for w in want):
            ok += 1
        else:
            bad += 1
            problems.append(f"{rid}: the row says {e['current_value']!r}, "
                            f"{e['source_file']} holds {cell!r}")

    print(f"{len(entries)} historical figures in {LIST.relative_to(ROOT)}")
    by = {}
    for e in entries:
        by[e["status"]] = by.get(e["status"], 0) + 1
    for k in ("reproduced", "corrected", "unsupported", "not_checked"):
        if k in by:
            print(f"  {k:12s} {by[k]}")
    print(f"\nchecked against their source file: {ok + bad}   agree: {ok}   disagree: {bad}")
    for p in problems:
        print(f"  ! {p}")
    print(f"\nnot machine-checkable, {len(unchecked)}:")
    for u in unchecked:
        print(f"  - {u}")
    if bad:
        sys.exit(1)
    print("\nevery checkable row agrees with the file it names.")


if __name__ == "__main__":
    main()
