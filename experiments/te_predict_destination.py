"""C88 - predict the genre an edit leads to from its push on the conditioning (docs/prereg_te_predict_destination.md).
Written 2026-10-18 with the pre-registration, before any computation. No renders.

  python te_predict_destination.py            # writes data/te_predict_tests.csv, data/te_predict_cases.csv
  python te_predict_destination.py --selftest
"""
import argparse, csv, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
sys.path.insert(0, str(HERE))
ENC = None
ORD = ["V1_Original", "V2_SubjectFirst", "V3_BGFirst", "V4_ActionFirst", "V5_Inverse"]
CHARS = ["D1_dwarf_paladin", "E2_elf_rogue", "G5_gnome_wizard", "H3_halfling_druid", "O4_halforc_fighter",
         "R6_dragonborn_cleric", "T7_tiefling_bard"]


def enc_root():
    import blk23_colorful as c47
    root = c47.IMG_ROOT if c47.IMG_ROOT.exists() else Path.home() / "mnt" / "D:--StabilityMatrix-win-x64--Data--Images--Text2Img"   # Windows, or the VM mount
    return root / "benchmark_te_conditioning"


def rd(n):
    return list(csv.DictReader(open(DATA / n, encoding="utf-8")))


def load_units():
    """[(set, prompt, edit, [labels], npz path)]"""
    root, units = enc_root(), []
    lab = defaultdict(list)
    for r in rd("te_genre_alessandro.csv"):
        if r["row"] == "originali":
            continue
        for i, o in enumerate(ORD):
            lab[("orders", o, r["row"])].append(r[f"g{i + 1}"])
    for r in rd("te_fallback_genre_alessandro.csv"):
        if r["grid"].startswith("fb_edits_"):
            ch = r["grid"][len("fb_edits_"):]
            lab[("chars", ch, r["row"])] += [r["g1"], r["g2"]]
    for (st, pr, ed), ls in sorted(lab.items()):
        ls = [g.strip() for g in ls if g.strip() and g.strip() != "rotto"]
        p = root / ("order" if st == "orders" else "chars") / f"{pr}_{ed}.npz"
        if ls and p.exists():
            units.append((st, pr, ed, ls, p))
    return units


def features(units):
    F, S = [], []
    for *_, p in units:
        z = np.load(p)
        d = z["dmean"].astype(np.float32)
        d = d / (np.linalg.norm(d, axis=1, keepdims=True) + 1e-12)
        F.append(d.reshape(-1)); S.append(z["rel"].astype(np.float32).mean(0))
    F = np.array(F); F /= np.linalg.norm(F, axis=1, keepdims=True) + 1e-12
    S = np.array(S); S /= np.linalg.norm(S, axis=1, keepdims=True) + 1e-12
    return F, S


def maj(ls, fallback=None):
    if not ls:
        return fallback
    c = Counter(ls).most_common()
    top = [g for g, n in c if n == c[0][1]]
    return top[0] if len(top) == 1 else (fallback if fallback in top else sorted(top)[0])


def predict(units, F, S, labels=None):
    """labels: optional override [list per unit] (permutations). Returns per-case rows."""
    L = labels or [u[3] for u in units]
    rows = []
    for st in ("orders", "chars"):
        idx = [i for i, u in enumerate(units) if u[0] == st]
        for pr in sorted({units[i][1] for i in idx}):
            test = [i for i in idx if units[i][1] == pr]
            train = [i for i in idx if units[i][1] != pr]
            m = maj([g for i in train for g in L[i]])
            for i in test:
                e = maj([g for j in train if units[j][2] == units[i][2] for g in L[j]], m)
                j1 = train[int(np.argmax(F[train] @ F[i]))]
                p = L[j1][0] if Counter(L[j1]).most_common(1)[0][1] == 1 and len(set(L[j1])) > 1 else maj(L[j1])
                j2 = train[int(np.argmax(S[train] @ S[i]))]
                s = L[j2][0] if Counter(L[j2]).most_common(1)[0][1] == 1 and len(set(L[j2])) > 1 else maj(L[j2])
                for g in L[i]:
                    rows.append({"set": st, "prompt": pr, "edit": units[i][2], "label": g, "MAJ": m, "EDIT": e,
                                 "PUSH": p, "SIZE": s, "neighbour": f"{units[j1][1]}|{units[j1][2]}"})
    return rows


def acc(rows, k, sel=None):
    r = [x for x in rows if sel is None or sel(x)]
    return sum(x[k] == x["label"] for x in r) / len(r) if r else float("nan")


def run(units, F, S, nperm=1000, seed=8888, quiet=False):
    rows = predict(units, F, S)
    out = []
    for name, sel in (("pooled", None), ("orders", lambda x: x["set"] == "orders"), ("chars", lambda x: x["set"] == "chars")):
        out.append({"test": f"accuracy {name}", "value": " ".join(f"{k} {acc(rows, k, sel):.3f}" for k in ("MAJ", "EDIT", "PUSH", "SIZE"))
                    + f" (n {len([x for x in rows if sel is None or sel(x)])})", "verdict": ""})
    d = acc(rows, "PUSH") - acc(rows, "EDIT")
    rng = np.random.default_rng(seed); ge = 0
    groups = defaultdict(list)
    for i, u in enumerate(units):
        groups[(u[0], u[2])].append(i)
    for _ in range(nperm):
        L = [u[3] for u in units]
        for g in groups.values():
            perm = rng.permutation(g)
            L2 = [units[j][3] for j in perm]
            for i, l in zip(g, L2):
                L[i] = l
        r2 = predict(units, F, S, L)
        ge += (acc(r2, "PUSH") - acc(r2, "EDIT")) >= d
    p = (ge + 1) / (nperm + 1)
    em = acc(rows, "EDIT") - acc(rows, "MAJ")
    if d >= 0.10 and p < 0.05: v = "prompt modulates, predictably"
    elif abs(d) < 0.05 and em >= 0.15: v = "edit decides"
    else: v = "inconclusive"
    out.append({"test": "Rule: PUSH - EDIT (pooled)", "value": f"{d:+.3f}, permutation p = {p:.3f} ({nperm}); EDIT - MAJ {em:+.3f}", "verdict": v})
    out.append({"test": "PUSH where EDIT is wrong (reported)", "value": f"{acc(rows, 'PUSH', lambda x: x['EDIT'] != x['label']):.3f} of {len([x for x in rows if x['EDIT'] != x['label']])}", "verdict": ""})
    if not quiet:
        for o in out:
            print(o["test"], "|", o["value"], "|", o["verdict"])
    return out, rows


def selftest():
    """Synthetic: genre set by the push direction only (two clusters crossing edits) -> PUSH beats EDIT."""
    rng = np.random.default_rng(0); units = []; F = []
    for st, prompts in (("orders", ORD), ("chars", CHARS)):
        for pi, pr in enumerate(prompts):
            for e in range(6):
                c = (pi + e) % 2
                units.append((st, pr, f"E{e}", ["anime" if c else "fumetto"] * 2, None))
                v = np.zeros(20); v[c] = 1; v += rng.normal(0, 0.1, 20); F.append(v / np.linalg.norm(v))
    F = np.array(F); out, _ = run(units, F, F, nperm=50, quiet=True)
    v = [o for o in out if o["test"].startswith("Rule")][0]
    assert v["verdict"] == "prompt modulates, predictably", v
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
    else:
        units = load_units(); F, S = features(units)
        print("units", len(units), Counter(u[0] for u in units))
        out, rows = run(units, F, S)
        with open(DATA / "te_predict_tests.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
        with open(DATA / "te_predict_cases.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
