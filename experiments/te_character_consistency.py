"""C92 - do characters deviate from an edit's usual destination consistently? (docs/prereg_te_character_consistency.md)
Written 2026-10-18 with the pre-registration, before any computation. No renders.

  python te_character_consistency.py
  python te_character_consistency.py --selftest
"""
import argparse, csv
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data"


def load():
    L = {}
    for r in csv.DictReader(open(DATA / "te_fallback_genre_alessandro.csv", encoding="utf-8")):
        if r["grid"].startswith("fb_edits_"):
            L[(r["grid"][9:], r["row"])] = [g.strip() if g.strip() and g.strip() != "rotto" else None for g in (r["g1"], r["g2"])]
    return L


def maj(ls, fb=None):
    ls = [g for g in ls if g]
    if not ls:
        return fb
    c = Counter(ls).most_common(); top = [g for g, n in c if n == c[0][1]]
    return top[0] if len(top) == 1 else (fb if fb in top else sorted(top)[0])


def predict(L):
    chars = sorted({c for c, _ in L}); edits = sorted({e for _, e in L}); rows = []
    for c in chars:
        for e in edits:
            if (c, e) not in L:
                continue
            others = [d for d in chars if d != c and (d, e) in L]
            m = maj([g for k, v in L.items() if k != (c, e) for g in v])
            ed = maj([g for d in others for g in L[(d, e)]], m)
            # CHAR+EDIT: share of each genre for this character on the other edits + share for this edit on the
            # other characters; argmax (ties -> EDIT). (Replaced a nearest-characters predictor that failed the selftest
            # before any real data was read.)
            own = Counter(g for f in edits if f != e and (c, f) in L for g in L[(c, f)] if g)
            col = Counter(g for d in others for g in L[(d, e)] if g)
            no, nc = max(sum(own.values()), 1), max(sum(col.values()), 1)
            sc = {g: own[g] / no + col[g] / nc for g in set(own) | set(col)}
            best = max(sc.values()) if sc else 0
            top = sorted(g for g, v in sc.items() if v == best)
            ch = top[0] if len(top) == 1 else (ed if ed in top else top[0])
            for g in L[(c, e)]:
                if g:
                    rows.append({"char": c, "edit": e, "label": g, "MAJ": m, "EDIT": ed, "CHAR": ch})
    return rows


def acc(rows, k):
    return sum(r[k] == r["label"] for r in rows) / len(rows)


def run(L, nperm=1000, seed=9292, quiet=False):
    rows = predict(L); d = acc(rows, "CHAR") - acc(rows, "EDIT")
    rng = np.random.default_rng(seed); ge = 0
    edits = sorted({e for _, e in L})
    for _ in range(nperm):
        L2 = dict(L)
        for e in edits:
            ks = [k for k in L if k[1] == e]; vs = [L[k] for k in ks]
            for k, j in zip(ks, rng.permutation(len(vs))):
                L2[k] = vs[j]
        r2 = predict(L2); ge += acc(r2, "CHAR") - acc(r2, "EDIT") >= d
    p = (ge + 1) / (nperm + 1)
    v = "characters deviate consistently" if d >= 0.10 and p < 0.05 else ("no consistent deviation" if d <= 0.02 else "inconclusive")
    out = [{"test": "accuracy", "value": f"MAJ {acc(rows, 'MAJ'):.3f} EDIT {acc(rows, 'EDIT'):.3f} CHAR {acc(rows, 'CHAR'):.3f} (n {len(rows)})", "verdict": ""},
           {"test": "Rule: CHAR - EDIT", "value": f"{d:+.3f}, permutation p = {p:.3f} ({nperm})", "verdict": v}]
    if not quiet:
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
    return out, rows


def selftest():
    """Synthetic: each character has a bias genre it takes on half the edits; edits otherwise go to their own genre."""
    rng = np.random.default_rng(1); G = ["fumetto", "anime", "cartoon", "pittura", "realist"]
    chars = [f"C{i}" for i in range(7)]; edits = [f"E{j:02d}" for j in range(11)]
    bias = {c: G[i % 5] for i, c in enumerate(chars)}; own = {e: G[(j + 2) % 5] for j, e in enumerate(edits)}
    L = {(c, e): [bias[c] if rng.random() < 0.6 else own[e]] * 2 for c in chars for e in edits}
    out, _ = run(L, nperm=100, quiet=True)
    assert out[1]["verdict"] == "characters deviate consistently", out
    L0 = {(c, e): [own[e] if rng.random() < 0.6 else G[int(rng.integers(5))]] * 2 for c in chars for e in edits}
    out0, _ = run(L0, nperm=100, quiet=True)                      # no character bias: must not pass
    assert out0[1]["verdict"] != "characters deviate consistently", out0
    print("selftest ok", out[0]["value"], "| control:", out0[1]["value"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
    else:
        out, rows = run(load())
        with open(DATA / "te_character_consistency_tests.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        with open(DATA / "te_character_consistency_cases.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
