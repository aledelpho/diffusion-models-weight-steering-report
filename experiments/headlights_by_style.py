# -*- coding: utf-8 -*-
"""
experiments/headlights_by_style.py

Persist the per-style headlight table that the notebook quotes.

Rule 7 of docs/errors_log.md: a number that lives only in prose has no source. The per-style
breakdown of the blind headlight round was written into the old README by hand and existed in
no file. This script derives it from the sealed scoring round and writes it to disk, so the
page can name the file its numbers come from.

Inputs
  data/stage9_headlights_raw.csv   the blind scores: hash_id, code, timestamp_ms
  data/stage9_headlights_key.csv   the sealed key: hash_id -> prompt_id, cond_name, seed

Scoring codes, recovered by reconciling against data/stage9_headlights_results.csv:
  0 = off, 1 = can't tell, 2 = lit.

Four images were scored twice during the round (675f3ee8e649, 9690d97c75a1, 24072f70ac4a,
a0b491158a3e); two of them differently. The published rates in stage9_headlights_results.csv
reproduce exactly under "the later score wins", and under no other rule, so that is the rule
applied here and recorded in the output. The only condition the choice touches is rand_pos x2
(2/36 under later-wins, 3/37 under earlier-wins); no headline number depends on it.

    python experiments/headlights_by_style.py
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "stage9_headlights_by_style.csv"

CODE = {"0": "off", "1": "cant_tell", "2": "lit"}


def main() -> int:
    key = {r["hash_id"]: r for r in csv.DictReader((DATA / "stage9_headlights_key.csv")
                                                   .open(encoding="utf-8", newline=""))}
    scored: dict[str, str] = {}
    duplicates: set[str] = set()
    for row in csv.DictReader((DATA / "stage9_headlights_raw.csv")
                              .open(encoding="utf-8", newline="")):
        if row["hash_id"] in scored:
            duplicates.add(row["hash_id"])
        scored[row["hash_id"]] = row["code"]        # later score wins

    tally: dict[tuple[str, str], dict[str, int]] = {}
    for hash_id, code in scored.items():
        k = key.get(hash_id)
        if k is None:
            raise KeyError(f"scored image {hash_id} is not in the sealed key")
        cell = tally.setdefault((k["prompt_id"], k["cond_name"]),
                                {"lit": 0, "off": 0, "cant_tell": 0})
        cell[CODE[code]] += 1

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["prompt_id", "condition", "lit", "off", "cant_tell", "n_scorable", "rate"])
        for (prompt, cond) in sorted(tally):
            c = tally[(prompt, cond)]
            n = c["lit"] + c["off"]
            w.writerow([prompt, cond, c["lit"], c["off"], c["cant_tell"], n,
                        f"{c['lit'] / n:.4f}" if n else ""])

    print(f"wrote {OUT.relative_to(ROOT)}  "
          f"({len(tally)} cells, {len(scored)} images, {len(duplicates)} rescored)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
