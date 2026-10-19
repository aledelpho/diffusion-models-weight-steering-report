"""C102 blind page (docs/prereg_te_depth_control.md, section 3). Written 2026-10-19 after the renders, before any label
and before any C102 rule was computed.

48 units (4 prompts x 12 edited conditions; each shows the three seeds as plain -> changed) + 6 repeats, order random
(seed 10202), conditions hidden. One question, positive: "Nelle tre coppie l'immagine cambia nello stesso modo?"

  python te_depth_control_page.py      # data/te_depth_control_key.csv and Text2Img/occhio_C102.html
"""
import csv, os, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_depth_control as T
from eye_grid_page import thumb, build

RNG_SEED, N_REPEAT, MIN_GAP = 10202, 6, 10


def main():
    R = T.img_root(); root = str(R)
    rng = random.Random(RNG_SEED)
    base = [(p, c) for p in T.PROMPTS for c in T.conds()[1:]]
    rng.shuffle(base)
    reps = rng.sample(base, N_REPEAT)
    order = list(base)
    for r in reps:                                     # insert each repeat at least MIN_GAP after its first showing
        i = order.index(r)
        pos = rng.randint(min(i + MIN_GAP, len(order)), len(order))
        order.insert(pos, r)
    key, units, seen = [], [], set()
    for n, (p, c) in enumerate(order, 1):
        uid = f"U{n:02d}"
        key.append({"unit": uid, "prompt": p, "cond": c, "repeat": int((p, c) in seen)}); seen.add((p, c))
        rows = []
        for k, s in enumerate(T.SEEDS, 1):
            a = thumb(str(R / T.FOLDER / f"{p}_C0_krea2_seed{s}_00001_.png"), root)
            b = thumb(str(R / T.FOLDER / f"{p}_{c}_krea2_seed{s}_00001_.png"), root)
            rows.append({"label": f"coppia {k}", "cells": [{"t": a[0], "f": a[1]}, {"t": b[0], "f": b[1]}]})
        units.append({"id": uid, "title": f"Scheda {n:02d}", "groups": [{"id": "g", "name": "", "cols": ["prima", "dopo"], "rows": rows}]})
    with open(T.KEY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["unit", "prompt", "cond", "repeat"]); w.writeheader(); w.writerows(key)
    build(os.path.join(root, "occhio_C102.html"), "C102 · lo stesso cambiamento?", units,
          [("same", "Nelle tre coppie l'immagine cambia nello stesso modo?", [("si", "sì"), ("inparte", "in parte"), ("no", "no")])],
          [("si", "sì"), ("inparte", "in parte"), ("no", "no")], "c102_labels_v1", "te_depth_control_labels.csv")
    print("units", len(units), "repeats", sum(k["repeat"] for k in key), "->", os.path.join(root, "occhio_C102.html"))


if __name__ == "__main__":
    main()
