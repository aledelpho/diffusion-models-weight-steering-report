"""C64 phase 1 tally: Alessandro's blind labels (doses +-1.00) joined to the key.

  python te_pilot_phase1_tally.py
      -> data/te_pilot_phase1_joined.csv   one row per first showing, with condition and note flags
         data/te_pilot_phase1_repeats.csv  the 10 repeats against their first showing
         data/te_pilot_phase1_summary.csv  counts by part x sign x layer band
      and prints the tables used in docs/te_pilot_phase1_result.md.

Note flags are keyword searches over Alessandro's free notes (Italian), descriptive only:
  patch_swap   "benda" + "altro occhio"           the eyepatch moved to the other eye
  arm_down     "abbass" + "senza guanto"           the bare arm is lowered
  lost_traits  "perso|perde|manca|mancano|niente|no corna|non ha più|non è più"
  anime        "anime|chibi|cartone|cartoon|animazione"
"""
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
ORDER = {"nessuna": 0, "lieve": 1, "media": 2, "forte": 3, "testo": 4}
FLAGS = {
    "patch_swap": lambda t: "benda" in t and "altro occhio" in t,
    "arm_down": lambda t: "abbass" in t and "senza guanto" in t,
    "lost_traits": lambda t: re.search(r"\bpers[oa]\b|\bperde\b|\bmanca|\bniente\b|no corna|non ha più|non è più|senza il guanto", t) is not None,
    "anime": lambda t: re.search(r"anime|chibi|cartone|cartoon|animazione", t) is not None,
}


def rd(n):
    return list(csv.DictReader(open(DATA / n, encoding="utf-8")))


def band(unit):
    if not unit.startswith("L"):
        return unit
    L = int(unit[1:])
    return "L00" if L == 0 else "L01-04" if L <= 4 else "L05-11" if L <= 11 else "L12-23" if L <= 23 else "L24-34" if L <= 34 else unit


def main():
    key = {r["item"]: r for r in rd("te_pilot_eye_key_phase1.csv")}
    lab = rd("te_pilot_eye_alessandro_phase1.csv")
    first, reps = {}, []
    for r in sorted(lab, key=lambda r: int(r["slot"].split("#")[1])):
        it = r["slot"].split("#")[0]
        if it in first:
            reps.append((first[it], r))
        else:
            first[it] = r
    rows = []
    for it, r in first.items():
        k = key[it]
        txt = (r["stilenote"] + " " + r["note"]).lower()
        d = float(k["dose"])
        rows.append({"item": it, "cond": k["cond"], "unit": k["unit"], "part": k["part"], "sign": "+" if d > 0 else "-",
                     "phase": k["phase"], "band": band(k["unit"]), "entita": r["entita"], "stile": r["stile"],
                     "braccio": r["braccio"], "dmg": r["dmg"], "imported": r["imported"],
                     **{f: int(fn(txt)) for f, fn in FLAGS.items()}, "stilenote": r["stilenote"], "note": r["note"]})
    rows.sort(key=lambda x: (x["phase"], x["part"], x["unit"], x["sign"]))
    with open(DATA / "te_pilot_phase1_joined.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(DATA / "te_pilot_phase1_repeats.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["item", "cond", "q", "first", "repeat"])
        for a, b in reps:
            for q in ("entita", "stile", "braccio", "dmg"):
                w.writerow([a["slot"].split("#")[0], key[a["slot"].split("#")[0]]["cond"], q, a[q], b[q]])
    # summary
    summ = defaultdict(Counter)
    for x in rows:
        if x["phase"] != "main":
            continue
        g = (x["part"], x["sign"], x["band"])
        summ[g]["n"] += 1
        summ[g]["ent_" + x["entita"]] += 1
        summ[g]["stile_cambiato"] += x["stile"] == "cambiato"
        summ[g]["braccio_" + (x["braccio"] or "na")] += 1
        summ[g]["dmg_" + x["dmg"]] += 1
        for fl in FLAGS:
            summ[g][fl] += x[fl]
    cols = ["n"] + [f"ent_{e}" for e in ORDER] + ["stile_cambiato", "braccio_stesso", "braccio_altro", "braccio_ambiguo", "braccio_na"] + \
           [f"dmg_{d}" for d in ("pulito", "come", "lieve", "medio", "forte")] + list(FLAGS)
    with open(DATA / "te_pilot_phase1_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["part", "sign", "band"] + cols)
        for g in sorted(summ):
            w.writerow(list(g) + [summ[g][c] for c in cols])
    # prints
    print("first showings", len(rows), "repeats", len(reps), "imported", sum(x["imported"] == "1" for x in rows))
    print("\nchecks:")
    for x in rows:
        if x["phase"] == "check":
            print(f"  {x['cond']:28s} {x['entita']:8s} stile={x['stile']:10s} dmg={x['dmg']:6s} {x['stilenote'][:60]}")
    print("\nrepeat agreement:")
    for q in ("entita", "stile", "braccio", "dmg"):
        same = sum(a[q] == b[q] for a, b in reps)
        within1 = sum(abs(ORDER.get(a[q], 9) - ORDER.get(b[q], 9)) <= 1 for a, b in reps) if q == "entita" else None
        print(f"  {q:8s} exact {same}/{len(reps)}" + (f", within one step {within1}/{len(reps)}" if within1 is not None else ""))
    print("\nby part x sign x band (main): n | none slight medium strong text | style changed | arm same/other/ambig | dmg clean/as/sl/med/str | patch_swap arm_down lost anime")
    for g in sorted(summ):
        s = summ[g]
        print(f"  {g[0]:5s} {g[1]} {g[2]:22s} {s['n']:3d} | " + " ".join(f"{s['ent_' + e]:2d}" for e in ORDER) +
              f" | {s['stile_cambiato']:2d} | {s['braccio_stesso']:2d}/{s['braccio_altro']:2d}/{s['braccio_ambiguo']:2d}"
              f" | " + "/".join(str(s['dmg_' + d]) for d in ("pulito", "come", "lieve", "medio", "forte")) +
              f" | {s['patch_swap']:2d} {s['arm_down']:2d} {s['lost_traits']:2d} {s['anime']:2d}")
    print("\nper layer (main), entita code 0-4 and style changed, attn/mlp x sign:")
    per = defaultdict(dict)
    for x in rows:
        if x["phase"] == "main" and x["part"] in ("attn", "mlp"):
            per[x["unit"]][x["part"] + x["sign"]] = str(ORDER[x["entita"]]) + ("S" if x["stile"] == "cambiato" else "") + \
                ("a" if x["braccio"] == "altro" else "m" if x["braccio"] == "ambiguo" else "")
    print("  layer  attn-  attn+  mlp-  mlp+")
    for u in sorted(per):
        p = per[u]
        print(f"  {u}   " + "  ".join(f"{p.get(k, '.'):5s}" for k in ("attn-", "attn+", "mlp-", "mlp+")))


if __name__ == "__main__":
    main()
