# -*- coding: utf-8 -*-
"""
experiments/measure_parameter_families.py
=========================================
C35 / C36 — do the six kinds of parameter behave differently under the same tool?

    python experiments/measure_parameter_families.py --inert   # which families move anything at all
    python experiments/measure_parameter_families.py --ladder  # dose response of the ones that do

**The inert test needs no baseline and makes no assumption.** `F_norms` (56 `*.scale`),
`F_qknorm` (56 `*.scale`) and `F_mod` (28 `mod.lin`) patch **disjoint** sets of tensors. If any
patch in any of them had an effect, their renders could not coincide. So pixel-identity across the
three is a proof that none of the three did anything, and their common state is the unperturbed
model — which then serves as the baseline this bench never rendered.

No render is generated.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "experiments"))

import groove_or_hole as G  # noqa: E402
import retro_texture_axes as T  # noqa: E402

BENCH = Path("/sessions/rcw-01fzmivsryy2r8cd26detdrb/mnt/benchmark_parameter_families")
for c in (BENCH, Path("C:/StabilityMatrix-win-x64/Data/Images/Text2Img/benchmark_parameter_families")):
    if c.is_dir():
        BENCH = c
        break
ARCH, REND = BENCH / "archive_d100", BENCH / "renders"
INERT = ("norms", "qknorm", "mod")
PAT = re.compile(r"^(P\d\d)_F_([a-z]+)_d([+-][\d.]+)_krea2_seed(\d+)_")


def arr(p: Path):
    import numpy as np
    from PIL import Image
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def inert() -> None:
    import numpy as np
    rows = []
    for P in ("P01", "P02"):
        fs = sorted(ARCH.glob(f"{P}_F_*_d+1.000_krea2_seed42_*.png"))
        ims = {PAT.match(f.name).group(2): arr(f) for f in fs}
        for a, b in itertools.combinations(sorted(ims), 2):
            d = np.abs(ims[a] - ims[b])
            rows.append({"prompt": P, "dose": "+1.000", "family_a": a, "family_b": b,
                         "mean_abs_diff": f"{d.mean():.4f}", "max_abs_diff": int(d.max()),
                         "identical": str(bool(d.max() == 0)),
                         "both_inert": str(a in INERT and b in INERT)})
    with open(DATA / "parameter_families_inert.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    ok = [r for r in rows if r["both_inert"] == "True"]
    bad = [r for r in ok if r["identical"] != "True"]
    print(f"  pairs among {INERT}: {len(ok)}, identical: {len(ok)-len(bad)}, differing: {len(bad)}")
    for r in rows:
        if r["both_inert"] != "True":
            print(f"    {r['prompt']} {r['family_a']:7}vs {r['family_b']:7} mean |d| = {r['mean_abs_diff']:>8}  max {r['max_abs_diff']}")
    print(f"  -> {DATA/'parameter_families_inert.csv'}")


def ladder() -> None:
    """Dose response at seed 42, against the baseline the inert families hand us for free."""
    import numpy as np
    base = {P: ARCH / f"{P}_F_norms_d+1.000_krea2_seed42_00001_.png" for P in ("P01", "P02")}
    for P, p in base.items():
        if not p.is_file():
            sys.exit(f"missing derived baseline: {p}")
    bm = {P: T.measure(p) for P, p in base.items()}   # (coherence, bands[5], var, sat, hue_mean)
    ba = {P: arr(p) for P, p in base.items()}
    rows = []
    for f in sorted(REND.glob("*.png")):
        m = PAT.match(f.name)
        if not m:
            continue
        P, fam, dose, seed = m.groups()
        if seed != "42":
            continue                                  # only seed 42 has a true baseline
        coh, bands, var, sat, hue = T.measure(f)
        bcoh, bbands, bvar, bsat, bhue = bm[P]
        d = np.abs(arr(f) - ba[P])
        rows.append({"prompt": P, "family": fam, "dose": dose, "seed": seed, "file": f.name,
                     "mean_abs_diff": f"{d.mean():.4f}",
                     "coherence": f"{coh:.6f}", "L_vs_baseline": f"{coh/bcoh:.6f}",
                     "band0_ratio": f"{bands[0]/bbands[0]:.6f}",
                     "band4_ratio": f"{bands[4]/bbands[4]:.6f}",
                     "sat_ratio": f"{sat/bsat:.6f}"})
    with open(DATA / "parameter_families_ladder.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f"  {len(rows)} cells -> {DATA/'parameter_families_ladder.csv'}")
    for fam in sorted({r["family"] for r in rows}):
        print(f"\n  {fam}")
        for P in ("P01", "P02"):
            rs = sorted((r for r in rows if r["family"] == fam and r["prompt"] == P),
                        key=lambda r: float(r["dose"]))
            print(f"    {P} |d|  " + " ".join(f"{r['dose']}:{float(r['mean_abs_diff']):6.2f}" for r in rs))
            print(f"    {P}  L   " + " ".join(f"{r['dose']}:{float(r['L_vs_baseline']):6.3f}" for r in rs))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inert", action="store_true")
    ap.add_argument("--ladder", action="store_true")
    a = ap.parse_args()
    if a.inert: inert()
    if a.ladder: ladder()
    if not (a.inert or a.ladder): ap.error("--inert or --ladder")


if __name__ == "__main__":
    main()
