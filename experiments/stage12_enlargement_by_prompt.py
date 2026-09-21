# -*- coding: utf-8 -*-
"""
experiments/stage12_enlargement_by_prompt.py

Persist the per-prompt table behind the stage-12 enlargement result.

Rule 7 of docs/errors_log.md: a number that lives only in prose has no source. The per-prompt
ratios, the per-style split by how well the annotator could identify the condition, and the
aggregate rho were all quoted in the write-ups and existed in no file. `stage12_bbox_results.csv`
holds the three condition-level rows and nothing underneath them.

Inputs
  data/stage12_bbox_raw.csv       annotated boxes: hash_id -> bbox_area_frac
  data/stage12_bbox_key.csv       sealed key: hash_id -> prompt, condition, seed, duplicate flag
  data/stage12_pattern_results.json   the 4-AFC round, per style

Aggregation, stated because the choice changes the fourth decimal and because the
pre-registration did not name it (see docs/stage12_verifica.md §5):

  * the twenty hidden duplicates are averaged with their original, not dropped;
  * a cell is (prompt, condition, seed); a prompt's value is the mean over its five seeds;
  * rho is the prompt's treated mean over its own baseline mean -- the unit of analysis the
    pre-registration fixed, which is the prompt and not the cell.

    python experiments/stage12_enlargement_by_prompt.py
"""

from __future__ import annotations

import collections
import csv
import itertools
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "stage12_enlargement_by_prompt.csv"
OUT_TESTS = DATA / "stage12_enlargement_tests.csv"
OUT_NOISE = DATA / "stage12_annotator_noise.csv"

CONDITIONS = ["blockshuf_neg_1x", "blockshuf_neg_2x", "preset_pos_2x"]


def cells() -> dict:
    raw = {r["hash_id"]: float(r["bbox_area_frac"])
           for r in csv.DictReader((DATA / "stage12_bbox_raw.csv").open(encoding="utf-8",
                                                                       newline=""))}
    acc = collections.defaultdict(list)
    for k in csv.DictReader((DATA / "stage12_bbox_key.csv").open(encoding="utf-8", newline="")):
        if k["hash_id"] not in raw:
            raise KeyError(f"key row {k['hash_id']} has no annotation in stage12_bbox_raw.csv")
        acc[(k["prompt_id"], k["cond_name"], k["seed"])].append(raw[k["hash_id"]])
    return {k: sum(v) / len(v) for k, v in acc.items()}


# The pre-registration fixed "exact sign-flip permutation on the 10 prompts" and did not name
# the statistic (docs/stage12_verifica.md section 5). All four readings a reasonable person
# would try are computed here rather than one being chosen after seeing the answers.
STATISTICS = {
    "mean_log_ratio": (lambda rho, dpp: [math.log(v) for v in rho],
                       lambda v: statistics.mean(v)),
    "log_mean_ratio": (lambda rho, dpp: [math.log(v) for v in rho],
                       lambda v: math.log(statistics.mean(math.exp(x) for x in v))),
    "mean_ratio_minus_one": (lambda rho, dpp: [v - 1 for v in rho],
                             lambda v: statistics.mean(v)),
    "mean_delta_pp": (lambda rho, dpp: list(dpp), lambda v: statistics.mean(v)),
}


def signflip_p(values: list[float], stat) -> float:
    """Exact two-tailed sign-flip permutation p over all 2^n sign patterns."""
    obs = abs(stat(values))
    n = len(values)
    hits = sum(1 for signs in itertools.product((1, -1), repeat=n)
               if abs(stat([s * v for s, v in zip(signs, values)])) >= obs - 1e-12)
    return hits / 2 ** n


def holm(pvalues: dict) -> dict:
    out, running = {}, 0.0
    for i, cond in enumerate(sorted(pvalues, key=pvalues.get)):
        running = max(running, min(1.0, (len(pvalues) - i) * pvalues[cond]))
        out[cond] = running
    return out


def write_tests(rows: list[dict]) -> None:
    with OUT_TESTS.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["statistic", "condition", "n_prompts", "value",
                    "p_signflip_two_tailed", "p_holm_across_3_conditions", "passes_at_0.05"])
        for name, (prep, stat) in STATISTICS.items():
            raw_p, values = {}, {}
            for cond in CONDITIONS:
                sel = [r for r in rows if r["condition"] == cond]
                v = prep([r["rho"] for r in sel], [r["delta_pp"] for r in sel])
                values[cond] = stat(v)
                raw_p[cond] = signflip_p(v, stat)
            adj = holm(raw_p)
            for cond in CONDITIONS:
                w.writerow([name, cond, len([r for r in rows if r["condition"] == cond]),
                            round(values[cond], 6), round(raw_p[cond], 6),
                            round(adj[cond], 6), "yes" if adj[cond] < 0.05 else "no"])
    print(f"wrote {OUT_TESTS.relative_to(ROOT)}")


def write_noise() -> None:
    """The instrument's own noise, and whether the blinding disturbances moved the hand.

    Two diagnostics the pre-registration promised to publish whatever the outcome. Both lived
    only in prose until now.

      * test-retest, from the 20 hidden duplicates shown with a different mirror state;
      * the regression of annotated area on the disturbances applied at random, on the
        baseline annotations only and excluding the duplicates, because a duplicated image
        would enter the regression twice.
    """
    raw = {r["hash_id"]: float(r["bbox_area_frac"])
           for r in csv.DictReader((DATA / "stage12_bbox_raw.csv").open(encoding="utf-8",
                                                                       newline=""))}
    key = list(csv.DictReader((DATA / "stage12_bbox_key.csv").open(encoding="utf-8",
                                                                   newline="")))
    pairs = [(raw[k["orig_hash_id"]], raw[k["hash_id"]])
             for k in key if k["is_duplicate"] == "1"
             and k["hash_id"] in raw and k["orig_hash_id"] in raw]
    if not pairs:
        raise ValueError("no hidden duplicates found -- the test-retest cannot be computed")
    diffs = [abs(a - b) * 100 for a, b in pairs]
    rel = [abs(a - b) / ((a + b) / 2) for a, b in pairs]

    def pearson(xs, ys):
        mx, my = statistics.mean(xs), statistics.mean(ys)
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sxx = sum((x - mx) ** 2 for x in xs)
        syy = sum((y - my) ** 2 for y in ys)
        return sxy / sxx, sxy / math.sqrt(sxx * syy)

    _, r_retest = pearson([a for a, _ in pairs], [b for _, b in pairs])

    base = [(k, raw[k["hash_id"]]) for k in key
            if k["cond_name"] == "baseline" and k["is_duplicate"] == "0" and k["hash_id"] in raw]

    with OUT_NOISE.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "n", "value", "unit", "r", "p_two_tailed"])
        w.writerow(["test_retest_mean_abs_difference", len(pairs),
                    round(statistics.mean(diffs), 4), "percentage points of canvas", "", ""])
        w.writerow(["test_retest_sd_abs_difference", len(pairs),
                    round(statistics.stdev(diffs), 4), "percentage points of canvas", "", ""])
        w.writerow(["test_retest_median_relative_error", len(pairs),
                    round(statistics.median(rel), 6), "fraction", "", ""])
        w.writerow(["test_retest_correlation", len(pairs), round(r_retest, 6), "pearson r",
                    round(r_retest, 6), ""])
        for col in ("sat_factor", "lum_factor", "noise_sigma"):
            xs = [float(k[col]) for k, _ in base]
            ys = [v * 100 for _, v in base]
            slope, r = pearson(xs, ys)
            n = len(xs)
            tstat = r * math.sqrt((n - 2) / (1 - r * r))
            pval = 2 * (1 - 0.5 * (1 + math.erf(abs(tstat) / math.sqrt(2))))
            w.writerow([f"annotated_area_on_{col}", n, round(slope, 4),
                        "percentage points per unit", round(r, 6), round(pval, 4)])
    print(f"wrote {OUT_NOISE.relative_to(ROOT)}")


def main() -> int:
    cell = cells()
    prompts = sorted({p for p, _, _ in cell})
    breakdown = json.loads((DATA / "stage12_pattern_results.json").read_text(encoding="utf-8"))
    styles = breakdown["style_breakdown"]

    rows = []
    for prompt in prompts:
        base = [v for (p, c, _), v in cell.items() if p == prompt and c == "baseline"]
        if not base:
            raise ValueError(f"{prompt} has no baseline cells")
        mb = sum(base) / len(base)
        for cond in CONDITIONS:
            treated = [v for (p, c, _), v in cell.items() if p == prompt and c == cond]
            if not treated:
                raise ValueError(f"{prompt} has no {cond} cells")
            mt = sum(treated) / len(treated)
            rows.append({
                "prompt_id": prompt,
                "condition": cond,
                "n_seeds": len(treated),
                "baseline_area_frac": round(mb, 6),
                "treated_area_frac": round(mt, 6),
                "rho": round(mt / mb, 6),
                "delta_pp": round((mt - mb) * 100, 4),
                "identified_blockshuf_2x": styles[prompt]["b2_correct"],
                "identified_preset_pos_2x": styles[prompt]["p2_correct"],
                "n_afc_trials": styles[prompt]["total"],
            })

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {OUT.relative_to(ROOT)}  ({len(rows)} rows, {len(prompts)} prompts)")
    write_tests(rows)
    write_noise()
    for cond in CONDITIONS:
        r = [x["rho"] for x in rows if x["condition"] == cond]
        geo = math.exp(sum(math.log(v) for v in r) / len(r))
        print(f"  {cond:18s} mean rho {sum(r)/len(r):.4f}  geometric {geo:.4f}  "
              f"above 1: {sum(1 for v in r if v > 1)}/{len(r)}")
    b2 = [x for x in rows if x["condition"] == "blockshuf_neg_2x"]
    for label, sel in (("identified 2/2", 2), ("identified 0/2", 0)):
        g = [x["rho"] for x in b2 if x["identified_blockshuf_2x"] == sel]
        geo = math.exp(sum(math.log(v) for v in g) / len(g))
        print(f"  {label:18s} n={len(g)}  mean rho {sum(g)/len(g):.4f}  geometric {geo:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
