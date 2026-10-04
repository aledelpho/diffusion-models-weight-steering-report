"""Annotation page for the C45 eye pass (docs/prereg_prompt_writing.md, "The eye").

Amendment 2026-10-04, made while the eye pass was in progress and before any C45 number
was computed: marks are recorded per arm AND per subject, and each question gets a fourth
answer, "troppo debole" (the change is too faint to judge). Reason: Alessandro reported that
on S2 (lotus canoe) the arms are hard to see. Marks given with the first version of the page
(per arm) are copied into both subjects as a starting point.

  python experiments/build_prompt_writing_eye_page.py -> benchmark_prompt_writing/occhio_C45.html
Export -> save as data/prompt_writing_eye_alessandro.csv
"""
import os
from analyze_prompt_writing import WRIT, CONTENT, SEEDS, PW, path, plan
from eye_grid_page import thumb, build

ROWS = [("W1 originale", 0), ("W2 riordinato", 1), ("W3 tag", 2), ("W4 sinonimi", 3), ("C1 contenuto cambiato", None)]


def main():
    units = []
    for c in [c for c in plan() if c != "baseline"]:
        groups = []
        for s in ("S1", "S2"):
            rows = []
            for label, k in ROWS:
                pid = WRIT[s][k] if k is not None else CONTENT[s]
                cells = []
                for j, (cond, seed) in enumerate([("baseline", SEEDS[0]), (c, SEEDS[0]), ("baseline", SEEDS[1]), (c, SEEDS[1])]):
                    t, f = thumb(path(pid, cond, seed), PW)
                    cells.append({"t": t, "f": f, "hl": cond != "baseline", "b": j - j % 2})
                rows.append({"label": label, "cells": cells})
            groups.append({"id": s, "name": "S1 · elfa" if s == "S1" else "S2 · canoa",
                           "cols": ["base 3141592", "braccio 3141592", "base 1234567", "braccio 1234567"], "rows": rows})
        units.append({"id": c, "title": c, "groups": groups})
    build(os.path.join(PW, "occhio_C45.html"), "C45 · stessa modifica, scritture diverse", units,
          [("q1", "Fa la stessa cosa al variare della scrittura (W1–W4)?"),
           ("q2", "Fa la stessa cosa dopo il cambio di contenuto (C1)?")],
          [("si", "sì"), ("inparte", "in parte"), ("no", "no"), ("debole", "troppo debole")],
          "occhio_C45_v2", "prompt_writing_eye_alessandro.csv", migrate="occhio_C45_v1")
    print("written")


if __name__ == "__main__":
    main()
