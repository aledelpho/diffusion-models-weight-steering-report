"""C73 tally (docs/prereg_te_fallback.md). Written 2026-10-13, before any C73 label. Input:
data/te_fallback_genre_alessandro.csv (committed as downloaded). Outputs: data/te_fallback_tests.csv,
data/te_fallback_by_char.csv.

  python te_fallback_tally.py
  python te_fallback_tally.py --selftest
"""
import argparse, csv
from collections import Counter
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data"
CHARS = ["D1_dwarf_paladin", "E2_elf_rogue", "O4_halforc_fighter", "G5_gnome_wizard", "H3_halfling_druid",
         "R6_dragonborn_cleric", "T7_tiefling_bard"]
EDITS = ["L02_mlp_p1.00", "L05_mlp_p1.00", "L06_mlp_p1.00", "L09_mlp_p1.00", "L12_mlp_p1.00", "L14_mlp_p1.00",
         "L17_mlp_p1.00", "L20_mlp_p1.00", "L25_mlp_p1.00", "L26_mlp_p1.00", "L28_mlp_p1.00"]


def table(rows):
    t = {}
    for r in rows:
        n = 4 if r["grid"] in ("fb_with", "fb_without") else 2
        t[(r["grid"], r["row"])] = [r.get(f"g{i}", "") for i in range(1, n + 1)]
    return t


def majority(gs):
    c = Counter(g for g in gs if g and g != "rotto")
    if not c:
        return "none"
    g, n = c.most_common(1)[0]
    return g if n >= 3 else "mixed"


def tally(rows):
    t = table(rows); out, per = [], []
    fb = {ch: majority(t.get(("fb_without", ch), [])) for ch in CHARS}
    withg = {ch: t.get(("fb_with", ch), [""] * 4) for ch in CHARS}
    clear = [g for g in fb.values() if g not in ("mixed", "none")]
    distinct = sorted(set(clear))
    h1 = "supported: the fallback depends on the character" if len(distinct) >= 2 else ("not supported: one fallback" if len(distinct) == 1 else "inconclusive: no clear fallback")
    out.append({"test": "H1", "value": f"majority no-style genre per character: {fb}; distinct {distinct}", "verdict": h1})
    # H2: switched edit pictures land on the character's own fallback?
    sw = []
    for ch in CHARS:
        for e in EDITS:
            gs = t.get((f"fb_edits_{ch}", e), ["", ""])
            for i, g in enumerate(gs):
                g0 = withg[ch][i]
                if g and g0 and g != g0 and g != "rotto":
                    sw.append((ch, g))
    base = Counter(g for _, g in sw)
    elig = [(ch, g) for ch, g in sw if fb[ch] not in ("mixed", "none")]
    if elig:
        match = sum(g == fb[ch] for ch, g in elig) / len(elig)
        expected = sum(base[fb[ch]] / len(sw) for ch, _ in elig) / len(elig)
        d = match - expected
        h2 = ("supported: edits go to the character's own fallback" if (d >= 0.20 and match >= 0.5)
              else ("not supported" if d <= 0.05 else "inconclusive"))
        out.append({"test": "H2", "value": f"match {match:.2f} vs expected {expected:.2f} (n {len(elig)} switched pictures of characters with a clear fallback; all switches {len(sw)}: {dict(base)})", "verdict": h2})
    else:
        out.append({"test": "H2", "value": "no eligible switched pictures", "verdict": "inconclusive"})
    out.append({"test": "with-style genres (reported)", "value": dict(Counter(g for ch in CHARS for g in withg[ch] if g)), "verdict": ""})
    for ch in CHARS:
        e_sw = [g for c, g in sw if c == ch]
        per.append({"char": ch, "with_style": " ".join(withg[ch]), "no_style": " ".join(t.get(("fb_without", ch), [])), "fallback": fb[ch],
                    "edit_switches": len(e_sw), "edit_switch_genres": dict(Counter(e_sw))})
    return out, per


def run():
    out, per = tally(list(csv.DictReader(open(DATA / "te_fallback_genre_alessandro.csv", encoding="utf-8"))))
    with open(DATA / "te_fallback_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    with open(DATA / "te_fallback_by_char.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(per[0])); w.writeheader(); w.writerows(per)
    for o in out: print(o)
    for p in per: print(p)


def selftest():
    fake_fb = ["anime", "realist", "realist", "anime", "pittura", "anime", "fumetto"]
    rows = []
    for ch, f in zip(CHARS, fake_fb):
        rows.append({"grid": "fb_with", "row": ch, **{f"g{i}": "fumetto" for i in range(1, 5)}})
        rows.append({"grid": "fb_without", "row": ch, **{f"g{i}": f for i in range(1, 5)}})
        for e in EDITS:
            rows.append({"grid": f"fb_edits_{ch}", "row": e, "g1": f if f != "fumetto" else "anime", "g2": "fumetto"})
    out, _ = tally(rows)
    d = {o["test"]: o for o in out}
    assert d["H1"]["verdict"].startswith("supported"), d["H1"]
    assert d["H2"]["verdict"].startswith("supported"), d["H2"]
    rows2 = [r if r["grid"] != "fb_without" else {**r, **{f"g{i}": "anime" for i in range(1, 5)}} for r in rows]
    assert tally(rows2)[0][0]["verdict"].startswith("not supported")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    selftest() if a.selftest else run()
