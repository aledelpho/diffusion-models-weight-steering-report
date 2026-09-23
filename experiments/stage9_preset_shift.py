# -*- coding: utf-8 -*-
"""
experiments/stage9_preset_shift.py
==================================
Derive the per-condition feature shifts of the stage 9 bench, and persist them.

WHY THIS EXISTS
    `experiments/build_figures_stage12.py` line 405 carried three numbers as literals:

        ("preset_pos_2x", "preset_pos x2",
         [(-3.30, "L* -3.30 (darkens)"), (-3.54, "colorfulness -3.54"), (+0.07, "lbp_entropy +0.07")])

    They are correct -- all three reproduce from the feature tables to four decimals -- but the
    rule that produces them was written down nowhere, which made them unverifiable in practice
    and put them in breach of rule 7. That is pitfall 40 in its exact form: a figure whose
    caption was typed by hand rather than read out of a measurement.

THE AGGREGATION, WHICH IS NOT THE SAME FOR ALL THREE
    Every shift is PAIRED: each treated render is differenced against the baseline of its own
    prompt and its own seed, and the differences are averaged. What differs is the reduction
    inside one image:

      * L*              the MASS-WEIGHTED mean of the six swatch L* values, weighting `swN_L`
                        by `swN_share`. Paper and ink are excluded. This weighting is the part
                        nobody recorded, and computing L* unweighted gives -2.09, not -3.30.
      * colorfulness_hs one value per image already; a plain paired mean.
      * lbp_entropy     one value per image already; a plain paired mean.

    Reproduced 2026-09-23: preset_pos_2x gives L* -3.3033, colorfulness -3.5407,
    lbp_entropy +0.0698, against the published -3.30, -3.54 and +0.07.

OUTPUT
    data/stage9_preset_shift.csv -- one row per (condition, feature), with the paired mean, the
    standard deviation across cells, the number of cells and the aggregation rule named in the
    row itself, so a reader never has to guess which of the two it was.
"""
from __future__ import annotations

import csv
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PALETTE = DATA / "palette_features_stage9.csv"
STYLE = DATA / "style_features_stage9.csv"
OUT = DATA / "stage9_preset_shift.csv"

SWATCHES = range(1, 7)
PLAIN_FEATURES = ["colorfulness_hs", "lbp_entropy"]


def _rows(path: Path) -> list[dict]:
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))


def _cell(row: dict) -> tuple[str, str]:
    """A cell is one prompt and one seed. Both tables name the prompt differently."""
    prompt = next(row[k] for k in row if "prompt" in k.lower())
    return prompt, row["seed"]


def mass_weighted_L(row: dict) -> float:
    """The six swatch L* values, weighted by the share of the frame each swatch occupies."""
    w = [float(row[f"sw{i}_share"]) for i in SWATCHES]
    total = sum(w)
    if total <= 0:
        raise ValueError(f"{row.get('file')}: swatch shares sum to {total}, cannot weight")
    return sum(float(row[f"sw{i}_L"]) * wi for i, wi in zip(SWATCHES, w)) / total


def paired(rows: list[dict], condition: str, value) -> tuple[float, float, int]:
    cond_key = next(k for k in rows[0] if "cond" in k.lower())
    base = {_cell(r): r for r in rows if r[cond_key] == "baseline"}
    diffs = []
    for r in rows:
        if r[cond_key] != condition:
            continue
        b = base.get(_cell(r))
        if b is None:
            continue                      # a treated cell with no baseline is skipped, and counted
        diffs.append(value(r) - value(b))
    if not diffs:
        return None, None, 0
    return st.mean(diffs), (st.stdev(diffs) if len(diffs) > 1 else 0.0), len(diffs)


def main() -> int:
    pal, sty = _rows(PALETTE), _rows(STYLE)
    pal_cond = next(k for k in pal[0] if "cond" in k.lower())
    sty_cond = next(k for k in sty[0] if "cond" in k.lower())

    out = []
    for cond in sorted({r[pal_cond] for r in pal} - {"baseline"}):
        m, sd, n = paired(pal, cond, mass_weighted_L)
        if n == 0:
            # chaos_edges_v2 rides on four prompts of another corpus and has no baseline here.
            # It is named rather than dropped: a condition that silently disappears is worse.
            out.append({"condition": cond, "feature": "L_star", "paired_mean": "not computable",
                        "sd_across_cells": "", "n_cells": 0,
                        "aggregation": "no baseline for this condition in this bench",
                        "source": "data/palette_features_stage9.csv"})
            continue
        out.append({"condition": cond, "feature": "L_star", "paired_mean": f"{m:.4f}",
                    "sd_across_cells": f"{sd:.4f}", "n_cells": n,
                    "aggregation": "mass-weighted mean of sw1..sw6 L* by swN_share; "
                                   "paper and ink excluded",
                    "source": "data/palette_features_stage9.csv"})
    for cond in sorted({r[sty_cond] for r in sty} - {"baseline"}):
        for feat in PLAIN_FEATURES:
            if feat not in sty[0]:
                continue
            m, sd, n = paired(sty, cond, lambda r, f=feat: float(r[f]))
            if n == 0:
                out.append({"condition": cond, "feature": feat, "paired_mean": "not computable",
                            "sd_across_cells": "", "n_cells": 0,
                            "aggregation": "no baseline for this condition in this bench",
                            "source": "data/style_features_stage9.csv"})
                continue
            out.append({"condition": cond, "feature": feat, "paired_mean": f"{m:.4f}",
                        "sd_across_cells": f"{sd:.4f}", "n_cells": n,
                        "aggregation": "plain paired mean, one value per image",
                        "source": "data/style_features_stage9.csv"})

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["condition", "feature", "paired_mean",
                                          "sd_across_cells", "n_cells", "aggregation", "source"])
        w.writeheader()
        w.writerows(out)

    # The figure's three published numbers, checked against what this script derives.
    want = {("preset_pos_2x", "L_star"): -3.30,
            ("preset_pos_2x", "colorfulness_hs"): -3.54,
            ("preset_pos_2x", "lbp_entropy"): 0.07}
    print(f"wrote {OUT.relative_to(ROOT)} -- {len(out)} rows")
    for row in out:
        k = (row["condition"], row["feature"])
        if k in want:
            got = float(row["paired_mean"])
            ok = abs(got - want[k]) < 0.005
            print(f"  {k[0]:18s} {k[1]:16s} {got:+8.4f}  published {want[k]:+.2f}  "
                  f"{'MATCHES' if ok else 'DOES NOT MATCH'}  (n = {row['n_cells']})")
            if not ok:
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
