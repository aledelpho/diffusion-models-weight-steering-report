"""C65 eye tally: Alessandro's labels joined to the key (descriptive; no decision rule uses them).

  python te_characters_eye_tally.py
      -> data/te_characters_eye_joined.csv   one row per sheet showing, with the edit and seed
      and prints: repeat agreement, per edit x seed the verdict, follow/other/unchanged counts per character, and
      the "degradation" column (Alessandro, 2026-10-12: the surface never broke, so he used the scale for how far
      the picture stops following the prompt, e.g. a coloured background where white was asked).
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
CH = ["D1", "E2", "O4", "G5", "H3", "R6", "T7"]


def main():
    key = {r["item"]: r for r in csv.DictReader(open(DATA / "te_characters_eye_key.csv", encoding="utf-8"))}
    lab = list(csv.DictReader(open(DATA / "te_characters_eye_alessandro.csv", encoding="utf-8")))
    rows, seen, reps = [], {}, []
    for r in sorted(lab, key=lambda r: int(r["slot"].split("#")[1])):
        it = r["slot"].split("#")[0]
        k = key[it]
        x = {"slot": r["slot"], "item": it, "cond": k["cond"], "seed": k["seed"], "first": int(it not in seen),
             "stessa": r["stessa"], "dmg": r["dmg"], **{f"c_{c}": r[f"c{j+1}"] for j, c in enumerate(CH)},
             "n_follow": sum(r[f"c{j+1}"] == "segue" for j in range(7)) if r["stessa"] else "",
             "n_other": sum(r[f"c{j+1}"] == "diverso" for j in range(7)) if r["stessa"] else "",
             "n_unchanged": sum(r[f"c{j+1}"] == "invariato" for j in range(7)) if r["stessa"] else "",
             "direzione": r["direzione"], **{f"t_{c}": r[f"t{j+1}"] for j, c in enumerate(CH)}, "note": r["note"]}
        if it in seen:
            reps.append((seen[it], x))
        else:
            seen[it] = x
        rows.append(x)
    with open(DATA / "te_characters_eye_joined.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    first = [x for x in rows if x["first"]]
    print("showings", len(rows), "sheets", len(first), "repeats", len(reps),
          "| sheets without the 'same direction' answer:", sum(not x["stessa"] for x in first))
    print("\nrepeats (first -> repeat):")
    for a, b in reps:
        print(f"  {a['cond']:16s} {a['seed']}  stessa {a['stessa'] or '-':5s}->{b['stessa'] or '-':5s}  dmg {a['dmg'] or '-':6s}->{b['dmg'] or '-':6s}"
              f"  follow {a['n_follow']}->{b['n_follow']}")
    print("\nper edit (first showings): seed 2645751 | seed 3316624   [same-direction, follow/other/unchanged, degradation]")
    by = defaultdict(dict)
    for x in first:
        by[x["cond"]][x["seed"]] = x
    fmt = lambda x: (f"{x['stessa'] or '?':5s} {x['n_follow']}/{x['n_other']}/{x['n_unchanged']} {x['dmg'] or '?':6s}"
                     if x and x["stessa"] else f"{'?':5s} -/-/- {'?':6s}" if x else "missing")
    for k in sorted(by, key=lambda c: (int(c[1:3]), c)):
        print(f"  {k:16s} {fmt(by[k].get('2645751'))} | {fmt(by[k].get('3316624'))}")
    print("\noverall, first showings with an answer:")
    ans = [x for x in first if x["stessa"]]
    print("  same direction:", dict(Counter(x["stessa"] for x in ans)))
    print("  degradation   :", dict(Counter(x["dmg"] for x in ans)))
    print("  'other way' per character:", {c: sum(x[f"c_{c}"] == "diverso" for x in ans) for c in CH})
    print("  'unchanged' per character:", {c: sum(x[f"c_{c}"] == "invariato" for x in ans) for c in CH})
    # does the two-seed verdict agree for an edit?
    both = [(v["2645751"], v["3316624"]) for v in by.values() if all(s in v and v[s]["stessa"] for s in ("2645751", "3316624"))]
    print(f"  edits judged on both seeds: {len(both)}; same 'same-direction' answer on both: {sum(a['stessa'] == b['stessa'] for a, b in both)}")


if __name__ == "__main__":
    main()
