"""MOSS2 confirmation - blind key and page (docs/prereg_moss_bench.md, amendment 2; rule fixed here, 2026-10-25, after the
renders and before any label).

  python moss_confirm_page.py      # data/moss_confirm_key.csv, Text2Img/occhio_MOSS2.html
  python moss_confirm_page.py --rules   # once data/moss_confirm_labels.csv exists

Each card shows two pairs, before -> after, of the dwarf at 2645751: one pair made with the turbo (T10), one at 50 steps
(R50), in random order and unlabelled. Matched cards: the same edit in both pairs (6, the confirmation cells). Control
cards: two different edits (6, each edit paired with another by a fixed rotation). 3 matched cards repeated.
Question: "Il cambiamento è dello stesso tipo nelle due coppie?" stesso / qualcosa di simile / in modi diversi / non si vede.

Rule: score 1 / 0.5 / 0 (non si vede excluded), first showings. The confirmation holds if matched cards score >= 0.67 and
control cards <= 0.33; per edit, a matched card at >= 0.5 confirms that edit.
"""
import csv, os, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import moss_gate as G
from eye_grid_page import thumb, build

DATA = HERE.parent / "data"
KEY, LAB = DATA / "moss_confirm2_key.csv", DATA / "moss_confirm2_labels.csv"
FOLDER = "benchmark_moss_bench"
DOSE = "p2"   # amendment 3: d = 2.0 (at d = 1.0 Alessandro saw no change)
EDITS = ["dit06", "dit20", "dit35", "te06", "te15", "te27"]
OPTS = [("stesso", "stesso tipo"), ("simile", "qualcosa di simile"), ("diversi", "in modi diversi"), ("nonsivede", "non si vede")]
f = lambda st, c: f"{st}_D1_dwarf_paladin_{c}_seed2645751_00001_.png"


def main():
    vm = Path(os.path.expanduser("~/mnt/D:--StabilityMatrix-win-x64--Data--Images--Text2Img"))
    R = vm if vm.exists() else G.IMG
    root = str(R); rng = random.Random(20251025)
    cards = [{"kind": "matched", "t10": e, "r50": e} for e in EDITS]
    cards += [{"kind": "control", "t10": e, "r50": EDITS[(i + 3) % 6]} for i, e in enumerate(EDITS)]
    rng.shuffle(cards)
    reps = rng.sample([i for i, c in enumerate(cards) if c["kind"] == "matched"], 3)
    order = list(range(len(cards)))
    for i in reps:
        j = order.index(i); order.insert(rng.randint(min(j + 5, len(order)), len(order)), i)
    key, units, seen = [], [], set()
    for n, i in enumerate(order, 1):
        c = cards[i]; uid = f"M{n:02d}"; t10_first = rng.random() < 0.5
        key.append({"unit": uid, "kind": c["kind"], "t10_edit": c["t10"], "r50_edit": c["r50"], "t10_first": int(t10_first), "repeat": int(i in seen)}); seen.add(i)
        pairs = [("T10", f"{c['t10']}_{DOSE}"), ("R50", f"{c['r50']}_{DOSE}")]
        if not t10_first:
            pairs.reverse()
        rows = []
        for k, (st, cnd) in enumerate(pairs, 1):
            a = thumb(str(R / FOLDER / f(st, "plain")), root); b = thumb(str(R / FOLDER / f(st, cnd)), root)
            rows.append({"label": f"coppia {k}", "cells": [{"t": a[0], "f": a[1]}, {"t": b[0], "f": b[1]}]})
        units.append({"id": uid, "title": f"Scheda {n:02d}", "groups": [{"id": "g", "name": "", "cols": ["prima", "dopo"], "rows": rows}]})
    with open(KEY, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    build(os.path.join(root, "occhio_MOSS2b.html"), "MOSS2 · lo stesso cambiamento? (d = 2)", units,
          [("same", "Il cambiamento è dello stesso tipo nelle due coppie?", OPTS)], OPTS, "moss2_confirm_v2", "moss_confirm2_labels.csv")
    print("cards", len(units), "->", os.path.join(root, "occhio_MOSS2b.html"))


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
            print(f"  {k['t10_edit']}: {a} ->", "confirmed" if a in sc and sc[a] >= 0.5 else "not confirmed")


if __name__ == "__main__":
    rules() if "--rules" in sys.argv else main()
