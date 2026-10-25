"""C109 - blind key and page (docs/prereg_te_light_presets.md, section 3). Written 2026-10-25 after the renders, before any
label. C105's units and questions; the C109 presets, C105's E14 and E26 re-shown, 12 null controls, 8 repeats.

  python te_light_presets_page.py          # data/te_light_presets_key.csv, Text2Img/occhio_C109.html (superseded)
  python te_light_presets_page.py --full   # amendment 1: data/te_light_presets_key_full.csv, Text2Img/occhio_C109b.html
"""
import csv, os, random, statistics, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_light_presets as LP
import te_domain_transfer as DT
from eye_grid_page import thumb, build

DATA = HERE.parent / "data"
KEY = DATA / "te_light_presets_key.csv"


def matched(metrics):
    M = {}
    for r in csv.DictReader(open(metrics, encoding="utf-8")):
        M.setdefault((r["prompt"], r["pert"]), []).append(float(r["dinov2_dist_to_base"]))
    return {k for k, v in M.items() if LP.MATCH_LO <= statistics.median(v) <= LP.MATCH_HI}


def specs():
    okP = matched(DATA / "te_light_presets_metrics.csv")
    okE = {k for k in matched(DATA / "te_domain_transfer_metrics.csv") if k[1] in ("E14", "E26")}
    U = []
    for src, ok, perts in (("C109", okP, list(LP.PERTS)), ("C105", okE, ["E14", "E26"])):
        for n in perts:
            for s in LP.TEST_SEEDS:
                for k, subj in LP.SETS.items():
                    cells = [(p, n) for p in subj if (p, n) in ok]
                    if len(cells) >= LP.MIN_CELLS:
                        U.append({"src": src, "kind": k, "pert": n, "seed": s, "cells": cells})
    names = list(LP.PERTS)
    plan = [(s, k, 0) for s in LP.TEST_SEEDS for k in LP.SETS] + [(LP.TEST_SEEDS[0], k, 6) for k in LP.SETS]
    for s, k, off in plan:                       # 12 null controls: each subject with a different preset
        subj = LP.SETS[k]
        for r in range(12):
            cells = [c for c in ((p, names[(j * 3 + off + r) % 12]) for j, p in enumerate(subj)) if c in okP]
            if len(cells) >= LP.MIN_CELLS:
                U.append({"src": "C109", "kind": "N" + k, "pert": "mixed", "seed": s, "cells": cells}); break
    return U


def main():
    R = LP.T.img_root(); root = str(R); rng = random.Random(10909)
    sP = {(r["prompt"], r["pert"]): r for r in csv.DictReader(open(DATA / "te_light_presets_strengths.csv", encoding="utf-8"))}
    sE = {(r["prompt"], r["pert"]): r for r in csv.DictReader(open(DATA / "te_domain_transfer_strengths.csv", encoding="utf-8"))}
    U = specs(); rng.shuffle(U)
    reps = rng.sample(range(len(U)), 8); order = list(range(len(U)))
    for i in reps:
        j = order.index(i); order.insert(rng.randint(min(j + 15, len(order)), len(order)), i)
    key, units, seen = [], [], set()
    for n_, i in enumerate(order, 1):
        u = U[i]; uid = f"Z{n_:03d}"
        key.append({"unit": uid, "src": u["src"], "kind": u["kind"], "pert": u["pert"], "seed": u["seed"],
                    "cells": " ".join(f"{p}:{n}" for p, n in u["cells"]), "repeat": int(i in seen)}); seen.add(i)
        rows = []
        for k, (p, n) in enumerate(u["cells"], 1):
            if n in ("E14", "E26"):
                folder, t = DT.FOLDER, DT.tag(n, float(sE[(p, n)]["strength"]))
            else:
                folder, t = LP.FOLDER, LP.tag(n, float(sP[(p, n)]["strength"]))
            a = thumb(str(R / folder / LP.fname(p, "C0", u["seed"])), root)
            b = thumb(str(R / folder / LP.fname(p, t, u["seed"])), root)
            rows.append({"label": f"coppia {k}", "cells": [{"t": a[0], "f": a[1]}, {"t": b[0], "f": b[1]}]})
        units.append({"id": uid, "title": f"Scheda {n_:03d}", "groups": [{"id": "g", "name": "", "cols": ["prima", "dopo"], "rows": rows}]})
    with open(KEY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    qs = [("content", "Il tipo di cambiamento del contenuto (soggetti, forme, oggetti, età, materiali) è lo stesso in tutte le coppie?", DT.OPTS),
          ("style", "Il tipo di cambiamento dello stile (resa, tecnica, colori, tratto) è lo stesso in tutte le coppie?", DT.OPTS)]
    build(os.path.join(root, "occhio_C109.html"), "C109 · lo stesso cambiamento su soggetti diversi?", units, qs, DT.OPTS,
          "c109_labels_v1", "te_light_presets_labels.csv")
    kinds = {}
    for k in key:
        if not k["repeat"]:
            kinds[(k["src"], k["kind"][0] == "N")] = kinds.get((k["src"], k["kind"][0] == "N"), 0) + 1
    print("units", len(units), kinds, "->", os.path.join(root, "occhio_C109.html"))


SUBJ_ORDER = LP.COMICS + LP.OTHER
OPTS3 = [("si", "sì"), ("inparte", "in parte"), ("no", "no"), ("nonsivede", "non si vede")]


def main_full():
    """Amendment 1 (2026-10-25, before any label): one card per perturbation x test seed with every subject that has a
    test render, portraits first, in a fixed order; null cards give each subject a different preset."""
    R = LP.T.img_root(); root = str(R); rng = random.Random(10910)
    sP = {(r["prompt"], r["pert"]): r for r in csv.DictReader(open(DATA / "te_light_presets_strengths.csv", encoding="utf-8"))}
    sE = {(r["prompt"], r["pert"]): r for r in csv.DictReader(open(DATA / "te_domain_transfer_strengths.csv", encoding="utf-8"))}
    have = lambda S, p, n: (p, n) in S and S[(p, n)]["reached"] == "1"
    U = []
    for n in LP.PERTS:
        for s in LP.TEST_SEEDS:
            U.append({"src": "C109", "kind": "FULL", "pert": n, "seed": s, "cells": [(p, n) for p in SUBJ_ORDER if have(sP, p, n)]})
    for n in ("E14", "E26"):
        for s in LP.TEST_SEEDS:
            U.append({"src": "C105", "kind": "FULL", "pert": n, "seed": s, "cells": [(p, n) for p in SUBJ_ORDER if have(sE, p, n)]})
    names = list(LP.PERTS)
    for s in LP.TEST_SEEDS:
        for off in (0, 5):
            cells = []
            for j, p in enumerate(SUBJ_ORDER):
                for r in range(12):
                    n = names[(j + off + r) % 12]
                    if have(sP, p, n) and n not in [c[1] for c in cells]:
                        cells.append((p, n)); break
            U.append({"src": "C109", "kind": "NULL", "pert": "mixed", "seed": s, "cells": cells})
    rng.shuffle(U)
    reps = rng.sample(range(len(U)), 4); order = list(range(len(U)))
    for i in reps:
        j = order.index(i); order.insert(rng.randint(min(j + 8, len(order)), len(order)), i)
    key, units, seen = [], [], set()
    for n_, i in enumerate(order, 1):
        u = U[i]; uid = f"F{n_:02d}"
        key.append({"unit": uid, "src": u["src"], "kind": u["kind"], "pert": u["pert"], "seed": u["seed"],
                    "cells": " ".join(f"{p}:{n}" for p, n in u["cells"]), "repeat": int(i in seen)}); seen.add(i)
        rows = []
        for k, (p, n) in enumerate(u["cells"], 1):
            if n in ("E14", "E26"):
                folder, t = DT.FOLDER, DT.tag(n, float(sE[(p, n)]["strength"]))
            else:
                folder, t = LP.FOLDER, LP.tag(n, float(sP[(p, n)]["strength"]))
            a = thumb(str(R / folder / LP.fname(p, "C0", u["seed"])), root)
            b = thumb(str(R / folder / LP.fname(p, t, u["seed"])), root)
            rows.append({"label": f"coppia {k}", "cells": [{"t": a[0], "f": a[1]}, {"t": b[0], "f": b[1]}]})
        units.append({"id": uid, "title": f"Scheda {n_:02d}", "groups": [{"id": "g", "name": "", "cols": ["prima", "dopo"], "rows": rows}]})
    with open(DATA / "te_light_presets_key_full.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    qs = [("content", "Il tipo di cambiamento del contenuto (soggetti, forme, oggetti, età, materiali) è lo stesso in tutte le coppie?", DT.OPTS),
          ("style", "Il tipo di cambiamento dello stile (resa, tecnica, colori, tratto) è lo stesso in tutte le coppie?", DT.OPTS),
          ("domains", "Il cambiamento del contenuto è dello stesso tipo nei ritratti a fumetto e nelle altre immagini?", OPTS3)]
    build(os.path.join(root, "occhio_C109b.html"), "C109 · set completi", units, qs, DT.OPTS, "c109b_labels_v1", "te_light_presets_labels_full.csv")
    print("cards", len(units), "->", os.path.join(root, "occhio_C109b.html"))


if __name__ == "__main__":
    main_full() if "--full" in sys.argv else main()
