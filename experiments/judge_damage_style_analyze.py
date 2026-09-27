#!/usr/bin/env python3
"""Analysis for docs/prereg_damage_or_style.md. Reads data/damage_style_answers.csv.

Scoring rule, frozen in the pre-registration: a cell counts only when BOTH orders agree.
Disagreements are the position-bias measure; they are counted and discarded, never tie-broken.
"""
import collections, csv, itertools, math, pathlib, sys
import numpy as np

OUT = pathlib.Path("data/damage_style_answers.csv")
BLOCKS = [f"Block_{i}" for i in range(1, 7)]
DOSES = ["0.050", "0.200"]


def load():
    rows = list(csv.DictReader(OUT.open(encoding="utf-8")))
    by = collections.defaultdict(dict)
    for r in rows:
        by[(r["arm"], r["item_id"])][r["order"]] = r
    return rows, by


def cells(by, arm):
    """(item, verdict) where verdict is 1 (both orders hit), 0 (both miss) or None (disagree)."""
    out = []
    for (a, iid), d in by.items():
        if a != arm or len(d) < 2:
            continue
        h = [d["0"]["hit"], d["1"]["hit"]]
        if "-1" in h or "" in h:
            out.append((d["0"], None)); continue
        h = [int(x) for x in h]
        out.append((d["0"], 1 if h == [1, 1] else (0 if h == [0, 0] else None)))
    return out


def share(cs):
    good = [v for _, v in cs if v is not None]
    return (np.mean(good) if good else float("nan")), len(good), len(cs)


def main():
    if not OUT.exists():
        sys.exit(f"{OUT} does not exist -- nothing was run")
    rows, by = load()
    print(f"answers: {len(rows)}   items: {len(by)}")
    for arm in ("A_null", "B_null", "A", "B"):
        n = len([1 for (a, _) in by if a == arm])
        print(f"   {arm:7s} {n:4d} items")
    print()
    # ---- nulls and position bias -------------------------------------------------
    for arm in ("A_null", "B_null"):
        sub = [r for r in rows if r["arm"] == arm and r["choice"]]
        if sub:
            s = sum(1 for r in sub if r["choice"] == "A") / len(sub)
            print(f"NULL {arm:7s} A-share {s:.3f} over {len(sub)} calls "
                  f"-> {'inside' if 0.30 <= s <= 0.70 else 'OUTSIDE'} [0.30,0.70]")
    allc = [r for r in rows if r["choice"] and r["arm"] in ("A", "B")]
    print(f"position: overall A-share {sum(1 for r in allc if r['choice']=='A')/len(allc):.3f}")
    bad = sum(1 for r in rows if not r["choice"]) / len(rows)
    print(f"unparseable: {bad:.2%}")
    print()
    # ---- D1, D2 -------------------------------------------------------------------
    A = cells(by, "A")
    print("ARM A -- damage (share of order-agreeing cells calling the perturbed image defective)")
    print(f"{'block':10s}" + "".join(f"{d:>12s}" for d in DOSES))
    dmg = {}
    for b in BLOCKS:
        line = f"{b:10s}"
        for d in DOSES:
            cs = [(r, v) for r, v in A if r["block"] == b and r["dose"] == d]
            s, n, tot = share(cs)
            dmg[(b, d)] = s
            line += f"   {s:.3f}({n:2d}/{tot:2d})"
        print(line)
    for d in DOSES:
        cs = [(r, v) for r, v in A if r["dose"] == d]
        s, n, tot = share(cs)
        print(f"{'POOLED':10s} dose {d}: {s:.3f}  ({n} usable of {tot}, "
              f"{(tot-n)/tot:.1%} order disagreement)")
    p200 = share([(r, v) for r, v in A if r["dose"] == "0.200"])[0]
    print(f"\nD1  dose 0.200 share {p200:.3f}  -> "
          f"{'CONFIRMED' if p200 > 0.75 else ('FALSIFIED' if p200 < 0.55 else 'GREY')}")
    up = sum(1 for b in BLOCKS if dmg[(b, '0.200')] > dmg[(b, '0.050')])
    print(f"D2  damage grows with dose in {up}/6 blocks -> "
          f"{'CONFIRMED' if up >= 5 else ('FALSIFIED' if up <= 3 else 'GREY')}")
    print()
    # ---- D3 -----------------------------------------------------------------------
    B = cells(by, "B")
    print("ARM B -- style identity (share choosing the magnitude-matched same-block candidate)")
    print(f"{'block':10s}" + "".join(f"{d:>12s}" for d in DOSES) + "      mean")
    mat = {}
    for b in BLOCKS:
        line = f"{b:10s}"; vals = []
        for d in DOSES:
            cs = [(r, v) for r, v in B if r["block"] == b and r["dose"] == d]
            s, n, tot = share(cs); mat[(b, d)] = s; vals.append(s)
            line += f"   {s:.3f}({n:2d}/{tot:2d})"
        print(line + f"   {np.nanmean(vals):.3f}")
    pooled, n, tot = share(B)
    above = sum(1 for b in BLOCKS if np.nanmean([mat[(b, d)] for d in DOSES]) > 0.50)
    print(f"\nD3  pooled {pooled:.3f} ({n} usable of {tot}), blocks above 0.50: {above}/6 -> "
          f"{'CONFIRMED' if pooled > 0.60 and above >= 5 else ('FALSIFIED' if pooled <= 0.55 else 'GREY')}")
    # exact sign test over the 12 block x dose cells
    k = sum(1 for b in BLOCKS for d in DOSES if mat[(b, d)] > 0.5)
    p = sum(math.comb(12, i) for i in range(k, 13)) / 2 ** 12
    print(f"    exact sign test over 12 block x dose cells: {k}/12 above chance, one-sided p = {p:.5f}")
    print()
    # ---- D4 -----------------------------------------------------------------------
    xs = [dmg[(b, d)] for b in BLOCKS for d in DOSES]
    ys = [mat[(b, d)] for b in BLOCKS for d in DOSES]
    m = [i for i in range(len(xs)) if not (np.isnan(xs[i]) or np.isnan(ys[i]))]
    if len(m) > 2:
        x = np.array([xs[i] for i in m]); y = np.array([ys[i] for i in m])
        x = x - x.mean(); y = y - y.mean()
        rho = float(x @ y / math.sqrt((x @ x) * (y @ y))) if x.any() and y.any() else float("nan")
        print(f"D4  rho(damage, matching) over {len(m)} cells = {rho:+.3f} -> "
              f"{'CONFIRMED' if abs(rho) < 0.60 else ('ARM B DISCARDED' if rho > 0.80 else 'GREY')}")
    print()
    # ---- D5, D6 --------------------------------------------------------------------
    rd = sorted(BLOCKS, key=lambda b: -np.nanmean([dmg[(b, d)] for d in DOSES]))
    rm = sorted(BLOCKS, key=lambda b: -np.nanmean([mat[(b, d)] for d in DOSES]))
    print(f"D5  damage ranking   {rd}")
    print(f"    matching ranking {rm}")
    i, j = rd.index("Block_6"), rm.index("Block_6")
    print(f"    Block_6 is {i+1} on damage and {j+1} on matching -> "
          f"{'CONFIRMED' if i < 2 and j < 2 else ('FALSIFIED' if i >= 3 and j >= 3 else 'GREY')}")
    for sg in ("pos", "neg"):
        cs = [(r, v) for r, v in B if r["block"] == "Block_6" and r["dose"] == "0.200"
              and r["sign"] == sg]
        print(f"D6  Block_6 0.200 {sg}: matching {share(cs)[0]:.3f}")
    print()
    # ---- the quadrant ---------------------------------------------------------------
    print("THE READING (pre-registered quadrants), per block x dose")
    print(f"{'cell':18s} {'damage':>8s} {'matching':>9s}   verdict")
    for b in BLOCKS:
        for d in DOSES:
            D, M = dmg[(b, d)], mat[(b, d)]
            if np.isnan(D) or np.isnan(M):
                v = "insufficient"
            elif D > 0.75 and M > 0.60:
                v = "a style that costs quality"
            elif D > 0.75:
                v = "pure damage"
            elif M > 0.60:
                v = "a clean style"
            else:
                v = "nothing happened"
            print(f"{b+' @'+d:18s} {D:8.3f} {M:9.3f}   {v}")


if __name__ == "__main__":
    main()
