"""C115 - which attributes an encoder edit adds, moves or removes: per-picture questions on C114's renders, conditions
hidden (docs/prereg_te_attributes.md). Written 2026-10-29 with the pre-registration, before any label. No new render.

  python te_attributes.py --selftest
  python te_attributes.py --page     # Text2Img/occhio_C115_<prompt>.html (3 pages), key data/te_attributes_key.csv
  python te_attributes.py --rules    # once data/te_attributes_labels_<prompt>.csv exist (3 files)
"""
import argparse, csv, os, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import te_tree as TT
import te_depth_control as T

DATA = HERE.parent / "data"
KEY, TESTS = DATA / "te_attributes_key.csv", DATA / "te_attributes_tests.csv"
FOLDER = "benchmark_te_unseen"
SEEDS = TT.TEST_SEEDS
CONDS = {"C0": "C0", "E06": "E06_0p8", "E14": "E14_0p8", "E28": "E28_1p06066", "P01": "P01_1p75"}
YN = [("si", "sì"), ("no", "no"), ("dubbio", "non so")]
Q = {"U3_robot": [("copper", "Gli occhi sono di rame (bordi o lenti color rame)?"),
                  ("clay", "Il robot sembra di plastilina o argilla (non di metallo)?"),
                  ("second", "C'è una seconda figura oltre al robot?"),
                  ("pupils", "Gli occhi hanno grandi pupille nere?")],
     "U1_redtree": [("water", "C'è acqua alla base dell'albero?"),
                    ("spiral", "Il tronco forma una spirale o un ricciolo evidente?"),
                    ("red", "Le foglie sono rosse?"),
                    ("watercolor", "È dipinto ad acquerello?")],
     "U2_dagger": [("inlay", "Ci sono decorazioni dorate geometriche sulla lama o sull'impugnatura?"),
                   ("panel", "Dietro il pugnale c'è un pannello o uno sfondo decorato art déco?"),
                   ("dark", "Lo sfondo è scuro (nero o quasi)?"),
                   ("upright", "Il pugnale è dritto, verticale e al centro?")]}
# Predictions (Claude's non-blind reading of the C114 sheets, written before any C115 label):
# attribute, edit, direction: +1 emerges, -1 lost (count of "sì" over 8 seeds, edit minus plain, |diff| >= 5)
PRED = [("U3_robot", "copper", "E14", -1), ("U3_robot", "copper", "P01", -1), ("U3_robot", "clay", "P01", -1),
        ("U3_robot", "second", "P01", +1), ("U3_robot", "pupils", "E06", +1), ("U3_robot", "pupils", "E14", +1),
        ("U3_robot", "pupils", "E28", +1), ("U1_redtree", "water", "E28", +1), ("U1_redtree", "spiral", "E28", +1),
        ("U2_dagger", "panel", "E06", +1), ("U2_dagger", "panel", "P01", +1), ("U2_dagger", "dark", "E06", +1),
        ("U2_dagger", "dark", "P01", +1), ("U2_dagger", "dark", "E28", +1), ("U2_dagger", "upright", "E06", +1),
        ("U2_dagger", "upright", "P01", +1)]
BAR = 5
NREP = 4                                                   # repeated pictures per prompt


def labels_path(p):
    return DATA / f"te_attributes_labels_{p}.csv"


def page():
    from eye_grid_page import thumb, build
    root = str(T.img_root()); rng = random.Random(11515); key = []
    for p, qs in Q.items():
        items = [(c, s) for c in CONDS for s in SEEDS]; rng.shuffle(items)
        reps = rng.sample(range(len(items)), NREP); order = list(range(len(items)))
        for i in reps:
            j = order.index(i); order.insert(rng.randint(min(j + 12, len(order)), len(order)), i)
        units, seen = [], set()
        for k, i in enumerate(order, 1):
            c, s = items[i]; uid = f"{p[:2]}{k:03d}"
            key.append({"unit": uid, "prompt": p, "edit": c, "seed": s, "repeat": int(i in seen)}); seen.add(i)
            t, f = thumb(str(T.img_root() / FOLDER / TT.fname(p, CONDS[c], s)), root)
            units.append({"id": uid, "title": f"Immagine {k:03d}", "groups": [{"id": "g", "name": "", "cols": [""], "rows": [{"label": "", "cells": [{"t": f, "f": f}]}]}]})
        out = os.path.join(root, f"occhio_C115_{p}.html")
        build(out, f"C115 · attributi · {p.split('_')[1]}", units, [(q, t, YN) for q, t in qs], YN, f"c115_{p}_v1", f"te_attributes_labels_{p}.csv")
        h = open(out, encoding="utf-8").read().replace("max-width:150px", "max-width:520px")
        open(out, "w", encoding="utf-8").write(h)
        print(p, len(units), "->", out)
    with open(KEY, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)


def counts(labels, key):
    """(prompt, attribute, edit) -> number of 'sì' over the 8 seeds (first showing only); plus test-retest pairs."""
    first, reps, n = {}, [], {}
    for r in labels:
        k = key.get(r["unit"])
        if not k:
            continue
        t = (k["prompt"], k["edit"], k["seed"])
        if str(k["repeat"]) == "1":
            reps.append((t, r)); continue
        first[t] = r
    for (p, e, s), r in first.items():
        for q, _ in Q[p]:
            n.setdefault((p, q, e), [0, 0])
            if r.get(q) == "si":
                n[(p, q, e)][0] += 1
            if r.get(q) in ("si", "no"):
                n[(p, q, e)][1] += 1
    agree = [sum(first[t].get(q) == r.get(q) for q, _ in Q[t[0]]) for t, r in reps if t in first]
    return n, agree, sum(len(Q[t[0]]) for t, r in reps if t in first)


def rules(labels, key):
    n, agree, tot = counts(labels, key)
    yes = lambda p, q, e: n.get((p, q, e), [0, 0])[0]
    out, hit = [], 0
    for p, q, e, d in PRED:
        diff = yes(p, q, e) - yes(p, q, "C0")
        ok = diff * d >= BAR; hit += ok
        out.append({"test": f"Prediction {p} {q} {e} {'+' if d > 0 else '-'}", "value": f"{yes(p, q, e)} vs plain {yes(p, q, 'C0')} (diff {diff:+d})", "verdict": "confirmed" if ok else "not confirmed"})
    out.insert(0, {"test": "Rule 1 predicted changes confirmed (|diff| >= 5 of 8 in the predicted direction)", "value": f"{hit} of {len(PRED)}",
                   "verdict": "the reading holds blind" if hit >= 0.7 * len(PRED) else "the reading does not hold blind"})
    pred = {(p, q, e) for p, q, e, _ in PRED}
    extra = [f"{p} {q} {e} {yes(p, q, e) - yes(p, q, 'C0'):+d}" for p in Q for q, _ in Q[p] for e in CONDS if e != "C0"
             and (p, q, e) not in pred and abs(yes(p, q, e) - yes(p, q, "C0")) >= BAR]
    out.insert(1, {"test": "Rule 2 changes >= 5 not predicted (reported)", "value": "; ".join(extra) or "none", "verdict": f"{len(extra)}"})
    table = "; ".join(f"{p} {q}: " + " ".join(f"{e} {yes(p, q, e)}" for e in CONDS) for p in Q for q, _ in Q[p])
    out.append({"test": "Reported 'sì' out of 8 per prompt, attribute and condition", "value": table, "verdict": "-"})
    out.append({"test": "Reported test-retest (answers)", "value": f"{sum(agree)} of {tot}", "verdict": "-"})
    return out


def selftest():
    key, lab = {}, []
    for p in Q:
        for c in CONDS:
            for s in SEEDS:
                uid = f"{p}{c}{s}"; key[uid] = {"prompt": p, "edit": c, "seed": s, "repeat": "0"}
                r = {"unit": uid}
                for q, _ in Q[p]:
                    d = next((d for pp, qq, e, d in PRED if pp == p and qq == q and e == c), 0)
                    base = q in ("copper", "clay", "red", "watercolor", "inlay")
                    r[q] = "si" if (base and d >= 0) or d > 0 else "no"
                lab.append(r)
    o = rules(lab, key)
    assert o[0]["value"] == f"{len(PRED)} of {len(PRED)}", o[0]
    assert all(e in CONDS for _, _, e, _ in PRED) and all(q in dict(Q[p]) for p, q, _, _ in PRED)
    print("selftest ok;", len(PRED), "predictions;", 3 * (40 + NREP), "pictures to label")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("selftest", "page", "rules"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.page: page()
    if a.rules:
        key = {r["unit"]: r for r in csv.DictReader(open(KEY, encoding="utf-8"))}
        lab = [r for p in Q for r in csv.DictReader(open(labels_path(p), encoding="utf-8"))]
        out = rules(lab, key)
        with open(TESTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
