"""Eye-pass page for C47 (docs/prereg_blk23_vs_colorful.md, "The eye"). Built before any C47
number is shown to Alessandro.

One unit per prompt x seed (16). Two groups:
  "più colore":  base | "colorful" in the prompt | blk23 -0.15 | -0.30 | -0.45
  "meno colore": base | "muted" in the prompt    | blk23 +0.15 | +0.30
In each group the blk23 rung whose mean chroma is closest to the text's is outlined (the
only use of a measurement on this page; its value is not shown). Questions per group:
  q1  which changed the CONTENT more than the base (objects, faces, composition, style):
      the words, blk23 at the outlined rung, or equal
  q2  does blk23 move colour in the expected direction, growing with the dose?
Export -> save as data/blk23_colorful_eye_alessandro.csv

  python experiments/build_blk23_colorful_eye_page.py -> benchmark_blk23_colorful/occhio_C47.html
"""
import csv, os
import numpy as np
from blk23_colorful import PLAN, IMG_ROOT, FOLDER
from block_effect_overlap import lab
from eye_grid_page import thumb, build

ROOT = str(IMG_ROOT / FOLDER)
if not os.path.isdir(ROOT):
    ROOT = os.path.expanduser("~/mnt/benchmark_blk23_colorful")


def chroma(p):
    x = lab(p); return float(np.hypot(x[..., 1], x[..., 2]).mean())


def main():
    rows = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    cells = sorted({(r["prompt_id"], r["seed"]) for r in rows}, key=lambda t: ([r["prompt_id"] for r in rows].index(t[0]), t[1]))
    units = []
    for pid, seed in cells:
        f = lambda c: os.path.join(ROOT, f"{pid}_{c}_krea2_seed{seed}_00001_.png")
        groups = []
        for gid, name, txt, ladder in [("up", "più colore", "txtpos", ["b23_m0.150", "b23_m0.300", "b23_m0.450"]),
                                       ("down", "meno colore", "txtneg", ["b23_p0.150", "b23_p0.300"])]:
            ct = chroma(f(txt))
            near = min(ladder, key=lambda c: abs(chroma(f(c)) - ct))
            cols = ["base", "testo", *[c.replace("b23_m", "blk23 −").replace("b23_p", "blk23 +") for c in ladder]]
            cs = []
            for c in ["baseline", txt, *ladder]:
                t, full = thumb(f(c), ROOT)
                cs.append({"t": t, "f": full, "hl": c == near, "b": 0})
            groups.append({"id": gid, "name": name, "cols": cols, "rows": [{"label": "", "cells": cs}]})
        units.append({"id": f"{pid}_seed{seed}", "title": f"{pid} · seme {seed}", "groups": groups})
    build(os.path.join(ROOT, "occhio_C47.html"), "C47 · blk23 contro le parole", units,
          [("q1", "Chi ha cambiato di più il CONTENUTO rispetto alla base: le parole o blk23 al gradino evidenziato?",
            [("testo", "le parole"), ("blk23", "blk23"), ("pari", "uguale")]),
           ("q2", "blk23 sposta il colore nella direzione attesa, crescendo con la dose?",
            [("si", "sì"), ("inparte", "in parte"), ("no", "no")])],
          [], "occhio_C47_v1", "blk23_colorful_eye_alessandro.csv")
    print("written", len(units), "units")


if __name__ == "__main__":
    main()
