# -*- coding: utf-8 -*-
"""
experiments/stage12_headlights.py

The second confirmatory hypothesis the stage-12 corpus was built to carry.

docs/prereg_stage12_ingrandimento.md registers, beside the enlargement test, a headlight
confirmation on the same renders: the calibrated preset lights headlights the prompt never
mentions, the block derangement puts them out, with the same clause that a condition reaching
significance with the wrong sign counts as a failure. It was scored on 2026-09-21 against the
criterion frozen in docs/stage12_headlights_criterion.md.

This script does three things the hand-made data/stage12_headlights_results.csv does not:

  * it re-joins every score to the SEALED key of the bounding-box round
    (data/stage12_bbox_key.csv) and raises if a single row disagrees, so the condition labels
    are not taken on trust;
  * it counts the INFORMATIVE prompts -- the ones where any condition differs from another --
    because with n informative units the exact sign-flip floor is 2/2^n and the answer to
    "did it confirm" is decided by that number before any effect size is looked at
    (rules 8 and 11 of docs/errors_log.md);
  * it repeats the whole table excluding the 27 tiles scored before the criterion was
    tightened, which the criterion document promised and did not deliver.

    python experiments/stage12_headlights.py
"""

from __future__ import annotations

import csv
import itertools
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "stage12_headlights_by_style.csv"

KEY_FIELDS = ("prompt_id", "cond_name", "seed", "is_duplicate", "orig_hash_id")
CONDITIONS = ["baseline", "blockshuf_neg_1x", "blockshuf_neg_2x", "preset_pos_2x"]
CLARIFIED_AFTER = 27          # tiles seen before the criterion was tightened


def load() -> list[dict]:
    key = {r["hash_id"]: r
           for r in csv.DictReader((DATA / "stage12_bbox_key.csv").open(encoding="utf-8",
                                                                       newline=""))}
    rows = list(csv.DictReader((DATA / "stage12_headlights_raw.csv").open(encoding="utf-8",
                                                                          newline="")))
    for r in rows:
        k = key.get(r["hash_id"])
        if k is None:
            raise KeyError(f"scored tile {r['hash_id']} is not in the sealed bbox key")
        mismatch = [f for f in KEY_FIELDS if k[f] != r[f]]
        if mismatch:
            raise ValueError(f"tile {r['hash_id']} disagrees with the sealed key on "
                             f"{mismatch} -- the scores were joined to the wrong labels")
        r["view_order"] = int(r["view_order"])
    return rows


def tally(rows: list[dict], prompt: str, cond: str) -> tuple[int, int, int]:
    sel = [r for r in rows if r["prompt_id"] == prompt and r["cond_name"] == cond]
    lit = sum(1 for r in sel if r["score"] == "ACCESO")
    unc = sum(1 for r in sel if r["score"] == "INCERTO")
    return lit, len(sel) - unc, unc          # lit, scorable, uncertain


def signflip_p(values: list[float]) -> float:
    obs = abs(statistics.mean(values))
    n = len(values)
    hits = sum(1 for s in itertools.product((1, -1), repeat=n)
               if abs(statistics.mean([a * v for a, v in zip(s, values)])) >= obs - 1e-12)
    return hits / 2 ** n


def report(rows: list[dict], scope: str, writer) -> None:
    prompts = sorted({r["prompt_id"] for r in rows})
    informative = []
    for p in prompts:
        rates = {c: (tally(rows, p, c)[0]) for c in CONDITIONS}
        if len(set(rates.values())) > 1:
            informative.append(p)
        for c in CONDITIONS:
            lit, scorable, unc = tally(rows, p, c)
            writer.writerow([scope, p, c, lit, scorable, unc,
                             f"{lit / scorable:.4f}" if scorable else "",
                             "yes" if p in informative else "no"])

    print(f"\n-- {scope}")
    print(f"   informative prompts (any condition differs): {len(informative)} of "
          f"{len(prompts)}  {informative}")
    floor = 2 / 2 ** len(informative) if informative else float("nan")
    print(f"   exact sign-flip floor with that many units: 2/2^{len(informative)} = {floor:.4f}"
          + ("   -- no effect of any size can reach 0.05" if not (floor < 0.05) else ""))
    for c in CONDITIONS:
        lit = sum(tally(rows, p, c)[0] for p in prompts)
        sc = sum(tally(rows, p, c)[1] for p in prompts)
        print(f"   {c:18s} {lit:3d} / {sc:3d} = {lit / sc:.3f}")
    for c in CONDITIONS[1:]:
        deltas = [tally(rows, p, c)[0] / 5 - tally(rows, p, "baseline")[0] / 5
                  for p in prompts]
        print(f"   {c:18s} mean delta vs baseline {statistics.mean(deltas):+.3f}   "
              f"exact sign-flip p = {signflip_p(deltas):.4f}")


def main() -> int:
    rows = load()
    originals = [r for r in rows if r["is_duplicate"] == "0"]

    pairs = {}
    for r in rows:
        pairs.setdefault(r["orig_hash_id"], []).append(r["score"])
    repeated = {o: v for o, v in pairs.items() if len(v) > 1}
    disagree = {o: v for o, v in repeated.items() if len(set(v)) > 1}
    print(f"re-shown tiles: {len(repeated)}   disagreements: {len(disagree)}  {disagree}")

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scope", "prompt_id", "condition", "lit", "scorable", "uncertain",
                    "rate", "prompt_is_informative"])
        report(originals, "all_tiles", w)
        report([r for r in originals if r["view_order"] > CLARIFIED_AFTER],
               "after_criterion_tightened", w)
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
