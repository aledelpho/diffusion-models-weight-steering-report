# -*- coding: utf-8 -*-
"""
experiments/stage7_chromatic_coherence.py

Persist the chromatic-coherence result, and check it against the frozen script's own output.

docs/prereg_chromatic_signatures.md carries the confirmation as three prose tables. The
numbers are reproducible -- `analyze_palette_coherence.py` prints them -- but printing is not
persisting, and the Holm column, the exploratory comparison and the survives/does-not line
existed in no file. That is rule 7.

This script does not re-implement the analysis. It imports `feature_vector` and
`mean_pairwise_cos` from the pre-registered module, repeats its orchestration exactly
(paired difference against the same prompt and seed, seeds averaged first because the unit is
the prompt, per-dimension scaling by the SD over all differences, row normalisation, exact
sign-flip permutation over the prompts), then:

  * asserts every diagonal against data/palette_condition_cosines_stage7.csv, the matrix the
    frozen run wrote, and raises on any disagreement past 5e-4;
  * adds the Holm correction across the six conditions and the registered pass/fail;
  * puts the exploratory column beside the confirmation one, read from
    data/palette_condition_cosines.csv rather than retyped.

    python experiments/stage7_chromatic_coherence.py
"""

from __future__ import annotations

import csv
import itertools
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
sys.path.insert(0, str(HERE))
from analyze_palette_coherence import feature_vector, mean_pairwise_cos  # noqa: E402

FEATURES = DATA / "palette_features_stage7_all.csv"
FROZEN_MATRIX = DATA / "palette_condition_cosines_stage7.csv"
EXPLORATORY_MATRIX = DATA / "palette_condition_cosines.csv"
OUT = DATA / "stage7_chromatic_coherence.csv"

BASELINE = "baseline"
REGISTERED_BAR = 4          # conditions that must survive Holm for "confirmed"
ALPHA = 0.05


def directions() -> tuple[dict, list[str], int]:
    rows = list(csv.DictReader(FEATURES.open(encoding="utf-8")))
    stage_key = "source_csv" if "source_csv" in rows[0] else None
    cell = {}
    for r in rows:
        pid = (r.get(stage_key, ""), r["prompt_sha1"])
        cell[(pid, r["condition"], r["seed"])] = feature_vector(r)

    prompts = sorted({k[0] for k in cell})
    conds = sorted({k[1] for k in cell} - {BASELINE})
    diffs = defaultdict(dict)
    for p in prompts:
        bseeds = {k[2] for k in cell if k[0] == p and k[1] == BASELINE}
        if not bseeds:
            continue
        for c in conds:
            shared = sorted({k[2] for k in cell if k[0] == p and k[1] == c} & bseeds)
            if shared:
                diffs[c][p] = np.mean([cell[(p, c, s)] - cell[(p, BASELINE, s)]
                                       for s in shared], axis=0)

    usable = sorted({p for c in diffs for p in diffs[c]})
    full = [c for c in conds if set(diffs[c]) >= set(usable)]
    allv = np.stack([diffs[c][p] for c in full for p in usable])
    sd = allv.std(axis=0)
    sd[sd < 1e-9] = 1.0
    scaled = {c: np.stack([diffs[c][p] / sd for p in usable]) for c in full}
    unit = {c: v / np.linalg.norm(v, axis=1, keepdims=True) for c, v in scaled.items()}
    return unit, full, len(usable)


def holm(pvalues: dict) -> dict:
    out, running = {}, 0.0
    for i, key in enumerate(sorted(pvalues, key=pvalues.get)):
        running = max(running, min(1.0, (len(pvalues) - i) * pvalues[key]))
        out[key] = running
    return out


def diagonal(path: Path) -> dict:
    out = {}
    for r in csv.DictReader(path.open(encoding="utf-8")):
        name = r[""] if "" in r else r[list(r)[0]]
        out[name] = float(r[name])
    return out


def main() -> int:
    unit, conds, n = directions()
    if n > 16:
        raise ValueError(f"{n} prompts: the exact enumeration this script assumes stops at 16")
    signs = np.array(list(itertools.product([1, -1], repeat=n)))

    observed, raw_p = {}, {}
    for c in conds:
        obs = mean_pairwise_cos(unit[c])
        null = np.array([mean_pairwise_cos(s[:, None] * unit[c]) for s in signs])
        observed[c] = obs
        raw_p[c] = float(np.mean(null >= obs - 1e-12))

    frozen = diagonal(FROZEN_MATRIX)
    for c, v in observed.items():
        if abs(v - frozen[c]) > 5e-4:
            raise ValueError(f"{c}: recomputed {v:.4f} against {frozen[c]:.4f} in "
                             f"{FROZEN_MATRIX.name} -- the frozen run and this one disagree")
    print(f"all {len(observed)} coherences agree with {FROZEN_MATRIX.name} to 4 decimals")

    adj = holm(raw_p)
    explor = diagonal(EXPLORATORY_MATRIX)
    survivors = [c for c in conds if adj[c] < ALPHA]

    within = float(np.mean([observed[c] for c in conds]))
    between = float(np.mean([abs(mean_pairwise_cos(unit[a], unit[b]))
                             for a, b in itertools.combinations(conds, 2)]))

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["condition", "cosine_confirmation", "p_signflip", "p_holm",
                    "survives_holm_0.05", "cosine_exploratory", "shrinkage_ratio"])
        for c in sorted(conds, key=lambda k: -observed[k]):
            e = explor.get(c, float("nan"))
            w.writerow([c, round(observed[c], 4), f"{raw_p[c]:.3e}", f"{adj[c]:.3e}",
                        "yes" if adj[c] < ALPHA else "no", round(e, 4),
                        round(observed[c] / e, 3) if e else ""])
        w.writerow(["MEAN_WITHIN_CONDITION", round(within, 4), "", "", "",
                    round(float(np.mean(list(explor.values()))), 4), ""])
        w.writerow(["MEAN_BETWEEN_CONDITIONS_ABS", round(between, 4), "", "", "", "", ""])
        w.writerow(["WITHIN_MINUS_BETWEEN", round(within - between, 4), "", "", "", "", ""])

    print(f"\n{'condition':<16}{'cosine':>9}{'p':>11}{'Holm':>11}   survives   exploratory")
    for c in sorted(conds, key=lambda k: -observed[k]):
        print(f"{c:<16}{observed[c]:>+9.3f}{raw_p[c]:>11.2e}{adj[c]:>11.2e}"
              f"{'   yes     ' if adj[c] < ALPHA else '   no      '}{explor.get(c, 0):>+9.3f}")
    print(f"\nsurvivors: {len(survivors)} of {len(conds)} against a registered bar of "
          f"{REGISTERED_BAR}  ->  "
          f"{'confirmed' if len(survivors) >= REGISTERED_BAR else 'ambiguous' if len(survivors) > 2 else 'refuted'}")
    print(f"within {within:+.3f}   between |cos| {between:+.3f}   difference {within - between:+.3f}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
