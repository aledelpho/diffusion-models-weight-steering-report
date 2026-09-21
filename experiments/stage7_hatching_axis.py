# -*- coding: utf-8 -*-
"""
experiments/stage7_hatching_axis.py

Persist the per-prompt and per-pair table behind the hatching-axis confirmation.

docs/prereg_hatching_axis_stage7.md carries the result as a five-row table in prose. The
numbers underneath it -- sixteen per-prompt differences per family, eighty seed-level pairs per
family -- existed in no file, which is rule 7. This script derives them from the measurement
the pre-registration named and from nothing else.

Inputs
  data/style_features_stage7.csv    600 rows, crosshatch_entropy_mean per image
  data/confirmation_prompts.csv     the 16 prompt hashes the selection rule took

The statistic, fixed by the pre-registration: delta = crosshatch_entropy_mean(pos) - (neg),
averaged over the five seeds of a prompt first, because the unit of analysis is the prompt and
not the cell (pitfall 17). Exact two-tailed sign-flip permutation over the 16 prompts, Holm
across the three families.

One reporting detail this script makes explicit. The published table counts preset and
blockshuffle in the PREDICTED direction and randsign in its OBSERVED one, so randsign's
"11/16 prompts, 50/80 pairs" sits in the same column as "16/16, 80/80" under a different rule.
Both columns are written out here, named.

    python experiments/stage7_hatching_axis.py
"""

from __future__ import annotations

import collections
import csv
import itertools
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT_PAIRS = DATA / "stage7_hatching_pairs.csv"
OUT_SUMMARY = DATA / "stage7_hatching_summary.csv"

METRIC = "crosshatch_entropy_mean"
# family -> (positive arm, negative arm, sign predicted for pos - neg)
FAMILIES = {
    "preset": ("preset_pos", "preset_neg", -1),
    "blockshuffle": ("blockshuf_pos", "blockshuf_neg", +1),
    "randsign": ("rand_pos", "rand_neg", -1),
}


def load() -> dict:
    keep = {r["prompt_sha1"] for r in
            csv.DictReader((DATA / "confirmation_prompts.csv").open(encoding="utf-8-sig",
                                                                    newline=""))}
    cells = collections.defaultdict(dict)
    for r in csv.DictReader((DATA / "style_features_stage7.csv").open(encoding="utf-8-sig",
                                                                      newline="")):
        if r["prompt_sha1"] in keep:
            cells[(r["prompt_sha1"], r["seed"])][r["condition"]] = float(r[METRIC])
    if len(keep) != 16:
        raise ValueError(f"expected 16 confirmation prompts, found {len(keep)}")
    return cells


def signflip_p(values: list[float]) -> float:
    obs = abs(statistics.mean(values))
    n = len(values)
    hits = sum(1 for s in itertools.product((1, -1), repeat=n)
               if abs(statistics.mean([a * v for a, v in zip(s, values)])) >= obs - 1e-12)
    return hits / 2 ** n


def main() -> int:
    cells = load()
    prompts = sorted({p for p, _ in cells})

    pairs, per_prompt = [], {}
    for fam, (pos, neg, predicted) in FAMILIES.items():
        per_prompt[fam] = []
        for prompt in prompts:
            deltas = []
            for (p, seed), c in sorted(cells.items()):
                if p != prompt:
                    continue
                if pos not in c or neg not in c:
                    raise KeyError(f"{prompt}/{seed} is missing an arm of {fam}")
                d = c[pos] - c[neg]
                deltas.append(d)
                pairs.append({"family": fam, "prompt_sha1": prompt, "seed": seed,
                              "pos_arm": round(c[pos], 6), "neg_arm": round(c[neg], 6),
                              "delta": round(d, 6),
                              "matches_prediction": "yes" if d * predicted > 0 else "no"})
            per_prompt[fam].append((prompt, statistics.mean(deltas)))

    with OUT_PAIRS.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pairs[0]))
        w.writeheader()
        w.writerows(pairs)

    raw_p = {fam: signflip_p([d for _, d in per_prompt[fam]]) for fam in FAMILIES}
    holm, running = {}, 0.0
    for i, fam in enumerate(sorted(raw_p, key=raw_p.get)):
        running = max(running, min(1.0, (len(raw_p) - i) * raw_p[fam]))
        holm[fam] = running

    with OUT_SUMMARY.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["family", "predicted_sign", "delta", "p_signflip", "p_holm",
                    "prompts_matching_prediction", "n_prompts",
                    "pairs_matching_prediction", "n_pairs",
                    "prompts_matching_observed_sign", "pairs_matching_observed_sign"])
        for fam, (_, _, predicted) in FAMILIES.items():
            deltas = [d for _, d in per_prompt[fam]]
            mean = statistics.mean(deltas)
            fam_pairs = [x for x in pairs if x["family"] == fam]
            w.writerow([
                fam, "negative" if predicted < 0 else "positive", round(mean, 6),
                f"{raw_p[fam]:.6g}", f"{holm[fam]:.6g}",
                sum(1 for d in deltas if d * predicted > 0), len(deltas),
                sum(1 for x in fam_pairs if x["matches_prediction"] == "yes"), len(fam_pairs),
                sum(1 for d in deltas if d * mean > 0),
                sum(1 for x in fam_pairs if x["delta"] * mean > 0),
            ])
            print(f"{fam:13s} delta {mean:+.4f}  p {raw_p[fam]:.3e}  Holm {holm[fam]:.3e}  "
                  f"predicted-direction prompts {sum(1 for d in deltas if d * predicted > 0)}"
                  f"/{len(deltas)}  pairs "
                  f"{sum(1 for x in fam_pairs if x['matches_prediction'] == 'yes')}"
                  f"/{len(fam_pairs)}")
    print(f"wrote {OUT_PAIRS.relative_to(ROOT)} and {OUT_SUMMARY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
