# -*- coding: utf-8 -*-
"""
experiments/judge_capability_analyze.py
======================================
STEP 3. Applies docs/prereg_capability_judge.md sections 4-6 (as amended) to
data/capability_judge_raw.csv. Computes nothing that is not frozen there.

Order, and it matters: the guards run first and can end the study.
  G1 test-retest agreement on the 30 repeated images, per question. Below 0.80 -> STOP.
  G2 yes-bias, the share of yes on the positive polarity. Outside [0.05, 0.95] -> STOP.
  G3 polarity consistency. An item whose two polarities AGREE is discarded and counted; above
     20% discarded -> STOP.
  G4 positive control, baselines against early_attn_draw2. Reported. The blocking control is the
     style gate of amendment 01 section 3, which is stronger; this one is descriptive.

Then, on the surviving items:
  score          = the positive-polarity answer, 0 or 1
  Delta cap(p,s) = score(preset p, scene s) - score(baseline, scene s)
  Cost           = mean Delta cap over the 192 cells, per question
  Trade-off      = number of presets whose 8 scenes contain BOTH a -1 and a +1

The null for the trade-off count is the judge's own noise, as the pre-registration requires. It is
simulated: p_flip = 1 - test-retest agreement; for each preset the true displacement is taken as
constant across scenes and equal to its rounded observed mean; the two underlying answers of every
cell are flipped independently with probability p_flip; 10000 draws, random.Random(1337). The
reported p is the share of draws whose total both-signs count reaches the observed one.
"""

from __future__ import annotations

import collections
import csv
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "capability_judge_raw.csv"
OUT = DATA / "capability_judge_tests.csv"
N_SIM = 10000
SEED = 1337
POSCTRL = ("early_attn", "2")


def main():
    if not RAW.exists():
        sys.exit("ABORT: data/capability_judge_raw.csv does not exist. Run judge_capability_run.py first.")
    rows = list(csv.DictReader(RAW.open(encoding="utf-8")))
    models = sorted({r["judge_model"] for r in rows})
    out = []

    for model in models:
        R = [r for r in rows if r["judge_model"] == model]
        print(f"\n=== judge {model}: {len(R)} answers")
        ans = {}
        for r in R:
            ans[(r["file"], r["question"], r["polarity"], r["repetition"])] = int(r["answer"])
        files = sorted({r["file"] for r in R})
        meta = {r["file"]: (r["scene"], r["kind"], r["condition"], r["draw"]) for r in R}

        rec = {}
        for q in ("Q1", "Q2"):
            # G1 test-retest
            pairs = [(ans.get((f, q, "positive", "0")), ans.get((f, q, "positive", "1")))
                     for f in files if (f, q, "positive", "1") in ans]
            pairs = [(a, b) for a, b in pairs if a in (0, 1) and b in (0, 1)]
            rt = sum(1 for a, b in pairs if a == b) / len(pairs) if pairs else float("nan")
            # G3 polarity
            items, agree_n, tot = {}, 0, 0
            for f in files:
                p, n = ans.get((f, q, "positive", "0")), ans.get((f, q, "negative", "0"))
                if p not in (0, 1) or n not in (0, 1):
                    continue
                tot += 1
                if p == n:
                    agree_n += 1
                else:
                    items[f] = p
            pol_bad = agree_n / tot if tot else float("nan")
            # G2 yes-bias
            yes = statistics.mean(items.values()) if items else float("nan")
            rec[q] = dict(retest=rt, n_retest=len(pairs), polarity_discarded=pol_bad,
                          n_items=len(items), yes_share=yes, items=items)
            print(f"  {q}: test-retest {rt:.3f} (n={len(pairs)})  "
                  f"polarity discarded {pol_bad:.3f}  yes {yes:.3f}  usable items {len(items)}")

        stop = []
        for q in ("Q1", "Q2"):
            if not (rec[q]["retest"] >= 0.80):
                stop.append(f"{q} test-retest {rec[q]['retest']:.3f} < 0.80")
            if not (0.05 <= rec[q]["yes_share"] <= 0.95):
                stop.append(f"{q} yes-share {rec[q]['yes_share']:.3f} outside [0.05, 0.95]")
            if rec[q]["polarity_discarded"] > 0.20:
                stop.append(f"{q} polarity discarded {rec[q]['polarity_discarded']:.3f} > 0.20")

        res = dict(judge_model=model, verdict="", **{f"{q}_{k}": rec[q][k] for q in ("Q1", "Q2")
                   for k in ("retest", "n_retest", "polarity_discarded", "n_items", "yes_share")})

        if stop:
            res["verdict"] = "judge_unusable: " + "; ".join(stop)
            print(f"  VERDICT: {res['verdict']}")
            out.append(res)
            continue

        for q in ("Q1", "Q2"):
            it = rec[q]["items"]
            base = {meta[f][0]: v for f, v in it.items() if meta[f][1] == "baseline"}
            cells = collections.defaultdict(dict)
            for f, v in it.items():
                sc, kind, cond, draw = meta[f]
                if kind == "baseline" or sc not in base:
                    continue
                cells[(cond, draw)][sc] = v - base[sc]
            allv = [v for d in cells.values() for v in d.values()]
            cost = statistics.mean(allv) if allv else float("nan")
            both = [p for p, d in cells.items() if any(v > 0 for v in d.values())
                    and any(v < 0 for v in d.values())]
            # null from judge noise
            pflip = 1.0 - rec[q]["retest"]
            rng = random.Random(SEED)
            ge = 0
            keys = sorted(cells)
            truth = {}
            for p in keys:
                m = round(statistics.mean(cells[p].values()))
                truth[p] = {sc: (base[sc], min(1, max(0, base[sc] + m))) for sc in cells[p]}
            for _ in range(N_SIM):
                c = 0
                for p in keys:
                    d = []
                    for sc, (sb, sp) in truth[p].items():
                        b = 1 - sb if rng.random() < pflip else sb
                        a = 1 - sp if rng.random() < pflip else sp
                        d.append(a - b)
                    if any(x > 0 for x in d) and any(x < 0 for x in d):
                        c += 1
                if c >= len(both):
                    ge += 1
            p_trade = (1 + ge) / (1 + N_SIM)
            per_scene = {sc: round(statistics.mean([cells[p][sc] for p in keys if sc in cells[p]]), 4)
                         for sc in sorted(base)}
            pc = [v for sc, v in (cells.get(POSCTRL) or {}).items()]
            res[f"{q}_cost"] = cost
            res[f"{q}_n_cells"] = len(allv)
            res[f"{q}_tradeoff_presets"] = len(both)
            res[f"{q}_tradeoff_p_vs_judge_noise"] = p_trade
            res[f"{q}_p_flip"] = pflip
            res[f"{q}_poscontrol_early_attn_d2_mean"] = round(statistics.mean(pc), 4) if pc else ""
            for sc, v in per_scene.items():
                res[f"{q}_scene_{sc}"] = v
            print(f"  {q}: cost {cost:+.4f} over {len(allv)} cells | trade-off presets {len(both)} "
                  f"(p vs judge noise {p_trade:.4f}) | per scene {per_scene}")

        v = []
        for q in ("Q1", "Q2"):
            if res[f"{q}_tradeoff_p_vs_judge_noise"] < 0.05:
                v.append(f"{q}:trade_off")
            elif abs(res[f"{q}_cost"]) <= res[f"{q}_p_flip"]:
                v.append(f"{q}:no_cost")
            elif res[f"{q}_cost"] < 0:
                v.append(f"{q}:uniform_cost")
            else:
                v.append(f"{q}:gain_requires_replication")
        res["verdict"] = " ".join(v)
        print(f"  VERDICT: {res['verdict']}")
        out.append(res)

    keys = []
    for r in out:
        for k in r:
            if k not in keys:
                keys.append(k)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in out:
            w.writerow({k: (round(r[k], 6) if isinstance(r.get(k), float) else r.get(k, "")) for k in keys})
    print(f"\n  wrote data/capability_judge_tests.csv ({len(out)} judge(s))")


if __name__ == "__main__":
    main()
