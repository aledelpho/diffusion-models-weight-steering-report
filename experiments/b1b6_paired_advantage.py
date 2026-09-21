# -*- coding: utf-8 -*-
"""
experiments/b1b6_paired_advantage.py

Persist the paired contrast behind the Block_1 vs Block_6 confirmation.

The pre-registration's falsification criterion is a comparison of two means:
V_bar > V_scramble_bar. The report states both and their difference, and the per-prompt
difference -- the quantity that says whether the advantage holds prompt by prompt rather than
only on average -- existed in no file. That is rule 7.

Inputs
  data/rotations_block1_vs_block6_prompt_scores.csv   V(p) and V_scramble(p), 10 prompts
  data/rotations_block1_vs_block6_results.csv         the five measurement spaces

The unit of analysis is the prompt, fixed by the pre-registration; the test is the exact
two-tailed sign-flip permutation over the 10 prompts, floor 2/2^10 = 0.00195.

    python experiments/b1b6_paired_advantage.py
"""

from __future__ import annotations

import csv
import itertools
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SCORES = DATA / "rotations_block1_vs_block6_prompt_scores.csv"
RESULTS = DATA / "rotations_block1_vs_block6_results.csv"
OUT_PROMPTS = DATA / "b1b6_paired_by_prompt.csv"
OUT_SPACES = DATA / "b1b6_paired_by_space.csv"


def signflip_p(values: list[float]) -> float:
    obs = abs(statistics.mean(values))
    n = len(values)
    hits = sum(1 for s in itertools.product((1, -1), repeat=n)
               if abs(statistics.mean([a * v for a, v in zip(s, values)])) >= obs - 1e-12)
    return hits / 2 ** n


def main() -> int:
    rows = list(csv.DictReader(SCORES.open(encoding="utf-8-sig", newline="")))
    if len(rows) != 10:
        raise ValueError(f"expected 10 prompts, found {len(rows)}")

    per_prompt = []
    for r in rows:
        v, vs = float(r["V_p"]), float(r["V_scramble_p"])
        per_prompt.append({"prompt_id": r["prompt_id"],
                           "V": round(v, 6), "V_scramble": round(vs, 6),
                           "paired_advantage": round(v - vs, 6),
                           "exceeds_null": "yes" if v > vs else "no"})

    d = [r["paired_advantage"] for r in per_prompt]
    p = signflip_p(d)
    with OUT_PROMPTS.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(per_prompt[0]))
        w.writeheader()
        w.writerows(per_prompt)

    spaces = list(csv.DictReader(RESULTS.open(encoding="utf-8-sig", newline="")))
    with OUT_SPACES.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["space", "n_features", "V", "p_V", "V_scramble", "p_V_scramble",
                    "paired_advantage", "falsification_passed", "coherence_block1",
                    "coherence_block6", "cross_cosine", "cross_cosine_disattenuated"])
        for s in spaces:
            w.writerow([s["space"], s["n_features"], round(float(s["mean_V"]), 4),
                        s["p_val_V"], round(float(s["mean_V_scramble"]), 4),
                        s["p_val_V_scramble"],
                        round(float(s["mean_V"]) - float(s["mean_V_scramble"]), 4),
                        s["falsification_passed"], round(float(s["coh_b1"]), 4),
                        round(float(s["coh_b6"]), 4),
                        round(float(s["raw_cross_cos_B1_B6"]), 4),
                        round(float(s["disattenuated_cos"]), 4)])

    print(f"paired advantage V - V_scramble: mean {statistics.mean(d):+.4f}   "
          f"sign-flip p {p:.5f}   positive {sum(1 for v in d if v > 0)}/{len(d)}   "
          f"range {min(d):+.3f} .. {max(d):+.3f}")
    print(f"the null itself: V_scramble mean {statistics.mean(r['V_scramble'] for r in per_prompt):+.4f} "
          f"-- two arbitrary scrambles at the same displacement do separate, and by a lot")
    print(f"wrote {OUT_PROMPTS.relative_to(ROOT)} and {OUT_SPACES.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
