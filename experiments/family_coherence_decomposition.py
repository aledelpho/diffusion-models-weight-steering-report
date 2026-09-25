# -*- coding: utf-8 -*-
"""
experiments/family_coherence_decomposition.py
=============================================
POST-HOC and DESCRIPTIVE. Reads data/family_coherence_pairs.csv, produced by the
pre-registered experiments/family_coherence.py, and breaks the single family gap G into
the cosine of every family pair.

This script exists to CHECK whether the pre-registered statistic measures what its name
says. It reports no p-value and supports no claim; see
docs/prereg_family_coherence_amendment_02.md for what it found and what was withdrawn.
"""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
COMICS = {"A1", "A2", "B"}


def main():
    rows = list(csv.DictReader((DATA / "family_coherence_pairs.csv").open(encoding="utf-8")))
    by_pair = defaultdict(list)
    comics_w, comics_b, full_w, full_b = (defaultdict(list) for _ in range(4))
    for r in rows:
        arm, c = r["arm"], float(r["cosine"])
        fa, fb = r["family_a"], r["family_b"]
        by_pair[(arm, tuple(sorted((fa, fb))))].append(c)
        (full_w if fa == fb else full_b)[arm].append(c)
        if fa in COMICS and fb in COMICS:
            (comics_w if fa == fb else comics_b)[arm].append(c)

    out = []
    for (arm, fam), vals in sorted(by_pair.items()):
        out.append(dict(arm=arm, family_a=fam[0], family_b=fam[1],
                        same_family=int(fam[0] == fam[1]), n_pairs=len(vals),
                        cos_mean=round(statistics.mean(vals), 6),
                        cos_median=round(statistics.median(vals), 6),
                        cos_sd=round(statistics.stdev(vals), 6) if len(vals) > 1 else ""))
    with (DATA / "family_coherence_by_family_pair.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)

    rest = []
    for arm in sorted(full_w):
        row = dict(arm=arm,
                   W_all4=round(statistics.mean(full_w[arm]), 6),
                   Bt_all4=round(statistics.mean(full_b[arm]), 6),
                   G_all4=round(statistics.mean(full_w[arm]) - statistics.mean(full_b[arm]), 6),
                   n_within_all4=len(full_w[arm]), n_between_all4=len(full_b[arm]))
        if arm in comics_w and arm in comics_b:
            row.update(W_comics_only=round(statistics.mean(comics_w[arm]), 6),
                       Bt_comics_only=round(statistics.mean(comics_b[arm]), 6),
                       G_comics_only=round(statistics.mean(comics_w[arm]) - statistics.mean(comics_b[arm]), 6),
                       n_within_comics=len(comics_w[arm]), n_between_comics=len(comics_b[arm]))
        rest.append(row)
    keys = ["arm", "W_all4", "Bt_all4", "G_all4", "n_within_all4", "n_between_all4",
            "W_comics_only", "Bt_comics_only", "G_comics_only", "n_within_comics", "n_between_comics"]
    with (DATA / "family_coherence_restricted.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rest:
            w.writerow({k: r.get(k, "") for k in keys})
    for r in rest:
        print("  ", r)


if __name__ == "__main__":
    main()
