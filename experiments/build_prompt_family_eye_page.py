"""Eye-pass page for C49 (docs/prereg_prompt_family.md, "The eye"). Run after the renders.

One unit per arm x family (7 x 3 = 21). Rows: the 6 subjects. Columns: seed 5772156 base | arm |
seed 1414213 base | arm. Questions per unit:
  q1  does the preset give these six pictures a common, recognisable look?  yes / partly / no
  q2  is the cost (grain, artefacts, damage) acceptable?                      yes / partly / no
Export -> data/prompt_family_eye_alessandro.csv
"""
import os
from prompt_family import FAMILIES, SUBJECTS, SEEDS, ARMS
from analyze_prompt_family import D, path
from eye_grid_page import thumb, build


def main():
    units = []
    for arm in [a for a in ARMS if a != "baseline"]:
        for fam in FAMILIES:
            rows = []
            for subj in SUBJECTS:
                pid = f"{fam}_{subj}"; cells = []
                for j, (a, s) in enumerate([("baseline", SEEDS[0]), (arm, SEEDS[0]), ("baseline", SEEDS[1]), (arm, SEEDS[1])]):
                    t, f = thumb(path(pid, a, s), D)
                    cells.append({"t": t, "f": f, "hl": a != "baseline", "b": j - j % 2})
                rows.append({"label": subj, "cells": cells})
            units.append({"id": f"{arm}|{fam}", "title": f"{arm} · {fam}",
                          "groups": [{"id": "g", "name": fam, "cols": [f"base {SEEDS[0]}", "preset", f"base {SEEDS[1]}", "preset"], "rows": rows}]})
    build(os.path.join(D, "occhio_C49.html"), "C49 · un preset per famiglia di prompt", units,
          [("q1", "Il preset dà a queste sei immagini un aspetto comune, riconoscibile?"),
           ("q2", "Il costo (grana, artefatti, danni) è accettabile?")],
          [("si", "sì"), ("inparte", "in parte"), ("no", "no")],
          "occhio_C49_v1", "prompt_family_eye_alessandro.csv")
    print("written", len(units))


if __name__ == "__main__":
    main()
