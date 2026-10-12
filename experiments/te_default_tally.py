"""C72 tally (docs/prereg_te_default.md + amendments 1-2). Written 2026-10-12, before any C72 label; it computes only
what the pre-registration fixes. Inputs: data/te_default_genre_alessandro.csv (blocks A, C and the plain / real
renders) and data/te_words_alessandro.csv (block B), committed as downloaded. Outputs: data/te_default_tests.csv,
data/te_default_cells.csv, data/te_words_table.csv.

  python te_default_tally.py            # A1, C1-C3 and the reported counts
  python te_default_tally.py --selftest
"""
import argparse, csv, sys
from collections import Counter
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data"
EDITS = ["L05_mlp_p1.00", "L06_mlp_p1.00", "L28_mlp_p1.00"]
VARS = ["permuted", "shared", "token"]
SEEDS = ["3141592", "1234567"]


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def genre_table(rows):
    """{(seed, row_label): [g1..g5]} for the two seed grids; {'empty': [g1..g4]}."""
    t = {}
    for r in rows:
        if r["grid"].startswith("c72_") and r["grid"] != "c72_empty":
            t[(r["grid"][4:], r["row"])] = [r.get(f"g{i}", "") for i in range(1, 6)]
        elif r["grid"] == "c72_empty":
            t["empty"] = [r.get(f"g{i}", "") for i in range(1, 5)]
    return t


def verdict_ratio(R):
    if R is None:
        return "undefined (no real switches)"
    return "size alone suffices: supported" if R >= 0.5 else ("the direction matters" if R <= 0.2 else "inconclusive")


def tally(rows, words=None):
    t = genre_table(rows)
    out, cells = [], []
    # A1
    ns = [g for s in SEEDS for g in t.get((s, "senza_stile"), []) if g]
    n_anime = sum(g == "anime" for g in ns)
    a1 = "default anime: supported" if n_anime >= 7 else ("not supported" if n_anime <= 3 else "inconclusive")
    out.append({"test": "A1", "value": f"{n_anime} anime of {len(ns)} labelled ({dict(Counter(ns))})", "verdict": a1 if len(ns) == 10 else a1 + " (incomplete labels)"})
    # C: switch = genre differs from the plain render of the same order and seed, broken counts as no switch
    def sw(seed, label, i):
        g0, g = t[(seed, "originale")][i], t[(seed, label)][i]
        if not g0 or not g:
            return None
        return int(g != g0 and g != "rotto")
    real = [sw(s, f"{e}_reale", i) for e in EDITS for s in SEEDS for i in range(5)]
    rr = [x for x in real if x is not None]; rate_real = sum(rr) / len(rr) if rr else 0
    for k, var in zip(("C1", "C2", "C3"), VARS):
        xs = [sw(s, f"{e}_{var}", i) for e in EDITS for s in SEEDS for i in range(5)]
        xx = [x for x in xs if x is not None]; rate = sum(xx) / len(xx) if xx else 0
        R = rate / rate_real if rate_real else None
        out.append({"test": k + f" ({var})", "value": f"switch rate {rate:.2f} ({sum(xx)}/{len(xx)}) / real {rate_real:.2f} ({sum(rr)}/{len(rr)}) = R "
                    + (f"{R:.2f}" if R is not None else "n/a"), "verdict": verdict_ratio(R)})
    # amendment 2: C1 is read with C2/C3
    v = [o["verdict"] for o in out[1:4]]
    out.append({"test": "C joint reading (amendment 2)", "value": "; ".join(v),
                "verdict": v[0] if len(set(v)) == 1 else "depends on the form of the push"})
    # reported
    out.append({"test": "empty prompt (reported)", "value": str(t.get("empty")), "verdict": ""})
    swg = [t[(s, f"{e}_{var}")][i] for e in EDITS for var in VARS for s in SEEDS for i in range(5) if sw(s, f"{e}_{var}", i)]
    out.append({"test": "anime share among switched random pushes (reported)", "value": f"{sum(g == 'anime' for g in swg)}/{len(swg)}", "verdict": ""})
    br = Counter(var for e in EDITS for var in VARS for s in SEEDS for i in range(5) if t[(s, f"{e}_{var}")][i] == "rotto")
    out.append({"test": "broken pictures per variant (reported)", "value": dict(br), "verdict": ""})
    for e in EDITS:
        for var in ["reale"] + VARS:
            xs = [sw(s, f"{e}_{var}", i) for s in SEEDS for i in range(5)]
            xx = [x for x in xs if x is not None]
            cells.append({"edit": e, "variant": var, "switched": sum(xx), "labelled": len(xx),
                          "genres": dict(Counter(t[(s, f"{e}_{var}")][i] for s in SEEDS for i in range(5)))})
    if words:
        out += words_report(words)
    return out, cells


def words_report(rows):
    out, table = [], []
    for r in rows:
        if r["grid"] != "c72_words":
            continue
        g = [r.get(f"g{i}", "") for i in range(1, 5)]; p = [r.get(f"p{i}", "") for i in range(1, 5)]; b = [r.get(f"b{i}", "") for i in range(1, 5)]
        table.append({"word": r["row"], "genres": " ".join(g), "persons": " ".join(p), "beards": " ".join(b)})
    with open(DATA / "te_words_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["word", "genres", "persons", "beards"]); w.writeheader(); w.writerows(table)
    def find(word):
        return next((x for x in table if x["word"].split(" · ", 1)[-1] == word), None)
    for word in ("dwarf", "female dwarf", "female paladin mountain dwarf", "uniform"):
        x = find(word)
        if x:
            out.append({"test": f"word '{word}' (reported)", "value": f"genres {x['genres']} | persons {x['persons']} | beards {x['beards']}", "verdict": ""})
    x = find("dwarf")
    if x and not x["persons"].strip():
        out.append({"test": "'dwarf' alone gives a bearded man in >= 3 of 4 seeds (reported)", "value": "row not labelled", "verdict": "n/a"})
    elif x:
        n = sum(1 for p, b in zip(x["persons"].split(), x["beards"].split()) if p == "uomo" and b == "sì")
        out.append({"test": "'dwarf' alone gives a bearded man in >= 3 of 4 seeds (reported)", "value": f"{n} of 4", "verdict": "yes" if n >= 3 else "no"})
    allg = Counter(g for x in table for g in x["genres"].split())
    out.append({"test": "genres over all single-word pictures (reported)", "value": dict(allg), "verdict": ""})
    return out


def run():
    rows = rd(DATA / "te_default_genre_alessandro.csv")
    words = rd(DATA / "te_words_alessandro.csv") if (DATA / "te_words_alessandro.csv").exists() else None
    out, cells = tally(rows, words)
    with open(DATA / "te_default_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    with open(DATA / "te_default_cells.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(cells[0])); w.writeheader(); w.writerows(cells)
    for o in out:
        print(o)


def selftest():
    rows = []
    for s in SEEDS:
        rows.append({"grid": f"c72_{s}", "row": "originale", **{f"g{i}": "fumetto" for i in range(1, 6)}})
        rows.append({"grid": f"c72_{s}", "row": "senza_stile", **{f"g{i}": "anime" for i in range(1, 6)}})
        for e in EDITS:
            rows.append({"grid": f"c72_{s}", "row": f"{e}_reale", **{f"g{i}": "anime" for i in range(1, 6)}})
            rows.append({"grid": f"c72_{s}", "row": f"{e}_permuted", **{f"g{i}": ("anime" if i <= 3 else "fumetto") for i in range(1, 6)}})
            rows.append({"grid": f"c72_{s}", "row": f"{e}_shared", **{f"g{i}": "rotto" for i in range(1, 6)}})
            rows.append({"grid": f"c72_{s}", "row": f"{e}_token", **{f"g{i}": ("cartoon" if i == 1 else "fumetto") for i in range(1, 6)}})
    rows.append({"grid": "c72_empty", "row": "vuoto", **{f"g{i}": "anime" for i in range(1, 5)}})
    out, cells = tally(rows)
    d = {o["test"].split(" ")[0]: o for o in out}
    assert d["A1"]["verdict"].startswith("default anime: supported")
    assert "R 0.60" in d["C1"]["value"] and d["C1"]["verdict"].startswith("size alone")      # 18/30 vs 30/30
    assert "R 0.00" in d["C2"]["value"] and d["C2"]["verdict"] == "the direction matters"     # broken = no switch
    assert "R 0.20" in d["C3"]["value"]
    assert [o for o in out if o["test"].startswith("C joint")][0]["verdict"] == "depends on the form of the push"
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    selftest() if a.selftest else run()
