"""Eye-pass page for C52 phase C (docs/prereg_portrait_preset.md, "The eye, first"). Run after the renders.

One unit per character (7: four calibration, three held out). Rows: the four phase C seeds.
Columns: base | preset. Questions per character:
  q1  does the preset give it the look you calibrated?        yes / partly / no
  q2  is it still the same character?                         yes / partly / no
  q3  is the cost (noise, artefacts, deformation) acceptable? yes / partly / no
Export -> data/portrait_preset_eye_alessandro.csv
"""
import os
from portraits import CALIBRATION, HELD_OUT, SEEDS_C, FOLDER_C, IMG_ROOT
from analyze_portrait_preset import path
from eye_grid_page import thumb, build


def main():
    D = os.path.join(str(IMG_ROOT), FOLDER_C)
    units = []
    for group, chars in (("held out", HELD_OUT), ("calibration", CALIBRATION)):
        for ch in chars:
            rows = []
            for s in SEEDS_C:
                cells = []
                for j, cond in enumerate(("baseline", "preset")):
                    t, f = thumb(path(ch, cond, s), D)
                    cells.append({"t": t, "f": f, "hl": cond == "preset", "b": 0})
                rows.append({"label": f"seed {s}", "cells": cells})
            units.append({"id": ch, "title": f"{ch} · {group}",
                          "groups": [{"id": "g", "name": group, "cols": ["base", "preset"], "rows": rows}]})
    build(os.path.join(D, "occhio_C52.html"), "C52 · il preset dei ritratti", units,
          [("q1", "Il preset dà a questo personaggio il look che hai calibrato?"),
           ("q2", "È ancora lo stesso personaggio?"),
           ("q3", "Il costo (rumore, artefatti, deformazioni) è accettabile?")],
          [("si", "sì"), ("inparte", "in parte"), ("no", "no")],
          "occhio_C52_v1", "portrait_preset_eye_alessandro.csv")
    print("written", len(units))


if __name__ == "__main__":
    main()
