"""MOSS3b block A - blind confirmation page (docs/prereg_moss_atlas2.md; MOSS2 protocol). Written 2026-10-27 after the
renders, before any label.

  python moss_atlas2_page.py           # data/moss_atlas2_confirm_key.csv, Text2Img/occhio_MOSS3.html
  python moss_atlas2_page.py --rules   # once data/moss_atlas2_confirm_labels.csv exists

Each card: two pairs of the blacksmith at 2718281, before -> after, one at T10 (MOSS3 atlas) and one at R50 (MOSS3b),
random order, unlabelled. Matched: the same cell (12, drawn before the atlas). Control: cell i at T10 with cell i+6 at R50
(12). 4 matched cards repeated. Rule: matched >= 0.67 and control <= 0.33; a cell is confirmed at >= 0.5.
"""
import csv, os, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import moss_gate as G
import moss_atlas2 as M
from eye_grid_page import thumb, build

KEY, LAB = M.KEY, M.LAB
OPTS = [("stesso", "stesso tipo"), ("simile", "qualcosa di simile"), ("diversi", "in modi diversi"), ("nonsivede", "non si vede")]


def path(R, setting, c):
    folder = "benchmark_moss_atlas" if setting == "T10" else M.FOLDER
    return R / folder / f"{setting}_P01_blacksmith_{c}_seed{M.SEED}_00001_.png"


def main():
    vm = Path(os.path.expanduser("~/mnt/D:--StabilityMatrix-win-x64--Data--Images--Text2Img"))
    R = vm if vm.exists() else G.IMG; root = str(R); rng = random.Random(20261027)
    C = M.CONFIRM
    cards = [{"kind": "matched", "t10": c, "r50": c} for c in C] + [{"kind": "control", "t10": c, "r50": C[(i + 6) % 12]} for i, c in enumerate(C)]
    rng.shuffle(cards)
    reps = rng.sample([i for i, c in enumerate(cards) if c["kind"] == "matched"], 4); order = list(range(len(cards)))
    for i in reps:
        j = order.index(i); order.insert(rng.randint(min(j + 6, len(order)), len(order)), i)
    key, units, seen = [], [], set()
    for n, i in enumerate(order, 1):
        c = cards[i]; uid = f"X{n:02d}"; t10_first = rng.random() < 0.5
        key.append({"unit": uid, "kind": c["kind"], "t10_cell": c["t10"], "r50_cell": c["r50"], "t10_first": int(t10_first), "repeat": int(i in seen)}); seen.add(i)
        pairs = [("T10", c["t10"]), ("R50", c["r50"])]
        if not t10_first:
            pairs.reverse()
        rows = []
        for k, (st, cell) in enumerate(pairs, 1):
            a = thumb(str(path(R, st, "plain")), root); b = thumb(str(path(R, st, cell)), root)
            rows.append({"label": f"coppia {k}", "cells": [{"t": a[0], "f": a[1]}, {"t": b[0], "f": b[1]}]})
        units.append({"id": uid, "title": f"Scheda {n:02d}", "groups": [{"id": "g", "name": "", "cols": ["prima", "dopo"], "rows": rows}]})
    with open(KEY, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    build(os.path.join(root, "occhio_MOSS3.html"), "MOSS3 · lo stesso cambiamento?", units,
          [("same", "Il cambiamento è dello stesso tipo nelle due coppie?", OPTS)], OPTS, "moss3_confirm_v1", "moss_atlas2_confirm_labels.csv")
    print("cards", len(units), "->", os.path.join(root, "occhio_MOSS3.html"))


def rules():
    K = {r["unit"]: r for r in csv.DictReader(open(KEY, encoding="utf-8"))}
    L = {r["unit"]: r for r in csv.DictReader(open(LAB, encoding="utf-8"))}
    sc = {"stesso": 1.0, "simile": 0.5, "diversi": 0.0}
    def score(kind):
        v = [sc[L[u]["same"]] for u, k in K.items() if k["kind"] == kind and k["repeat"] == "0" and L.get(u, {}).get("same") in sc]
        return (sum(v) / len(v) if v else float("nan")), len(v)
    m, c = score("matched"), score("control")
    print(f"matched {m[0]:.2f} (n {m[1]}), control {c[0]:.2f} (n {c[1]}) ->", "CONFIRMED" if m[0] >= 0.67 and c[0] <= 0.33 else "NOT CONFIRMED")
    for u, k in K.items():
        if k["kind"] == "matched" and k["repeat"] == "0":
            a = L.get(u, {}).get("same", "")
            print(f"  {k['t10_cell']}: {a} ->", "confirmed" if a in sc and sc[a] >= 0.5 else ("not visible" if a == "nonsivede" else "not confirmed"))
    rep = {}
    for u, k in K.items():
        if k["kind"] == "matched":
            rep.setdefault(k["t10_cell"], []).append(L.get(u, {}).get("same", ""))
    same = [len(set(v)) == 1 for v in rep.values() if len(v) == 2]
    print(f"repeats {sum(same)} of {len(same)} identical")


if __name__ == "__main__":
    rules() if "--rules" in sys.argv else main()
