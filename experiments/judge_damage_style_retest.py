#!/usr/bin/env python3
"""Determinism re-test. Amendment 01 to docs/prereg_damage_or_style.md.

The first version selected items by sorting item_id, which put all 16 in arm A and left arm B
never re-tested. This takes 8 items from EACH arm, both orders: 32 calls.

    python experiments/judge_damage_style_retest.py --renders "<...>" --model qwen3.8:27b
"""
import argparse, csv, os, pathlib, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from judge_damage_style_run import items_A, items_B, foil_table, run, OUT

SNAP = pathlib.Path("data/damage_style_answers_run1.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--url", default="http://127.0.0.1:11434")
    a = ap.parse_args()
    if not OUT.exists():
        sys.exit("nothing to re-test")
    if not SNAP.exists():
        shutil.copy(OUT, SNAP)
        print(f"snapshot written to {SNAP}")
    orig = list(csv.DictReader(SNAP.open(encoding="utf-8")))
    pick = []
    for arm in ("A", "B"):
        ids = sorted({r["item_id"] for r in orig if r["arm"] == arm})[:8]
        pick += ids
    print(f"re-testing {len(pick)} items, 8 per arm, both orders = {len(pick)*2} calls")
    keep = [r for r in orig if r["item_id"] not in pick]
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(orig[0].keys()))
        w.writeheader()
        for r in keep:
            w.writerow(r)
    foils = foil_table()
    todo = [it for it in items_A(a.renders) + items_B(a.renders, foils) if it["item_id"] in pick]
    run(a, todo, set(), [r for r in keep], set())
    new = {(r["item_id"], r["order"]): r["choice"]
           for r in csv.DictReader(OUT.open(encoding="utf-8")) if r["item_id"] in pick}
    old = {(r["item_id"], r["order"]): r["choice"] for r in orig if r["item_id"] in pick}
    both = [k for k in old if k in new]
    same = sum(1 for k in both if old[k] == new[k])
    rate = same / len(both) if both else float("nan")
    print(f"\ntest-retest: {same}/{len(both)} = {rate:.3f}  -> "
          f"{'PASS' if rate >= 0.95 else 'FAIL -- the run is invalidated and must be reported as such'}")


if __name__ == "__main__":
    main()
